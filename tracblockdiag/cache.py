# -*- coding: utf-8 -*-

import time
import hashlib
import pickle

cache = {}


def is_obsolete(entry, duration):
    return time.time() - entry['time'] > duration


def compute_key(function, args, kwargs):
    key = pickle.dumps((function.func_name, args, kwargs))
    return hashlib.sha1(key).hexdigest()


def memoize(duration=10):
    def _memoize(function):
        def __memoize(*args, **kwargs):
            key = compute_key(function, args, kwargs)
            if key in cache and not is_obsolete(cache[key], duration):
                cache[key]['time'] = time.time()
                return cache[key]['value']
            result = function(*args, **kwargs)
            cache[key] = {'value': result, 'time': time.time()}
            return result
        return __memoize
    return _memoize
