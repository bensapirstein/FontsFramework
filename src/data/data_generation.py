import defcon

def create_unified_font(font_paths):
    # Create a new font object
    new_font = defcon.Font()
    new_font.ufoVersion = "3.0"

    # Load the source fonts
    fonts = [defcon.Font(path) for path in font_paths]

    unite_infos(new_font, fonts)

    # Copy the glyphs from the source fonts to the new font
    for font in fonts:
        for glyph in font:
            new_font.newGlyph(glyph.name)
            new_font[glyph.name].unicode = glyph.unicode
            new_font[glyph.name].width = glyph.width
            new_font[glyph.name].note = glyph.note
            new_font[glyph.name].lib[glyph.name] = glyph.lib

    return new_font

def unite_infos(new_font, fonts):

    new_font.familyName = " ".join(font.info.familyName for font in fonts)
    pass