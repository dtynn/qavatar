#coding=utf-8
from base import WwwBaseHdl


class PageIndexHdl(WwwBaseHdl):
    def get(self):
        globalConf = self.settings['globalConfig']
        selfHost = globalConf.get('website', 'host')
        self.render('upload.html', selfHost=selfHost)
        return


class PageListHdl(WwwBaseHdl):
    def get(self):
        mDataMod = self.settings['mods']['mData']
        iconList = mDataMod.IconList()
        self.ajax_finish(iconList)
        return


class PageCropHdl(WwwBaseHdl):
    def get(self):
        key = self.get_argument('key', '')
        if key:
            mDataMod = self.settings['mods']['mData']
            res = mDataMod.IconGet(key)
            if res:
                globalConf = self.settings['globalConfig']
                domain = globalConf.get('qiniu', 'domain')
                self.render('crop.html', key=key, domain=domain)
                return
        self.write('404')
        return