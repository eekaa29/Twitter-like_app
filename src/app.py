from flask import Flask, jsonify, json, request
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_mysqldb import MySQL
import logging


logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

conexion = MySQL(app)

#MOSTRAR TODOS LOS USUARIOS 
@app.route("/users", methods = ["GET"])
def get_usuarios():
    try:
        cursor = conexion.connection.cursor()
        query = """SELECT * FROM users"""
        cursor.execute(query)
        datos = cursor.fetchall()
        if datos:
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
        return jsonify({"Error": "There is no data "}), 404
        
    except Exception as e:
        return jsonify({"Error": str(e)}), 400
#MOSTRAR TODOS LOS SEGUIDORES 
@app.route("/followers", methods = ["GET"])
def get_follows():
    try: 
        cursor = conexion.connection.cursor()
        query = """SELECT * FROM followers"""
        cursor.execute(query)
        tabla = cursor.fetchall()
        if tabla:
            follows = []
            for fila in tabla:
                follow = {"follower_id":fila[0], "following_id": fila[1]}
                follows.append(follow)
            return jsonify({"Follows": follows})
        return jsonify({"Error": "There is no data "}), 404
    except Exception as e:
        return jsonify({"Error": str(e)}), 400

#MOSTRAR TODOS LOS TWEETS
@app.route("/tweets", methods=["GET"])
def get_tweets():
    try:
        cursor = conexion.connection.cursor()
        query = """SELECT * FROM tweets"""
        cursor.execute(query)
        info = cursor.fetchall()
        if info:
            tweets = []
            for i in info:
                tweet = {"tweet_id": i[0],"user_id": i[1], "tweet" : i[2], "likes": i[3], "retweets": i[4], "comments": i[5], "created_at": i[6] }
                tweets.append(tweet)
            return jsonify({"tweets": tweets})
        return jsonify({"Error": "There is no data "}), 404
    except Exception as e:
        return jsonify({"Error": str(e)}), 400

#MOSTRAR USUARIO CON UN DETERMINADO ID
@app.route("/users/<user_id>", methods = ["GET"])
def get_usuario(user_id):
    try:
        cursor = conexion.connection.cursor()
        query = """SELECT * FROM users WHERE user_id = %s """ #El $s es evitar usar el .format, evitando fallos de sintaxis y riesgo de inyecciones SQL 
        if verify_user(user_id):
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
        return jsonify({"Error": f"User with user_id {user_id} does not exists"}), 404
    except Exception as e:
        return jsonify({"Error": str(e)}), 400

#MOSTRAR TODOS LOS FOLLOWERS DE UN DETERMINADO USER 
@app.route("/followers/<following_id>", methods = ["GET"])
def get_follow(following_id):
    try:
        cursor = conexion.connection.cursor()
        query = """SELECT * FROM followers WHERE following_id = %s"""
        if verify_user(following_id):
            cursor.execute(query, following_id)
            datos = cursor.fetchall()#aquí pongo fetchall() porque hay más de un follower_id que sigue al mismo following_id, por lo que quiero que salgan todos
            follower_list = [follower[0] for follower in datos]# Datos es un lista de tuplas;meto en la lista el primer valor de cada tupla
            conexion.connection.commit()
            return jsonify({"following_id": following_id, "followers": follower_list})
        return jsonify({"Error": f"User with following_id {following_id} does not exists"}), 404 
    except Exception as e:
        return jsonify({"Error": str(e)}), 400
    
#MOSTRAR TWEETS DE UN DETERMINADO USER
@app.route("/tweets/<user_id>", methods = ["GET"])
def tweets_per_user(user_id):
    try:
        cursor = conexion.connection.cursor()
        query = """SELECT * FROM tweets WHERE user_id = %s"""
        if verify_user(user_id):
            cursor.execute(query, (user_id,))
            datos = cursor.fetchall()
            logging.debug(datos)
            if datos:
                tweets = [tweet[2] for tweet in datos]
                return jsonify({"user_id": user_id, "tweets": tweets})
            return jsonify({"Message":f"User with user_id {user_id} has not created any tweet yet"}), 404
        return jsonify({"Error":f"User with user_id {user_id} does not exist"}), 404
    except Exception as e:
        return jsonify({"Error": f"Exception {str(e)}"}), 404
    
#AÑADIR USERS
@app.route("/users", methods = ["POST"])
def add_user():
    try:
        cursor = conexion.connection.cursor()
        query = """INSERT INTO users (user_handle, email_address, first_name, last_name, phone_number, follower_count)
        VALUES (%s, %s, %s, %s, %s, %s)"""
        data = [request.json["user_handle"], request.json["email_address"], request.json["first_name"], 
        request.json["last_name"], request.json["phone_number"], request.json["follower_count"]]
        if not verify_user_handle(request.json["user_handle"]):
            cursor.execute(query, data)
            conexion.connection.commit()
            return jsonify({"Message": "User successfully added"}), 200
        return jsonify({"Error": f"User with user_handle {request.json["user_handle"]} already exists"}), 404
    except Exception as e:
        return jsonify({"Exception error": str(e)}), 400    

