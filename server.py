from flask import Flask, jsonify
import pymysql

app = Flask(__name__)

def conectar_banco():
    return pymysql.connect(
        host="localhost",
        port=3306,
        user="root",
        password="senha123",
        database="imoveis_db",
        cursorclass=pymysql.cursors.DictCursor
    )

@app.get("/imoveis")
def index():
    conexao = conectar_banco()
    try:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT * FROM imoveis")
            imoveis = cursor.fetchall()

        return jsonify(imoveis)

    finally:
        conexao.close()

if __name__ == "__main__":
    app.run(debug=True)