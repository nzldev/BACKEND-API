from app import app
from flask import request, make_response, send_file , json
import psycopg2
from io import BytesIO
from db.database import connect


class profiles():
    def __init__(self):
        try:
            self.conn, self.cur = connect()
        except psycopg2.Error as error:
            print(error)
                
    def add_profile(self, data):
        try:
            # Decode the data bytes to string and parse as JSON
            data_str = data.decode('utf-8')
            data_dict = json.loads(data_str)
            
            new_name = data_dict['name']
            new_email = data_dict['email']
            new_telephone = data_dict['telephone']
            new_adresse = data_dict['adresse']
            new_image = data_dict['image']
            new_description = data_dict['description']
            new_user_id = data_dict['user_id']
            sql = """INSERT INTO profiles (name, email, telephone, adresse, image, description, user_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            self.cur.execute(sql, (new_name, new_email, new_telephone,
                                new_adresse, new_image, new_description, new_user_id))
            self.conn.commit()
            self.cur.execute(
                "SELECT currval(pg_get_serial_sequence('profiles', 'id'));")
            profile_id = self.cur.fetchone()[0]
            # profile_id = self.cur.lastrowid
            return make_response({"message": f"Profile with the id: {profile_id} created successfully"}, 201)
            # return f"Profile with the id: {profile_id} created successfully", 201
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error retrieving add profile : {e}"}, 500)
