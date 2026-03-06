from flask import render_template,redirect , url_for
from database_creator import *
from routes import *
# tous les fonctions utils
from flask import session

# ---- Session ----- 
def save_session(data:dict):
    for key ,value in data.items() :
        session[key] = value
    print("session saved!")
def session_exists():
    return "userid" in session

# ---- POST data ----
def user_exists(username:str):
    result = cursor.execute(f"SELECT username,password from users where username = '{username}'")
    result = cursor.fetchone() # si une ligne exist au min
    if result is None :
        # not exists
        return False
    else :
        # 1. get the userid
        userid = "" # get from database
        session["userid"] = userid
        return True

def empty(data:str):
    return data == ""