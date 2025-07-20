import json
from sentence_transformers import InputExample
from zhconv import convert  # 替换opencc为zhconv

def clean_qa_pair(messages):
    if len(messages) < 2:
        return None
    if messages[0]['role'] != 'user' or messages[1]['role'] != 'assistant':
        return None
    q = messages[0]['content'].strip()
    a = messages[1]['content'].strip()
    # 繁体转简体
    q = convert(q, 'zh-cn')
    a = convert(a, 'zh-cn')
    # 可根据需要调整长度限制
    if not q or not a or len(q) < 2 or len(a) < 2:
        return None
    return (q, a)

# 读取并清洗数据
qa_pairs = []
with open('data/raw_data.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        try:
            obj = json.loads(line)
            pair = clean_qa_pair(obj.get('messages', []))
            if pair:
                qa_pairs.append(pair)
        except Exception as e:
            continue  # 跳过格式错误的行

# 按8:1:1划分
n = len(qa_pairs)
train_end = int(n * 0.8)
val_end = int(n * 0.9)

train_pairs = qa_pairs[:train_end]
val_pairs = qa_pairs[train_end:val_end]
test_pairs = qa_pairs[val_end:]

# 转换为InputExample
train_examples = [InputExample(texts=[q, a], label=1.0) for q, a in train_pairs]
val_examples = [InputExample(texts=[q, a], label=1.0) for q, a in val_pairs]
test_examples = [InputExample(texts=[q, a], label=1.0) for q, a in test_pairs]

print(f"训练集样本数: {len(train_examples)}")
print(f"验证集样本数: {len(val_examples)}")
print(f"测试集样本数: {len(test_examples)}")

# 保存划分结果到data目录
with open('data/train.jsonl', 'w', encoding='utf-8') as f:
    for q, a in train_pairs:
        f.write(json.dumps({'question': q, 'answer': a}, ensure_ascii=False) + '\n')
with open('data/val.jsonl', 'w', encoding='utf-8') as f:
    for q, a in val_pairs:
        f.write(json.dumps({'question': q, 'answer': a}, ensure_ascii=False) + '\n')
with open('data/test.jsonl', 'w', encoding='utf-8') as f:
    for q, a in test_pairs:
        f.write(json.dumps({'question': q, 'answer': a}, ensure_ascii=False) + '\n')
