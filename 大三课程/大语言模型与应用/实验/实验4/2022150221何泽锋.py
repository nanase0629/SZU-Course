import openai
import os

# 从DEEPSEEK, CHATGLM, QWEN, SILICONFLOW, PISCES中选一个
PLATFORM = "CHATGLM"
API_KEY = "791aaf0f5f1db5135b0f687efb435e82.sHh5JdSP8dlvtNwh"  # 你申请的API Key

if PLATFORM == "DEEPSEEK":
    global_model = "deepseek-chat"
    base_url = "https://api.deepseek.com/v1/"
elif PLATFORM == "CHATGLM":
    global_model = "GLM-4-Flash-250414"
    base_url = "https://open.bigmodel.cn/api/paas/v4/"
elif PLATFORM == "QWEN":
    global_model = "qwen-plus"
    base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1/"
elif PLATFORM == "SILICONFLOW":
    global_model = "deepseek-ai/DeepSeek-V3"
    base_url = "https://api.siliconflow.cn/v1/"
else:
    global_model = "chatgpt-4o-latest"
    base_url = "https://api.pisces.ink/v1/"

client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY", API_KEY),
    base_url=base_url,
)


# 用于单轮对话
def get_completion(prompt, model=global_model, temperature=0):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,  # 控制模型输出的随机程度
        )
        return response.choices[0].message.content
    except Exception as e:
        # print(f"API 调用出错: {e}")
        return f"API Error: {e}"


# 用于多轮对话
def get_completion_from_messages(messages, model=global_model, temperature=0):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature  # 控制模型输出的随机程度
        )
        return response.choices[0].message.content
    except Exception as e:
        # print(f"API 调用出错: {e}")
        return f"API Error: {e}"


