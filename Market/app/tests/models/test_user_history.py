from datetime import datetime, UTC
from models.user_history import UserHistory
import uuid

def test_user_history_init():
    uid = uuid.uuid4()
    now = datetime.now(UTC)
    history = UserHistory(
        user_id=uid,
        attempted=now,
        user_agent="TestAgent",
        user_device_type="desktop",
        success=False
    )
    assert history.user_id == uid
    assert history.user_agent == "TestAgent"
    assert history.user_device_type == "desktop"
    assert not history.success
    assert isinstance(repr(history), str)