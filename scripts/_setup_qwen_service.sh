#!/bin/bash
set -e

cat > /tmp/nova-qwen.service << 'EOF'
[Unit]
Description=Nova Clinical AI - PoC Version B (Qwen)
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user
Environment=PATH=/opt/nova-qwen/venv/bin:/usr/bin
Environment=AWS_REGION=ap-southeast-1
Environment=BEDROCK_KB_ID=MUEEBGPRSJ
Environment=BEDROCK_GRAPHRAG_KB_ID=FU6SXD0B8B
Environment=STUDENT_ENDPOINT_NAME=HA-c20tc3R1ZGVudC1lcA
ExecStart=/opt/nova-qwen/venv/bin/uvicorn app.server:app --host 0.0.0.0 --port 80
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

sudo mv /tmp/nova-qwen.service /etc/systemd/system/nova-qwen.service
sudo systemctl daemon-reload
sudo systemctl enable nova-qwen.service
sudo systemctl start nova-qwen.service
sleep 3
sudo systemctl status nova-qwen.service --no-pager | head -15
curl -sS http://127.0.0.1:80/healthz || echo "healthz not ready"
