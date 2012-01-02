# -*- coding: utf-8 -*-

import time
import unittest

from tracblockdiag import cache


class TestFunction(unittest.TestCase):
    def test_is_obsolete(self):
        entry = {'time': time.time()}
        self.assertTrue(cache.is_obsolete(entry, 0))
        self.assertFalse(cache.is_obsolete(entry, 3600))

    def test_compute_key(self):
        def foo_func():
            pass
        key = cache.compute_key(foo_func, [1, 2], {'a': 1, 'b': 2})
        isinstance(key, str)


class TestGC(unittest.TestCase):
    def setUp(self):
        self.gc = cache.GC(2, 60)
        cache.cache = {
            'a': {'time': time.time() - 60},
            'b': {'time': time.time()}
        }

    def test_run(self):
        # not run yet
        expect = cache.cache.copy()
        self.gc.run()
        self.assertEqual(cache.cache, expect)
        # run and collect 'a'
        expect.pop('a')
        self.gc.run()
        self.assertEqual(cache.cache, expect)
        # not run yet
        cache.cache['b']['time'] -= 60
        cache.cache['c'] = {'time': time.time() - 60}
        expect = cache.cache.copy()
        self.gc.run()
        self.assertEqual(cache.cache, expect)
        # run and collect all entry
        self.gc.run()
        self.assertEqual(cache.cache, {})

    def tearDown(self):
        cache.cache = {}


class TestMemoize(unittest.TestCase):
    def setUp(self):
        cache.cache = {}
        self.args = (1, 2)
        self.key = cache.compute_key(self.foo_meth, self.args, {})

    def foo_meth(self, a, b):
        return a + b

    def test_memoize(self):
        # execute function and cache result
        meth = cache.memoize(300)(self.foo_meth)
        self.assertEqual(meth(*self.args), 3)
        self.assertEqual(cache.cache.keys(), [self.key])
        # pollute cache, check that return value is polluted
        cache.cache[self.key]['value'] = 4
        self.assertEqual(meth(*self.args), 4)
        self.assertEqual(cache.cache.keys(), [self.key])
        # cache is expired, re-calculate
        cache.cache[self.key]['time'] -= 300
        self.assertEqual(meth(*self.args), 3)
        self.assertEqual(cache.cache.keys(), [self.key])
        self.assertEqual(cache.cache[self.key]['value'], 3)

    def tearDown(self):
        cache.cache = {}
