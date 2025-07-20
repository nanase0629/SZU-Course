from llm_api import call_llm_api
import re
import json

def detect_conflicts(sources, model=None):
    """
    使用大模型API判断不同来源内容是否存在冲突。
    sources: [{'text': '内容', 'type': '来源类型'}]
    返回：(has_conflict, reason)
    has_conflict: True 表示有冲突，False 表示无冲突
    reason: 大模型输出的详细推理过程
    """
    if not sources or len(sources) < 2:
        return False, "内容来源不足，无法检测冲突。"
    # 构造prompt
    context = "\n\n".join([
        f"来源{idx+1}（{item.get('type', '未知')}）：\n{item.get('text', '')}" for idx, item in enumerate(sources)
    ])
    prompt = f"""
你是一个专业的事实核查助手。请判断以下不同来源的内容是否存在事实冲突或矛盾，并详细说明你的推理过程和理由。

{context}

请先输出你的分析推理过程，最后只用一行结论回答"有冲突"或"无冲突"。
"""
    result = call_llm_api(prompt, temperature=0.0, max_tokens=256, model=model)
    has_conflict = False
    reason = result if isinstance(result, str) else str(result)
    if isinstance(result, str):
        if "有冲突" in result:
            has_conflict = True
        elif "无冲突" in result:
            has_conflict = False
    return has_conflict, reason

def extract_facts(text):
    facts = {}
    numbers = re.findall(r'\b\d{4}年|\b\d+%', text)
    if numbers:
        facts['关键数值'] = numbers
    if "产业图谱" in text:
        facts['技术方法'] = list(set(re.findall(r'[A-Za-z]+模型|[A-Z]{2,}算法', text)))
    return facts

def evaluate_source_credibility(source):
    credibility_scores = {
        "gov.cn": 0.9,
        "edu.cn": 0.85,
        "weixin": 0.7,
        "zhihu": 0.6,
        "baidu": 0.5
    }
    url = source.get('url', '')
    if not url:
        return 0.5
    domain_match = re.search(r'//([^/]+)', url)
    if not domain_match:
        return 0.5
    domain = domain_match.group(1)
    for known_domain, score in credibility_scores.items():
        if known_domain in domain:
            return score
    return 0.5 