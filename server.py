from flask import Flask
import sqlite3

app = Flask(__name__)

def conectar_banco():
    return sqlite3.connect("banco.db")

@app.get('/imoveis')
def index():
    return []
