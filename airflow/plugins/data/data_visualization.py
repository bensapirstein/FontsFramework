from defcon import Font
from svgpath2mpl import parse_path
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.transforms as transforms
import arabic_reshaper
from data.data_utils import glyph_to_svg_path
from bidi.algorithm import get_display

matplotlib.rcParams['figure.figsize'] = (12, 12)

def plot_text(font, text):

    # create a figure and an axis
    fig, ax = plt.subplots()

    # Initialize the current x position to 0
    x_pos = 0

    for i, char in enumerate(text):
        glyph_name = font.unicodeData[ord(char)][0]
        glyph = font[glyph_name]
        svg = glyph_to_svg_path(glyph)

        kerning_value = 0

        if svg:
            patch_path = patches.PathPatch(parse_path(svg), facecolor="#f5f5f5")
            plt.gcf().gca().add_patch(patch_path)
            # Apply the necessary transformations to the glyph
            transform = transforms.Affine2D().translate(x_pos + kerning_value, 0)
            patch_path.set_transform(transform + ax.transData)

        # Update the current x position
        x_pos += glyph.width + kerning_value

        # set the x-axis and y-axis limits
        ax.set_xlim(0, x_pos)
        ax.set_ylim(-font.info.unitsPerEm, font.info.unitsPerEm)

    ax.set_aspect('equal')
    plt.show()

if "__main__" == __name__:
    text = get_display(arabic_reshaper.reshape('مرحبا يا عالم'))
    # text = "Hello World"
    ufo_path = '../../data/processed/fonts/UFO/Amiri/Amiri-Regular.ufo'
    font = Font(ufo_path)
    plot_text(font, text)

