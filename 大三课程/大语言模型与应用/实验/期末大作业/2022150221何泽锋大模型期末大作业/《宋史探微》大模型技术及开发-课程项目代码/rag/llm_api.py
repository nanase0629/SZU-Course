import requests
import json
import logging
from config import SILICONFLOW_API_KEY, SILICONFLOW_API_URL, LLM_PROVIDER, OPENAI_API_KEY, OPENAI_API_BASE, OPENAI_MODEL

def call_siliconflow_api(prompt, temperature=0.7, max_tokens=1024, model=None):
    if not SILICONFLOW_API_KEY:
        logging.error("未设置 SILICONFLOW_API_KEY 环境变量。请在config.py中设置您的 API 密钥。")
        return "错误：未配置 SiliconFlow API 密钥。", ""
    if model is None:
        model = "Pro/deepseek-ai/DeepSeek-R1"
    try:
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "stream": False,
            "max_tokens": max_tokens,
            "stop": None,
            "temperature": temperature,
            "top_p": 0.7,
            "top_k": 50,
            "frequency_penalty": 0.5,
            "n": 1,
            "response_format": {"type": "text"}
        }
        headers = {
            "Authorization": f"Bearer {SILICONFLOW_API_KEY}",
            "Content-Type": "application/json; charset=utf-8"
        }
        json_payload = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        response = requests.post(
            SILICONFLOW_API_URL,
            data=json_payload,
            headers=headers,
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        if "choices" in result and len(result["choices"]) > 0:
            message = result["choices"][0]["message"]
            content = message.get("content", "")
            reasoning = message.get("reasoning_content", "")
            if reasoning:
                full_response = f"{content}<think>{reasoning}</think>"
                return full_response
            else:
                return content
        else:
            return "API返回结果格式异常，请检查"
    except requests.exceptions.RequestException as e:
        logging.error(f"调用SiliconFlow API时出错: {str(e)}")
        return f"调用API时出错: {str(e)}"
    except json.JSONDecodeError:
        logging.error("SiliconFlow API返回非JSON响应")
        return "API响应解析失败"
    except Exception as e:
        logging.error(f"调用SiliconFlow API时发生未知错误: {str(e)}")
        return f"发生未知错误: {str(e)}"

# 新版openai>=1.0.0兼容API调用
def call_openai_api(prompt, temperature=0.7, max_tokens=1536, model=None):
    import openai
    openai.api_key = OPENAI_API_KEY
    openai.base_url = OPENAI_API_BASE
    if model is None:
        model = OPENAI_MODEL
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE)
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"OpenAI API调用失败: {str(e)}"

# 统一大模型调用入口
def call_llm_api(prompt, temperature=0.7, max_tokens=1536, model=None):
    if LLM_PROVIDER == "openai":
        return call_openai_api(prompt, temperature, max_tokens, model)
    elif LLM_PROVIDER == "siliconflow":
        return call_siliconflow_api(prompt, temperature, max_tokens, model)
    elif LLM_PROVIDER == "ollama":
        # 这里假设有session和本地Ollama服务
        import json as _json
        import requests as _requests
        try:
            payload = {
                "model": model or "deepseek-r1:7b",
                "prompt": prompt,
                "stream": False
            }
            response = _requests.post(
                "http://localhost:11434/api/generate",
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "未获取到有效回答")
        except Exception as e:
            return f"Ollama本地API调用失败: {str(e)}"
    else:
        return "不支持的大模型提供方类型，请检查LLM_PROVIDER参数设置。" 