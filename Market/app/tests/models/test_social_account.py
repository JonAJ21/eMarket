from models.social_account import SocialAccount
from schemas.social import SocialNetworks
import uuid

def test_social_account_init():
    uid = uuid.uuid4()
    acc = SocialAccount(user_id=uid, social_id="123", social_name=SocialNetworks.GOOGLE)
    assert acc.user_id == uid
    assert acc.social_id == "123"
    assert acc.social_name == SocialNetworks.GOOGLE
    assert isinstance(repr(acc), str)