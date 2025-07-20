import os
import re
import openai
from typing import List, Dict, Any, Optional, Union, Callable
# 配置你的API KEY和BASE URL
api_key = "sk-9aa6QfiEdvoXYLga_D2Q1w"
base_url = "https://llmapi.blsc.cn/v1"
model = ""  # 或 "DeepSeek-R1" 等你有权限的模型

client = openai.OpenAI(api_key=api_key, base_url=base_url)
# --- 配置 ---
# 尝试从环境变量读取 API 密钥
# 或者你也可以直接在这里设置: OPENAI_API_KEY = "sk-your_api_key_here"
OPENAI_API_KEY = "sk-9aa6QfiEdvoXYLga_D2Q1w"
if not OPENAI_API_KEY:
    raise ValueError("请设置 OPENAI_API_KEY 环境变量或在代码中直接指定。")

DEFAULT_MODEL = "DeepSeek-V3-250324-P001"


class LLMQueryRewriter:
    def __init__(self, api_key: str = "sk-9aa6QfiEdvoXYLga_D2Q1w", model: str = "DeepSeek-V3-250324-P001"):
        self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    def _call_llm(self, prompt: str, system_message: str = None, temperature: float = 0.7, max_tokens: int = 150) -> str:
        """
        调用 LLM API 并获取响应。
        """
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                n=1, # Number of chat completion choices to generate for each input message.
                stop=None, # Up to 4 sequences where the API will stop generating further tokens.
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"调用 LLM API 时出错: {e}")
            return ""

    def _clean_list_output(self, text_output: str) -> list[str]:
        """清理 LLM 返回的列表式文本输出。"""
        items = []
        # 尝试按换行符分割，并去除数字/项目符号和空白
        for line in text_output.splitlines():
            # 去除常见的列表标记，如 "1. ", "- ", "* "
            cleaned_line = re.sub(r"^\s*[\d\.\-\*]+\s*", "", line).strip()
            if cleaned_line:
                items.append(cleaned_line)
        return items if items else [text_output.strip()] # 如果没有解析出列表，则返回整个文本


    def rewrite_query2doc_style(self, original_query: str, num_keywords: int = 5) -> str:
        """
        Query2doc 风格：生成伪文档并提取关键词进行扩展。
        返回: 原始查询 + 提取的关键词 (字符串形式)
        """
        print(f"\n--- Query2doc 风格重写 ---")
        print(f"原始查询: {original_query}")

        # 1. 生成伪文档
        pseudo_doc_prompt = (
            f"针对以下用户查询，请生成一段简短的、高度相关的“理想文档”片段（大约50-100字），"
            f"这段文字应该像是能完美回答用户查询的内容。\n\n用户查询：'{original_query}'"
        )
        system_message_doc = "你是一个有用的助手，擅长根据用户查询生成相关的文档片段。"
        pseudo_document = self._call_llm(pseudo_doc_prompt, system_message=system_message_doc, max_tokens=150)
        print(f"生成的伪文档: {pseudo_document}")

        if not pseudo_document:
            return original_query # 如果伪文档生成失败，返回原始查询

        # 2. 从伪文档中提取关键词
        keyword_extraction_prompt = (
            f"从以下文本中提取最重要的 {num_keywords} 个关键词或短语，用于查询扩展。请每行返回一个关键词/短语。\n\n"
            f"文本：\n'''\n{pseudo_document}\n'''\n\n"
            f"提取的关键词/短语："
        )
        system_message_kw = "你是一个有用的助手，擅长从文本中提取核心关键词和短语。"
        keywords_text = self._call_llm(keyword_extraction_prompt, system_message=system_message_kw, max_tokens=50 * num_keywords)
        extracted_keywords = self._clean_list_output(keywords_text)
        print(f"提取的关键词: {extracted_keywords}")

        if extracted_keywords:
            # 可以选择不同的组合方式，这里简单地将关键词追加到原始查询后
            expanded_query = f"{original_query} {' '.join(extracted_keywords)}"
            return expanded_query
        return original_query

    def rewrite_paraphrase(self, original_query: str, num_paraphrases: int = 3) -> list[str]:
        """
        语义等价改写/释义。
        返回: 多个释义后的查询列表
        """
        print(f"\n--- 语义等价改写 ---")
        print(f"原始查询: {original_query}")

        paraphrase_prompt = (
            f"请将以下查询改写成 {num_paraphrases} 种不同的、但意思基本相同的说法。请每行返回一个改写后的查询。\n\n"
            f"原始查询：'{original_query}'\n\n"
            f"改写后的查询："
        )
        system_message = "你是一个有用的助手，擅长对文本进行释义和改写。"
        paraphrased_text = self._call_llm(paraphrase_prompt, system_message=system_message, max_tokens=50 * num_paraphrases)
        paraphrased_queries = self._clean_list_output(paraphrased_text)
        print(f"释义后的查询: {paraphrased_queries}")
        return [original_query] + paraphrased_queries # 包含原始查询

    def rewrite_intent_refinement(self, original_query: str, num_subqueries: int = 3) -> list[str]:
        """
        意图细化与子问题分解。
        返回: 多个细化后的子查询列表
        """
        print(f"\n--- 意图细化/子问题分解 ---")
        print(f"原始查询: {original_query}")

        subquery_prompt = (
            f"用户输入了查询：'{original_query}'。\n"
            f"这个查询可能比较宽泛。请分析用户可能的具体意图，并列出 {num_subqueries} 个更具体、可操作的子查询或相关问题。"
            f"请每行返回一个子查询/问题。\n\n"
            f"具体的子查询/问题："
        )
        system_message = "你是一个有用的助手，擅长分析用户查询意图并将其分解为更具体的问题。"
        subqueries_text = self._call_llm(subquery_prompt, system_message=system_message, max_tokens=50 * num_subqueries)
        refined_queries = self._clean_list_output(subqueries_text)
        print(f"细化后的子查询: {refined_queries}")
        return [original_query] + refined_queries # 包含原始查询

    def rewrite_concept_expansion(self, original_query: str, num_concepts: int = 5) -> str:
        """
        概念扩展与相关实体联想。
        返回: 原始查询 + 扩展的概念/实体 (字符串形式)
        """
        print(f"\n--- 概念扩展与相关实体联想 ---")
        print(f"原始查询: {original_query}")

        expansion_prompt = (
            f"用户的查询是：'{original_query}'。\n"
            f"请识别此查询中的核心概念或实体，并联想出 {num_concepts} 个与之高度相关的其他重要术语、概念或实体，"
            f"用于扩展查询。请每行返回一个术语/概念/实体。\n\n"
            f"相关的术语/概念/实体："
        )
        system_message = "你是一个知识渊博的助手，擅长识别概念并联想相关实体。"
        concepts_text = self._call_llm(expansion_prompt, system_message=system_message, max_tokens=30 * num_concepts)
        expanded_concepts = self._clean_list_output(concepts_text)
        print(f"扩展的概念/实体: {expanded_concepts}")

        if expanded_concepts:
            expanded_query = f"{original_query} {' '.join(expanded_concepts)}"
            return expanded_query
        return original_query


    def recognize_initial_intent(self, original_query: str) -> Dict[str, str]:
        """
        识别用户初始查询的主要意图。
        返回: 一个包含 'category' 和 'description' 的字典。
        """
        print(f"\n--- 初始意图识别 ---")
        print(f"原始查询: {original_query}")

        intent_categories = [
            "寻求信息/事实 (Fact-seeking)",
            "寻求定义 (Definition-seeking)",
            "寻求解释/原因 (Explanation/Reason-seeking)",
            "寻求方法/步骤 (How-to/Procedural)",
            "寻求比较 (Comparison)",
            "寻求观点/评论 (Opinion/Review-seeking)",
            # "导航/定位 (Navigational)", # 根据你的应用场景决定是否需要
            # "事务性 (Transactional)",
            # "对话式/闲聊 (Conversational/Chit-chat)"
        ]
        intent_prompt = (
            f"用户查询是：'{original_query}'\n\n"
            f"请分析此查询的主要意图。从以下意图类别中选择最合适的一个。如果以下类别都不完全符合，请简要描述一个新的意图类别。\n"
            f"备选类别：\n" + "\n".join([f"- {cat}" for cat in intent_categories]) + "\n\n"
            f"主要意图类别：[请在此填写，尽量从备选类别中选择]\n"
            f"对意图的简要描述（可选，如果类别不明确或需要补充）：[请在此填写]"
        )
        system_message = "你是一个专业的查询意图分析助手。"
        # 调整 max_tokens 以适应可能的描述
        intent_output = self._call_llm(intent_prompt, system_message=system_message, temperature=0.3, max_tokens=100)
        print(f"LLM对意图的分析结果: {intent_output}")

        # 解析 LLM 的输出 (这是一个简化的解析，实际可能需要更复杂的逻辑)
        intent_category = "未知"
        intent_description = intent_output # 默认描述是整个输出
        
        # 尝试从输出中提取 "主要意图类别：" 后面的内容
        category_match = re.search(r"主要意图类别：\s*\[?([^\]\n]+)\]?", intent_output, re.IGNORECASE)
        if category_match:
            intent_category = category_match.group(1).strip()
            # 尝试去除描述中已包含的类别部分
            intent_description = re.sub(r"主要意图类别：\s*\[?[^\]\n]+\]?\s*", "", intent_output, flags=re.IGNORECASE).strip()
            desc_match = re.search(r"对意图的简要描述（可选，如果类别不明确或需要补充）：\s*\[?([^\]\n]+)\]?", intent_description, re.IGNORECASE)
            if desc_match:
                intent_description = desc_match.group(1).strip()
            elif not intent_description.startswith("对意图的简要描述"): # 如果没有明确的描述标签，但有剩余文本
                 pass # intent_description 已经是剩余文本了
            else: # 如果只有类别，描述为空
                intent_description = ""


        # 进一步标准化意图类别 (可选)
        # 例如，如果LLM返回 "寻求定义"，我们希望是 "Definition-seeking"
        normalized_category = intent_category # 默认
        for cat_option in intent_categories:
            if intent_category in cat_option or cat_option in intent_category: # 简单匹配
                normalized_category = cat_option # 或者只取英文部分 cat_option.split('(')[1][:-1]
                break
        
        result = {"category": normalized_category, "description": intent_description}
        print(f"识别到的意图: {result}")
        return result

    def analyze_clarification_intent(self, initial_query: str, previous_query: str, retrieved_summary: str, new_query_from_llm: str) -> str:
        """
        分析LLM生成的新查询相对于原始问题的澄清意图或子意图。
        返回: 对新查询意图的描述字符串。
        """
        print(f"\n--- 澄清意图分析 ---")
        analysis_prompt = (
            f"原始问题是：'{initial_query}'\n"
            f"之前探索的查询是：'{previous_query}'\n"
            f"已检索到的信息摘要如下：\n'''\n{retrieved_summary}\n'''\n"
            f"基于此，LLM 提出的新查询是：'{new_query_from_llm}'\n\n"
            f"请分析这个新查询 '{new_query_from_llm}' 相对于原始问题 '{initial_query}' 而言，它主要想澄清或探索原始问题的哪个具体方面或子意图？"
            f"例如，它是想了解更具体的细节、不同的方面、原因、解决方案、同义词替换、还是其他什么？请用一两句话清晰描述。"
        )
        system_message = "你是一个深入理解对话和查询演进的分析助手。"
        clarification_description = self._call_llm(analysis_prompt, system_message=system_message, temperature=0.5, max_tokens=150)
        print(f"LLM对新查询 '{new_query_from_llm}' 的澄清意图分析: {clarification_description}")
        return clarification_description.strip()


