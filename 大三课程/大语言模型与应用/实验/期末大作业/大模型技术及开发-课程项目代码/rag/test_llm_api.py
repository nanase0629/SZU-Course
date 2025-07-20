import openai

# 配置你的API KEY和BASE URL
api_key = "sk-9aa6QfiEdvoXYLga_D2Q1w"
base_url = "https://llmapi.blsc.cn/v1"
model = "DeepSeek-V3-250324-P001"  # 或 "DeepSeek-R1" 等你有权限的模型

client = openai.OpenAI(api_key=api_key, base_url=base_url)

prompt = "请用一句话介绍一下你自己。"

try:
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=512,
        stream=False
    )
    print("【大模型生成的答案】\n", response.choices[0].message.content)
except Exception as e:
    print("OpenAI API调用失败:", e)