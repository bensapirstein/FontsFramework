###############################################
# This DAG is used to granulate data from UFOs
###############################################

from defcon import Font
from include.data_utils.json_to_ufo import json_to_ufo
from include.data_utils.glyph_utils import glyph_stats, glyph_to_svg_path
import pandas as pd

def extract_glyphs_data(font: Font) -> pd.DataFrame:
    """
    Extract the data from the glyphs in the font. The data is returned as a
    Pandas DataFrame.

    Parameters
    ----------
    font : defcon.Font
        The font object.
    """

    # Create a list to store the glyph data
    glyph_data = []

    for glyph_name in font.keys():
        # Get the glyph object for the glyph
        glyph = font[glyph_name]

        meanX, meanY, stddevX, stddevY = glyph_stats(glyph)

        # Split the bounds tuple into separate fields
        bl_x, bl_y, tr_x, tr_y = glyph.bounds if glyph.bounds else [None]*4

        # Create a dictionary to store the glyph data
        glyph_dict = {
            #'glyph_name': glyph_name,
            #'svg': glyph_to_svg_path(glyph),
            'advance': glyph.width,
            #'unicode' : glyph.unicode,
            'meanX' : meanX,
            'meanY' : meanY,
            'stddevX' : stddevX,
            'stddevY' : stddevY,
            'area' : glyph.area,
            'bottomLeftX' : bl_x,
            'bottomLeftY' : bl_y,
            'topRightX' : tr_x,
            'topRightY' : tr_y,
        }
        # Add the glyph data to the list
        glyph_data.append(glyph_dict)
    
    return glyph


def granulate_data(ufo_path: str) -> pd.DataFrame:
    """
    Granulate the data from the font.
    
    Parameters
    ----------
    ufo_path : str
        The path to the UFO file.
    """

    # convert to defcon font
    font = Font(ufo_path)

    font_info = {
        'ascender' : font.info.ascender,
        'capHeight' : font.info.capHeight,
        'descender' : font.info.descender,
        'italicAngle' : font.info.italicAngle,
        'xHeight' : font.info.xHeight,
    }

    # TODO: normalize glyph using unitsPerEm 
    unitsPerEm = font.info.unitsPerEm # 1000 or 2048

    glyph_data = extract_glyphs_data(font)
    
    return font_info, pd.DataFrame(glyph_data).agg(['mean', 'std']) # Granulate the data
