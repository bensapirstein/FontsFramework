# Description: This script contains functions for collecting data from the Google Fonts API and downloading the fonts.
# Import necessary libraries
import ast
import pandas as pd
import os
from tqdm import tqdm
import json
import zipfile
import requests
from include.data_utils.font_to_ufo import ttf_to_ufo, var_ttf_to_ufo
from include.data_utils.ufo_to_json import ufo_to_json
from pymongo.collection import Collection

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


def filter_fonts(df: pd.DataFrame, num_fonts: int=None, categories: list=None, subsets: list=None, families: list=None, ufo_collection: Collection=None) -> pd.DataFrame:
    """
    This function selects a subset of fonts from the specified DataFrame based on the categories and subsets.
    It returns a random sample of the specified number of fonts.
    If no number is specified, it returns all the fonts in the dataset that match the specified categories and subsets.
    If a MongoDB collection is provided, the function filters out fonts that already exist in the collection

    Parameters:
    - df (pd.DataFrame): A Pandas DataFrame containing a list of fonts, with a 'category' column specifying the font category and a 'subsets' column specifying the supported character subsets.
    - num_fonts (int): The number of fonts to select from the dataset. If not specified, all the fonts in the dataset that match the specified categories and subsets will be returned.
    - categories (list): A list of font categories to filter the dataset by.
    - subsets (list): A list of character subsets to filter the dataset by.
    - families (list): A list of font families to filter the dataset by.
    - ufo_collection (Collection): A MongoDB collection containing the fonts that already exist in the dataset.

    Returns:
    - pd.DataFrame: A Pandas DataFrame containing a list of fonts, with a 'category' column specifying the font category and a 'subsets' column specifying the supported character subsets.

    Example:
    - font_dataset = select_fonts(fonts_info_df, None, categories=['sans-serif'], subsets=['latin', 'cyrillic'])
    """

    # Filter the font DataFrame by the specified categories
    if categories:
        print(f"Selected categories: {categories}.")
        df = df[df['category'].isin(categories)]

    # Filter the font DataFrame by the specified subsets
    if subsets:
        print(f"Selected subsets: {subsets}.")
        df = df[df["subsets"].apply(lambda x: any(lang in x for lang in subsets))]

    # Filter the font DataFrame by the specified font families
    if families:
        print(f"Selected families: {families}.")
        df = df[df['family'].isin(families)]

    if ufo_collection:
        # The function removes fonts that are already present in the specified MongoDB collection
        existing_families = [doc['family'] for doc in ufo_collection.find()]

        print(f"The following families already exist in the MongoDB collection and will be dropped: "
              f"{[family for family in existing_families if family in df['family'].tolist()]}")
        df = df[~df['family'].isin(existing_families)]

    # Return the generated dataset of fonts
    if num_fonts:
        if num_fonts < df.shape[0]:
            print(f"Selected {num_fonts} random fonts out of {df.shape[0]}.")
            return df.sample(num_fonts)
        else:
            print(f"Requested number of fonts is greater than the remaining amount. Returning {df.shape[0]} fonts.")
            return df



def download_fonts(font_dataset: pd.DataFrame, font_folder: str) -> pd.DataFrame:
    """
    This function downloads the fonts from the specified dataset and saves them in the specified folder.

    Parameters:
    - font_dataset (pd.DataFrame): A Pandas DataFrame containing a list of fonts, with a 'category' column specifying the font category and a 'subsets' column specifying the supported character subsets.
    - font_folder (str): The path to the folder where the fonts will be saved.

    Returns:
    - pd.DataFrame: A Pandas DataFrame containing a list of fonts, with a 'category' column specifying the font category and a 'subsets' column specifying the supported character subsets.

    Example:
    - font_dataset = download_fonts(font_dataset, "data/fonts")
    """

    # Create a folder to store the font files
    if not os.path.exists(font_folder):
        os.makedirs(font_folder)

    families_paths = []
    # Iterate through each font in the dataset
    for _, row in tqdm(font_dataset.iterrows(), total=font_dataset.shape[0]):
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

def parse_list(string): 
    """
    This function parses a string containing a list of values and returns a list of the values.
    """
    return [s.strip("''") for s in string.strip('[]').split(', ')]

