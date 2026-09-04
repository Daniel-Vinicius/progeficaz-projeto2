import pytest
from unittest.mock import MagicMock, patch

from server import app


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_db():
    with patch("server.conectar_banco") as mock_conectar:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        # Configura o cursor usado dentro do `with`
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_conectar.return_value = mock_conn

        yield mock_conectar, mock_conn, mock_cursor


def test_lista_imoveis_vazia(client, mock_db):
    _, mock_conn, mock_cursor = mock_db
    mock_cursor.fetchall.return_value = []

    response = client.get("/imoveis")

    assert response.status_code == 200
    assert response.get_json() == []

    mock_cursor.execute.assert_called_once_with("SELECT * FROM imoveis")
    mock_cursor.fetchall.assert_called_once()
    mock_conn.close.assert_called_once()


def test_lista_imoveis_com_registros(client, mock_db):
    _, mock_conn, mock_cursor = mock_db

    # Com DictCursor, o MySQL devolve dicionários.
    mock_cursor.fetchall.return_value = [
        {
            "id": 1,
            "logradouro": "Nicole Common",
            "tipo_logradouro": "Travessa",
            "bairro": "Lake Danielle",
            "cidade": "Judymouth",
            "cep": "85184",
            "tipo": "casa em condominio",
            "valor": 488423.52,
            "data_aquisicao": "2017-07-29",
        },
        {
            "id": 2,
            "logradouro": "Price Prairie",
            "tipo_logradouro": "Travessa",
            "bairro": "Colonton",
            "cidade": "North Garyville",
            "cep": "93354",
            "tipo": "casa em condominio",
            "valor": 260069.89,
            "data_aquisicao": "2021-11-30",
        },
    ]

    response = client.get("/imoveis")

    assert response.status_code == 200
    assert response.get_json() == mock_cursor.fetchall.return_value

    mock_cursor.execute.assert_called_once_with("SELECT * FROM imoveis")
    mock_cursor.fetchall.assert_called_once()
    mock_conn.close.assert_called_once()

def test_find_imovel_by_id(client, mock_db):
    _, mock_conn, mock_cursor = mock_db
    mock_cursor.fetchone.return_value = {
        "id": 2,
        "logradouro": "Price Prairie",
        "tipo_logradouro": "Travessa",
        "bairro": "Colonton",
        "cidade": "North Garyville",
        "cep": "93354",
        "tipo": "casa em condominio",
        "valor": 260069.89,
        "data_aquisicao": "2021-11-30",
    }

    response = client.get("/imoveis/2")

    assert response.status_code == 200
    assert response.get_json() == mock_cursor.fetchone.return_value

    mock_cursor.execute.assert_called_once_with("SELECT * FROM imoveis WHERE id = %s", (2,))
    mock_cursor.fetchone.assert_called_once()
    mock_conn.close.assert_called_once()

    mock_cursor.fetchone.return_value = None
    response = client.get("/imoveis/2100")
    assert response.status_code == 404

def test_add_imovel(client, mock_db):
    _, mock_conn, mock_cursor = mock_db
    mock_cursor.lastrowid = 1002
    
    novo_imovel = {
        "id": 1002, # nao é definido pela request, e sim pelo lastrowid, so coloquei aqui pra facilitar o assert
        "logradouro": "Price Prairie",
        "tipo_logradouro": "Travessa",
        "bairro": "Colonton",
        "cidade": "North Garyville",
        "cep": "93354",
        "tipo": "casa em condominio",
        "valor": 260069.89,
        "data_aquisicao": "2021-11-30",
    }

    response = client.post("/imoveis", json=novo_imovel)

    mock_cursor.execute.assert_called_once_with(
                """
                INSERT INTO imoveis
                    (logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    novo_imovel["logradouro"], novo_imovel["tipo_logradouro"], novo_imovel["bairro"], novo_imovel["cidade"], novo_imovel["cep"], novo_imovel["tipo"], novo_imovel["valor"], novo_imovel["data_aquisicao"]
                )
            )
    mock_conn.close.assert_called_once()

    assert response.get_json() == novo_imovel
    assert response.status_code == 201

def test_add_imovel_campos_faltantes(client, mock_db):
    response = client.post("/imoveis", json={})

    assert response.get_json() == {"erro": "Campos obrigatórios: logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao"}
    assert response.status_code == 400

def test_atualizar_imovel(client, mock_db):
    _, mock_conn, mock_cursor = mock_db
    mock_cursor.rowcount = 1

    response = client.put(
        "/imoveis/1",
        json={
            "logradouro": "Caleb Heights ATUALIZADO",
            "tipo_logradouro":"Travessa",
            "bairro":"Lake Charles",
            "cidade":"Youngport",
            "cep":"48943",
            "tipo":"apartamento",
            "valor": 86254.13,
            "data_aquisicao": "2022-07-27",
        },
    )

    assert response.status_code == 200
    assert response.get_json() == {
        "mensagem": "Property updated successfully"
    }

    mock_cursor.execute.assert_called_once_with(
        "UPDATE imoveis SET logradouro = %s, tipo_logradouro = %s, bairro = %s, cidade = %s, cep = %s, tipo = %s, valor = %s, data_aquisicao = %s WHERE id = %s",
        ('Caleb Heights ATUALIZADO', 'Travessa', 'Lake Charles', 'Youngport', '48943', 'apartamento', 86254.13, '2022-07-27', 1),
    )
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()

def test_update_imovel_campos_faltantes(client, mock_db):
    response = client.put("/imoveis/1", json={})

    assert response.get_json() == {"erro": "Campos obrigatórios: logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao"}
    assert response.status_code == 400

def test_update_imovel_nao_existente(client, mock_db):
    _, mock_conn, mock_cursor = mock_db
    mock_cursor.rowcount = 0

    response = client.put("/imoveis/1", json={
        "logradouro": "Caleb Heights ATUALIZADO",
        "tipo_logradouro": "Travessa",
        "bairro": "Lake Charles",
        "cidade": "Youngport",
        "cep": "48943",
        "tipo": "apartamento",
        "valor": 86254.13,
        "data_aquisicao": "2022-07-27",
    })

    assert response.get_json() == {"erro": "Property not found"}
    assert response.status_code == 404

def test_delete_property(client, mock_db):
    _, mock_conn, mock_cursor = mock_db
    mock_cursor.rowcount = 1

    response = client.delete("/imoveis/1")
    assert response.status_code == 204

    mock_cursor.execute.assert_called_once_with("DELETE FROM imoveis WHERE id = %s", (1,))
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()

def test_delete_non_existent_property(client, mock_db):
    _, mock_conn, mock_cursor = mock_db
    mock_cursor.rowcount = 0
    response = client.delete("/imoveis/1")
    assert response.status_code == 404
