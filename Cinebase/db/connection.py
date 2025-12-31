
import pymysql
import os

def get_connection():
    host = os.getenv('DB_HOST', 'localhost')
    user = os.getenv('DB_USER', 'root')
    password = os.getenv('DB_PASSWORD', '2005') 
    database = os.getenv('DB_NAME', 'cinebase')
   
    return pymysql.connect(host=host, user=user, password=password, database=database, cursorclass=pymysql.cursors.DictCursor)