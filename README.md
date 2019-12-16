# get_picture_from_seedbox
盒子视频截图并上传

**前提条件：盒子上有python3环境,ffmpeg,mediainfo.**

**预装包：PIL,pymediainfo,lxml,beautifulsoup4**

#### 获取代码至服务器端：

+ sudo或者切换至root: 

`git clone https://github.com/tomorrow505/get_picture_from_seedbox.git`

+ 将文件放到当前文件夹下

`mv ./get_picture_from_seedbox/* . && rm -rf ./get_picture_from_seedbox/`

+ 新建tmp和imgs目录

`mkdir tmp`

`midir imgs`

+ pwd获取当前目录路径

`pwd` --> 如：/home/matthew/test

+ 然后更改目录权限：

`chmod 777 /home/matthew/test`

#### 代码更改：

代码有几处需要改成自己设置的地方,后边结合工具可能会做成参数,现在测试用。

-----------------------------签名内容(修改为自己的id)---------------------------------------------------------

self.special_id = 'MatthewLXJ'

-----------------------------签名使用的字体（可以自己测试想要的字体）-------------------------------------------------------

name_file = 'Sample.TTF' 

----------------------------签名的位置（距离左边和距离图片上边的像素）----------------------------

self.position = (900, 50)

-----------------------------字体大小（默认48）---------------------------------------------------------------

self.namefont = ImageFont.truetype(name_file, 48)


#### 使用方法

python3 脚本路径 视频路径

+ 测试：

`python3 picture_handler.py /home/qbittorrent/download/Cinta.Itu.Buta.2019.1080p.NF.WEB-DL.DDP5.1.H.264-Beerus.mkv`

+ 输出：

*正在上传图片至lightshot*

*http://image.prntscr.com/image/KVs9tmYiRGiXHeSqHcRS7Q.jpg*

*[img]http://image.prntscr.com/image/KVs9tmYiRGiXHeSqHcRS7Q.jpg[/img]*

预览

![预览](http://image.prntscr.com/image/KVs9tmYiRGiXHeSqHcRS7Q.jpg)

