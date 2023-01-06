import bson.json_util
import data_utils
import math
import pymongo

class FontsDataEngine:
    def __init__(self, mongos_host, mongos_port, mongos_username=None, mongos_password=None):
        self.client = pymongo.MongoClient(f'mongodb://{mongos_username}:{mongos_password}@{mongos_host}:{mongos_port}/')
        self.ufo_fonts = self.client['ufo']['ufo_fonts']
        self.ufo_fonts.create_index([('family', pymongo.ASCENDING), ('variant', pymongo.ASCENDING)], unique=True)
        self.client.admin.command('enableSharding', 'ufo')
        self.client.admin.command('shardCollection', 'ufo.ufo_fonts', key={'family': 1, 'variant': 1})

    def add_ufo_font(self, ufo_font_xml, family, variant):
        ufo_font_dict = data_utils.xml_to_dict(ufo_font_xml)
        ufo_font_bson = bson.BSON.encode(ufo_font_dict)
        self.ufo_fonts.insert_one({'family': family, 'variant': variant, 'data': ufo_font_bson})

    def get_ufo_font(self, family, variant):
        ufo_font_doc = self.ufo_fonts.find_one({'family': family, 'variant': variant})
        ufo_font_bson = ufo_font_doc['data']
        ufo_font_dict = bson.BSON.decode(ufo_font_bson)
        ufo_font_xml = data_utils.dict_to_xml(ufo_font_dict)
        return ufo_font_xml

    def delete_ufo_font(self, family, variant):
        self.ufo_fonts.delete_one({'family': family, 'variant': variant})

    def update_ufo_font(self, ufo_font_xml, family, variant):
        ufo_font_dict = data_utils.xml_to_dict(ufo_font_xml)
        ufo_font_bson = bson.BSON.encode(ufo_font_dict)
        self.ufo_fonts.update_one({'family': family, 'variant': variant}, {'$set': {'data': ufo_font_bson}})

    def search_ufo_font(self, ufo_font_xml):
        ufo_font_dict = data_utils.xml_to_dict(ufo_font_xml)
        ufo_font_glyphs = ufo_font_dict['glyphs']
        for doc in self.ufo_fonts.find():
            existing_font_bson = doc['data']
            existing_font_dict = bson.BSON.decode(existing_font_bson)
            existing_font_glyphs = existing_font_dict['glyphs']
            if self._is_similar(ufo_font_glyphs, existing_font_glyphs):
                return existing_font_dict
        return None

    def _is_similar(self, ufo_font_glyphs, existing_font_glyphs):
        similarity_score = 0
        for glyph_name in ufo_font_glyphs:
            if glyph_name not in existing_font_glyphs:
                continue
            ufo_glyph = ufo_font_glyphs[glyph_name]
            existing_glyph = existing_font_glyphs[glyph_name]
            similarity_score += self._compare_glyphs(ufo_glyph, existing_glyph)
        return similarity_score / len(ufo_font_glyphs)

    def _compare_glyphs(self, ufo_glyph, existing_glyph):
        attributes = ('advance', 'unicode', 'meanX', 'meanY', 'stddevX', 'stddevY', 'area', 'bottomLeftX', 'bottomLeftY', 'topRightX', 'topRightY')
        ufo_attributes = [ufo_glyph[attr] for attr in attributes]
        existing_attributes = [existing_glyph[attr] for attr in attributes]

        dot_product = sum(ufo_attr * existing_attr for ufo_attr, existing_attr in zip(ufo_attributes, existing_attributes))
        ufo_magnitude = math.sqrt(sum(ufo_attr ** 2 for ufo_attr in ufo_attributes))
        existing_magnitude = math.sqrt(sum(existing_attr ** 2 for existing_attr in existing_attributes))

        return dot_product / (ufo_magnitude * existing_magnitude)




if "__main__" == __name__:
    # Connect to the MongoDB sharded cluster
    data_engine = FontsDataEngine('mongos.example.com', 27017, 'family', 'username', 'password')

    # Read a UFO font file as an XML string
    with open('font.ufo', 'r') as f:
        ufo_font_xml = f.read()

    # Add the UFO font to the database
    data_engine.add_ufo_font(ufo_font_xml, 'MyFont', 'Regular')

    # Retrieve the UFO font from the database
    retrieved_ufo_font_xml = data_engine.get_ufo_font('MyFont', 'Regular')

    # Print the retrieved UFO font XML
    print(retrieved_ufo_font_xml)
