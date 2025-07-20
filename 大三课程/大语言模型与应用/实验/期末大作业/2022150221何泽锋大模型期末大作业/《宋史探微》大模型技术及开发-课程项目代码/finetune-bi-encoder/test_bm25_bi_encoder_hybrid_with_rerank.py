import json
import numpy as np
import pandas as pd
import os
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, util, CrossEncoder
from tqdm import tqdm
import torch
import argparse

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

# 分词（优先用jieba）
def tokenize(text):
    try:
        import jieba
        return list(jieba.cut(text))
    except ImportError:
        return list(text)

answers_tokenized = [tokenize(a) for a in answers]
bm25 = BM25Okapi(answers_tokenized)

# 加载Fine-tune过的Bi-encoder
bi_model_path = './model/bge-large-zh-v1.5-finetuned'
bi_model = SentenceTransformer(bi_model_path)

# embedding缓存路径
def get_emb_path(model_path, prefix):
    return os.path.join('embeddings_cache', f'emb_cache_{os.path.basename(model_path)}_{prefix}_{args.mode}.npy')

def get_embeddings(model_path, model, texts, prefix):
    emb_path = get_emb_path(model_path, prefix)
    if os.path.exists(emb_path):
        print(f'从{emb_path}加载embedding...')
        return torch.tensor(np.load(emb_path))
    else:
        print(f'计算embedding并保存到{emb_path}...')
        embs = model.encode(texts, batch_size=32, convert_to_tensor=True, show_progress_bar=True)
        np.save(emb_path, embs.cpu().numpy())
        return embs

# 加载CrossEncoder reranker
rerank_model_path = './model/bge-reranker-large-finetuned'
rerank_model = CrossEncoder(rerank_model_path)

# 混合权重
bm25_weight = 0.2
bi_weight = 0.8

N = len(questions)
rank_first_relevant = []
recall_at = {k: 0 for k in range(1, 6)}  # Recall@1-5
mrr_at = {k: 0.0 for k in range(1, 6)}   # MRR@1-5

# 预先获取所有embedding
question_embs = get_embeddings(bi_model_path, bi_model, questions, 'q')
answer_embs = get_embeddings(bi_model_path, bi_model, answers, 'a')

for idx, q in tqdm(enumerate(questions), total=N):
    q_tok = tokenize(q)
    bm25_scores = bm25.get_scores(q_tok)
    # Bi-encoder对所有答案打分
    q_emb = question_embs[idx]
    bi_scores = util.cos_sim(q_emb, answer_embs)[0].cpu().numpy()
    # 分数归一化
    bm25_scores_norm = (bm25_scores - bm25_scores.min()) / (bm25_scores.max() - bm25_scores.min() + 1e-8)
    bi_scores_norm = (bi_scores - bi_scores.min()) / (bi_scores.max() - bi_scores.min() + 1e-8)
    # 加权混合
    hybrid_scores = bm25_weight * bm25_scores_norm + bi_weight * bi_scores_norm
    # 召回top50
    top_k = 50
    top_indices = np.argsort(-hybrid_scores)[:top_k]
    # rerank重排
    rerank_pairs = [[q, answers[j]] for j in top_indices]
    rerank_scores = rerank_model.predict(rerank_pairs)
    rerank_scores = np.array(rerank_scores)
    rerank_order = np.argsort(-rerank_scores)
    rerank_indices = [top_indices[i] for i in rerank_order]
    # 找正样本在重排后的位置
    if idx in rerank_indices:
        rank = rerank_indices.index(idx)
        rank_first_relevant.append(rank + 1)
        for k in range(1, 6):
            if rank < k:
                recall_at[k] += 1
                mrr_at[k] += 1.0 / (rank + 1)
    else:
        # 正样本未进召回top50，记其在全体中的原始混合分数排名
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
    'model': f'bm25+bi-encoder-mix({bm25_weight},{bi_weight})-top50-{args.mode}+rerank'
}
print('BM25+Bi-encoder混合召回top50+Rerank指标:', metrics)

# 保存对比结果到result_compare.json
result = {
    'bm25+bi-encoder-hybrid+rerank(finetuned)': metrics
}
with open('result_compare.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print('对比结果已保存到 result_compare.json')

# 保存总和性能到csv，文件名根据mode区分
csv_name = f'result_compare_all_{args.mode}1.csv'
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