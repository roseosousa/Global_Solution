import pytest

from server import app


@pytest.fixture(scope='module')
def client():
    # ensure we use the test client and seed DB
    from seed_fixtures import seed
    seed()
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c


def test_login_success(client):
    # seed_fixtures seeds users named 'User1 Test' with password 'pwd12025'
    resp = client.post('/api/login', json={'nome': 'User1 Test', 'senha': 'pwd12025'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data.get('ok') is True
    assert 'user' in data
    # token present when PyJWT installed
    assert 'token' in data
    # store token for next requests
    client.environ_base['HTTP_AUTHORIZATION'] = f"Bearer {data.get('token')}"


def test_deliverables_list(client):
    resp = client.get('/api/deliverables')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'ok' in data
    assert isinstance(data.get('files', []), list)
