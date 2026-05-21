"""Deploy the fine-tuned Qwen3-4B student as a SageMaker Endpoint.

Creates:
  - Model (points to the training job artifact in S3)
  - EndpointConfig (ml.g4dn.xlarge, 1x T4 16GB)
  - Endpoint (real-time inference)

Usage:
    python poc/aws_qwen/finetune/sm_deploy_endpoint.py \
        --job-name HA-c20tdHJhaW5pbmctcGhhc2Ux-0518-1656

Cost: ml.g4dn.xlarge = ~$0.74/hr in ap-southeast-1
Remember to delete when done:
    python poc/aws_qwen/finetune/sm_deploy_endpoint.py --delete
"""
from __future__ import annotations

import argparse
import base64
import json
import logging
import time

import boto3

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

AWS_PROFILE = "gapv50k"
REGION = "ap-southeast-1"
ROLE_ARN = "arn:aws:iam::307711587176:role/service-role/AmazonSageMaker-ExecutionRole-20260313T100722"

# HuggingFace Inference DLC — supports PEFT/LoRA loading natively
INFERENCE_IMAGE = (
    "763104351884.dkr.ecr.ap-southeast-1.amazonaws.com/"
    "huggingface-pytorch-inference:2.6.0-transformers5.5.3-gpu-py312-cu124-ubuntu22.04-v2.1"
)

INSTANCE_TYPE = "ml.g4dn.xlarge"  # 1x T4 16GB, $0.74/hr

def _ha(name: str) -> str:
    return "HA-" + base64.urlsafe_b64encode(name.encode()).decode().rstrip("=")

MODEL_NAME = _ha("sm-student-model")           # HA-c20tc3R1ZGVudC1tb2RlbA
ENDPOINT_CONFIG_NAME = _ha("sm-student-epc")   # HA-c20tc3R1ZGVudC1lcGM
ENDPOINT_NAME = _ha("sm-student-ep")           # HA-c20tc3R1ZGVudC1lcA


def get_session():
    return boto3.Session(profile_name=AWS_PROFILE, region_name=REGION)


def deploy(job_name: str) -> str:
    """Deploy the trained model as a SageMaker Endpoint."""
    session = get_session()
    sm = session.client("sagemaker")

    # Get model artifact from training job
    desc = sm.describe_training_job(TrainingJobName=job_name)
    model_s3 = desc["ModelArtifacts"]["S3ModelArtifacts"]
    log.info("Model artifact: %s", model_s3)

    # 1. Create Model
    log.info("Creating model: %s", MODEL_NAME)
    try:
        sm.create_model(
            ModelName=MODEL_NAME,
            PrimaryContainer={
                "Image": INFERENCE_IMAGE,
                "ModelDataUrl": model_s3,
                "Environment": {
                    "HF_MODEL_ID": "Qwen/Qwen3-4B",
                    "HF_TASK": "text-generation",
                    "PEFT_MODEL_ID": "/opt/ml/model/adapter",
                    "MAX_INPUT_LENGTH": "1024",
                    "MAX_TOTAL_TOKENS": "2048",
                    "SM_NUM_GPUS": "1",
                },
            },
            ExecutionRoleArn=ROLE_ARN,
            Tags=[
                {"Key": "Owner", "Value": "nova-health-poc"},
                {"Key": "LogicalName", "Value": "sm-student-model"},
            ],
        )
    except sm.exceptions.ClientError as e:
        if "Cannot create already existing model" in str(e):
            log.info("Model already exists, continuing...")
        else:
            raise

    # 2. Create EndpointConfig
    log.info("Creating endpoint config: %s", ENDPOINT_CONFIG_NAME)
    try:
        sm.create_endpoint_config(
            EndpointConfigName=ENDPOINT_CONFIG_NAME,
            ProductionVariants=[{
                "VariantName": "primary",
                "ModelName": MODEL_NAME,
                "InstanceType": INSTANCE_TYPE,
                "InitialInstanceCount": 1,
                "InitialVariantWeight": 1.0,
            }],
            Tags=[
                {"Key": "Owner", "Value": "nova-health-poc"},
                {"Key": "LogicalName", "Value": "sm-student-epc"},
            ],
        )
    except sm.exceptions.ClientError as e:
        if "Cannot create already existing" in str(e):
            log.info("Endpoint config already exists, continuing...")
        else:
            raise

    # 3. Create Endpoint
    log.info("Creating endpoint: %s (this takes 5-10 min)...", ENDPOINT_NAME)
    try:
        sm.create_endpoint(
            EndpointName=ENDPOINT_NAME,
            EndpointConfigName=ENDPOINT_CONFIG_NAME,
            Tags=[
                {"Key": "Owner", "Value": "nova-health-poc"},
                {"Key": "LogicalName", "Value": "sm-student-ep"},
            ],
        )
    except sm.exceptions.ClientError as e:
        if "Cannot create already existing" in str(e):
            log.info("Endpoint already exists, checking status...")
        else:
            raise

    # 4. Wait for endpoint to be InService
    log.info("Waiting for endpoint to be InService...")
    while True:
        resp = sm.describe_endpoint(EndpointName=ENDPOINT_NAME)
        status = resp["EndpointStatus"]
        log.info("  Status: %s", status)
        if status == "InService":
            break
        elif status == "Failed":
            log.error("Endpoint creation failed: %s", resp.get("FailureReason", "unknown"))
            return ""
        time.sleep(30)

    endpoint_url = f"https://runtime.sagemaker.{REGION}.amazonaws.com/endpoints/{ENDPOINT_NAME}/invocations"
    log.info("Endpoint InService!")
    log.info("Endpoint name: %s", ENDPOINT_NAME)
    log.info("Invoke via boto3: sm_runtime.invoke_endpoint(EndpointName='%s', ...)", ENDPOINT_NAME)

    print(f"\n{'='*60}")
    print(f"Student endpoint deployed: {ENDPOINT_NAME}")
    print(f"Instance: {INSTANCE_TYPE} (~$0.74/hr)")
    print(f"Delete when done: python {__file__} --delete")
    print(f"{'='*60}")

    return ENDPOINT_NAME


def delete_endpoint():
    """Delete the endpoint, config, and model to stop billing."""
    session = get_session()
    sm = session.client("sagemaker")

    for name, delete_fn in [
        (ENDPOINT_NAME, lambda: sm.delete_endpoint(EndpointName=ENDPOINT_NAME)),
        (ENDPOINT_CONFIG_NAME, lambda: sm.delete_endpoint_config(EndpointConfigName=ENDPOINT_CONFIG_NAME)),
        (MODEL_NAME, lambda: sm.delete_model(ModelName=MODEL_NAME)),
    ]:
        try:
            delete_fn()
            log.info("Deleted: %s", name)
        except Exception as e:
            log.warning("Could not delete %s: %s", name, e)

    print("Endpoint resources deleted. Billing stopped.")


def main():
    parser = argparse.ArgumentParser(description="Deploy/delete student SageMaker Endpoint")
    parser.add_argument("--job-name", default="HA-c20tdHJhaW5pbmctcGhhc2Ux-0518-1656",
                        help="Training job name to deploy from")
    parser.add_argument("--delete", action="store_true", help="Delete the endpoint")
    args = parser.parse_args()

    if args.delete:
        delete_endpoint()
    else:
        deploy(args.job_name)


if __name__ == "__main__":
    main()
