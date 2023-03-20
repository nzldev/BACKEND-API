from app import app
from flask import request, make_response, jsonify
import psycopg2
from datetime import datetime, timedelta
import jwt
from db.database import connect
import json
from flask_jwt_extended import JWTManager, unset_jwt_cookies, jwt_required

class users():

    def __init__(self):
        try:
            self.conn, self.cur = connect()
        except psycopg2.Error as error:
            print(error)

    def user_login(self, data):
        try:
            # Decode the data bytes to string and parse as JSON
            data_str = data.decode('utf-8')
            data_dict = json.loads(data_str)

            # Retrieve the username and password from the parsed data
            username = data_dict['username']
            password = data_dict['password']

            # Check if the username and password are valid
            self.cur.execute(
                "SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
            result = self.cur.fetchone()
            if not result:
                # If the username or password are incorrect, return a failure response
                return make_response({"message": "Incorrect username or password"}, 401)

            # If the username and password are correct, create a token and set it as a cookie
            user_id = result[0]
            self.cur.execute(
                f"SELECT users_roles.role_id FROM users LEFT JOIN users_roles ON users.id = users_roles.user_id WHERE users.id = {user_id}")
            res = self.cur.fetchall()
            roles = [r[0] for r in res]
            payload = {
                "user_id": result[0],
                "username": result[1],
                "password": result[2],
                "type_id": result[3],
                "role_id": roles,
                "exp": int((datetime.now() + timedelta(minutes=45)).timestamp())
            }
            jwtoken = jwt.encode(payload, "HoussemYousfi", algorithm="HS256")
            response = make_response({'token': jwtoken}, 200)
            response.set_cookie("token", jwtoken)
            # Return the success response with the token cookie set
            return response
        except Exception as e:
            return make_response({"erreur": str(e)}, 500)
        