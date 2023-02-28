from defcon import Font
from svgpath2mpl import parse_path
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.transforms as transforms
import arabic_reshaper
from include.data_utils.glyph_utils import glyph_to_svg_path
from bidi.algorithm import get_display
import imageio
import numpy as np
import random
from PIL import Image

matplotlib.rcParams['figure.figsize'] = (12, 12)

def plot_glyph(svg, x_pos, ax):
    """
    Plot a glyph on the given axis. The glyph is plotted as a path patch.
    """

    if svg:
        patch_path = patches.PathPatch(parse_path(svg), facecolor="#000000")
        # Apply the necessary transformations to the glyph
        transform = transforms.Affine2D().translate(x_pos, 0)
        patch_path.set_transform(transform + ax.transData)
        ax.add_patch(patch_path)

def plot_text(font: Font, text: str):
    """
    Plot a text string using the given font.
    
    Parameters
    ----------
    font : defcon.Font
        The font to use.
    text : str 
        The text to plot.
    """

    # create a figure and an axis
    fig, ax = plt.subplots()

    # Initialize the current x position to 0
    x_pos = 0

    for i, char in enumerate(text):
        glyph_name = font.unicodeData[ord(char)][0]
        glyph = font[glyph_name]
        svg = glyph_to_svg_path(glyph)
        plot_glyph(svg, glyph.width, ax)
        kerning_value = 0 # font.kerning.get((glyph_name, font.unicodeData[ord(text[i+1])][0]), 0)

        # Update the current x position
        x_pos += glyph.width + kerning_value

        # set the x-axis and y-axis limits
        ax.set_xlim(0, x_pos)
        ax.set_ylim(-font.info.unitsPerEm, font.info.unitsPerEm)

    ax.set_aspect('equal')
    plt.show()

def plot_random_text(fonts_df, text):
    """
    Plot a text string using randomly picked glyphs from the provided fonts.

    Parameters
    ----------
    fonts_df : pandas.DataFrame
        A dataframe containing the glyphs for each character in the text.
        The dataframe should have columns: char, family, variant, nsvg, nwidth.
    text : str
        The text to plot.
    """

    # create a figure and an axis
    fig, ax = plt.subplots()

    # Initialize the current x position to 0
    x_pos = 0

    for i, char in enumerate(text):
        # Randomly pick a glyph from the dataframe for the current character
        char_df = fonts_df[fonts_df['char'] == char]
        if len(char_df) == 0:
            continue
        glyph_row = char_df.sample(n=1).iloc[0]
        glyph_path = glyph_row['nsvg']
        glyph_width = glyph_row['nwidth']

        # Plot the glyph
        plot_glyph(glyph_path, x_pos, ax)

        # Update the current x position
        x_pos += glyph_width

    # set the x-axis and y-axis limits
    ax.set_xlim(0, x_pos)
    ax.set_ylim(-1, 1)
    ax.set_xticks([])
    ax.set_yticks([])

    ax.set_aspect('equal')
    plt.show()


def animate_random_text(fonts_df, text, n_frames, gif_path):
    # create a figure and an axis
    fig, ax = plt.subplots()

    # Initialize the current x position to 0
    x_pos = 0

    # Create a list to store the frames of the animation
    frames = []

    # Create the first frame of the animation
    for i, char in enumerate(text):
        # Randomly pick a glyph from the dataframe for the current character
        char_df = fonts_df[fonts_df['char'] == char]
        if len(char_df) == 0:
            continue
        glyph_row = char_df.sample(n=1).iloc[0]
        glyph_path = glyph_row['nsvg']
        glyph_width = glyph_row['nwidth']

        # Plot the glyph
        plot_glyph(glyph_path, x_pos, ax)

        # Update the current x position
        x_pos += glyph_width

    # set the x-axis and y-axis limits
    ax.set_xlim(0, x_pos)
    ax.set_ylim(-1, 1)
    ax.set_xticks([])
    ax.set_yticks([])

    ax.set_aspect('equal')

    # Save the figure as a PNG image file
    fig.savefig("temp.png", dpi=300)
    image = Image.open("temp.png")
    frame = np.array(image)
    # Add the frame to the frames list
    frames.append(frame)

    # Create the rest of the frames
    for i in range(1, n_frames):
        # Choose a random character in the text to change
        char_idx = random.randint(0, len(text) - 1)

        # Randomly pick a new glyph from the dataframe for the chosen character
        char_df = fonts_df[fonts_df['char'] == text[char_idx]]
        if len(char_df) == 0:
            continue
        glyph_row = char_df.sample(n=1).iloc[0]
        glyph_path = glyph_row['nsvg']
        glyph_width = glyph_row['nwidth']

        # Update the glyph in the plot
        patch_path = ax.patches[char_idx]
        patch_path.remove()
        plot_glyph(glyph_path, x_pos, ax)

        # Update the current x position
        x_pos += glyph_width

        # set the x-axis and y-axis limits
        ax.set_xlim(0, x_pos)
        ax.set_ylim(-1, 1)
        ax.set_xticks([])
        ax.set_yticks([])

        ax.set_aspect('equal')

        # Save the figure as a PNG image file
        fig.savefig("temp.png", dpi=300)
        image = Image.open("temp.png")
        frame = np.array(image)
        # Add the frame to the frames list
        frames.append(frame)

    # Save the frames to a gif file
    imageio.mimsave(gif_path, frames, fps=10)



if "__main__" == __name__:
    text = get_display(arabic_reshaper.reshape('مرحبا يا عالم'))
    # text = "Hello World"
    ufo_path = '../../data/processed/fonts/UFO/Amiri/Amiri-Regular.ufo'
    font = Font(ufo_path)
    plot_text(font, text)