from models.user_role import UserRole
from sqlalchemy import inspect

def test_user_role_columns():
    mapper = inspect(UserRole)
    col_names = [col.key for col in mapper.columns]
    assert "user_id" in col_names
    assert "role_id" in col_names