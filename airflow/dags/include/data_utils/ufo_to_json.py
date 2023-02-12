import plistlib
import os

import xml.etree.ElementTree as ET
import json


def glif_to_json(glif_xml_string: str) -> dict:
    # parse the XML string
    root = ET.fromstring(glif_xml_string)

    # create a dictionary to hold the JSON object
    glyph = {}

    # add all attributes of the root element to the JSON object
    for attr, value in root.attrib.items():
        glyph[attr] = value

    # add the advance element to the JSON object
    advance = root.find('advance')
    if advance is not None:
        glyph['advance'] = {
            'width': advance.attrib.get('width', 0),
            'height': advance.attrib.get('height', 0)
        }

    # add the unicode elements to the JSON object
    glyph['unicode'] = []
    for unicode_elem in root.findall('unicode'):
        glyph['unicode'].append({'hex': unicode_elem.attrib['hex']})

    # add the note element to the JSON object
    note = root.find('note')
    if note is not None:
        glyph['note'] = note.text

    # add the image element to the JSON object
    image = root.find('image')
    if image is not None:
        glyph['image'] = {}
        for attr, value in image.attrib.items():
            glyph['image'][attr] = value

    # add the guideline elements to the JSON object
    glyph['guideline'] = []
    for guideline in root.findall('guideline'):
        guideline_dict = {}
        for attr, value in guideline.attrib.items():
            guideline_dict[attr] = value
        glyph['guideline'].append(guideline_dict)

    # add the outline element to the JSON object
    outline = root.find('outline')
    if outline is not None:
        glyph['outline'] = {
            'contour': [],
            'component': []
        }

        # add the contour elements to the JSON object
        for contour in outline.findall('contour'):
            contour_dict = {'point': []}
            for point in contour.findall('point'):
                point_dict = {}
                for attr, value in point.attrib.items():
                    point_dict[attr] = value
                contour_dict['point'].append(point_dict)
            glyph['outline']['contour'].append(contour_dict)

        # add the component elements to the JSON object
        for component in outline.findall('component'):
            component_dict = {}
            for attr, value in component.attrib.items():
                component_dict[attr] = value
            glyph['outline']['component'].append(component_dict)

    return glyph


def ufo_to_json(ufo_path):
    # Read in all plist files and convert to dictionaries
    plist_files = ['metainfo.plist', 'fontinfo.plist', 'groups.plist', 'kerning.plist',
                   'lib.plist', 'layercontents.plist', 'glyphs/contents.plist', 'glyphs/layerinfo.plist']
    plist_data = {}
    for plist_file in plist_files:
        if not os.path.exists(f'{ufo_path}/{plist_file}'):
            continue
        with open(f'{ufo_path}/{plist_file}', 'rb') as f:
            # replace dots in keys with underscores (to be compatible with MongoDB)
            k = plist_file.replace('.', '_')
            plist_data[k] = plistlib.load(f)
    # Read in GLIF files and convert to dictionaries
    glyph_data = {}

    for glyph_name, glif_fname in plist_data['glyphs/contents_plist'].items():
        # Read in GLIF file and convert to dictionary
        with open(f'{ufo_path}/glyphs/{glif_fname}', 'r') as f:
            glif_fn_no_extension = ".".join(glif_fname.split('.')[:-1])
            glyph_data[glif_fn_no_extension] = glif_to_json(f.read())

    if os.path.exists(f'{ufo_path}/features.fea'):
        with open(f'{ufo_path}/features.fea', "rb") as f:
            plist_data['features_fea'] = f.read()

    # Combine all data into a single dictionary
    ufo_data = {
        **plist_data,
        'glyphs': glyph_data
    }
    return ufo_data

if "__main__" == __name__:
    # Example usage
    ufo_path = '../../../../data/processed/fonts/UFO/Alef/Alef-Regular.ufo'
    ufo_dict = ufo_to_json(ufo_path)

    # Save to JSON file
    with open(f'{ufo_path}/../Alef-Regular.json', 'w') as f:
        json.dump(ufo_dict, f, indent=4)