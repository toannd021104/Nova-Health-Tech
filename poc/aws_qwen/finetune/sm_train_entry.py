"""SageMaker Training Job entry point for Qwen3.5-4B SFT + LoRA.

This script runs INSIDE the SageMaker training container.
SageMaker injects environment variables and mounts:
  - /opt/ml/input/data/training/  <- training JSONL (from S3)
  - /opt/ml/model/                <- output model saved here (uploaded to S3)
  - /opt/ml/output/               <- logs and metrics

Hyperparameters passed via --hyperparameters in create_training_job:
  base_model, max_steps, num_epochs, batch_size, grad_accum, lr, use_4bit

Usage (SageMaker runs this automatically):
  python sm_train_entry.py --base_model Qwen/Qwen3.5-4B --max_steps 200
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)

# SageMaker standard paths
SM_INPUT_DIR = Path(os.environ.get("SM_CHANNEL_TRAINING", "/opt/ml/input/data/training"))
SM_MODEL_DIR = Path(os.environ.get("SM_MODEL_DIR", "/opt/ml/model"))
SM_OUTPUT_DIR = Path(os.environ.get("SM_OUTPUT_DATA_DIR", "/opt/ml/output/data"))

LORA_RANK = 16
LORA_ALPHA = 32
LORA_DROPOUT = 0.05
MAX_SEQ_LEN = 1024


def format_chat(example: dict) -> dict:
    """Convert messages list to ChatML text string."""
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


def load_jsonl(path: Path):
    from datasets import Dataset  # noqa: PLC0415
    records = []
    for f in sorted(path.glob("*.jsonl")):
        log.info("Loading %s ...", f)
        with open(f, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    try:
                        records.append(json.loads(line))
                    except Exception:
                        pass
    log.info("Total records: %d", len(records))
    return Dataset.from_list(records)


def train(args: argparse.Namespace) -> None:
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from peft import LoraConfig, get_peft_model, TaskType
        from trl import SFTConfig, SFTTrainer
    except ImportError as e:
        raise SystemExit(f"Missing dep: {e}") from e

    SM_MODEL_DIR.mkdir(parents=True, exist_ok=True)
    SM_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    log.info("=== SageMaker Training Job: Qwen3.5-4B SFT+LoRA ===")
    log.info("Base model: %s", args.base_model)
    log.info("Input dir: %s", SM_INPUT_DIR)
    log.info("Model dir: %s", SM_MODEL_DIR)
    log.info("CUDA available: %s", torch.cuda.is_available())
    if torch.cuda.is_available():
        log.info("GPU: %s (%dMB)", torch.cuda.get_device_name(0),
                 torch.cuda.get_device_properties(0).total_memory // 1024**2)

    # Load tokenizer
    log.info("Loading tokenizer ...")
    tokenizer = AutoTokenizer.from_pretrained(
        args.base_model, trust_remote_code=True, padding_side="right"
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Load model
    log.info("Loading model ...")
    load_kwargs = {
        "trust_remote_code": True,
        "torch_dtype": torch.bfloat16 if torch.cuda.is_available() else torch.float32,
        "device_map": "auto",
    }
    if args.use_4bit:
        from transformers import BitsAndBytesConfig  # noqa: PLC0415
        load_kwargs["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
        )
    model = AutoModelForCausalLM.from_pretrained(args.base_model, **load_kwargs)
    model.enable_input_require_grads()

    # LoRA
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=LORA_RANK,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        target_modules=["q_proj","k_proj","v_proj","o_proj",
                        "gate_proj","up_proj","down_proj"],
        bias="none",
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # Dataset
    dataset = load_jsonl(SM_INPUT_DIR)
    dataset = dataset.map(format_chat, remove_columns=dataset.column_names)
    split = dataset.train_test_split(test_size=0.05, seed=42)
    log.info("Train: %d  Eval: %d", len(split["train"]), len(split["test"]))

    # Training config
    ckpt_dir = str(SM_OUTPUT_DIR / "checkpoints")
    training_args = SFTConfig(
        output_dir=ckpt_dir,
        num_train_epochs=args.num_epochs if args.max_steps < 0 else 1,
        max_steps=args.max_steps,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        warmup_ratio=0.03,
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

    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=split["train"],
        eval_dataset=split["test"],
        tokenizer=tokenizer,
    )

    log.info("Starting training ...")
    trainer.train()

    # Save LoRA adapter separately (merge_and_unload fails with 4-bit on some peft versions)
    # The adapter + base model can be merged locally after download
    log.info("Saving LoRA adapter (skipping merge for 4-bit compatibility) ...")
    model.save_pretrained(str(SM_MODEL_DIR / "adapter"))
    tokenizer.save_pretrained(str(SM_MODEL_DIR / "adapter"))

    # Also save a merge script so the user can merge locally
    merge_script = SM_MODEL_DIR / "merge_adapter.py"
    merge_script.write_text(
        'from peft import PeftModel\n'
        'from transformers import AutoModelForCausalLM, AutoTokenizer\n'
        'import torch, pathlib, sys\n'
        'base = sys.argv[1] if len(sys.argv) > 1 else "Qwen/Qwen3-4B"\n'
        'adapter_path = str(pathlib.Path(__file__).parent / "adapter")\n'
        'out_path = str(pathlib.Path(__file__).parent / "merged")\n'
        'print(f"Loading base {base} ...")\n'
        'model = AutoModelForCausalLM.from_pretrained(base, torch_dtype=torch.bfloat16, device_map="cpu")\n'
        'tokenizer = AutoTokenizer.from_pretrained(adapter_path)\n'
        'print("Applying adapter ...")\n'
        'model = PeftModel.from_pretrained(model, adapter_path)\n'
        'model = model.merge_and_unload()\n'
        'print(f"Saving merged model to {out_path} ...")\n'
        'model.save_pretrained(out_path)\n'
        'tokenizer.save_pretrained(out_path)\n'
        'print("Done.")\n'
    )

    log.info("Adapter saved to %s", SM_MODEL_DIR / "adapter")
    log.info("To merge locally: python merge_adapter.py")

    # Save training summary
    summary = {
        "base_model": args.base_model,
        "max_steps": args.max_steps,
        "num_epochs": args.num_epochs,
        "lora_rank": LORA_RANK,
        "train_samples": len(split["train"]),
        "eval_samples": len(split["test"]),
    }
    with open(SM_MODEL_DIR / "training_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    log.info("Training complete. Model saved to %s", SM_MODEL_DIR)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base_model", default="Qwen/Qwen3.5-4B")
    parser.add_argument("--max_steps", type=int, default=200,
                        help="200 = ~30 min on g4dn.2xlarge. -1 = use epochs.")
    parser.add_argument("--num_epochs", type=int, default=3)
    parser.add_argument("--batch_size", type=int, default=2)
    parser.add_argument("--grad_accum", type=int, default=8)
    parser.add_argument("--lr", type=float, default=2e-4)
    parser.add_argument("--use_4bit", type=lambda x: x.lower() == "true", default=False)
    args = parser.parse_args()
    train(args)


if __name__ == "__main__":
    main()
