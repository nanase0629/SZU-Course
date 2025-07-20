import json
import os
import asyncio
import httpx
from tqdm import tqdm
import time
import math

API_KEY = "sk-9aa6QfiEdvoXYLga_D2Q1w"  # 请替换为你的API KEY
API_URL = "https://llmapi.blsc.cn/v1/chat/completions"
MODEL_NAME = "DeepSeek-V3-250324-P001"  # 可换为国产大模型
N = 10  # 每个问题生成几个难负样本
IN_PATH = "data/test.jsonl"
OUT_PATH = "data/test_hard_negatives.jsonl"
CACHE_PATH = "data/test_hard_negatives_cache.jsonl"

RPM = 1000  # 每分钟最大请求数
TPM = 1000000  # 每分钟最大tokens数
MAX_CONCURRENCY = 32  # 并发数上限
MAX_TOKENS = 4096  # 放宽max_tokens

# 读取原始数据
data = []
with open(IN_PATH, 'r', encoding='utf-8') as f:
    for line in f:
        obj = json.loads(line)
        data.append(obj)

# 断点续跑：已完成的缓存
done = {}
if os.path.exists(CACHE_PATH):
    with open(CACHE_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            obj = json.loads(line)
            done[obj['question']] = obj

# 速率控制
class RateLimiter:
    def __init__(self, rpm, tpm):
        self.rpm = rpm
        self.tpm = tpm
        self.req_times = []
        self.token_times = []
        self.tokens_used = []
        self.lock = asyncio.Lock()

    async def acquire(self, tokens):
        async with self.lock:
            now = time.time()
            # 清理过期
            self.req_times = [t for t in self.req_times if now-t < 60]
            self.token_times = [t for t in self.token_times if now-t < 60]
            self.tokens_used = self.tokens_used[-len(self.token_times):]
            # 检查速率
            while len(self.req_times) >= self.rpm or (sum(self.tokens_used)+tokens) > self.tpm:
                await asyncio.sleep(0.1)
                now = time.time()
                self.req_times = [t for t in self.req_times if now-t < 60]
                self.token_times = [t for t in self.token_times if now-t < 60]
                self.tokens_used = self.tokens_used[-len(self.token_times):]
            self.req_times.append(now)
            self.token_times.append(now)
            self.tokens_used.append(tokens)

rate_limiter = RateLimiter(RPM, TPM)

def build_prompt(q, a, n):
    return f"""# 角色设定\n你是一位精通宋朝历史的专家，并且擅长为自然语言处理（NLP）信息检索模型设计具有挑战性的评测数据。你的任务是创造"难负样本"。\n\n# 任务说明\n给定一个关于宋朝历史的"问题（Q）"以及其对应的"正确答案段落（A_positive）"，请你生成 {n} 个"难负样本段落（A_hard_negative）"。这些难负样本将用于测试一个信息检索模型区分正确答案与高相似度干扰项的能力。\n\n# 输入信息\n\n**问题 (Q):**\n{q}\n\n**正确答案段落 (A_positive):**\n{a}\n\n# "难负样本段落 (A_hard_negative)"生成要求\n\n生成的每一个"难负样本段落"必须符合以下所有特点：\n\n1.  **不回答问题Q：** 这是最重要的，它绝对不能正确或直接地回答原始的"问题Q"。它可以是部分错误、信息不全、或者回答了另一个相关但不相同的问题。\n2.  **主题相关性/迷惑性：**\n    * 应与"问题Q"或"正确答案段落A_positive"在**主题、涉及的人物、事件、地点、概念或时期**上具有一定的相关性。\n    * 目标是让它看起来**似乎可能**是问题Q的一个合理答案，或者至少是高度相关的背景信息。\n3.  **包含重叠元素：**\n    * 可以包含一些与"问题Q"或"正确答案段落A_positive"相同的**关键词、短语或概念**，以增加迷惑性。\n4.  **内容合理性与风格一致性：**\n    * 内容本身应该是连贯的，并且在宋朝历史的大背景下听起来是** plausible（貌似真实的）**，即使它对于具体问题Q是错误的。\n    * 语言风格应尽量与宋朝史料的风格或"正确答案段落A_positive"的风格保持一致（例如，正式、书面化）。\n5.  **与A_positive有区别：** 必须与"正确答案段落A_positive"在核心事实上有所区别，不能只是A_positive的简单同义改写或微小删改而仍然回答了Q。\n6.  **避免完全无关或荒谬：** 不要生成与宋朝历史完全无关，或内容明显荒谬、逻辑不通的段落。目标是"难（Hard）"而非"不可能（Impossible）"或"愚蠢（Silly）"。\n7.  **信息来源（构思）：** 你可以基于你对宋朝历史的知识来构思这些难负样本，但要确保最终生成的段落对于**原始问题Q**是不正确的答案。你可以想象一个略微偏离主题的史料片段，或者一个包含轻微事实错误的史料片段。\n\n# 输出格式\n请为每个生成的"难负样本段落"提供清晰的标识。如果生成多个，请编号。\n\n{n}个难负样本段落：\n\nA_hard_negative_1:\n[生成的第一个难负样本段落]\n\nA_hard_negative_2:\n[生成的第二个难负样本段落]\n\n...\n\nA_hard_negative_{n}:\n[生成的第n个难负样本段落]\n\n# 现在，请基于上方提供的"问题 (Q)"和"正确答案段落 (A_positive)", 生成 {n} 个符合所有要求的"难负样本段落 (A_hard_negative)"。"""

def parse_hard_negatives(result, n):
    hard_negatives = []
    for i in range(1, n+1):
        key = f"A_hard_negative_{i}:"
        idx = result.find(key)
        if idx == -1:
            alt_keys = [f"{i}.", f"{i}：", f"A_hard_negative_{i}："]
            for alt in alt_keys:
                idx = result.find(alt)
                if idx != -1:
                    key = alt
                    break
        if idx == -1:
            continue
        next_idx = [result.find(f"A_hard_negative_{j}:", idx+1) for j in range(i+1, n+2)]
        next_idx += [result.find(f"{j}.", idx+1) for j in range(i+1, n+2)]
        next_idx += [result.find(f"{j}：", idx+1) for j in range(i+1, n+2)]
        next_idx += [result.find(f"A_hard_negative_{j}：", idx+1) for j in range(i+1, n+2)]
        next_idx = [x for x in next_idx if x != -1]
        end = min(next_idx) if next_idx else len(result)
        text = result[idx+len(key):end].strip().replace('\n', ' ')
        if text:
            hard_negatives.append(text)
    if len(hard_negatives) < n:
        import re
        pattern = r"A_hard_negative_\d+[:：]\s*(.*?)(?=A_hard_negative_\d+[:：]|$)"
        matches = re.findall(pattern, result, re.DOTALL)
        if len(matches) >= n:
            hard_negatives = [m.strip().replace('\n', ' ') for m in matches[:n]]
    return hard_negatives

async def call_api_async(prompt, client, semaphore, rate_limiter, max_retry=3):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 1.0,
        "max_tokens": MAX_TOKENS
    }
    tokens = MAX_TOKENS  # 估算最大消耗
    for _ in range(max_retry):
        async with semaphore:
            await rate_limiter.acquire(tokens)
            try:
                resp = await client.post(API_URL, headers=headers, json=payload, timeout=120)
                if resp.status_code == 200:
                    res = resp.json()
                    if asyncio.iscoroutine(res):
                        res = await res
                    return res["choices"][0]["message"]["content"]
                else:
                    print(f"API错误: {resp.status_code}, {resp.text}")
            except Exception as e:
                print("API异常，重试：", e)
            await asyncio.sleep(2)
    return None

