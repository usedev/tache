#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tache
"""
import os

from .serializer import Serializer
from .utils import NO_VALUE


class BaseBackend(object):
    """
    Based cache implemention
    """

    def get(self, cache_key):
        raise NotImplementedError()

    def set(self, cache_key, data, timeout):
        raise NotImplementedError()

    def delete(self, cache_key):
        raise NotImplementedError()

    def mget(self, cache_keys):
        raise NotImplementedError()

    def mset(self, mapping, timeout):
        raise NotImplementedError()

    def get_key(self):
        raise NotImplementedError()


class RedisBackend(BaseBackend):
    def __init__(self, conn, format=None):
        self.conn = conn
        self.serializer = Serializer(format=format)

    def get(self, cache_key):
        data = self.conn.get(cache_key)
        if data is None:
            return NO_VALUE
        return self.serializer.decode(data)

    def set(self, cache_key, data, timeout):
        if data is None:
            timeout = int(max(min(300, 0.1 * timeout), 1))
        data = self.serializer.encode(data)
        self.conn.setex(cache_key, timeout, data)

    def delete(self, *cache_keys):
        self.conn.delete(*cache_keys)

    def mget(self, cache_keys):
        result = self.conn.mget(cache_keys)
        return [self.serializer.decode(r) if r else NO_VALUE for r in result]

    def mset(self, mapping, timeout):
        pipe = self.conn.pipeline(transaction=False)
        for k, v in mapping.items():
            v = self.serializer.encode(v)
            pipe.setex(k, timeout, v)
        pipe.execute()

    def get_key(self):
        return str(self.conn.incr('tag:id'))


class FileBackend(BaseBackend):
    def __init__(self, conn, format=None):
        self.conn = conn
        self.serializer = Serializer(format=format)

    def get(self, cache_key):
        if os.path.exists(cache_key):
            if self.serializer.format == 'BYTES':
                f = open(cache_key, 'rb')
            else:
                f = open(cache_key, 'r')
            data = f.read()
            f.close()
        else:
            data = None

        if data is None:
            return NO_VALUE
        return self.serializer.decode(data)

    def set(self, cache_key, data, timeout):
        if data is None:
            timeout = int(max(min(300, 0.1 * timeout), 1))
        data = self.serializer.encode(data)

        f_path = os.path.dirname(cache_key)
        if not os.path.exists(f_path):
            os.makedirs(f_path)

        if self.serializer.format == 'BYTES':
            f = open(cache_key, 'wb')
        else:
            f = open(cache_key, 'w')
        f.write(data)
        f.close()

    def delete(self, *cache_keys):
        for key in cache_keys:
            if os.path.exists(key):
                os.remove(key)

    def mget(self, cache_keys):
        result = self.conn.mget(cache_keys)
        return [self.serializer.decode(r) if r else NO_VALUE for r in result]

    def mset(self, mapping, timeout):
        pipe = self.conn.pipeline(transaction=False)
        for k, v in mapping.items():
            v = self.serializer.encode(v)
            pipe.setex(k, timeout, v)
        pipe.execute()

    def get_key(self):
        return str(self.conn.incr('tag:id'))
