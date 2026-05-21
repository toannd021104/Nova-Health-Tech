"""Launch a SageMaker Training Job for Qwen3.5-4B SFT+LoRA.

Full pipeline:
  1. Generate distillation data (Nova Pro teacher -> JSONL) if not already done
  2. Upload JSONL to S3
  3. Package the training script into a source tarball
  4. Submit SageMaker Training Job on ml.g4dn.2xlarge (T4 16GB, Singapore)
  5. Print job name and CloudWatch log stream URL

Usage:
    # Phase 1 — 30 min fine-tune (200 steps, ~4000 Q&A)
    python poc/aws_qwen/finetune/sm_launch_training.py --phase 1

    # Phase 2 — full fine-tune (3 epochs, ~10000 Q&A)
    python poc/aws_qwen/finetune/sm_launch_training.py --phase 2

    # Skip data generation (use existing JSONL)
    python poc/aws_qwen/finetune/sm_launch_training.py --phase 1 --skip-datagen

Requirements:
    pip install boto3 sagemaker
    AWS profile gapv50k with SageMaker + S3 + IAM access
"""
from __future__ import annotations

import argparse
import base64
import datetime
import json
import logging
import os
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

import boto3

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# ── HA-naming convention (matches NAMING.md) ──────────────────────────────────
def _ha(logical: str) -> str:
    """HA-<base64url(logical)> with padding stripped."""
    return "HA-" + base64.urlsafe_b64encode(logical.encode()).decode().rstrip("=")

# Resource name map — all AWS-visible names use HA-encoding
RESOURCE_NAMES = {
    "sm-training-phase1": _ha("sm-training-phase1"),  # HA-c20tdHJhaW5pbmctcGhhc2Ux
    "sm-training-phase2": _ha("sm-training-phase2"),  # HA-c20tdHJhaW5pbmctcGhhc2Uy
    "qwen-ft-data-p1":    _ha("qwen-ft-data-p1"),     # HA-cXdlbi1mdC1kYXRhLXAx
    "qwen-ft-data-p2":    _ha("qwen-ft-data-p2"),     # HA-cXdlbi1mdC1kYXRhLXAy
    "qwen-ft-source":     _ha("qwen-ft-source"),      # HA-cXdlbi1mdC1zb3VyY2U
    "qwen-ft-output-p1":  _ha("qwen-ft-output-p1"),   # HA-cXdlbi1mdC1vdXRwdXQtcDE
    "qwen-ft-output-p2":  _ha("qwen-ft-output-p2"),   # HA-cXdlbi1mdC1vdXRwdXQtcDI
}

# ── Config ────────────────────────────────────────────────────────────────────
AWS_PROFILE = "gapv50k"
REGION = "ap-southeast-1"
S3_BUCKET = "ha-cg9jlwnsyxvkzs1idwnrzxq-307711587176"
ROLE_ARN = "arn:aws:iam::307711587176:role/service-role/AmazonSageMaker-ExecutionRole-20260313T100722"
INSTANCE_TYPE = "ml.g4dn.2xlarge"

TRAINING_IMAGE = (
    "763104351884.dkr.ecr.ap-southeast-1.amazonaws.com/"
    "huggingface-pytorch-training:2.5.1-transformers4.49.0-gpu-py311-cu124-ubuntu22.04-v2.1"
)

PHASE_CONFIG = {
    1: {"n_qa": 4000, "max_steps": 200, "num_epochs": 1,
        "data_file": "data/distillation/phase1.jsonl",
        "data_key":  "qwen-ft-data-p1",
        "source_key": "qwen-ft-source",
        "output_key": "qwen-ft-output-p1",
        "job_key":   "sm-training-phase1"},
    2: {"n_qa": 10000, "max_steps": -1, "num_epochs": 3,
        "data_file": "data/distillation/phase2.jsonl",
        "data_key":  "qwen-ft-data-p2",
        "source_key": "qwen-ft-source",
        "output_key": "qwen-ft-output-p2",
        "job_key":   "sm-training-phase2"},
}


def get_session():
    session = boto3.Session(profile_name=AWS_PROFILE, region_name=REGION)
    return session


