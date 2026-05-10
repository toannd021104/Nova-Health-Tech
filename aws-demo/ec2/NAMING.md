# Resource Naming Map

All resources are named `HA-<base64url(logical-name)>` (padding stripped). This lets anyone trace a console-visible name back to its purpose.

| Logical name | Encoded tag | AWS resource | Region |
|---|---|---|---|
| `vpc-nova` | `HA-dnBjLW5vdmE` | VPC (10.20.0.0/16) | ap-southeast-1 |
| `subnet-pub` | `HA-c3VibmV0LXB1Yg` | Public subnet (10.20.1.0/24) | ap-southeast-1a |
| `igw-nova` | `HA-aWd3LW5vdmE` | Internet Gateway | - |
| `rt-pub` | `HA-cnQtcHVi` | Public route table | - |
| `sg-web` | `HA-c2ctd2Vi` | Security Group (SSH 22 + HTTP 80 + HTTPS 443) | - |
| `ec2-bedrock` | `HA-ZWMyLWJlZHJvY2s` | IAM role attached to EC2 (Bedrock + S3 read) | global |
| `s3-bucket` | `ha-czmtynvja2v0-<acct>` (lowercased, suffixed) | S3 bucket for RAG source docs | ap-southeast-1 |
| `kb-src` | `HA-a2Itc3Jj` | S3 prefix for RAG ingestion (inside the bucket) | - |
| `ec2-nova` | `HA-ZWMyLW5vdmE` | EC2 instance (t4g.small) | ap-southeast-1a |
| `eip-nova` | `HA-ZWlwLW5vdmE` | Elastic IP attached to the instance | ap-southeast-1 |

## How to reproduce the names

```python
import base64
def tag(name: str) -> str:
    return "HA-" + base64.urlsafe_b64encode(name.encode()).decode().rstrip("=")
```

`tag("vpc-nova")` → `HA-dnBjLW5vdmE`.

## What isn't created (per user request — "no log, firewall, VPN, DR")

- No CloudTrail, CloudWatch alarms, or log aggregation.
- No AWS WAF (only a simple Security Group restricts inbound).
- No Site-to-Site VPN.
- No DR region / snapshot.
- No OpenSearch Serverless (to avoid its cost floor). We use a local FAISS index in the EC2 instance instead — fine for demo.
