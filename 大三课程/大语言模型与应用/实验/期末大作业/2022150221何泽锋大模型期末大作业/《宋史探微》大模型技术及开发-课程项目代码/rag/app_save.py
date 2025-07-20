from flask import Flask, request, jsonify, send_from_directory, Response, stream_with_context
# from flask_cors import CORS
import os
import glob
# 导入你的RAG系统组件
from file_processor import process_multiple_pdfs, file_processor, update_bm25_index
from retrieval import recursive_retrieval
from llm_api import call_llm_api
from conflict_detection import detect_conflicts
from TextCleaner import WebScraper, TextCleaner
import logging
import sqlite3

app = Flask(__name__)
# CORS(app)  # 允许跨域请求


# 服务静态HTML文件
@app.route('/')
def serve_html():
    return send_from_directory('.', 'index.html')


@app.route('/api/retrieve', methods=['POST'])
def retrieve():
    try:
        data = request.json
        question = data['question']
        enable_web_search = data.get('enable_web_search', True)
        max_iterations = data.get('max_iterations', 2)
        custom_url = data.get('custom_url', '').strip()
        search_mode = data.get('search_mode', 'quick')

        # 设置联网搜索参数
        if search_mode == 'quick':
            web_max_pages = 2
            web_crawl_depth = 0
        else:
            web_max_pages = 5
            web_crawl_depth = 1

        # 调用你的recursive_retrieval函数
        contexts, doc_ids, metadatas = recursive_retrieval(
            initial_query=question,
            max_iterations=max_iterations,
            enable_web_search=enable_web_search,
            model_choice="siliconflow",
            web_max_pages=web_max_pages,
            web_crawl_depth=web_crawl_depth,
            custom_url=custom_url
        )

        cleaner = TextCleaner()
        custom_context = None
        if custom_url:
            if search_mode == 'quick':
                scraper = WebScraper(max_pages=1, crawl_depth=0)
            else:
                scraper = WebScraper(max_pages=web_max_pages, crawl_depth=web_crawl_depth)
            results_list = []
            if search_mode == 'quick':
                result = scraper.scrape_url(custom_url)
                if result and result.get('content'):
                    content = result.get('content') or ''
                    try:
                        print(f"[调试] 原始网页内容长度: {len(content)}，前100字: {content[:100]}")
                        cleaned = cleaner.clean_text(content)
                        print(f"[调试] clean_text后长度: {len(cleaned)}，前100字: {cleaned[:100]}")
                        deep_cleaned_content = cleaner.clean_content(cleaned)
                        print(f"[调试] clean_content后长度: {len(deep_cleaned_content)}，前100字: {deep_cleaned_content[:100]}")
                    except Exception as e:
                        logging.error(f"TextCleaner clean_content error: {e}")
                        print(f"[调试] clean_content异常: {e}, 回退原始内容，前100字: {content[:100]}")
                        deep_cleaned_content = content
                    custom_context = {
                        'content': deep_cleaned_content,
                        'source': result['url'],
                        'type': '指定网页',
                        'title': result.get('title', ''),
                        'url': result['url']
                    }
            else:
                crawled = scraper.collect_web_data_with_depth([custom_url])
                for res in crawled:
                    if res and res.get('content'):
                        content = res.get('content') or ''
                        try:
                            print(f"[调试] 原始网页内容长度: {len(content)}，前100字: {content[:100]}")
                            cleaned = cleaner.clean_text(content)
                            print(f"[调试] clean_text后长度: {len(cleaned)}，前100字: {cleaned[:100]}")
                            deep_cleaned_content = cleaner.clean_content(cleaned)
                            print(f"[调试] clean_content后长度: {len(deep_cleaned_content)}，前100字: {deep_cleaned_content[:100]}")
                        except Exception as e:
                            logging.error(f"TextCleaner clean_content error: {e}")
                            print(f"[调试] clean_content异常: {e}, 回退原始内容，前100字: {content[:100]}")
                            deep_cleaned_content = content
                        results_list.append({
                            'content': deep_cleaned_content,
                            'source': res['url'],
                            'type': '指定网页',
                            'title': res.get('title', ''),
                            'url': res['url']
                        })
                if results_list:
                    custom_context = results_list

        # 格式化返回结果
        results = []
        for ctx, meta in zip(contexts, metadatas):
            source_type = meta.get('type') if meta.get('type') else ('网络来源' if meta.get('source', '').startswith(('http', 'www')) else '本地文档')
            results.append({
                'content': ctx,
                'source': meta.get('source', '本地文档'),
                'type': source_type,
                'title': meta.get('title', ''),
                'url': meta.get('url', '')
            })

        if custom_context:
            if isinstance(custom_context, list):
                results = custom_context + results
            else:
                results.insert(0, custom_context)

        return jsonify(results)

    except Exception as e:
        import traceback
        logging.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


