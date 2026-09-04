from flask import Flask, jsonify, request
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

@app.get("/imoveis/<id>")
def find_imovel_by_id(id):
    conexao = conectar_banco()
    try:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT * FROM imoveis WHERE id = %s", (int(id),))
            imovel = cursor.fetchone()
            if not imovel:
                return {"message": "Property not found"}, 404

        return jsonify(imovel), 200

    finally:
        conexao.close()

@app.post("/imoveis")
def add_imovel():
    dados = request.json or {}

    if "logradouro" not in dados or "tipo_logradouro" not in dados or "bairro" not in dados or "cidade" not in dados or "cep" not in dados or "tipo" not in dados or "valor" not in dados or "data_aquisicao" not in dados:
        return jsonify({"erro": "Campos obrigatórios: logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao"}), 400

    conexao = conectar_banco()
    try:
        with conexao.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO imoveis
                    (logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    dados["logradouro"], dados["tipo_logradouro"], dados["bairro"], dados["cidade"], dados["cep"], dados["tipo"], dados["valor"], dados["data_aquisicao"]
                )
            )
            dados["id"] = cursor.lastrowid
            conexao.commit()

        return dados, 201

    finally:
        conexao.close()

@app.put("/imoveis/<id>")
def update_imovel(id):
    dados = request.json or {}

    if "logradouro" not in dados or "tipo_logradouro" not in dados or "bairro" not in dados or "cidade" not in dados or "cep" not in dados or "tipo" not in dados or "valor" not in dados or "data_aquisicao" not in dados:
        return jsonify({"erro": "Campos obrigatórios: logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao"}), 400

    conexao = conectar_banco()
    try:
        with conexao.cursor() as cursor:
          cursor.execute(
            "UPDATE imoveis SET logradouro = %s, tipo_logradouro = %s, bairro = %s, cidade = %s, cep = %s, tipo = %s, valor = %s, data_aquisicao = %s WHERE id = %s",
            (dados["logradouro"], dados["tipo_logradouro"], dados["bairro"], dados["cidade"], dados["cep"], dados["tipo"], dados["valor"], dados["data_aquisicao"], int(id)),
        )
        conexao.commit()
        
        linhas = cursor.rowcount
        
        if linhas == 0:
            return jsonify({"erro": "Property not found"}), 404

        return jsonify({"mensagem": "Property updated successfully"}), 200

    finally:
        conexao.close()

if __name__ == "__main__":
    app.run(debug=True)