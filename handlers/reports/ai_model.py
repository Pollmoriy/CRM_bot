# ai_model.py
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_PATH = "models/tinyllama"

print("⚙️ Загружаем локальную ИИ-модель...")

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, use_fast=False)
model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, torch_dtype=torch.float32)
model.eval()

print("✅ Локальная модель TinyLlama загружена")