#AÑADIR FOLLOWERS    
@app.route("/followers", methods = ["POST"])
def add_follow():
    try:
        cursor= conexion.connection.cursor()
        query = """INSERT INTO followers (follower_id, following_id)
        VALUES (%s, %s)"""
        datos = [request.json["follower_id"], request.json["following_id"]]
        cursor.execute(query,datos)
        conexion.connection.commit()
        return jsonify({"Message":"Follow added"}), 200
    except Exception as e:
        return jsonify({"Error": str(e)}), 400#No creo que sea necesario añadir ninguna validación de existencia de user, 
    #ya que en la interfaz es imposible que aparezca un user que no existe para poder darle follow
    
#AÑADIR TWEETS
@app.route("/tweets",methods =["POST"])
def add_tweet():
    try:
        cursor= conexion.connection.cursor()
        query = """INSERT INTO tweets (user_id, tweet_text, num_likes, num_retweets, num_comments)
        VALUES (%s, %s, %s, %s, %s)"""
        values = [request.json["user_id"], request.json["tweet_text"], request.json["num_likes"], 
                  request.json["num_retweets"], request.json["num_comments"]]
        cursor.execute(query, values)
        conexion.connection.commit()
        return jsonify({"Message": "Tweet succesfully created"}), 200
    except Exception as e:
        return jsonify({"Error": str(e)}), 400#Aquí no creo que deba de verificar si el tweet ya existe, si el usuario quiere twitear lo mismo más de una vez que lo haga.
    
#ELIMINAR USER
@app.route("/users/<user_id>", methods = ["DELETE"])
def delete_users(user_id):
    try: 
        cursor = conexion.connection.cursor()
        query1 = """DELETE FROM users WHERE user_id = (%s)"""
        usuario = user_id
        if verify_user(usuario) == True:
            cursor.execute(query1, usuario)
            conexion.connection.commit()
            return jsonify({"Message": "User successfully deleted"}), 200
        return jsonify({"Error": f"User with user_id {usuario} does not exists"}), 404
    except Exception as e:
        return jsonify({"Error": str(e)})

#ELIMINAR TWEET EN BASE AL tweet_id
@app.route("/tweets/<tweet_id>", methods = ["DELETE"])
def del_tweet(tweet_id):
    try:
        cursor = conexion.connection.cursor()
        query = """DELETE FROM tweets WHERE tweet_id = (%s)"""
        if verify_tweet(tweet_id):
            cursor.execute(query, tweet_id)
            conexion.connection.commit()
            return jsonify({"Message": f"Tweet with tweet_id {tweet_id} has been deleted "}), 200
        return jsonify({"Message": f"Tweet with tweet_id {tweet_id} does not exist "}), 404
    except Exception as e:
        return jsonify({"Error": str(e)})

#MODIFICAR USERS
@app.route("/users/<user_id>", methods = ["PUT"])
def modify_user(user_id):
    try:
        cursor = conexion.connection.cursor()
        query = """UPDATE users SET first_name = %s WHERE user_id = %s"""
        if verify_user(user_id):
            cursor.execute(query, (request.json["first_name"], user_id))
            conexion.connection.commit()
            return jsonify({"Message": f"User with user_id {user_id} has been updated "}), 200
        return jsonify({"Message": f"User with user_id {user_id} does not exists"}), 404
    except Exception as e:
        return jsonify({"Error": str(e)})


#MODIFICAR TWEET POR SU tweet_id
@app.route("/tweets/<tweet_id>", methods = ["PUT"])
def edit_tweet(tweet_id):
    try:
        cursor = conexion.connection.cursor()
        query = """UPDATE tweets SET tweet_text = %s WHERE tweet_id = %s"""
        if verify_tweet(tweet_id):
            cursor.execute(query, (request.json["tweet_text"], tweet_id))
            conexion.connection.commit()
            return jsonify({"Message": f"Tweet with tweet_id {tweet_id} succesfully edited"}), 200
        return jsonify({"Message": f"Tweet with tweet_id {tweet_id} does not exist"}), 404
    except Exception as e:
        return jsonify({"Error": str(e)})
    
#ERROR HANDLERS
@app.errorhandler(404)
def route_not_found(error):
    return jsonify({"Error": "Endpoint not found. Check the API documentation."}), 404
# Error 400 - Bad Request
@app.errorhandler(400)
def bad_request(error):
    return jsonify({"Error": "Bad request. Check your request data."}), 400

# Error 405 - Método no permitido (ej: un POST en una ruta que solo acepta GET)
@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"Error": "Method not allowed. Check the API documentation."}), 405

# Error 500 - Error interno del servidor
@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({"Error": "Internal server error. Please try again later."}), 500


def verify_user(user_id):
    cursor = conexion.connection.cursor()
    query = """SELECT * FROM users WHERE user_id = %s"""
    cursor.execute(query, (user_id,))
    return cursor.fetchone() is not None #Devuleve True si el usuario existe y False si no existe(porque sería == None)

def verify_tweet(tweet_id):
    cursor = conexion.connection.cursor()
    query = """SELECT * FROM tweets WHERE tweet_id = %s"""
    cursor.execute(query, (tweet_id,))
    return cursor.fetchone() is not None

def verify_user_handle(user_handle):
    cursor = conexion.connection.cursor()
    query = """SELECT * FROM users WHERE user_handle = %s"""
    cursor.execute(query, (user_handle,))
    return cursor.fetchone() is not None


if __name__ == "__main__":
    app.config.from_object(config["development"])
    app.register_error_handler(404, route_not_found)
    app.run()