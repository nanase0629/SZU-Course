import faiss
import numpy as np
 
# FAISS相关的全局变量
faiss_index = None
faiss_contents_map = {}  # original_id -> content
faiss_metadatas_map = {} # original_id -> metadata
faiss_id_order_for_index = [] # 保持ID顺序 