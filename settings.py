#coding=utf-8
import os

wwwSettings = dict(
    cookie_secret="43oETsK8aAGaYdkLtgEmGeJJ4uYh7EQnp2XdTP1o/Vo=",
    login_url='/',
    template_path=os.path.abspath('tmpl'),
    autoescape="xhtml_escape",
    static_path=os.path.abspath('static'),
)
