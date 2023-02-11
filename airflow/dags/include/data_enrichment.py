from defcon import Font
from include.data_utils.json_to_ufo import json_to_ufo
from include.data_utils.glyph_utils import glyph_stats, glyph_to_svg_path

def enrich_data(font):
    ufo_path = f"/tmp/{font['family']}-{font['variant']}.ufo"
    json_to_ufo(font["data"], ufo_path)
    # get the font
    font = Font(ufo_path)
    
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
            'glyph_name': glyph_name,
            'svg': glyph_to_svg_path(glyph),
            'advance': glyph.width,
            'unicode' : glyph.unicode,
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
    
    return glyph_data
