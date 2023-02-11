import plistlib
import os
import xml.etree.ElementTree as ET
import json

def json_to_glif(glyph_json: dict) -> str:
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
        glif_xml_string = json_to_glif(glyph_json)
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

    # create the UFO file
    ufo_path = 'Alef-Regular.ufo'
    json_to_ufo(ufo_json, ufo_path)

if __name__ == '__main__':
    main()