# --- 主程序示例 ---
if __name__ == "__main__":
    if not OPENAI_API_KEY:
        print("错误：OPENAI_API_KEY 未设置。请在代码顶部或环境变量中设置它。")
    else:
        rewriter = LLMQueryRewriter()

        queries_to_test = [
            "AI 发展趋势",
            "如何缓解工作压力",
            "学习编程",
            "特斯拉自动驾驶",
            "上海 美食 推荐"
        ]

        for query in queries_to_test:
            print(f"\n========================================")
            print(f"测试原始查询: '{query}'")
            print(f"========================================")

            # 1. Query2doc 风格
            q2d_rewritten = rewriter.rewrite_query2doc_style(query, num_keywords=4)
            print(f"Query2doc 重写结果: {q2d_rewritten}")

            # 2. 语义等价改写
            paraphrased_results = rewriter.rewrite_paraphrase(query, num_paraphrases=2)
            print(f"语义等价改写结果: {paraphrased_results}")

            # 3. 意图细化
            refined_results = rewriter.rewrite_intent_refinement(query, num_subqueries=2)
            print(f"意图细化结果: {refined_results}")

            # 4. 概念扩展
            concept_expanded_result = rewriter.rewrite_concept_expansion(query, num_concepts=3)
            print(f"概念扩展结果: {concept_expanded_result}")

            print("\n")
