from defcon import Font
import random

def create_shuffled_font(font_paths):
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

def get_font_combinations(subsets, fonts, num_fonts):

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



def create_unified_font(font_paths):
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

def unite_infos(new_font, fonts):

    new_font.info.familyName = " ".join(font.info.familyName for font in fonts)
    new_font.info.styleName = " ".join(font.info.styleName for font in fonts)