#coding=utf-8
import itertools
import logging
import sqlite3


sqlForSqlite = [
    #'DROP TABLE IF EXISTS `users`',
    '''
    CREATE TABLE IF NOT EXISTS `icons` (
        `id` TEXT NOT NULL PRIMARY KEY,
        `uid` INTEGER NOT NULL DEFAULT -1 ,
        `created_at` INTEGER NOT NULL DEFAULT 0,
        `updated_at` INTEGER NOT NULL DEFAULT 0
    )
    ''',
]


def dbInitSqlite(dbPath):
    logging.debug('DB initializing:%s' % (dbPath,))
    conn = makeSqliteConn(dbPath)
    dbInit(conn, sqlForSqlite)
    logging.debug('DB initialized')
    return


def dbInit(conn, sqls):
    for sql in sqls:
        conn.execute(sql)
    return


def makeSqliteConn(dbPath, isolation_level=None):
    if dbPath:
        return SqliteConnection(dbPath, isolation_level)
    return sqlite3.connect(dbPath, isolation_level=isolation_level)


class SqliteError(Exception):
    def __init__(self, *args, **kwargs):
        pass


class SqliteConnection(object):
    def __init__(self, dbPath, isolation_level=None):
        self._dbPath = dbPath
        self._conn = None
        self._isolation_level = isolation_level
        self._retry = 2
        return

    def __del__(self):
        self.close()
        return

    def close(self):
        """Closes this database connection pool."""
        if getattr(self, "_conn", None) is not None:
            self._conn.close()
            self._conn = None
        return

    def reconnect(self):
        """
        单连接重连机制
        """
        self.close()
        self._conn = sqlite3.connect(self._dbPath, isolation_level=self._isolation_level)
        self._conn.execute('PRAGMA encoding = "UTF-8"')
        return

    def _ensure_connected(self):
        if getattr(self, "_conn", None) is not None:
            try:
                self._conn.execute('SELECT 1')
            except Exception as e:
                logging.error(e)
                self.reconnect()
        else:
            self.reconnect()

    def _cursor(self):
        self._ensure_connected()
        return self._conn.cursor()

    def _execute(self, cursor, query, parameters):
        try:
            if self._isolation_level:
                cursor.execute('rollback')
            return cursor.execute(query, *parameters)
        except Exception:
            self.close()
            raise

    def query(self, query, *parameters):
        """Returns a row list for the given query and parameters."""
        count = 0
        while count < self._retry:
            cursor = self._cursor()
            try:
                self._execute(cursor, query, parameters)
                column_names = [d[0] for d in cursor.description]
                return [Row(itertools.izip(column_names, row)) for row in cursor]
            except Exception as e:
                logging.error(e)
                self.reconnect()
                count += 1
            finally:
                cursor.close()
        raise SqliteError("failed 2 times in query()")

    def get(self, query, *parameters):
        """Returns the first row returned for the given query."""
        #basic method query
        rows = self.query(query, *parameters)
        if not rows:
            return None
        elif len(rows) > 1:
            raise SqliteError("Multiple rows returned for Database.get() query")
        else:
            return rows[0]

    def execute(self, query, *parameters):
        """Executes the given query, returning the lastrowid from the query."""
        #basic method execute_lastrowid
        return self.execute_lastrowid(query, *parameters)

    def execute_lastrowid(self, query, *parameters):
        """Executes the given query, returning the lastrowid from the query."""
        count = 0
        while count < self._retry:
            cursor = self._cursor()
            try:
                self._execute(cursor, query, parameters)
                #assert cursor.rowcount != -1
                return cursor.lastrowid
            except Exception as e:
                logging.error(e)
                self.reconnect()
                count += 1
            #finally:
            #    cursor.close()
        raise SqliteError("failed 2 times in execute_lastrowid()")

    def execute_rowcount(self, query, *parameters):
        """Executes the given query, returning the rowcount from the query."""
        count = 0
        while count < self._retry:
            cursor = self._cursor()
            try:
                self._execute(cursor, query, parameters)
                assert cursor.rowcount != -1
                return cursor.rowcount
            except Exception as e:
                logging.error(e)
                self.reconnect()
                count += 1
            finally:
                cursor.close()
        raise SqliteError("failed 2 times in execute_rowcount()")

    def executemany(self, query, parameters):
        """Executes the given query against all the given param sequences.

        We return the lastrowid from the query.
        """
        #basic method executemany_lastrowid
        return self.executemany_lastrowid(query, parameters)

    def executemany_lastrowid(self, query, parameters):
        """Executes the given query against all the given param sequences.

        We return the lastrowid from the query.
        """
        cursor = self._cursor()
        try:
            cursor.executemany(query, parameters)
            return cursor.lastrowid
        finally:
            cursor.close()

    def executemany_rowcount(self, query, parameters):
        """Executes the given query against all the given param sequences.

        We return the rowcount from the query.
        """
        cursor = self._cursor()
        try:
            cursor.executemany(query, parameters)
            return cursor.rowcount
        finally:
            cursor.close()


class Row(dict):
    """A dict that allows for object-like property access syntax."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)