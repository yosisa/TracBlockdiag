# -*- coding: utf-8 -*-

import os
import sys
from threading import RLock

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

lock = RLock()


class BlockdiagLoader(object):
    def __init__(self):
        self._d = {}
        for name in ('blockdiag', 'seqdiag', 'actdiag', 'nwdiag'):
            try:
                self.load_module(name)
            except ImportError:
                pass

    def load_module(self, name):
        self._d[name[:-4]] = BlockdiagModule(name)

    def __getattr__(self, name):
        return self.__getitem__(name)

    def __getitem__(self, key):
        return self._d[key]


class BlockdiagModule(object):
    def __init__(self, name):
        self.name = name
        diagparser = self._from_import(name, 'diagparser')
        builder = self._from_import(name, 'builder')
        DiagramDraw = self._from_import(name, 'DiagramDraw')
        self.parse = diagparser.parse
        self.tokenize = diagparser.tokenize
        self.ScreenNodeBuilder = builder.ScreenNodeBuilder
        self.DiagramDraw = DiagramDraw.DiagramDraw

    def _from_import(self, frm_, imp_):
        return getattr(__import__('%s.%s' % (frm_, imp_)), imp_)


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


def get_diag(type_, text, fmt, font=None, antialias=True, nodoctype=False):
    m = _diag[type_]
    fmt = fmt.upper()
    if fmt == 'SVG':
        return _get_diag(m, text, fmt, font, antialias, nodoctype)
    elif fmt == 'PNG':
        lock.acquire()
        try:
            return _get_diag(m, text, fmt, font, antialias, nodoctype)
        finally:
            lock.release()


def _get_diag(m, text, fmt, font=None, antialias=True, nodoctype=False):
    if not isinstance(fmt, basestring):
        return None
    fmt = fmt.upper()
    if fmt not in ('SVG', 'PNG'):
        return None

    tree = m.parse(m.tokenize(text))
    diagram = m.ScreenNodeBuilder.build(tree)
    fp = None if fmt == 'SVG' else StringIO()
    drawer = m.DiagramDraw(fmt, diagram, fp, font=font,
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


_diag = BlockdiagLoader()
