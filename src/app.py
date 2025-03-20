from flask import Flask, jsonify, json, request
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_mysqldb import MySQL
import logging
app = Flask(__name__)

conexion = MySQL(app)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#MOSTRAR TODOS LOS USUARIOS 
@app.route("/users", methods = ["GET"])
def listar_usuarios():
    try:
        cursor = conexion.connection.cursor()
        query = """SELECT * FROM users"""
        cursor.execute(query)
        datos = cursor.fetchall()
        usuarios = []
        for dato in datos:
            usuario = {"user_id": dato[0],
                       "user_handle": dato[1],
                       "email_address": dato[2],
                       "first_name": dato[3],
                       "last_name": dato[4],
                       "phone_number": dato[5],
                       "follower_count": dato[6],
                       "created_at": dato[7]}
            usuarios.append(usuario)
        return jsonify({"Usuarios": usuarios})
        
    except Exception as e:
        return jsonify({"Mensaje":"Error"}), 500
#MOSTRAR TODOS LOS SEGUIDORES 
@app.route("/followers", methods = ["GET"])
def listar_follows():
    try: 
        cursor = conexion.connection.cursor()
        query = """SELECT * FROM followers"""
        cursor.execute(query)
        tabla = cursor.fetchall()
        follows = []
        for fila in tabla:
            follow = {"follower_id":fila[0], "following_id": fila[1]}
            follows.append(follow)
        return jsonify({"Follows": follows})
    except Exception as e:
        return jsonify({"Mensaje": "Error"}), 500

#MOSTRAR TODOS LOS USUARIOS CON UN DETERMINADO ID
@app.route("/users/<user_id>", methods = ["GET"])
def listar_usuario(user_id):
    try:
        cursor = conexion.connection.cursor()
        query = f"""SELECT * FROM users WHERE user_id = {user_id} """
        cursor.execute(query)
        dato = cursor.fetchone()
        if dato != None:
            usuario = {"user_id": dato[0],
                        "user_handle": dato[1],
                        "email_address": dato[2],
                        "first_name": dato[3],
                        "last_name": dato[4],
                        "phone_number": dato[5],
                        "follower_count": dato[6],
                        "created_at": dato[7]}
        return jsonify({"Usuario": usuario})
    except Exception as e:
        return jsonify({"Mensaje": "Error"}), 500

#MOSTRAR TODOS LOS FOLLOWERS CON UN DETERMINADO FOLLOWING_ID 
@app.route("/followers/<following_id>", methods = ["GET"])
def listar_follow(following_id):
    try:
        cursor = conexion.connection.cursor()
        query = f"""SELECT * FROM followers WHERE following_id = {following_id}"""
        cursor.execute(query)
        datos = cursor.fetchall()#aquí pongo fetchall porque hay más de un follower_id que sigue al mismo following_id, por lo que quiero que salgan todos
        if datos != None:
            return jsonify({"follower_id": datos[0], "following_id": datos[1]})
    except Exception as e:
        return jsonify({"Mensaje": "Error"}), 500
    
#AÑADIR USERS
@app.route("/users", methods = ["POST"])
def añadir_user():
    try:
        cursor = conexion.connection.cursor()
        query = f"""INSERT INTO users (user_id, user_handle, email_address, first_name, last_name, phone_number, follower_count, created_at)
        VALUES ({request.json["user_id"]}, {request.json["user_handle"]}, {request.json["email_address"]}, {request.json["first_name"]}, 
        {request.json["last_name"]}, {request.json["phone_number"]}, {request.json["follower_count"]}, {request.json["created_at"]})"""
        cursor.execute(query)
        conexion.connection.commit()
        return jsonify({"Mensaje": "Usuario añadido correctamente"})
    except Exception as e:
        raise e

    

#AÑADIR FOLLOWERS    
@app.route("/followers", methods = ["POST"])
def añadir_follow():
    try:
        cursor= conexion.connection.cursor()
        query = f"""INSERT INTO followers (follower_id, following_id)
        VALUES
        ({request.json["follower_id"]}, {request.json["following_id"]})"""
        cursor.execute(query)
        conexion.connection.commit()
        return jsonify({"Mensaje":"Followers registrados"})
    except Exception as e:
        return jsonify({"Mensaje": "Error"}), 500
    


def pagina_no_encontrada(error):
    return jsonify({"Error":"La página que intentas buscar no existe..."})


if __name__ == "__main__":
    app.config.from_object(config["development"])
    app.register_error_handler(404, pagina_no_encontrada)
    app.run()