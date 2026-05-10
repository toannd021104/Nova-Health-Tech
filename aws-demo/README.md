# Nova Health Tech — AWS Demo Web UI (publicly accessible for verification)

Lightweight clinician-facing web app with a right-hand AI assistant panel. Use this to sanity-check the AI service behind it. The UI is intentionally simple; the **production** design of the AI service itself is in `docs/proposals/version_a_aws_claude.md`.

## What it shows

- A minimal clinical portal (patient list, one patient summary, a couple of trials).
- A persistent right-hand AI assistant panel calling Amazon Bedrock through API Gateway + Lambda.
- `bedrock-runtime.converse` with `temperature=0.2, top_p=0.8` — same low-variance settings used by the production plan for tone consistency.

## Not production

The demo deploys without:

- Cognito / hospital SSO (anyone with the URL can chat — fine for a verification demo, not for real use).
- Bedrock Guardrails + Comprehend Medical PHI masking (must be on for real clinical traffic).
- Bedrock Knowledge Base wiring for real RAG (answers come from Claude's training data, not from WHO + internal trials).
- VPC isolation, WAF, CloudTrail → S3 Object Lock.

Wire those up per `docs/proposals/version_a_aws_claude.md` before putting the UI in front of any clinician with real data.

## Files

```
aws-demo/
├── frontend/        ← index.html + app.js + styles.css  (static, S3+CloudFront deploy)
├── backend/         ← chat_handler.py  (Lambda)
├── template.yaml    ← SAM: API Gateway + Lambda + IAM
└── README.md
```

## Quickstart

```bash
cd aws-demo
sam build
sam deploy --guided
```

Copy the `ApiEndpoint` output, open `frontend/index.html` in a browser, paste the endpoint in the top-right box. Try:

- "Summarize immediate management for inferior STEMI."
- "What's the adult sepsis bundle?"

To make it production-grade, continue with the AWS architecture doc — specifically wire up a Bedrock Knowledge Base and switch the router Lambda to the two-lane (student/teacher) pattern.
