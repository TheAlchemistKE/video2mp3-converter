import os, gridfs, pika, json
from flask import Flask, request
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from auth import validate
from auth_svc import access
from storage import util

load_dotenv()

server = Flask(__name__)
server.config["MONGO_URI"] = "mongodb://host.minikube.internal:27017/videos"

mongo = PyMongo(server)

fs = gridfs.GridFS(mongo.db)

connnection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
channel = connnection.channel()


@server.route("/login", methods=["POST"])
def login():
    token, err = access.login(request)

    if not err:
        return token
    else:
        return err


@server.route("/upload", methods=["POST"])
def upload():
    access, err = validate.token(request)
    access = json.loads(access)

    if access["admin"]:
        if len(request.files) > 1 or len(request.form) < 1:
            return "exactly one file required", 400
        
        for _, f in request.files.items():
            err = util.upload(f, fs, channel, access)

            if err:
                return err
            
        return "success!", 200
    else:
        return "unauthorized", 401
    
@server.route('/download', methods=['GET'])
def download():
    pass

if __name__ == "__main__":
    server.run(host=os.environ.get("HOST"), port=os.environ.get("PORT"), debug=True)
