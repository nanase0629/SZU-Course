import logging
import re
import numpy as np
from typing import List, Dict, Any, Optional, Union, Callable
import nltk # 仍然保留 NLTK，作为 PySBD 之后的后备
import os
# import shutil # 如果不再需要在脚本中删除 nltk_data，可以注释掉

# --- NLTK 数据下载和测试部分 (可以保留或根据需要调整) ---
# print(f"NLTK Version: {nltk.__version__}")
# nltk_data_path_to_use = "/root/nltk_data"
# os.makedirs(nltk_data_path_to_use, exist_ok=True)
# if nltk_data_path_to_use not in nltk.data.path:
#     nltk.data.path.insert(0, nltk_data_path_to_use)
# print(f"NLTK Data Path being used: {nltk.data.path}")
# print("Attempting to download 'punkt' to specified directory...")
# try:
#     nltk.download('punkt', download_dir=nltk_data_path_to_use)
#     print("'punkt' download process completed.")
#     print("Attempting to load default English punkt tokenizer...")
#     tokenizer = nltk.data.load('tokenizers/punkt/PY3/english.pickle')
#     print("Successfully loaded English punkt tokenizer object.")
#     test_sentence = "This is a test. This is another test."
#     sentences = nltk.sent_tokenize(test_sentence)
#     print(f"Test sentence tokenization (English): {sentences}")
# except Exception as e:
#     print(f"An error occurred during NLTK setup or test: {e}")
# --- NLTK 数据下载和测试部分结束 ---


# LangChain for recursive splitting
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Sentence Transformers for semantic splitting embeddings
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

# Scikit-learn for cosine similarity
from sklearn.metrics.pairwise import cosine_similarity

# Tiktoken for OpenAI token counting
try:
    import tiktoken
except ImportError:
    tiktoken = None

# Hugging Face Transformers for general token counting
try:
    from transformers import AutoTokenizer
except ImportError:
    AutoTokenizer = None

# PySBD for sentence segmentation
try:
    import pysbd
    logger_pysbd_init = logging.getLogger(__name__ + ".pysbd_check") # Specific logger
    logger_pysbd_init.info("PySBD 库已成功导入。")
except ImportError:
    pysbd = None
    logger_pysbd_init = logging.getLogger(__name__ + ".pysbd_check")
    logger_pysbd_init.warning("PySBD 库未安装，句子切分功能将受限。请运行 'pip install pysbd'")


logger = logging.getLogger(__name__)

