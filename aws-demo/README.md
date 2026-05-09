# Nova Health Tech — AWS Demo App

Minimal clinician-facing web app with a right-hand AI assistant panel.

## What it shows

- A simple clinical portal (patient list, current patient summary, recent trials) in the main area.
- A persistent right-hand **AI Assistant** panel that streams answers from Amazon Bedrock (Claude Haiku 4.5 by default).
- Calls a Lambda `/chat` endpoint behind API Gateway.
- Uses `bedrock-runtime.converse_stream` for token streaming so the first token shows up inside ~500 ms — important for the "emergency 2-second SLA" scenario.

## Architecture (demo, not production)

```
Browser (static HTML+JS)
      │  HTTPS
      ▼
CloudFront → API Gateway → Lambda (/chat)
                                  │
                                  ▼
                            Amazon Bedrock
                       (Claude Haiku 4.5)
```

Production would add: Cognito auth, Bedrock Guardrails, Bedrock Knowledge Base retrieval, Comprehend Medical PHI scan, VPC, WAF, CloudTrail → S3 Object Lock (see `docs/architecture/AWS_architecture.md`).

## Files

```
aws-demo/
├── frontend/
│   ├── index.html          ← clinical portal + right-panel chat
│   ├── app.js
│   └── styles.css
├── backend/
│   └── chat_handler.py     ← Lambda with Bedrock Converse streaming
├── template.yaml           ← SAM template: API Gateway + Lambda + IAM
└── README.md
```

## Quickstart

### 1. Prereqs

- AWS CLI configured (`aws configure`)
- AWS SAM CLI installed
- Bedrock access enabled for `anthropic.claude-haiku-4-5-*` in your region (Bedrock → Model access)

### 2. Deploy backend

```bash
cd aws-demo
sam build
sam deploy --guided
```

Note the `ApiEndpoint` output.

### 3. Run frontend locally

Open `frontend/index.html` in your browser (or host on any static web server). Paste the `ApiEndpoint` into the settings box at top right.

For production, upload `frontend/` to an S3 bucket and front it with CloudFront.

## Test prompts (scenario-aligned)

- "Summarize the latest WHO sepsis bundle recommendations."
- "A 68-year-old presents with chest pain, ST elevation on lead II–III. What is the immediate protocol?"
- "Compare efficacy of tenecteplase vs alteplase in acute ischemic stroke."

Without the full RAG pipeline wired in, Claude will answer from its training data with a warning. Hooking up Bedrock Knowledge Base is the next step (see `docs/architecture/AWS_architecture.md`).
