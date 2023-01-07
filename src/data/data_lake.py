import json
import math
import pymongo
from data_utils.ufo_to_json import ufo_to_json
from data_utils.json_to_ufo import json_to_ufo
from data_utils.ufo_to_ttf import ufo_to_ttf

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
        json_to_ufo(json.loads(json_font), f"{family}-{variant}.ufo")
        ufo_to_ttf(f"{family}-{variant}.ufo", f"{family}-{variant}.ttf")


    def delete_ufo_font(self, family, variant):
        self.ufo_fonts.delete_one({'family': family, 'variant': variant})

    def update_ufo_font(self, ufo_path, family, variant):
        ufo_json = ufo_to_json(ufo_path)
        self.ufo_fonts.update_one({'family': family, 'variant': variant}, {'$set': {'data': ufo_json}})

if "__main__" == __name__:
    family = "Amiri"
    variant = "Regular"
    # Example usage
    ufo_path = f'../../data/processed/fonts/UFO/{family}/{family}-{variant}.ufo'

    # Connect to the MongoDB sharded cluster
    data_engine = FontsDataEngine(27017)

    data_engine.delete_ufo_font(family, variant)

    # Add the UFO font to the database
    data_engine.add_ufo_font(ufo_path, family, variant)

    # Retrieve the UFO font from the database
    retrieved_ufo_font_xml = data_engine.get_ufo_font(family, variant)

    # Print the retrieved UFO font XML
    print(retrieved_ufo_font_xml)