def init_db():
    conn = sqlite3.connect('qa_history.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS qa_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def save_qa_to_db(question, answer):
    try:
        print(f"[数据库写入] question类型: {type(question)}, 长度: {len(str(question)) if question is not None else 'None'}，前100字: {str(question)[:100] if question else ''}")
        print(f"[数据库写入] answer类型: {type(answer)}, 长度: {len(str(answer)) if answer is not None else 'None'}，前100字: {str(answer)[:100] if answer else ''}")
        conn = sqlite3.connect('qa_history.db')
        c = conn.cursor()
        c.execute('INSERT INTO qa_history (question, answer) VALUES (?, ?)', (question, answer))
        conn.commit()
        conn.close()
    except Exception as e:
        import traceback
        print(f"[数据库写入异常] {e}")
        print(traceback.format_exc())

@app.route('/api/history', methods=['GET'])
def get_history():
    conn = sqlite3.connect('qa_history.db')
    c = conn.cursor()
    c.execute('SELECT id, question, answer, datetime(created_at, "+8 hours") as created_at FROM qa_history ORDER BY id DESC LIMIT 20')
    rows = c.fetchall()
    conn.close()
    return jsonify([
        {'id': row[0], 'question': row[1], 'answer': row[2], 'created_at': row[3]}
        for row in rows
    ])

@app.route('/api/history/<int:history_id>', methods=['DELETE'])
def delete_history(history_id):
    try:
        conn = sqlite3.connect('qa_history.db')
        c = conn.cursor()
        c.execute('DELETE FROM qa_history WHERE id = ?', (history_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        question = data['question']
        contexts = data['contexts']

        # 构建prompt
        prompt = build_prompt(contexts, question)

        # 先调用LLM生成答案
        answer = call_llm_api(prompt, temperature=0.7, max_tokens=1536)

        # 写入数据库
        save_qa_to_db(question, answer)

        # 再进行冲突检测，指定模型为DeepSeek-R1-0528
        sources_for_conflict = [{'text': ctx['content'], 'type': ctx['source']} for ctx in contexts]
        has_conflicts, conflict_reason = detect_conflicts(sources_for_conflict, model="DeepSeek-R1-0528")

        # 格式化返回结果
        response = {
            'answer': answer,
            'sources': contexts,
            'hasConflicts': has_conflicts,
            'conflict_reason': conflict_reason,
            'injected_prompt': prompt
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def build_prompt(contexts, question):
    # 构建prompt的函数
    context_lines = []
    for ctx in contexts:
        source_text = f"[{ctx['type']}] {ctx['title']}" if ctx['title'] else f"[{ctx['type']}]"
        context_lines.append(f"{source_text}\n{ctx['content']}")

    context = "\n\n".join(context_lines)
    prompt = f"""你是一个专业的宋代历史问答助手。请仅基于以下参考内容回答用户问题，不要凭空编造。
参考内容：
{context}

用户问题：{question}

请用中文作答，并在结尾注明"【基于知识库检索】"。
"""
    return prompt


def call_llm_api_stream(prompt, temperature=0.7, max_tokens=1536, model=None):
    from config import LLM_PROVIDER, OPENAI_API_KEY, OPENAI_API_BASE, OPENAI_MODEL
    if LLM_PROVIDER == "openai":
        import openai
        openai.api_key = OPENAI_API_KEY
        openai.base_url = OPENAI_API_BASE
        if model is None:
            model = OPENAI_MODEL
        client = openai.OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE)
        stream = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=4096,
            stream=True
        )
        for chunk in stream:
            if hasattr(chunk, 'choices') and chunk.choices and hasattr(chunk.choices[0], 'delta'):
                delta = chunk.choices[0].delta
                if hasattr(delta, 'content') and delta.content:
                    yield delta.content
            elif hasattr(chunk, 'choices') and chunk.choices and hasattr(chunk.choices[0], 'message'):
                message = chunk.choices[0].message
                if hasattr(message, 'content') and message.content:
                    yield message.content
    else:
        yield "[当前大模型不支持流式输出]"


@app.route('/api/generate_stream', methods=['POST'])
def generate_stream():
    data = request.json
    question = data['question']
    contexts = data['contexts']
    prompt = build_prompt(contexts, question)
    answer_chunks = []
    def generate():
        for chunk in call_llm_api_stream(prompt):
            answer_chunks.append(chunk)
            yield chunk
        # 流式结束后写入数据库
        final_answer = ''.join(answer_chunks)
        save_qa_to_db(question, final_answer)
    return Response(stream_with_context(generate()), mimetype='text/plain')


def detect_conflicts_stream(sources, model=None):
    try:
        if not sources or len(sources) < 2:
            yield "内容来源不足，无法检测冲突。"
            return
        context = "\n\n".join([
            f"来源{idx+1}（{item.get('type', '未知')}）：\n{item.get('text', '')}" for idx, item in enumerate(sources)
        ])
        prompt = f"""
你是一个专业的事实核查助手。请判断以下不同来源的内容是否存在事实冲突或矛盾，并给出简明总结和结论。

{context}

请直接输出你的总结和结论，最后只用一行结论回答"有冲突"或"无冲突"。
"""
        for chunk in call_llm_api_stream(prompt, temperature=0.0, max_tokens=2048, model=model):
            yield chunk
    except Exception as e:
        yield f'\n[冲突检测流式出错: {str(e)}]'

@app.route('/api/conflict_stream', methods=['POST'])
def conflict_stream():
    data = request.json
    contexts = data['contexts']
    sources_for_conflict = [{'text': ctx['content'], 'type': ctx['source']} for ctx in contexts]
    def generate():
        for chunk in detect_conflicts_stream(sources_for_conflict, model="DeepSeek-R1-0528"):
            yield chunk
    return Response(stream_with_context(generate()), mimetype='text/plain')


if __name__ == '__main__':
    # 确保必要的初始化已完成
    supported_files = []
    for f in glob.glob('./pdfs/*'):
        if f.lower().endswith('.pdf') or f.lower().endswith('.txt'):
            supported_files.append(open(f, 'rb'))
    status, file_list = process_multiple_pdfs(supported_files)
    print("文件处理状态：", status)
    print("已处理文件：", file_list)

    # 启动Flask服务器
    app.run(debug=True, port=5000)