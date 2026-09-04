import json
from src.captcha_signup import CaptchaVerifier, SignupRequest, signup
class FakeResponse:
    status = 422; headers = {}
    def __enter__(self): return self
    def __exit__(self, *_args): return False
    def read(self): return json.dumps({"ok": False, "error": {"code": "CAPTCHA_SCORE_TOO_LOW"}}).encode()
def test_low_score_becomes_signup_rejection():
    decision = signup(SignupRequest("bot@example.com", "secret", "Bot", "token"), CaptchaVerifier("test-key", opener=lambda _: FakeResponse()))
    assert not decision.accepted
    assert decision.reason == "CAPTCHA_SCORE_TOO_LOW"
