import requests
import json
import re

# 配置信息
API_URL = "https://api.siliconflow.cn/v1/chat/completions"
API_KEY = "sk-zadiajusdurgmkbbvppkaohyjnvetazfrmgeqgzspjcqslnc"  # 注意：实际使用请保护密钥！

# 构建请求头
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "Accept": "text/event-stream"
}

BOOK_DATA = [
  {
    "书名": "V字仇杀队",
    "图书位置": "A"
  },
  {
    "书名": "农村中学毕业生进城务工指南",
    "图书位置": "B"
  },
  {
    "书名": "艾美梦游",
    "图书位置": "C"
  },
  {
    "书名": "再见，幽门螺杆菌！",
    "图书位置": "B"
  },
  {
    "书名": "三毛流浪记全集",
    "图书位置": "C"
  },
  {
    "书名": "勃朗特姐妹的小小书",
    "图书位置": "C"
  },
  {
    "书名": "芒之颂歌",
    "图书位置": "D"
  },
  {
    "书名": "The Silmarillion",
    "图书位置": "D"
  },
  {
    "书名": "如何爱一个具体的人",
    "图书位置": "B"
  },
  {
    "书名": "灌籃高手完全版 1",
    "图书位置": "A"
  },
  {
    "书名": "时空定位钟",
    "图书位置": "D"
  },
  {
    "书名": "深入理解计算机系统（原书第2版）",
    "图书位置": "E"
  },
  {
    "书名": "好忙好忙小镇（全7册）",
    "图书位置": "C"
  },
  {
    "书名": "巴巴爸爸经典系列",
    "图书位置": "C"
  },
  {
    "书名": "如果在旷野，一个旅人",
    "图书位置": "D"
  },
  {
    "书名": "会打喷嚏的墙",
    "图书位置": "C"
  },
  {
    "书名": "黄气球",
    "图书位置": "C"
  },
  {
    "书名": "机器猫哆啦A梦（共45册）",
    "图书位置": "A"
  },
  {
    "书名": "藤子・F・不二雄大全集 哆啦A夢 01",
    "图书位置": "A"
  },
  {
    "书名": "終將成為妳 (8)",
    "图书位置": "A"
  },
  {
    "书名": "龙珠",
    "图书位置": "A"
  },
  {
    "书名": "哈利·波特",
    "图书位置": "D"
  },
  {
    "书名": "百年孤独",
    "图书位置": "D"
  },
  {
    "书名": "魔戒：插图版",
    "图书位置": "D"
  },
  {
    "书名": "The Return of the King",
    "图书位置": "D"
  },
  {
    "书名": "海的尽头有歌声",
    "图书位置": "D"
  },
  {
    "书名": "简单沟通：陪孩子走过青春期",
    "图书位置": "B"
  },
  {
    "书名": "两只小老鼠(全5册)",
    "图书位置": "C"
  },
  {
    "书名": "管錐編（全四冊）",
    "图书位置": "F"
  },
  {
    "书名": "全都抓起来啦！",
    "图书位置": "C"
  },
  {
    "书名": "后来呢后来怎么了",
    "图书位置": "C"
  },
  {
    "书名": "会飞的帽子",
    "图书位置": "C"
  },
  {
    "书名": "全景式图画书·开车出发系列（套装共7册）",
    "图书位置": "C"
  },
  {
    "书名": "今夜是满月",
    "图书位置": "C"
  },
  {
    "书名": "小麦的猴杆儿",
    "图书位置": "C"
  },
  {
    "书名": "火之鳥 復刻版 05",
    "图书位置": "A"
  },
  {
    "书名": "火之鳥 復刻版 04",
    "图书位置": "A"
  },
  {
    "书名": "丁丁历险记（共22本）",
    "图书位置": "A"
  },
  {
    "书名": "龙珠8",
    "图书位置": "A"
  },
  {
    "书名": "黃金神威（13）",
    "图书位置": "A"
  },
  {
    "书名": "黃金神威（14）",
    "图书位置": "A"
  },
  {
    "书名": "鼠族",
    "图书位置": "A"
  },
  {
    "书名": "火之鳥 復刻版 02",
    "图书位置": "A"
  },
  {
    "书名": "火之鳥 復刻版 11",
    "图书位置": "A"
  },
  {
    "书名": "跃动青春 7",
    "图书位置": "A"
  },
  {
    "书名": "黃金神威 (9)",
    "图书位置": "A"
  },
  {
    "书名": "龙珠14",
    "图书位置": "A"
  },
  {
    "书名": "龙珠 16",
    "图书位置": "A"
  },
  {
    "书名": "龙珠17",
    "图书位置": "A"
  },
  {
    "书名": "软件之道",
    "图书位置": "E"
  },
  {
    "书名": "大规模C++程序设计",
    "图书位置": "E"
  },
  {
    "书名": "程序员的思维修炼",
    "图书位置": "E"
  },
  {
    "书名": "面向对象是怎样工作的（第2版）",
    "图书位置": "E"
  },
  {
    "书名": "C#图解教程（第5版）",
    "图书位置": "E"
  },
  {
    "书名": "程序是怎样跑起来的",
    "图书位置": "E"
  },
  {
    "书名": "软件人才管理的艺术",
    "图书位置": "E"
  },
  {
    "书名": "代码整洁之道",
    "图书位置": "E"
  },
  {
    "书名": "软件项目成功之道",
    "图书位置": "E"
  },
  {
    "书名": "计算机程序的构造和解释(原书第2版)",
    "图书位置": "E"
  },
  {
    "书名": "ANSYS Workbench 工程实例详解",
    "图书位置": "E"
  },
  {
    "书名": "产品经理必懂的技术那点事儿：成为全栈产品经理",
    "图书位置": "E"
  },
  {
    "书名": "疯狂的程序员",
    "图书位置": "D"
  },
  {
    "书名": "编程之美",
    "图书位置": "E"
  },
  {
    "书名": "C专家编程",
    "图书位置": "E"
  },
  {
    "书名": "像计算机科学家一样思考Python",
    "图书位置": "E"
  },
  {
    "书名": "Python语言程序设计",
    "图书位置": "E"
  },
  {
    "书名": "MATLAB在数学建模中的应用",
    "图书位置": "E"
  },
  {
    "书名": "松本行弘的程式世界",
    "图书位置": "E"
  },
  {
    "书名": "Linux从入门到精通",
    "图书位置": "E"
  },
  {
    "书名": "深入淺出設計模式",
    "图书位置": "E"
  },
  {
    "书名": "从问题到程序",
    "图书位置": "E"
  },
  {
    "书名": "程序员修炼之道",
    "图书位置": "E"
  },
  {
    "书名": "Swift语言实战入门",
    "图书位置": "E"
  },
  {
    "书名": "Java语言精粹",
    "图书位置": "E"
  },
  {
    "书名": "黑客与画家",
    "图书位置": "E"
  },
  {
    "书名": "编程珠玑",
    "图书位置": "E"
  },
  {
    "书名": "JavaScript DOM编程艺术",
    "图书位置": "E"
  },
  {
    "书名": "C++ Primer 中文版（第 4 版）",
    "图书位置": "E"
  },
  {
    "书名": "Java编程思想",
    "图书位置": "E"
  },
  {
    "书名": "深入理解计算机系统",
    "图书位置": "E"
  },
  {
    "书名": "通用源码阅读指导书――MyBatis源码详解",
    "图书位置": "E"
  },
  {
    "书名": "司法的过程",
    "图书位置": "F"
  },
  {
    "书名": "iBATIS实战",
    "图书位置": "E"
  },
  {
    "书名": "Java编程思想 （第4版）",
    "图书位置": "E"
  },
  {
    "书名": "Effective C# 中文版",
    "图书位置": "E"
  },
  {
    "书名": "轻快的Java",
    "图书位置": "E"
  },
  {
    "书名": "设计模式",
    "图书位置": "E"
  },
  {
    "书名": "法治构图",
    "图书位置": "F"
  },
  {
    "书名": "松本行弘的程序世界",
    "图书位置": "E"
  },
  {
    "书名": "Linux内核设计的艺术",
    "图书位置": "E"
  },
  {
    "书名": "交易系统",
    "图书位置": "E"
  },
  {
    "书名": "编程人生",
    "图书位置": "E"
  },
  {
    "书名": "C语言深度解剖",
    "图书位置": "E"
  },
  {
    "书名": "编程之魂",
    "图书位置": "E"
  },
  {
    "书名": "梦断代码",
    "图书位置": "E"
  },
  {
    "书名": "Head First 设计模式（中文版）",
    "图书位置": "E"
  },
  {
    "书名": "CSS禅意花园",
    "图书位置": "E"
  },
  {
    "书名": "电脑报（上下册）",
    "图书位置": "E"
  },
  {
    "书名": "正当法律程序简史",
    "图书位置": "F"
  },
  {
    "书名": "宦官与太监/中国文化知识读本",
    "图书位置": "历史与社会科学"
  },
  {
    "书名": "丘吉尔：第二次世界大战回忆录",
    "图书位置": "历史与社会科学"
  },
  {
    "书名": "再次远行：莱昂纳德·科恩访谈录",
    "图书位置": "历史与社会科学"
  },
  {
    "书名": "纵横天下一张嘴",
    "图书位置": "历史与社会科学"
  },
  {
    "书名": "定量社会研究方法(上、下)",
    "图书位置": "历史与社会科学"
  },
  {
    "书名": "诗词动物城：漫画李白传",
    "图书位置": "A"
  },
  {
    "书名": "当代心理治疗",
    "图书位置": "B"
  },
  {
    "书名": "精神现象学",
    "图书位置": "B"
  },
  {
    "书名": "毛泽东选集",
    "图书位置": "历史与社会科学"
  },
  {
    "书名": "陀思妥耶夫斯基（第1卷）",
    "图书位置": "D"
  },
  {
    "书名": "史记（中华经典名著全本全注全译丛书-三全本·全十册）",
    "图书位置": "历史与社会科学"
  },
  {
    "书名": "吉尔莫·德尔·托罗的奇思妙想",
    "图书位置": "历史与社会科学"
  },
  {
    "书名": "全球通史",
    "图书位置": "历史与社会科学"
  },
  {
    "书名": "原来古代人是这样打仗的：古希腊与波斯",
    "图书位置": "历史与社会科学"
  },
  {
    "书名": "东晋门阀政治",
    "图书位置": "历史与社会科学"
  },
  {
    "书名": "中国近代思想与学术的系谱",
    "图书位置": "历史与社会科学"
  },
  {
    "书名": "画作的诞生",
    "图书位置": "A"
  },
  {
    "书名": "可复制的创意力",
    "图书位置": "B"
  },
  {
    "书名": "从呼捷玛斯到未来图景：苏俄设计历史（修订本）",
    "图书位置": "设计与技术"
  },
  {
    "书名": "助人技术本土化的刻意练习",
    "图书位置": "B"
  },
  {
    "书名": "卡拉马佐夫兄弟",
    "图书位置": "D"
  },
  {
    "书名": "勃朗特姐妹的小小书",
    "图书位置": "C"
  },
  {
    "书名": "千千阕",
    "图书位置": "D"
  },
  {
    "书名": "柬埔寨双子星",
    "图书位置": "D"
  },
  {
    "书名": "如何爱一个具体的人",
    "图书位置": "B"
  },
  {
    "书名": "驾驭恐惧",
    "图书位置": "B"
  },
  {
    "书名": "西方艺术史",
    "图书位置": "历史与社会科学"
  },
  {
    "书名": "无物象的世界",
    "图书位置": "设计与技术"
  },
  {
    "书名": "论确定性",
    "图书位置": "历史与社会科学"
  },
  {
    "书名": "先验唯心论体系",
    "图书位置": "历史与社会科学"
  },
  {
    "书名": "写给孩子的哲学启蒙书（全9册）",
    "图书位置": "C"
  },
  {
    "书名": "现象学的心灵",
    "图书位置": "B"
  },
  {
    "书名": "几何原本",
    "图书位置": "历史与社会科学"
  },
  {
    "书名": "理性的悖谬与潜能",
    "图书位置": "历史与社会科学"
  },
  {
    "书名": "康德《道德形而上学奠基》评注",
    "图书位置": "历史与社会科学"
  },
  {
    "书名": "18-19世纪德国哲学",
    "图书位置": "历史与社会科学"
  },
  {
    "书名": "论动物的运动",
    "图书位置": "历史与社会科学"
  },
  {
    "书名": "孙中山史事编年",
    "图书位置": "历史与社会科学"
  },
  {
    "书名": "乱世的抗争：讲给大家的<孟子>",
    "图书位置": "D"
  },
  {
    "书名": "陀思妥耶夫斯基（第5卷）",
    "图书位置": "D"
  },
  {
    "书名": "托马斯·哈代传",
    "图书位置": "D"
  },
  {
    "书名": "帕斯捷尔纳克传（上下）",
    "图书位置": "D"
  },
  {
    "书名": "南京大屠杀",
    "图书位置": "历史与社会科学"
  },
  {
    "书名": "资治通鉴",
    "图书位置": "历史与社会科学"
  },
  {
    "书名": "法国旧制度末期的税收、特权和政治",
    "图书位置": "历史与社会科学"
  },
  {
    "书名": "中国历史纪年表",
    "图书位置": "历史与社会科学"
  },
  {
    "书名": "1007天的战争",
    "图书位置": "历史与社会科学"
  },
  {
    "书名": "室内设计实战指南（工艺、材料篇）",
    "图书位置": "设计与技术"
  },
  {
    "书名": "印谱（第三版）",
    "图书位置": "设计与技术"
  },
  {
    "书名": "红楼梦",
    "图书位置": "D"
  },
  {
    "书名": "反思社会学导引",
    "图书位置": "B"
  },
  {
    "书名": "精神病学的权力",
    "图书位置": "B"
  },
  {
    "书名": "知否知否应是人间清照",
    "图书位置": "D"
  },
  {
    "书名": "少年游·敦煌",
    "图书位置": "C"
  },
  {
    "书名": "敦煌",
    "图书位置": "历史与社会科学"
  },
  {
    "书名": "小王子",
    "图书位置": "D"
  },
  {
    "书名": "世界童话名著连环画",
    "图书位置": "C"
  },
  {
    "书名": "再见，幽门螺杆菌！",
    "图书位置": "B"
  },
  {
    "书名": "哈利·波特与火焰杯",
    "图书位置": "D"
  },
  {
    "书名": "女孩和流浪猫",
    "图书位置": "A"
  },
  {
    "书名": "红楼梦脂评汇校本",
    "图书位置": "D"
  },
  {
    "书名": "红楼梦脂评汇校本",
    "图书位置": "D"
  },
  {
    "书名": "十一家注孙子校理",
    "图书位置": "历史与社会科学"
  },
  {
    "书名": "史记会注考证（修订本）",
    "图书位置": "历史与社会科学"
  },
  {
    "书名": "李太白全集",
    "图书位置": "历史与社会科学"
  },
  {
    "书名": "乐府诗集（新排本）",
    "图书位置": "历史与社会科学"
  },
  {
    "书名": "Kay Nielsen: East of the Sun and West of the Moon",
    "图书位置": "A"
  },
  {
    "书名": "猫头鹰的眼泪茶·世界大师经典桥梁书（全6册）",
    "图书位置": "C"
  },
  {
    "书名": "如果历史是一所学校",
    "图书位置": "C"
  },
  {
    "书名": "点点冒险故事-全7册",
    "图书位置": "C"
  },
  {
    "书名": "讲了100万次的中国神怪故事（第1辑）",
    "图书位置": "C"
  },
  {
    "书名": "百年孤独",
    "图书位置": "D"
  },
  {
    "书名": "红楼梦（大字本）",
    "图书位置": "D"
  },
  {
    "书名": "红楼梦：脂砚斋全评本",
    "图书位置": "D"
  },
  {
    "书名": "十二个月",
    "图书位置": "历史与社会科学"
  },
  {
    "书名": "新刻繡像批評金瓶梅(會校本·重訂版)",
    "图书位置": "历史与社会科学"
  },
  {
    "书名": "The Character Of Physical Law",
    "图书位置": "历史与社会科学"
  },
  {
    "书名": "脂砚斋评石头记（上下）",
    "图书位置": "D"
  },
  {
    "书名": "红楼梦（全三册）",
    "图书位置": "D"
  },
  {
    "书名": "梦见沈从文先生",
    "图书位置": "历史与社会科学"
  },
  {
    "书名": "诗人之舌",
    "图书位置": "D"
  },
  {
    "书名": "物性论",
    "图书位置": "D"
  },
  {
    "书名": "给孩子的诗与歌",
    "图书位置": "C"
  },
  {
    "书名": "新譯唐詩三百首",
    "图书位置": "D"
  },
  {
    "书名": "唐集体例笺证",
    "图书位置": "历史与社会科学"
  },
  {
    "书名": "宋本杜工部集（全五册）",
    "图书位置": "历史与社会科学"
  },
  {
    "书名": "The Lyrics",
    "图书位置": "D"
  },
  {
    "书名": "法国童话精选",
    "图书位置": "C"
  },
  {
    "书名": "摹仿论",
    "图书位置": "D"
  },
  {
    "书名": "会打喷嚏的墙",
    "图书位置": "D"
  },
  {
    "书名": "皮皮熊和他的朋友们",
    "图书位置": "C"
  },
  {
    "书名": "寄生之子 1",
    "图书位置": "D"
  },
  {
    "书名": "让美寻找美",
    "图书位置": "D"
  },
  {
    "书名": "巴巴爸爸经典系列",
    "图书位置": "C"
  },
  {
    "书名": "绿宝石阴谋",
    "图书位置": "D"
  }
]

