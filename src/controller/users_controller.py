from app import app
from model.users_model import users
from model.auth_model import auth_model
from flask import request, make_response
import traceback


obj = users()
auth = auth_model()

@app.route("/user/login", methods=["POST"])
def user_login():
    try:
        return obj.user_login(request.data)
    except Exception as e:
        traceback.print_exc()
        return make_response(f"Error user_login controller : {e}", 204)
    