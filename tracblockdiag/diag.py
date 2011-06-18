# -*- coding: utf-8 -*-

import os
import sys

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


class BlockdiagModule(object):
    def __init__(self, diagparser, builder, DiagramDraw):
        self._diagparser = diagparser
        self._builder = builder
        self._DiagramDraw = DiagramDraw

    def __getattr__(self, name):
        if name in ('parse', 'tokenize'):
            return getattr(self._diagparser, name)
        if name == 'ScreenNodeBuilder':
            return getattr(self._builder, name)
        if name == 'DiagramDraw':
            return getattr(self._DiagramDraw, name)
        return object.__getattr__(self, name)


class BlockdiagSwitch(object):
    def __init__(self):
        self._d = {}

    def add_module(self, name, module):
        self._d[name] = module

    def __getattr__(self, name):
        return self.__getitem__(name)

    def __getitem__(self, key):
        return self._d[key]


_diag = BlockdiagSwitch()
try:
    import blockdiag.diagparser
    import blockdiag.builder
    import blockdiag.DiagramDraw
    _diag.add_module('block', BlockdiagModule(
        blockdiag.diagparser, blockdiag.builder, blockdiag.DiagramDraw))
except ImportError:
    pass

try:
    import seqdiag.diagparser
    import seqdiag.builder
    import seqdiag.DiagramDraw
    _diag.add_module('seq', BlockdiagModule(
        seqdiag.diagparser, seqdiag.builder, seqdiag.DiagramDraw))
except ImportError:
    pass

try:
    import actdiag.diagparser
    import actdiag.builder
    import actdiag.DiagramDraw
    _diag.add_module('act', BlockdiagModule(
        actdiag.diagparser, actdiag.builder, actdiag.DiagramDraw))
except ImportError:
    pass

try:
    import nwdiag.diagparser
    import nwdiag.builder
    import nwdiag.DiagramDraw
    _diag.add_module('nw', BlockdiagModule(
        nwdiag.diagparser, nwdiag.builder, nwdiag.DiagramDraw))
except ImportError:
    pass


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
    return _get_diag(_diag[type_], text, fmt, font, antialias, nodoctype)


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