class AdvancedTextSplitter:
    """
    一个高级文本切分器，支持多种切分策略。
    """
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        length_function: Callable[[str], int] = len,
        default_splitting_method: str = "recursive",
        recursive_separators: Optional[List[str]] = None,
        semantic_sentence_embedder: Optional[Union[str, Any]] = "./models/paraphrase-multilingual-MiniLM-L12-v2",
        semantic_similarity_threshold: float = 0.7,
        semantic_min_chunk_sentences: int = 2,
        semantic_max_chunk_sentences: int = 10,
        tokenizer_name_or_path: Optional[str] = "gpt-3.5-turbo",
        sentence_segmenter_language: str = "zh" # PySBD 语言参数
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self._length_function_type = "char"
        if length_function == len:
            self.length_function = len
        elif hasattr(length_function, '__name__') and length_function.__name__ == 'get_token_count':
            self.length_function = self.get_token_count
            self._length_function_type = "token"
        else:
            self.length_function = length_function
        self.default_splitting_method = default_splitting_method.lower()

        self.tokenizer = None
        self.tokenizer_type = None
        if tokenizer_name_or_path:
            try:
                if tiktoken and any(m in tokenizer_name_or_path for m in ["gpt-4", "gpt-3.5", "text-embedding"]):
                    self.tokenizer = tiktoken.encoding_for_model(tokenizer_name_or_path)
                    self.tokenizer_type = 'tiktoken'
                    logger.info(f"使用 tiktoken tokenizer for model: {tokenizer_name_or_path}")
                elif AutoTokenizer:
                    self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name_or_path)
                    self.tokenizer_type = 'hf'
                    logger.info(f"使用 Hugging Face tokenizer: {tokenizer_name_or_path}")
            except Exception as e:
                logger.warning(f"初始化 tokenizer '{tokenizer_name_or_path}' 失败: {e}.")
        if self._length_function_type == "token" and not self.tokenizer:
            logger.warning("选择了基于token的长度函数，但tokenizer未成功初始化。回退到字符长度。")
            self.length_function = len
            self._length_function_type = "char"

        self.recursive_separators = recursive_separators or ["\n\n", "\n", "。", "！", "？", ". ", " ", ""]
        self.recursive_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=self.length_function,
            separators=self.recursive_separators,
            add_start_index=True
        )

        self.semantic_sentence_embedder_model = None
        # 修改SBERT加载逻辑，使其更明确从本地路径加载
        if semantic_sentence_embedder and SentenceTransformer:
            if isinstance(semantic_sentence_embedder, str) and os.path.exists(semantic_sentence_embedder):
                try:
                    self.semantic_sentence_embedder_model = SentenceTransformer(semantic_sentence_embedder)
                    logger.info(f"成功从本地路径加载语义切分嵌入模型: {semantic_sentence_embedder}")
                except Exception as e:
                    logger.warning(f"从本地路径加载语义嵌入模型 '{semantic_sentence_embedder}' 失败: {e}. 语义切分可能不可用。")
            elif hasattr(semantic_sentence_embedder, 'encode'):
                 self.semantic_sentence_embedder_model = semantic_sentence_embedder
                 logger.info("使用了预加载的 SBERT 模型实例。")
            elif isinstance(semantic_sentence_embedder, str): # 如果是字符串但不是有效路径，尝试按名称加载（可能联网）
                logger.warning(f"提供的 SBERT 路径 '{semantic_sentence_embedder}' 不存在，尝试按名称加载（可能联网）。")
                try:
                    self.semantic_sentence_embedder_model = SentenceTransformer(semantic_sentence_embedder)
                    logger.info(f"成功按名称加载语义切分嵌入模型: {semantic_sentence_embedder}")
                except Exception as e:
                    logger.warning(f"按名称加载语义嵌入模型 '{semantic_sentence_embedder}' 失败: {e}. 语义切分可能不可用。")
        elif not SentenceTransformer:
            logger.warning("SentenceTransformer 库未安装，语义切分功能不可用。")


        self.semantic_similarity_threshold = semantic_similarity_threshold
        self.semantic_min_chunk_sentences = semantic_min_chunk_sentences
        self.semantic_max_chunk_sentences = semantic_max_chunk_sentences

        # 初始化 PySBD 分割器
        self.sbd_segmenter = None
        self.sentence_segmenter_language = sentence_segmenter_language # 保存语言参数
        if pysbd:
            try:
                self.sbd_segmenter = pysbd.Segmenter(language=self.sentence_segmenter_language, clean=False)
                logger.info(f"PySBD ({self.sentence_segmenter_language}) 句子分割器初始化成功。")
            except Exception as e:
                logger.warning(f"PySBD ({self.sentence_segmenter_language}) 句子分割器初始化失败: {e}. 将无法使用 PySBD。")
        else:
            # 这个警告在文件顶部已经有了
            pass

    def get_token_count(self, text: str) -> int:
        if not self.tokenizer:
            return len(text)
        if self.tokenizer_type == 'tiktoken':
            return len(self.tokenizer.encode(text))
        elif self.tokenizer_type == 'hf':
            return len(self.tokenizer.encode(text, add_special_tokens=False))
        return len(text)

    def _segment_text_into_sentences(self, text: str) -> List[str]:
        """使用 PySBD (首选) 或 NLTK/正则后备方法将文本分割成句子列表。"""
        sentences = []
        # 1. 尝试 PySBD
        if self.sbd_segmenter:
            try:
                # logger.debug(f"使用 PySBD ({self.sbd_segmenter.language}) 进行句子切分...")
                sentences = self.sbd_segmenter.segment(text)
                # logger.debug(f"PySBD 切分出 {len(sentences)} 个句子。")
                if sentences: return sentences # 如果 PySBD 成功切分出内容，直接返回
            except Exception as e:
                logger.error(f"PySBD 句子切分失败: {e}")
        
        # 2. 如果 PySBD 失败或未切分出句子，尝试 NLTK (不指定语言)
        if not sentences and text.strip():
            if self.sbd_segmenter : # 仅当pysbd尝试过但失败时打印
                logger.warning("PySBD 未切分出任何句子，尝试 NLTK (不指定语言) 后备切分。")
            elif not pysbd:
                logger.warning("PySBD 未安装/初始化，尝试 NLTK (不指定语言) 切分。")

            try:
                sentences = nltk.sent_tokenize(text)
                if sentences: return sentences # 如果 NLTK 成功切分出内容，直接返回
            except Exception as nltk_e:
                logger.error(f"NLTK sent_tokenize (不指定语言) 失败: {nltk_e}")

        # 3. 如果 NLTK 也失败或未切分出句子，尝试正则表达式
        if not sentences and text.strip():
            logger.warning("NLTK (不指定语言) 也未切分出句子，尝试基于正则的最终后备切分。")
            sentence_parts = re.split(r'(?<=[。！？\n])\s*|\s*(?=\n)', text)
            current_sentence = ""
            for part in sentence_parts:
                if not part or part.isspace():
                    if current_sentence and '\n' in part and not part.strip():
                        if current_sentence.strip():
                            sentences.append(current_sentence.strip())
                        current_sentence = ""
                    continue
                current_sentence += part
                if any(current_sentence.endswith(p) for p in ['。','！','？']) or ('\n' in part and part.strip()):
                    if current_sentence.strip():
                        sentences.append(current_sentence.strip())
                    current_sentence = ""
            if current_sentence.strip():
                sentences.append(current_sentence.strip())
            if sentences: return sentences

        # 4. 如果所有方法都失败，将整个文本视为一个句子
        if not sentences and text.strip():
            logger.warning("所有句子切分方法均未成功，将整个文本视为一个句子。")
            sentences = [text.strip()]
        return sentences

    def _split_recursively(self, text: str) -> List[Dict[str, Any]]:
        docs = self.recursive_splitter.create_documents([text])
        chunks = []
        for doc in docs:
            chunks.append({
                "text": doc.page_content,
                "metadata": {**doc.metadata}
            })
        return chunks

    def _split_semantically(self, text: str) -> List[Dict[str, Any]]:
        if not self.semantic_sentence_embedder_model:
            logger.warning("语义嵌入模型未加载，语义切分回退到递归切分。")
            return self._split_recursively(text)

        sentences = self._segment_text_into_sentences(text)
        if not sentences or (len(sentences) == 1 and sentences[0] == text.strip()): # 如果无法有效分割成多个句子
            logger.warning("无法将文本有效分割成多个句子，语义切分回退到递归切分。")
            return self._split_recursively(text)

        sentence_embeddings = self.semantic_sentence_embedder_model.encode(sentences)
        chunks_data = []
        current_chunk_sentences = []
        text_offset = 0

        for i, sentence in enumerate(sentences):
            if not current_chunk_sentences:
                current_chunk_start_offset = text.find(sentence, text_offset)
                if current_chunk_start_offset == -1:
                    # 如果句子经过处理（例如strip），可能在原文中找不到完全匹配
                    # 可以尝试更宽松的查找或记录原始句子位置，但这里简化
                    current_chunk_start_offset = text_offset
                    logger.debug(f"句子 '{sentence[:20]}...' 在原文偏移 {text_offset} 后未直接找到，使用当前偏移。")


            current_chunk_sentences.append(sentence)
            split_here = False
            if len(current_chunk_sentences) >= self.semantic_min_chunk_sentences:
                if i == len(sentences) - 1:
                    split_here = True
                elif len(current_chunk_sentences) >= self.semantic_max_chunk_sentences:
                    split_here = True
                elif i + 1 < len(sentences):
                    try:
                        similarity = cosine_similarity(
                            sentence_embeddings[i].reshape(1, -1),
                            sentence_embeddings[i+1].reshape(1, -1)
                        )[0][0]
                        if similarity < self.semantic_similarity_threshold:
                            split_here = True
                    except Exception as e:
                        logger.error(f"计算句子相似度时出错: {e}")
                        if len(current_chunk_sentences) >= self.semantic_min_chunk_sentences:
                            split_here = True
            if split_here:
                chunk_text = " ".join(current_chunk_sentences)
                chunks_data.append({
                    "text": chunk_text,
                    "metadata": {"start_index": current_chunk_start_offset}
                })
                current_chunk_sentences = []
                if chunk_text: # 更新下一个可能的搜索起始位置
                    # 确保 text_offset 不会因为 join 后的空格而错位太多
                    # 理想情况下，应该基于原始句子的长度来推进 text_offset
                    text_offset = current_chunk_start_offset + sum(len(s) for s in current_chunk_sentences[:-1]) + len(current_chunk_sentences[-1]) if current_chunk_sentences else current_chunk_start_offset + len(chunk_text)


        if current_chunk_sentences: # 处理最后剩余的句子
            chunk_text = " ".join(current_chunk_sentences) # 先组合文本
            # 确定这个剩余块的起始位置
            if chunks_data: # 如果前面已经有块了
                # 使用上一个块的文本和元数据来估算下一个查找起点
                last_chunk_meta = chunks_data[-1]["metadata"]
                last_chunk_text_len = self.length_function(chunks_data[-1]["text"]) # 用实际长度函数
                # start_search_from 大约是上一个块的结束
                start_search_from = last_chunk_meta.get("start_index", 0) + last_chunk_text_len - self.chunk_overlap # 减去重叠部分尝试
                start_search_from = max(0, start_search_from) # 确保不为负
            else: #这是第一个也是唯一的块
                start_search_from = 0

            first_sentence_of_remainder = current_chunk_sentences[0]
            remainder_start_offset = text.find(first_sentence_of_remainder, start_search_from)
            if remainder_start_offset == -1: # 如果找不到，就用估算的开始位置
                remainder_start_offset = start_search_from
                logger.debug(f"剩余块首句 '{first_sentence_of_remainder[:20]}...' 在偏移 {start_search_from} 后未找到，使用估算偏移。")


            chunks_data.append({
                "text": chunk_text,
                "metadata": {"start_index": remainder_start_offset}
            })
        return chunks_data

    def _split_by_tokens(self, text: str) -> List[Dict[str, Any]]:
        if not self.tokenizer:
            logger.warning("Tokenizer 未初始化，Token 切分回退到递归字符切分。")
            return self._split_recursively(text)

        sentences = self._segment_text_into_sentences(text)
        if not sentences or (len(sentences) == 1 and sentences[0] == text.strip()):
            logger.warning("无法将文本有效分割成多个句子，Token 切分回退到递归字符切分。")
            return self._split_recursively(text)

        chunks_data = []
        current_chunk_sentences = []
        current_chunk_tokens = 0
        text_offset = 0 # 用于跟踪原始文本中的字符偏移

        for sentence_idx, sentence in enumerate(sentences):
            sentence_tokens = self.get_token_count(sentence)
            
            # 记录当前句子的原始起始位置 (如果这是新块的第一个句子)
            if not current_chunk_sentences:
                current_chunk_start_offset = text.find(sentence, text_offset)
                if current_chunk_start_offset == -1:
                    current_chunk_start_offset = text_offset # Fallback
                    logger.debug(f"句子(token) '{sentence[:20]}...' 在原文偏移 {text_offset} 后未直接找到，使用当前偏移。")


            # 如果当前句子加入后块大小未超限，或者这是块的第一个句子
            if current_chunk_tokens + sentence_tokens <= self.chunk_size or not current_chunk_sentences:
                current_chunk_sentences.append(sentence)
                current_chunk_tokens += sentence_tokens
            else:
                # 当前块已满，保存它
                chunk_text = " ".join(current_chunk_sentences)
                chunks_data.append({
                    "text": chunk_text,
                    "metadata": {"start_index": current_chunk_start_offset}
                })
                
                # 更新 text_offset 以准备下一个块的查找
                # 理想情况下，应该基于原始句子的长度
                # 这里简化为：假设上一个块的文本在原文中是连续的
                if chunk_text:
                    # 找到上一个块文本在原文的结束位置
                    # 这个假设可能不完美，因为 " ".join 会加入空格
                    # 但对于start_index的粗略定位是可接受的
                    text_offset = current_chunk_start_offset + len(chunk_text)


                # 开始新块
                current_chunk_start_offset = text.find(sentence, text_offset) # 为新块找到句子的起始
                if current_chunk_start_offset == -1:
                    current_chunk_start_offset = text_offset
                    logger.debug(f"新块句子(token) '{sentence[:20]}...' 在原文偏移 {text_offset} 后未直接找到，使用当前偏移。")

                current_chunk_sentences = [sentence]
                current_chunk_tokens = sentence_tokens
            
            # 在每个句子处理后更新 text_offset，使其指向当前句子之后的位置
            # 这样下一个句子的 find 操作会从正确的位置开始
            # 如果 text.find 找不到，说明句子被strip等处理过
            temp_offset = text.find(sentence, text_offset)
            if temp_offset != -1:
                text_offset = temp_offset + len(sentence)
            else: # 如果找不到，就假设它紧跟在上一个找到的位置之后
                 # 这在句子被normalize后可能发生
                text_offset += len(sentence)


        # 添加最后一个块
        if current_chunk_sentences:
            chunk_text = " ".join(current_chunk_sentences)
            # 为最后一个块确定 start_index
            # 如果 chunks_data 为空，说明这是唯一的块，start_index 应该是第一个句子的位置
            if not chunks_data:
                 # 这个current_chunk_start_offset应该是上面循环中最后一次设置的，代表这个块第一个句子的开始
                 final_chunk_start_offset_val = current_chunk_start_offset
            else: # 否则，从上一个块的结束位置估算
                last_chunk_meta = chunks_data[-1]["metadata"]
                last_chunk_text_len = self.length_function(chunks_data[-1]["text"])
                # 与语义切分类似地估算
                start_search_from = last_chunk_meta.get("start_index", 0) + last_chunk_text_len - self.chunk_overlap
                start_search_from = max(0, start_search_from)
                
                first_sentence_of_final_chunk = current_chunk_sentences[0]
                final_chunk_start_offset_val = text.find(first_sentence_of_final_chunk, start_search_from)
                if final_chunk_start_offset_val == -1:
                    final_chunk_start_offset_val = start_search_from # Fallback
                    logger.debug(f"最后块首句(token) '{first_sentence_of_final_chunk[:20]}...' 在偏移 {start_search_from} 后未找到，使用估算偏移。")


            chunks_data.append({
                "text": chunk_text,
                "metadata": {"start_index": final_chunk_start_offset_val}
            })
        return chunks_data


    def split_text(self, text: str, method: Optional[str] = None) -> List[Dict[str, Any]]:
        if not text.strip():
            return []
        current_method = (method or self.default_splitting_method).lower()
        if current_method == "recursive":
            return self._split_recursively(text)
        elif current_method == "semantic":
            return self._split_semantically(text)
        elif current_method == "token":
             return self._split_by_tokens(text)
        else:
            logger.warning(f"未知的切分方法: {current_method}. 回退到默认方法: {self.default_splitting_method}")
            return self.split_text(text, method=self.default_splitting_method)

    def split_documents(self, documents: List[Dict[str, Any]], content_key="content", metadata_key="metadata", method: Optional[str] = None) -> List[Dict[str, Any]]:
        all_chunks = []
        for doc_idx, doc in enumerate(documents):
            original_content = doc.get(content_key, "")
            original_metadata = doc.get(metadata_key, {}).copy()
            original_doc_id = original_metadata.get("id", original_metadata.get("doc_id", f"doc_{doc_idx}"))
            if not original_content.strip():
                continue
            chunks_for_doc = self.split_text(original_content, method=method)
            for chunk_idx, chunk_data in enumerate(chunks_for_doc):
                chunk_metadata = original_metadata.copy()
                chunk_metadata.update({
                    "original_doc_id": original_doc_id,
                    "chunk_index": chunk_idx,
                    "chunk_start_index_in_original": chunk_data["metadata"].get("start_index", -1)
                })
                chunk_metadata["chunk_id"] = f"{original_doc_id}_chunk_{chunk_idx}"
                all_chunks.append({
                    "text": chunk_data["text"],
                    "metadata": chunk_metadata
                })
        return all_chunks


