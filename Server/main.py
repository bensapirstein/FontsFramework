from flask import Flask
import json
from bson import ObjectId
from flask_cors import CORS
import sys
import BLL.json_to_ufo
from routers.fonts import fonts

class JSONEncoder(json.JSONEncoder):
    def default(self, obj) :
        if isinstance(obj, ObjectId):
            return str(obj)
        return json.JSONEncoder.default(self,obj)

app = Flask(__name__)
CORS(app)

app.json_encoder = JSONEncoder


app.register_blueprint(fonts, url_prefix="/fonts")

app.run()