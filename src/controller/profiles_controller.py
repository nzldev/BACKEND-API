from app import app
from model.profiles_model import profiles
from model.auth_model import auth_model
from flask import request, make_response, send_file
import traceback
from datetime import datetime


obj = profiles()
auth = auth_model()

@app.route("/profiles", methods=["POST"])
@auth.token_auth()
def add_profile():
    try:
        return obj.add_profile(request.data)
    except Exception as e:
        traceback.print_exc()
        return make_response(f"error in add profile controller: {e}", 204)
    