def generate_data(phase: int, data_file: Path, n_qa: int) -> None:
    """Run the distillation data generator if the file doesn't exist or is too small."""
    if data_file.exists():
        lines = sum(1 for _ in open(data_file, encoding="utf-8"))
        if lines >= n_qa * 0.9:
            log.info("Data file already has %d lines (need %d), skipping generation", lines, n_qa)
            return
        log.info("Data file has %d lines, need %d more", lines, n_qa - lines)

    log.info("Generating %d Q&A pairs via Qwen3.5-397B-A17B (DeepInfra/HuggingFace) ...", n_qa)
    script = Path(__file__).parent / "generate_distillation_data.py"
    result = subprocess.run(
        [sys.executable, str(script), "--phase", str(phase),
         "--output", str(data_file)],
        check=False
    )
    if result.returncode != 0:
        raise RuntimeError(f"Data generation failed with code {result.returncode}")


def upload_data(session, data_file: Path, phase: int) -> str:
    """Upload JSONL to S3 using HA-encoded prefix and return the S3 URI."""
    s3 = session.client("s3")
    config = PHASE_CONFIG[phase]
    ha_prefix = RESOURCE_NAMES[config["data_key"]]
    s3_key = f"{ha_prefix}/training.jsonl"
    log.info("Uploading %s -> s3://%s/%s ...", data_file, S3_BUCKET, s3_key)
    s3.upload_file(str(data_file), S3_BUCKET, s3_key)
    uri = f"s3://{S3_BUCKET}/{s3_key}"
    log.info("Uploaded: %s", uri)
    return uri


def package_source(phase: int) -> str:
    """Package the training entry script + setup script into a tarball, upload to S3."""
    session = get_session()
    s3 = session.client("s3")

    finetune_dir = Path(__file__).parent
    entry_script = finetune_dir / "sm_train_entry.py"
    setup_script = finetune_dir / "sm_setup_and_train.sh"

    with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp:
        tar_path = tmp.name

    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add(str(entry_script), arcname="sm_train_entry.py")
        tar.add(str(setup_script), arcname="sm_setup_and_train.sh")

    ha_prefix = RESOURCE_NAMES[PHASE_CONFIG[phase]["source_key"]]
    s3_key = f"{ha_prefix}/phase{phase}/sourcedir.tar.gz"
    log.info("Uploading source tarball -> s3://%s/%s ...", S3_BUCKET, s3_key)
    s3.upload_file(tar_path, S3_BUCKET, s3_key)
    os.unlink(tar_path)

    uri = f"s3://{S3_BUCKET}/{s3_key}"
    log.info("Source uploaded: %s", uri)
    return uri


