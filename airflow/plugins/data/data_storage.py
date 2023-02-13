import json
import pymongo
from data.data_utils.ufo_to_json import ufo_to_json
from data.data_utils.json_to_ufo import json_to_ufo

#Data management imports
from defcon import Font
from ufo2ft import compileOTF

class FontStorage:
    def __init__(self, ufo_collection: int):
        """
        Initializes a new instance of the DataLake class.

        Parameters:
        - mongos_port (int): The port number of the MongoDB instance to connect to.
        """
        self.ufo_collection = ufo_collection
        # self.client = pymongo.MongoClient(port=mongos_port)
        # self.ufo_fonts = self.client['ufo']['ufo_fonts']
        # self.ufo_fonts.create_index([('family', pymongo.ASCENDING), ('variant', pymongo.ASCENDING)], unique=True)

    def add_ufo_font(self, ufo_path: str, family: str, variant: str):
        """
        Adds a new UFO font to the data lake.

        Parameters:
        - ufo_path (str): The file path of the UFO font to add.
        - family (str): The font family name.
        - variant (str): The font variant name.
        """
        ufo_json = ufo_to_json(ufo_path)
        self.ufo_fonts.insert_one({'family': family, 'variant': variant, 'data': ufo_json})

    def get_ufo_font(self, family: str, variant: str) -> str:
        """
        Retrieves a UFO font from the data lake.

        Parameters:
        - family (str): The font family name.
        - variant (str): The font variant name.

        Returns:
        - The UFO font data as a string in XML format.
        """
        ufo_font_doc = self.ufo_fonts.find_one({'family': family, 'variant': variant})
        json_font = ufo_font_doc['data']
        json_to_ufo(json_font, f"{family}-{variant}.ufo")
        ufo_to_ttf(f"{family}-{variant}.ufo", f"{family}-{variant}.ttf")


    def delete_ufo_font(self, family: str, variant: str):
        """
        Deletes a UFO font from the data lake.

        Parameters:
        - family (str): The font family name.
        - variant (str): The font variant name.
        """
        self.ufo_fonts.delete_one({'family': family, 'variant': variant})

    def update_ufo_font(self, ufo_path: str, family: str, variant: str):
        """
        Updates an existing UFO font in the data lake.

        Parameters:
        - ufo_path (str): The file path of the UFO font to update.
        - family (str): The font family name.
        - variant (str): The font variant name.
        """
        ufo_json = ufo_to_json(ufo_path)
        self.ufo_fonts.update_one({'family': family, 'variant': variant}, {'$set': {'data': ufo_json}})

if "__main__" == __name__:
    family = "Alef"
    variant = "Regular"
    # Example usage
    ufo_path = f'../../data/processed/fonts/UFO/{family}/{family}-{variant}.ufo'

    # Connect to the MongoDB sharded cluster
    data_engine = FontStorage(27017)

    data_engine.delete_ufo_font(family, variant)

    # Add the UFO font to the database
    data_engine.add_ufo_font(ufo_path, family, variant)

    # Retrieve the UFO font from the database
    data_engine.get_ufo_font(family, variant)