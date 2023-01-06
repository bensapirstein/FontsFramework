from defcon import Font
from svgpath2mpl import parse_path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from data_utils import glyph_to_svg_path

def plot_text(ufo_path, text):
    font = Font(ufo_path)

    # create a figure and an axis
    fig, ax = plt.subplots()

    # set the x-axis and y-axis limits
    ax.set_xlim(0, font.info.unitsPerEm)
    ax.set_ylim(0, font.info.unitsPerEm)

    for char in text:
        glyph_name = font.unicodeData[ord(char)][0]
        glyph = font[glyph_name]
        svg = glyph_to_svg_path(glyph)
        if svg:
            patch_path = patches.PathPatch(parse_path(svg), facecolor="#f5f5f5", zorder=0)
            plt.gcf().gca().add_patch(patch_path)
    plt.show()

if "__main__" == __name__:
    plot_text('../../data/processed/fonts/UFO/Alef/Alef-Regular.ufo', 'שלום עולם')

