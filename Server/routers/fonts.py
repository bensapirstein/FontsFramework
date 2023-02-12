from flask import Blueprint,jsonify, request
from BLL.font_bl import FontBL

fonts = Blueprint('fonts', __name__)

font_bl = FontBL()

#Get All
@fonts.route("/", methods=['GET'])
def get_all_fonts():
    fonts = font_bl.get_all_fonts()
    return jsonify(fonts)

#Get Font by id
#Get All
@fonts.route("/<id>", methods=['GET'])
def get_font(id):
    font = font_bl.get_font(id)
    return jsonify(font)

@fonts.route("/<id>/glyphs", methods=['GET'])
def get_font_glyphs(id):
    font = font_bl.get_font(id)
    return jsonify(font)


#Create new
@fonts.route("/", methods=['POST'])
def add_font():
    obj = request.json
    result = font_bl.add_font(obj)
    return jsonify(result)


#Update Font

@fonts.route("/<id>", methods=['PUT'])
def update_font(id):
    obj = request.json
    result = font_bl.update_font(id,obj)
    return jsonify(result)


#Delete
@fonts.route("/<id>", methods=['DELETE'])
def delete_font(id):
    result = font_bl.delete_font(id)
    return jsonify(result)


@fonts.route("glyphs/<glyphName>", methods=['GET'])
def get_fonts_By_glyph_Name(glyphName):
    font = font_bl.get_all_fonts_With_GlyphName(glyphName)
    return jsonify(font)
