# weixindocs
这是一个用Python(2.7.10)写的用来下载微信公众号文章的一个小工具。
需要在http://weixin.sogou.com这个网站找到你想要下载的公众号的openid，然后执行：
python getwxlinks.py openid pagenumber
pagenumber可以是1、2等，1表示下载第一页的10篇文章，2是20篇，以此类推。
就可以下载最新的10篇文章到当前目录下的一个临时目录里。

