#Code Description:
    # Function token_auth : Verif if the current user has the permission for access to the api requested or not !



from functools import wraps
import psycopg2
from app import app
from urllib import request
from flask import make_response, request, json
import jwt
import re
from db.database import connect


class auth_model():
    
    def __init__(self):
        try:
            self.conn, self.cur = connect()
        except psycopg2.Error as error:
            print(error)

    def token_auth(self, endpoint=""):
        def inner1(func):
            @wraps(func)
            def inner2(*args, **kwargs):
                endpoint = request.url_rule.rule
                # print(endpoint)
                token = request.headers.get("Authorization", "").split(" ")[-1]
                # print(token)
                if token:
                    try:
                        jwtdecoded = jwt.decode(token, "HoussemYousfi", algorithms="HS256")
                        user_info = {
                            "user_id": jwtdecoded["user_id"],
                            "username": jwtdecoded["username"],
                            "password": jwtdecoded["password"],
                            "type_id": jwtdecoded["type_id"],
                            # "roles": jwtdecoded.get("roles"),
                            # "role_id": jwtdecoded.get("role_id"),
                            "role_ids": jwtdecoded.get("role_id", [])
                        }
                        # print(user_info)
                    except jwt.ExpiredSignatureError:
                        return make_response({"ERROR": "TOKEN_EXPIRED"}, 401)
                    
                    role_ids = user_info.get("role_ids", [])
                    if not role_ids:
                        return make_response({"ERROR": "USER_HAS_NO_ROLES"}, 401)
                    
                    self.cur.execute(f"SELECT id FROM permissions WHERE endpoint = '{endpoint}' AND method = '{request.method}'")
                    permission = self.cur.fetchone()
                    if permission is None:
                        return make_response({"ERROR": "INVALID_PERMISSION"}, 401)
                    per_id = permission[0]
                    # self.cur.execute(f"SELECT role_id from permissions_view WHERE endpoint = '{endpoint}' AND method = '{request.method}' ")
                    self.cur.execute(f"SELECT role_id FROM roles_permissions WHERE permission_id= '{per_id}'")
                    result = self.cur.fetchall()
                    if result is not None:
                        role_ids_db = [res[0] for res in result]
                        # if role_id in role_ids_db:
                        if set(role_ids).intersection(set(role_ids_db)):
                            return func(*args, **kwargs)
                        else:
                            return make_response({"ERROR": "INVALID_ROLE"}, 403)
                    else:
                        return make_response({"ERROR": "UNKNOWN_ENDPOINT"}, 404)
                else:
                    return make_response({"ERROR": "INVALID_TOKEN"}, 401)
            return inner2
        return inner1
    