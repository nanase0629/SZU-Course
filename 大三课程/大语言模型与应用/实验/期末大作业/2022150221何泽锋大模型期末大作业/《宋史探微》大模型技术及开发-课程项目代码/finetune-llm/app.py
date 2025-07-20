from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import re
app = FastAPI()

# 设置设备
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# 模型路径（本地）
model_path = "./new_model"

# 加载 tokenizer
tokenizer = AutoTokenizer.from_pretrained(
    model_path,
    trust_remote_code=True,
    local_files_only=True
)

# 加载模型，使用 float16 减少显存占用
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    trust_remote_code=True,
    local_files_only=True,
    torch_dtype=torch.float16 if device.type == "cuda" else torch.float32
).to(device)

model.eval()

# 请求格式
class PromptRequest(BaseModel):
    prompt: str
    max_length: int = 256

@app.post("/generate/")
async def generate_text(req: PromptRequest):
    full_prompt = f"{req.prompt.strip()}\n请在 {req.max_length} 个 token 内完整作答，不要输出提示内容。"
    inputs = tokenizer(full_prompt, return_tensors="pt").to(model.device)

    # 生成文本
    outputs = model.generate(
        **inputs,
        max_new_tokens=256,
        do_sample=True,
        temperature=0.7,
        top_p=0.95,
        top_k=50,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.eos_token_id
    )
    # 去除 prompt 部分
    input_len = inputs['input_ids'].shape[1]
    output_ids = outputs[0][input_len:]  # 只保留新生成的 token
    result = tokenizer.decode(output_ids, skip_special_tokens=True).strip()
    clean_result = re.sub(r'^[\s\.,:;!?，。！？【】（）《》“”‘’]+', '', result)
    return clean_result

