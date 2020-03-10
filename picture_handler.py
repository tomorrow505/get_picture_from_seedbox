# -*- coding: utf-8 -*-
# Author:tomorrow505

import subprocess
from PIL import Image, ImageDraw, ImageFont
from pymediainfo import MediaInfo
from bs4 import BeautifulSoup
import requests
import random
import json
import re
import sys
import os


class Video:
    def __init__(self, filename):

        # 影片名字
        self.filename = filename
        # 影片大小
        self.filesize = self.get_file_size()

        # 获取图片——第0秒的 及其大小
        example = self.get_frame_at(0)
        self.resolution = example.size
        # RBG
        self.mode = example.mode

        # 获取秒数
        self.duration = self.get_video_duration()
        self.thumbnails = []

        # 图片大小
        self.thumbsize = self.resolution
        self.thumbcount = 0

    def get_file_size(self):
        return round(os.stat(self.filename).st_size / 1048576.0 / 1024, 2)

    def get_video_duration(self):
        media_info = MediaInfo.parse(self.filename)
        data = media_info.to_json()
        data = json.loads(data)['tracks']
        frame_rate = 1
        frame_count = 0
        for key in data:
            if key['track_type'] == 'Video':
                frame_rate = key['frame_rate']
                frame_count = key['frame_count']
                break
        duration = int(frame_count) / (int(frame_rate.split('.')[0]))
        return duration

    def get_frame_at(self, seektime, n=99):
        timestring = get_time_string(seektime)
        file_name = os.path.basename(self.filename)

        # --------------这个是临时的图片文件夹的绝对路径，需要获取读写权限----------------------------
        tmp_path = './tmp'

        img_path = os.path.join(tmp_path, "{filename}-out-{d}.jpg".format(filename=file_name, d=n))
        command = 'ffmpeg -ss {timestring} -y -i "{file}" "-f" "image2" "-frames:v"  "1" "-c:v" "png" ' \
                  '"-loglevel" "8" {img_path}'.format(timestring=timestring, file=self.filename, img_path=img_path)
        try:
            subprocess.call(command, shell=True)
            img = Image.open(img_path.format(n=n))
        except Exception as exc:
            print(exc)
        return img

    # 把所有间隔多少的截图都放到一个列表里
    def make_thumbnails(self, interval, number=0):
        if not number:
            total_thumbs = int(self.duration // interval)
        else:
            total_thumbs = number
        thumbs_list = []
        seektime = 0
        for n in range(0, total_thumbs):
            seektime += interval
            img = self.get_frame_at(seektime, n)
            if img:
                thumbs_list.append(img)
        self.thumbnails = thumbs_list
        self.thumbcount = len(thumbs_list)
        return thumbs_list

    # 收缩图片大小
    def shrink_thumbs(self, maxsize):
        if self.thumbcount == 0:
            return
        for i in range(0, self.thumbcount):
            self.thumbnails[i].thumbnail(maxsize)
        self.thumbsize = self.thumbnails[0].size
        return self.thumbnails


def get_time_string(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    timestring = str(hours) + ":" + str(minutes).rjust(2, '0') + ":" + str(seconds).rjust(2, '0')
    return timestring


class Sheet:
    def __init__(self, video):

        # 主体的字体，介绍影片信息，绝对地址，建议使用这个字体
        fontfile = 'Cyberbit.ttf'

        self.font = ImageFont.truetype(fontfile, 18)
        self.headerColour = (255, 255, 255, 0)
        self.backgroundColour = (255, 255, 255, 0)

        # 字体颜色，固定为黑色
        self.textColour = (0, 0, 0, 0)
        self.headerSize = 135

        # 时间戳的颜色
        self.time_color = (255, 255, 224, 0)

        self.gridColumn = random.choice([2, 3])

        t = int(1200 / self.gridColumn)
        self.maxThumbSize = (t, t)
        self.timestamp = True

        self.audio_string = ''
        self.video_string = ''
        self.info_string = ''

        # -----------------------------就是签名内容---------------------------------------------------------
        self.special_id = 'Rainism'

        # -----------------------------签名使用的字体-------------------------------------------------------
        name_file = 'Sample.ttf'

        # ----------------------------签名的位置（距离左边和距离图片上边的像素）----------------------------
        self.position = (900, 50)

        # -----------------------------字体大小---------------------------------------------------------------
        self.namefont = ImageFont.truetype(name_file, 48)

        self.box_width = 4
        self.video = video

    def make_grid(self):
        column = self.gridColumn
        row = self.video.thumbcount // column
        if (self.video.thumbcount % column) > 0:
            row += 1
        width = self.video.thumbsize[0]
        height = self.video.thumbsize[1]
        grid = Image.new(self.video.mode,
                         (width * column + self.box_width * (column + 1), height * row + self.box_width * (row + 1)),
                         self.backgroundColour)
        d = ImageDraw.Draw(grid)
        seektime = 0
        for j in range(0, row):
            for i in range(0, column):
                if j * column + i >= self.video.thumbcount:
                    break
                aps_x = (i + 1) * self.box_width
                aps_y = (j + 1) * self.box_width
                grid.paste(self.video.thumbnails[j * column + i], (width * i + aps_x, height * j + aps_y))
                if self.timestamp:
                    seektime += self.vid_interval
                    ts = get_time_string(seektime)
                    d.text(((width + self.box_width) * (i + 1) - 60, (height + self.box_width) * (j + 1) - 25), ts,
                           font=self.font,
                           fill=self.time_color)
        self.grid = grid
        dir_name = './tmp'
        base_name = os.path.basename(self.video.filename)
        img_name = os.path.join(dir_name, base_name)
        for i in range(0, 12):
            try:
                img_path = '{filename}-out-{d}.jpg'.format(filename=img_name, d=i)
                # print(img_path)
                os.remove(img_path)
            except Exception:
                pass
        try:
            os.remove('{filename}-out-99.jpg'.format(filename=img_name))
        except Exception:
            pass
        return grid

    def make_header(self):
        self.get_header_info()
        duration = self.video.duration
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)
        timestring = (str(hours) + ":" + str(minutes).rjust(2, '0') + ":" + str(seconds).rjust(2, '0'))

        header = Image.new(self.grid.mode, (self.grid.width, self.headerSize), self.headerColour)

        d = ImageDraw.Draw(header)
        d.text((10, 14), "File: " + os.path.basename(self.video.filename), font=self.font, fill=self.textColour)
        d.text((10, 38), "Size: " + str(self.video.filesize) + "GB, " + 'Duration: ' + timestring + self.info_string,
               font=self.font, fill=self.textColour)
        d.text((10, 62), self.audio_string, font=self.font, fill=self.textColour)
        d.text((10, 86), self.video_string, font=self.font, fill=self.textColour)

        # 这句话也可以修改，建议可以做一些宣传性的内容？随便啦
        d.text((10, 110), "Auto generated by FFMPEG combined with python code from seedbox.", font=self.font, fill=self.textColour)

        d.text(self.position, self.special_id, font=self.namefont, fill=self.textColour)
        self.header = header
        return header

    def make_sheet_by_interval(self, interval, number=0):
        self.video.make_thumbnails(interval, number)
        self.video.shrink_thumbs(self.maxThumbSize)
        self.make_grid()
        self.make_header()
        self.sheet = Image.new(self.grid.mode, (self.grid.width, self.grid.height + self.header.height))
        self.sheet.paste(self.header, (0, 0))
        self.sheet.paste(self.grid, (0, self.header.height))
        return self.sheet

    def make_sheet_by_number(self):
        if self.gridColumn == 3:
            num_of_thumbs = 12
        else:
            num_of_thumbs = 8
        interval = (self.video.duration / (num_of_thumbs + 1))
        self.vid_interval = interval
        return self.make_sheet_by_interval(interval, number=num_of_thumbs)

    def get_header_info(self):
        media_info = MediaInfo.parse(self.video.filename)
        data = media_info.to_json()
        data = json.loads(data)['tracks']
        audio_num = 0

        overall_bit_rate = ''
        video_format = ''
        video_color = ''
        video_chroma_subsampling = ''
        video_codec_id = ''
        video_format_profile = ''
        video_other_frame_rate = ''
        video_other_bit_rate = ''
        audio_other_format = ''
        audio_other_sampling_rate = ''
        audio_other_bit_rate = ''
        audio_other_fram_rate = ''

        for key in data:
            if key['track_type'] == 'General':
                if 'other_overall_bit_rate' in key.keys():
                    overall_bit_rate = key['other_overall_bit_rate'][0]
            elif key['track_type'] == 'Video':
                if 'format' in key.keys():
                    video_format = key['format'].lower()
                if 'color_space' in key.keys():
                    video_color = key['color_space'].lower()
                if 'chroma_subsampling' in key.keys():
                    video_chroma_subsampling = key['chroma_subsampling']
                if 'codec_id' in key.keys():
                    video_codec_id = key['codec_id'].lower()
                if 'format_profile' in key.keys():
                    video_format_profile = key['format_profile'].lower()
                if 'other_frame_rate' in key.keys():
                    video_other_frame_rate = key['other_frame_rate'][0]
                if 'other_bit_rate' in key.keys():
                    video_other_bit_rate = key['other_bit_rate'][0]
            elif key['track_type'] == 'Audio':
                audio_num = audio_num + 1
                if audio_num > 1:
                    continue
                if 'other_format' in key.keys():
                    audio_other_format = key['other_format'][0].lower()
                if 'other_sampling_rate' in key.keys():
                    audio_other_sampling_rate = key['other_sampling_rate'][0]
                if 'other_bit_rate' in key.keys():
                    audio_other_bit_rate = key['other_bit_rate'][0]
                if 'other_fram_rate' in key.keys():
                    audio_other_fram_rate = key['other_fram_rate'][0]

        self.info_string = ', avg.bitrate: ' + overall_bit_rate
        self.audio_string = 'Audio: %s, %s, %s, %s' % (audio_other_format, audio_other_sampling_rate,
                                                       audio_other_fram_rate, audio_other_bit_rate)
        self.video_string = 'Video: %s, %s, %s, %s: %s, %sx%s, %s, %s' % (video_format, video_format_profile,
                                                                          video_codec_id, video_color,
                                                                          video_chroma_subsampling,
                                                                          self.video.resolution[0],
                                                                          self.video.resolution[1],
                                                                          video_other_bit_rate, video_other_frame_rate)


def get_picture(file_loc, img_loc):
    if not os.path.exists(img_loc):
        vid = Video(file_loc)
        vsheet = Sheet(vid)
        vsheet.make_sheet_by_number()
        vsheet.sheet.save(img_loc)

    funcs = [0, 1, 2, 3]
    func = random.choice(funcs)
    #   func = 3
    if func == 0:
        pic_url = send_picture(img_loc=img_loc)
    elif func == 1:
        pic_url = send_picture_2(img_loc=img_loc)
    elif func == 2:
        pic_url = send_picture_3(img_loc=img_loc)
    else:
        pic_url = send_picture_4(img_loc=img_loc)
    if pic_url:
        return '\n\n[img]' + pic_url + '[/img]\n\n'
    else:
        return ''


# sm.ms
def send_picture(img_loc=None):
    print('正在上传到SM.MS……')
    files = {
        'smfile': open(img_loc, "rb"),
        'format': 'json'
    }

    des_url = 'https://sm.ms/api/v2/upload?inajax=1'
    try:
        des_post = requests.post(
            url=des_url,
            files=files)

        data = json.loads(des_post.content.decode())['data']

        url_to_descr = data['url']

        print(url_to_descr)
    except Exception as exc:
        url_to_descr = ''
        print('上传到sm.ms失败: %s' % exc)

    # print('获取图片链接成功。')
    return url_to_descr


# img_url
def send_picture_2(img_loc=None):
    print('正在上传到imgurl……')
    headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/74.0.3729.169"}

    des_url = 'https://imgurl.org/upload/ftp'
    img = open(img_loc, 'rb')
    try:
        files = [('file', (img_loc.split('\\')[-1], img, 'image/jpeg'))]
        des_post = requests.post(headers=headers, url=des_url, files=files)
        response = des_post.content.decode()
        url = re.search('"thumbnail_url":"(.*?)"', response)
        url = url.group(1).replace('/', '')
        url = url.replace('\\', '/')
        url = url.replace('_thumb', '')
        print(url)
    except Exception as exc:
        print('上传到imgurl错误：%s' % exc)
        url = ''

    return url


# catbox
def send_picture_3(img_loc=None):
    # cookie = {
    #     "PHPSESSID": "8o8v85dtpg91v6tj6kugniue53"
    # }
    print('正在上传到catbox……')
    headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/74.0.3729.169",
               'Referer': 'https: // catbox.moe /?tdsourcetag = s_pctim_aiomsg'
               }
    des_url = 'https://catbox.moe/user/api.php'
    img = open(img_loc, 'rb')
    try:
        files = [('fileToUpload', (img_loc.split('\\')[-1], img, 'image/jpeg'))]
        data = {
            'reqtype': 'fileupload',
            'userhash': ''
        }
        des_post = requests.post(headers=headers, url=des_url, data=data, files=files)
        url = des_post.content.decode()
        print(url)
    except Exception as exc:
        print('上传到catbox错误: %s' % exc)
        url = ''

    return url


