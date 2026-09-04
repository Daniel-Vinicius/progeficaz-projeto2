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


