import json
import openai
import numpy as np
import torch
import os
import pandas as pd
from sentence_transformers import util
import argparse

API_KEY =   # 请替换为你的API KEY
API_URL = "https://llmapi.blsc.cn/v1/"
MODEL_NAMES = [
    "Doubao-Embedding-Text-P001",
    "Doubao-Embedding-Large-Text-P001",
    "GLM-Embedding-2-P002"
]

parser = argparse.ArgumentParser()
parser.add_argument('--mode', choices=['easy', 'hard'], default='easy', help='选择评测集类型：easy（默认，data/test.jsonl）或 hard（data/test_hard_negatives.jsonl）')
args = parser.parse_args()

if args.mode == 'easy':
    test_file = 'data/test.jsonl'
else:
    test_file = 'data/test_hard_negatives.jsonl'

# 读取测试集
def load_data():
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
    return questions, answers

questions, answers = load_data()

# embedding缓存路径
EMB_CACHE_DIR = 'embeddings_cache'
os.makedirs(EMB_CACHE_DIR, exist_ok=True)

def get_emb_path(model_name, prefix):
    return os.path.join(EMB_CACHE_DIR, f'emb_cache_{model_name}_{prefix}_{args.mode}.npy')

def get_api_embeddings(model_name, texts, prefix):
    emb_path = get_emb_path(model_name, prefix)
    if os.path.exists(emb_path):
        print(f'从{emb_path}加载embedding...')
        return torch.tensor(np.load(emb_path))
    else:
        print(f'通过API获取embedding并保存到{emb_path}...')
        client = openai.OpenAI(api_key=API_KEY, base_url=API_URL)
        all_embs = []
        embedding_dim = None
        if model_name.startswith('GLM-'):
            for idx, text in enumerate(texts):
                try:
                    response = client.embeddings.create(
                        model=model_name,
                        input=text
                    )
                except Exception as e:
                    print(f"[DEBUG] 第{idx}条请求报错，text内容如下：")
                    print(text)
                    print(f"[DEBUG] 异常信息：{e}")
                    continue
                for item in response.data:
                    if item is None:
                        print(f"[DEBUG] 第{idx}条API返回None，text内容如下：")
                        print(text)
                        print("[DEBUG] response对象：", response)
                        print("[DEBUG] item内容：", item)
                        if embedding_dim is not None:
                            all_embs.append([0.0]*embedding_dim)
                        else:
                            print("警告: 第一次API就返回None，无法确定embedding维度")
                            continue
                    elif hasattr(item, 'embedding'):
                        all_embs.append(item.embedding)
                        if embedding_dim is None:
                            embedding_dim = len(item.embedding)
                    elif isinstance(item, dict) and 'embedding' in item:
                        all_embs.append(item['embedding'])
                        if embedding_dim is None:
                            embedding_dim = len(item['embedding'])
                    else:
                        print(f"[DEBUG] 未知item类型: {type(item)}, 内容: {item}")
                        if embedding_dim is not None:
                            all_embs.append([0.0]*embedding_dim)
                        else:
                            print("警告: 未知item类型且无法确定embedding维度")
        else:
            batch_size = 32
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i+batch_size]
                response = client.embeddings.create(
                    model=model_name,
                    input=batch
                )
                for item in response.data:
                    if item is None:
                        print(f"[DEBUG] 批量第{i}条API返回None，batch内容如下：")
                        print(batch)
                        print("[DEBUG] response对象：", response)
                        print("[DEBUG] item内容：", item)
                        if embedding_dim is not None:
                            all_embs.append([0.0]*embedding_dim)
                        else:
                            print("警告: 批量第一次API就返回None，无法确定embedding维度")
                            continue
                    elif hasattr(item, 'embedding'):
                        all_embs.append(item.embedding)
                        if embedding_dim is None:
                            embedding_dim = len(item.embedding)
                    elif isinstance(item, dict) and 'embedding' in item:
                        all_embs.append(item['embedding'])
                        if embedding_dim is None:
                            embedding_dim = len(item['embedding'])
                    else:
                        print(f"[DEBUG] 未知item类型: {type(item)}, 内容: {item}")
                        if embedding_dim is not None:
                            all_embs.append([0.0]*embedding_dim)
                        else:
                            print("警告: 未知item类型且无法确定embedding维度")
        embs = np.array(all_embs)
        np.save(emb_path, embs)
        return torch.tensor(embs)

def evaluate_api(model_name, questions, answers):
    question_embs = get_api_embeddings(model_name, questions, 'q')
    answer_embs = get_api_embeddings(model_name, answers, 'a')
    # 归一化
    question_embs = torch.nn.functional.normalize(question_embs, p=2, dim=1)
    answer_embs = torch.nn.functional.normalize(answer_embs, p=2, dim=1)
    N = len(questions)
    rank_first_relevant = []
    recall_at = {k: 0 for k in range(1, 6)}  # Recall@1-5
    mrr_at = {k: 0.0 for k in range(1, 6)}   # MRR@1-5
    for idx, (q, q_emb) in enumerate(zip(questions, question_embs)):
        scores = util.cos_sim(q_emb, answer_embs)[0]
        sorted_indices = torch.argsort(scores, descending=True)
        rank = (sorted_indices == idx).nonzero(as_tuple=True)[0].item()
        rank_first_relevant.append(rank + 1)
        for k in range(1, 6):
            if rank < k:
                recall_at[k] += 1
                mrr_at[k] += 1.0 / (rank + 1)
    recall_at = {f'Recall@{k}': round(recall_at[k]/N, 4) for k in recall_at}
    mrr_at = {f'MRR@{k}': round(mrr_at[k]/N, 4) for k in mrr_at}
    mean_rank = round(np.mean(rank_first_relevant), 2)
    return {
        'MeanRankFirstRelevant': mean_rank,
        **recall_at,
        **mrr_at
    }

if __name__ == '__main__':
    all_results = {}
    for model_name in MODEL_NAMES:
        print(f'\n===== 评测API模型: {model_name} =====')
        metrics = evaluate_api(model_name, questions, answers)
        print(f'{model_name} 指标:', metrics)
        all_results[model_name] = metrics
    # 保存API结果
    with open(f'result_api_compare_{args.mode}.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f'所有API模型指标已保存到 result_api_compare_{args.mode}.json')

    # 合并本地result_compare.json和API结果到csv
    rows = []
    # 先加载本地模型结果
    if os.path.exists('result_compare.json'):
        with open('result_compare.json', 'r', encoding='utf-8') as f:
            local = json.load(f)
            for k, v in local.items():
                v = v.copy()
                v['model'] = k
                rows.append(v)
    # 加载API模型结果
    for k, v in all_results.items():
        v = v.copy()
        v['model'] = k
        rows.append(v)
    # 转为DataFrame并排序
    df = pd.DataFrame(rows)
    df = df.sort_values('MeanRankFirstRelevant')
    csv_name = f'result_compare_all_{args.mode}.csv'
    if os.path.exists(csv_name):
        df.to_csv(csv_name, mode='a', index=False, encoding='utf-8-sig', header=False)
    else:
        df.to_csv(csv_name, index=False, encoding='utf-8-sig', header=True)
    print(f'所有模型对比结果已保存到 {csv_name}') 