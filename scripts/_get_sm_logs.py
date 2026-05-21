import boto3, sys

JOB = "HA-c20tdHJhaW5pbmctcGhhc2Ux-0518-1656"
REGION = "ap-southeast-1"
PROFILE = "gapv50k"
LOG_GROUP = "/aws/sagemaker/TrainingJobs"

session = boto3.Session(profile_name=PROFILE, region_name=REGION)
logs = session.client("logs")
sm = session.client("sagemaker")

# Get failure reason
desc = sm.describe_training_job(TrainingJobName=JOB)
print(f"Status: {desc['TrainingJobStatus']} / {desc.get('SecondaryStatus','')}")
print(f"Failure: {desc.get('FailureReason','none')}")
print()

# Find stream
streams = logs.describe_log_streams(
    logGroupName=LOG_GROUP,
    logStreamNamePrefix=JOB,
    limit=5,
)["logStreams"]

if not streams:
    print("No log streams found yet")
    sys.exit(0)

stream_name = streams[0]["logStreamName"]
print(f"Stream: {stream_name}\n")

events = logs.get_log_events(
    logGroupName=LOG_GROUP,
    logStreamName=stream_name,
    startFromHead=False,
    limit=80,
)["events"]

# Write to file to avoid encoding issues
with open("sm_logs_latest.txt", "w", encoding="utf-8") as f:
    for e in events:
        msg = e["message"].strip()
        if msg:
            f.write(msg + "\n")

print("Logs written to sm_logs_latest.txt")
print("\nLast 30 lines:")
lines = open("sm_logs_latest.txt", encoding="utf-8").readlines()
for l in lines[-30:]:
    print(l.rstrip())