def submit_training_job(
    session,
    phase: int,
    data_s3_uri: str,
    source_s3_uri: str,
    config: dict,
    base_model: str,
    use_4bit: bool,
) -> str:
    """Submit the SageMaker Training Job using HA-encoded job name."""
    sm = session.client("sagemaker")

    # Job name: HA-tag + timestamp suffix (SageMaker requires unique names)
    ts = datetime.datetime.now().strftime("%m%d-%H%M")
    ha_job_base = RESOURCE_NAMES[config["job_key"]]
    job_name = f"{ha_job_base}-{ts}"

    ha_output = RESOURCE_NAMES[config["output_key"]]
    output_s3 = f"s3://{S3_BUCKET}/{ha_output}/"

    hyperparameters = {
        "base_model": base_model,
        "max_steps": str(config["max_steps"]),
        "num_epochs": str(config["num_epochs"]),
        "batch_size": "2",
        "grad_accum": "8",
        "lr": "2e-4",
        "use_4bit": str(use_4bit).lower(),
    }

    job_config = {
        "TrainingJobName": job_name,
        "RoleArn": ROLE_ARN,
        "AlgorithmSpecification": {
            "TrainingImage": TRAINING_IMAGE,
            "TrainingInputMode": "File",
            "ContainerEntrypoint": [
                "bash", "-c",
                "cd /opt/ml/input/data/code && tar xzf sourcedir.tar.gz && "
                "bash sm_setup_and_train.sh "
                + " ".join(f"--{k} {v}" for k, v in hyperparameters.items())
            ],
        },
        "HyperParameters": hyperparameters,
        "InputDataConfig": [
            {
                "ChannelName": "training",
                "DataSource": {
                    "S3DataSource": {
                        "S3DataType": "S3Prefix",
                        "S3Uri": data_s3_uri.rsplit("/", 1)[0] + "/",
                        "S3DataDistributionType": "FullyReplicated",
                    }
                },
                "ContentType": "application/jsonlines",
            },
            {
                "ChannelName": "code",
                "DataSource": {
                    "S3DataSource": {
                        "S3DataType": "S3Prefix",
                        "S3Uri": source_s3_uri.rsplit("/", 1)[0] + "/",
                        "S3DataDistributionType": "FullyReplicated",
                    }
                },
            },
        ],
        "OutputDataConfig": {"S3OutputPath": output_s3},
        "ResourceConfig": {
            "InstanceType": INSTANCE_TYPE,
            "InstanceCount": 1,
            "VolumeSizeInGB": 50,
        },
        "StoppingCondition": {
            "MaxRuntimeInSeconds": 7200 if phase == 1 else 28800,
        },
        "Environment": {
            "HF_HOME": "/tmp/hf_cache",
            "TRANSFORMERS_CACHE": "/tmp/hf_cache",
            "HF_DATASETS_CACHE": "/tmp/hf_cache",
        },
        "Tags": [
            {"Key": "Owner", "Value": "nova-health-poc"},
            {"Key": "Phase", "Value": str(phase)},
            {"Key": "LogicalName", "Value": config["job_key"]},
            {"Key": "HAName", "Value": ha_job_base},
        ],
    }

    log.info("Submitting training job: %s", job_name)
    log.info("  Logical name: %s -> %s", config["job_key"], ha_job_base)
    log.info("  Instance: %s | Phase: %d | Steps: %s | Epochs: %s",
             INSTANCE_TYPE, phase, config["max_steps"], config["num_epochs"])
    log.info("  Output S3: %s", output_s3)

    sm.create_training_job(**job_config)

    cw_url = (
        f"https://{REGION}.console.aws.amazon.com/cloudwatch/home"
        f"?region={REGION}#logsV2:log-groups/log-group/"
        f"%2Faws%2Fsagemaker%2FTrainingJobs/log-events/{job_name}%2Falgo-1-*"
    )
    log.info("CloudWatch logs: %s", cw_url)
    return job_name


def main():
    parser = argparse.ArgumentParser(description="Launch SageMaker Training Job for Qwen3.5-4B")
    parser.add_argument("--phase", type=int, choices=[1, 2], default=1)
    parser.add_argument("--base-model", default="Qwen/Qwen3.5-4B")
    parser.add_argument("--skip-datagen", action="store_true",
                        help="Skip data generation, use existing JSONL")
    parser.add_argument("--use-4bit", action="store_true",
                        help="Use QLoRA 4-bit (reduces VRAM, slower)")
    args = parser.parse_args()

    config = PHASE_CONFIG[args.phase]
    data_file = Path(config["data_file"])
    session = get_session()

    # Step 1: Generate distillation data
    if not args.skip_datagen:
        generate_data(args.phase, data_file, config["n_qa"])
    else:
        if not data_file.exists():
            raise SystemExit(f"Data file not found: {data_file}. Run without --skip-datagen first.")
        log.info("Skipping data generation, using: %s", data_file)

    # Step 2: Upload data to S3
    data_s3_uri = upload_data(session, data_file, args.phase)

    # Step 3: Package and upload training script
    source_s3_uri = package_source(args.phase)

    # Step 4: Submit training job
    job_name = submit_training_job(
        session, args.phase, data_s3_uri, source_s3_uri,
        config, args.base_model, args.use_4bit
    )

    print(f"\n{'='*60}")
    print(f"Training job submitted: {job_name}")
    print(f"Monitor with:")
    print(f"  python poc/aws_qwen/finetune/sm_monitor_job.py --job-name {job_name}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
