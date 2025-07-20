# 这里只做骨架，后续可细化
import logging
import numpy as np
from bm25 import BM25_MANAGER
from models import EMBED_MODEL, get_cross_encoder, session
from vector_store import faiss_index, faiss_contents_map, faiss_metadatas_map, faiss_id_order_for_index
from web_search import update_web_results, check_serpapi_key
from llm_api import call_llm_api
from config import RERANK_METHOD
from functools import lru_cache
import re


# 递归检索主流程

def recursive_retrieval(
    initial_query,
    max_iterations,
    enable_web_search,
    model_choice,
    web_max_pages=2,
    web_crawl_depth=0,
    custom_url=None
):
    query = initial_query
    all_contexts = []
    all_doc_ids = []
    all_metadata = []
    global faiss_index, faiss_contents_map, faiss_metadatas_map, faiss_id_order_for_index
    for i in range(max_iterations):
        logging.info(f"递归检索迭代 {i + 1}/{max_iterations}，当前查询: {query}")
        web_results_texts = []
        if enable_web_search and check_serpapi_key():
            try:
                web_search_raw_results = update_web_results(query)
                web_search_raw_results = web_search_raw_results[:web_max_pages]  # 只取前N个
                for res in web_search_raw_results:
                    text = f"标题：{res.get('title', '')}\n摘要：{res.get('snippet', '')}"
                    web_results_texts.append(text)
                    all_contexts.append(res.get('snippet', ''))
                    all_metadata.append({
                        'source': res.get('url', ''),
                        'title': res.get('title', ''),
                        'url': res.get('url', ''),
                        'type': '网络来源',
                        'content': res.get('snippet', '')
                    })
            except Exception as e:
                logging.error(f"网络搜索错误: {str(e)}")
        query_embedding = EMBED_MODEL.encode([query])
        query_embedding_np = np.array(query_embedding).astype('float32')
        semantic_results_docs = []
        semantic_results_metadatas = []
        semantic_results_ids = []
        if faiss_index and faiss_index.ntotal > 0:
            try:
                D, I = faiss_index.search(query_embedding_np, k=10)
                for faiss_idx in I[0]:
                    if faiss_idx != -1 and faiss_idx < len(faiss_id_order_for_index):
                        original_id = faiss_id_order_for_index[faiss_idx]
                        semantic_results_docs.append(faiss_contents_map.get(original_id, ""))
                        semantic_results_metadatas.append(faiss_metadatas_map.get(original_id, {}))
                        semantic_results_ids.append(original_id)
            except Exception as e:
                logging.error(f"FAISS 检索错误: {str(e)}")
        bm25_results = BM25_MANAGER.search(query, top_k=10)
        prepared_semantic_results_for_hybrid = {
            "ids": [semantic_results_ids],
            "documents": [semantic_results_docs],
            "metadatas": [semantic_results_metadatas]
        }
        hybrid_results = hybrid_merge(prepared_semantic_results_for_hybrid, bm25_results, alpha=0.7)
        doc_ids_current_iter = []
        docs_current_iter = []
        metadata_list_current_iter = []
        if hybrid_results:
            for doc_id, result_data in hybrid_results[:10]:
                doc_ids_current_iter.append(doc_id)
                docs_current_iter.append(result_data['content'])
                metadata_list_current_iter.append(result_data['metadata'])
        if docs_current_iter:
            try:
                reranked_results = rerank_results(query, docs_current_iter, doc_ids_current_iter,
                                                  metadata_list_current_iter, top_k=5)
            except Exception as e:
                logging.error(f"重排序错误: {str(e)}")
                reranked_results = [(doc_id, {'content': doc, 'metadata': meta, 'score': 1.0})
                                    for doc_id, doc, meta in
                                    zip(doc_ids_current_iter, docs_current_iter, metadata_list_current_iter)]
        else:
            reranked_results = []
        current_contexts_for_llm = web_results_texts[:]
        for doc_id, result_data in reranked_results:
            doc = result_data['content']
            metadata = result_data['metadata']
            if doc_id not in all_doc_ids:
                all_doc_ids.append(doc_id)
                all_contexts.append(doc)
                all_metadata.append(metadata)
            current_contexts_for_llm.append(doc)
        if i == max_iterations - 1:
            break
        if current_contexts_for_llm:
            current_summary = "\n".join(current_contexts_for_llm[:3]) if current_contexts_for_llm else "未找到相关信息"
            next_query_prompt = f"""基于原始问题: {initial_query}
以及已检索信息: 
{current_summary}

分析是否需要进一步查询。如果需要，请提供新的查询问题，使用不同角度或更具体的关键词。
如果已经有充分信息，请回复'不需要进一步查询'。

新查询(如果需要):"""
            try:
                if model_choice == "siliconflow":
                    logging.info("使用SiliconFlow API分析是否需要进一步查询")
                    next_query_result = call_llm_api(next_query_prompt, temperature=0.7, max_tokens=256)
                    if isinstance(next_query_result, tuple):
                        next_query = next_query_result[0].strip()
                    else:
                        next_query = next_query_result.strip()
                    if "<think>" in next_query:
                        next_query = next_query.split("<think>")[0].strip()
                else:
                    logging.info("使用本地Ollama模型分析是否需要进一步查询")
                    response = session.post(
                        "http://localhost:11434/api/generate",
                        json={
                            "model": "deepseek-r1:1.5b",
                            "prompt": next_query_prompt,
                            "stream": False
                        },
                        timeout=30
                    )
                    next_query = response.json().get("response", "").strip()
                if "不需要" in next_query or "不需要进一步查询" in next_query or len(next_query) < 5:
                    logging.info("LLM判断不需要进一步查询，结束递归检索")
                    break
                query = next_query
                logging.info(f"生成新查询: {query}")
            except Exception as e:
                logging.error(f"生成新查询时出错: {str(e)}")
                break
        else:
            break
    return all_contexts, all_doc_ids, all_metadata