# 初始化对话历史

class LibraryAssistant:
    def __init__(self):
        self.conversation_history = [
            {
                "role": "system",
                "content": (
                    "你是一个图书馆助手，负责帮助用户查找书籍位置，以及介绍书籍的详细内容。"
                    "我们图书馆的书籍存放位置如下：\n" +
                    "\n".join([f"- 《{book['书名']}》: 位置 {book['图书位置']}" for book in BOOK_DATA]) +
                    "\n\n当用户询问书籍位置时，请直接回答具体位置。"
                    "如果书籍不在列表中，请如实告知用户。"
                    "请保持友好、专业的服务态度。"
                )
            }
        ]
        self.last_location = None
        self.last_book_title = None


    # def print_conversation_history():
    #     """打印完整的对话历史（调试用）"""
    #     print("\n===== 当前对话历史 =====")
    #     for entry in conversation_history:
    #         role = entry["role"]
    #         content = entry["content"]
    #
    #         if role == "system":
    #             print(f"系统: {content}")
    #         elif role == "user":
    #             print(f"用户: {content}")
    #         elif role == "assistant":
    #             print(f"AI助手: {content}")
    #     print("=======================\n")


    last_location = None
    last_book_title = None


    def get_ai_response(self, prompt):
        """获取AI的流式响应并返回完整回复"""
        # 添加用户消息到历史记录
        self.conversation_history.append({"role": "user", "content": prompt})

        # 构建请求体
        payload = {
            "model": "deepseek-ai/DeepSeek-R1",
            "messages": self.conversation_history,
            "stream": True,
            "temperature": 0.5
        }

        full_content = ""
        try:
            response = requests.post(API_URL, headers=headers, json=payload, stream=True)

            if response.status_code != 200:
                return None, f"请求失败: {response.status_code} - {response.text}"

            for chunk in response.iter_lines():
                if chunk:
                    decoded_chunk = chunk.decode('utf-8').strip()

                    if not decoded_chunk or decoded_chunk == "data: [DONE]":
                        continue

                    if decoded_chunk.startswith('data:'):
                        json_str = decoded_chunk[5:].strip()

                        try:
                            data = json.loads(json_str)
                            if "choices" in data and data["choices"]:
                                content = data["choices"][0].get("delta", {}).get("content", "")
                                if content:
                                    full_content += content
                        except json.JSONDecodeError:
                            continue

            # 添加AI回复到历史记录
            if full_content:
                ai_response_entry = {"role": "assistant", "content": full_content}
                self.conversation_history.append(ai_response_entry)
                self._extract_location_and_title(full_content)

            return full_content, None

        except requests.RequestException as e:
            return None, f"请求异常: {e}"


    def _extract_location_and_title(self, response):
        """从AI回复中提取位置信息和书名"""
        # 尝试匹配位置信息
        location_match = re.search(
            r'(位置|在|位于)\s*([A-Z]|历史与社会科学|设计与技术|\b[A-Z]区\b|\b[A-Z]位置\b)',
            response
        )
        if location_match:
            loc = location_match.group(2)
            if loc:
                self.last_location = loc

        # 尝试匹配书名
        book_match = re.search(r'《(.+?)》', response)
        if book_match:
            self.last_book_title = book_match.group(1)


    def handle_navigation_request(self, user_input):
        """处理导航请求"""
        # 尝试从用户输入中提取书名
        if not self.last_book_title:
            book_match = re.search(r'《(.+?)》', user_input)
            if book_match:
                self.last_book_title = book_match.group(1)

        # 如果位置信息缺失但书名存在，尝试查找位置
        if not self.last_location and self.last_book_title:
            for book in BOOK_DATA:
                if book["书名"] == self.last_book_title:
                    self.last_location = book["图书位置"]
                    break

        if not self.last_location:
            return "抱歉，我还没有记录任何位置信息，请先查询一本书的位置。"

        if not self.last_book_title:
            return f"请前往位置 {self.last_location} 寻找您要的书籍。"

        return f"请前往位置 {self.last_location} 寻找《{self.last_book_title}》。"

    def get_conversation_history(self):
        """获取对话历史"""
        return self.conversation_history.copy()

    # def handle_navigation_request(user_input):
    #   """处理导航请求"""
    #   global last_location, last_book_title
    #
    #   # 尝试从用户输入中提取书名
    #   if not last_book_title:
    #     book_match = re.search(r'《(.+?)》', user_input)
    #     if book_match:
    #       last_book_title = book_match.group(1)
    #       # print(f"[DEBUG] 从用户输入中提取书名: {last_book_title}")
    #
    #   # 如果位置信息缺失但书名存在，尝试查找位置
    #   if not last_location and last_book_title:
    #     # 在BOOK_DATA中查找位置
    #     for book in BOOK_DATA:
    #       if book["书名"] == last_book_title:
    #         last_location = book["图书位置"]
    #         # print(f"[DEBUG] 根据书名查找位置: {last_book_title} -> {last_location}")
    #         break
    #
    #   if not last_location:
    #     return "抱歉，我还没有记录任何位置信息，请先查询一本书的位置。"
    #
    #   if not last_book_title:
    #     return f"请前往位置 {last_location} 寻找您要的书籍。"
    #
    #   return f"请前往位置 {last_location} 寻找《{last_book_title}》。"


# 主循环
# if __name__ == "__main__":
#
#
#   print("===== 图书馆智能助手 =====")
#   print("输入 '带我去找' 导航到最近查询的书籍位置")
#   print("输入您的问题开始对话，输入 '退出' 结束对话")
#   print("输入 '历史' 查看当前对话记录\n")
#
#   while True:
#     user_input = input("\n你: ").strip()
#
#     if not user_input:
#       continue
#
#     if user_input.lower() in ["退出", "exit", "quit"]:
#       print("\n感谢使用图书馆查询系统！")
#       break
#
#     if user_input.lower() in ["历史", "history"]:
#       print_conversation_history()
#       continue
#
#     # 检查是否是导航请求
#     if "带我去找" in user_input or "带路" in user_input or "导航" in user_input:
#       response = handle_navigation_request(user_input)
#       print(f"\nAI: {response}")
#
#       # 添加到对话历史
#       conversation_history.append({
#         "role": "assistant",
#         "content": response
#       })
#     else:
#       # 普通对话处理
#       ai_response = get_ai_response(user_input)
#
#       # 处理空响应
#       if not ai_response:
#         print("\n(未收到有效响应，请重试)")