import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_create_project_requires_auth():
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:

        response = await ac.post(
            "/api/projects/",
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
            "/api/auth/signup",
            json={
                "name": "Project User",
                "email": unique_email,
                "password": "password123"
            },
        )

        # Login
        login = await ac.post(
            "/api/auth/login",
            data={
                "username": unique_email,
                "password": "password123"
            },
        )

        token = login.json()["access_token"]

        # Create project
        response = await ac.post(
            "/api/projects/",
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


@pytest.mark.asyncio
async def test_delete_project_success_for_maintainer():
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        unique_email = f"user_{uuid.uuid4().hex[:6]}@test.com"
        unique_key = f"DEL_{uuid.uuid4().hex[:6]}"

        await ac.post(
            "/api/auth/signup",
            json={
                "name": "Project User",
                "email": unique_email,
                "password": "password123"
            },
        )

        login = await ac.post(
            "/api/auth/login",
            data={
                "username": unique_email,
                "password": "password123"
            },
        )

        token = login.json()["access_token"]

        project = await ac.post(
            "/api/projects/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Delete Project",
                "key": unique_key,
                "description": "Test"
            },
        )
        project_id = project.json()["id"]

        delete_response = await ac.delete(
            f"/api/projects/{project_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert delete_response.status_code == 200


@pytest.mark.asyncio
async def test_delete_project_forbidden_for_member():
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        owner_email = f"owner_{uuid.uuid4().hex[:6]}@test.com"
        member_email = f"member_{uuid.uuid4().hex[:6]}@test.com"
        key = f"DELM_{uuid.uuid4().hex[:6]}"

        await ac.post(
            "/api/auth/signup",
            json={
                "name": "Owner",
                "email": owner_email,
                "password": "password123"
            },
        )
        await ac.post(
            "/api/auth/signup",
            json={
                "name": "Member",
                "email": member_email,
                "password": "password123"
            },
        )

        owner_login = await ac.post(
            "/api/auth/login",
            data={
                "username": owner_email,
                "password": "password123"
            },
        )
        member_login = await ac.post(
            "/api/auth/login",
            data={
                "username": member_email,
                "password": "password123"
            },
        )

        owner_token = owner_login.json()["access_token"]
        member_token = member_login.json()["access_token"]

        project = await ac.post(
            "/api/projects/",
            headers={"Authorization": f"Bearer {owner_token}"},
            json={
                "name": "Delete Project Member",
                "key": key,
                "description": "Test"
            },
        )
        project_id = project.json()["id"]

        add_member = await ac.post(
            f"/api/projects/{project_id}/members",
            headers={"Authorization": f"Bearer {owner_token}"},
            json={"email": member_email, "role": "member"},
        )
        assert add_member.status_code == 200

        delete_response = await ac.delete(
            f"/api/projects/{project_id}",
            headers={"Authorization": f"Bearer {member_token}"}
        )

        assert delete_response.status_code == 403


