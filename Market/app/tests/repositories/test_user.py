import pytest
from unittest.mock import AsyncMock

from models.user import User
from models.user_history import UserHistory
from models.social_account import SocialAccount
from schemas.user import UserCreateDTO, UserHistoryCreateDTO
from schemas.social import SocialCreateDTO, SocialNetworks
from repositories.user import UserPostgreRepository, CachedUserPostgreRepository


@pytest.mark.asyncio
async def test_get_by_login(mocker):
    session = AsyncMock()
    repo = UserPostgreRepository(session=session)
    
    expected_user = User(login="testuser", password="secret", email="test@example.com")
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none.return_value = expected_user
    
    session.execute.return_value = mock_result

    result = await repo.get_by_login(login="testuser")
    
    assert result == expected_user
    session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_user_history(mocker):
    session = AsyncMock()
    repo = UserPostgreRepository(session=session)

    expected_history = [UserHistory(id="h1"), UserHistory(id="h2")]

    mock_result = AsyncMock()
    mock_result.scalars.return_value.all.return_value = expected_history
    session.execute.return_value = mock_result

    result = await repo.get_user_history(user_id="user123")

    assert result == expected_history
    session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_user_social(mocker):
    session = AsyncMock()
    repo = UserPostgreRepository(session=session)

    expected_social = SocialAccount(id="social1")
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none.return_value = expected_social
    session.execute.return_value = mock_result

    result = await repo.get_user_social(social_id="123", social_name=SocialNetworks.google)

    assert result == expected_social


@pytest.mark.asyncio
async def test_insert_user_login_user_exists(mocker):
    session = AsyncMock()
    repo = UserPostgreRepository(session=session)

    user = User(id="u1")
    data = UserHistoryCreateDTO(user_id="u1", user_agent="test-agent", ip="127.0.0.1")

    mocker.patch.object(repo, "get", return_value=user)
    mocker.patch.object(user, "add_user_session")

    result = await repo.insert_user_login(data=data)

    assert isinstance(result, UserHistory)
    user.add_user_session.assert_called_once_with(result)


@pytest.mark.asyncio
async def test_insert_user_login_user_not_found(mocker):
    session = AsyncMock()
    repo = UserPostgreRepository(session=session)

    data = UserHistoryCreateDTO(user_id="u1", user_agent="test-agent", ip="127.0.0.1")
    mocker.patch.object(repo, "get", return_value=None)

    result = await repo.insert_user_login(data=data)

    assert result is None


@pytest.mark.asyncio
async def test_insert_user_social_user_exists(mocker):
    session = AsyncMock()
    repo = UserPostgreRepository(session=session)

    user = User(id="u1")
    data = SocialCreateDTO(user_id="u1", social_id="sid", social_name=SocialNetworks.google)

    mocker.patch.object(repo, "get", return_value=user)
    mocker.patch.object(user, "add_social_account")

    result = await repo.insert_user_social(data=data)

    assert isinstance(result, SocialAccount)
    user.add_social_account.assert_called_once_with(result)


@pytest.mark.asyncio
async def test_insert_user_social_user_not_found(mocker):
    session = AsyncMock()
    repo = UserPostgreRepository(session=session)

    data = SocialCreateDTO(user_id="u1", social_id="sid", social_name=SocialNetworks.google)
    mocker.patch.object(repo, "get", return_value=None)

    result = await repo.insert_user_social(data=data)

    assert result is None