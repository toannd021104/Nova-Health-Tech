"""Generate HA-<base64url> names for all aws_qwen SageMaker fine-tuning resources."""
import base64

def tag(name: str) -> str:
    return "HA-" + base64.urlsafe_b64encode(name.encode()).decode().rstrip("=")

resources = [
    # SageMaker
    ("sm-training-phase1",   "SageMaker Training Job — Phase 1 (200 steps, ~30 min)"),
    ("sm-training-phase2",   "SageMaker Training Job — Phase 2 (3 epochs, full)"),
    # S3 prefixes (inside existing bucket)
    ("qwen-ft-data-p1",      "S3 prefix: distillation JSONL phase 1"),
    ("qwen-ft-data-p2",      "S3 prefix: distillation JSONL phase 2"),
    ("qwen-ft-source",       "S3 prefix: training entry script tarball"),
    ("qwen-ft-output-p1",    "S3 prefix: trained model artifact phase 1"),
    ("qwen-ft-output-p2",    "S3 prefix: trained model artifact phase 2"),
    # IAM (reuse existing role — no new role needed)
    ("sm-exec-role",         "IAM role: AmazonSageMaker-ExecutionRole-20260313T100722 (existing)"),
    # CloudWatch log group (auto-created by SageMaker)
    ("cw-sm-training",       "CloudWatch log group: /aws/sagemaker/TrainingJobs"),
]

print(f"{'Logical name':<28} {'HA-tag':<36} Description")
print("-" * 100)
for logical, desc in resources:
    print(f"{logical:<28} {tag(logical):<36} {desc}")

print("\n# Python mapping dict:")
print("RESOURCE_NAMES = {")
for logical, desc in resources:
    print(f'    "{logical}": "{tag(logical)}",  # {desc}')
print("}")
