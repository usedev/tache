#!/usr/bin/env python
# -*- coding: utf-8 -*-
import functools

from .backend import RedisBackend, FileBackend
from .tache import Tache

RedisCache = functools.partial(Tache, RedisBackend)
FileCache = functools.partial(Tache, FileBackend)

__all__ = ['RedisCache', 'FileCache']
