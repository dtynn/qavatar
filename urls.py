#coding=utf-8
from handlers import *

wwwUrls = [
    (r'/', PageIndexHdl),
    (r'/list', PageListHdl),
    (r'/crop', PageCropHdl),
    (r'/api/q_token', ApiUpTokenHdl),
    (r'/api/q_callback', ApiUpCallbackHdl),
]