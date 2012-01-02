# -*- coding: utf-8 -*-

import time
import hashlib
import pickle
from threading import RLock

cache = {}


def is_obsolete(entry, duration):
    return time.time() - entry['time'] > duration


def compute_key(function, args, kwargs):
    key = pickle.dumps((function.func_name, args, kwargs))
    return hashlib.sha1(key).hexdigest()


def memoize(duration=300):
    def _memoize(function):
        def __memoize(*args, **kwargs):
            gc.run()
            key = compute_key(function, args, kwargs)
            entry = cache.get(key, None)
            if entry is not None and not is_obsolete(entry, duration):
                entry['time'] = time.time()
                return entry['value']
            result = function(*args, **kwargs)
            cache[key] = {'value': result, 'time': time.time()}
            return result
        return __memoize
    return _memoize


class GC(object):
    def __init__(self, interval=50, expire_time=300):
        self.interval = interval
        self.expire_time = expire_time
        self.lock = RLock()
        self.count = self.interval

    def run(self):
        self.count -= 1
        if self.count > 0:
            return
        if not self.lock.acquire(False):
            return
        try:
            self.count = self.interval
            for key in cache.keys():
                entry = cache.get(key, None)
                if entry is not None and is_obsolete(entry, self.expire_time):
                    cache.pop(key, None)
        finally:
            self.lock.release()


def set_gc_params(interval=None, expire_time=None):
    if interval is not None:
        gc.interval = interval
    if expire_time is not None:
        gc.expire_time = expire_time


gc = GC()
