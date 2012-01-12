# -*- coding: utf-8 -*-

import os

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

try:
    from blockdiag.utils.fontmap import FontMap
except ImportError:
    FontMap = None


class BlockdiagLoader(object):
    search_builders = ['blockdiag', 'seqdiag', 'actdiag', 'nwdiag', 'rackdiag']

    def __init__(self):
        self._d = {}
        for name in self.search_builders:
            builder = self.make_builder(name) or self.make_legacy_builder(name)
            if builder is not None:
                self._d[name[:-4]] = builder

    def make_builder(self, name):
        try:
            return BlockdiagBuilder(name)
        except ImportError:
            return None

    def make_legacy_builder(self, name):
        try:
            return LegacyBlockdiagBuilder(name)
        except ImportError:
            return None

    def available_builders(self):
        return [x + 'diag' for x in self._d.keys()]

    def __getattr__(self, name):
        return self.__getitem__(name)

    def __getitem__(self, key):
        return self._d[key]


class BlockdiagBuilder(object):
    def __init__(self, name):
        self.name = name
        self.load_module()

    def load_module(self):
        parser = _from_import(self.name, 'parser')
        builder = _from_import(self.name, 'builder')
        drawer = _from_import(self.name, 'drawer')

        # copy needed class/func for easily overriding
        self.parse_string = parser.parse_string
        self.ScreenNodeBuilder = builder.ScreenNodeBuilder
        self.DiagramDraw = drawer.DiagramDraw

    def prepare_options(self, options):
        options['font'] = detectfont(options.get('font', None))
        if FontMap is not None:
            options['fontmap'] = self.create_fontmap(options['font'])

    def build(self, text, format, options):
        self.prepare_options(options)
        tree = self.parse_string(text)
        diagram = self.ScreenNodeBuilder.build(tree)
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


class LegacyBlockdiagBuilder(BlockdiagBuilder):
    """Blockdiag Builder for Compatibility"""

    def load_module(self):
        diagparser = _from_import(self.name, 'diagparser')
        builder = _from_import(self.name, 'builder')
        DiagramDraw = _from_import(self.name, 'DiagramDraw')

        self.parse = diagparser.parse
        self.tokenize = diagparser.tokenize
        self.ScreenNodeBuilder = builder.ScreenNodeBuilder
        self.DiagramDraw = DiagramDraw.DiagramDraw

    def parse_string(self, text):
        return self.parse(self.tokenize(text))


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
