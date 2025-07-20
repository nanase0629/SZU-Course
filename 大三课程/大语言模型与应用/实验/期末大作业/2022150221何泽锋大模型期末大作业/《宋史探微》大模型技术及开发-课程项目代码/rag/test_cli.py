from file_processor import process_multiple_pdfs, file_processor, update_bm25_index
from retrieval import recursive_retrieval
import glob

# 1. 处理PDF文件（假设你有pdf文件在 ./pdfs/ 目录下）
pdf_files = [open(f, 'rb') for f in glob.glob('./pdfs/*.pdf')]
status, file_list = process_multiple_pdfs(pdf_files)
print("文件处理状态：", status)
print("已处理文件：", file_list)

# 2. 命令行输入问题并检索
while True:
    question = input("\n请输入你的问题（输入exit退出）：\n")
    if question.strip().lower() == "exit":
        break
    # 只用本地知识库，不联网
    contexts, doc_ids, metadatas = recursive_retrieval(
        initial_query=question,
        max_iterations=2,
        enable_web_search=False,
        model_choice="ollama"
    )
    print("\n【检索到的上下文片段】")
    for i, ctx in enumerate(contexts):
        print(f"片段{i+1}：{ctx[:200]}...\n")