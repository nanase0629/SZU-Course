from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    local_dir="./models/paraphrase-multilingual-MiniLM-L12-v2",
    local_dir_use_symlinks=False  # 可选：不使用符号链接，方便移动和部署
)