# lightshot
def send_picture_4(img_loc=None):

    print('正在上传图片至lightshot')
    headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/74.0.3729.169",
               }
    des_url = 'https://prntscr.com/upload.php'
    img = open(img_loc, 'rb')
    try:
        files = [('image', (img_loc.split('\\')[-1], img, 'image/jpeg'))]
        des_post = requests.post(headers=headers, url=des_url, files=files)
        html_ = des_post.content.decode()
        # print(html_)
        url = re.search('"data":"(.*)"', html_)
        url = url.group(1).replace('\\', '')
        html_ = requests.get(url, headers=headers).text
        soup = BeautifulSoup(html_, 'lxml')
        div = soup.find('div', class_="image-container image__pic js-image-pic")
        img = div.find('img')
        url = img.get_attribute_list('src')[0]
        url = url.replace('https', 'http')
        print(url)
    except Exception as exc:
        print('上传图片错误%s :' % exc)
        url = ''

    return url



def change_to_ss(number):
    hh = int(number / 3600)
    number_ = number - 3600 * hh
    mm = int(number_ / 60)
    ss = int(number_ - 60 * mm)
    hh = str(hh).zfill(2)
    mm = str(mm).zfill(2)
    ss = str(ss).zfill(2)
    time = '%s:%s:%s' % (hh, mm, ss)
    return time


def hex_2_rgb(hex_str):
    r = int(hex_str[1:3], 16)
    g = int(hex_str[3:5], 16)
    b = int(hex_str[5:7], 16)
    rgb = (r, g, b, 0)

    return rgb


if __name__ == "__main__":
    args = sys.argv[1:]

    video_path = args[0]

    video_name = video_path.split('/')[-1]

    pic_path = './imgs/%s.jpg' % re.sub('[^0-9a-zA-Z-\.]', '', video_name)

    print(get_picture(video_path, pic_path))

