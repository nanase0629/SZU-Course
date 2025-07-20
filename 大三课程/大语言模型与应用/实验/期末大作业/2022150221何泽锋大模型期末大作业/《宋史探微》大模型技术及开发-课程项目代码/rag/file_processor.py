import os
import time
import logging
from datetime import datetime
from io import StringIO

import numpy as np
import faiss
import jieba
import docx2txt
from pdfminer.high_level import extract_text_to_fp
from langchain_text_splitters import RecursiveCharacterTextSplitter
from Split_Text import AdvancedTextSplitter

# 假设这些对象在别处初始化并导入
# from your_app import app, UPLOAD_FOLDER, allowed_file
from models import EMBED_MODEL
from vector_store import faiss_index, faiss_contents_map, faiss_metadatas_map, faiss_id_order_for_index
from bm25 import BM25_MANAGER



logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class FileProcessor:
    def __init__(self):
        self.processed_files = {}

    def clear_files(self):
        self.processed_files = {}

    def add_file(self, file_name, status='等待处理', chunks=0):
        self.processed_files[file_name] = {
            'status': status,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'chunks': chunks
        }

    def update_status(self, file_name, status, chunks=None):
        if file_name in self.processed_files:
            self.processed_files[file_name]['status'] = status
            if chunks is not None:
                self.processed_files[file_name]['chunks'] = chunks
    
    def get_file_list(self):
        return [
            f"📄 {fname} | {info['status']} ({info['chunks']} 个文本块)"
            for fname, info in self.processed_files.items()
        ]

file_processor = FileProcessor()


def extract_text(filepath):
    """根据文件扩展名提取文本内容"""
    ext = filepath.lower().rsplit('.', 1)[-1]
    if ext == 'pdf':
        output = StringIO()
        with open(filepath, 'rb') as file:
            extract_text_to_fp(file, output)
        return output.getvalue()
    elif ext in ['txt', 'md']: # 将 markdown 文件视为纯文本提取
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()
    elif ext in ['doc', 'docx']:
        try:
            return docx2txt.process(filepath)
        except Exception as e:
            logging.error(f"处理Word文档 {filepath} 时出错: {e}")
            raise ValueError(f"无法处理Word文档: {e}")
    else:
        raise ValueError(f"不支持的文件类型: {filepath}")

# --- 新增函数：在应用启动时加载整个知识库 ---
def load_knowledge_base(knowledge_base_dir='./pdfs'):
    """
    扫描指定目录下的所有 .embedding.npz 文件，将它们加载到内存中，
    并构建初始的FAISS和BM25索引。
    此函数应在应用启动时调用一次。
    """
    global faiss_index, faiss_contents_map, faiss_metadatas_map, faiss_id_order_for_index

    logging.info("--- 开始加载知识库 ---")
    all_chunks = []
    all_embeddings_list = []
    all_metadatas = []
    all_original_ids = []

    # 清理任何已存在的内存数据，确保从一个干净的状态开始
    faiss_index = None
    faiss_contents_map.clear()
    faiss_metadatas_map.clear()
    faiss_id_order_for_index.clear()
    BM25_MANAGER.clear()
    file_processor.clear_files()
    
    found_files = 0
    for filename in os.listdir(knowledge_base_dir):
        if filename.endswith(".embedding.npz"):
            embedding_file_path = os.path.join(knowledge_base_dir, filename)
            original_filename = filename.replace(".embedding.npz", "")
            try:
                logging.info(f"正在加载 embedding 文件: {filename}")
                data = np.load(embedding_file_path, allow_pickle=True)
                
                chunks = data["chunks"].tolist()
                embeddings_np = data["embeddings"]
                metadatas = data["metadatas"].tolist()
                original_ids = data["original_ids"].tolist()
                
                all_chunks.extend(chunks)
                all_embeddings_list.append(embeddings_np)
                all_metadatas.extend(metadatas)
                all_original_ids.extend(original_ids)
                
                file_processor.add_file(original_filename, "已加载", len(chunks))
                found_files += 1
            except Exception as e:
                logging.error(f"加载 embedding 文件 {filename} 失败: {e}")
                file_processor.add_file(original_filename, f"加载失败: {e}")

    if not all_chunks:
        logging.warning("未找到任何 embedding 文件。知识库为空。")
        return "知识库为空，未加载任何文件。", []

    logging.info(f"从 {found_files} 个文件中加载了数据，总计 {len(all_chunks)} 个文本块。")

    # 1. 构建 FAISS 索引
    logging.info("正在从加载的数据构建FAISS索引...")
    all_embeddings_np = np.vstack(all_embeddings_list)
    dimension = all_embeddings_np.shape[1]
    faiss_index = faiss.IndexFlatL2(dimension)
    faiss_index.add(all_embeddings_np)
    
    # 2. 填充内容和元数据映射
    for i, original_id in enumerate(all_original_ids):
        faiss_contents_map[original_id] = all_chunks[i]
        faiss_metadatas_map[original_id] = all_metadatas[i]
    
    faiss_id_order_for_index.extend(all_original_ids)
    logging.info(f"FAISS索引构建完成。总向量数: {faiss_index.ntotal}")

    # 3. 构建 BM25 索引
    update_bm25_index()
    
    summary = f"成功加载 {found_files} 个文件，总计 {len(all_chunks)} 个文本块。"
    logging.info("--- 知识库加载完成 ---")
    return summary, file_processor.get_file_list()


