class DevelopmentConfig():
    DEBUG = True
    MYSQL_HOST = "localhost"
    MYSQL_USER = "root"
    MYSQL_PASSWORD = "Ekaitz-2003"
    MYSQL_DB = "twitter_db"


config = {
    "development" : DevelopmentConfig
} #El punto importante aquí es que al crear el diccionario apuntando a la
#clase "DevelopmentConfig", en el script de la app solamente tendría que 
#importar el diccionario para ejecutar todo lo que está dentro de la clase, ya que el diccionario apunta a la clase.
