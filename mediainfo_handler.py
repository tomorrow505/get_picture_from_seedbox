# -*- coding: utf-8 -*-
# Author:tomorrow505


import json
import sys
from pymediainfo import MediaInfo


def get_video_info(video_file):
    mediainfo = {
        'general': '',
        'Video': '',
        'Audio': '',
        'language': '',
        'subtitle': '',
        'full_info': ''
    }

    text_info = ''

    media_info = MediaInfo.parse(video_file)
    data = media_info.to_json()
    data = json.loads(data)['tracks']
    audio_num = 0
    text_num = 0
    for key in data:
        if key['track_type'] == 'General':
            general = get_general(key)
            mediainfo['general'] = general
        elif key['track_type'] == 'Video':
            video = get_video(key)
            mediainfo['Video'] = video
        elif key['track_type'] == 'Audio':
            audio_num = audio_num + 1
            audio = get_audio(key, audio_num)
            mediainfo['Audio'] = mediainfo['Audio'] + audio

            if 'title' in key.keys():
                title = key['title']
                if title.find('粤语') >= 0:
                    mediainfo['language'] += '|粤语'
                elif title.find('国语') >= 0:
                    mediainfo['language'] += '|国语'
                    # else:
                    #     mediainfo['language'].append('国语')
            else:
                if'other_language' in key.keys():
                    language = key['other_language'][0]
                    if language.lower() == 'chinese':
                        mediainfo['language'] += '|国语'

        elif key['track_type'] == 'Text':

            text_num = text_num + 1
            text = get_text(key, text_num)
            text_info = text_info + text

            if 'other_language' in key.keys():
                subtitle = key['other_language'][0]
                if subtitle.lower() == 'chinese':
                    mediainfo['subtitle'] += '|中字'
                if subtitle.lower() == 'english':
                    mediainfo['subtitle'] += '|英字'
            else:
                if 'title' in key.keys():
                    subtitle = key['title']
                    if subtitle.find('中字') >= 0 or subtitle.find('简体') >= 0 or subtitle.find('繁体') >= 0:
                        mediainfo['subtitle'] += '|中字'
    if mediainfo['Audio']:
        mediainfo['Audio'] = 'Audio' + mediainfo['Audio']
    if text_info:
        mediainfo['Audio'] = mediainfo['Audio'] + '**********Text' + text_info

    mediainfo['full_info'] = get_video_info_1(video_file)

    print(mediainfo)
    return mediainfo


def get_general(key):

    general = []
    general.append(key['track_type'])
    general.append(check('Name..............: ', key, 'file_name'))
    general.append(check('Container.........: ', key, 'format'))
    general.append(check('Size..............: ', key, 'other_file_size'))
    general.append(check('Duration..........: ', key, 'other_duration'))
    general.append(check('BitRate...........: ', key, 'other_overall_bit_rate'))
    general = '*****'.join(part for part in general if part)
    return general


def get_audio(key, audio_num):

    audio_string = '*****Audio # %s............: ' % audio_num
    if 'format' in key.keys():
        audio_string = audio_string + key['format']
    if 'channel_s' in key.keys():
        if str(key['channel_s']).find('2') >= 0:
            audio_string = audio_string + ' ' + '2.0ch'
        elif str(key['channel_s']).find('6') >= 0:
            audio_string = audio_string + ' ' + '5.1ch'
        elif str(key['channel_s']).find('8') >= 0:
            audio_string = audio_string + ' ' + '7.1ch'
    if 'other_bit_rate' in key.keys():
        audio_string = audio_string + ' @ ' + key['other_bit_rate'][0]
    if 'title' in key.keys():
        audio_string = audio_string + ' ' + key['title']

    return audio_string


def get_text(key, text_num):

    text_string = '*****Text # %s.............: ' % text_num
    if 'format' in key.keys():
        text_string = text_string + key['format']
    if 'title' in key.keys():
        text_string = text_string + ' ' + key['title']

    return text_string


def get_video(key):

    general = []
    general.append(key['track_type'])
    if 'format' in key.keys():
        if key['format'] == 'AVC':
            key['format'] = 'X264'
    general.append(check('Codec.............: ', key, 'format'))
    general.append(check('BitRate...........: ', key, 'other_bit_rate'))
    if 'width' in key.keys() and 'height' in key.keys():
        width = key['width']
        height = key['height']
        string = '{width}x{height} pixels'.format(width=width, height=height)
        # print(string)
        general.append('Resolution........: %s' % string)
    general.append(check('Aspect Ratio......: ', key, 'other_display_aspect_ratio'))
    general.append(check('Frame Rate........: ', key, 'other_frame_rate'))
    general.append(check('Title.............: ', key, 'title'))
    general = '*****'.join(part for part in general if part)
    return general


def check(str1, key, str2):
    if str2 in key.keys():
        if str2.find('other') >= 0:
            r_part = key[str2][0]
        else:
            r_part = key[str2]
        return str1 + r_part
    else:
        return ''


