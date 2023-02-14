import plistlib
import os
import xml.etree.ElementTree as ET
import json
from defcon import Font, Glyph, Guideline, Contour, Component

import matplotlib.pyplot as plt
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.svgLib.path import SVGPath
from fontTools.misc.transform import Identity
import matplotlib.patches as patches
from svgpath2mpl import parse_path
import matplotlib.transforms as transforms

svg_path_format="""<svg>
  <path d="%s" />
  Sorry, your browser does not support inline SVG.
</svg>"""

def transform_svg(svg, tx, ty, sx, sy):
    svgPath = SVGPath.fromstring(svg_path_format % svg, Identity.scale(sx, sy).translate(tx, ty))
    pen = SVGPathPen(None)
    svgPath.draw(pen)
    return pen.getCommands()

def glyph_to_svg_path(glyph, unitsPerEm):
    pen = SVGPathPen(glyph.getParent())
    glyph.draw(pen)
    svg = pen.getCommands()
    # normalize the svg path
    nsvg = transform_svg(svg, 0, 0, 1/unitsPerEm, 1/unitsPerEm)
    return nsvg


def plot_glyph(glyph, ax, unitsPerEm):
    svg = glyph_to_svg_path(glyph, unitsPerEm)

    if svg:
        patch_path = patches.PathPatch(parse_path(svg), facecolor="#f5f5f5")
        plt.gcf().gca().add_patch(patch_path)
        # Apply the necessary transformations to the glyph
        transform = transforms.Affine2D().translate(glyph.width / unitsPerEm, 0)
        patch_path.set_transform(transform + ax.transData)

    # set the x-axis and y-axis limits
    ax.set_xlim(0, int(glyph.advance[0]) / unitsPerEm)
    #ax.set_ylim(-1, 1)
    #ax.set_xlim(0, int(glyph.advance[0]))
    #ax.set_ylim(-unitsPerEm, unitsPerEm)

def create_glyph_example():
    font = Font()

    baseGlyph = font.newGlyph("baseGlyph")
    pointPen = baseGlyph.getPointPen()
    pointPen.beginPath()
    pointPen.addPoint((0, 0), "move")
    pointPen.addPoint((0, 100), "line")
    pointPen.addPoint((100, 100), "line")
    pointPen.addPoint((100, 0), "line")
    pointPen.addPoint((0, 0), "line")
    pointPen.endPath()
    
    assert baseGlyph.area == 10000

def glyph_json_to_Glyph(glyph_json: dict) -> Glyph:
    # create the glyph object
    glyph = Glyph()

    # set the glyph attributes
    for attr, value in glyph_json.items():
        setattr(glyph, attr, value)

    # set the advance
    advance = glyph_json.get('advance')
    if advance is not None:
        glyph.advance = (advance['width'], advance['height'])

    # set the unicode
    glyph.unicode = [unicode_dict['hex'] for unicode_dict in glyph_json.get('unicode', [])]

    # set the note
    glyph.note = glyph_json.get('note')

    # set the image
    glyph.image = glyph_json.get('image')

    # set the guidelines
    glyph.guidelines = [Guideline(**guideline_dict) for guideline_dict in glyph_json.get('guideline', [])]

    # draw the glyph
    pointPen = glyph.getPointPen()

    # set the outline
    outline_dict = glyph_json.get('outline')
    if outline_dict is not None:
        for contour_dict in outline_dict.get('contour', []):
            pointPen.beginPath()
            for point_dict in contour_dict.get('point', []):
                pointPen.addPoint((point_dict['x'], point_dict['y']), point_dict.get('type', None))
            pointPen.endPath()
        for component_dict in outline_dict.get('component', []):
            pointPen.addComponent(**component_dict)

    return glyph


