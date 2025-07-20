import json
import numpy as np
import pandas as pd
import os
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, util
from tqdm import tqdm
import torch
import argparse
import openai
import time
import asyncio
import httpx

# ====== API参数 ======
API_KEY = "sk-9aa6QfiEdvoXYLga_D2Q1w"
API_URL = "https://llmapi.blsc.cn/v1/"
REWRITE_MODEL = "DeepSeek-V3-250324-P001"  # 或你实际用的模型名
PROMPT_METHOD = "QueryWithKeywords"  # 标记当前提示词方法
REWRITE_CACHE = f'rewrite_questions_{PROMPT_METHOD}.json'

parser = argparse.ArgumentParser()
parser.add_argument('--mode', choices=['easy', 'hard'], default='easy', help='选择评测集类型：easy（默认，data/test.jsonl）或 hard（data/test_hard_negatives.jsonl）')
args = parser.parse_args()

if args.mode == 'easy':
    test_file = 'data/test.jsonl'
else:
    test_file = 'data/test_hard_negatives.jsonl'

questions = []
answers = []
if args.mode == 'easy':
    with open(test_file, 'r', encoding='utf-8') as f:
        for line in f:
            obj = json.loads(line)
            questions.append(obj['question'].strip())
            answers.append(obj['answer'].strip())
else:
    hard_neg_pool = []
    with open(test_file, 'r', encoding='utf-8') as f:
        for line in f:
            obj = json.loads(line)
            questions.append(obj['question'].strip())
            answers.append(obj['answer'].strip())
            hards = obj.get('hard_negatives', [])
            for hn in hards:
                hard_neg_pool.append(hn.strip())
    answers.extend(hard_neg_pool)

def tokenize(text):
    try:
        import jieba
        return list(jieba.cut(text))
    except ImportError:
        return list(text)

answers_tokenized = [tokenize(a) for a in answers]
bm25 = BM25Okapi(answers_tokenized)

bi_model_path = './model/bge-large-zh-v1.5-finetuned'
bi_model = SentenceTransformer(bi_model_path)

def get_emb_path(model_path, prefix):
    return os.path.join('embeddings_cache', f'emb_cache_{os.path.basename(model_path)}_{prefix}_{args.mode}.npy')

def get_embeddings(model_path, model, texts, prefix):
    emb_path = get_emb_path(model_path, prefix)
    device = next(model.parameters()).device  # 获取模型所在设备
    if os.path.exists(emb_path):
        print(f'从{emb_path}加载embedding...')
        embs = torch.tensor(np.load(emb_path))
    else:
        print(f'计算embedding并保存到{emb_path}...')
        embs = model.encode(texts, batch_size=32, convert_to_tensor=True, show_progress_bar=True)
        np.save(emb_path, embs.cpu().numpy())
    return embs.to(device)

bm25_weight = 0.2
bi_weight = 0.8

N = len(questions)
rank_first_relevant = []
recall_at = {k: 0 for k in range(1, 6)}
mrr_at = {k: 0.0 for k in range(1, 6)}

# ===== 查询改写API调用（并发版） =====
MAX_CONCURRENCY = 16  # 并发数，可根据API限制调整

async def call_rewrite_api(prompt, client, max_retry=3):
    for _ in range(max_retry):
        try:
            resp = await client.post(
                API_URL + "chat/completions" if not API_URL.endswith("completions") else API_URL,
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": REWRITE_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 128
                },
                timeout=60
            )
            if resp.status_code == 200:
                res = resp.json()
                return res["choices"][0]["message"]["content"].strip()
            else:
                print(f"API错误: {resp.status_code}, {resp.text}")
        except Exception as e:
            print(f"API异常，重试: {e}")
        await asyncio.sleep(2)
    return prompt  # 失败时返回原prompt

