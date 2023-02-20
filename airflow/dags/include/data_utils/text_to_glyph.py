import json
from svgpath2mpl import parse_path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.transforms as transforms
import arabic_reshaper
from glyph_utils import glyph_to_svg_path
from bidi.algorithm import get_display
import pandas as pd
from defcon import Font
import yaml
from include.mongo_utils import pymongo_get_ufo_collection

def get_glyphs_for_character(unicode_char):
    # Load the JSON files for the glyphs and contents plist
    with open('glyphs.json', 'r') as f:
        glyphs_data = json.load(f)
    with open('contents.plist.json', 'r') as f:
        contents_data = json.load(f)

    # Create an empty list to store the matching glyphs
    matching_glyphs = []

    # Loop over all glyphs in the glyphs data
    for glyph_name, glyph_data in glyphs_data['glyphs'].items():
        # Check if the glyph has a Unicode character that matches the search character
        for unicode_data in glyph_data.get('unicode', []):
            if unicode_data.get('hex') == unicode_char:
                # If there's a match, add the glyph to the list of matching glyphs
                matching_glyphs.append(glyph_name)
                break
        # Check if the glyph is a component that references another glyph
        for component_data in glyph_data.get('outline', {}).get('component', []):
            if component_data.get('base') == glyph_name:
                # If the component references the glyph itself, skip it to avoid infinite recursion
                continue
            # Check if the referenced glyph has a Unicode character that matches the search character
            referenced_glyph_data = glyphs_data['glyphs'].get(component_data.get('base'))
            if referenced_glyph_data is not None:
                for unicode_data in referenced_glyph_data.get('unicode', []):
                    if unicode_data.get('hex') == unicode_char:
                        # If there's a match, add the referenced glyph to the list of matching glyphs
                        matching_glyphs.append(component_data.get('base'))
                        break

    # Create an empty list to store the paths to the matching glyphs
    matching_glyph_paths = []

    # Loop over all keys in the contents data
    for glyph_name, glyph_path in contents_data['glyphs/contents_plist'].items():
        # Check if the key matches one of the matching glyphs
        if glyph_name in matching_glyphs:
            # If there's a match, add the path to the matching glyph to the list
            matching_glyph_paths.append(glyph_path)

    # Return the list of matching glyph paths
    return matching_glyph_paths

def get_glyphs_for_text(text):
    # Load the fonts JSON object
    with open('fonts.json') as f:
        fonts = json.load(f)

    # List to store all the glyphs
    glyphs = []

    # Iterate through all the fonts
    for font in fonts:
        # Load the contents plist for the font
        with open(fonts[font]['contents_plist']) as f:
            contents = json.load(f)

        # Iterate through all the characters in the text
        for char in text:
            # Get the filename of the glyph for the character from the contents plist
            filename = contents.get(char.encode('unicode_escape').decode('utf-8'))

            if filename:
                # Load the glyph json file for the character
                with open('glyphs/' + filename) as f:
                    glyph = json.load(f)

                # Add the glyph to the list
                glyphs.append(glyph)

    return glyphs



def text_to_glyphs(json_obj: dict, text: str):
    """
    Fetches all glyphs for all fonts in the JSON object and plots the text using those glyphs.
    
    Parameters
    ----------
    json_obj : dict
        The JSON object containing font data.
    text : str 
        The text to plot.
    """
    
    # create a figure and an axis
    fig, ax = plt.subplots()

    # Initialize the current x position to 0
    x_pos = 0

    for i, char in enumerate(text):
        glyph_name = json_obj["glyphs"].get(ord(char))
        if not glyph_name:
            continue
        glyph_data = json_obj["fonts"][glyph_name]["glyphs"][glyph_name]
        glyph_path = glyph_data.get("svg")
        if not glyph_path:
            continue
        glyph_width = glyph_data.get("width", 0)
        patch_path = patches.PathPatch(parse_path(glyph_path), facecolor="#f5f5f5")
        plt.gcf().gca().add_patch(patch_path)
        # Apply the necessary transformations to the glyph
        transform = transforms.Affine2D().translate(glyph_width, 0)
        patch_path.set_transform(transform + ax.transData)

        kerning_value = 0 # TODO: handle kerning

        # Update the current x position
        x_pos += glyph_width + kerning_value

        # set the x-axis and y-axis limits
        ax.set_xlim(0, x_pos)
        ax.set_ylim(-json_obj["units_per_em"], json_obj["units_per_em"])

    ax.set_aspect('equal')
    plt.show()

import unicodedata

def unicode_to_postscript(char: str) -> str:
    """
    Converts a Unicode character to its corresponding PostScript name.
    """
    name = unicodedata.name(char, None)
    if name:
        name = name.replace(' ', '')
        name = name.replace('-', '')
        name = name.replace(',', '')
        name = name.replace('.', '')
        name = name.replace(';', '')
        name = name.replace('_', '')
        name = name.replace('(', '')
        name = name.replace(')', '')
        name = name.lower()
    return name


import pandas as pd
import pymongo
from pymongo.collection import Collection
from bson.objectid import ObjectId
import random

import pandas as pd
from bson.objectid import ObjectId

def get_glyphs_dataframe(text: str, ufo_collection) -> pd.DataFrame:
    """
    Returns a pandas dataframe containing relevant glyphs for the given text.

    Parameters
    ----------
    text : str
        The text to find relevant glyphs for.
    ufo_collection : pymongo.collection.Collection
        The MongoDB collection containing UFO font data.

    Returns
    -------
    pd.DataFrame
        A pandas dataframe containing the relevant glyphs for the given text.
    """
    glyphs = []
    for char in text:
        postscript = unicode_to_postscript(char)
        cursor = ufo_collection.aggregate([
            {"$match": {"glyphs": postscript}},
            {"$sample": {"size": 20}},
            {"$project": {
                "family": 1,
                "variant": 1,
                "glyph": {
                    "$filter": {
                        "input": "$glyphs",
                        "as": "glyph",
                        "cond": {"$eq": ["$$glyph.postscriptName", postscript]}
                    }
                }
            }}
        ])
        for font in cursor:
            if len(font["glyph"]) > 0:
                glyph = font["glyph"][0]
                glyphs.append({
                    "font_family": font["family"],
                    "font_variant": font["variant"],
                    "unicode": ord(char),
                    "postscript": postscript,
                    "outline": glyph["outline"],
                    "advance": glyph["advanceWidth"]
                })

    if glyphs:
        return pd.DataFrame(glyphs)
    else:
        return pd.DataFrame(columns=["family", "variant", "char", "svg"])


import aglfn

def text_to_glyph_names(text):
    glyph_names = []
    for char in text:
        glyph_name = aglfn.name(char)
        if glyph_name:
            glyph_names.append(glyph_name)
    return glyph_names




def main():
    print(aglfn.names)
    print(aglfn.glyphs)

    print(text_to_glyph_names('HELLO'))
    with open('../../../airflow_settings.yaml') as f:
        settings = yaml.safe_load(f)["airflow"]
    collection = pymongo_get_ufo_collection('FontsFramework', 'UFOs', settings)
    
    # Get the text to plot
    text = "مرحبا بالعالم"

    # Reshape the text to display it correctly
    reshaped_text = arabic_reshaper.reshape(text)

    # Display the text in the correct direction
    bidi_text = get_display(reshaped_text)

    # Plot the text using the glyphs
    df = get_glyphs_dataframe(bidi_text, collection)

    print(df)
    

if __name__ == "__main__":
    main()

