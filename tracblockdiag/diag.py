# -*- coding: utf-8 -*-

import os
import time
import hashlib
import pickle

from blockdiag.diagparser import parse, tokenize
from blockdiag.builder import ScreenNodeBuilder
from blockdiag.DiagramDraw import DiagramDraw

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

_cache = {}


def is_obsolete(entry, duration):
    return time.time() - entry['time'] > duration


def compute_key(function, args, kwargs):
    key = pickle.dumps((function.func_name, args, kwargs))
    return hashlib.sha1(key).hexdigest()


def memoize(duration=10):
    def _memoize(function):
        def __memoize(*args, **kwargs):
            key = compute_key(function, args, kwargs)
            if key in _cache and not is_obsolete(_cache[key], duration):
                _cache[key]['time'] = time.time()
                return _cache[key]['value']
            result = function(*args, **kwargs)
            _cache[key] = {'value': result, 'time': time.time()}
            return result
        return __memoize
    return _memoize


def detectfont(prefer=None):
    prefer = prefer or []
    fonts = prefer + \
            ['c:/windows/fonts/VL-Gothic-Regular.ttf',  # for Windows
             'c:/windows/fonts/msmincho.ttf',  # for Windows
             '/usr/share/fonts/truetype/ipafont/ipagp.ttf',  # for Debian
             '/usr/local/share/font-ipa/ipagp.otf',  # for FreeBSD
             '/System/Library/Fonts/AppleGothic.ttf']  # for MaxOS
    for font in fonts:
        if font and os.path.isfile(font):
            return font


@memoize(300)
def get_diag(text, fmt, font=None, antialias=True, nodoctype=False):
    if not isinstance(fmt, basestring):
        return None
    fmt = fmt.upper()
    if fmt not in ('SVG', 'PNG'):
        return None

    tree = parse(tokenize(text))
    diagram = ScreenNodeBuilder.build(tree)
    fp = None if fmt == 'SVG' else StringIO()
    drawer = DiagramDraw(fmt, diagram, fp, font=font,
                         antialias=antialias, nodoctype=nodoctype)
    drawer.draw()
    if fmt == 'SVG':
        return drawer.save()
    if fmt == 'PNG':
        drawer.save()
        diag = fp.getvalue()
        try:
            fp.close()
        except:
            pass
        return diag
