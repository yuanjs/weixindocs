# -*- coding: utf-8 -*-
import os
import codecs
import sys
import weixin
import requests
import urllib
import time
from lxml import html
from lxml.builder import E
#import tornado.httpclient
from PIL import Image
from StringIO import StringIO
import tempfile

global_user_agent = {'User-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11) AppleWebKit/601.1.50 (KHTML, like Gecko) Version/9.0 Safari/601.1.50'}

WEIXIN_URL = 'http://weixin.sogou.com/gzhjs?cb=sogou.weixin.gzhcb&openid={id}&e\
qs={eqs}&ekv={ekv}&page={n}&t={t}'
WEIXIN_BASE = 'http://weixin.sogou.com'
global_session = requests.Session()

def getlinks(contents, pagenumber):
    key, level, secret, setting = weixin.process_key(contents)
    eqs = weixin.process_eqs(key,secret,setting)
    i = 1
    items = []
    while i <= pagenumber:
        weixinurl = WEIXIN_URL.format(id=secret, eqs=urllib.quote(eqs), ekv=level, n=i, t=int(time.time()*1000)) # 生成api url
        page = global_session.get(weixinurl)
        page.encoding = 'utf-8'
        nitems = weixin.process_jsonp(page.text)
        if len(nitems) <= 0:
            break
        items = items + nitems
        i = i + 1
    #print "Page numebr: " + str(pagenumber)
    #print "Total items: " + str(len(items))
    return items

def saveimglocal(contents, docindex, tempdir):
    imgs = contents.xpath('//img[@data-src]')
    i = 0
    for img in imgs:
        imgurl = img.get("data-src")
        if imgurl.find("http") >= 0:
            try:
                r = global_session.get(imgurl)
                f = Image.open(StringIO(r.content))
                imgfilename = tempdir + "/" +  str(docindex) + str(i) + "." + f.format
                #print f.format
                #print imgfilename
                f.save(imgfilename)
                img.attrib["src"] = str(docindex) + str(i) + "." + f.format
            except requests.HTTPError, e:
                print "Error while getting image: " + imgurl
                print 'HTTP ERROR %s occured' % e.code
        i = i + 1


def writelinks(items, wxname):
    # 保存文章及文章的索引文件
    count = 0

    indexroot = html.Element("html")
    indexbody = html.Element("body")
    title = E.H2(wxname)
    indexbody.append(title)

    tempdir = tempfile.mkdtemp(dir=".")
    
    for i in items:
        print u"获取文章：" + i['title']
        link = WEIXIN_BASE + i['link']
        #print u'链接:' + link
        page = global_session.get(link)
        page.encoding = 'utf-8'
        tree = html.fromstring(page.text)
        contents = tree.xpath('//div[@id="page-content"]')[0]
        saveimglocal(contents, count, tempdir)
        ncontents = html.tostring(tree)
        #npage = weixin.process_content(ncontents)
        f = codecs.open(tempdir + "/" + str(count) + ".html", "w", "utf-8")
        f.write(ncontents)
        f.close()
        doclocallink = str(count) + ".html"
        indexlist = E.li(E.a(i['title'],href = doclocallink))
        indexbody.append(indexlist)
        count = count + 1
    print("Writing index html file...")
    indexroot.append(indexbody)
    f = codecs.open(tempdir + "/index.html","w","utf-8")
    f.write(html.tostring(indexroot, pretty_print = True))
    f.close()
    print("Finished. All documents stored in: " + tempdir)
    print("Index file is: index.html")
    
def getweixinname(contents):
    tree = html.fromstring(contents)
    weixinnames = tree.xpath('//*[@id="weixinname"]')
    return weixinnames[0].text_content()

def main():
    if len(sys.argv) < 2:
        print "Usage: "
        print sys.argv[0] + " openid"
        sys.exit(0)
    if len(sys.argv) == 3:
        pagenumber = int(sys.argv[2])
    else:
        pagenumber = 1
    print "Beginning to get documents..."
    page = global_session.get("http://weixin.sogou.com/gzh?openid=" + sys.argv[1])
    page.encoding = 'utf-8'
    weixinname = getweixinname(page.text)
    items = getlinks(page.text, pagenumber)
    print "Weixin documents: " + str(len(items))
    #print "First Link: " + items[0]['link']
    writelinks(items, weixinname)
    
    
    
##############################
if __name__ == "__main__":
        main();
        
