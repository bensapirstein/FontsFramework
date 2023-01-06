import json
import plistlib
import os
from fontTools.ufoLib import glifLib

def ufo_to_json(ufo_path):
    # Read in all plist files and convert to dictionaries
    plist_files = ['metainfo.plist', 'fontinfo.plist', 'groups.plist', 'kerning.plist', 'lib.plist', 'layercontents.plist']
    plist_data = {}
    for plist_file in plist_files:
        if not os.path.exists(f'{ufo_path}/{plist_file}'):
            continue
        with open(f'{ufo_path}/{plist_file}', 'rb') as f:
            plist_data[plist_file] = plistlib.load(f)

    # Read in GLIF files and convert to dictionaries
    glyph_data = {}
    for glyph_name in os.listdir(f'{ufo_path}/glyphs'):
        # Read in GLIF file and convert to dictionary
        with open(f'{ufo_path}/glyphs/{glyph_name}', 'r') as f:
            glyph_data[glyph_name] = f.read()

    # Combine all data into a single dictionary
    ufo_data = {
        **plist_data,
        'glyph_data': glyph_data
    }

    # Convert UFO data to JSON
    ufo_json = json.dumps(ufo_data)
    return ufo_json

# Example usage
ufo_path = '../../../data/processed/fonts/UFO/Alef/Alef-Regular.ufo'
ufo_json = ufo_to_json(ufo_path)
with open('ufo.json', 'w') as f:
  f.write(ufo_json)