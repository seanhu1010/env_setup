# -*- coding=utf-8 -*-

import psycopg2
from envlib.env.envlogging import logger
import psycopg2.extras
import vertica_python

__all__ = ['Database', ]


class Database(object):
    """数据库类

    Attributes:
        type: 数据库类型吗，取值'pgsql'、'vertica',默认为'pgsql'
        database: 数据库，初始化时为None
        connections: 连接，初始化为{}
    """

    def __init__(self, type='pgsql'):
        """初始化"""
        self.type = type
        self.database = None
        self.connections = {}

    def connect(self, database, user, password, host, port):
        """建立数据库连接

        Args:
            database: 数据库名
            user: 用户名
            password: 密码
            host: 数据库服务端ip
            port: 数据库服务端port

        Returns:
            None
        """

        try:
            if self.type == "vertica":
                info = f"vertica://{user}:{password}@{host}:{port}/{database}"
                if self.database:
                    if info in self.connections:
                        logger.debug(f"返回已存在的数据库连接 vertica://{host}:{port}/{database}成功,用户名:{user}")
                    else:
                        self._connect(database, user, password, host, port)
                else:
                    self._connect(database, user, password, host, port)
            else:
                info = "postgres://{user}:{password}@{host}:{port}/{database}"
                if info in self.connections:
                    self.database = self.connections.get(info)
                    logger.debug("返回已存在的数据库连接 postgres://{}:{}/{}成功,用户名:{}".format(host, port, database, user))
                else:
                    connect = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
                    self.connections[info] = connect
                    self.database = connect
                    logger.debug("连接数据库 postgres://{}:{}/{}成功,用户名:{}".format(host, port, database, user))
        except Exception as e:
            logger.error("连接数据库 postgres://{}:{}/{}失败,用户名:{}".format(host, port, database, user))

    def _connect(self, database, user, password, host, port):
        self.database = vertica_python.connect(database=database, user=user, password=password, host=host, port=port)
        info = f"vertica://{user}:{password}@{host}:{port}/{database}"
        self.connections[info] = self.database
        logger.debug(f"连接数据库 vertica://{host}:{port}/{database}成功,用户名:{user}")

    def execute_sql(self, database, user, password, host, port, sql):
        """执行数据库sql语句

        Args:
            database: 数据库名
            user: 用户名
            password: 密码
            host: 数据库服务端ip
            port: 数据库服务端port
            sql: 执行sql

        Returns:
            sql执行结果，以list of tuple形式返回，结合namedtuple使用
        """

        self.connect(database=database, user=user, password=password, host=host, port=port)
        rows = None
        try:
            cur = self.database.cursor()
            cur.execute(sql)
            if sql.strip().upper().startswith("SELECT"):
                rows = cur.fetchall()  # all rows in table
            else:
                rows = cur.statusmessage
            self.database.commit()
            logger.debug("执行sql语句成功:{}".format(sql))
            cur.close()
            # self.database.close()
        except Exception as e:
            logger.info("执行sql语句失败:{},异常信息:{}".format(sql, e.args[0]))
            self.database.commit()
        finally:
            self.close()
            return rows

    def execute_sql_dict(self, database, user, password, host, port, sql):
        """执行数据库sql语句

        Args:
            database: 数据库名
            user: 用户名
            password: 密码
            host: 数据库服务端ip
            port: 数据库服务端port
            sql: 执行sql

        Returns:
            sql执行结果，以dict形式返回
        """

        self.connect(database=database, user=user, password=password, host=host, port=port)
        rows = None
        try:
            if self.type == "vertica":
                cur = self.database.cursor('dict')
                cur.execute(sql)
                rows = cur.fetchall()  # all rows in table
            else:
                cur = self.database.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                cur.execute(sql)
                if sql.strip().upper().startswith("SELECT"):
                    rows = cur.fetchall()  # all rows in table
                else:
                    rows = cur.statusmessage
            self.database.commit()
            logger.debug("执行sql语句成功:{}".format(sql))
            cur.close()
            # self.database.close()
        except Exception as e:
            logger.info("执行sql语句失败:{},异常信息:{}".format(sql, e.args[0]))
            self.database.commit()
        finally:
            self.close()
            return rows

    def close(self):
        try:
            if self.connections is not {}:
                for info, connection in self.connections.items():
                    connection.close()
                    self.connections = {}
                    logger.debug("成功关闭数据库连接：{}".format(info))
        except:
            logger.error("关闭数据库连接失败：{}".format(self.connections))


if __name__ == '__main__':
    pass
