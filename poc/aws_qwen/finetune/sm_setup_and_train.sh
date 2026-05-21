#!/bin/bash
# SageMaker container setup script — runs inside the training container.
# Installs latest transformers (for Qwen3.5 support) then launches training.
set -e

echo "=== Installing dependencies ==="
pip install -q \
    "git+https://github.com/huggingface/transformers.git" \
    "bitsandbytes>=0.46.1" \
    peft trl accelerate

echo "=== Starting training ==="
cd /opt/ml/input/data/code
python sm_train_entry.py "$@"