def hybrid_merge(semantic_results, bm25_results, alpha=0.7):
    merged_dict = {}
    global faiss_metadatas_map
    if (semantic_results and
            isinstance(semantic_results.get('documents'), list) and len(semantic_results['documents']) > 0 and
            isinstance(semantic_results.get('metadatas'), list) and len(semantic_results['metadatas']) > 0 and
            isinstance(semantic_results.get('ids'), list) and len(semantic_results['ids']) > 0 and
            isinstance(semantic_results['documents'][0], list) and
            isinstance(semantic_results['metadatas'][0], list) and
            isinstance(semantic_results['ids'][0], list) and
            len(semantic_results['documents'][0]) == len(semantic_results['metadatas'][0]) == len(
                semantic_results['ids'][0])):
        num_results = len(semantic_results['documents'][0])
        for i, (doc_id, doc, meta) in enumerate(
                zip(semantic_results['ids'][0], semantic_results['documents'][0], semantic_results['metadatas'][0])):
            score = 1.0 - (i / max(1, num_results))
            merged_dict[doc_id] = {
                'score': alpha * score,
                'content': doc,
                'metadata': meta
            }
    else:
        logging.warning(
            "Semantic results are missing, have an unexpected format, or are empty. Skipping semantic part in hybrid merge.")
    if not bm25_results:
        return sorted(merged_dict.items(), key=lambda x: x[1]['score'], reverse=True)
    valid_bm25_scores = [r['score'] for r in bm25_results if isinstance(r, dict) and 'score' in r]
    max_bm25_score = max(valid_bm25_scores) if valid_bm25_scores else 1.0
    for result in bm25_results:
        if not (isinstance(result, dict) and 'id' in result and 'score' in result and 'content' in result):
            logging.warning(f"Skipping invalid BM25 result item: {result}")
            continue
        doc_id = result['id']
        normalized_score = result['score'] / max_bm25_score if max_bm25_score > 0 else 0
        if doc_id in merged_dict:
            merged_dict[doc_id]['score'] += (1 - alpha) * normalized_score
        else:
            metadata = faiss_metadatas_map.get(doc_id, {})
            merged_dict[doc_id] = {
                'score': (1 - alpha) * normalized_score,
                'content': result['content'],
                'metadata': metadata
            }
    merged_results = sorted(merged_dict.items(), key=lambda x: x[1]['score'], reverse=True)
    return merged_results


