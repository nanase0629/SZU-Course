SYSTEM_CONFIG = {
    "project_name": "宋代历史RAG系统",
    "version": "1.1.0",  # 更新版本号
    "encoding": "utf-8"
}

DATA_SOURCES = {
    "default_urls": [
        "https://zh.wikipedia.org/wiki/宋朝",
        "https://zh.wikipedia.org/wiki/北宋",
        "https://zh.wikipedia.org/wiki/南宋",
        "https://zh.wikipedia.org/wiki/宋朝文化",
        "https://zh.wikipedia.org/wiki/宋朝科技",
        "https://zh.wikipedia.org/wiki/宋朝行政区划",
        "https://zh.wikipedia.org/wiki/宋朝货币",
        "https://zh.wikipedia.org/wiki/宋朝建筑",
        "https://zh.wikipedia.org/wiki/宋朝文学",
        "https://ls.httpcn.com/chaodai/songchao/",
        "https://www.baike.com/wikiid/2231426834419581803?baike_source=doubao",
        "https://www.gugong.net/zhongguo/songchao/",
        "https://www.lishimingren.com/chaodai/songchao/",
        "https://baike.sogou.com/v6826.htm",
        "https://www.sohu.com/a/217665369_99996707",
        "https://www.worldhistory.org/trans/zh/1-16215/",
        "https://www.thepaper.cn/newsDetail_forward_14553739",
        'https://skzx.zjol.com.cn/ch133/system/2022/03/08/033516803.shtml',
        'https://news.qq.com/rain/a/20200427A0FQHY00',
        'https://www.163.com/dy/article/JHTIMBPN05521GCR.html',
        'https://epaper.scdaily.cn/shtml/scrb/20250530/327046.shtml',
        'http://economy.guoxue.com/?p=2805',
        'http://iolaw.cssn.cn/jdfls/200506/t20050614_4596220.shtml',
        'https://www.sohu.com/a/387363581_523159',
        'https://www.aisixiang.com/data/122264.html',
        'https://epaper.gmw.cn/gmrb/html/2017-01/02/nw.D110000gmrb_20170102_2-06.htm',
        'https://www.163.com/money/article/BR63B62U00253B0H.html',
        'http://lishisuo.cass.cn/lsyjs_zhcx/lsyjs_py/202010/t20201009_5192323.shtml'

    ],
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    },
    "timeout": 30,
    "retry_times": 3,
    "delay_between_requests": 1,  # 秒
    "crawl_depth": 0,  # 搜索深度
    "max_pages": 200,  # 新增：最大爬取页面数限制
    "max_links_per_page": 10,  # 新增：每个页面最多爬取的内链数
    "allowed_namespaces": ["宋朝", "北宋", "南宋", "宋代", "宋元", "赵匡胤", "赵光义", "赵构", "王安石", "司马光",
                           "苏轼", "沈括",
                           "朱熹", "岳飞", "文天祥", "杨家将", "水浒传", "清明上河图", "活字印刷", "交子", "宋词",
                           "程朱理学", "宋诗",
                           "火药", "指南针", "陈桥兵变", "平定割据", "杯酒释兵权", "科举取士", "宋辽之战", "澶渊之盟",
                           "泰山封禅",
                           "宋夏之战", "庆历新政", "嘉祐盛治", "熙宁变法", "元祐更化", "海上之盟", "靖康之变",
                           "绍兴和议", "隆兴和议",
                           "三朝内禅", "庆元党禁", "开禧北伐", "端平更化", "端平入洛", "襄阳之战", "崖山海战"],
    "disallowed_domains": [
        "taobao.com", "jd.com", "douyin.com", "weibo.com"
    ],
    "allowed_languages": ["zh-cn", "zh"]
}

TEXT_PROCESSING = {
    "chunk_size": 500,
    "chunk_overlap": 50,
    "min_chunk_size": 100,
    "remove_patterns": [
        r'[编辑]', r'[隐藏]', r'[显示]',
        r'^\s*\n', r'\n{3,}',
        r'（.*?）', r'广告.*', r'版权声明.*', r'联系我们.*'
    ],
    "remove_elements": [
        'script', 'style', 'sup.reference',
        '.navbox', '.infobox', '.toc',
        '.mw-editsection', '.hatnote', '.thumb',
        '.mw-jump-link', '.mw-empty-elt', '.ambox',
        '.navpopup', '.metadata', '.mw-references-wrap',
    ]
}

FILE_CONFIG = {
    "supported_formats": [".txt", ".md", ".pdf", ".html"],
    "max_file_size": 10 * 1024 * 1024,
    "upload_folder": "./uploads",
    "output_folder": "./output"
}

OUTPUT_FILES = {
    "raw_data": "raw/raw_data.json",
    "cleaned_data": "clean/cleaned_data.json"
}

LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "output/log/rag_system.log"
}