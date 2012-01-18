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


class TestBlockdiagBuilder(unittest.TestCase):
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
        self.builder = diag.BlockdiagBuilder

    def test_attr(self):
        self.assertTrue(hasattr(self.builder, 'parse_string'))
        self.assertTrue(hasattr(self.builder, 'ScreenNodeBuilder'))
        self.assertTrue(hasattr(self.builder, 'DiagramDraw'))

    def test_build_png(self):
        png = self.builder().build(self.blockdiag_text, 'PNG',
                                   self.default_options)
        self.assertEqual(png[:8], ''.join(chr(x) for x in self.png_header))

    def test_build_svg(self):
        svg = self.builder().build(self.blockdiag_text, 'SVG',
                                   self.default_options)
        dom = minidom.parseString(svg)
        self.assertEqual(dom.doctype.name, 'svg')


class TestFunctions(unittest.TestCase):
    def test_builder_generation(self):
        for name in diag.available_builders:
            self.assertTrue(hasattr(diag, name.title() + 'Builder'))

    def test_get_builder(self):
        self.assertEqual(diag.get_builder('block'), diag.BlockdiagBuilder)
        with self.assertRaises(AttributeError):
            diag.get_builder('notexists')


if __name__ == '__main__':
    unittest.main()