# --- 示例用法 ---
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, # DEBUG可以看到更多切分过程日志
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger_main = logging.getLogger(__name__) # 主脚本的 logger
    logger_main.info("测试 AdvancedTextSplitter...")

    long_text_1 = """
人工智能（AI）正在以前所未有的速度改变世界。从自动驾驶汽车到智能助手，AI的应用无处不在。这是第一段。
深度学习是AI领域的一个重要分支，它依赖于大型神经网络和海量数据进行训练。自然语言处理（NLP）则致力于让计算机理解和生成人类语言，例如机器翻译和情感分析。这是第二段的主要内容。
AI的发展也带来了一些挑战，如数据隐私、算法偏见和就业结构变化。我们需要在推动技术进步的同时，关注其伦理和社会影响。第三段讨论了挑战。这是一个非常非常非常非常非常非常非常非常非常非常非常长的句子，用来测试切分能力，它应该被适当地切开。
"""
    long_text_2 = "太阳能是清洁能源。风能也是。水力发电历史悠久。地热能有潜力。"
    long_text_3_no_punctuation = "第一句话第二句话第三句话没有标点只有换行\n第四句话第五句话" # 测试正则对换行的处理
    long_text_4_mixed = "你好！世界。这是一个测试。\n换行了，还有吗？有的。" # 混合标点和换行
    long_text_5_short_no_split = "一整个句子不需要分割。"


    local_sbert_model_path = "./models/paraphrase-multilingual-MiniLM-L12-v2"

    # --- 测试 Recursive Character Splitting ---
    print("\n" + "="*10 + " 测试 Recursive Character Splitting " + "="*10)
    splitter_recursive = AdvancedTextSplitter(
        chunk_size=100,
        chunk_overlap=20,
        default_splitting_method="recursive",
        semantic_sentence_embedder=local_sbert_model_path
    )
    chunks_recursive = splitter_recursive.split_text(long_text_1)
    for i, chunk in enumerate(chunks_recursive):
        print(f"块 {i+1} (递归, 字符): (元数据: {chunk['metadata']})")
        print(f"  内容: '{chunk['text'][:80]}...'")


    # --- 测试 Semantic Splitting ---
    print("\n" + "="*10 + " 测试 Semantic Splitting " + "="*10)
    splitter_semantic = AdvancedTextSplitter(
        default_splitting_method="semantic",
        semantic_sentence_embedder=local_sbert_model_path,
        semantic_similarity_threshold=0.5, # 降低阈值看看效果
        semantic_min_chunk_sentences=1,
        semantic_max_chunk_sentences=2, #减少每个块的句子数
        sentence_segmenter_language="zh"
    )
    if splitter_semantic.sbd_segmenter:
         logger_main.info("PySBD for semantic splitter is initialized.")
    else:
         logger_main.warning("PySBD for semantic splitter FAILED to initialize or PySBD not installed.")

    test_texts_semantic = {
        "长文本1": long_text_1,
        "短文本2": long_text_2,
        "无标点换行文本3": long_text_3_no_punctuation,
        "混合标点换行文本4": long_text_4_mixed,
        "短句不分割文本5": long_text_5_short_no_split
    }
    for name, text_input in test_texts_semantic.items():
        print(f"\n--- 对 '{name}' 进行语义切分 ---")
        chunks_semantic = splitter_semantic.split_text(text_input)
        for i, chunk in enumerate(chunks_semantic):
            print(f"块 {i+1} (语义): (元数据: {chunk['metadata']})")
            print(f"  内容: '{chunk['text'][:100]}...'")
        if not chunks_semantic:
            print("没有切分出任何块。")


    # --- 测试 Token-based Splitting ---
    if tiktoken: # 仅当 tiktoken 可用时测试
        print("\n" + "="*10 + " 测试 Token-based Splitting " + "="*10)
        splitter_token = AdvancedTextSplitter(
            chunk_size=35, # 调整 token 数量
            chunk_overlap=5,
            length_function=lambda x: splitter_token.get_token_count(x),
            default_splitting_method="token",
            tokenizer_name_or_path="gpt-3.5-turbo",
            semantic_sentence_embedder=local_sbert_model_path, # 以防万一回退需要
            sentence_segmenter_language="zh"
        )
        # 确保其内部的 recursive_splitter (用于回退) 也使用 token 计数
        splitter_token.recursive_splitter = RecursiveCharacterTextSplitter(
            chunk_size=splitter_token.chunk_size,
            chunk_overlap=splitter_token.chunk_overlap,
            length_function=splitter_token.length_function,
            separators=splitter_token.recursive_separators,
            add_start_index=True
        )
        if splitter_token.sbd_segmenter:
             logger_main.info("PySBD for token splitter is initialized.")
        else:
             logger_main.warning("PySBD for token splitter FAILED to initialize or PySBD not installed.")

        test_texts_token = {
            "长文本1": long_text_1,
            "短文本2": long_text_2,
            "混合标点换行文本4": long_text_4_mixed,
            "短句不分割文本5": long_text_5_short_no_split
        }
        for name, text_input in test_texts_token.items():
            print(f"\n--- 对 '{name}' 进行 Token 切分 ---")
            chunks_token = splitter_token.split_text(text_input)
            for i, chunk in enumerate(chunks_token):
                token_count = splitter_token.get_token_count(chunk['text'])
                print(f"块 {i+1} (Token): (元数据: {chunk['metadata']}, Tokens: {token_count})")
                print(f"  内容: '{chunk['text'][:100]}...'")
            if not chunks_token:
                print("没有切分出任何块。")
    else:
        print("\n--- 跳过 Token-based Splitting (tiktoken 未安装或不可用) ---")


    # --- 测试切分文档列表 ---
    print("\n" + "="*10 + " 测试切分文档列表 (默认递归) " + "="*10)
    docs_to_split = [
        {"id": "docA", "content": long_text_1, "metadata": {"source": "report.pdf", "author": "AI Lab"}},
        {"id": "docB", "content": long_text_2, "metadata": {"source": "blog.html", "category": "Energy"}},
        {"id": "docC", "content": long_text_3_no_punctuation, "metadata": {"source": "note.txt"}}
    ]
    splitter_docs = AdvancedTextSplitter(
        chunk_size=120,
        chunk_overlap=15,
        default_splitting_method="recursive", # 显式指定，以免受其他实例化影响
        semantic_sentence_embedder=local_sbert_model_path, # 为可能的语义调用提供
        sentence_segmenter_language="zh"
        )
    all_doc_chunks = splitter_docs.split_documents(docs_to_split, content_key="content", metadata_key="metadata")

    print(f"从 {len(docs_to_split)} 个文档中总共切分出 {len(all_doc_chunks)} 个块。")
    for i, chunk in enumerate(all_doc_chunks[:5]):
        print(f"文档块 {i+1}:")
        print(f"  文本: '{chunk['text'][:60]}...'")
        print(f"  元数据: {chunk['metadata']}")
        print("-" * 10)
