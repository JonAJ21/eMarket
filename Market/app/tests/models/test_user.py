import pytest
from models.user import User
from models.role import Role
from models.user_history import UserHistory
from models.social_account import SocialAccount
from datetime import datetime, UTC

def test_user_init(mocker):
    mocker.patch("models.user.hashpw", return_value=b"hashed")
    mocker.patch("models.user.gensalt", return_value=b"salt")

    user = User(login="testuser", password="secret", email="test@example.com")
    assert user.login == "testuser"
    assert user.password == "hashed"
    assert user.email == "test@example.com"
    assert user.social_accounts == []

def test_check_password(mocker):
    mocker.patch("models.user.hashpw", return_value=b"hashedpass")
    mocker.patch("models.user.gensalt", return_value=b"salt")
    mock_checkpw = mocker.patch("models.user.checkpw", return_value=True)

    user = User(login="check", password="test")
    assert user.check_password("test") is True
    mock_checkpw.assert_called_once()

def test_change_password_success(mocker):
    mocker.patch("models.user.hashpw", side_effect=[b"oldhash", b"newhash"])
    mocker.patch("models.user.gensalt", return_value=b"salt")
    mocker.patch("models.user.checkpw", return_value=True)

    user = User(login="change", password="old")
    result = user.change_password("old", "new")
    assert result is True
    assert user.password == "newhash"

def test_update_personal():
    user = User(login="old", password="pass", email="old@example.com")
    user.update_personal(login="new", email="new@example.com")
    assert user.login == "new"
    assert user.email == "new@example.com"

def test_roles_management():
    user = User(login="roleuser", password="pass")
    role = Role(name="admin")

    user.assign_role(role)
    assert user.has_role("admin")
    user.remove_role(role)
    assert not user.has_role("admin")

def test_social_account_management():
    user = User(login="social", password="pass")
    acc = SocialAccount(user_id=user.id, social_id="123", social_name="telegram")

    user.add_social_account(acc)
    assert user.has_social_account(acc)
    user.remove_social_account(acc)
    assert not user.has_social_account(acc)

def test_add_user_session():
    user = User(login="history", password="pass")
    session = UserHistory(user_id=user.id, attempted=datetime.now(UTC), user_agent="agent", user_device_type="mobile", success=True)
    user.add_user_session(session)
    assert session in user.history