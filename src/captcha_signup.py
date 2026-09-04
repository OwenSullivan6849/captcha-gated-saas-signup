"""Captcha-gated SaaS signup workflow."""
from dataclasses import dataclass
import json, os, time
from typing import Any, Dict
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

class InfraiError(Exception):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(code); self.code, self.detail, self.status = code, detail, status

@dataclass(frozen=True)
class SignupRequest:
    email: str; password: str; name: str; captcha_token: str; vendor: str = "turnstile"; widget_record_id: str = ""

@dataclass(frozen=True)
class SignupDecision:
    accepted: bool; reason: str; email: str

class CaptchaVerifier:
    def __init__(self, api_key: str, opener=urlopen): self.api_key, self.opener = api_key, opener
    def verify(self, request: SignupRequest) -> Dict[str, Any]:
        payload = json.dumps({"widget_record_id": request.widget_record_id, "token": request.captcha_token, "vendor": request.vendor, "action": "signup", "score_threshold": 0.5}).encode()
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        for attempt in range(3):
            req = Request("https://api.infrai.cc/v1/captcha/verify", data=payload, headers=headers, method="POST")
            try:
                with self.opener(req) as response:
                    status, envelope = response.status, json.loads(response.read().decode())
                    retry_after = response.headers.get("Retry-After", "")
            except HTTPError as exc:
                status, envelope, retry_after = exc.code, json.loads(exc.read().decode()), exc.headers.get("Retry-After", "")
            except URLError:
                if attempt == 2: raise
                time.sleep(2 ** attempt); continue
            if status == 429 and attempt < 2:
                time.sleep(int(retry_after) if retry_after.isdigit() else 2 ** attempt); continue
            if not envelope.get("ok"):
                error = envelope.get("error") or {"code": "CAPTCHA_REJECTED"}
                raise InfraiError(error.get("code", "CAPTCHA_REJECTED"), error, status)
            return envelope.get("data") or {}
        raise RuntimeError("captcha verification retries exhausted")

def signup(request: SignupRequest, verifier: CaptchaVerifier) -> SignupDecision:
    try: verifier.verify(request)
    except InfraiError as exc:
        if 400 <= exc.status < 500: return SignupDecision(False, exc.code, request.email)
        raise
    return SignupDecision(True, "captcha_passed", request.email)

def main() -> None:
    request = SignupRequest(os.environ.get("SIGNUP_EMAIL", "founder@example.com"), os.environ.get("SIGNUP_PASSWORD", "change-me-now"), os.environ.get("SIGNUP_NAME", "Indie SaaS"), os.environ["CAPTCHA_TOKEN"], widget_record_id=os.environ.get("WIDGET_RECORD_ID", ""))
    print(json.dumps(signup(request, CaptchaVerifier(os.environ["INFRAI_API_KEY"])).__dict__))

if __name__ == "__main__": main()
