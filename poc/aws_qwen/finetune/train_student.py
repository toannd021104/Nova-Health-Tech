"""SFT + LoRA fine-tuning of Qwen2.5-1.5B-Instruct (student) on distillation data.

Teacher: qwen-plus-latest (via DashScope API, generates training data)
Student: Qwen/Qwen2.5-1.5B-Instruct (HuggingFace, fine-tuned locally)

Phase 1 (~30 min on a single GPU):
    python poc/aws_qwen/finetune/train_student.py \
        --data data/distillation/phase1.jsonl \
        --output models/qwen-student-phase1 \
        --max-steps 200

Phase 2 (full fine-tune, ~2-4 hours):
    python poc/aws_qwen/finetune/train_student.py \
        --data data/distillation/phase2.jsonl \
        --output models/qwen-student-phase2 \
        --epochs 3

Requirements:
    pip install transformers>=4.45 trl>=0.12 peft>=0.13 accelerate>=0.34 datasets bitsandbytes

GPU: CUDA recommended. CPU fallback works but is very slow.
     For 30-min training: at least 8GB VRAM (RTX 3070 / T4 / A10).
     For CPU-only: use --max-steps 50 and expect ~2 hours.

The output is a merged LoRA adapter saved as a full model checkpoint.
Set STUDENT_MODEL_PATH=<output> before starting the server to enable /api/student/chat.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
from pathlib import Path

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

BASE_MODEL = "Qwen/Qwen3-4B"    # Standard transformer (qwen3 arch, no Gated DeltaNet)
                                # Fits on T4 16GB with QLoRA. 7M downloads, Apache 2.0.
                                # Qwen3.5-4B uses hybrid Gated DeltaNet which OOMs on T4.
                                # HuggingFace: https://huggingface.co/Qwen/Qwen3-4B
LORA_RANK = 16
LORA_ALPHA = 32
LORA_DROPOUT = 0.05
LEARNING_RATE = 2e-4
WARMUP_RATIO = 0.03
MAX_SEQ_LEN = 1024


def load_dataset_from_jsonl(path: Path):
    """Load JSONL distillation data into a HuggingFace Dataset."""
    from datasets import Dataset  # noqa: PLC0415

    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as e:
                log.warning("Skipping malformed line: %s", e)

    log.info("Loaded %d records from %s", len(records), path)
    return Dataset.from_list(records)


def format_chat(example: dict) -> dict:
    """Convert messages list to a single text string using ChatML format."""
    messages = example.get("messages", [])
    text = ""
    for msg in messages:
        role = msg["role"]
        content = msg["content"]
        if role == "system":
            text += f"<|im_start|>system\n{content}<|im_end|>\n"
        elif role == "user":
            text += f"<|im_start|>user\n{content}<|im_end|>\n"
        elif role == "assistant":
            text += f"<|im_start|>assistant\n{content}<|im_end|>\n"
    return {"text": text}


def train(
    data_path: Path,
    output_dir: Path,
    base_model: str = BASE_MODEL,
    max_steps: int = -1,
    num_epochs: int = 3,
    batch_size: int = 2,
    grad_accum: int = 8,
    learning_rate: float = LEARNING_RATE,
    use_4bit: bool = False,
) -> None:
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
        from peft import LoraConfig, get_peft_model, TaskType
        from trl import SFTTrainer, SFTConfig
    except ImportError as e:
        raise SystemExit(
            f"Missing dependency: {e}\n"
            "Install: pip install transformers trl peft accelerate datasets bitsandbytes"
        ) from e

    output_dir.mkdir(parents=True, exist_ok=True)

    # ── Load tokenizer ────────────────────────────────────────────────────────
    log.info("Loading tokenizer from %s ...", base_model)
    tokenizer = AutoTokenizer.from_pretrained(
        base_model,
        trust_remote_code=True,
        padding_side="right",
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # ── Load base model ───────────────────────────────────────────────────────
    log.info("Loading base model %s ...", base_model)
    load_kwargs: dict = {
        "trust_remote_code": True,
        "torch_dtype": torch.bfloat16 if torch.cuda.is_available() else torch.float32,
        "device_map": "auto",
    }
    if use_4bit:
        from transformers import BitsAndBytesConfig  # noqa: PLC0415
        load_kwargs["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
        )

    model = AutoModelForCausalLM.from_pretrained(base_model, **load_kwargs)
    model.enable_input_require_grads()

    # ── LoRA config ───────────────────────────────────────────────────────────
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=LORA_RANK,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        bias="none",
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # ── Dataset ───────────────────────────────────────────────────────────────
    dataset = load_dataset_from_jsonl(data_path)
    dataset = dataset.map(format_chat, remove_columns=dataset.column_names)

    # Split 95/5 train/eval
    split = dataset.train_test_split(test_size=0.05, seed=42)
    train_ds = split["train"]
    eval_ds = split["test"]
    log.info("Train: %d, Eval: %d", len(train_ds), len(eval_ds))

    # ── Training args ─────────────────────────────────────────────────────────
    training_args = SFTConfig(
        output_dir=str(output_dir / "checkpoints"),
        num_train_epochs=num_epochs if max_steps < 0 else 1,
        max_steps=max_steps,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        gradient_accumulation_steps=grad_accum,
        learning_rate=learning_rate,
        warmup_ratio=WARMUP_RATIO,
        lr_scheduler_type="cosine",
        bf16=torch.cuda.is_available(),
        fp16=False,
        logging_steps=10,
        eval_strategy="steps",
        eval_steps=50,
        save_strategy="steps",
        save_steps=100,
        save_total_limit=2,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        report_to="none",
        dataloader_num_workers=0,
        max_seq_length=MAX_SEQ_LEN,
        dataset_text_field="text",
        packing=False,
    )

    # ── Trainer ───────────────────────────────────────────────────────────────
    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=eval_ds,
        tokenizer=tokenizer,
    )

    log.info("Starting training ...")
    trainer.train()

    # ── Merge LoRA and save full model ────────────────────────────────────────
    log.info("Merging LoRA adapter into base model ...")
    merged_model = model.merge_and_unload()
    final_path = output_dir / "merged"
    merged_model.save_pretrained(str(final_path))
    tokenizer.save_pretrained(str(final_path))
    log.info("Merged model saved to %s", final_path)

    # Save training summary
    summary = {
        "base_model": base_model,
        "data_path": str(data_path),
        "num_train_samples": len(train_ds),
        "num_eval_samples": len(eval_ds),
        "max_steps": max_steps,
        "num_epochs": num_epochs,
        "lora_rank": LORA_RANK,
        "lora_alpha": LORA_ALPHA,
        "learning_rate": learning_rate,
        "output": str(final_path),
    }
    with open(output_dir / "training_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    log.info("Training summary: %s", output_dir / "training_summary.json")

    print(f"\nDone. Set environment variable:")
    print(f"  export STUDENT_MODEL_PATH={final_path}")
    print(f"Then restart the server to enable /api/student/chat")


def main():
    parser = argparse.ArgumentParser(description="Fine-tune Qwen2.5-1.5B student via SFT + LoRA")
    parser.add_argument("--data", required=True, help="Path to JSONL distillation data")
    parser.add_argument("--output", default="models/qwen-student", help="Output directory")
    parser.add_argument("--base-model", default=BASE_MODEL, help="HuggingFace base model ID")
    parser.add_argument("--max-steps", type=int, default=-1,
                        help="Max training steps (-1 = use --epochs). Use 200 for ~30 min.")
    parser.add_argument("--epochs", type=int, default=3, help="Number of epochs (if max-steps=-1)")
    parser.add_argument("--batch-size", type=int, default=2, help="Per-device batch size")
    parser.add_argument("--grad-accum", type=int, default=8, help="Gradient accumulation steps")
    parser.add_argument("--lr", type=float, default=LEARNING_RATE, help="Learning rate")
    parser.add_argument("--4bit", dest="use_4bit", action="store_true",
                        help="Use 4-bit quantization (QLoRA) — reduces VRAM to ~4GB")
    args = parser.parse_args()

    train(
        data_path=Path(args.data),
        output_dir=Path(args.output),
        base_model=args.base_model,
        max_steps=args.max_steps,
        num_epochs=args.epochs,
        batch_size=args.batch_size,
        grad_accum=args.grad_accum,
        learning_rate=args.lr,
        use_4bit=args.use_4bit,
    )


if __name__ == "__main__":
    main()
