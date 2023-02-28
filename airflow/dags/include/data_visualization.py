import arabic_reshaper
from bidi.algorithm import get_display
import yaml
from include.mongo_utils import pymongo_get_ufo_collection
from include.data_utils.text_utils import animate_random_text

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from typing import List
from include.data_utils.text_utils import plot_glyph, plot_text

def generate_glyph_df(text: str, ufo_collection, n: int) -> pd.DataFrame:
    glyphs = []
    for char in text:
        cursor = ufo_collection.find(
            {f"unicodes_svg.{char}": {"$exists": True}},
            {"family": 1, "variant": 1, f"unicodes_svg.{char}.nsvg": 1, f"unicodes_svg.{char}.nwidth": 1}
        ).limit(n)
        for glyph in cursor:
            glyphs.append({
                "char": char,
                "family": glyph["family"],
                "variant": glyph["variant"],
                "nsvg": glyph["unicodes_svg"][char]["nsvg"],
                "nwidth": glyph["unicodes_svg"][char]["nwidth"]
             })
    return pd.DataFrame(glyphs)

class DataVisualization:
    def __init__(self, fonts_df: pd.DataFrame):
        self.fonts_df = fonts_df

    def plot_glyphs(self, char: str, n_rows: int = 4, n_cols: int = 4):
        fig, axs = plt.subplots(nrows=n_rows, ncols=n_cols, figsize=(8, 2*n_cols))
        fig.tight_layout(pad=0.3)

        # go over rows with the same character

        for i, (index, row) in enumerate(self.fonts_df[(self.fonts_df["char"] == char)].iterrows()):
            ax = axs[i // n_cols][i % n_cols]
            glyph_path = row["nsvg"]
            plot_glyph(glyph_path, 0, ax)
            ax.set_xticks([])
            ax.set_yticks([])

            #axs[i][0].set_ylabel(row["family"], rotation=0, labelpad=25)


        plt.show()

    def plot_word(self, word: str, fonts: List[str]):
        fig, axs = plt.subplots(nrows=len(fonts), figsize=(8, 2*len(fonts)))
        fig.tight_layout(pad=1.0)

        for i, family in enumerate(fonts):
            df = self.fonts_df[(self.fonts_df["family"] == family) & (self.fonts_df["char"].isin(word))]
            text = "".join(df["char"].tolist())
            svg = "".join(df["nsvg"].tolist())
            plot_text(svg, text, ax=axs[i])
            axs[i].set_title(family)

        plt.show()

    def plot_alphabets(self, fonts: List[str]):
        fig = plt.figure(figsize=(8, 6))
        gs = GridSpec(1, len(fonts))

        for i, family in enumerate(fonts):
            df = self.fonts_df[(self.fonts_df["family"] == family) & (self.fonts_df["char"].str.len() == 1)]
            chars = df["char"].tolist()
            svgs = df["nsvg"].tolist()

            ax = fig.add_subplot(gs[0, i])
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_title(family)
            for char, svg in zip(chars, svgs):
                plot_glyph(svg, 0, ax)
                ax.text(0, -50, char, ha="center", va="top", fontsize=16)

        plt.show()

    def plot_variants(self, char: str, families: List[str]):
        """
        Plots the variants of the given character for the given families.
        takes a Unicode character and a list of font families as input and generates a plot of the variants of the specified character in the specified font families.
        The plot consists of subplots, where each subplot corresponds to a font family and contains the variants of the character in that font family. 
        The title of each subplot is the name of the font family and the variant of the character.

        Args:
            char (str): The Unicode character to plot the variants of.
            families (List[str]): A list of font families to plot the variants in.
        """
        fig, axs = plt.subplots(nrows=len(families), figsize=(8, 2*len(families)))
        fig.tight_layout(pad=1.0)

        for i, family in enumerate(families):
            df = self.fonts_df[(self.fonts_df["family"] == family) & (self.fonts_df["char"] == char)]
            variants = df["variant"].tolist()
            svgs = df["nsvg"].tolist()

            for variant, svg in zip(variants, svgs):
                ax = axs[i]
                plot_glyph(svg, 0, ax)
                ax.set_title(f"{family} - {variant}")

        plt.show()

def create_multilingual_text_animation(text: str, ufo_collection, num_frames: int, output_file: str) -> None:
    """
    Creates a random multilingual text animation from the given text using glyphs from the provided UFO collection.

    Args:
        text (str): The multilingual text to animate.
        ufo_collection (pymongo.collection.Collection): The UFO collection to use for generating the glyphs.
        num_frames (int): The number of frames to use for the animation.
        output_file (str): The output file name to save the animation.

    Returns:
        None
    """
    # Reshape the text to display it correctly
    reshaped_text = arabic_reshaper.reshape(text)

    # Display the text in the correct direction
    bidi_text = get_display(reshaped_text)

    # get glyphs dataframe for the given text
    df = generate_glyph_df(bidi_text, ufo_collection, num_frames)

    # create and save the animation
    animate_random_text(df, bidi_text, num_frames, output_file)


def main():
    # Load settings from configuration file
    with open('../../../airflow_settings.yaml') as f:
        settings = yaml.safe_load(f)["airflow"]

    # Connect to MongoDB and get the UFO collection
    collection = pymongo_get_ufo_collection('FontsFramework', 'UFOs', settings)

    # Define the multilingual text to animate
    text = "שלום\nHello\nمرحبات"

    glyphs_df = generate_glyph_df(text, collection, n=16)

    # visualize glyphs
    viz = DataVisualization(glyphs_df)
    viz.plot_glyphs("ت", 4, 4)
    viz.plot_word("Hello, world!", ["Arial", "Courier", "Times New Roman"])

    # plot variants for the letter A
    viz.plot_variants("A", ["Arial", "Courier", "Times New Roman"])


if __name__ == "__main__":
    main()

