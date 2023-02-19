from defcon import Font
import random

def create_shuffled_font(font_paths: list) -> Font:
    """
    Create a new font with the glyphs from the source fonts shuffled.
    
    Parameters
    ----------
    font_paths : list
        A list of paths to the source fonts.

    Returns
    -------
    defcon.Font
        A new font object with the glyphs from the source fonts shuffled.

    """
    # Create a new font object
    new_font = Font()
    new_font.ufoVersion = "3.0"

    # Load the source fonts
    fonts = [Font(path) for path in font_paths]

    unite_infos(new_font, fonts)

    # Create a union of all glyph sets
    glyph_names = set()
    for font in fonts:
        glyph_names.update(font.keys())

    # for each glyph in the union, copy a glyph at random from the source fonts
    for glyph_name in glyph_names:
        font = random.choice(fonts)
        glyph = font[glyph_name]
        new_font.newGlyph(glyph_name)
        new_font[glyph_name].unicode = glyph.unicode
        new_font[glyph_name].width = glyph.width
        new_font[glyph_name].note = glyph.note
        new_font[glyph_name].lib[glyph_name] = glyph.lib
        glyph.draw(new_font[glyph_name].getPen())

    return new_font

def get_font_combinations(subsets: list, fonts: dict, num_fonts: int) -> list:
    """
    Returns a list of font combinations.
    
    Parameters
    ----------
    subsets : list
        A list of font subsets.
    fonts : dict
        A dictionary of fonts, where the keys are the font subsets and the values are lists of font paths.
    num_fonts : int 
        The number of font combinations to return.

    Returns 
    -------
    list
        A list of font combinations, where each combination is a dictionary of font paths, where the keys are the font subsets and the values are font paths.
    """

    # Create a list of all possible combinations
    combinations = []
    for i in range(num_fonts):
        # Initialize an empty combination
        combination = {}

        # Add a random font for each subset to the combination
        for subset in subsets:
            available = fonts[subset]
            font = random.choice(available)
            combination[subset] = font

        # Add the combination to the list of possibilities
        combinations.append(combination)

    return combinations



def create_unified_font(font_paths: list) -> Font:
    """
    Create a new font with the glyphs from the source fonts.
    
    Parameters
    ----------
    font_paths : list
        A list of paths to the source fonts.

    Returns
    -------
    defcon.Font
        A new font object with the glyphs from the source fonts.
    """
    # Create a new font object
    new_font = Font()
    new_font.ufoVersion = "3.0"

    # Load the source fonts
    fonts = [Font(path) for path in font_paths]

    unite_infos(new_font, fonts)

    # Copy the glyphs from the source fonts to the new font
    for font in fonts:
        for glyph in font:
            new_font.newGlyph(glyph.name)
            new_font[glyph.name].unicode = glyph.unicode
            new_font[glyph.name].width = glyph.width
            new_font[glyph.name].note = glyph.note
            new_font[glyph.name].lib[glyph.name] = glyph.lib
            glyph.draw(new_font[glyph.name].getPen())

    return new_font

def unite_infos(new_font: Font, fonts: list):
    """
    Unite the font infos of the source fonts into the new font.

    Parameters
    ----------
    new_font : defcon.Font
        The new font object.
    fonts : list
        A list of source font objects.
    """

    new_font.info.familyName = " ".join(font.info.familyName for font in fonts)
    new_font.info.styleName = " ".join(font.info.styleName for font in fonts)