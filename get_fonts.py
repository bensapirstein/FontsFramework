# Import necessary libraries
import pandas as pd
import requests
import os
from tqdm import tqdm
import json
import zipfile

def get_fonts_info(api_key: str) -> pd.DataFrame:
    """
    This function retrieves the list of fonts available from the Google Fonts API and returns it as a Pandas DataFrame.

    Parameters:
    - api_key (str): The API key for the Google Fonts API.

    Returns:
    - pd.DataFrame: A Pandas DataFrame containing the list of fonts, with each row representing a font and each column
      containing information about the font.

    Example:
    - fonts_info_df = get_fonts_info(api_key)
    """
    # Set the API endpoint for the Google Fonts API
    GOOGLE_FONTS_API_ENDPOINT = 'https://www.googleapis.com/webfonts/v1/webfonts'

    # Set the parameters for the API request
    params = {
        'key': api_key,
        'sort': 'popularity'
    }

    # Make the API request to get the list of fonts
    response = requests.get(GOOGLE_FONTS_API_ENDPOINT, params=params)

    # Parse the response as JSON
    fonts = json.loads(response.text)

    # Return as DataFrame
    return pd.DataFrame(fonts['items'])


def select_fonts(df: pd.DataFrame, num_fonts: int=None, categories: list=None, subsets: list=None) -> pd.DataFrame:
    """
    This function selects a subset of fonts from the specified DataFrame based on the categories and subsets.
    It returns a random sample of the specified number of fonts.
    If no number is specified, it returns all the fonts in the dataset that match the specified categories and subsets.

    Parameters:
    - df (pd.DataFrame): A Pandas DataFrame containing a list of fonts, with a 'category' column specifying the font category and a 'subsets' column specifying the supported character subsets.
    - num_fonts (int): The number of fonts to select from the dataset. If not specified, all the fonts in the dataset that match the specified categories and subsets will be returned.
    - categories (list): A list of font categories to filter the dataset by.
    - subsets (list): A list of character subsets to filter the dataset by.

    Returns:
    - pd.DataFrame: A Pandas DataFrame containing the selected fonts.

    Example:
    - font_dataset = select_fonts(fonts_info_df, None, categories=['sans-serif'], subsets=['latin', 'cyrillic'])
    """

    # Filter the font DataFrame by the specified categories
    if categories:
        df = df[df['category'].isin(categories)]

    # Filter the font DataFrame by the specified subsets
    if subsets:
        df = df[df["subsets"].apply(lambda x: any(lang in x for lang in subsets))]

    # Return the generated dataset of fonts
    return df.sample(num_fonts) if num_fonts else df



def download_fonts(font_dataset: pd.DataFrame, font_folder: str) -> pd.DataFrame:
    """
    This function downloads the full zip of the fonts, including variable font files, for each font in the specified dataset.
    The zip files are saved in a 'zips' subfolder in the 'fonts' folder. The file paths of the TTF files are added to the
    'file_path' column of the font dataset.

    Parameters:
    - font_dataset (pd.DataFrame): A Pandas DataFrame containing a list of fonts, with a 'family' column specifying the
      font family name.

    Returns:
    - pd.DataFrame: The input font dataset with the 'file_path' column updated with the file paths of the TTF files.

    Example:
    - font_dataset = select_fonts(fonts_info_df, None, categories=['sans-serif'], subsets=['latin', 'cyrillic'])
    - font_dataset = download_font_zip(font_dataset)
    """

    # Create a folder to store the font files
    if not os.path.exists(font_folder):
        os.makedirs(font_folder)

    families_paths = []
    # Iterate through each font in the dataset
    for index, row in tqdm(font_dataset.iterrows()):
        # Get the font family
        family = row['family']

        # Create a folder for the font family
        family_folder = os.path.join(font_folder, family)
        if not os.path.exists(family_folder):
            os.makedirs(family_folder)

        # Set the URL for the font family's ZIP file
        url = f"https://fonts.google.com/download?family={family}"

        # Send a request to the URL and save the response as a file
        response = requests.get(url)
        zip_path = os.path.join(family_folder, f"{family}.zip")
        with open(zip_path, 'wb') as f:
            f.write(response.content)

        # Unzip the file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(family_folder)

        # Recursively search for TTF files in the unzipped folder
        ttf_files = []
        for root, dirs, files in os.walk(family_folder):
            for file in files:
                if file.endswith('.ttf'):
                    ttf_files.append(os.path.join(root, file))

        families_paths.append(ttf_files)
    return font_dataset.assign(file_path=families_paths)
