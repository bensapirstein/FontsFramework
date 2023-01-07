import bson.json_util
import math
import pymongo
from data_utils.ufo_to_json import ufo_to_json

class FontsDataEngine:
    def __init__(self, mongos_port):
        self.client = pymongo.MongoClient(port=mongos_port)
        self.ufo_fonts = self.client['ufo']['ufo_fonts']
        self.ufo_fonts.create_index([('family', pymongo.ASCENDING), ('variant', pymongo.ASCENDING)], unique=True)

    def add_ufo_font(self, ufo_path, family, variant):
        ufo_json = ufo_to_json(ufo_path)
        self.ufo_fonts.insert_one({'family': family, 'variant': variant, 'data': ufo_json})

    def get_ufo_font(self, family, variant):
        ufo_font_doc = self.ufo_fonts.find_one({'family': family, 'variant': variant})
        json_font = ufo_font_doc['data']
        return json_font

    def delete_ufo_font(self, family, variant):
        self.ufo_fonts.delete_one({'family': family, 'variant': variant})

    def update_ufo_font(self, ufo_path, family, variant):
        ufo_json = ufo_to_json(ufo_path)
        self.ufo_fonts.update_one({'family': family, 'variant': variant}, {'$set': {'data': ufo_json}})

if "__main__" == __name__:
    # Example usage
    ufo_path = '../../data/processed/fonts/UFO/Alef/Alef-Bold.ufo'

    # Connect to the MongoDB sharded cluster
    data_engine = FontsDataEngine(27017)

    # Add the UFO font to the database
    data_engine.add_ufo_font(ufo_path, 'Alef', 'Bold')

    # Retrieve the UFO font from the database
    retrieved_ufo_font_xml = data_engine.get_ufo_font('Alef', 'Bold')

    # Print the retrieved UFO font XML
    print(retrieved_ufo_font_xml)
