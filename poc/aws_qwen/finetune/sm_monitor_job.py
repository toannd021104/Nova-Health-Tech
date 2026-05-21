"""Monitor a SageMaker Training Job and download the model when done.

Usage:
    # Tail logs until job completes
    python poc/aws_qwen/finetune/sm_monitor_job.py --job-name nova-qwen35-phase1-30min-0518-1430

    # Download model after job completes
    python poc/aws_qwen/finetune/sm_monitor_job.py --job-name <name> --download --output models/qwen-student-phase1
"""
from __future__ import annotations

import argparse
import logging
import os
import subprocess
import sys
import time
from pathlib import Path

import boto3

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

AWS_PROFILE = "gapv50k"
REGION = "ap-southeast-1"
S3_BUCKET = "ha-cg9jlwnsyxvkzs1idwnrzxq-307711587176"
S3_PREFIX = "sagemaker/qwen-finetune"

TERMINAL_STATES = {"Completed", "Failed", "Stopped"}


def get_session():
    return boto3.Session(profile_name=AWS_PROFILE, region_name=REGION)


def get_job_status(sm, job_name: str) -> dict:
    resp = sm.describe_training_job(TrainingJobName=job_name)
    return {
        "status": resp["TrainingJobStatus"],
        "secondary": resp.get("SecondaryStatus", ""),
        "start": resp.get("TrainingStartTime"),
        "end": resp.get("TrainingEndTime"),
        "failure": resp.get("FailureReason", ""),
        "model_s3": resp.get("ModelArtifacts", {}).get("S3ModelArtifacts", ""),
    }


def tail_logs(session, job_name: str, poll_interval: int = 15) -> str:
    """Poll job status and stream CloudWatch logs until terminal state."""
    sm = session.client("sagemaker")
    logs = session.client("logs")

    log_group = "/aws/sagemaker/TrainingJobs"
    log_stream_prefix = f"{job_name}/algo-1-"
    seen_tokens: dict[str, str] = {}
    last_status = ""

    log.info("Monitoring job: %s", job_name)
    log.info("Log group: %s", log_group)

    while True:
        info = get_job_status(sm, job_name)
        status = info["status"]

        if status != last_status:
            log.info("Status: %s | Secondary: %s", status, info["secondary"])
            last_status = status

        # Try to stream logs
        try:
            streams_resp = logs.describe_log_streams(
                logGroupName=log_group,
                logStreamNamePrefix=log_stream_prefix,
                orderBy="LastEventTime",
                descending=True,
                limit=5,
            )
            for stream in streams_resp.get("logStreams", []):
                stream_name = stream["logStreamName"]
                kwargs = {"logGroupName": log_group, "logStreamName": stream_name,
                          "startFromHead": True}
                if stream_name in seen_tokens:
                    kwargs["nextToken"] = seen_tokens[stream_name]

                events_resp = logs.get_log_events(**kwargs)
                for event in events_resp.get("events", []):
                    print(f"  {event['message']}", flush=True)
                seen_tokens[stream_name] = events_resp.get("nextForwardToken", "")
        except Exception:
            pass  # Log stream may not exist yet

        if status in TERMINAL_STATES:
            if status == "Completed":
                log.info("Job completed successfully!")
                log.info("Model artifacts: %s", info["model_s3"])
            elif status == "Failed":
                log.error("Job FAILED: %s", info["failure"])
            else:
                log.warning("Job stopped.")
            return status

        time.sleep(poll_interval)


def download_model(session, job_name: str, output_dir: Path) -> None:
    """Download the trained model from S3 to local output_dir."""
    sm = session.client("sagemaker")
    s3 = session.client("s3")

    info = get_job_status(sm, job_name)
    model_s3 = info["model_s3"]

    if not model_s3:
        log.error("No model artifacts found for job %s", job_name)
        return

    log.info("Downloading model from %s ...", model_s3)
    output_dir.mkdir(parents=True, exist_ok=True)

    # model_s3 is like s3://bucket/prefix/output/model.tar.gz
    bucket = model_s3.split("/")[2]
    key = "/".join(model_s3.split("/")[3:])
    local_tar = output_dir / "model.tar.gz"

    s3.download_file(bucket, key, str(local_tar))
    log.info("Downloaded to %s", local_tar)

    # Extract
    import tarfile  # noqa: PLC0415
    log.info("Extracting ...")
    with tarfile.open(str(local_tar), "r:gz") as tar:
        tar.extractall(str(output_dir))
    local_tar.unlink()

    log.info("Model extracted to %s", output_dir)
    log.info("Files: %s", [f.name for f in output_dir.iterdir()])

    print(f"\nModel ready at: {output_dir}")
    print(f"Set environment variable:")
    print(f"  set STUDENT_MODEL_PATH={output_dir}")
    print(f"Then restart the server to enable /api/student/chat")


def main():
    parser = argparse.ArgumentParser(description="Monitor SageMaker Training Job")
    parser.add_argument("--job-name", required=True, help="SageMaker training job name")
    parser.add_argument("--download", action="store_true",
                        help="Download model after job completes")
    parser.add_argument("--output", default="models/qwen-student",
                        help="Local directory to download model to")
    parser.add_argument("--poll", type=int, default=15,
                        help="Log polling interval in seconds")
    args = parser.parse_args()

    session = get_session()
    final_status = tail_logs(session, args.job_name, args.poll)

    if final_status == "Completed" and args.download:
        download_model(session, args.job_name, Path(args.output))
    elif final_status == "Completed":
        log.info("Job done. Run with --download to fetch the model.")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
