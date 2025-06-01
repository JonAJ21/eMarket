import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from models.role import Role
from repositories.role import CachedRolePostgreRepository, RolePostgreRepository

@pytest.mark.asyncio
async def test_get_role_by_name_found(mocker):
    session_mock = mocker.AsyncMock(spec=AsyncSession)
    repo = RolePostgreRepository(session=session_mock)
    
    role_instance = Role(name="admin")
    execute_result = mocker.Mock()
    execute_result.scalar_one_or_none.return_value = role_instance
    session_mock.execute.return_value = execute_result

    result = await repo.get_role_by_name(name="admin")

    session_mock.execute.assert_called_once()
    assert result == role_instance


@pytest.mark.asyncio
async def test_get_role_by_name_not_found(mocker):
    session_mock = mocker.AsyncMock(spec=AsyncSession)
    repo = RolePostgreRepository(session=session_mock)

    execute_result = mocker.Mock()
    execute_result.scalar_one_or_none.return_value = None
    session_mock.execute.return_value = execute_result

    result = await repo.get_role_by_name(name="nonexistent")

    session_mock.execute.assert_called_once()
    assert result is None
    
@pytest.mark.asyncio
async def test_cached_get_role_by_name_from_cache(mocker):
    session_mock = mocker.AsyncMock()
    cache_mock = mocker.AsyncMock()
    
    role = Role(name="admin")
    cache_mock.get.return_value = role

    repo = CachedRolePostgreRepository(session=session_mock, cache_service=cache_mock)

    result = await repo.get_role_by_name(name="admin")

    cache_mock.get.assert_called_once_with(key="Role_admin")
    session_mock.execute.assert_not_called()
    assert result == role


@pytest.mark.asyncio
async def test_cached_get_role_by_name_fallback_to_db(mocker):
    session_mock = mocker.AsyncMock()
    cache_mock = mocker.AsyncMock()
    
    cache_mock.get.return_value = None

    db_role = Role(name="admin")
    execute_result = mocker.Mock()
    execute_result.scalar_one_or_none.return_value = db_role
    session_mock.execute.return_value = execute_result

    repo = CachedRolePostgreRepository(session=session_mock, cache_service=cache_mock)

    result = await repo.get_role_by_name(name="admin")

    cache_mock.get.assert_called_once_with(key="Role_admin")
    session_mock.execute.assert_called_once()
    assert result == db_role