def get_rewrite_questions(questions):
    # 新的关键词拼接提示词
    def build_prompt(q):
        return (
            "请根据下列问题，先提取出3-5个最能代表该问题语义的关键词，然后将这些关键词用空格拼接，并与原问题用空格拼接，最后只输出拼接后的新查询，不要输出其它内容，不要输出解释。\n"
            f"问题：{q}\n新查询："
        )
    cache_path = REWRITE_CACHE
    async def async_rewrite_all_with_keywords(questions, cache_path):
        if os.path.exists(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                cached = json.load(f)
            if len(cached) == len(questions):
                print("已存在完整缓存，直接返回。")
                return cached
        else:
            cached = [None] * len(questions)
        async with httpx.AsyncClient() as client:
            sem = asyncio.Semaphore(MAX_CONCURRENCY)
            async def rewrite_one(idx, q):
                if cached[idx] is not None:
                    return
                prompt = build_prompt(q)
                async with sem:
                    rewrite = await call_rewrite_api(prompt, client)
                cached[idx] = rewrite
                if (idx+1) % 10 == 0:
                    print(f"已生成{idx+1}/{len(questions)}条改写...")
                    for j in range(idx-9, idx+1):
                        if 0 <= j < len(cached) and cached[j] is not None:
                            print(f"第{j+1}条: {cached[j]}")
            tasks = [rewrite_one(i, q) for i, q in enumerate(questions)]
            await asyncio.gather(*tasks)
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(cached, f, ensure_ascii=False, indent=2)
        return cached
    return asyncio.run(async_rewrite_all_with_keywords(questions, cache_path))

# ===== 获取改写query（并发+缓存） =====
rewrite_questions = get_rewrite_questions(questions)

# 预先获取所有embedding（原始query用于bi-encoder）
question_embs = get_embeddings(bi_model_path, bi_model, questions, 'q')
answer_embs = get_embeddings(bi_model_path, bi_model, answers, 'a')

for idx, (q, bm25_q) in tqdm(list(enumerate(zip(questions, rewrite_questions))), total=N):
    # BM25用改写后的query
    q_tok = tokenize(bm25_q)
    bm25_scores = bm25.get_scores(q_tok)
    # Bi-encoder用原始query
    q_emb = question_embs[idx]
    bi_scores = util.cos_sim(q_emb, answer_embs)[0].cpu().numpy()
    bm25_scores_norm = (bm25_scores - bm25_scores.min()) / (bm25_scores.max() - bm25_scores.min() + 1e-8)
    bi_scores_norm = (bi_scores - bi_scores.min()) / (bi_scores.max() - bi_scores.min() + 1e-8)
    hybrid_scores = bm25_weight * bm25_scores_norm + bi_weight * bi_scores_norm
    top_k = 50
    rerank_indices = np.argsort(-hybrid_scores)[:top_k]
    if idx in rerank_indices:
        rank = np.where(rerank_indices == idx)[0][0]
        rank_first_relevant.append(rank + 1)
        for k in range(1, 6):
            if rank < k:
                recall_at[k] += 1
                mrr_at[k] += 1.0 / (rank + 1)
    else:
        all_indices = np.argsort(-hybrid_scores)
        orig_rank = np.where(all_indices == idx)[0][0]
        rank_first_relevant.append(orig_rank + 1)

recall_at = {f'Recall@{k}': round(recall_at[k]/N, 4) for k in recall_at}
mrr_at = {f'MRR@{k}': round(mrr_at[k]/N, 4) for k in mrr_at}
mean_rank = round(np.mean(rank_first_relevant), 2)

metrics = {
    'MeanRankFirstRelevant': mean_rank,
    **recall_at,
    **mrr_at,
    'model': f'bm25+bi-encoder-mix({bm25_weight},{bi_weight})-top50-{args.mode}-rewrite-{PROMPT_METHOD}'
}
print(f'BM25+Bi-encoder top50加权混合（查询改写，方法：{PROMPT_METHOD}）指标:', metrics)

result = {
    f'bm25+bi-encoder-hybrid-rewrite-{PROMPT_METHOD}': metrics
}
json_path = f'result_compare_{PROMPT_METHOD}.json'
if os.path.exists(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        try:
            all_results = json.load(f)
        except Exception:
            all_results = {}
else:
    all_results = {}
all_results.update(result)
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)
print(f'对比结果已保存到 {json_path}')

csv_name = f'result_compare_all_{args.mode}_rewrite.csv'
all_metrics = []
for model_name, m in result.items():
    row = {'model': model_name}
    row.update(m)
    all_metrics.append(row)
df = pd.DataFrame(all_metrics)
if os.path.exists(csv_name):
    df.to_csv(csv_name, mode='a', index=False, encoding='utf-8-sig', header=False)
else:
    df.to_csv(csv_name, index=False, encoding='utf-8-sig', header=True)
print(f'总和性能已保存到 {csv_name}') 