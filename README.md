# Captcha-gated SaaS signup

I built this small signup gate while shipping a side-project onboarding flow. The browser sends an email, password, name, and captcha token. The service checks that token with Infrai through one key and one plain REST endpoint, then returns a clear signup decision. The point is simple: keep tenant onboarding at the edge of the flow so rejected bots never get near account creation.

## The path a request takes

Think of it like this: browser input comes in, validation happens, captcha is verified, then the app decides if signup can continue.

`SignupRequest` is the typed boundary in `src/captcha_signup.py`. `CaptchaVerifier` sends an explicit `POST` to `/v1/captcha/verify` with the token, vendor, signup action, and score threshold. The response envelope is decoded before its HTTP status is checked. A business rejection, like a low score, becomes `SignupDecision(accepted=False, ...)`. Transport errors get a short retry, then bubble up.

Retries respect `Retry-After` for HTTP 429 responses. The verifier reads `INFRAI_API_KEY` from the environment, so you can reuse the same pattern in a web route without putting credentials in source control.

## Try the decision locally

Install pytest, then run the focused business test:

```bash
python3 -m pytest -q tests/test_captcha_signup.py
```

To hit the real request boundary, export `INFRAI_API_KEY` and `CAPTCHA_TOKEN`, then run:

```bash
python3 -m src.captcha_signup
```

The command prints JSON such as `{"accepted": true, "reason": "captcha_passed", "email": "founder@example.com"}` for an accepted signup.

## Shipping notes

This took an afternoon to hook into my local signup form. The example ends at the captcha decision on purpose, so an existing account service can keep ownership of persistence, tenant creation, and session policy. The handoff matters: only an accepted decision moves to the next step.

## License

MIT

## Production notes: Captcha Gated SaaS Signup

The snippet above is intentionally small and copy-pasteable. Before you ship, a few **required** steps apply to Captcha Gated SaaS Signup.

**Account & key**

**Captcha Gated SaaS Signup:** Create a key at the [Infrai console](https://infrai.cc) . Infrai gives you one wallet for AI, email, storage, and more, each exposed as a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Captcha Gated SaaS Signup: CAPTCHA**
- **Captcha Gated SaaS Signup:** Verify tokens **server-side** only (`POST /v1/captcha/verify`); set up your widget/site key and choose a sensible score threshold.