async def get_hard_negatives_with_retry_async(prompt, n, client, semaphore, rate_limiter):
    for _ in range(3):
        result = await call_api_async(prompt, client, semaphore, rate_limiter)
        if result is None:
            continue
        hard_negatives = parse_hard_negatives(result, n)
        if len(hard_negatives) >= n:
            return hard_negatives, result
    print(f"警告：无法正常解析出{n}个难负样本，跳过。\n原始返回：\n{result}")
    return [], result

async def main():
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
    async with httpx.AsyncClient() as client:
        tasks = []
        items = [d for d in data if d['question'] not in done]
        for item in items:
            q, a = item['question'], item['answer']
            prompt = build_prompt(q, a, N)
            tasks.append(get_hard_negatives_with_retry_async(prompt, N, client, semaphore, rate_limiter))
        results = []
        for fut, item in tqdm(zip(asyncio.as_completed(tasks), items), total=len(tasks)):
            hard_negatives, result = await fut
            q, a = item['question'], item['answer']
            print("\n====================")
            print(f"问题: {q}")
            print(f"标准答案: {a}")
            print(f"API返回内容:\n{result}")
            print(f"解析到的hard_negatives: {hard_negatives}")
            print("====================\n")
            if len(hard_negatives) < N:
                continue
            results.append({
                "question": q,
                "answer": a,
                "hard_negatives": hard_negatives
            })
        # 主线程统一写入，避免并发写冲突
        with open(CACHE_PATH, 'a', encoding='utf-8') as fout:
            for r in results:
                fout.write(json.dumps(r, ensure_ascii=False) + '\n')
                fout.flush()
    # 合并缓存为最终输出
    with open(CACHE_PATH, 'r', encoding='utf-8') as fin, open(OUT_PATH, 'w', encoding='utf-8') as fout:
        for line in fin:
            fout.write(line)
    print(f'已生成所有难负样本，输出到{OUT_PATH}')

if __name__ == "__main__":
    asyncio.run(main()) 