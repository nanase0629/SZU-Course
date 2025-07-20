import json
import random
import numpy as np
import torch
from sentence_transformers import SentenceTransformer, InputExample, losses, models, evaluation
from torch.utils.data import DataLoader
import os
from torch.utils.tensorboard import SummaryWriter
from sentence_transformers.evaluation import InformationRetrievalEvaluator, SimilarityFunction

# ===== 设置随机种子，保证实验可复现性 =====
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
torch.cuda.manual_seed_all(SEED)

# ===== 参数设置 =====
LEARNING_RATE = 3e-5  # 学习率
BATCH_SIZE = 8       # 批次大小
EPOCHS = 3            # 训练轮次
WEIGHT_DECAY = 0.01   # 权重衰减
EVAL_STEPS = 500     # 评估步数
OUTPUT_PATH = './model/bge-large-zh-v1.5-finetuned'  # 模型保存路径

# ===== 加载数据集 =====
def load_examples(path):
    examples = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            obj = json.loads(line)
            q = obj['question'].strip()
            a = obj['answer'].strip()
            if q and a:
                examples.append(InputExample(texts=[q, a], label=1.0))
    return examples

train_examples = load_examples('data/train.jsonl')
val_examples = load_examples('data/val.jsonl')

# ===== 加载模型 =====
model = SentenceTransformer('./model/bge-large-zh-v1.5')

# ===== DataLoader，训练集shuffle=True =====
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=BATCH_SIZE)
val_dataloader = DataLoader(val_examples, shuffle=False, batch_size=BATCH_SIZE)

# ===== 损失函数 =====
train_loss = losses.MultipleNegativesRankingLoss(model)

# ===== 评估器（检索式评估） =====
if len(val_examples) > 0:
    # 构建IR评估器所需数据结构
    val_queries = {}
    val_corpus = {}
    val_relevant_docs = {}
    for idx, ex in enumerate(val_examples):
        qid = f"q{idx}"
        did = f"d{idx}"
        val_queries[qid] = ex.texts[0]
        val_corpus[did] = ex.texts[1]
        val_relevant_docs[qid] = set([did])
    evaluator = InformationRetrievalEvaluator(
        queries=val_queries,
        corpus=val_corpus,
        relevant_docs=val_relevant_docs,
        main_score_function=SimilarityFunction.COSINE,
        name='val-ir',
        show_progress_bar=False,
        precision_recall_at_k=[1, 5, 10],
        mrr_at_k=[10]
    )
else:
    evaluator = None

# ===== 计算总步数和预热步数 =====
total_steps = len(train_dataloader) * EPOCHS
warmup_steps = int(total_steps * 0.1)

# ===== TensorBoard日志 =====
writer = SummaryWriter(log_dir='./runs/finetune')

# ===== 训练 =====
model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    evaluator=evaluator,
    epochs=EPOCHS,
    evaluation_steps=EVAL_STEPS,
    output_path=OUTPUT_PATH,
    save_best_model=True,
    show_progress_bar=True,
    warmup_steps=warmup_steps,
    weight_decay=WEIGHT_DECAY,
    optimizer_params={
        'lr': LEARNING_RATE,
        'eps': 1e-6
    }
)

writer.close() 