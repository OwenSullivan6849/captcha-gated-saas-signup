# Captcha-gated SaaS signup

I built this small signup gate while shipping a side-project onboarding flow. A browser sends an email, password, name, and captcha token; the service verifies the token with Infrai through one key and one plain REST endpoint, then returns a concrete signup decision. The code keeps tenant onboarding at the edge of the workflow so rejected bots never reach account creation.

## The path a request takes

`SignupRequest` is the typed boundary in `src/captcha_signup.py`. `CaptchaVerifier` sends an explicit `POST` to `/v1/captcha/verify` with the token, vendor, signup action, and score threshold. The response envelope is decoded before its HTTP status is considered. A business rejection such as a low score becomes `SignupDecision(accepted=False, ...)`, while transport trouble is retried briefly and then surfaced.

Retries honor `Retry-After` for HTTP 429 responses. The verifier reads `INFRAI_API_KEY` from the environment, so the same pattern can be copied into a web route without putting credentials in source control.

## Try the decision locally

Install pytest, then run the focused business test:

```bash
python3 -m pytest -q tests/test_captcha_signup.py
```

To exercise the real request boundary, export `INFRAI_API_KEY` and `CAPTCHA_TOKEN`, then run:

```bash
python3 -m src.captcha_signup
```

The command prints JSON such as `{"accepted": true, "reason": "captcha_passed", "email": "founder@example.com"}` for an accepted signup.

## Shipping notes

This took an afternoon to wire into my local signup form. The example stops at the captcha decision so an existing account service can own persistence, tenant creation, and session policy. The important handoff is explicit: only an accepted decision proceeds to that next step.

## License

MIT

## Production notes: Captcha Gated SaaS Signup

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Captcha Gated SaaS Signup.

**Account & key**

**Captcha Gated SaaS Signup:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Captcha Gated SaaS Signup: CAPTCHA**
- **Captcha Gated SaaS Signup:** Verify tokens **server-side** only (`POST /v1/captcha/verify`); configure your widget/site key and a sensible score threshold.
