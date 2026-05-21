# Fine-tuning Pipeline — Nova Health PoC (AWS + Qwen)

Teacher: **qwen-plus-latest** (DashScope API, Alibaba Cloud Model Studio)
Student: **Qwen/Qwen2.5-1.5B-Instruct** (HuggingFace, SFT + LoRA locally)

---

## Prerequisites

```bash
pip install -r poc/aws_qwen/requirements-finetune.txt
pip install torch --index-url https://download.pytorch.org/whl/cu121  # CUDA 12.1

# HuggingFace token with billing enabled (for DeepInfra provider)
# Get at: https://huggingface.co/settings/tokens
export HF_TOKEN=hf_...
```

## Architecture

```
Qwen/Qwen3.5-397B-A17B  (teacher, 397B MoE, 17B active)
  via HuggingFace InferenceClient -> DeepInfra provider
  $0.54/1M input + $3.40/1M output
        |
        | generates 4000-10000 clinical Q&A
        v
data/distillation/phaseN.jsonl
        |
        | SFT + LoRA (TRL SFTTrainer, SageMaker ml.g4dn.2xlarge)
        v
Qwen/Qwen3.5-4B  (student, 4B dense, fine-tuned)
  saved to S3 -> downloaded locally
        |
        | loaded by server.py /api/student/chat
        v
UI "Student" toggle — compare vs teacher in real time
```

---

## Phase 1 — 30-minute fine-tune (4000 Q&A)

### Step 1: Generate distillation data

```bash
python poc/aws_qwen/finetune/generate_distillation_data.py \
    --phase 1 \
    --output data/distillation/phase1.jsonl
```

This calls **Qwen3.5-397B-A17B** (397B total, 17B active MoE) via HuggingFace InferenceClient routed to **DeepInfra** to generate 4000 clinical Q&A pairs across all 12 departments.
- Requires `HF_TOKEN` with billing enabled
- Cost: ~$1.73 for 4000 Q&A
- Rate: ~200 RPM on DeepInfra = ~20 minutes to generate
- Resume-safe: re-run the same command if interrupted

### Step 2: Train the student

```bash
python poc/aws_qwen/finetune/train_student.py \
    --data data/distillation/phase1.jsonl \
    --output models/qwen-student-phase1 \
    --max-steps 200
```

`--max-steps 200` = approximately 30 minutes on a single GPU (RTX 3070 / T4 / A10).
On CPU only: use `--max-steps 50` (expect ~2 hours).
For QLoRA (4GB VRAM): add `--4bit`.

### Step 3: Start the server with the student model

```bash
export STUDENT_MODEL_PATH=models/qwen-student-phase1/merged
uvicorn poc.aws_qwen.app.server:app --reload --port 8001
```

Open http://localhost:8001 and switch to "Student" mode in the sidebar.

### Step 4: Evaluate

```bash
python poc/aws_qwen/finetune/eval_student.py \
    --student-path models/qwen-student-phase1/merged \
    --eval-data data/distillation/phase1.jsonl \
    --n 100 \
    --output eval_results_phase1.json
```

---

## Phase 2 — Full fine-tune (10000 Q&A)

Only run Phase 2 after Phase 1 looks good (judge score >= 6/10).

```bash
# Generate 10000 Q&A (resumes from phase1 data if you want to extend it)
python poc/aws_qwen/finetune/generate_distillation_data.py \
    --phase 2 \
    --output data/distillation/phase2.jsonl

# Full training (3 epochs, ~2-4 hours on GPU)
python poc/aws_qwen/finetune/train_student.py \
    --data data/distillation/phase2.jsonl \
    --output models/qwen-student-phase2 \
    --epochs 3

# Evaluate
python poc/aws_qwen/finetune/eval_student.py \
    --student-path models/qwen-student-phase2/merged \
    --eval-data data/distillation/phase2.jsonl \
    --n 200 \
    --output eval_results_phase2.json
```

---

## What the eval harness measures

| Metric | Description |
|--------|-------------|
| `avg_judge_score` | 0-10 score from qwen-plus-latest as judge (accuracy + completeness + format + safety) |
| `citation_rate` | % of answers that include [N] citation tags |
| `recommendation_rate` | % of answers that end with "Recommendation:" line |
| `avg_length_ratio` | student tokens / teacher tokens (efficiency) |

Target for Phase 1: judge score >= 6/10, citation rate >= 0.7
Target for Phase 2: judge score >= 7.5/10, citation rate >= 0.85

---

## Architecture

```
DashScope API (qwen-plus-latest)
        |
        | generates 4000-10000 clinical Q&A
        v
data/distillation/phaseN.jsonl
        |
        | SFT + LoRA (TRL SFTTrainer)
        v
models/qwen-student-phaseN/merged/
        |
        | loaded by server.py /api/student/chat
        v
UI "Student" toggle — compare vs teacher in real time
```

---

## Cost estimate

| Item | Phase 1 | Phase 2 |
|------|---------|---------|
| Teacher API (Qwen3.5-397B via DeepInfra) | ~4000 x $0.00043 = $1.73 | ~10000 x $0.00043 = $4.33 |
| SageMaker training (ml.g4dn.2xlarge) | ~0.5hr x $1.05 = $0.53 | ~3hr x $1.05 = $3.15 |
| S3 storage | < $0.01 | < $0.01 |
| **Total** | **~$2.26** | **~$7.49** |

Teacher pricing: DeepInfra Qwen3.5-397B-A17B = $0.54/1M input + $3.40/1M output.
At ~800 tokens/call average (500 in + 300 out): ~$0.00043/call.
