"""
_________________________________
SERVER_NAME
Server description goes here
__________________________________
"""

import flask
import flask_cors
import pymongo
import os
import dotenv

from models.response import Response

"""
__________________________________
DEVELOPMENTAL ENVIRONMENT VARIABLES
__________________________________
"""
if os.environ.get("environment") != "production":
	dotenv.load_dotenv()


"""
__________________________________
SERVER INSTANCE SETUP
__________________________________
"""
server_instance = flask.Flask(__name__,
			static_folder="./assets/",
            static_url_path="/server_name/assets/")
flask_cors.CORS(server_instance, resources={r"*": {"origins": "*"}})

"""
__________________________________
DATABASE CONNECTION
__________________________________
"""
client = None
if os.environ.get("MONGO_CONNECTION"):
	client = pymongo.MongoClient(os.environ.get("MONGODB_CONNECTION"))


"""
__________________________________
SERVER INSTANCE ROUTES
__________________________________
"""
# Returns status of the server
@server_instance.route("/template/status", methods=["GET"])
@flask_cors.cross_origin()
def status():
	print(flask.request)
	return Response(cd=200, msg="Running.").to_json()