def get_video_info_1(video_file):

    mediainfo = ''
    media_info = MediaInfo.parse(video_file)
    data = media_info.to_json()
    data = json.loads(data)['tracks']
    for key in data:
        if key['track_type'] == 'General':
            general = get_general_1(key)
            mediainfo = general + '*****'
        elif key['track_type'] == 'Video':
            video = get_video_1(key)
            mediainfo = mediainfo + '*****' + video + '*****'
        elif key['track_type'] == 'Audio':
            # audio_num = audio_num + 1
            # if audio_num > 2:
            #     continue
            audio = get_audio_1(key)
            mediainfo = mediainfo + '*****' + audio + '*****'

    mediainfo = mediainfo

    return mediainfo


def get_general_1(key):

    general = []
    general.append(key['track_type'])
    general.append(check('UniqueID/String------------------: ', key, 'other_unique_id'))
    general.append(check('Format/String--------------------: ', key, 'format'))
    general.append(check('Format_Version-------------------: ', key, 'format_version'))
    general.append(check('FileSize/String------------------: ', key, 'other_file_size'))
    general.append(check('Duration/String------------------: ', key, 'other_duration'))
    general.append(check('OverallBitRate/String------------: ', key, 'other_overall_bit_rate'))
    general.append(check('Encoded_Date---------------------: ', key, 'encoded_date'))
    general.append(check('other_writing_application--------: ', key, 'other_writing_application'))
    general.append(check('Encoded_Application/String-------: ', key, 'writing_library'))
    general = '*****'.join(part for part in general if part)
    return general


def get_audio_1(key):

    general = []
    general.append(key['track_type'])
    general.append(check('ID/String------------------------: ', key, 'count_of_stream_of_this_kind'))
    general.append(check('Format/String--------------------: ', key, 'other_format'))
    general.append(check('Format/Info----------------------: ', key, 'format_info'))
    general.append(check('CodecID--------------------------: ', key, 'codec_id'))
    general.append(check('Duration/String------------------: ', key, 'other_duration'))
    general.append(check('BitRate/String-------------------: ', key, 'other_bit_rate'))
    general.append(check('Channel(s)/String----------------: ', key, 'other_channel_s'))
    general.append(check('ChannelLayout--------------------: ', key, 'channel_layout'))
    general.append(check('SamplingRate/String--------------: ', key, 'other_sampling_rate'))
    general.append(check('FrameRate/String-----------------: ', key, 'other_frame_rate'))
    general.append(check('Compression_Mode/String----------: ', key, 'compression_mode'))
    general.append(check('Video_Delay/String---------------: ', key, 'other_delay_relative_to_video'))
    general.append(check('StreamSize/String----------------: ', key, 'other_stream_size'))
    general.append(check('Title----------------------------: ', key, 'title'))
    general.append(check('Language/String------------------: ', key, 'other_language'))
    general.append(check('Default/String-------------------: ', key, 'default'))
    general.append(check('Forced/String--------------------: ', key, 'forced'))
    general = '*****'.join(part for part in general if part)
    return general


def get_video_1(key):

    general = []
    general.append(key['track_type'])
    general.append(check('ID/String------------------------: ', key, 'count_of_stream_of_this_kind'))
    general.append(check('Format/String--------------------: ', key, 'format'))
    general.append(check('Format/Info----------------------: ', key, 'format_info'))
    general.append(check('Format_Profile-------------------: ', key, 'format_profile'))
    general.append(check('Format_Settings------------------: ', key, 'format_settings'))
    general.append(check('Format_Settings_CABAC/String-----: ', key, 'format_settings__cabac'))
    general.append(check('Format_Settings_RefFrames/String-: ', key, 'other_format_settings__reframes'))
    general.append(check('CodecID--------------------------: ', key, 'codec_id'))
    general.append(check('Duration/String------------------: ', key, 'other_duration'))
    general.append(check('BitRate/String-------------------: ', key, 'other_bit_rate'))
    general.append(check('Width/String---------------------: ', key, 'other_width'))
    general.append(check('Height/String--------------------: ', key, 'other_height'))
    general.append(check('DisplayAspectRatio/String--------: ', key, 'other_display_aspect_ratio'))
    general.append(check('FrameRate_Mode/String------------: ', key, 'other_frame_rate_mode'))
    general.append(check('FrameRate/String-----------------: ', key, 'other_frame_rate'))
    general.append(check('ColorSpace-----------------------: ', key, 'color_space'))
    general.append(check('ChromaSubsampling/String---------: ', key, 'chroma_subsampling'))
    general.append(check('BitDepth/String------------------: ', key, 'other_bit_depth'))
    general.append(check('ScanType/String------------------: ', key, 'other_scan_type'))
    general.append(check('Bits-(Pixel*Frame)---------------: ', key, 'bits__pixel_frame'))
    general.append(check('StreamSize/String----------------: ', key, 'other_stream_size'))
    general.append(check('Default/String-------------------: ', key, 'default'))
    general.append(check('Forced/String--------------------: ', key, 'forced '))
    general = '*****'.join(part for part in general if part)
    return general


if __name__ == "__main__":

    video_path = sys.argv[1]

    get_video_info(video_path)
