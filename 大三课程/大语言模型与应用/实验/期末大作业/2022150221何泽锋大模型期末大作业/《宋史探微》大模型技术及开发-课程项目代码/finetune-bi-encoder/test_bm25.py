import json
import numpy as np
import pandas as pd
import os
from rank_bm25 import BM25Okapi
from tqdm import tqdm
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

# 分词（可用简单空格分词或jieba分词）
def tokenize(text):
    try:
        import jieba
        return list(jieba.cut(text))
    except ImportError:
        return list(text)

answers_tokenized = [tokenize(a) for a in answers]

bm25 = BM25Okapi(answers_tokenized)

N = len(questions)
rank_first_relevant = []
recall_at = {k: 0 for k in range(1, 6)}  # Recall@1-5
mrr_at = {k: 0.0 for k in range(1, 6)}   # MRR@1-5

for idx, q in tqdm(enumerate(questions), total=N):
    q_tok = tokenize(q)
    scores = bm25.get_scores(q_tok)
    sorted_indices = np.argsort(-scores)
    # 正样本排名
    rank = np.where(sorted_indices == idx)[0][0]
    rank_first_relevant.append(rank + 1)
    for k in range(1, 6):
        if rank < k:
            recall_at[k] += 1
            mrr_at[k] += 1.0 / (rank + 1)

recall_at = {f'Recall@{k}': round(recall_at[k]/N, 4) for k in recall_at}
mrr_at = {f'MRR@{k}': round(mrr_at[k]/N, 4) for k in mrr_at}
mean_rank = round(np.mean(rank_first_relevant), 2)

metrics = {
    'MeanRankFirstRelevant': mean_rank,
    **recall_at,
    **mrr_at,
    'model': f'bm25_{args.mode}'
}
print('BM25指标:', metrics)

# 保存对比结果到result_compare.json
result = {
    'bm25': metrics
}
with open('result_compare.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print('对比结果已保存到 result_compare.json')

# 保存总和性能到csv，文件名根据mode区分
csv_name = f'result_compare_all_{args.mode}.csv'
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