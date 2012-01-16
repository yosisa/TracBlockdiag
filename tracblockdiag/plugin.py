# -*- coding: utf-8 -*-

import re
from bz2 import compress, decompress
from base64 import b64encode, b64decode

from trac.core import *
from trac.util.html import html
from trac.web import IRequestHandler
from trac.wiki import IWikiMacroProvider
from trac.wiki.formatter import system_message

from . import diag, cache

_template = u"""
= What's this? =
Generate %(kind)s diagram from source text.

See [http://blockdiag.com/en/%(module)s/ %(module)s (en)] or
[http://blockdiag.com/ja/%(module)s/ for Japanese]

== Arguments (Only Trac 0.12 or later) ==
 `type`:: Image format (png or svg)
 `others`:: Used to IMG tag attributes
"""

_descriptions = {
    'blockdiag': {'kind': 'block', 'module': 'blockdiag'},
    'seqdiag': {'kind': 'sequence', 'module': 'seqdiag'},
    'actdiag': {'kind': 'activity', 'module': 'actdiag'},
    'nwdiag': {'kind': 'network', 'module': 'nwdiag'},
    'rackdiag': {'kind': 'rack', 'module': 'nwdiag'}
}

macro_defs = {}
for name in diag.loader.available_builders():
    macro_defs[name] = _template % _descriptions[name]

content_types = {'png': 'image/png',
                 'svg': 'image/svg+xml'}
_conf_section = 'tracblockdiag'


class BlockdiagRenderer(Component):
    implements(IWikiMacroProvider, IRequestHandler)

    def __init__(self):
        self.font = self.config.getlist(_conf_section, 'font')
        self.default_type = self.config.get(_conf_section, 'default_type',
                                            'svg')
        cachetime = self.config.getint(_conf_section, 'cachetime', 300)
        gc_interval = self.config.getint(_conf_section, 'gc_interval', 100)
        self.url = re.compile(r'/blockdiag/([a-z]+)/(png|svg)/(.+)')
        self.src = 'blockdiag/%(type)s/%(fmt)s/%(data)s'
        cache.set_gc_params(gc_interval, cachetime)
        self.get_diag = cache.memoize(cachetime)(diag.get_diag)

    def get_macros(self):
        return macro_defs.keys()

    def get_macro_description(self, name):
        return macro_defs.get(name, '')

    def expand_macro(self, formatter, name, content, args=None):
        args = args or {}
        data = b64encode(compress(content.encode('utf-8')))
        type_ = name[:-4]
        fmt = args.pop('type', self.default_type)
        params = {'type': type_, 'data': data, 'fmt': 'png'}
        attrs = args.copy()
        attrs['src'] = formatter.req.href(self.src % params)
        img = html.img(**attrs)
        if fmt == 'png':
            return img
        params['fmt'] = 'svg'
        attrs = args.copy()
        attrs['data'] = formatter.req.href(self.src % params)
        attrs['type'] = content_types['svg']
        obj = html.object(**attrs)(img)
        return obj

    def match_request(self, req):
        return bool(self.url.match(req.path_info))

    def process_request(self, req):
        type_, fmt, data = self.url.match(req.path_info).groups()
        text = decompress(b64decode(data)).decode('utf-8')
        diag = self.get_diag(type_, text, fmt, self.font)
        req.send(diag, content_types.get(fmt.lower(), ''), status=200)
