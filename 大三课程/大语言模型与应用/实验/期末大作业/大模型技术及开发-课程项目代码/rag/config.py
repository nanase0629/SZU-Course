import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# Hugging Face 镜像
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['NO_PROXY'] = 'localhost,127.0.0.1'

# API密钥和配置
SERPAPI_KEY = "7447324e67d85b420e219874579b139e7e512bcd52ab2ef86c02f7e3b6aabbe8"  # 你的SERPAPI_KEY
SEARCH_ENGINE = "google"
RERANK_METHOD = "cross_encoder"
SILICONFLOW_API_KEY = ""  # 你的硅基流动API密钥
SILICONFLOW_API_URL = "https://api.siliconflow.cn/v1/chat/completions"

# OpenAI兼容API参数
OPENAI_API_KEY = "sk-9aa6QfiEdvoXYLga_D2Q1w"
OPENAI_API_BASE = "https://llmapi.blsc.cn/v1"
OPENAI_MODEL = "DeepSeek-V3-250324-P001"

# 统一大模型类型选择
LLM_PROVIDER = "openai"  # 可选: "openai", "siliconflow", "ollama"

# 端口配置
DEFAULT_PORTS = [17995, 17996, 17997, 17998, 17999]

# 嵌入模型名
EMBED_MODEL_NAME = './models/bge-large-zh-v1.5'  # 示例：本地模型路径
# 交叉编码器模型名
CROSS_ENCODER_MODEL_NAME = './models/bge-reranker-large'

# ====== RAG系统自定义参数 ======
# 分块参数
CHUNK_SIZE = 400
CHUNK_OVERLAP = 40
CHUNK_SEPARATORS = ["\n\n", "\n", "。", "，", "；", "：", " ", ""]

# 检索参数
MAX_ITERATIONS = 2  # 递归检索最大轮数
top_k_faiss = 10    # 向量检索top_k
top_k_bm25 = 10     # BM25检索top_k
TOP_K_RERANK = 5    # 重排序后top_k
ALPHA_HYBRID = 0.7  # 混合权重

# 大模型生成参数
LLM_MODEL = "Pro/deepseek-ai/DeepSeek-R1"
LLM_TEMPERATURE = 0.7
LLM_MAX_TOKENS = 1536 