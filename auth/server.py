import jwt
import datetime
import os
from flask import Flask, request
from flask_mysqldb import MySQL
from dotenv import load_dotenv

load_dotenv()

server = Flask(__name__)
mysql = MySQL(server)

server.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST")
server.config["MYSQL_USER"] = os.environ.get("MYSQL_USER")
server.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD")
server.config["MYSQL_DB"] = os.environ.get("MYSQL_DB")
server.config["MYSQL_PORT"] = os.environ.get("MYSQL_PORT")


@server.route("/login", methods=["POST"])
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return "missing credentials", 401

    cur = mysql.connection.cursor()
    res = cur.execute(
        "SELECT email, password FROM users WHERE email = %s", [auth.username])

    if res > 0:
        user = cur.fetchone()
        email, password = user

        if auth.username != email or auth.password != password:
            return "invalid credentials", 401
        else:
            return create_jwt(auth.username, os.environ.get("JWT_SECRET"), True)
    else:
        return 'invalid credentials', 401

@server.route("/validate", methods=["POST"])
def validate():
    encoded_jwt = request.headers.get("Authorization")
    if not encoded_jwt:
        return "missing credentials", 401


def create_jwt(username, secret, admin):
    return jwt.encode({
        "username": username,
        "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=1),
        "iat": datetime.datetime.utcnow(),
        "admin": admin
    }, secret, algorithm="HS256")


if __name__ == "__main__":
    server.run(host=os.environ.get("HOST"),
               port=os.environ.get("PORT"), debug=True)