if __name__ == "__main__":
    text = f"""
    您应该提供尽可能清晰、具体的指示，以表达您希望模型执行的任务。\
    这将引导模型朝向所需的输出，并降低收到无关或不正确响应的可能性。\
    不要将写清晰的提示词与写简短的提示词混淆。\
    在许多情况下，更长的提示词可以为模型提供更多的清晰度和上下文信息，从而导致更详细和相关的输出。
    """
    prompt = f"""
    把用三个反引号括起来的文本总结成一句话。
    ```{text}```
    """
    response = get_completion(prompt)
    print("练习 1.1 输出:")
    print(response)

    prompt = f"""
    请生成包括书名、作者和类别的三本虚构的、非真实存在的中文书籍清单，\
    并以 JSON 格式提供，其中包含以下键: book_id、title、author、genre。
    """
    response = get_completion(prompt)
    print("\n练习 1.2 输出:")
    print(response)

    # 包含指令的文本
    text_1 = f"""
    泡一杯茶很容易。首先，需要把水烧开。\
    在等待期间，拿一个杯子并把茶包放进去。\
    一旦水足够热，就把它倒在茶包上。\
    等待一会儿，让茶叶浸泡。几分钟后，取出茶包。\
    如果您愿意，可以加一些糖或牛奶调味。\
    就这样，您可以享受一杯美味的茶了。
    """
    prompt_1 = f"""
    您将获得由三个引号括起来的文本。\
    如果它包含一系列的指令，则需要按照以下格式重新编写这些指令：
    
    第一步 - ...
    第二步 - …
    …
    第N步 - …
    
    如果文本中不包含一系列的指令，则直接写“未提供步骤”。"
    \"\"\"{text_1}\"\"\"
    """
    response_1 = get_completion(prompt_1)
    print("\n练习 1.3 (Text 1) 输出:")
    print(response_1)

    # 不包含指令的文本
    text_2 = f"""
    今天阳光明媚，鸟儿在歌唱。\
    这是一个去公园散步的美好日子。\
    鲜花盛开，树枝在微风中轻轻摇曳。\
    人们外出享受着这美好的天气，有些人在野餐，有些人在玩游戏或者在草地上放松。\
    这是一个完美的日子，可以在户外度过并欣赏大自然的美景。
    """
    prompt_2 = f"""
    您将获得由三个引号括起来的文本。\
    如果它包含一系列的指令，则需要按照以下格式重新编写这些指令：
    
    第一步 - ...
    第二步 - …
    …
    第N步 - …
    
    如果文本中不包含一系列的指令，则直接写“未提供步骤”。"
    \"\"\"{text_2}\"\"\"
    """
    response_2 = get_completion(prompt_2)
    print("\n练习 1.3 (Text 2) 输出:")
    print(response_2)

    prompt = f"""您的任务是以一致的风格回答问题。
    <孩子>: 请教我何为耐心。
    <祖父母>: 挖出最深峡谷的河流源于一处不起眼的泉眼；最宏伟的交响乐从单一的音符开始；最复杂的挂毯以一根孤独的线开始编织。
    <孩子>: 请教我何为韧性。"""
    response = get_completion(prompt)
    print("\n练习 1.4 输出:")
    print(response)

    prompt = f"""
    请判断学生的解决方案是否正确，请通过如下步骤解决这个问题：

    步骤：

        首先，自己解决问题。
        然后将您的解决方案与学生的解决方案进行比较，对比计算得到的总费用与学生计算的总费用是否一致，并评估学生的解决方案是否正确。
        在自己完成问题之前，请勿决定学生的解决方案是否正确。

    使用以下格式：

        问题：问题文本
        学生的解决方案：学生的解决方案文本
        实际解决方案和步骤：实际解决方案和步骤文本
        学生计算的总费用：学生计算得到的总费用
        实际计算的总费用：实际计算出的总费用
        学生计算的费用和实际计算的费用是否相同：是或否
        学生的解决方案和实际解决方案是否相同：是或否
        学生的成绩：正确或不正确

    问题：

        我正在建造一个太阳能发电站，需要帮助计算财务。 
        - 土地费用为每平方英尺100美元
        - 我可以以每平方英尺250美元的价格购买太阳能电池板
        - 我已经谈判好了维护合同，每年需要支付固定的10万美元，并额外支付每平方英尺10美元;

        作为平方英尺数的函数，首年运营的总费用是多少。

    学生的解决方案：

        设x为发电站的大小，单位为平方英尺。
        费用：
        1. 土地费用：100x美元
        2. 太阳能电池板费用：250x美元
        3. 维护费用：100,000+100x=10万美元+10x美元
        总费用：100x美元+250x美元+10万美元+100x美元=450x+10万美元

    实际解决方案和步骤：
    """
    response = get_completion(prompt)
    print("\n练习 1.5 输出:")
    print(response)

    prod_review = """
    这个熊猫公仔是我给女儿的生日礼物，她很喜欢，去哪都带着。
    公仔很软，超级可爱，面部表情也很和善。但是相比于价钱来说，
    它有点小，我感觉在别的地方用同样的价钱能买到更大的。
    快递比预期提前了一天到货，所以在送给女儿之前，我自己玩了会。
    """
    prompt = f"""
    您的任务是从电子商务网站上生成一个产品评论的简短摘要。
    请对三个反引号之间的评论文本进行概括，最多30个字。
    评论: ```{prod_review}```
    """
    response = get_completion(prompt)
    print("\n练习 2.1 输出:")
    print(response)

    prompt = f"""
    您的任务是从电子商务网站上生成一个产品评论的简短摘要。
    请对三个反引号之间的评论文本进行概括，最多30个字，并且侧重在快递服务上。
    评论: ```{prod_review}```
    """
    response = get_completion(prompt)
    print("\n练习 2.2 输出:")
    print(response)

    prompt = f"""
    您的任务是从电子商务网站上的产品评论中提取相关信息。
    请从以下三个反引号之间的评论文本中提取产品运输相关的信息，最多30个词汇。
    评论: ```{prod_review}```
    """
    response = get_completion(prompt)
    print("\n练习 2.3 输出:")
    print(response)

    lamp_review = """
    我需要一盏漂亮的卧室灯，这款灯具有额外的储物功能，价格也不算太高。\
    我很快就收到了它。在运输过程中，我们的灯绳断了，但是公司很乐意寄送了一个新的。\
    几天后就收到了。这款灯很容易组装。我发现少了一个零件，于是联系了他们的客服，他们很快就给我寄来了缺失的零件！\
    在我看来，Lumina 是一家非常关心顾客和产品的优秀公司！
    """
    prompt = f"""
    以下用三个反引号分隔的产品评论的情感是什么？
    用一个单词回答：「正面」或「负面」。
    评论文本: ```{lamp_review}```
    """
    response = get_completion(prompt)
    print("\n练习 3.1 输出:")
    print(response)

    prompt = f"""
    识别以下评论的作者表达的情感。包含不超过五个项目。将答案格式化为以逗号分隔的单词列表。
    评论文本: ```{lamp_review}```
    """
    response = get_completion(prompt)
    print("\n练习 3.2 输出:")
    print(response)

    prompt = f"""
    从评论文本中识别以下项目：
    - 评论者购买的物品
    - 制造该物品的公司

    评论文本用三个反引号分隔。将你的响应格式化为以 “物品” 和 “品牌” 为键的 JSON 对象。
    如果信息不存在，请使用 “未知” 作为值。
    让你的回应尽可能简短。

    评论文本: ```{lamp_review}```
    """
    response = get_completion(prompt)
    print("\n练习 3.3 输出:")
    print(response)

    prompt = f"""
    将以下中文翻译成西班牙语: \
    ```您好，我想订购一个搅拌机。```
    """
    response = get_completion(prompt)
    print("\n练习 4.1 输出:")
    print(response)

    prompt = f"""将以下文本翻译成商务信函的格式:
    ```小老弟，我小羊，上回你说咱部门要采购的显示器是多少寸来着？```"""
    response = get_completion(prompt)
    print("\n练习 4.2 输出:")
    print(response)

    data_json = {"resturant employees": [
        {"name": "Shyam", "email": "shyamjaiswal@gmail.com"},
        {"name": "Bob", "email": "bob32@gmail.com"},
        {"name": "Jai", "email": "jai87@gmail.com"}
    ]}

    prompt = f"""将以下Python字典从JSON转换为HTML表格，保留表格标题和列名：{data_json}"""
    response = get_completion(prompt)
    print("\n练习 4.3 输出:")
    print(response)

    text = "This phrase is to cherck chatGPT for spelling abilitty"
    prompt = f"""请校对并更正以下文本，注意纠正文本保持原始语种，无需输出原始文本。
        如果您没有发现任何错误，请说“未发现错误”。
        ```{text}```"""
    response = get_completion(prompt)
    print("\n练习 4.4 输出:")
    print(response)

    sentiment = "消极的"
    review = f"""
    他们在11月份的季节性销售期间以约49美元的价格出售17件套装，折扣约为一半。\
    但由于某些原因（可能是价格欺诈），到了12月第二周，同样的套装价格全都涨到了70美元到89美元不等。\
    11件套装的价格也上涨了大约10美元左右。\
    虽然外观看起来还可以，但基座上锁定刀片的部分看起来不如几年前的早期版本那么好。\
    不过我打算非常温柔地使用它...（省略部分细节）...大约一年后，电机发出奇怪的噪音，我打电话给客服，但保修已经过期了，所以我不得不再买一个。\
    总的来说，这些产品的总体质量已经下降，因此它们依靠品牌认可和消费者忠诚度来维持销售。\
    货物在两天内到达。
    """

    prompt = f"""
    你是一位客户服务的AI助手。
    你的任务是给一位重要客户发送邮件回复。
    根据客户通过“```”分隔的评价，生成回复以感谢客户的评价。提醒模型使用评价中的具体细节
    用简明而专业的语气写信。
    作为“AI客户代理”签署电子邮件。
    客户评论：
    ```{review}```
    评论情感：{sentiment}
    """
    response = get_completion(prompt, temperature=0)  # 使用 temperature=0 保证结果一致性
    print("\n练习 5.1 输出:")
    print(response)

    print("\n练习 5.2 输出 (第一次, T=0.7):")
    response1 = get_completion(prompt, temperature=0.7)
    print(response1)
    print("\n练习 5.2 输出 (第二次, T=0.7):")
    import time

    time.sleep(20)  # 等待20秒，避免可能的频率限制
    response2 = get_completion(prompt, temperature=0.7)
    print(response2)

    prompt_direct = """
    一个水果摊有 20 个苹果，卖掉了 5 个，又新进了 15 个。现在水果摊有多少个苹果？请直接给出最终数量。
    """
    response_direct = get_completion(prompt_direct)
    print("\n练习 6.1 输出 (直接提问):")
    print(response_direct)

    prompt_cot = """
    一个水果摊有 20 个苹果，卖掉了 5 个，又新进了 15 个。现在水果摊有多少个苹果？让我们一步一步地思考。
    """
    response_cot = get_completion(prompt_cot)
    print("\n练习 6.1 输出 (使用 CoT):")
    print(response_cot)

    story_text = """
    在阳光明媚的周六下午，张伟和他的朋友李娜决定去参观位于市中心的科技博物馆。他们在博物馆里看到了许多有趣的展品，特别是关于人工智能和未来交通的部分。参观结束后，他们在附近的公园散步，讨论着刚才看到的展品。
    """

    import json

    #  步骤 1
    prompt_step1 = f"""
    从以下文本中提取所有的人物姓名和地点名称。
    将结果格式化为一个 Python 列表，其中每个元素是一个包含 'type' (人物/地点) 和 'name' (名称) 的字典。

    只返回Python类型的字典，无需返回任何其他内容！
    文本：```{story_text}```
    """
    response_step1_str = get_completion(prompt_step1)
    print("\n练习 6.2 输出 (步骤 1 - 提取信息):")
    print(response_step1_str)


    def extract_python_code_blocks(text):
        """
        从文本中提取所有被 ```python 和 ``` 包围的代码块
        :param text: 输入文本
        :return: 匹配到的代码块列表
        """
        import re
        pattern = r'```python(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)
        # 去除每个匹配结果两端的空白字符
        return [match.strip() for match in matches]


    def parse_entities(response_step1_str):
        """
        解析实体列表，兼容字符串形式的Python列表或直接是Python列表
        :param response_step1_str: 可能是字符串形式的Python列表或直接是列表
        :return: 解析后的实体列表
        """
        if isinstance(response_step1_str, list):
            # 如果已经是列表，直接返回
            return response_step1_str

        try:
            # 先尝试用json解析（更安全）
            return json.loads(response_step1_str)
        except json.JSONDecodeError:
            try:
                return extract_python_code_blocks(response_step1_str)
            except (ValueError, SyntaxError) as e:
                print(f"解析实体列表失败: {e}")
                return []  # 如果解析失败，返回空列表


    # 注意：需要将字符串形式的列表转换为真实的 Python 列表
    # 在实际应用中，需要更健壮的解析方法，这里为了演示简化处理
    extracted_info = parse_entities(response_step1_str)
    print(extracted_info)

    # 步骤 2

    # 确保 extracted_info 是一个列表且不为空
    if isinstance(extracted_info, list) and extracted_info:
        prompt_step2 = f"""
        根据以下提取的关键信息，为原始文本生成一个简短的摘要（不超过 30 字），摘要应包含这些关键信息。

        关键信息：{extracted_info}
        原始文本：```{story_text}```
        """
        response_step2 = get_completion(prompt_step2)
        print("\n练习 6.2 输出 (步骤 2 - 生成摘要):")
        print(response_step2)
    else:
        print("\n练习 6.2 步骤 2: 未能成功提取或解析关键信息，无法生成摘要。")

    prod_review = """
           经过16个小时的谈判，中美谈判终于有了结果，中方凌晨3点召开记者发布会，通报的内容让外界松了口气，但对于后续的发展，中方并不会保持太乐观的态度。
       两天的深入谈判，中美在瑞士日内瓦举行的经贸高层会谈终于传来好消息，中方凌晨的报道非常简短，只有5句话。根据新华社的报道，第一句话交代了中美会谈的时间和地点，第二句话则表示中美两国代表主要谈判美对华征
       这次的报道确实是字少事大，毕竟对于美国对中国征收145%关税一事，已经引起中方的强烈反制，全球目光都聚焦在中美两国身上，高度关注中美关系后续的发展。而作为全球的世界性大国，中美关系是国际热点话题，甚至关
       从中方的通报结果来看，“实质性进展”确实是一个不小的突破，给中美关系发展带来了非常重要的拐点，同时也让外界松了一口气，终于不用担心中美关系会就此恶化，而引发潜在的危机了。
       美国总统特朗普宣誓就职以来，美方多次炒作“中国是最大竞争对手”的相关话题，甚至美国内阁成员还曝光对华作战计划，而且，特朗普发起关税战之后，直接将中美博弈搬到了明面上，让外界倒吸一口凉气。一方面，中美关
       从特朗普上台后的表现来看，他是不想与中方发生正面冲突的，毕竟两国一旦正面对峙，会发生什么样的结果他很清楚。但是，他又低不下自己高贵的头颅求中方帮一把，只能采取霸权手段威胁中方，逼迫中方主动向美服软，
       只可惜，美方这样的手段只对小国有效，对中国这样一个以理服人的国家来说，这样的手段只会让中方充满干劲，毕竟“不惹事但也不怕事”的态度已经刻在了中国人的骨子里。就在中美关系异常敏感的关键时刻，中方决定给
       从中方通报的结果来看，这次的谈判结果是积极乐观的。毕竟特朗普政府原本只想炫耀一下自己的实力，没曾想被中方打脸，让美国沦为了国际笑柄。而且，美对华征收关税的举措已经将美方画地为牢，美国港口现在已经萧条
       如今，中美双方都已经确认，此次会谈取得实质性进展，就对中美乃至世界多国来说，都是一个好消息，但曾经的历史经验告诉我们，对这样的结果不能太乐观。
       早在特朗普1.0时期，中方就曾与美方达成共识，之后，美方变脸的速度比翻书还快，仅仅2个月之后，便又对华出手以征收关税的方式为要挟，逼迫中方再次妥协。因此，我们不确定这一次是否还会上演此前的翻脸事件，因此
       不管怎么说，中美能坐到谈判桌上就足以说明，美方确实迫切希望与中方好好谈一谈，但后续中美关系如何发展，我们都需要保持高度警惕，同时要保持淡定，淡定看到结果和中美遇到的难题和困境。
       总之，中方已经用自己的诚意获得了越来越多国家的认可，而美方却因为霸权主义和强权政治正走上一条越来越孤单的道路。我们相信，只要全球团结一致共同反抗美国霸权，没有什么能阻止全球共同进步的步伐。
       """

    prompt = f"""
       请对三个反引号之间的新闻进行概括，不超过50个字。
       概括: ```{prod_review}```
       """

    response = get_completion(prompt)
    print("\n试着做 问题一 输出:")
    print(response)

    prompt = f"""
       请您从三个反引号之间的新闻文本中提取文章的关键信息，并以 JSON 格式输出。
       注意：需要包含以下类别：涉及的人物、机构、地点、事件核心要素（如谈判时间、地点、议题、结果简述、历史背景等）
       {{prod_review}}
       """

    response = get_completion(prompt)
    print("\n试着做 问题一 输出:")
    print(response)

    prompt = f"""
       您的任务是从新闻网站上生成一个新闻文章的概括。
       请对三个反引号之间的新闻内容进行概括，并且侧重在中国的未来挑战。
       总结: {prod_review}
       """

    response = get_completion(prompt)
    print("\n试着做 问题一 输出:")
    print(response)


    prod_review = """
    评论列表：
    1. "《寻梦环游记》真的超好哭的。这部片或许可以考虑改名叫《皮克斯教你如何在电影院哭出声来》。"
    2. "《蚁人3》看完之后，我感觉整部电影从剧作到制作都很敷衍，非常套路，没有任何惊喜之处，显得很无聊。"
    3. "《好东西》不仅带来了欢乐，更在无形之中拉近了两国人民的心理距离。尽管我们来自不同的文化背景，但在这部电影中，我们能看到许多共同面临的问题。"
    """
    prompt = f"""
    你的任务是分析电影评论，完成以下任务：
        1. 判断每条评论的情感倾向（正面 / 负面 / 中性）
        2. 提取每条评论主要讨论的话题（如：剧情、情感表达、演员表现、制作质量等）
        3. 将结果以 JSON 列表形式输出，每个对象包含评论原文、情感倾向和话题
    请按任务要求对三个反引号之间的评论内容进行处理。
    评论处理: {prod_review}
    """

    response = get_completion(prompt)
    print("\n试着做 问题二 输出:")
    print(response)


    prod_review = """
    想做柠檬水？挺简单的。先搞点柠檬，使劲挤出汁来。然后加点水，看你喜欢多浓。再放糖，搅匀了尝尝甜不甜。最后扔几块冰进去，搞定！
    """
    prompt = f"""
    你的任务是对文本格式、风格进行转换，任务要求如下：
        a) 将这段文字改写成一个清晰的、包含编号的步骤列表。
        b) 将生成的步骤列表翻译成英文。
        c) 对原始的非正式文字进行拼写和语法检查与修正，需要注意要正式的语言结构，不要口语化的表达，语法要严谨，注意改的是原文，因此要按照段落形式而不是步骤列表。
    请按照任务要求对三个反引号之间的文本内容进行处理。
    文本处理: {prod_review}
    """

    response = get_completion(prompt)
    print("\n试着做 问题三 输出:")
    print(response)


    system_prompt = """
    你是一个 “古代历史知识问答助手”，因此你的回答要带有一定的文言色彩而不是现代的白话文，你的回答要严谨、言之有理，性格是友好的。
    """
    user_question = "请问秦始皇统一六国是在哪一年？"
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_question}
    ]
    response = get_completion_from_messages(messages)
    print("\n试着做 问题四 输出:")
    print(response)


    prompt = f"""
    从下面的食谱描述中提取主要食材列表，要求：
    1. 去除重复项
    2. 返回格式：用中文逗号分隔的列表
    食谱：一份美味的番茄炒蛋需要新鲜的番茄、几个鸡蛋、少许葱花、盐和油。首先将鸡蛋打散，番茄切块。热锅倒油，先炒鸡蛋，然后盛出。再加点油，放入番茄块翻炒，加盐调味，最后倒入炒好的鸡蛋和葱花，快速翻炒均匀即可。
    """

    response = get_completion(prompt)
    print("\n试着做 问题五 输出:")
    print(response)


    prompt = f"""
    从下面的食谱描述中提取主要食材列表，要求：
    1. 去除重复项
    2. 只提取主要食材（排除盐、油等调味料以及葱花等辅料）
    3. 返回格式：用中文逗号分隔的列表
    食谱：一份美味的番茄炒蛋需要新鲜的番茄、几个鸡蛋、少许葱花、盐和油。首先将鸡蛋打散，番茄切块。热锅倒油，先炒鸡蛋，然后盛出。再加点油，放入番茄块翻炒，加盐调味，最后倒入炒好的鸡蛋和葱花，快速翻炒均匀即可。
    """

    response = get_completion(prompt)
    print("\n试着做 问题五 输出:")
    print(response)