def rerank_with_cross_encoder(query, docs, doc_ids, metadata_list, top_k=5):
    if not docs:
        return []
    encoder = get_cross_encoder()
    if encoder is None:
        logging.warning("交叉编码器不可用，跳过重排序")
        return [(doc_id, {'content': doc, 'metadata': meta, 'score': 1.0 - idx / len(docs)})
                for idx, (doc_id, doc, meta) in enumerate(zip(doc_ids, docs, metadata_list))]
    cross_inputs = [[query, doc] for doc in docs]
    try:
        scores = encoder.predict(cross_inputs)
        results = [
            (doc_id, {
                'content': doc,
                'metadata': meta,
                'score': float(score)
            })
            for doc_id, doc, meta, score in zip(doc_ids, docs, metadata_list, scores)
        ]
        results = sorted(results, key=lambda x: x[1]['score'], reverse=True)
        return results[:top_k]
    except Exception as e:
        logging.error(f"交叉编码器重排序失败: {str(e)}")
        return [(doc_id, {'content': doc, 'metadata': meta, 'score': 1.0 - idx / len(docs)})
                for idx, (doc_id, doc, meta) in enumerate(zip(doc_ids, docs, metadata_list))]


@lru_cache(maxsize=32)
def get_llm_relevance_score(query, doc):
    try:
        prompt = f"""给定以下查询和文档片段，评估它们的相关性。
        评分标准：0分表示完全不相关，10分表示高度相关。
        只需返回一个0-10之间的整数分数，不要有任何其他解释。

        查询: {query}

        文档片段: {doc}

        相关性分数(0-10):"""
        response = session.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "deepseek-r1:1.5b",
                "prompt": prompt,
                "stream": False
            },
            timeout=30
        )
        result = response.json().get("response", "").strip()
        try:
            score = float(result)
            score = max(0, min(10, score))
            return score
        except ValueError:
            match = re.search(r'\b([0-9]|10)\b', result)
            if match:
                return float(match.group(1))
            else:
                return 5.0
    except Exception as e:
        logging.error(f"LLM评分失败: {str(e)}")
        return 5.0


def rerank_with_llm(query, docs, doc_ids, metadata_list, top_k=5):
    if not docs:
        return []
    results = []
    for doc_id, doc, meta in zip(doc_ids, docs, metadata_list):
        score = get_llm_relevance_score(query, doc)
        results.append((doc_id, {
            'content': doc,
            'metadata': meta,
            'score': score / 10.0
        }))
    results = sorted(results, key=lambda x: x[1]['score'], reverse=True)
    return results[:top_k]


def rerank_results(query, docs, doc_ids, metadata_list, method=None, top_k=5):
    if method is None:
        method = RERANK_METHOD
    if method == "llm":
        return rerank_with_llm(query, docs, doc_ids, metadata_list, top_k)
    elif method == "cross_encoder":
        return rerank_with_cross_encoder(query, docs, doc_ids, metadata_list, top_k)
    else:
        return [(doc_id, {'content': doc, 'metadata': meta, 'score': 1.0 - idx / len(docs)})
                for idx, (doc_id, doc, meta) in enumerate(zip(doc_ids, docs, metadata_list))] 


