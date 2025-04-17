from models.role import Role

def test_role_init():
    role = Role(name="admin", description="Administrator")
    assert role.name == "admin"
    assert role.description == "Administrator"

def test_role_repr():
    role = Role(name="moderator")
    assert repr(role) == "<Role moderator>"

def test_update_role():
    role = Role(name="old", description="Old desc")
    role.update_role(name="new", description="New desc")
    assert role.name == "new"
    assert role.description == "New desc"