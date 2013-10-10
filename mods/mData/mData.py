#coding=utf-8
import time


class mData(object):
    def __init__(self, dbConn):
        self.dbConn = dbConn
        return

    def IconAdd(self, uid, fileKey):
        table = 'icons'
        sql = '''
        INSERT OR IGNORE INTO %s(id, uid, created_at) VALUES (?, ?, ?)
        ''' % (table,)
        sql_update = '''
        UPDATE %s SET updated_at=?
        ''' % (table,)
        now = int(time.time())
        self.dbConn.execute(sql, (fileKey, uid, now))
        res_update = self.dbConn.execute(sql_update, (now,))
        return res_update > 0

    def IconGet(self, etag):
        table = 'icons'
        sql = '''
        SELECT id, uid, created_at, updated_at from %s WHERE id=?
        ''' % (table,)
        res = self.dbConn.get(sql, (etag,))
        return res

    def IconList(self):
        table = 'icons'
        sql = '''
        SELECT id, uid, created_at, updated_at from %s
        ''' % (table,)
        res = self.dbConn.query(sql)
        return res