# -*- coding: utf-8 -*-

import os

from blockdiag.diagparser import parse, tokenize
from blockdiag.builder import ScreenNodeBuilder
from blockdiag.DiagramDraw import DiagramDraw

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


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
