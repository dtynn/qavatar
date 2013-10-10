#coding=utf-8
from base import WwwBaseHdl
import json
from qiniu import conf as qConf, rs as qRs


class ApiUpTokenHdl(WwwBaseHdl):
    def get(self):
        globalConf = self.settings['globalConfig']
        accessKey = globalConf.get('qiniu', 'accesskey')
        secretKey = globalConf.get('qiniu', 'secretkey')
        bucket = globalConf.get('qiniu', 'bucket')
        selfHost = globalConf.get('website', 'host')
        qConf.ACCESS_KEY = accessKey
        qConf.SECRET_KEY = secretKey
        policy = qRs.PutPolicy(bucket)
        policy.callbackUrl = '%s/api/q_callback' % (selfHost,)
        policy.callbackBody = 'etag=$(etag)'
        uploadToken = policy.token()
        self.ajax_result(0, 0, data=uploadToken)
        return


class ApiUpCallbackHdl(WwwBaseHdl):
    def post(self):
        etag = self.get_argument('etag', '')
        if etag:
            uid = -1
            mDataMod = self.settings['mods']['mData']
            res = 0 if mDataMod.IconAdd(uid, etag) else 1
            extra = dict()
            extra['key'] = etag
            self.ajax_result(1, res, extra=extra)
            return
        self.ajax_result(1, 1)
        return
