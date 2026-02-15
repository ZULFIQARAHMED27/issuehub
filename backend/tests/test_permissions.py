import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_create_project_requires_auth():
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:

        response = await ac.post(
            "/api/v1/projects/",
            json={
                "name": "Test Project",
                "key": f"TP_{uuid.uuid4().hex[:6]}",
                "description": "Test"
            }
        )

        assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_project_success():
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:

        unique_email = f"user_{uuid.uuid4().hex[:6]}@test.com"
        unique_key = f"TP_{uuid.uuid4().hex[:6]}"

        # Signup
        await ac.post(
            "/api/v1/auth/signup",
            json={
                "name": "Project User",
                "email": unique_email,
                "password": "password123"
            },
        )

        # Login
        login = await ac.post(
            "/api/v1/auth/login",
            data={
                "username": unique_email,
                "password": "password123"
            },
        )

        token = login.json()["access_token"]

        # Create project
        response = await ac.post(
            "/api/v1/projects/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Test Project",
                "key": unique_key,
                "description": "Test"
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Project"
