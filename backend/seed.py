from app.db.session import SessionLocal
from app.models.user import User
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.issue import Issue
from app.models.comment import Comment
from app.core.security import get_password_hash


USERS = [
    {"name": "Ali", "email": "ali@test.com", "password": "password123"},
    {"name": "Zulfiqar", "email": "zulfiqar@test.com", "password": "password123"},
    {"name": "Ayesha", "email": "ayesha@test.com", "password": "password123"},
    {"name": "Rahul", "email": "rahul@test.com", "password": "password123"},
]

PROJECTS = [
    {
        "name": "MediaMint Tracker",
        "key": "MMT",
        "description": "Internal bug tracker for MediaMint",
    },
    {
        "name": "Client Portal",
        "key": "CPORT",
        "description": "Issue tracking for client portal MVP",
    },
]

# 12 issues total (within requested 10-20 range)
ISSUES = [
    # MMT (6)
    {
        "project_key": "MMT",
        "title": "Login page not responsive",
        "description": "UI breaks on mobile devices under 390px width.",
        "status": "open",
        "priority": "high",
        "reporter": "ali@test.com",
        "assignee": "zulfiqar@test.com",
    },
    {
        "project_key": "MMT",
        "title": "Signup email validation missing",
        "description": "Invalid emails are accepted on signup form.",
        "status": "in_progress",
        "priority": "critical",
        "reporter": "ayesha@test.com",
        "assignee": "ali@test.com",
    },
    {
        "project_key": "MMT",
        "title": "Dashboard loads slowly",
        "description": "Project list endpoint latency spikes after 200 rows.",
        "status": "resolved",
        "priority": "medium",
        "reporter": "rahul@test.com",
        "assignee": "ali@test.com",
    },
    {
        "project_key": "MMT",
        "title": "Issue search ignores spaces",
        "description": "Searching multi-word titles returns empty results.",
        "status": "open",
        "priority": "medium",
        "reporter": "zulfiqar@test.com",
        "assignee": None,
    },
    {
        "project_key": "MMT",
        "title": "Comments timestamp timezone mismatch",
        "description": "Timestamps are displayed in UTC without label.",
        "status": "closed",
        "priority": "low",
        "reporter": "ali@test.com",
        "assignee": "rahul@test.com",
    },
    {
        "project_key": "MMT",
        "title": "Cannot unassign issue from table",
        "description": "Unassigned option sends incorrect payload.",
        "status": "in_progress",
        "priority": "high",
        "reporter": "ayesha@test.com",
        "assignee": "zulfiqar@test.com",
    },
    # CPORT (6)
    {
        "project_key": "CPORT",
        "title": "Session timeout not handled",
        "description": "User is not redirected to login on token expiry.",
        "status": "open",
        "priority": "critical",
        "reporter": "rahul@test.com",
        "assignee": "ayesha@test.com",
    },
    {
        "project_key": "CPORT",
        "title": "Project key duplicate check case-sensitive",
        "description": "CPORT and cport are both allowed.",
        "status": "resolved",
        "priority": "medium",
        "reporter": "ali@test.com",
        "assignee": "rahul@test.com",
    },
    {
        "project_key": "CPORT",
        "title": "Issue modal closes on backdrop click",
        "description": "Accidental click outside modal loses draft text.",
        "status": "open",
        "priority": "low",
        "reporter": "zulfiqar@test.com",
        "assignee": None,
    },
    {
        "project_key": "CPORT",
        "title": "Maintainer controls visible to member",
        "description": "Role-based rendering regression on Issue Detail page.",
        "status": "closed",
        "priority": "high",
        "reporter": "ayesha@test.com",
        "assignee": "ali@test.com",
    },
    {
        "project_key": "CPORT",
        "title": "Pagination resets after status update",
        "description": "Updating issue status returns to page 1 unexpectedly.",
        "status": "in_progress",
        "priority": "medium",
        "reporter": "rahul@test.com",
        "assignee": "zulfiqar@test.com",
    },
    {
        "project_key": "CPORT",
        "title": "Sort by priority order incorrect",
        "description": "Critical issues appear below medium in sorted results.",
        "status": "open",
        "priority": "high",
        "reporter": "ali@test.com",
        "assignee": "ayesha@test.com",
    },
]


