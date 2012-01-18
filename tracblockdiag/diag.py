# -*- coding: utf-8 -*-

import os
from threading import RLock

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

try:
    from blockdiag.utils.fontmap import FontMap
except ImportError:
    FontMap = None

lock = RLock()


class BlockdiagLoader(object):
    search_builders = ['blockdiag', 'seqdiag', 'actdiag', 'nwdiag', 'rackdiag']

    def __init__(self):
        self._d = {}
        for name in self.search_builders:
            try:
                self._d[name[:-4]] = make_builder(name)
            except ImportError:
                pass

    def available_builders(self):
        return [x + 'diag' for x in self._d.keys()]

    def __getattr__(self, name):
        return self.__getitem__(name)

    def __getitem__(self, key):
        return self._d[key]()


class BaseBuilder(object):
    def __init__(self):
        raise NotImplementedError

    def prepare_options(self, options):
        options['font'] = detectfont(options.get('font', None))
        if FontMap is not None:
            options['fontmap'] = self.create_fontmap(options['font'])

    def build(self, text, format, options):
        self.prepare_options(options)
        tree = self.parse_string(text)
        lock.acquire()
        try:
            diagram = self.ScreenNodeBuilder.build(tree)
        finally:
            lock.release()
        draw = getattr(self, 'draw_%s' % format.lower())
        return draw(diagram, options)

    def draw_png(self, diagram, options):
        sio = StringIO()
        drawer = self.DiagramDraw('PNG', diagram, sio, **options)
        drawer.draw()
        drawer.save()
        png = sio.getvalue()
        try:
            sio.close()
        except:
            pass
        return png

    def draw_svg(self, diagram, options):
        drawer = self.DiagramDraw('SVG', diagram, None, **options)
        drawer.draw()
        return drawer.save()

    def create_fontmap(self, font):
        fontmap = FontMap()
        fontmap.set_default_font(font)
        return fontmap


def make_builder(module):
    name = module.title() + 'Builder'
    dct = {
        'module': module,
        '__init__': lambda self: None
    }
    klass = type(name, (BaseBuilder,), dct)
    assign_module(klass, module)
    return klass


def assign_module(klass, module):
    try:
        _assign_module2(klass, module)
    except ImportError:
        # for backward compatibility
        _assign_module(klass, module)


def _assign_module(klass, module):
    diagparser = _from_import(module, 'diagparser')
    builder = _from_import(module, 'builder')
    DiagramDraw = _from_import(module, 'DiagramDraw')
    parse = diagparser.parse
    tokenize = diagparser.tokenize
    klass.ScreenNodeBuilder = builder.ScreenNodeBuilder
    klass.DiagramDraw = DiagramDraw.DiagramDraw
    klass.parse_string = lambda self, text: parse(tokenize(text))


def _assign_module2(klass, module):
    parser = _from_import(module, 'parser')
    builder = _from_import(module, 'builder')
    drawer = _from_import(module, 'drawer')
    klass.ScreenNodeBuilder = builder.ScreenNodeBuilder
    klass.DiagramDraw = drawer.DiagramDraw
    klass.parse_string = lambda self, text: parser.parse_string(text)


def _from_import(frm_, imp_):
    return getattr(__import__('%s.%s' % (frm_, imp_)), imp_)


def detectfont(prefer=None):
    prefer = prefer or []
    fonts = prefer + [
        'c:/windows/fonts/VL-Gothic-Regular.ttf',       # for Windows
        'c:/windows/fonts/msmincho.ttf',                # for Windows
        'c:/windows/fonts/msgoth04.ttc',                # for Windows
        '/usr/share/fonts/truetype/ipafont/ipagp.ttf',  # for Debian
        '/usr/local/share/font-ipa/ipagp.otf',          # for FreeBSD
        '/Library/Fonts/Hiragino Sans GB W3.otf',       # for MacOS
        '/System/Library/Fonts/AppleGothic.ttf'         # for MaxOS
    ]
    for font in fonts:
        if font and os.path.isfile(font):
            return font


def get_diag(type_, text, fmt, font=None, antialias=True, nodoctype=False):
    builder = loader[type_]
    options = {'font': font, 'antialias': antialias, 'nodoctype': nodoctype}
    return builder.build(text, fmt, options)


loader = BlockdiagLoader()
