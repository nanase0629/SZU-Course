from sentence_transformers import SentenceTransformer, CrossEncoder
import threading
import logging
import requests
from config import EMBED_MODEL_NAME, CROSS_ENCODER_MODEL_NAME

# 嵌入模型
EMBED_MODEL = SentenceTransformer(EMBED_MODEL_NAME)

# 交叉编码器延迟加载
cross_encoder = None
cross_encoder_lock = threading.Lock()

def get_cross_encoder():
    global cross_encoder
    if cross_encoder is None:
        with cross_encoder_lock:
            if cross_encoder is None:
                try:
                    cross_encoder = CrossEncoder(CROSS_ENCODER_MODEL_NAME)
                    logging.info("交叉编码器加载成功")
                except Exception as e:
                    logging.error(f"加载交叉编码器失败: {str(e)}")
                    cross_encoder = None
    return cross_encoder

# LLM会话
session = requests.Session() 