def glyph_json_to_glif(glyph_json: dict) -> str:
    # create the root element
    root = ET.Element('glyph', attrib=glyph_json)

    # add the advance element
    advance = glyph_json.get('advance')
    if advance is not None:
        advance_elem = ET.SubElement(root, 'advance')
        advance_elem.attrib['width'] = str(advance['width'])
        advance_elem.attrib['height'] = str(advance['height'])

    # add the unicode elements
    for unicode_dict in glyph_json.get('unicode', []):
        unicode_elem = ET.SubElement(root, 'unicode')
        unicode_elem.attrib['hex'] = unicode_dict['hex']

    # add the note element
    note = glyph_json.get('note')
    if note is not None:
        note_elem = ET.SubElement(root, 'note')
        note_elem.text = note

    # add the image element
    image = glyph_json.get('image')
    if image is not None:
        image_elem = ET.SubElement(root, 'image')
        for attr, value in image.items():
            image_elem.attrib[attr] = value

    # add the guideline elements
    for guideline_dict in glyph_json.get('guideline', []):
        guideline_elem = ET.SubElement(root, 'guideline')
        for attr, value in guideline_dict.items():
            guideline_elem.attrib[attr] = value

    # add the outline element
    outline_dict = glyph_json.get('outline')
    if outline_dict is not None:
        outline_elem = ET.SubElement(root, 'outline')

        # add the contour elements
        for contour_dict in outline_dict.get('contour', []):
            contour_elem = ET.SubElement(outline_elem, 'contour')
            for point_dict in contour_dict.get('point', []):
                point_elem = ET.SubElement(contour_elem, 'point')
                for attr, value in point_dict.items():
                    point_elem.attrib[attr] = value

        # add the component elements
        for component_dict in outline_dict.get('component', []):
            component_elem = ET.SubElement(outline_elem, 'component')
            for attr, value in component_dict.items():
                component_elem.attrib[attr] = value

    # convert the ElementTree object to an XML string
    return ET.tostring(root, encoding='unicode')

def json_to_ufo(ufo_json: dict, ufo_path):
    # create the UFO directory if it doesn't exist
    if not os.path.exists(ufo_path):
        os.makedirs(ufo_path)

    # create the glyphs directory if it doesn't exist
    glyphs_path = f'{ufo_path}/glyphs'
    if not os.path.exists(glyphs_path):
        os.makedirs(glyphs_path)

    # write the plist files
    for plist_file, plist_data in ufo_json.items():
        if plist_file == 'glyphs' or plist_file == 'features_fea':
            continue
        plist_file = plist_file.replace('_', '.')
        plist_path = f'{ufo_path}/{plist_file}'
        with open(plist_path, 'wb') as f:
            plistlib.dump(plist_data, f)

    # write the glyph files
    glyphs = ufo_json['glyphs']
    for glyph_name, glyph_json in glyphs.items():
        glif_xml_string = glyph_json_to_glif(glyph_json)
        glif_path = f'{glyphs_path}/{glyph_name}.glif'
        with open(glif_path, 'w') as f:
            f.write(glif_xml_string)

    # write the features.fea file
    if 'features_fea' in ufo_json:
        features_fea_path = f'{ufo_path}/features.fea'
        with open(features_fea_path, 'w') as f:
            f.write(ufo_json['features_fea'])


def main():
    # load the JSON object
    with open('Alef-Regular.json', 'r') as f:
        ufo_json = json.load(f)

    # get glyph json for A 
    glif_name = ufo_json['glyphs/contents_plist']['A'].split('.')[0]
    glyph_json = ufo_json['glyphs'][glif_name]
    unitsPerEm = ufo_json['fontinfo_plist']['unitsPerEm']

    # create the Glyph object
    glyph = glyph_json_to_Glyph(glyph_json)

    # convert to svg path
    svg_path = svg_path_format % glyph_to_svg_path(glyph, unitsPerEm)
    print(svg_path)

    # create new figure
    _, ax = plt.subplots()

    # plot the glyph
    plot_glyph(glyph, ax, unitsPerEm)

    # create the UFO file
    ufo_path = 'Alef-Regular.ufo'
    json_to_ufo(ufo_json, ufo_path)

if __name__ == '__main__':
    main()