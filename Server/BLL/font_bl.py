from cmath import log
from pymongo import MongoClient
from bson import ObjectId

svg_path_format="""<svg>
  <path d="%s" />
  Sorry, your browser does not support inline SVG.
</svg>"""

class FontBL:
    def __init__(self):
        self.__client = MongoClient("mongodb+srv://fouad:8vmcWmV5gD9CZEnn@cluster0.slwp6m3.mongodb.net")
        self.__db = self.__client["FontsFramework"]
        self.__collection = self.__db["UFOs"]

    def get_all_fonts(self):
       fonts = list(self.__collection.find({}))
       return fonts

    def get_font(self,id):
        font = self.__collection.find_one({ "_id" : ObjectId(id) })
        return font


    def add_font(self,obj):
        self.__collection.insert_one(obj)
        return 'Created with ID' + str(obj["_id"])    

    def update_font(self,id,obj):
        self.__collection.update_one({"_id" : ObjectId(id)}, {"$set" : obj})
        return 'Updated!' 

    def delete_font(self,id):
        self.__collection.delete_one({"_id" : ObjectId(id)})
        return 'Deleted!'  
    


    def get_all_fonts_With_GlyphName(self,glyphName):
        field_name_plist = "data.glyphs/contents_plist.{}".format(glyphName)
        query_plist = {field_name_plist: {"$exists": True, "$ne": None}}

        unitsPerEm_query = {"data.fontinfo_plist.unitsPerEm": {"$exists": True, "$ne": None}}

        projection_plist = {"_id": 1, "family": 1, "variant": 1, field_name_plist: 1}
        glyphNamesPList = list(self.__collection.find(query_plist,projection_plist))
        # data.glyphs/contents_plist.A
        if len(glyphNamesPList) == 0:
            return glyphNamesPList
        
        glif_filename = glyphNamesPList[0]['data']['glyphs/contents_plist'][glyphName]

        glif_name = glif_filename.split(".")[0]

        field_name_glyph = "data.glyphs.{}".format(glif_name)
        query_glyph = {field_name_glyph: {"$exists": True, "$ne": None}}
        projection_glyph = {"_id": 1, "family": 1, "variant": 1, field_name_glyph: 1,\
                        "data.fontinfo_plist.unitsPerEm":1}
        glypsList = list(self.__collection.find(query_glyph,projection_glyph))
        resp = {'glyphs':glypsList,'Glyph Name':glif_name}
        # convert to svg path
        for glyph_json in resp['glyphs']:
            glyph = glyph_json_to_Glyph(glyph_json)
            svg_path = svg_path_format % glyph_to_svg_path(glyph, unitsPerEm)
            # add svg path to response
            
        return resp