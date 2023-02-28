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
    svgPath = SVGPath.fromstring(svg_path_format % svg, Identity.scale(sx, sy).translate(tx, ty))
    pen = SVGPathPen(None)
    svgPath.draw(pen)
    return pen.getCommands()

def normalize_svg(svg, meanX, meanY, stddevY):
    return transform_svg(svg, -meanX, -meanY, np.abs(1/stddevY), np.abs(1/stddevY))

# write normalize_svg again but suggest a better name for it reflecting the fact that it uses euclidean distance to normalize
def normalize_svg_euclidean(svg, meanX, meanY, stddevX, stddevY):
    return transform_svg(svg, -meanX, -meanY, np.abs(1/stddevX), np.abs(1/stddevY))

# write a function that uses unitsPerEm to normalize the svg path
def normalize_svg_unitsPerEm(svg, unitsPerEm):
    return transform_svg(svg, 0, 0, 1/unitsPerEm, 1/unitsPerEm)

def normalize_glyph(glyph):
    return transform_svg(glyph["svg"], -glyph["meanX"], -glyph["meanY"],
                        np.abs(1/glyph["stddevX"]), np.abs(1/glyph["stddevY"]))

def glyphs_to_svg_paths(ufo_path):
    font = Font(ufo_path)
    unitsPerEm = font.info.unitsPerEm

    # write it in list comprehension
    glyphs = {chr(glyph.unicode): {
        "svg": glyph_to_svg_path(glyph),
        "width": glyph.width,
        "nwidth": glyph.width/unitsPerEm,
        } for glyph in font if glyph.unicode}
    
    # normalize the svg paths using unitsPerEm under "nsvg" key
    for glyph in glyphs:
        glyphs[glyph]["nsvg"] = normalize_svg_unitsPerEm(glyphs[glyph]["svg"], unitsPerEm)

    return glyphs
    