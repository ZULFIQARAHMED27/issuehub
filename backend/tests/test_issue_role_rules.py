import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from app.main import app


async def signup_and_login(ac: AsyncClient, name: str, email: str, password: str):
    await ac.post(
        "/api/v1/auth/signup",
        json={"name": name, "email": email, "password": password},
    )
    login = await ac.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    return login.json()["access_token"]


@pytest.mark.asyncio
async def test_member_cannot_change_status_or_assignee_but_can_update_own_issue_fields():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        owner_email = f"owner_{uuid.uuid4().hex[:6]}@test.com"
        member_email = f"member_{uuid.uuid4().hex[:6]}@test.com"
        key = f"RL_{uuid.uuid4().hex[:6]}"

        owner_token = await signup_and_login(ac, "Owner", owner_email, "password123")
        member_token = await signup_and_login(ac, "Member", member_email, "password123")

        project = await ac.post(
            "/api/v1/projects/",
            headers={"Authorization": f"Bearer {owner_token}"},
            json={"name": "Role Rules", "key": key, "description": "Test"},
        )
        project_id = project.json()["id"]

        add_member = await ac.post(
            f"/api/v1/projects/{project_id}/members",
            headers={"Authorization": f"Bearer {owner_token}"},
            json={"email": member_email, "role": "member"},
        )
        assert add_member.status_code == 200

        issue = await ac.post(
            f"/api/v1/projects/{project_id}/issues",
            headers={"Authorization": f"Bearer {member_token}"},
            json={"title": "Member issue", "description": "Desc", "priority": "medium"},
        )
        issue_id = issue.json()["id"]

        update_status = await ac.patch(
            f"/api/v1/issues/{issue_id}",
            headers={"Authorization": f"Bearer {member_token}"},
            json={"status": "resolved"},
        )
        assert update_status.status_code == 403

        update_assignee = await ac.patch(
            f"/api/v1/issues/{issue_id}",
            headers={"Authorization": f"Bearer {member_token}"},
            json={"assignee_id": 1},
        )
        assert update_assignee.status_code == 403

        update_title = await ac.patch(
            f"/api/v1/issues/{issue_id}",
            headers={"Authorization": f"Bearer {member_token}"},
            json={"title": "Updated title"},
        )
        assert update_title.status_code == 200
        assert update_title.json()["title"] == "Updated title"


@pytest.mark.asyncio
async def test_maintainer_can_change_any_issue_status_and_assignee():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        owner_email = f"owner2_{uuid.uuid4().hex[:6]}@test.com"
        member_email = f"member2_{uuid.uuid4().hex[:6]}@test.com"
        key = f"RL2_{uuid.uuid4().hex[:6]}"

        owner_token = await signup_and_login(ac, "Owner2", owner_email, "password123")
        member_token = await signup_and_login(ac, "Member2", member_email, "password123")

        project = await ac.post(
            "/api/v1/projects/",
            headers={"Authorization": f"Bearer {owner_token}"},
            json={"name": "Role Rules 2", "key": key, "description": "Test"},
        )
        project_id = project.json()["id"]

        add_member = await ac.post(
            f"/api/v1/projects/{project_id}/members",
            headers={"Authorization": f"Bearer {owner_token}"},
            json={"email": member_email, "role": "member"},
        )
        assert add_member.status_code == 200

        issue = await ac.post(
            f"/api/v1/projects/{project_id}/issues",
            headers={"Authorization": f"Bearer {member_token}"},
            json={"title": "Issue", "description": "Desc", "priority": "high"},
        )
        issue_id = issue.json()["id"]

        list_members = await ac.get(
            f"/api/v1/projects/{project_id}/members",
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        member_id = next(m["id"] for m in list_members.json() if m["email"] == member_email)

        update_issue = await ac.patch(
            f"/api/v1/issues/{issue_id}",
            headers={"Authorization": f"Bearer {owner_token}"},
            json={"status": "closed", "assignee_id": member_id},
        )
        assert update_issue.status_code == 200
        assert update_issue.json()["status"] == "closed"
        assert update_issue.json()["assignee_id"] == member_id
