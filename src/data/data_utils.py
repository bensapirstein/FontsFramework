from defcon import Font
#import extractor
import numpy as np
#from ufo2ft import compileOTF
from fontTools.pens.statisticsPen import StatisticsPen
from fontTools.svgLib.path import SVGPath
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.misc.transform import Identity

# import cairo


svg_format="""<svg>
  <path d="%s" />
  Sorry, your browser does not support inline SVG.
</svg>"""

def parse_list(string: str) -> list:
    """Convert a string representation of a list to a list."""
    return [s.strip("''") for s in string.strip('[]').split(', ')]

def ttf_to_ufo(ttf_file_path: str, ufo_file_path: str):
    # Convert TTF file to UFO
    ufo = Font()
    try:
        extractor.extractUFO(ttf_file_path, ufo)
    except Exception as e:
        print(e)
        print(f"While parsing {ttf_file_path}")

    ufo.save(ufo_file_path)

def var_ttf_to_ufo(ttf_file_path: str, ufo_file_path: str):
    # TODO: Change the implementation to fit variable fonts
    # Convert TTF file to UFO
    ufo = Font()
    try:
        extractor.extractUFO(ttf_file_path, ufo)
    except Exception as e:
        print(e)
        print(f"While parsing {ttf_file_path}")

    ufo.save(ufo_file_path)

def ufo_to_ttf(ufo_file_path, ttf_file_path):
    ufo = Font(ufo_file_path)
    otf = compileOTF(ufo)
    otf.save(ttf_file_path)

def glyph_to_svg_path(glyph):
    pen = SVGPathPen(glyph.getParent())
    glyph.draw(pen)
    return pen.getCommands()

def glyph_stats(glyph):
    pen = StatisticsPen(glyph.font)
    glyph.draw(pen)
    return pen.meanX, pen.meanY, pen.stddevX, pen.stddevY

def transform_svg(svg, tx, ty, sx, sy):
    svgPath = SVGPath.fromstring(svg_format % svg, Identity.scale(sx, sy).translate(tx, ty))
    pen = SVGPathPen(None)
    svgPath.draw(pen)
    return pen.getCommands()

def normalize_svg(svg, meanX, meanY, stddevY):
    return transform_svg(svg, -meanX, -meanY, np.abs(1/stddevY), np.abs(1/stddevY))

def normalize_glyph(glyph):
    return transform_svg(glyph["svg"], -glyph["meanX"], -glyph["meanY"],
                        np.abs(1/glyph["stddevX"]), np.abs(1/glyph["stddevY"]))