def convert_folder_to_ufo(fonts_path: str):
    """
    This function converts the fonts in the specified folder to UFO format and saves them in the specified folder.

    Parameters:
    - fonts_path (str): The path to the folder where the fonts will be saved.
    """
    # Create a folder to store the UFO files
    output_path = os.path.join(fonts_path, "ufo")
    
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Recursively search for TTF files in the fonts path
    ttf_files = []
    for root, dirs, files in os.walk(fonts_path):
        for file in files:
            if file.endswith('.ttf'):
                ttf_files.append(os.path.join(root, file))
    
    # Convert the TTF files to UFO format
    for ttf_file in tqdm(ttf_files):
        ufo_file_path = os.path.join(output_path, os.path.basename(ttf_file).replace(".ttf", ".ufo"))
        ttf_to_ufo(ttf_file, ufo_file_path)


# Receive another parameter for which rows of the df should be executed
def convert_df_to_ufo(df: pd.DataFrame, fonts_path: str):
    """
    This function converts the fonts in the specified dataset to UFO format and saves them in the specified folder.

    Parameters:
    - df (pd.DataFrame): A Pandas DataFrame containing a list of fonts, with a 'category' column specifying the font category and a 'subsets' column specifying the supported character subsets.
    - fonts_path (str): The path to the folder where the fonts will be saved.
    """
    # Parse the list columns
    df['subsets'] = df['subsets'].apply(parse_list)
    df['category'] = df['category'].apply(parse_list)
    df['file_path'] = df['file_path'].apply(parse_list)
    
    print(df.head())

    # Create a folder to store the UFO files
    if not os.path.exists(os.path.join(fonts_path, "UFO")):
        os.makedirs(os.path.join(fonts_path, "UFO"))

    # Create a Pandas DataFrame to store the font families, their subsets, categories, and master and variant files
    ufo_df = pd.DataFrame(columns=['family', 'subsets', 'category', 'master', 'variants'])
    for _, row in tqdm(df.iterrows(), total=df.shape[0], desc="Converting to UFO..."):
        # print row keys
        master = None
        file_path = row["file_path"]
        family = row["family"]
        print(family)
        # Set the file path of the UFO file
        family_folder = os.path.join(fonts_path, f"UFO/{family}")
        if not os.path.exists(family_folder):
            os.makedirs(family_folder)

        variants = {}
        for ttf_file_path in file_path:
            # Get the file name and extension of the TTF file
            ttf_file_name, ttf_file_extension = os.path.splitext(ttf_file_path)

            # Get the variant name from the TTF file name
            variant = ttf_file_name.split("-")[-1]

            ufo_file_path = os.path.join(family_folder, f"{family}-{variant}.ufo")

            # Convert the TTF file to a UFO file
            if "Variable" in variant:
                if not os.path.exists(ufo_file_path):
                    var_ttf_to_ufo(ttf_file_path, ufo_file_path)
                master = ufo_file_path
            else:
                if not os.path.exists(ufo_file_path):
                    ttf_to_ufo(ttf_file_path, ufo_file_path)
                variants[variant] = ufo_file_path

        # Add the converted UFO file information to the dataframe
        ufo_df = ufo_df.append({'family': family, 'subsets': row["subsets"], 'category': row["category"], 'master': master, 'variants': variants}, ignore_index=True)
    return ufo_df

def upload_ufos(data_file: str, ufo_collection: Collection):
    """
    This function uploads the UFO files in the specified dataset to the specified MongoDB collection.

    Parameters:
    - data_file (str): The path to the CSV file containing the UFO dataset.
    - ufo_collection (pymongo.collection.Collection): The MongoDB collection to upload the UFO files to.

    Returns:
    - failed_cases (list): A list of the font families that failed to upload.
    """
    failed_cases = []
    df = pd.read_csv(data_file, converters={"subsets": parse_list, "variants":ast.literal_eval})
    print(f"Uploading {df.shape[0]} fonts to MongoDB...")
    for _, row in tqdm(df.iterrows(), total=df.shape[0], desc="Uploading Fonts..."):
        family = row['family']
        variants = row['variants']
        subsets = row['subsets']
        print(f"Uploading {len(variants)} variants for {family}...")
        for variant, ufo_file_path in variants.items():
            print(f"Variant: {variant}")
            try:
                # Open the UFO file for the font
                ufo_json = ufo_to_json(ufo_file_path)
                print("Keys: ")
                print(ufo_json.keys())
                ufo_collection.insert_one({'family': family, 'variant': variant, 'data': ufo_json, 'subsets': subsets})
            except Exception as e:
                failed_cases.append({'family': family, 'variant': variant, 'error': str(e)})
    return failed_cases