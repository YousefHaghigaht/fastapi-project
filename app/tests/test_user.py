import pytest
import pytest_asyncio
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from main import app
from models.user_models import User
from tests.conftest import TestingSettionLocal
from sqlalchemy import select, func



@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


urls = {
    'register': 'create-user',
    'login': 'login',
    'list': 'list-user',
    'detail': 'detail-user',
    'delete': 'delete-user'
}


@pytest_asyncio.fixture
async def seed_user_data():

    async def _create_user(username: str = None, password: str = 'test-pass'):
        username = username or 'test-user'
        email = f'{username}@email.com'

        async with TestingSettionLocal() as session:
            user = User(username = username,
                        email= email,
                        password= password)

            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
    
    return _create_user


async def authenticate(client, username: str = 'test-user', password: str = 'test-user'):

    async with TestingSettionLocal() as session:
        user = User(username=username,email=f'{username}@email.com',password=password)
        session.add(user)
        await session.commit()
        await session.refresh(user)


    url = app.url_path_for(urls['login'])
    data = {
        'username': username,
        'password': password
    }
    response = await client.post(url, data=data)
    token = response.json().get('access_token')
    client.headers.update({
    "Authorization": f"Bearer {token}"
    })
    return True


@pytest.mark.asyncio
async def test_list_user_not_authenticate(client):
    url = app.url_path_for(urls['list'])
    response = await client.get(url)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_user(client):
    url = app.url_path_for(urls['list'])
    await authenticate(client)
    response = await client.get(url)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_register_user(client):

    url = app.url_path_for(urls['register'])
    data = {
        'username': 'test-user1',
        'email': 'testuser@email.com',
        'password': 'test-pass'
    }
    response = await client.post(url,json=data)
    print(response.json())
    assert response.status_code == 201

    async with TestingSettionLocal() as session:
        result = await session.execute(select(func.count()).select_from(User))
        count = result.scalar()

    assert count == 1

@pytest.mark.asyncio
async def test_detail_user_not_authenticate(client, seed_user_data):
    user = await seed_user_data()
    url = app.url_path_for(urls['detail'], user_id=user.id)
    response = await client.get(url)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_user(client):
    pass
