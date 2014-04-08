#!/usr/bin/env python
# -*- coding:utf-8 -*-
#A GAE web application to aggregate rss and send it to your kindle.
#Visit https://github.com/cdhigh/KindleEar for the latest version
#中文讨论贴：http://www.hi-pda.com/forum/viewthread.php?tid=1213082
#Contributors:
# rexdf <https://github.com/rexdf>

__Version__ = "1.13.2-alpha"
__Author__ = "cdhigh"

import os, datetime, logging, __builtin__, hashlib, time

# for debug
# 本地启动调试服务器：python.exe dev_appserver.py c:\kindleear
IsRunInLocal = (os.environ.get('SERVER_SOFTWARE', '').startswith('Development'))
log = logging.getLogger()
__builtin__.__dict__['default_log'] = log
__builtin__.__dict__['IsRunInLocal'] = IsRunInLocal

supported_languages = ['en','zh-cn','tr-tr'] #不支持的语种则使用第一个语言
#gettext.install('lang', 'i18n', unicode=True) #for calibre startup

import web
import jinja2
#from google.appengine.api import mail
from google.appengine.api import taskqueue
from google.appengine.api import memcache

from lib.memcachestore import MemcacheStore
from books import BookClasses

from apps.dbModels import Book
from apps.BaseHandler import BaseHandler
from apps.utils import fix_filesizeformat
from apps.View import *
from apps.Work import *

#reload(sys)
#sys.setdefaultencoding('utf-8')

log.setLevel(logging.INFO if IsRunInLocal else logging.WARN)

for book in BookClasses():  #添加内置书籍
    if memcache.get(book.title): #使用memcache加速
        continue
    b = Book.all().filter("title = ", book.title).get()
    if not b:
        b = Book(title=book.title,description=book.description,builtin=True)
        b.put()
        memcache.add(book.title, book.description, 86400)

class Test(BaseHandler):
    def GET(self):
        s = ''
        for d in os.environ:
            s += "<pre><p>" + str(d).rjust(28) + " | " + str(os.environ[d]) + "</p></pre>"
        return s

urls += ["/test", "Test",]

application = web.application(urls, globals())
store = MemcacheStore(memcache)
session = web.session.Session(application, store, initializer={'username':'','login':0,"lang":''})
jjenv = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'),
                            extensions=["jinja2.ext.do",'jinja2.ext.i18n'])
jjenv.filters['filesizeformat'] = fix_filesizeformat

app = application.wsgifunc()

web.config.debug = IsRunInLocal