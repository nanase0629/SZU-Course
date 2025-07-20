from file_processor import process_multiple_pdfs, file_processor, update_bm25_index
from retrieval import recursive_retrieval
from llm_api import call_llm_api
from conflict_detection import detect_conflicts
import glob
import json

# 1. 处理PDF文件（假设你有pdf文件在 ./pdfs/ 目录下）
supported_files = []
for f in glob.glob('./pdf/*'):
    if f.lower().endswith('.pdf') or f.lower().endswith('.txt'):
        supported_files.append(open(f, 'rb'))
status, file_list = process_multiple_pdfs(supported_files)
print("文件处理状态：", status)
print("已处理文件：", file_list)

def build_prompt(contexts, metadatas, question):
    # 带来源标注
    context_lines = []
    for doc, meta in zip(contexts, metadatas):
        if meta.get('source', '').startswith('http') or meta.get('source', '').startswith('www'):
            context_lines.append(f"[网络] {meta.get('title', '')} (URL: {meta.get('url', '')})\n{doc}")
        else:
            context_lines.append(f"[本地] {meta.get('source', '')}\n{doc}")
    context = "\n\n".join(context_lines)
    prompt = f"""你是一个专业的文档问答助手。请仅基于以下参考内容回答用户问题，不要凭空编造。
参考内容：
{context}

用户问题：{question}

请用中文作答，并在结尾注明"【基于知识库检索】"。
"""
    return prompt

# 让用户选择是否启用联网搜索和迭代轮数
enable_web_search = input("是否启用联网搜索？(y/n, 默认n): ").strip().lower() == 'y'
try:
    max_iterations = int(input("请输入递归检索最大轮数（默认2）: ") or 2)
except Exception:
    max_iterations = 2

while True:
    question = input("\n请输入你的问题（输入exit退出）：\n")
    if question.strip().lower() == "exit":
        break
    print(f"\n[INFO] 正在检索（迭代轮数: {max_iterations}, 联网搜索: {'开启' if enable_web_search else '关闭'}）...")

    # 详细打印每轮迭代的检索内容
    all_contexts = []
    all_doc_ids = []
    all_metadata = []
    query = question
    for i in range(max_iterations):
        print(f"\n--- 第{i+1}轮检索 ---")
        from retrieval import faiss_index, faiss_contents_map, faiss_metadatas_map, faiss_id_order_for_index, BM25_MANAGER
        from models import EMBED_MODEL
        import numpy as np
        import logging
        from web_search import update_web_results, check_serpapi_key
        web_results_texts = []
        if enable_web_search and check_serpapi_key():
            web_search_raw_results = update_web_results(query)
            for res in web_search_raw_results:
                text = f"[网络] 标题：{res.get('title', '')}\n摘要：{res.get('snippet', '')}"
                web_results_texts.append(text)
            if web_results_texts:
                print("[联网搜索参考内容]:")
                for idx, wtxt in enumerate(web_results_texts):
                    print(f"  网{idx+1}: {wtxt[:200]}...\n")
        query_embedding = EMBED_MODEL.encode([query])
        query_embedding_np = np.array(query_embedding).astype('float32')
        semantic_results_docs = []
        semantic_results_ids = []
        if faiss_index and faiss_index.ntotal > 0:
            D, I = faiss_index.search(query_embedding_np, k=10)
            for faiss_idx in I[0]:
                if faiss_idx != -1 and faiss_idx < len(faiss_id_order_for_index):
                    original_id = faiss_id_order_for_index[faiss_idx]
                    semantic_results_docs.append(faiss_contents_map.get(original_id, ""))
                    semantic_results_ids.append(original_id)
        bm25_results = BM25_MANAGER.search(query, top_k=10)
        print("[本地检索内容]:")
        for idx, doc in enumerate(semantic_results_docs):
            print(f"  语义{idx+1}: {doc[:200]}...\n")
        for idx, bm in enumerate(bm25_results):
            print(f"  BM25{idx+1}: {bm['content'][:200]}...\n")
        break
    # 继续用recursive_retrieval获取最终上下文
    contexts, doc_ids, metadatas = recursive_retrieval(
        initial_query=question,
        max_iterations=max_iterations,
        enable_web_search=enable_web_search,
        model_choice="siliconflow"
    )
    print("\n【最终检索到的上下文片段（含来源标注）】")
    for i, (ctx, meta) in enumerate(zip(contexts, metadatas)):
        if meta.get('source', '').startswith('http') or meta.get('source', '').startswith('www'):
            print(f"片段{i+1} [网络] {meta.get('title', '')} (URL: {meta.get('url', '')})\n{ctx[:200]}...\n")
        else:
            print(f"片段{i+1} [本地] {meta.get('source', '')}\n{ctx[:200]}...\n")
    # 矛盾检测
    sources_for_conflict = [{'text': doc, 'type': meta.get('source', '本地文档')} for doc, meta in zip(contexts, metadatas)]
    if detect_conflicts(sources_for_conflict):
        print("⚠️ 检测到不同来源内容存在矛盾，请注意甄别！")
    if not contexts:
        print("未检索到相关内容，无法生成答案。")
        continue
    prompt = build_prompt(contexts, metadatas, question)
    try:
        answer = call_llm_api(prompt, temperature=0.7, max_tokens=1536)
        print("\n【大模型生成的答案】\n", answer)
    except Exception as e:
        print("大模型API生成失败：", str(e))