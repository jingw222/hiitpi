import os
import redis


class RedisClient(object):
    """Sets up a Redis database client for data storage and transmission"""

    def __init__(self, host, port, db, password):
        self.pool = redis.BlockingConnectionPool(
            host=host, port=port, db=db, password=password
        )

    @property
    def conn(self):
        if not hasattr(self, "_conn"):
            self.get_connection()
        return self._conn

    def get_connection(self):
        self._conn = redis.StrictRedis(connection_pool=self.pool)

        self._conn.set_response_callback(
            "get", lambda i: float(i) if i is not None else None
        )
        self._conn.set_response_callback(
            "lpop", lambda i: float(i) if i is not None else None
        )
        self._conn.set_response_callback("lrange", lambda l: [float(i) for i in l])

    def set(self, key, value):
        self.conn.set(key, value)

    def get(self, key):
        return self.conn.get(key)

    def lpush(self, key, value, max_size=None):
        self.conn.lpush(key, value)
        if max_size is not None and self.conn.llen(key) > max_size:
            self.conn.ltrim(key, 0, max_size - 1)

    def lpop(self, key):
        return self.conn.lpop(key)
