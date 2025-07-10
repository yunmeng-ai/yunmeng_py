import tkinter as tk
from tkinter import ttk, scrolledtext, font, messagebox
import threading
import time
import queue
import random
from library_core import LibraryAssistant, BOOK_DATA
from serial_communicator import SerialCommunicator  # 导入下位机通信函数
import re


class LibraryAssistantGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("图书馆智能助手")
        self.root.geometry("1100x750")
        self.root.configure(bg="#f0f8ff")
        self.serial_comm = SerialCommunicator()  # 创建串口通信器实例
        # 设置应用图标
        try:
            self.root.iconbitmap("library_icon.ico")
        except:
            pass

        # 字体配置
        self.font_size = 15  # 默认字体大小
        self.title_font = ("Segoe UI", 24, "bold")
        self.subtitle_font = ("Segoe UI", 14)
        self.button_font = ("Segoe UI", 12, "bold")
        self.message_font = ("Segoe UI", self.font_size)
        self.small_font = ("Segoe UI", 10)
        self.header_font = ("Segoe UI", self.font_size + 4, "bold")  # 加大字体

        # 颜色主题 - 用户消息改为柔和的紫色
        self.colors = {
            "primary": "#4e73df",
            "secondary": "#1cc88a",
            "accent": "#36b9cc",
            "user": "#6a5acd",  # 柔和的紫色
            "assistant": "#4e73df",
            "background": "#f8f9fc",
            "card": "#ffffff",
            "text": "#5a5c69",
            "header": "#d35400"  # 加大字体的颜色
        }

        # 表情符号集合
        self.emojis = {
            "book": ["📚", "📖", "📕", "📗", "📘", "📙", "📓"],
            "search": ["🔍", "🔎", "🧐"],
            "location": ["📍", "🗺️", "🧭"],
            "happy": ["😊", "😄", "😃", "🤩", "🙂"],
            "think": ["🤔", "💭", "🧠"],
            "success": ["✅", "👍", "👏"],
            "error": ["❌", "⚠️", "😕"]
        }

        # 创建助手实例
        self.assistant = LibraryAssistant()

        # 创建界面
        self.create_widgets()

        # 显示欢迎消息
        self.show_welcome_message()

        # 设置主题
        self.set_theme()

        # 创建消息队列
        self.message_queue = queue.Queue()
        self.process_message_queue()

    def set_theme(self):
        """设置现代UI主题"""
        style = ttk.Style()
        style.theme_use('clam')

        # 配置颜色
        style.configure('TFrame', background=self.colors["background"])
        style.configure('TLabel', background=self.colors["background"],
                        foreground=self.colors["text"])
        style.configure('TButton', font=self.button_font, borderwidth=0)
        style.configure('Primary.TButton', background=self.colors["primary"],
                        foreground="white")
        style.configure('Secondary.TButton', background=self.colors["secondary"],
                        foreground="white")
        style.configure('Card.TFrame', background=self.colors["card"], borderwidth=1,
                        relief='solid', bordercolor="#e5e7eb")
        style.configure('TEntry', fieldbackground=self.colors["card"], borderwidth=1,
                        relief='solid', foreground=self.colors["text"],
                        font=self.message_font)

    def create_widgets(self):
        # 主容器
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 应用标题
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))

        title_label = ttk.Label(
            header_frame,
            text=f"🎓 {self.get_random_emoji('book')} 图书馆智能助手 {self.get_random_emoji('book')}",
            font=self.title_font,
            foreground=self.colors["primary"]
        )
        title_label.pack(side=tk.LEFT)

        # 字体大小控制
        font_frame = ttk.Frame(header_frame)
        font_frame.pack(side=tk.RIGHT, padx=10)

        ttk.Label(font_frame, text="字体大小:", font=self.small_font).pack(side=tk.LEFT)

        self.font_size_var = tk.IntVar(value=self.font_size)
        font_spin = ttk.Spinbox(
            font_frame,
            from_=10,
            to=18,
            width=3,
            textvariable=self.font_size_var,
            command=self.update_font_size
        )
        font_spin.pack(side=tk.LEFT, padx=5)

        # 副标题
        subtitle_label = ttk.Label(
            header_frame,
            text="查询书籍位置 | 获取书籍信息 | 导航到书架",
            font=self.subtitle_font,
            foreground=self.colors["accent"]
        )
        subtitle_label.pack(side=tk.LEFT, padx=20, pady=(10, 0))

        # 主内容区域 - 卡片式布局
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # 左侧功能卡片
        left_card = ttk.Frame(content_frame, width=300, style='Card.TFrame')
        left_card.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        left_card.pack_propagate(False)

        # 右侧聊天卡片
        chat_card = ttk.Frame(content_frame, style='Card.TFrame')
        chat_card.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 填充左侧卡片
        self.create_left_card(left_card)

        # 填充聊天卡片
        self.create_chat_card(chat_card)

        # 添加下位机响应样式
        self.history_text.tag_configure("device",
                                        foreground="#8B4513",  # 深棕色
                                        font=(self.message_font[0], self.font_size, "italic"))

    def create_left_card(self, parent):
        """创建左侧功能卡片"""
        # 功能标题
        card_header = ttk.Frame(parent, padding=(20, 20, 20, 10))
        card_header.pack(fill=tk.X)

        card_title = ttk.Label(
            card_header,
            text=f"{self.get_random_emoji('search')} 功能导航 {self.get_random_emoji('search')}",
            font=self.button_font,
            foreground=self.colors["primary"]
        )
        card_title.pack(anchor="w")

        # 功能按钮
        button_frame = ttk.Frame(parent, padding=(20, 10, 20, 20))
        button_frame.pack(fill=tk.X)

        nav_button = ttk.Button(
            button_frame,
            text=f"{self.get_random_emoji('location')} 带我去找书",
            command=self.navigate_to_book,
            style='Secondary.TButton',
            width=20
        )
        nav_button.pack(fill=tk.X, pady=5, ipady=8)

        search_button = ttk.Button(
            button_frame,
            text=f"{self.get_random_emoji('search')} 搜索书籍位置",
            command=self.search_book,
            style='Primary.TButton',
            width=20
        )
        search_button.pack(fill=tk.X, pady=5, ipady=8)

        # 分隔线
        separator = ttk.Separator(parent, orient='horizontal')
        separator.pack(fill=tk.X, padx=20, pady=10)

        # 热门话题区域
        topics_frame = ttk.Frame(parent, padding=(20, 10, 20, 20))
        topics_frame.pack(fill=tk.BOTH, expand=True)

        topics_label = ttk.Label(
            topics_frame,
            text=f"📌 热门话题",
            font=self.button_font,
            foreground=self.colors["primary"]
        )
        topics_label.pack(anchor="w", pady=(0, 10))

        # 话题列表
        topics = [
            "📚 查询图书位置",
            "📖 获取图书详情",
            "📍 导航到书架",
            "🔥 热门图书推荐",
            "🆕 新书上架信息",
            "ℹ️ 图书借阅指南",
            "🕒 图书馆开放时间",
            "💻 电子资源访问"
        ]

        for topic in topics:
            topic_btn = ttk.Button(
                topics_frame,
                text=topic,
                command=lambda t=topic: self.select_topic(t),
                style='Secondary.TButton',
                width=20
            )
            topic_btn.pack(fill=tk.X, pady=3, ipady=5)

    def create_chat_card(self, parent):
        """创建聊天卡片"""
        # 聊天标题
        chat_header = ttk.Frame(parent, padding=(20, 20, 20, 10))
        chat_header.pack(fill=tk.X)

        chat_title = ttk.Label(
            chat_header,
            text=f"💬 与助手对话",
            font=self.button_font,
            foreground=self.colors["primary"]
        )
        chat_title.pack(anchor="w")

        # 聊天历史区域
        history_frame = ttk.Frame(parent, padding=(10, 10, 10, 10))
        history_frame.pack(fill=tk.BOTH, expand=True)

        self.history_text = scrolledtext.ScrolledText(
            history_frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=self.message_font,
            bg=self.colors["card"],
            padx=15,
            pady=15,
            relief="flat",
            highlightthickness=0
        )
        self.history_text.pack(fill=tk.BOTH, expand=True)

        # 添加文本样式
        self.history_text.tag_configure("assistant",
                                        foreground=self.colors["assistant"],
                                        font=self.message_font)
        self.history_text.tag_configure("user",
                                        foreground=self.colors["user"],  # 使用柔和的紫色
                                        font=self.message_font)
        self.history_text.tag_configure("bold",
                                        font=(self.message_font[0], self.font_size, "bold"))
        self.history_text.tag_configure("italic",
                                        font=(self.message_font[0], self.font_size, "italic"))
        self.history_text.tag_configure("highlight",
                                        background="#fff9c4",
                                        font=self.message_font)
        self.history_text.tag_configure("header",  # 加大字体样式
                                        foreground=self.colors["header"],
                                        font=self.header_font)

        # 用户输入区域
        input_frame = ttk.Frame(parent, padding=(20, 10, 20, 20))
        input_frame.pack(fill=tk.X)

        self.input_entry = ttk.Entry(
            input_frame,
            font=self.message_font
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=8)
        self.input_entry.bind("<Return>", self.send_message)
        self.input_entry.focus_set()

        send_button = ttk.Button(
            input_frame,
            text=f"发送 {self.get_random_emoji('happy')}",
            command=self.send_message,
            style='Primary.TButton',
            width=10
        )
        send_button.pack(side=tk.RIGHT, ipady=8)

        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set(f"{self.get_random_emoji('happy')} 就绪 | 输入问题或点击功能按钮")
        status_bar = ttk.Label(
            input_frame,
            textvariable=self.status_var,
            anchor=tk.W,
            padding=(0, 0, 10, 0),
            foreground=self.colors["accent"],
            font=self.small_font
        )
        status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def get_random_emoji(self, category):
        """获取随机表情符号"""
        return random.choice(self.emojis.get(category, ["✨"]))

    def update_font_size(self):
        """更新字体大小"""
        self.font_size = self.font_size_var.get()
        self.message_font = ("Segoe UI", self.font_size)
        self.header_font = ("Segoe UI", self.font_size + 4, "bold")  # 更新加大字体

        # 更新历史消息字体
        self.history_text.config(font=self.message_font)

        # 更新标签配置
        self.history_text.tag_configure("assistant",
                                        font=self.message_font)
        self.history_text.tag_configure("user",
                                        font=self.message_font)
        self.history_text.tag_configure("bold",
                                        font=(self.message_font[0], self.font_size, "bold"))
        self.history_text.tag_configure("italic",
                                        font=(self.message_font[0], self.font_size, "italic"))
        self.history_text.tag_configure("header",
                                        font=self.header_font)

    def show_welcome_message(self):
        """显示欢迎消息"""
        welcome_msg = (
            f"{self.get_random_emoji('happy')} 您好！我是您的图书馆助手，可以帮您：\n\n"
            f" {self.get_random_emoji('search')} 查询书籍的位置\n"
            f" {self.get_random_emoji('book')} 介绍书籍的详细内容\n"
            f"### {self.get_random_emoji('location')} 导航到书籍所在位置###\n\n"  # 使用加大字体标记
            f"{self.get_random_emoji('think')} 请告诉我您需要什么帮助！"
        )
        self.add_message("助手", welcome_msg)

    def add_message(self, sender, message):
        """添加消息到对话历史"""
        self.history_text.config(state=tk.NORMAL)

        # 添加发送者标签
        if sender == "助手":
            tag = "assistant"
            prefix = f"🤖 助手: "
        else:
            tag = "user"
            prefix = f"👤 您: "

        # 添加前缀
        self.history_text.insert(tk.END, prefix, tag)

        # 添加消息内容（带格式）
        self.add_formatted_text(message)

        # 添加换行
        self.history_text.insert(tk.END, "\n\n")

        self.history_text.config(state=tk.DISABLED)
        self.history_text.see(tk.END)

    def add_formatted_text(self, text):
        """添加带格式的文本"""
        # 处理加大字体标记（###）
        parts = text.split("###")
        for i, part in enumerate(parts):
            if i % 2 == 0:
                # 普通文本部分
                self.add_text_with_bold(part)
            else:
                # 加大字体部分
                self.history_text.insert(tk.END, part, "header")

    def add_text_with_bold(self, text):
        """添加带加粗格式的文本"""
        # 处理加粗标记（**）
        parts = text.split("**")
        for i, part in enumerate(parts):
            if i % 2 == 0:
                # 普通文本
                self.history_text.insert(tk.END, part)
            else:
                # 加粗文本
                self.history_text.insert(tk.END, part, "bold")

    def send_message(self, event=None):
        """处理用户发送消息"""
        user_input = self.input_entry.get().strip()
        if not user_input:
            return

        # 清除输入框并添加用户消息
        self.input_entry.delete(0, tk.END)
        self.add_message("您", user_input)
        self.status_var.set(f"{self.get_random_emoji('think')} 助手正在思考...")

        # 检查是否是导航请求
        if "带我去找" in user_input or "带路" in user_input or "导航" in user_input or "带我找" in user_input:
            response = self.assistant.handle_navigation_request(user_input)
            self.add_message("助手", f"{self.get_random_emoji('location')} {response}")
            self.status_var.set(f"{self.get_random_emoji('success')} 就绪 | 导航信息已提供")

            # 解析位置信息并发送到下位机
            # print(response)
            self.send_navigation_command(response)
            return

        # 在单独线程中处理AI响应
        threading.Thread(
            target=self.get_ai_response_thread,
            args=(user_input,),
            daemon=True
        ).start()

    def send_navigation_command(self, response):
        """
        从响应中解析位置信息并发送到下位机

        参数:
        response: 助手生成的导航响应文本
        """
        # 使用正则表达式解析位置信息

        pattern =  r"位置\s+([A-Z])"
        match = re.search(pattern, response)

        if match:
            area = match.group(1).upper()  # 区域代码 (如 'A')
            print(area)
            # shelf = int(match.group(2))  # 书架编号
            # print(shelf)

            # 在单独的线程中发送命令
            threading.Thread(
                target=self._send_navigation_command_thread,
                args=(area),
                daemon=True
            ).start()
        else:
            print("无法从响应中解析位置信息")

    def _send_navigation_command_thread(self, area):
        """在后台线程中发送导航命令"""
        try:
            success, response = self.serial_comm.send_location_command(area)
            # if success:
            #     self.message_queue.put(("status", f"{self.get_random_emoji('success')} 导航命令已发送"))
            #     if response:
            #         self.message_queue.put(("assistant_message", f"下位机响应: {response}"))
            # else:
                # self.message_queue.put(("error", f"{self.get_random_emoji('error')} 导航命令发送失败"))
        except Exception as e:
            print("error")
            # self.message_queue.put(("error", f"{self.get_random_emoji('error')} 发送命令时出错: {str(e)}"))


    def get_ai_response_thread(self, user_input):
        """在后台线程中获取AI响应"""
        try:
            # 获取AI响应
            response, error = self.assistant.get_ai_response(user_input)

            if error:
                self.message_queue.put(("error", f"{self.get_random_emoji('error')} 抱歉，处理请求时出错:\n{error}"))
            elif response:
                # 添加表情符号和格式
                enhanced_response = self.enhance_response(response)

                # 将响应拆分为字符队列
                char_queue = queue.Queue()
                for char in enhanced_response:
                    char_queue.put(char)

                # 将字符队列放入消息队列
                self.message_queue.put(("start_stream", ""))
                while not char_queue.empty():
                    char = char_queue.get()
                    self.message_queue.put(("char", char))
                    time.sleep(0.03)  # 控制输出速度
                self.message_queue.put(("end_stream", ""))

                # 更新状态
                self.message_queue.put(("status", f"{self.get_random_emoji('success')} 就绪 | 响应已完成"))
        except Exception as e:
            self.message_queue.put(("error", f"{self.get_random_emoji('error')} 发生意外错误:\n{str(e)}"))

    def enhance_response(self, response):
        """增强响应内容，添加表情符号和格式"""
        # 根据关键词添加表情符号
        keywords = {
            "书": self.get_random_emoji("book"),
            "位置": self.get_random_emoji("location"),
            "找到": self.get_random_emoji("success"),
            "错误": self.get_random_emoji("error"),
            "成功": self.get_random_emoji("success"),
            "帮助": "🙏",
            "谢谢": "😊"
        }

        # 添加表情符号
        for word, emoji in keywords.items():
            if word in response:
                response = response.replace(word, f"{word}{emoji}", 1)

        # 添加加粗效果
        if "位置" in response:
            response = response.replace("位置", "**位置**")
        if "书名" in response:
            response = response.replace("书名", "**书名**")

        # 添加加大字体效果（###标记）
        if "位置" in response:
            response = response.replace("位置", "###位置###")
        if "区域" in response:
            response = response.replace("区域", "###区域###")

        return response

    def process_message_queue(self):
        """处理消息队列中的消息"""
        try:
            while not self.message_queue.empty():
                msg_type, content = self.message_queue.get_nowait()

                if msg_type == "assistant_message":
                    self.add_message("助手", content)
                elif msg_type == "start_stream":
                    self.start_streaming_response()
                elif msg_type == "char":
                    self.add_streaming_char(content)
                elif msg_type == "end_stream":
                    self.end_streaming_response()
                elif msg_type == "error":
                    self.add_message("助手", content)
                    self.status_var.set(f"{self.get_random_emoji('error')} 错误 | 处理请求时出现问题")
                elif msg_type == "status":
                    self.status_var.set(content)

        except queue.Empty:
            pass

        # 每50毫秒检查一次队列
        self.root.after(50, self.process_message_queue)

    def start_streaming_response(self):
        """开始流式响应"""
        self.history_text.config(state=tk.NORMAL)
        self.history_text.insert(tk.END, "🤖 助手: ", "assistant")
        self.streaming_pos = self.history_text.index(tk.END)
        self.history_text.config(state=tk.DISABLED)
        self.history_text.see(tk.END)

    def add_streaming_char(self, char):
        """添加流式字符到响应"""
        self.history_text.config(state=tk.NORMAL)

        # 处理加粗标记
        if char == "*" and self.history_text.get("end-2c") == "*":
            # 开始或结束加粗
            self.history_text.delete("end-2c")
            self.history_text.insert("end-2c", "", "bold")
        # 处理加大字体标记
        elif char == "#" and self.history_text.get("end-2c") == "#" and self.history_text.get("end-3c") == "#":
            # 开始或结束加大字体
            self.history_text.delete("end-3c", "end")
            self.history_text.insert("end-3c", "", "header")
        else:
            self.history_text.insert(self.streaming_pos, char)

        self.streaming_pos = self.history_text.index(tk.END)
        self.history_text.config(state=tk.DISABLED)
        self.history_text.see(tk.END)

    def end_streaming_response(self):
        """结束流式响应"""
        self.history_text.config(state=tk.NORMAL)
        self.history_text.insert(tk.END, "\n\n")
        self.history_text.config(state=tk.DISABLED)
        self.history_text.see(tk.END)

    def navigate_to_book(self):
        """导航到最近查询的书"""
        self.input_entry.delete(0, tk.END)
        self.input_entry.insert(0, "带我去找最近查询的书")
        self.send_message()

    def search_book(self):
        """打开书籍搜索对话框"""
        # 创建书籍选择对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("🔍 搜索书籍位置")
        dialog.geometry("750x550")
        dialog.resizable(True, True)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.colors["background"])

        # 设置对话框位置在父窗口中心
        self.center_window(dialog, 750, 550)

        # 标题
        dialog_title = ttk.Label(
            dialog,
            text=f"🔍 {self.get_random_emoji('search')} 搜索图书馆藏书 {self.get_random_emoji('book')}",
            font=self.title_font,
            foreground=self.colors["primary"],
            background=self.colors["background"]
        )
        dialog_title.pack(pady=(30, 20))

        # 搜索框
        search_frame = ttk.Frame(dialog, padding=(30, 10, 30, 20))
        search_frame.pack(fill=tk.X)
        search_frame.configure(style='TFrame')

        search_label = ttk.Label(
            search_frame,
            text="搜索书籍名称:",
            font=self.subtitle_font,
            background=self.colors["background"]
        )
        search_label.pack(side=tk.LEFT, padx=(0, 15))

        search_entry = ttk.Entry(
            search_frame,
            font=self.message_font,
            width=40
        )
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        search_entry.focus_set()

        # 书籍列表
        list_frame = ttk.Frame(dialog, padding=(30, 5, 30, 20))
        list_frame.pack(fill=tk.BOTH, expand=True)
        list_frame.configure(style='TFrame')

        # 添加滚动文本框
        books_listbox = tk.Listbox(
            list_frame,
            font=self.message_font,
            selectmode=tk.SINGLE,
            bg=self.colors["card"],
            relief="flat",
            highlightthickness=0
        )
        books_listbox.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        scrollbar = ttk.Scrollbar(
            list_frame,
            command=books_listbox.yview,
            orient=tk.VERTICAL
        )
        scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        books_listbox.config(yscrollcommand=scrollbar.set)

        # 填充书籍列表
        book_titles = sorted([book["书名"] for book in BOOK_DATA])
        for title in book_titles:
            books_listbox.insert(tk.END, f"📖 {title}")

        # 搜索功能
        def filter_books(event=None):
            query = search_entry.get().strip().lower()
            books_listbox.delete(0, tk.END)
            if not query:
                for title in book_titles:
                    books_listbox.insert(tk.END, f"📖 {title}")
            else:
                for title in book_titles:
                    if query in title.lower():
                        books_listbox.insert(tk.END, f"📖 {title}")

        search_entry.bind("<KeyRelease>", filter_books)

        # 选择书籍
        def select_book():
            selection = books_listbox.curselection()
            if selection:
                book_title = books_listbox.get(selection[0])[2:]  # 去掉前面的表情符号
                dialog.destroy()
                self.input_entry.delete(0, tk.END)
                self.input_entry.insert(0, f"《{book_title}》在什么位置？")
                self.send_message()

        # 按钮区域
        button_frame = ttk.Frame(dialog, padding=(30, 10, 30, 20))
        button_frame.pack(fill=tk.X)
        button_frame.configure(style='TFrame')

        select_button = ttk.Button(
            button_frame,
            text=f"查询位置 {self.get_random_emoji('location')}",
            command=select_book,
            style='Primary.TButton',
            width=15
        )
        select_button.pack(side=tk.RIGHT, padx=(10, 0))

        cancel_button = ttk.Button(
            button_frame,
            text=f"取消 {self.get_random_emoji('error')}",
            command=dialog.destroy,
            style='Secondary.TButton',
            width=10
        )
        cancel_button.pack(side=tk.RIGHT)

        # 双击选择
        books_listbox.bind("<Double-1>", lambda e: select_book())

        # 初始焦点
        search_entry.focus_set()

    def select_topic(self, topic):
        """选择热门话题"""
        self.input_entry.delete(0, tk.END)
        self.input_entry.insert(0, topic.split(" ", 1)[1])  # 去掉表情符号
        self.send_message()

    def center_window(self, window, width, height):
        """将窗口居中显示"""
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        window.geometry(f"{width}x{height}+{x}+{y}")