COMMENTS = [
    {
        "issue_title": "Login page not responsive",
        "author": "zulfiqar@test.com",
        "body": "Working on responsive grid fix for small devices.",
    },
    {
        "issue_title": "Signup email validation missing",
        "author": "ali@test.com",
        "body": "Added backend validation check, frontend patch pending.",
    },
    {
        "issue_title": "Session timeout not handled",
        "author": "ayesha@test.com",
        "body": "Will add interceptor handling for 401 responses.",
    },
    {
        "issue_title": "Sort by priority order incorrect",
        "author": "rahul@test.com",
        "body": "Need explicit CASE order in query for enum sort.",
    },
]


def get_or_create_user(db, user_data):
    user = db.query(User).filter(User.email == user_data["email"]).first()
    if user:
        return user

    user = User(
        name=user_data["name"],
        email=user_data["email"],
        password_hash=get_password_hash(user_data["password"]),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_or_create_project(db, project_data):
    project = db.query(Project).filter(Project.key == project_data["key"]).first()
    if project:
        return project

    project = Project(
        name=project_data["name"],
        key=project_data["key"],
        description=project_data["description"],
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def ensure_membership(db, project_id, user_id, role):
    membership = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id
    ).first()
    if membership:
        return membership

    membership = ProjectMember(project_id=project_id, user_id=user_id, role=role)
    db.add(membership)
    db.commit()
    return membership


def get_or_create_issue(db, issue_data, projects_by_key, users_by_email):
    project = projects_by_key[issue_data["project_key"]]
    reporter = users_by_email[issue_data["reporter"]]
    assignee = users_by_email[issue_data["assignee"]] if issue_data["assignee"] else None

    existing = db.query(Issue).filter(
        Issue.project_id == project.id,
        Issue.title == issue_data["title"]
    ).first()
    if existing:
        return existing

    issue = Issue(
        project_id=project.id,
        title=issue_data["title"],
        description=issue_data["description"],
        status=issue_data["status"],
        priority=issue_data["priority"],
        reporter_id=reporter.id,
        assignee_id=assignee.id if assignee else None,
    )
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue


def ensure_comment(db, issue_id, author_id, body):
    existing = db.query(Comment).filter(
        Comment.issue_id == issue_id,
        Comment.author_id == author_id,
        Comment.body == body
    ).first()
    if existing:
        return existing

    comment = Comment(issue_id=issue_id, author_id=author_id, body=body)
    db.add(comment)
    db.commit()
    return comment


def run():
    db = SessionLocal()
    try:
        print("Seeding database...")

        users_by_email = {u["email"]: get_or_create_user(db, u) for u in USERS}
        projects_by_key = {p["key"]: get_or_create_project(db, p) for p in PROJECTS}

        # memberships across 2 projects
        ensure_membership(db, projects_by_key["MMT"].id, users_by_email["ali@test.com"].id, "maintainer")
        ensure_membership(db, projects_by_key["MMT"].id, users_by_email["zulfiqar@test.com"].id, "member")
        ensure_membership(db, projects_by_key["MMT"].id, users_by_email["ayesha@test.com"].id, "member")
        ensure_membership(db, projects_by_key["MMT"].id, users_by_email["rahul@test.com"].id, "member")

        ensure_membership(db, projects_by_key["CPORT"].id, users_by_email["ayesha@test.com"].id, "maintainer")
        ensure_membership(db, projects_by_key["CPORT"].id, users_by_email["ali@test.com"].id, "member")
        ensure_membership(db, projects_by_key["CPORT"].id, users_by_email["zulfiqar@test.com"].id, "member")
        ensure_membership(db, projects_by_key["CPORT"].id, users_by_email["rahul@test.com"].id, "member")

        issues_by_title = {}
        for issue_data in ISSUES:
            issue = get_or_create_issue(db, issue_data, projects_by_key, users_by_email)
            issues_by_title[issue.title] = issue

        for comment_data in COMMENTS:
            issue = issues_by_title.get(comment_data["issue_title"])
            if not issue:
                continue
            author = users_by_email[comment_data["author"]]
            ensure_comment(db, issue.id, author.id, comment_data["body"])

        print("Database seeded successfully")
        print(f"Users: {len(users_by_email)}")
        print(f"Projects: {len(projects_by_key)}")
        print(f"Issues (target): {len(ISSUES)}")
        print(f"Comments (target): {len(COMMENTS)}")
    finally:
        db.close()


if __name__ == "__main__":
    run()
