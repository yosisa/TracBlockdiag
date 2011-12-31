# -*- coding: utf-8 -*-

import os
import sys

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


class BlockdiagLoader(object):
    def __init__(self):
        self._d = {}
        for name in ('blockdiag', 'seqdiag', 'actdiag', 'nwdiag'):
            try:
                self.load_module(name)
            except ImportError:
                pass

    def load_module(self, name):
        parser = _from_import(name, 'parser')
        builder = _from_import(name, 'builder')
        drawer = _from_import(name, 'drawer')
        self._d[name[:-4]] = BlockdiagBuilder(parser, builder, drawer)

    def __getattr__(self, name):
        return self.__getitem__(name)

    def __getitem__(self, key):
        return self._d[key]


class BlockdiagBuilder(object):
    def __init__(self, parser, builder, drawer):
        self.parser = parser
        self.builder = builder
        self.drawer = drawer

    def build(self, text, format, options):
        tree = self.parser.parse_string(text)
        diagram = self.builder.ScreenNodeBuilder.build(tree)
        draw = getattr(self, 'draw_%s' % format.lower())
        return draw(diagram, options)

    def draw_png(self, diagram, options):
        sio = StringIO()
        drawer = self.drawer.DiagramDraw('PNG', diagram, sio, **options)
        drawer.draw()
        drawer.save()
        png = sio.getvalue()
        try:
            sio.close()
        except:
            pass
        return png

    def draw_svg(self, diagram, options):
        drawer = self.drawer.DiagramDraw('SVG', diagram, None, **options)
        drawer.draw()
        return drawer.save()


def _from_import(frm_, imp_):
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
    builder = _diag[type_]
    options = {'font': font, 'antialias': antialias, 'nodoctype': nodoctype}
    return builder.build(text, fmt, options)


_diag = BlockdiagLoader()
