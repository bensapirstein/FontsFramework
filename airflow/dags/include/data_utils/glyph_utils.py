from defcon import Font
import numpy as np
from fontTools.pens.statisticsPen import StatisticsPen
from fontTools.svgLib.path import SVGPath
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.misc.transform import Identity

svg_path_format="""<svg>
  <path d="%s" />
  Sorry, your browser does not support inline SVG.
</svg>"""


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
