import os
import unittest
from xml.dom import minidom

from tracblockdiag import diag

sample_dir = os.path.join(os.path.dirname(__file__), 'samples')


def skipUnlessImport(module):
    try:
        __import__(module)
        return lambda func: func
    except ImportError:
        return unittest.skip("module not found: {0}".format(module))


class BlockdiagBuildMixin(object):
    png_header = (0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A)
    blockdiag_text = """
    {
      A -> B -> C;
           B -> D;
    }
    """

    def setUp(self):
        self.default_options = {
            'antialias': False,
            'nodoctype': False
        }

    def test_attr(self):
        self.assertTrue(hasattr(self.builder, 'parse_string'))
        self.assertTrue(hasattr(self.builder, 'ScreenNodeBuilder'))
        self.assertTrue(hasattr(self.builder, 'DiagramDraw'))

    def test_build_png(self):
        png = self.builder.build(self.blockdiag_text, 'PNG',
                                 self.default_options)
        self.assertEqual(png[:8], ''.join(chr(x) for x in self.png_header))

    def test_build_svg(self):
        svg = self.builder.build(self.blockdiag_text, 'SVG',
                                 self.default_options)
        dom = minidom.parseString(svg)
        self.assertEqual(dom.doctype.name, 'svg')


@skipUnlessImport('blockdiag.parser')
class TestBlockdiagBuilder(BlockdiagBuildMixin, unittest.TestCase):
    def setUp(self):
        super(TestBlockdiagBuilder, self).setUp()
        self.builder = diag.BlockdiagBuilder('blockdiag')


@skipUnlessImport('blockdiag.diagparser')
class TestLegacyBlockdiagBuilder(BlockdiagBuildMixin, unittest.TestCase):
    def setUp(self):
        super(TestBlockdiagBuilder, self).setUp()
        self.builder = diag.LegacyBlockdiagBuilder('blockdiag')


class TestBlockdiagLoader(unittest.TestCase):
    def setUp(self):
        diag.BlockdiagLoader.search_builders = ['blockdiag']
        self.loader = diag.BlockdiagLoader()

    def test_available_builders(self):
        self.assertEqual(self.loader.available_builders(), ['blockdiag'])


if __name__ == '__main__':
    unittest.main()
