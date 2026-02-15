import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_issue_access_denied_for_non_member():
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:

        owner_email = f"owner_{uuid.uuid4().hex[:6]}@test.com"
        stranger_email = f"stranger_{uuid.uuid4().hex[:6]}@test.com"
        unique_key = f"PERM_{uuid.uuid4().hex[:6]}"

        # Create owner
        await ac.post("/api/auth/signup", json={
            "name": "Owner",
            "email": owner_email,
            "password": "password123"
        })

        login_owner = await ac.post("/api/auth/login", data={
            "username": owner_email,
            "password": "password123"
        })

        owner_token = login_owner.json()["access_token"]

        # Create project
        project = await ac.post(
            "/api/projects/",
            headers={"Authorization": f"Bearer {owner_token}"},
            json={
                "name": "Permission Project",
                "key": unique_key,
                "description": "Test"
            }
        )

        assert project.status_code == 200
        project_id = project.json()["id"]

        # Create stranger
        await ac.post("/api/auth/signup", json={
            "name": "Stranger",
            "email": stranger_email,
            "password": "password123"
        })

        login_stranger = await ac.post("/api/auth/login", data={
            "username": stranger_email,
            "password": "password123"
        })

        stranger_token = login_stranger.json()["access_token"]

        # Stranger tries to access issues
        response = await ac.get(
            f"/api/projects/{project_id}/issues",
            headers={"Authorization": f"Bearer {stranger_token}"}
        )

        assert response.status_code == 403


