import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()  # Carga las variables del archivo .env

def conectar_db():
    return psycopg2.connect(
        host=os.getenv("host"),
        dbname=os.getenv("dbname"),
        user=os.getenv("user"),
        password=os.getenv("password"),
        port=os.getenv("port")
    ) 