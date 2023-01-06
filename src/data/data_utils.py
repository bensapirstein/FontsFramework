from defcon import Font
#import extractor
import numpy as np
#from ufo2ft import compileOTF
from fontTools.pens.statisticsPen import StatisticsPen
from fontTools.svgLib.path import SVGPath
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.misc.transform import Identity

import xml.etree.ElementTree as ET
import bson


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

def xml_to_dict(root):
    if root.text is None:
        text = ''
    else:
        text = root.text
    res = {root.tag: {}}
    children = list(root)
    if children:
        for child in children:
            child_res = xml_to_dict(child)
            if child.tag in res[root.tag]:
                if not isinstance(res[root.tag][child.tag], list):
                    res[root.tag][child.tag] = [res[root.tag][child.tag]]
                res[root.tag][child.tag].append(child_res[child.tag])
            else:
                res[root.tag].update(child_res)
    else:
        res[root.tag]['value'] = text
    return res

def dict_to_xml(dictionary):
    def build_xml(parent, element_dict):
        if isinstance(element_dict, dict):
            for tag, value in element_dict.items():
                if isinstance(value, list):
                    for item in value:
                        build_xml(parent, {tag: item})
                else:
                    new_element = Element(tag)
                    parent.append(new_element)
                    build_xml(new_element, value)
        elif isinstance(element_dict, str):
            parent.text = element_dict
    root_tag = list(dictionary.keys())[0]
    root = Element(root_tag)
    build_xml(root, dictionary[root_tag])
    return root