def recursive_retrieval_with_rounds(initial_query, max_iterations=3, enable_web_search=False, model_choice="siliconflow"):
    from retrieval import recursive_retrieval as old_recursive
    # 复制自 retrieval.py 的递归主流程，做分轮内容收集
    query = initial_query
    rounds_contexts = []
    rounds_metadatas = []
    all_doc_ids = []
    global faiss_index, faiss_contents_map, faiss_metadatas_map, faiss_id_order_for_index
    for i in range(max_iterations):
        web_results_texts = []
        round_contexts = []
        round_metadatas = []
        if enable_web_search and check_serpapi_key():
            try:
                web_search_raw_results = update_web_results(query)
                for res in web_search_raw_results:
                    text = f"标题：{res.get('title', '')}\n摘要：{res.get('snippet', '')}"
                    web_results_texts.append(text)
                    round_contexts.append(res.get('snippet', ''))
                    round_metadatas.append({
                        'source': res.get('url', ''),
                        'title': res.get('title', ''),
                        'url': res.get('url', ''),
                        'type': '网络来源',
                        'content': res.get('snippet', '')
                    })
            except Exception as e:
                logging.error(f"网络搜索错误: {str(e)}")
        query_embedding = EMBED_MODEL.encode([query])
        query_embedding_np = np.array(query_embedding).astype('float32')
        semantic_results_docs = []
        semantic_results_metadatas = []
        semantic_results_ids = []
        if faiss_index and faiss_index.ntotal > 0:
            try:
                D, I = faiss_index.search(query_embedding_np, k=10)
                for faiss_idx in I[0]:
                    if faiss_idx != -1 and faiss_idx < len(faiss_id_order_for_index):
                        original_id = faiss_id_order_for_index[faiss_idx]
                        semantic_results_docs.append(faiss_contents_map.get(original_id, ""))
                        semantic_results_metadatas.append(faiss_metadatas_map.get(original_id, {}))
                        semantic_results_ids.append(original_id)
            except Exception as e:
                logging.error(f"FAISS 检索错误: {str(e)}")
        bm25_results = BM25_MANAGER.search(query, top_k=10)
        prepared_semantic_results_for_hybrid = {
            "ids": [semantic_results_ids],
            "documents": [semantic_results_docs],
            "metadatas": [semantic_results_metadatas]
        }
        hybrid_results = hybrid_merge(prepared_semantic_results_for_hybrid, bm25_results, alpha=0.7)
        doc_ids_current_iter = []
        docs_current_iter = []
        metadata_list_current_iter = []
        if hybrid_results:
            for doc_id, result_data in hybrid_results[:10]:
                doc_ids_current_iter.append(doc_id)
                docs_current_iter.append(result_data['content'])
                metadata_list_current_iter.append(result_data['metadata'])
        if docs_current_iter:
            try:
                reranked_results = rerank_results(query, docs_current_iter, doc_ids_current_iter,
                                                  metadata_list_current_iter, top_k=5)
            except Exception as e:
                logging.error(f"重排序错误: {str(e)}")
                reranked_results = [(doc_id, {'content': doc, 'metadata': meta, 'score': 1.0})
                                    for doc_id, doc, meta in
                                    zip(doc_ids_current_iter, docs_current_iter, metadata_list_current_iter)]
        else:
            reranked_results = []
        current_contexts_for_llm = web_results_texts[:]
        for doc_id, result_data in reranked_results:
            doc = result_data['content']
            metadata = result_data['metadata']
            if doc_id not in all_doc_ids:
                all_doc_ids.append(doc_id)
                current_contexts_for_llm.append(doc)
            current_contexts_for_llm.append(doc)
        if i == max_iterations - 1:
            break
        if current_contexts_for_llm:
            current_summary = "\n".join(current_contexts_for_llm[:3]) if current_contexts_for_llm else "未找到相关信息"
            next_query_prompt = f"""基于原始问题: {initial_query}
以及已检索信息: 
{current_summary}

分析是否需要进一步查询。如果需要，请提供新的查询问题，使用不同角度或更具体的关键词。
如果已经有充分信息，请回复'不需要进一步查询'。

新查询(如果需要):"""
            try:
                if model_choice == "siliconflow":
                    logging.info("使用SiliconFlow API分析是否需要进一步查询")
                    next_query_result = call_llm_api(next_query_prompt, temperature=0.7, max_tokens=256)
                    if isinstance(next_query_result, tuple):
                        next_query = next_query_result[0].strip()
                    else:
                        next_query = next_query_result.strip()
                    if "<think>" in next_query:
                        next_query = next_query.split("<think>")[0].strip()
                else:
                    logging.info("使用本地Ollama模型分析是否需要进一步查询")
                    response = session.post(
                        "http://localhost:11434/api/generate",
                        json={
                            "model": "deepseek-r1:1.5b",
                            "prompt": next_query_prompt,
                            "stream": False
                        },
                        timeout=30
                    )
                    next_query = response.json().get("response", "").strip()
                if "不需要" in next_query or "不需要进一步查询" in next_query or len(next_query) < 5:
                    logging.info("LLM判断不需要进一步查询，结束递归检索")
                    break
                query = next_query
                logging.info(f"生成新查询: {query}")
            except Exception as e:
                logging.error(f"生成新查询时出错: {str(e)}")
                break
        else:
            break
        rounds_contexts.append(round_contexts)
        rounds_metadatas.append(round_metadatas)
    return rounds_contexts, rounds_metadatas 