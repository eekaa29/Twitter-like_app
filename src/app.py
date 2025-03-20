from flask import Flask, jsonify, json, request
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_mysqldb import MySQL

app = Flask(__name__)

conexion = MySQL(app)

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
        return jsonify({"Users": usuarios})
        
    except Exception as e:
        return jsonify({"Error": str(e)}), 400
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
        return jsonify({"Error": str(e)}), 400

#MOSTRAR USUARIO CON UN DETERMINADO ID
@app.route("/users/<user_id>", methods = ["GET"])
def listar_usuario(user_id):
    try:
        cursor = conexion.connection.cursor()
        query = """SELECT * FROM users WHERE user_id = %s """ #El $s es evitar usar el .format, evitando fallos de sintaxis y riesgo de inyecciones SQL 
        if verificar_user(user_id):
            cursor.execute(query, user_id)
            dato = cursor.fetchone()
            usuario = {"user_id": dato[0],
                        "user_handle": dato[1],
                        "email_address": dato[2],
                        "first_name": dato[3],
                        "last_name": dato[4],
                        "phone_number": dato[5],
                        "follower_count": dato[6],
                        "created_at": dato[7]}
            return jsonify({"User": usuario})
        return jsonify({"Error": f"User with user_id {user_id} does not exists"})
    except Exception as e:
        return jsonify({"Error": str(e)}), 400

#MOSTRAR TODOS LOS FOLLOWERS DE UN DETERMINADO USER 
@app.route("/followers/<following_id>", methods = ["GET"])
def listar_follow(following_id):
    try:
        cursor = conexion.connection.cursor()
        query = """SELECT * FROM followers WHERE following_id = %s"""
        if verificar_user(following_id):
            cursor.execute(query, following_id)
            datos = cursor.fetchall()#aquí pongo fetchall() porque hay más de un follower_id que sigue al mismo following_id, por lo que quiero que salgan todos
            follower_list = [follower[0] for follower in datos]# Datos es un lisata de tuplas;meto en la lista el primer valor de cada tupla
            conexion.connection.commit()
            return jsonify({"following_id": following_id, "followers": follower_list})
        return jsonify({"Error": f"User with following_id {following_id} does not exists"}) 
    except Exception as e:
        return jsonify({"Error": str(e)}), 400
    
#AÑADIR USERS
@app.route("/users", methods = ["POST"])
def añadir_user():
    try:
        cursor = conexion.connection.cursor()
        query = """INSERT INTO users (user_handle, email_address, first_name, last_name, phone_number, follower_count)
        VALUES (%s, %s, %s, %s, %s, %s)"""
        data = [request.json["user_handle"], request.json["email_address"], request.json["first_name"], 
        request.json["last_name"], request.json["phone_number"], request.json["follower_count"]]
        cursor.execute(query, data)
        conexion.connection.commit()
        return jsonify({"Message": "User successfully added"})
    except Exception as e:
        return jsonify({"Error": str(e)}), 400    

#AÑADIR FOLLOWERS    
@app.route("/followers", methods = ["POST"])
def añadir_follow():
    try:
        cursor= conexion.connection.cursor()
        query = """INSERT INTO followers (follower_id, following_id)
        VALUES (%s, %s)"""
        datos = [request.json["follower_id"], request.json["following_id"]]
        cursor.execute(query,datos)
        conexion.connection.commit()
        return jsonify({"Message":"Follow added"})
    except Exception as e:
        return jsonify({"Error": str(e)}), 400
    
#ELIMINAR USER
@app.route("/users/<user_id>", methods = ["DELETE"])
def delete_users(user_id):
    try: 
        cursor = conexion.connection.cursor()
        query1 = """DELETE FROM users WHERE user_id = (%s)"""
        usuario = user_id
        if verificar_user(usuario) == True:
            cursor.execute(query1, usuario)
            conexion.connection.commit()
            return jsonify({"Message": "User successfully deleted"})
        return jsonify({"Error": f"User with user_id {usuario} does not exists"})
    except Exception as e:
        return jsonify({"Error": str(e)})

#MODIFICAR USERS
@app.route("/users/<user_id>", methods = ["PUT"])
def modify_user(user_id):
    cursor = conexion.connection.cursor()
    query = """UPDATE users SET first_name = %s WHERE user_id = %s"""
    if verificar_user(user_id):
        cursor.execute(query, (request.json["first_name"], user_id))
        conexion.connection.commit()
        return jsonify({"Message": f"User with user_id {user_id} has been updated "})
    return jsonify({"Message": f"User with user_id {user_id} does not exists"})

def pagina_no_encontrada(error):
    return jsonify({"Error":"Page not found"})

def verificar_user(user_id):
    cursor = conexion.connection.cursor()
    query = """SELECT * FROM users WHERE user_id = %s"""
    cursor.execute(query, user_id)
    return cursor.fetchone() is not None #Devuleve True si el usuario existe y False si no existe(porque sería == None)


if __name__ == "__main__":
    app.config.from_object(config["development"])
    app.register_error_handler(404, pagina_no_encontrada)
    app.run()