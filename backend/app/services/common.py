def role_value(role):
    return role.value if hasattr(role, "value") else str(role)
