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


def memoize(duration=10, interval=50):
    gc = GC(duration, interval)
    def _memoize(function):
        def __memoize(*args, **kwargs):
            gc()
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
    def __init__(self, duration=10, interval=50):
        self.duration = duration
        self.interval = interval
        self.lock = RLock()
        self.count = self.interval

    def __call__(self):
        self.count -= 1
        if self.count > 0:
            return
        if not self.lock.acquire(False):
            return
        try:
            self.count = self.interval
            for key in cache.keys():
                entry = cache.get(key, None)
                if entry is not None and is_obsolete(entry, duration):
                    cache.pop(entry, None)
        finally:
            lock.release()