# --- 重构函数：增量式处理并添加新文件 ---
def add_files_to_knowledge_base(file_paths, progress=None):
    """
    处理一批新文件，生成它们的 embedding，然后将它们添加到
    已存在于内存中的FAISS和BM25索引中。
    """
    if not file_paths:
        return "未提供需要处理的文件。", file_processor.get_file_list()

    global faiss_index, faiss_contents_map, faiss_metadatas_map, faiss_id_order_for_index

    processed_results = []
    total_new_chunks = 0
    
    # 仅用于本次上传批次的数据
    batch_chunks = []
    batch_embeddings_list = []
    batch_metadatas = []
    batch_original_ids = []

    # 在文件处理循环外部实例化一次切分器
    text_splitter = AdvancedTextSplitter(
        chunk_size=400,
        chunk_overlap=40,
        default_splitting_method="recursive"  # 可改为"semantic"或"token"
    )

    for idx, file_path in enumerate(file_paths, 1):
        file_name = os.path.basename(file_path)
        file_processor.add_file(file_name) # 添加文件并标记为"等待处理"
        
        try:
            embedding_file = file_path + ".embedding.npz"

            # 正常上传流程下，这里不会存在。但为了健壮性，保留此检查。
            if os.path.exists(embedding_file):
                logging.info(f"发现已存在的 embedding 文件，直接加载: {embedding_file}")
                data = np.load(embedding_file, allow_pickle=True)
                chunks = data["chunks"].tolist()
                embeddings_np = data["embeddings"]
                metadatas = data["metadatas"].tolist()
                original_ids = data["original_ids"].tolist()
            else:
                logging.info(f"正在处理新文件: {file_name}")
                if progress: progress(idx / len(file_paths) * 0.5, desc=f"从 {file_name} 提取文本...")
                text = extract_text(file_path)
                
                # 替换原有的切分逻辑
                chunks_data = text_splitter.split_text(text)
                chunks = [chunk['text'] for chunk in chunks_data]
                if not chunks:
                    raise ValueError("文档内容为空或无法提取文本。")

                doc_id = f"doc_{int(time.time())}_{idx}"
                original_ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
                metadatas = [{"source": file_name, "doc_id": doc_id} for _ in chunks]
                
                if progress: progress(idx / len(file_paths) * 0.5 + 0.2, desc=f"正在向量化 {len(chunks)} 个文本块...")
                embeddings = EMBED_MODEL.encode(chunks, show_progress_bar=False) # 在服务端日志中保持简洁
                embeddings_np = np.array(embeddings).astype('float32')
                
                # 为新文件保存 embedding 文件，以实现持久化
                np.savez_compressed(
                    embedding_file,
                    chunks=np.array(chunks, dtype=object),
                    embeddings=embeddings_np,
                    metadatas=np.array(metadatas, dtype=object),
                    original_ids=np.array(original_ids, dtype=object)
                )
                logging.info(f"已保存新的 embedding 文件: {embedding_file}")
            
            # 将此文件的数据添加到批处理列表中
            batch_chunks.extend(chunks)
            batch_embeddings_list.append(embeddings_np)
            batch_metadatas.extend(metadatas)
            batch_original_ids.extend(original_ids)

            total_new_chunks += len(chunks)
            file_processor.update_status(file_name, "处理完成", len(chunks))
            processed_results.append(f"✅ {file_name}: 成功处理 {len(chunks)} 个文本块。")
            
        except Exception as e:
            error_msg = str(e)
            logging.error(f"处理文件 {file_name} 时出错: {error_msg}")
            file_processor.update_status(file_name, f"处理失败: {error_msg}")
            processed_results.append(f"❌ {file_name}: 处理失败 - {error_msg}")

    # 所有文件处理完毕后，如果_有_新数据，则更新全局索引
    if batch_chunks:
        logging.info(f"正在向知识库中添加 {total_new_chunks} 个新的文本块...")
        if progress: progress(0.8, desc="更新FAISS索引...")
        
        new_embeddings_np = np.vstack(batch_embeddings_list)
        
        # 关键：如果FAISS索引是首次创建，则初始化它
        if faiss_index is None:
            dimension = new_embeddings_np.shape[1]
            faiss_index = faiss.IndexFlatL2(dimension)
            logging.info(f"FAISS索引首次创建，维度为 {dimension}。")
        else:
            # 关键：防御性检查！确保新向量的维度与现有索引的维度匹配
            expected_dim = faiss_index.d
            actual_dim = new_embeddings_np.shape[1]
            if expected_dim != actual_dim:
                error_msg = (
                    f"致命错误：向量维度不匹配！"
                    f"现有FAISS索引需要维度 {expected_dim}，但新文件的向量维度为 {actual_dim}。"
                    f"这可能是因为更换了模型或模型配置不一致。请考虑清空并重建整个知识库。"
                )
                logging.error(error_msg)
                # 抛出一个清晰的异常，而不是让FAISS崩溃
                raise ValueError(error_msg)

        # 维度检查通过后，安全地添加新向量
        faiss_index.add(new_embeddings_np)
        
        # 更新内容和元数据映射
        for i, original_id in enumerate(batch_original_ids):
            faiss_contents_map[original_id] = batch_chunks[i]
            faiss_metadatas_map[original_id] = batch_metadatas[i]
        
        faiss_id_order_for_index.extend(batch_original_ids)
        logging.info(f"FAISS索引更新完成。总向量数: {faiss_index.ntotal}")

        # 使用所有文档（旧+新）重建BM25索引
        if progress: progress(0.95, desc="更新BM25索引...")
        update_bm25_index()

    summary = f"\n处理了 {len(file_paths)} 个文件，新增 {total_new_chunks} 个文本块。"
    processed_results.append(summary)
    
    return "\n".join(processed_results), file_processor.get_file_list()


def update_bm25_index():
    """从内存中完整的文档集合重建BM25索引"""
    global faiss_contents_map, faiss_id_order_for_index
    try:
        doc_ids = faiss_id_order_for_index
        if not doc_ids:
            logging.warning("没有可用于构建BM25索引的文档。")
            BM25_MANAGER.clear()
            return False
        
        documents = [faiss_contents_map.get(doc_id, "") for doc_id in doc_ids]
        
        valid_docs_with_ids = [(doc_id, doc) for doc_id, doc in zip(doc_ids, documents) if doc]
        if not valid_docs_with_ids:
            logging.warning("没有有效的文档内容可用于BM25索引。")
            BM25_MANAGER.clear()
            return False
            
        final_doc_ids, final_documents = zip(*valid_docs_with_ids)

        BM25_MANAGER.build_index(list(final_documents), list(final_doc_ids))
        logging.info(f"BM25索引重建成功。共索引 {len(final_doc_ids)} 个文档。")
        return True
    except Exception as e:
        logging.error(f"更新BM25索引失败: {e}")
        return False
