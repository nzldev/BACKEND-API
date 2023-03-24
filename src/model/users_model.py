

# ************************CODE DESCRIPTION USERS_MODEL************************

    # all Functions get requests from controller
        # Function user_login : get the username and password from request body from client-side 
                    #and save the token in cookies with name token and value (token.value)
    
    # For the rest of function : check the token and if he have permission he can access to function
        # Function add_user : get the username and password passed from client-side
                        # and check if the username is not used from another user, then save the new user
        # Function update_user : get the username and password passed from client-side
                        # and make the updates of the user who have the id passed in path
        # Function delete_user : get the id in path for the user that will be deleted
                        # and make the delete of the user who have the id passed in path
        # Function get_user : get the id in path for the user searched
                        # and get the user who have the id=id_passed 
        # Function get_all_users : get all users with the informations : "id":1 , "username":"houssem", "password":"houssem", "type_id":1, role_id[1,2]


from app import app
from flask import request, make_response, jsonify
import psycopg2
from datetime import datetime, timedelta
import jwt
from db.database import connect
import json
import logging

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


            # Set the Authorization header with the Bearer token prefix
            response.headers['Authorization'] = f'Bearer {jwtoken}'

            # response.set_cookie("token", jwtoken)
            # response.set_cookie("token", jwtoken, httponly=True, path='/')
            # token = request.cookies.get('token')
            # print(token)
            # Return the success response with the token cookie set
            logging.info(f"{username} has logged in at {datetime.now()}")
            return response
        
        except Exception as e:
            return make_response({"erreur": str(e)}, 500)
        
    def add_user(self, data):
        try:
            # Decode the data bytes to string and parse as JSON
            data_str = data.decode('utf-8')
            data_dict = json.loads(data_str)

            new_username = data_dict['username']
            new_password = data_dict['password']
            # new_type_id = data_dict['type_id']
            new_type_id = 1

            # Check if the username already exists
            self.cur.execute(
                f"SELECT id FROM users WHERE username='{new_username}'")
            existing_user = self.cur.fetchone()
            if existing_user:
                return make_response({"message": f"Username {new_username} already exists"}, 400)
            # Insert the new user
            sql = """INSERT INTO users (username, password, type_id)
                    VALUES (%s, %s, %s)"""
            self.cur.execute(sql, (new_username, new_password, new_type_id))
            self.conn.commit()
            self.cur.execute(
                "SELECT currval(pg_get_serial_sequence('users', 'id'));")
            user_id = self.cur.fetchone()[0]
            # logging.info(f"{username} has logged in at {datetime.now()}")
            return make_response({"message": f"User with the id: {user_id} and name: {new_username} created successfully"}, 201)
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error retrieving add user: {e}"}, 500)

    def update_user(self, id, data):
        try:
            # Decode the data bytes to string and parse as JSON
            data_str = data.decode('utf-8')
            data_dict = json.loads(data_str)

            current_username = data_dict['username']
            current_password = data_dict['password']
            sql = """UPDATE users
                    SET username=%s,
                        password=%s
                    WHERE id=%s"""
            self.cur.execute(sql, (current_username, current_password, id))
            self.conn.commit()
            # Return the updated user
            updated_user = {
                "username": current_username,
                "password": current_password
            }
            return make_response(updated_user, 201)
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error retrieving update user : {e}"}, 500)

    def get_user(self, id):
        try:
            self.cur.execute("SELECT * FROM users WHERE id=%s", (id,))
            row = self.cur.fetchone()
            if row is not None:
                self.cur.execute(
                    "SELECT name FROM types WHERE id=%s", (row[3],))
                type_res = self.cur.fetchone()
                if type_res is not None:
                    user = dict(id=row[0], username=row[1], password=row[2],
                                type_id=row[3], USER_TYPE=type_res[0])
                return make_response(user, 200)
            else:
                return make_response({"message": "No user found !"}, 202)
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error retrieving get user : {e}"}, 500)

    def get_all_users(self):
        try:
            self.cur.execute("SELECT * FROM users")
            users = []
            for row in self.cur.fetchall():
                self.cur.execute(
                    "SELECT name FROM types WHERE id=%s", (row[3],))
                type_res = self.cur.fetchone()
                self.cur.execute(
                    "SELECT role_id FROM users_roles WHERE user_id=%s", (row[0],))
                role_res = self.cur.fetchall()
                roles = [r[0] for r in role_res]
                user = dict(id=row[0], username=row[1], password=row[2],
                            type_id=row[3], USER_TYPE=type_res[0], role_id=roles)
                users.append(user)

            if users:
                return make_response(users, 200)
            else:
                return make_response({"message": "No users found !"}, 202)
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error retrieving all users: {e}"}, 500)