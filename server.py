"""
_________________________________
SERVER_NAME
Server description goes here
__________________________________
"""

from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
from pymongo import MongoClient
from os import environ
from dotenv import load_dotenv

from models.response import Response

"""
__________________________________
DEVELOPMENTAL ENVIRONMENT VARIABLES
__________________________________
"""
if environ.get("environment") != "production":
	load_dotenv()


"""
__________________________________
SERVER INSTANCE SETUP
__________________________________
"""
server_instance = Flask(__name__,
			static_folder="./assets/",
            static_url_path="/server_name/assets/")
CORS(server_instance, resources={r"*": {"origins": "*"}})

"""
__________________________________
DATABASE CONNECTION
__________________________________
"""
client = None
if environ.get("MONGO_CONNECTION"):
	client = MongoClient(environ.get("MONGODB_CONNECTION"), tlsInsecure=True)


"""
__________________________________
SERVER INSTANCE ROUTES
__________________________________
"""
# Returns status of the server
@server_instance.route("/template/status", methods=["GET"])
@cross_origin()
def status():
	return Response(cd=200, msg="Running.").to_json()