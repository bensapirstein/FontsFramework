from cmath import log
from pymongo import MongoClient
from bson import ObjectId


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
        projection_plist = {"_id": 1, "family": 1, "variant": 1, field_name_plist: 1}
        glyphNamesPList = list(self.__collection.find(query_plist,projection_plist))
        # data.glyphs/contents_plist.A
        if len(glyphNamesPList) == 0:
            return glyphNamesPList
        
        actual_GlyphFileName = glyphNamesPList[0]['data']['glyphs/contents_plist'][glyphName]

        actual_Glyph_Str = actual_GlyphFileName[:actual_GlyphFileName.find(".glif")]

        field_name_glyph = "data.glyphs.{}".format(actual_Glyph_Str)
        query_glyph = {field_name_glyph: {"$exists": True, "$ne": None}}
        projection_glyph = {"_id": 1, "family": 1, "variant": 1, field_name_glyph: 1}
        glypsList = list(self.__collection.find(query_glyph,projection_glyph))
        resp = {'glyphs':glypsList,'actualGlyphName':actual_Glyph_Str}
        # glyph name 
        return resp