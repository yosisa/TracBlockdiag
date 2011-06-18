# -*- coding: utf-8 -*-

import re
from base64 import b64encode, b64decode

from trac.core import *
from trac.util.html import html
from trac.web import IRequestHandler
from trac.wiki import IWikiMacroProvider
from trac.wiki.formatter import system_message

from .diag import detectfont, get_diag, memoize

macro_defs = {'blockdiag': 'description'}
content_types = {'png': 'image/png',
                 'svg': 'image/svg+xml'}
_conf_section = 'tracblockdiag'


class BlockdiagRenderer(Component):
    implements(IWikiMacroProvider, IRequestHandler)

    def __init__(self):
        preferfont = self.config.getlist(_conf_section, 'font')
        cachetime = self.config.getint(_conf_section, 'cachetime', 300)
        self.font = detectfont(preferfont)
        self.url = re.compile(r'/blockdiag/([a-z]+)/(png|svg)/(.+)')
        self.src = 'blockdiag/%(type)s/%(fmt)s/%(data)s'
        self.get_diag = memoize(cachetime)(get_diag)

    def get_macros(self):
        return macro_defs.keys()

    def get_macro_description(self, name):
        return macro_defs.get(name, '')

    def expand_macro(self, formatter, name, content, args=None):
        args = args or {}
        params = {'type': name[:-4], 'data': b64encode(content),
                  'fmt': args.pop('type', 'png')}
        args['src'] = formatter.req.href(self.src % params)
        return html.img(**args)

    def match_request(self, req):
        return bool(self.url.match(req.path_info))

    def process_request(self, req):
        type_, fmt, data = self.url.match(req.path_info).groups()
        diag = self.get_diag(b64decode(data), fmt, self.font)
        req.send(diag, content_types.get(fmt.lower(), ''), status=200)
