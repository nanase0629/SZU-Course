import random
import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from config import DB_CONFIG
import datetime
from db_operations import register_user  # 添加导入

class LostAndFoundApp:
    def __init__(self, root):
        self.root = root
        self.root.title("校园失物招领平台")
        self.root.geometry("800x600")
        
        # 设置主窗口的网格权重，使内容居中
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # 创建主容器框架
        self.main_container = ttk.Frame(self.root)
        self.main_container.grid(row=0, column=0, sticky="nsew")
        
        # 设置主容器的网格权重
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)
        
        self.current_user = None
        self.setup_db_connection()
        self.create_login_frame()

        self.last_notice_id = 0  # 初始化最后一个通知编号为0
        
    def setup_db_connection(self):
        try:
            self.conn = mysql.connector.connect(**DB_CONFIG)
            self.cursor = self.conn.cursor(dictionary=True)
            self.cursor.execute("SET NAMES utf8mb4")
            self.cursor.execute("SET CHARACTER SET utf8mb4")
            self.cursor.execute("SET character_set_connection=utf8mb4")
        except mysql.connector.Error as err:
            messagebox.showerror("数据库连接错误", str(err))
            
    def create_login_frame(self):
        # 创建登录框架
        self.login_frame = ttk.Frame(self.main_container)
        self.login_frame.grid(row=0, column=0)
        
        # 创建样式
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Microsoft YaHei UI', 24, 'bold'))
        style.configure('Subtitle.TLabel', font=('Microsoft YaHei UI', 10))
        style.configure('Custom.TButton', font=('Microsoft YaHei UI', 10))
        
        # 创建内容框架
        content_frame = ttk.Frame(self.login_frame, padding=20)
        content_frame.grid(row=0, column=0, padx=50, pady=50)
        
        # 标题和副标题
        ttk.Label(content_frame, text="校园失物招领平台", style='Title.TLabel').grid(row=0, column=0, columnspan=2, pady=(0, 10))
        ttk.Label(content_frame, text="Lost and Found System", style='Subtitle.TLabel').grid(row=1, column=0, columnspan=2, pady=(0, 30))
        
        # 用户名输入框
        ttk.Label(content_frame, text="用户编号:", font=('Microsoft YaHei UI', 10)).grid(row=2, column=0, padx=(0, 10), pady=5, sticky='e')
        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(content_frame, textvariable=self.username_var, width=30)
        username_entry.grid(row=2, column=1, pady=5, sticky='w')
        
        # 密码输入框
        ttk.Label(content_frame, text="密    码:", font=('Microsoft YaHei UI', 10)).grid(row=3, column=0, padx=(0, 10), pady=5, sticky='e')
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(content_frame, textvariable=self.password_var, show="*", width=30)
        password_entry.grid(row=3, column=1, pady=5, sticky='w')
        
        # 按钮框架
        button_frame = ttk.Frame(content_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        # 登录按钮
        login_btn = ttk.Button(button_frame, text="登录", command=self.login, style='Custom.TButton', width=15)
        login_btn.pack(side=tk.LEFT, padx=5)
        
        # 注册按钮
        register_btn = ttk.Button(button_frame, text="注册", command=self.show_register_frame, style='Custom.TButton', width=15)
        register_btn.pack(side=tk.LEFT, padx=5)
        
        # 版权信息
        ttk.Label(content_frame, text="2022150221 何泽锋",
                 style='Subtitle.TLabel').grid(row=5, column=0, columnspan=2, pady=(30, 0))
        
        # 设置默认焦点
        username_entry.focus()
        
        # 绑定回车键
        username_entry.bind('<Return>', lambda e: password_entry.focus())
        password_entry.bind('<Return>', lambda e: self.login())



    def create_main_frame(self):
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建标签页
        self.tab_control = ttk.Notebook(self.main_frame)
        
        # 失物列表标签页
        self.lost_items_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.lost_items_tab, text="失物列表")
        self.setup_lost_items_tab()
        
        # 报失/拾获标签页
        self.report_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.report_tab, text="报失/拾获")
        self.setup_report_tab()
        
        # 个人信息标签页
        self.profile_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.profile_tab, text="个人信息")
        self.setup_profile_tab()


        # 我的认领记录标签页（普通用户）
        if self.current_user['用户类型'] == '普通用户':
            self.my_claims_tab = ttk.Frame(self.tab_control)
            self.tab_control.add(self.my_claims_tab, text="我的认领记录")
            self.setup_my_claims_tab()
            # 系统通知标签页
            self.notices_tab = ttk.Frame(self.tab_control)
            self.tab_control.add(self.notices_tab, text="系统通知")
            self.setup_notices_tab()  # 设置通知标签页

        # 管理员标签页
        if self.current_user['用户类型'] == '管理员':
            self.admin_tab = ttk.Frame(self.tab_control)
            self.tab_control.add(self.admin_tab, text="管理")
            self.setup_admin_tab()
        
        self.tab_control.pack(expand=1, fill="both")
        
        # 登出按钮
        ttk.Button(self.main_frame, text="登出", command=self.logout).pack(pady=10)



    def setup_lost_items_tab(self):
        # 创建表格视图
        columns = ('物品编号', '物品名称', '类别', '地点', '时间', '状态', '是否贵重')
        self.lost_items_tree = ttk.Treeview(self.lost_items_tab, columns=columns, show='headings')
        
        for col in columns:
            self.lost_items_tree.heading(col, text=col)
            self.lost_items_tree.column(col, width=100)
            
        self.lost_items_tree.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        button_frame = ttk.Frame(self.lost_items_tab)
        button_frame.pack(pady=5)
        
        ttk.Button(button_frame, text="刷新", command=self.refresh_lost_items).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="认领", command=self.claim_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="查看详情", command=self.view_item_detail).pack(side=tk.LEFT, padx=5)
        
        self.refresh_lost_items()
        
    def setup_report_tab(self):
        # 创建报失/拾获表单
        ttk.Label(self.report_tab, text="报告失物/拾获物品").pack(pady=10)
        
        form_frame = ttk.Frame(self.report_tab)
        form_frame.pack(pady=10, padx=10)
        
        labels = ['物品名称:', '类别:', '描述:', '地点:', '时间:']
        self.report_vars = {}
        
        for i, label in enumerate(labels):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, pady=5, padx=5)
            self.report_vars[label] = tk.StringVar()
            ttk.Entry(form_frame, textvariable=self.report_vars[label]).grid(row=i, column=1, pady=5, padx=5)
            
        # 报告类型选择
        self.report_type = tk.StringVar(value="丢失")
        ttk.Radiobutton(form_frame, text="报失", variable=self.report_type, value="丢失").grid(row=len(labels), column=0)
        ttk.Radiobutton(form_frame, text="拾获", variable=self.report_type, value="拾获").grid(row=len(labels), column=1)
        
        # 贵重物品标记
        self.is_valuable = tk.BooleanVar(value=False)
        ttk.Checkbutton(form_frame, text="贵重物品", variable=self.is_valuable).grid(row=len(labels)+1, column=0, columnspan=2)
        
        # 提交按钮
        ttk.Button(form_frame, text="提交", command=self.submit_report).grid(row=len(labels)+2, column=0, columnspan=2, pady=10)
        
    def setup_admin_tab(self):
        # 创建管理员功能标签页
        admin_notebook = ttk.Notebook(self.admin_tab)
        
        # 认领管理标签页
        claims_frame = ttk.Frame(admin_notebook)
        admin_notebook.add(claims_frame, text="认领管理")
        
        # 投诉管理标签页
        complaints_frame = ttk.Frame(admin_notebook)
        admin_notebook.add(complaints_frame, text="投诉管理")
        
        # 用户管理标签页
        users_frame = ttk.Frame(admin_notebook)
        admin_notebook.add(users_frame, text="用户管理")
        
        # 失信名单标签页
        blacklist_frame = ttk.Frame(admin_notebook)
        admin_notebook.add(blacklist_frame, text="失信名单")

        notices_frame = ttk.Frame(admin_notebook)
        admin_notebook.add(notices_frame, text="编辑通知")


        admin_notebook.pack(expand=1, fill="both")
        
        # 设置各管理页面
        self.setup_claims_management(claims_frame)
        self.setup_complaints_management(complaints_frame)
        self.setup_users_management(users_frame)
        self.setup_blacklist_management(blacklist_frame)
        self.setup_notices_management(notices_frame)

        
    def setup_my_claims_tab(self):
        # 创建我的认领记录表格
        columns = ('认领编号', '物品名称', '认领时间', '认领状态')
        self.my_claims_tree = ttk.Treeview(self.my_claims_tab, columns=columns, show='headings')
        
        for col in columns:
            self.my_claims_tree.heading(col, text=col)
            self.my_claims_tree.column(col, width=100)
        
        self.my_claims_tree.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # 刷新按钮
        button_frame = ttk.Frame(self.my_claims_tab)
        button_frame.pack(pady=5)
        
        ttk.Button(button_frame, text="刷新", command=self.refresh_my_claims).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="查看详情", command=self.view_claim_detail).pack(side=tk.LEFT, padx=5)
        
        self.refresh_my_claims()

    def setup_notices_management(self, parent_frame):
        self.notices_tree = ttk.Treeview(parent_frame, columns=('通知编号', '标题', '发布时间', '有效期限'),
                                         show='headings')
        for col in self.notices_tree['columns']:
            self.notices_tree.heading(col, text=col)
            self.notices_tree.column(col, width=100)
        self.notices_tree.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        button_frame = ttk.Frame(parent_frame)
        button_frame.pack(pady=5)

        ttk.Button(button_frame, text="发布通知", command=self.create_notice).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="删除通知", command=self.delete_notice).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="刷新", command=self.refresh_notices).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="查看详情", command=self.view_notice_details).pack(side=tk.LEFT, padx=5)  # 添加查看详情按钮

        self.refresh_notices()

    def view_notice_details(self):
        selected_item = self.notices_tree.selection()
        if not selected_item:
            messagebox.showwarning("警告", "请先选择一个通知")
            return

        notice_id = self.notices_tree.item(selected_item, 'values')[0]
        try:
            self.cursor.execute("""
                   SELECT 通知编号, 标题, 发布时间, 有效期限, 内容
                   FROM 系统通知表
                   WHERE 通知编号 = %s
               """, (notice_id,))
            notice = self.cursor.fetchone()

            if notice:
                detail_window = tk.Toplevel(self.root)
                detail_window.title("通知详情")
                detail_window.geometry("400x300")

                content = f"编号: {notice['通知编号']}\n标题: {notice['标题']}\n发布时间: {notice['发布时间'].strftime('%Y-%m-%d %H:%M')}\n有效期限: {notice['有效期限'].strftime('%Y-%m-%d %H:%M') if notice['有效期限'] else '永久有效'}\n内容: {notice['内容']}"
                text_widget = tk.Text(detail_window, wrap=tk.WORD, width=50, height=15)
                text_widget.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
                text_widget.insert('1.0', content)
                text_widget.config(state='disabled')  # 禁止编辑文本

                # 关闭按钮
                ttk.Button(detail_window, text="关闭", command=detail_window.destroy).pack(pady=5)
            else:
                messagebox.showerror("错误", "未找到该通知的详细信息")
        except mysql.connector.Error as err:
            messagebox.showerror("数据库错误", str(err))

    def setup_notices_tab(self):
        # 创建表格视图
        columns = ('编号', '标题', '发布时间', '有效期限')
        self.notices_tree = ttk.Treeview(self.notices_tab, columns=columns, show='headings')

        for col in columns:
            self.notices_tree.heading(col, text=col)
            self.notices_tree.column(col, width=100, anchor='center')  # 设置列居中显示

        self.notices_tree.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        button_frame = ttk.Frame(self.notices_tab)
        button_frame.pack(pady=5)

        # 添加刷新按钮
        ttk.Button(button_frame, text="刷新", command=self.refresh_notices).pack(side=tk.LEFT, padx=5)

        # 添加查看详情按钮
        ttk.Button(button_frame, text="查看详情", command=self.view_notice_details).pack(side=tk.LEFT, padx=5)

    def view_notice_details(self):
        selected_item = self.notices_tree.selection()
        if not selected_item:
            messagebox.showwarning("警告", "请先选择一个通知")
            return

        # 获取选中通知的详细信息
        notice_id = self.notices_tree.item(selected_item, 'values')[0]
        try:
            self.cursor.execute("""
                        SELECT 通知编号, 标题, 发布时间, 有效期限, 内容
                        FROM 系统通知表
                        WHERE 通知编号 = %s
                    """, (notice_id,))
            notice = self.cursor.fetchone()

            if notice:
                # 显示通知详情
                detail_window = tk.Toplevel(self.root)
                detail_window.title("通知详情")
                detail_window.geometry("400x300")

                content = f"编号: {notice['通知编号']}\n标题: {notice['标题']}\n发布时间: {notice['发布时间'].strftime('%Y-%m-%d %H:%M')}\n有效期限: {notice['有效期限'].strftime('%Y-%m-%d %H:%M') if notice['有效期限'] else '永久有效'}\n内容: {notice['内容']}"
                text_widget = tk.Text(detail_window, wrap=tk.WORD, width=50, height=15)
                text_widget.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
                text_widget.insert('1.0', content)
                text_widget.config(state='disabled')  # 禁止编辑文本

                # 关闭按钮
                ttk.Button(detail_window, text="关闭", command=detail_window.destroy).pack(pady=5)
            else:
                messagebox.showerror("错误", "未找到该通知的详细信息")
        except mysql.connector.Error as err:
            messagebox.showerror("数据库错误", str(err))

    def refresh_notices(self):
        for item in self.notices_tree.get_children():
            self.notices_tree.delete(item)

        try:
            self.cursor.execute("""
               SELECT 通知编号, 标题, 发布时间, 有效期限
               FROM 系统通知表
               ORDER BY 发布时间 DESC
            """)
            for record in self.cursor.fetchall():
                self.notices_tree.insert('', 'end', values=(
                    record['通知编号'],
                    record['标题'],
                    record['发布时间'].strftime('%Y-%m-%d %H:%M') if record['发布时间'] else '',
                    record['有效期限'] if record['有效期限'] else '永久有效'
                ))
        except mysql.connector.Error as err:
            messagebox.showerror("错误", str(err))

    def insert_system_notice(self,notice_id, title, content, expiry_date):
        try:
            self.cursor.execute("""
                INSERT INTO 系统通知表 (通知编号, 标题, 内容, 有效期限)
                VALUES (%s, %s, %s, %s)
            """, (notice_id, title, content, expiry_date))
            self.conn.commit()
            messagebox.showinfo("成功", "通知发布成功")
        except mysql.connector.Error as err:
            messagebox.showerror("错误", str(err))

    def delete_system_notice(self, notice_id):
        try:
            self.cursor.execute("""
                DELETE FROM 系统通知表 WHERE 通知编号 = %s
            """, (notice_id,))
            self.conn.commit()
            messagebox.showinfo("成功", "通知删除成功")
        except mysql.connector.Error as err:
            messagebox.showerror("错误", str(err))

    def generate_notice_id(self):
        """生成唯一的通知编号"""
        self.last_notice_id += 1  # 递增编号
        return f"N{self.last_notice_id:03}"  # 格式化为N加上三位编号，不足的前面补零
    def create_notice(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("发布系统通知")
        dialog.geometry("400x300")

        ttk.Label(dialog, text="标题:").pack(pady=10)
        title_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=title_var).pack(pady=5)

        ttk.Label(dialog, text="内容:").pack(pady=10)
        content_var = tk.StringVar()
        text_widget = tk.Text(dialog, height=3, width=20)
        text_widget.pack(pady=5, padx=10)

        ttk.Label(dialog, text="有效期限 (YYYY-MM-DD):").pack(pady=10)
        expiry_date_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=expiry_date_var).pack(pady=5)

        def submit():
            title = title_var.get()
            content = content_var.get()
            expiry_date = expiry_date_var.get()
            if not title or not content:
                messagebox.showwarning("警告", "标题和内容不能为空")
                return
            try:
                notice_id = self.generate_notice_id()
                self.cursor.execute(self.insert_system_notice(notice_id, title, content, expiry_date))
                self.conn.commit()
                messagebox.showinfo("成功", "通知发布成功")
                dialog.destroy()
                self.refresh_notices()
            except mysql.connector.Error as err:
                messagebox.showerror("错误", str(err))

        ttk.Button(dialog, text="提交", command=submit).pack(pady=10)

    def delete_notice(self):
        selected = self.notices_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个通知")
            return

        notice_id = self.notices_tree.item(selected[0])['values'][0]

        try:
            self.cursor.execute(self.delete_system_notice(notice_id))
            self.conn.commit()
            messagebox.showinfo("成功", "通知删除成功")
            self.refresh_notices()
        except mysql.connector.Error as err:
            messagebox.showerror("错误", str(err))

    def refresh_notices(self):
        for item in self.notices_tree.get_children():
            self.notices_tree.delete(item)

        try:
            self.cursor.execute("""
                   SELECT 通知编号, 标题, 发布时间, 有效期限
                   FROM 系统通知表
                   ORDER BY 发布时间 DESC
               """)
            for record in self.cursor.fetchall():
                self.notices_tree.insert('', 'end', values=(
                    record['通知编号'],
                    record['标题'],
                    record['发布时间'].strftime('%Y-%m-%d %H:%M') if record['发布时间'] else '',
                    record['有效期限'] if record['有效期限'] else '永久有效'
                ))
        except mysql.connector.Error as err:
            messagebox.showerror("错误", str(err))

    def refresh_my_claims(self):
        for item in self.my_claims_tree.get_children():
            self.my_claims_tree.delete(item)
        
        try:
            self.cursor.execute("""
                SELECT r.认领编号, i.物品名称, r.认领时间, r.认领状态
                FROM 认领记录表 r
                JOIN 物品表 i ON r.物品编号 = i.物品编号
                WHERE r.认领人编号 = %s
                ORDER BY r.认领时间 DESC
            """, (self.current_user['用户编号'],))
            
            for record in self.cursor.fetchall():
                self.my_claims_tree.insert('', 'end', values=(
                    record['认领编号'],
                    record['物品名称'],
                    record['认领时间'].strftime('%Y-%m-%d %H:%M'),
                    record['认领状态']
                ))
        except mysql.connector.Error as err:
            messagebox.showerror("错误", str(err))
    
    def view_claim_detail(self):
        selected = self.my_claims_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一条认领记录")
            return
        
        claim_id = self.my_claims_tree.item(selected[0])['values'][0]
        
        try:
            # 获取认领详情
            self.cursor.execute("""
                SELECT r.认领编号, r.认领时间, r.认领状态,
                       i.物品名称, i.物品类别, i.物品描述, i.地点, i.时间,
                       u.用户姓名 as 发布人姓名
                FROM 认领记录表 r
                JOIN 物品表 i ON r.物品编号 = i.物品编号
                JOIN 用户表 u ON i.发布人编号 = u.用户编号
                WHERE r.认领编号 = %s
            """, (claim_id,))
            
            record = self.cursor.fetchone()
            if record:
                # 创建详情窗口
                detail_window = tk.Toplevel(self.root)
                detail_window.title("认领详情")
                detail_window.geometry("500x600")
                
                # 创建详情内容
                content = f"""
                认领编号：{record['认领编号']}
                认领时间：{record['认领时间'].strftime('%Y-%m-%d %H:%M')}
                认领状态：{record['认领状态']}
                
                物品信息：
                - 名称：{record['物品名称']}
                - 类别：{record['物品类别']}
                - 描述：{record['物品描述']}
                - 地点：{record['地点']}
                - 时间：{record['时间'].strftime('%Y-%m-%d %H:%M')}
                - 发布人：{record['发布人姓名']}
                """
                
                # 显示详情
                text_widget = tk.Text(detail_window, wrap=tk.WORD, width=50, height=25)
                text_widget.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
                text_widget.insert('1.0', content)
                
                # 获取所有相关投诉（包括其他用户的投诉）
                self.cursor.execute("""
                    SELECT c.投诉类型, c.投诉原因, c.处理状态, c.处理意见,
                           u.用户姓名 as 投诉人
                    FROM 投诉表 c
                    JOIN 用户表 u ON c.投诉人编号 = u.用户编号
                    WHERE c.认领编号 = %s
                    ORDER BY c.投诉时间 DESC
                """, (claim_id,))
                
                complaints = self.cursor.fetchall()
                if complaints:
                    complaint_text = "\n相关投诉记录：\n"
                    for complaint in complaints:
                        complaint_text += f"""
                        ----------------------------------------
                        投诉人：{complaint['投诉人']}
                        类型：{complaint['投诉类型']}
                        原因：{complaint['投诉原因']}
                        状态：{complaint['处理状态']}
                        """
                        if complaint['处理意见']:
                            complaint_text += f"管理员处理意见：{complaint['处理意见']}\n"
                    
                    text_widget.insert('end', complaint_text)
                
                text_widget.config(state='disabled')
                
                # 添加投诉按钮（如果是待处理状态）
                if record['认领状态'] == '待处理':
                    ttk.Button(detail_window, text="提交投诉", 
                             command=lambda: self.submit_complaint_from_detail(claim_id, detail_window)
                    ).pack(pady=5)
                
                # 关闭按钮
                ttk.Button(detail_window, text="关闭", command=detail_window.destroy).pack(pady=5)
                
        except mysql.connector.Error as err:
            messagebox.showerror("错误", str(err))
            
    def submit_complaint_from_detail(self, claim_id, parent_window):
        # 创建投诉对话框
        dialog = tk.Toplevel(parent_window)
        dialog.title("提交投诉")
        dialog.geometry("400x450")
        
        ttk.Label(dialog, text="投诉类型:").pack(pady=10)
        complaint_type = ttk.Combobox(dialog, values=['冒领', '虚假信息', '其他'])
        complaint_type.pack(pady=5)
        complaint_type.set('冒领')
        
        ttk.Label(dialog, text="投诉原因:").pack(pady=10)
        reason_text = tk.Text(dialog, height=10, width=40)
        reason_text.pack(pady=10, padx=10)
        
        def submit():
            if not complaint_type.get() or not reason_text.get("1.0", tk.END).strip():
                messagebox.showwarning("警告", "请填写完整投诉信息")
                return
                
            try:
                # 生成投诉编号
                complaint_id = f"T{datetime.datetime.now().strftime('%y%m%d%H%M')}"
                
                self.cursor.execute(
                    """
                    INSERT INTO 投诉表 (投诉编号, 认领编号, 投诉人编号, 投诉类型, 投诉原因, 投诉时间)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        complaint_id,
                        claim_id,
                        self.current_user['用户编号'],
                        complaint_type.get(),
                        reason_text.get("1.0", tk.END).strip(),
                        datetime.datetime.now()
                    )
                )
                self.conn.commit()
                messagebox.showinfo("成功", "投诉已提交")
                dialog.destroy()
                parent_window.destroy()  # 关闭详情窗口
                self.refresh_my_claims()  # 刷新列表
            except mysql.connector.Error as err:
                messagebox.showerror("错误", str(err))
                
        ttk.Button(dialog, text="提交", command=submit).pack(pady=10)
        
    def login(self):
        user_id = self.username_var.get()
        password = self.password_var.get()
        
        try:
            # 生成登录记录编号
            login_id = f"LG{datetime.datetime.now().strftime('%y%m%d%H%M%S')}"
            
            # 查询用户
            self.cursor.execute(
                """
                SELECT * FROM 用户表 
                WHERE 用户编号 = %s AND 登录密码 = %s
                """,
                (user_id, password)
            )
            user = self.cursor.fetchone()
            
            # 记录登录结果
            self.cursor.execute(
                """
                INSERT INTO 用户登录表 (登录编号, 用户编号, 登录时间, 登录状态)
                VALUES (%s, %s, %s, %s)
                """,
                (login_id, user_id, datetime.datetime.now(), '成功' if user else '失败')
            )
            self.conn.commit()
            
            if user:
                if user['账号状态']:
                    messagebox.showerror("错误", "该账号已被冻结")
                    return
                    
                self.current_user = user
                self.login_frame.grid_remove()
                self.create_main_frame()
            else:
                messagebox.showerror("错误", "用户名或密码错误")
        except mysql.connector.Error as err:
            messagebox.showerror("数据库错误", str(err))
            
    def show_register_frame(self):
        self.login_frame.grid_remove()
        
        # 创建注册框架
        self.register_frame = ttk.Frame(self.main_container)
        self.register_frame.grid(row=0, column=0)
        
        # 创建内容框架
        content_frame = ttk.Frame(self.register_frame, padding=20)
        content_frame.grid(row=0, column=0, padx=50, pady=30)
        
        # 标题
        ttk.Label(content_frame, text="用户注册", style='Title.TLabel').grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 注册字段
        fields = [
            ("用户姓名:", "用户姓名", "请输入真实姓名"),
            ("密码:", "登录密码", "请输入登录密码"),
            ("确认密码:", "确认密码", "请再次输入密码"),
            ("联系电话:", "联系电话", "请输入手机号码"),
            ("电子邮箱:", "电子邮箱", "请输入常用邮箱"),
            ("住址:", "住址", "请输入所在城市"),
            ("详细地址:", "详细地址", "请输入详细地址")
        ]
        
        self.register_vars = {}
        self.register_entries = {}
        
        for i, (label, var_name, placeholder) in enumerate(fields):
            # 标签
            ttk.Label(content_frame, text=label, font=('Microsoft YaHei UI', 10)).grid(
                row=i+1, column=0, padx=(0, 10), pady=5, sticky='e')
            
            # 输入框
            self.register_vars[var_name] = tk.StringVar()
            if var_name == "登录密码" or var_name == "确认密码":
                entry = ttk.Entry(content_frame, textvariable=self.register_vars[var_name], show="*", width=30)
            else:
                entry = ttk.Entry(content_frame, textvariable=self.register_vars[var_name], width=30)
            entry.grid(row=i+1, column=1, pady=5, sticky='w')
            
            # 存储Entry控件引用和占位符文本
            self.register_entries[var_name] = entry
            entry.placeholder = placeholder  # 将占位符保存为控件的属性
            
            # 添加占位符提示
            entry.insert(0, placeholder)
            entry.config(foreground='gray')
            
            # 绑定焦点事件
            entry.bind('<FocusIn>', lambda e, entry=entry: self.on_entry_focus_in(e, entry))
            entry.bind('<FocusOut>', lambda e, entry=entry: self.on_entry_focus_out(e, entry))
        
        # 按钮框架
        button_frame = ttk.Frame(content_frame)
        button_frame.grid(row=len(fields)+1, column=0, columnspan=2, pady=20)
        
        # 注册按钮
        ttk.Button(button_frame, text="注册", command=self.register, 
                  style='Custom.TButton', width=15).pack(side=tk.LEFT, padx=5)
        
        # 返回按钮
        ttk.Button(button_frame, text="返回登录", command=self.back_to_login,
                  style='Custom.TButton', width=15).pack(side=tk.LEFT, padx=5)
        
    def on_entry_focus_in(self, event, entry):
        if entry.get() == entry.placeholder:
            entry.delete(0, tk.END)
            entry.config(foreground='black')
            
    def on_entry_focus_out(self, event, entry):
        if entry.get() == '':
            entry.insert(0, entry.placeholder)
            entry.config(foreground='gray')
            
    def register(self):
        # 验证密码
        if self.register_vars["登录密码"].get() != self.register_vars["确认密码"].get():
            messagebox.showerror("错误", "两次输入的密码不一致")
            return

        # 验证必填字段
        required_fields = ["用户姓名", "登录密码", "联系电话"]
        for field in required_fields:
            value = self.register_vars[field].get()
            if not value or value.strip() == '':
                messagebox.showerror("错误", f"{field}不能为空")
                return

        try:
            # 准备用户数据
            user_data = {
                '用户姓名': self.register_vars["用户姓名"].get(),
                '登录密码': self.register_vars["登录密码"].get(),
                '住址': self.register_vars["住址"].get(),
                '联系电话': self.register_vars["联系电话"].get(),
                '电子邮箱': self.register_vars["电子邮箱"].get(),
                '详细地址': self.register_vars["详细地址"].get(),
                '用户类型': '普通用户'
            }

            # 对于非必填字段，如果值为空或只包含空白字符，则设置为空字符串
            for field in ['住址', '电子邮箱', '详细地址']:
                if not user_data[field] or user_data[field].strip() == '':
                    user_data[field] = ''

            # 调用注册函数
            new_user_id = register_user(user_data)  # 假设这个函数返回新注册用户的编号

            if new_user_id:
                messagebox.showinfo("成功", f"注册成功，您的用户编号是：{new_user_id}")
                self.back_to_login()
            else:
                messagebox.showerror("错误", "注册失败")
        except mysql.connector.Error as err:
            if err.errno == 1062:  # 重复键错误
                messagebox.showerror("错误", "该用户编号已被注册")
            else:
                messagebox.showerror("错误", str(err))
            
    def back_to_login(self):
        self.register_frame.grid_remove()
        self.login_frame.grid()
        
    def refresh_lost_items(self):
        for item in self.lost_items_tree.get_children():
            self.lost_items_tree.delete(item)
            
        try:
            self.cursor.execute("""
                SELECT 物品编号, 物品名称, 物品类别, 地点, 时间, 物品状态, 是否贵重
                FROM 物品表
                ORDER BY 时间 DESC
            """)
            for item in self.cursor.fetchall():
                self.lost_items_tree.insert('', 'end', values=(
                    item['物品编号'],
                    item['物品名称'],
                    item['物品类别'],
                    item['地点'],
                    item['时间'].strftime('%Y-%m-%d %H:%M'),
                    item['物品状态'],
                    '是' if item['是否贵重'] else '否'
                ))
        except mysql.connector.Error as err:
            messagebox.showerror("错误", str(err))
            
    def claim_item(self):
        selected = self.lost_items_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个物品")
            return
            
        item_id = self.lost_items_tree.item(selected[0])['values'][0]
        
        try:
            # 检查物品是否为贵重物品
            self.cursor.execute(
                "SELECT 是否贵重 FROM 物品表 WHERE 物品编号 = %s",
                (item_id,)
            )
            item = self.cursor.fetchone()
            
            if item and item['是否贵重']:
                # 创建认领说明对话框
                dialog = tk.Toplevel(self.root)
                dialog.title("贵重物品认领")
                dialog.geometry("400x300")
                
                ttk.Label(dialog, text="请填写认领说明：").pack(pady=10)
                
                # 认领说明文本框
                description_text = tk.Text(dialog, height=10, width=40)
                description_text.pack(pady=10, padx=10)
                
                def submit_claim():
                    description = description_text.get("1.0", tk.END).strip()
                    if not description:
                        messagebox.showwarning("警告", "请填写认领说明")
                        return
                        
                    self.submit_claim(item_id, description)
                    dialog.destroy()
                
                ttk.Button(dialog, text="提交", command=submit_claim).pack(pady=10)
            else:
                # 普通物品直接认领
                self.submit_claim(item_id)
                
        except mysql.connector.Error as err:
            messagebox.showerror("错误", str(err))
            
    def submit_claim(self, item_id, description=None):
        try:
            # 生成认领编号
            claim_id = f"C{datetime.datetime.now().strftime('%y%m%d%H%M')}"
            
            # 插入认领记录
            self.cursor.execute(
                """
                INSERT INTO 认领记录表 (认领编号, 物品编号, 认领人编号, 认领时间)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    claim_id,
                    item_id,
                    self.current_user['用户编号'],
                    datetime.datetime.now()
                )
            )
            
            # 如果是贵重物品，更新贵重单证表
            if description:
                self.cursor.execute(
                    """
                    UPDATE 贵重单证表
                    SET 备注 = CONCAT(IFNULL(备注, ''), '\n认领说明：', %s)
                    WHERE 物品编号 = %s
                    """,
                    (description, item_id)
                )
            
            self.conn.commit()
            messagebox.showinfo("成功", "认领申请已提交")
            self.refresh_lost_items()
        except mysql.connector.Error as err:
            messagebox.showerror("错误", str(err))
            
    def submit_report(self):
        try:
            # 生成物品编号
            item_id = f"L{datetime.datetime.now().strftime('%y%m%d%H%M')}"
            
            # 插入物品信息
            self.cursor.execute(
                """
                INSERT INTO 物品表 (物品编号, 物品名称, 物品类别, 物品描述, 地点, 时间, 发布人编号, 物品状态, 是否贵重)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    item_id,
                    self.report_vars['物品名称:'].get(),
                    self.report_vars['类别:'].get(),
                    self.report_vars['描述:'].get(),
                    self.report_vars['地点:'].get(),
                    datetime.datetime.strptime(self.report_vars['时间:'].get(), '%Y-%m-%d %H:%M'),
                    self.current_user['用户编号'],
                    self.report_type.get(),
                    self.is_valuable.get()
                )
            )
            
            # 如果是贵重物品，创建贵重单证
            if self.is_valuable.get():
                cert_id = f"G{datetime.datetime.now().strftime('%y%m%d%H%M')}"
                self.cursor.execute(
                    """
                    INSERT INTO 贵重单证表 (单证编号, 物品编号, 收据人编号, 登记时间)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (cert_id, item_id, self.current_user['用户编号'], datetime.datetime.now())
                )
            
            self.conn.commit()
            messagebox.showinfo("成功", "物品信息已提交")
            self.refresh_lost_items()
        except mysql.connector.Error as err:
            messagebox.showerror("错误", str(err))
        except ValueError:
            messagebox.showerror("错误", "时间格式错误，请使用 YYYY-MM-DD HH:MM 格式")
            
    def logout(self):
        self.current_user = None
        self.main_frame.destroy()
        self.create_login_frame()
        
    def setup_claims_management(self, parent_frame):
        # 创建认领管理界面
        columns = ('认领编号', '物品编号', '认领人', '认领时间', '状态')
        self.claims_tree = ttk.Treeview(parent_frame, columns=columns, show='headings')
        
        for col in columns:
            self.claims_tree.heading(col, text=col)
            self.claims_tree.column(col, width=100)
            
        self.claims_tree.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        button_frame = ttk.Frame(parent_frame)
        button_frame.pack(pady=5)
        
        ttk.Button(button_frame, text="通过", command=self.approve_claim).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="拒绝", command=self.reject_claim).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="标记冒领", command=self.mark_as_false_claim).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="刷新", command=self.refresh_claims).pack(side=tk.LEFT, padx=5)
        
        self.refresh_claims()
        
    def setup_complaints_management(self, parent_frame):
        # 创建投诉管理界面
        columns = ('投诉编号', '认领编号', '投诉人', '投诉类型', '投诉时间', '状态')
        self.complaints_tree = ttk.Treeview(parent_frame, columns=columns, show='headings')
        
        for col in columns:
            self.complaints_tree.heading(col, text=col)
            self.complaints_tree.column(col, width=100)
            
        self.complaints_tree.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        button_frame = ttk.Frame(parent_frame)
        button_frame.pack(pady=5)
        
        ttk.Button(button_frame, text="处理投诉", command=self.handle_complaint).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="刷新", command=self.refresh_complaints).pack(side=tk.LEFT, padx=5)
        
        self.refresh_complaints()
        
    def setup_users_management(self, parent_frame):
        # 创建用户管理界面
        columns = ('用户编号', '用户姓名', '联系电话', '电子邮箱', '账号状态', '违规次数')
        self.users_tree = ttk.Treeview(parent_frame, columns=columns, show='headings')
        
        for col in columns:
            self.users_tree.heading(col, text=col)
            self.users_tree.column(col, width=100)
            
        self.users_tree.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        button_frame = ttk.Frame(parent_frame)
        button_frame.pack(pady=5)
        
        ttk.Button(button_frame, text="查看详情", command=self.view_user_detail).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="冻结账号", command=self.freeze_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="解冻账号", command=self.unfreeze_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="刷新", command=self.refresh_users).pack(side=tk.LEFT, padx=5)
        
        self.refresh_users()
        
    def refresh_claims(self):
        for item in self.claims_tree.get_children():
            self.claims_tree.delete(item)
            
        try:
            self.cursor.execute("""
                SELECT r.认领编号, r.物品编号, u.用户姓名, r.认领时间, r.认领状态,
                       r.是否冒领
                FROM 认领记录表 r
                JOIN 用户表 u ON r.认领人编号 = u.用户编号
                ORDER BY r.认领时间 DESC
            """)
            for record in self.cursor.fetchall():
                status = record['认领状态']
                if record['是否冒领']:
                    status += '(冒领)'
                self.claims_tree.insert('', 'end', values=(
                    record['认领编号'],
                    record['物品编号'],
                    record['用户姓名'],
                    record['认领时间'].strftime('%Y-%m-%d %H:%M'),
                    status
                ))
        except mysql.connector.Error as err:
            messagebox.showerror("错误", str(err))
            
    def refresh_complaints(self):
        for item in self.complaints_tree.get_children():
            self.complaints_tree.delete(item)
            
        try:
            self.cursor.execute("""
                SELECT c.投诉编号, c.认领编号, u.用户姓名, c.投诉类型, c.投诉时间, c.处理状态
                FROM 投诉表 c
                JOIN 用户表 u ON c.投诉人编号 = u.用户编号
                ORDER BY c.投诉时间 DESC
            """)
            for record in self.cursor.fetchall():
                self.complaints_tree.insert('', 'end', values=(
                    record['投诉编号'],
                    record['认领编号'],
                    record['用户姓名'],
                    record['投诉类型'],
                    record['投诉时间'].strftime('%Y-%m-%d %H:%M'),
                    record['处理状态']
                ))
        except mysql.connector.Error as err:
            messagebox.showerror("错误", str(err))
            
    def refresh_users(self):
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
            
        try:
            self.cursor.execute("""
                SELECT 用户编号, 用户姓名, 联系电话, 电子邮箱, 账号状态, 违规次数
                FROM 用户表
                WHERE 用户类型 = '普通用户'
                ORDER BY 用户编号
            """)
            
            for user in self.cursor.fetchall():
                self.users_tree.insert('', 'end', values=(
                    user['用户编号'],
                    user['用户姓名'],
                    user['联系电话'],
                    user['电子邮箱'],
                    '已冻结' if user['账号状态'] else '正常',
                    user['违规次数']
                ))
        except mysql.connector.Error as err:
            messagebox.showerror("错误", str(err))
            
    def approve_claim(self):
        selected = self.claims_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个认领申请")
            return
            
        claim_id = self.claims_tree.item(selected[0])['values'][0]
        
        try:
            # 获取认领记录息
            self.cursor.execute(
                "SELECT 物品编号, 认领人编号 FROM 认领记录表 WHERE 认领编号 = %s",
                (claim_id,)
            )
            claim = self.cursor.fetchone()
            
            if claim:
                # 更新认领状态
                self.cursor.execute(
                    "UPDATE 认领记录表 SET 认领状态 = '已通过' WHERE 认领编号 = %s",
                    (claim_id,)
                )
                
                # 更新物品状态和认领人
                self.cursor.execute(
                    """
                    UPDATE 物品表 
                    SET 物品状态 = '已认领',
                        认领人编号 = %s
                    WHERE 物品编号 = %s
                    """,
                    (claim['认领人编号'], claim['物品编号'])
                )
                
                self.conn.commit()
                messagebox.showinfo("成功", "已通过认领申请")
                self.refresh_claims()
                self.refresh_lost_items()  # 刷新物品列表
        except mysql.connector.Error as err:
            messagebox.showerror("错误", str(err))
            
    def reject_claim(self):
        selected = self.claims_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个认领申请")
            return
            
        claim_id = self.claims_tree.item(selected[0])['values'][0]
        
        try:
            self.cursor.execute(
                "UPDATE 认领记录表 SET 认领状态 = '已拒绝' WHERE 认领编号 = %s",
                (claim_id,)
            )
            self.conn.commit()
            messagebox.showinfo("成功", "已拒绝认领申请")
            self.refresh_claims()
        except mysql.connector.Error as err:
            messagebox.showerror("错误", str(err))
            
    def handle_complaint(self):
        selected = self.complaints_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个投诉")
            return
            
        complaint_id = self.complaints_tree.item(selected[0])['values'][0]
        
        # 创建处理投诉的对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("处理投诉")
        dialog.geometry("400x300")
        
        ttk.Label(dialog, text="处理意见:").pack(pady=10)
        
        opinion_text = tk.Text(dialog, height=10, width=40)
        opinion_text.pack(pady=10, padx=10)
        
        def submit():
            opinion = opinion_text.get("1.0", tk.END).strip()
            if not opinion:
                messagebox.showwarning("警告", "请输入处理意见")
                return
                
            try:
                self.cursor.execute(
                    "UPDATE 投诉表 SET 处理意见 = %s, 处理状态 = '已处理' WHERE 投诉编号 = %s",
                    (opinion, complaint_id)
                )
                self.conn.commit()
                messagebox.showinfo("成功", "投诉已处理")
                dialog.destroy()
                self.refresh_complaints()
            except mysql.connector.Error as err:
                messagebox.showerror("错误", str(err))
                
        ttk.Button(dialog, text="提交", command=submit).pack(pady=10)
        
    def freeze_user(self):
        selected = self.users_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个用户")
            return
            
        user_id = self.users_tree.item(selected[0])['values'][0]
        
        try:
            self.cursor.execute(
                "UPDATE 用户表 SET 账号状态 = TRUE WHERE 用户编号 = %s",
                (user_id,)
            )
            self.conn.commit()
            messagebox.showinfo("成功", "已冻结用户账号")
            self.refresh_users()
        except mysql.connector.Error as err:
            messagebox.showerror("错误", str(err))
            
    def unfreeze_user(self):
        selected = self.users_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个用户")
            return
            
        user_id = self.users_tree.item(selected[0])['values'][0]
        
        try:
            self.cursor.execute(
                "UPDATE 用户表 SET 账号状态 = FALSE WHERE 用户编号 = %s",
                (user_id,)
            )
            self.conn.commit()
            messagebox.showinfo("成功", "已解冻用户账号")
            self.refresh_users()
        except mysql.connector.Error as err:
            messagebox.showerror("错误", str(err))
            
    def submit_complaint(self):
        selected = self.lost_items_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个物品")
            return
            
        item_id = self.lost_items_tree.item(selected[0])['values'][0]
        
        # 创建投诉对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("提交投诉")
        dialog.geometry("400x450")
        
        ttk.Label(dialog, text="投诉类型:").pack(pady=10)
        complaint_type = ttk.Combobox(dialog, values=['冒领', '虚假信息', '其他'])
        complaint_type.pack(pady=5)
        complaint_type.set('冒领')
        
        ttk.Label(dialog, text="投诉原因:").pack(pady=10)
        reason_text = tk.Text(dialog, height=10, width=40)
        reason_text.pack(pady=10, padx=10)
        
        def submit():
            if not complaint_type.get() or not reason_text.get("1.0", tk.END).strip():
                messagebox.showwarning("警告", "请填写完整投诉信息")
                return
                
            try:
                # 检查��否存在认领记录
                self.cursor.execute(
                    "SELECT 认领编号 FROM 认领记录表 WHERE 物品编号 = %s",
                    (item_id,)
                )
                claim_record = self.cursor.fetchone()
                
                if not claim_record:
                    messagebox.showwarning("警告", "该物品还没有认领记录，无法投诉")
                    return
                
                # 生成投诉编号
                complaint_id = f"T{datetime.datetime.now().strftime('%y%m%d%H%M')}"
                
                self.cursor.execute(
                    """
                    INSERT INTO 投诉表 (投诉编号, 认领编号, 投诉人编号, 投诉类型, 投诉原因, 投诉时间)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        complaint_id,
                        claim_record['认领编号'],
                        self.current_user['用户编号'],
                        complaint_type.get(),
                        reason_text.get("1.0", tk.END).strip(),
                        datetime.datetime.now()
                    )
                )
                self.conn.commit()
                messagebox.showinfo("成功", "投诉已提交")
                dialog.destroy()
            except mysql.connector.Error as err:
                messagebox.showerror("错误", str(err))
                
        ttk.Button(dialog, text="提交", command=submit).pack(pady=10)

    def setup_profile_tab(self):
        # 创建个人信息表单
        form_frame = ttk.Frame(self.profile_tab)
        form_frame.pack(pady=20, padx=20)
        
        # 获取用户信息
        self.cursor.execute(
            "SELECT * FROM 用户表 WHERE 用户编号 = %s",
            (self.current_user['用户编号'],)
        )
        user_info = self.cursor.fetchone()
        
        # 创建输入字段
        self.profile_vars = {}
        fields = [
            ("用户姓名", "用户姓名"),
            ("住址", "住址"),
            ("联系电话", "联系电话"),
            ("电子邮箱", "电子邮箱"),
            ("详细地址", "详细地址")
        ]
        
        for i, (label, field) in enumerate(fields):
            ttk.Label(form_frame, text=f"{label}:").grid(row=i, column=0, pady=5, padx=5, sticky='e')
            self.profile_vars[field] = tk.StringVar(value=user_info[field])
            ttk.Entry(form_frame, textvariable=self.profile_vars[field]).grid(row=i, column=1, pady=5, padx=5)
        
        # 修改密码部分
        ttk.Label(form_frame, text="新密码:").grid(row=len(fields), column=0, pady=5, padx=5, sticky='e')
        self.new_password_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.new_password_var, show="*").grid(row=len(fields), column=1, pady=5, padx=5)
        
        # 保存按钮
        ttk.Button(form_frame, text="保存修改", command=self.save_profile).grid(row=len(fields)+1, column=0, columnspan=2, pady=20)
        
    def save_profile(self):
        try:
            # 更新基本信息
            update_query = """
                UPDATE 用户表 
                SET 用户姓名 = %s, 住址 = %s, 联系电话 = %s, 电子邮箱 = %s, 详细地址 = %s
                WHERE 用户编号 = %s
            """
            self.cursor.execute(update_query, (
                self.profile_vars["用户姓名"].get(),
                self.profile_vars["住址"].get(),
                self.profile_vars["联系电话"].get(),
                self.profile_vars["电子邮箱"].get(),
                self.profile_vars["详细地址"].get(),
                self.current_user['用户编号']
            ))
            
            # 如果输入了新密码，则更新密码
            if self.new_password_var.get():
                self.cursor.execute(
                    "UPDATE 用户表 SET 登录密码 = %s WHERE 用户编号 = %s",
                    (self.new_password_var.get(), self.current_user['用户编号'])
                )
            
            self.conn.commit()
            messagebox.showinfo("成功", "个人信息已更新")
            
            # 更新当前用户信息
            self.cursor.execute(
                "SELECT * FROM 用户表 WHERE 用户编号 = %s",
                (self.current_user['用户编号'],)
            )
            self.current_user = self.cursor.fetchone()
            
        except mysql.connector.Error as err:
            messagebox.showerror("错误", str(err))

    def mark_as_false_claim(self):
        selected = self.claims_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个认领申请")
            return
            
        claim_id = self.claims_tree.item(selected[0])['values'][0]
        
        try:
            # 标记为冒领
            self.cursor.execute(
                "UPDATE 认领记录表 SET 是否冒领 = TRUE, 认领状态 = '已拒绝' WHERE 认领编号 = %s",
                (claim_id,)
            )
            
            # 获取认领人信息
            self.cursor.execute("""
                SELECT 认领人编号
                FROM 认领记录表
                WHERE 认领编号 = %s
            """, (claim_id,))
            claimer = self.cursor.fetchone()
            
            # 更新用户违规次数
            if claimer:
                self.cursor.execute("""
                    UPDATE 用户表 
                    SET 违规次数 = 违规次数 + 1,
                        加入失信名单时间 = CASE 
                            WHEN 违规次数 >= 2 THEN %s
                            ELSE 加入失信名单时间
                        END,
                        账号状态 = CASE 
                            WHEN 违规次数 >= 2 THEN TRUE
                            ELSE 账号状态
                        END
                    WHERE 用户编号 = %s
                """, (datetime.datetime.now(), claimer['认领人编号']))
            
            self.conn.commit()
            messagebox.showinfo("成功", "已标记为冒领并更新用户违规记录")
            self.refresh_claims()
            self.refresh_blacklist()
        except mysql.connector.Error as err:
            messagebox.showerror("错误", str(err))

    def view_item_detail(self):
        selected = self.lost_items_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个物品")
            return
            
        item_id = self.lost_items_tree.item(selected[0])['values'][0]
        
        try:
            # 获取物品详情
            self.cursor.execute("""
                SELECT i.*, u.用户姓名 as 发布人姓名,
                       r.认领编号, r.认领状态,
                       c.用户姓名 as 认领人姓名
                FROM 物品表 i
                JOIN 用户表 u ON i.发布人编号 = u.用户编号
                LEFT JOIN 认领记录表 r ON i.物品编号 = r.物品编号
                LEFT JOIN 用户表 c ON r.认领人编号 = c.用户编号
                WHERE i.物品编号 = %s
            """, (item_id,))
            item = self.cursor.fetchone()
            
            if item:
                # 如果是贵重物品，获取贵重单证信息
                cert_info = ""
                if item['是否贵重']:
                    self.cursor.execute("""
                        SELECT *
                        FROM 贵重单证表
                        WHERE 物品编号 = %s
                    """, (item_id,))
                    cert = self.cursor.fetchone()
                    if cert:
                        cert_info = f"""
                        贵重单证信息：
                        - 单证编号：{cert['单证编号']}
                        - 登记时间：{cert['登记时间'].strftime('%Y-%m-%d %H:%M')}
                        - 备注：{cert['备注'] if cert['备注'] else '无'}
                        """
                
                # 获取投诉信息
                complaint_info = ""
                if item['认领编号']:
                    self.cursor.execute("""
                        SELECT c.*, u.用户姓名 as 投诉人姓名
                        FROM 投诉表 c
                        JOIN 用户表 u ON c.投诉人编号 = u.用户编号
                        WHERE c.认领编号 = %s
                        ORDER BY c.投诉时间 DESC
                    """, (item['认领编号'],))
                    complaints = self.cursor.fetchall()
                    if complaints:
                        complaint_info = "\n投诉记录：\n"
                        for complaint in complaints:
                            complaint_info += f"""
                            投诉人：{complaint['投诉人姓名']}
                            类型：{complaint['投诉类型']}
                            原因：{complaint['投诉原因']}
                            状态：{complaint['处理状态']}
                            """
                            if complaint['处理意见']:
                                complaint_info += f"处理意见：{complaint['处理意见']}\n"
                
                # 创建详情窗口
                detail_window = tk.Toplevel(self.root)
                detail_window.title("物品详情")
                detail_window.geometry("500x600")
                
                # 创建详情内容
                content = f"""
                物品编号：{item['物品编号']}
                物品称：{item['物品名称']}
                物品类别：{item['物品类别']}
                物品描述：{item['物品描述']}
                地点：{item['地点']}
                时间：{item['时间'].strftime('%Y-%m-%d %H:%M')}
                状态：{item['物品状态']}
                是否贵重：{'是' if item['是否贵重'] else '否'}
                发布人：{item['发布人姓名']}
                
                认领状态：{item['认领状态'] if item['认领状态'] else '未认领'}
                认领人：{item['认领人姓名'] if item['认领人姓名'] else '无'}
                {cert_info}
                {complaint_info}
                """
                
                # 显示详情
                text_widget = tk.Text(detail_window, wrap=tk.WORD, width=50, height=25)
                text_widget.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
                text_widget.insert('1.0', content)
                text_widget.config(state='disabled')
                
                # 添加按钮框架
                button_frame = ttk.Frame(detail_window)
                button_frame.pack(pady=5)
                
                # 认领按钮
                if not item['认领状态'] or item['认领状态'] == '已拒绝':
                    ttk.Button(button_frame, text="认领", 
                             command=lambda: self.claim_item_from_detail(item_id, detail_window)
                    ).pack(side=tk.LEFT, padx=5)
                
                # 投诉按钮（只有在物品已被认领时才显示）
                if item['认领状态'] == '已通过':
                    ttk.Button(button_frame, text="投诉", 
                             command=lambda: self.submit_complaint_from_detail(item['认领编号'], detail_window)
                    ).pack(side=tk.LEFT, padx=5)
                
                # 关闭按钮
                ttk.Button(button_frame, text="关闭", 
                          command=detail_window.destroy
                ).pack(side=tk.LEFT, padx=5)
                
        except mysql.connector.Error as err:
            messagebox.showerror("错误", str(err))
            
    def claim_item_from_detail(self, item_id, parent_window):
        """从详情页面发起认领"""
        try:
            # 检查物品是否为贵重物品
            self.cursor.execute(
                "SELECT 是否贵重 FROM 物品表 WHERE 物品编号 = %s",
                (item_id,)
            )
            item = self.cursor.fetchone()
            
            if item and item['是否贵重']:
                # 创建认领说明对话框
                dialog = tk.Toplevel(parent_window)
                dialog.title("贵重物品认领")
                dialog.geometry("400x300")
                
                ttk.Label(dialog, text="请填写认领说明：").pack(pady=10)
                
                # 认领说明文本框
                description_text = tk.Text(dialog, height=10, width=40)
                description_text.pack(pady=10, padx=10)
                
                def submit():
                    description = description_text.get("1.0", tk.END).strip()
                    if not description:
                        messagebox.showwarning("警告", "请填写认领说明")
                        return
                        
                    self.submit_claim(item_id, description)
                    dialog.destroy()
                    parent_window.destroy()
                
                ttk.Button(dialog, text="提交", command=submit).pack(pady=10)
            else:
                # 普通物品直接认领
                self.submit_claim(item_id)
                parent_window.destroy()
                
        except mysql.connector.Error as err:
            messagebox.showerror("错误", str(err))

    def setup_blacklist_management(self, parent_frame):
        # 创建失信名单表格
        columns = ('用户编号', '用户姓名', '违规次数', '加入时间', '状态')
        self.blacklist_tree = ttk.Treeview(parent_frame, columns=columns, show='headings')
        
        for col in columns:
            self.blacklist_tree.heading(col, text=col)
            self.blacklist_tree.column(col, width=100)
            
        self.blacklist_tree.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        button_frame = ttk.Frame(parent_frame)
        button_frame.pack(pady=5)

        ttk.Button(button_frame, text="加入失信名单", command=self.add_to_blacklist).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="移出失信名单", command=self.remove_from_blacklist).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="刷新", command=self.refresh_blacklist).pack(side=tk.LEFT, padx=5)
        
        self.refresh_blacklist()
        
    def refresh_blacklist(self):
        for item in self.blacklist_tree.get_children():
            self.blacklist_tree.delete(item)
            
        try:
            self.cursor.execute("""
                SELECT 用户编号, 用户姓名, 违规次数, 加入失信名单时间, 账号状态
                FROM 用户表
                WHERE 加入失信名单时间 IS NOT NULL
                ORDER BY 违规次数 DESC, 加入失信名单时间 DESC
            """)
            
            for user in self.cursor.fetchall():
                self.blacklist_tree.insert('', 'end', values=(
                    user['用户编号'],
                    user['用户姓名'],
                    user['违规次数'],
                    user['加入失信名单时间'].strftime('%Y-%m-%d %H:%M') if user['加入失信名单时间'] else '',
                    '已冻结' if user['账号状态'] else '正常'
                ))
        except mysql.connector.Error as err:
            messagebox.showerror("错误", str(err))
            
    def add_to_blacklist(self):
        selected = self.users_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个用户")
            return
            
        user_id = self.users_tree.item(selected[0])['values'][0]
        
        try:
            # 更新用户违规次数和失信名单状态
            self.cursor.execute("""
                UPDATE 用户表 
                SET 违规次数 = 违规次数 + 1,
                    加入失信名单时间 = CASE 
                        WHEN 加入失信名单时间 IS NULL THEN %s
                        ELSE 加入失信名单时间
                    END,
                    账号状态 = TRUE
                WHERE 用户编号 = %s
            """, (datetime.datetime.now(), user_id))
            
            self.conn.commit()
            messagebox.showinfo("成功", "已将用户加入失信名单")
            self.refresh_users()
            self.refresh_blacklist()
        except mysql.connector.Error as err:
            messagebox.showerror("错误", str(err))
            
    def remove_from_blacklist(self):
        selected = self.blacklist_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个用户")
            return
            
        user_id = self.blacklist_tree.item(selected[0])['values'][0]
        
        try:
            # 更新用户状态
            self.cursor.execute("""
                UPDATE 用户表 
                SET 加入失信名单时间 = NULL,
                    账号状态 = FALSE
                WHERE 用户编号 = %s
            """, (user_id,))
            
            self.conn.commit()
            messagebox.showinfo("成功", "已将用户移出失信名单")
            self.refresh_users()
            self.refresh_blacklist()
        except mysql.connector.Error as err:
            messagebox.showerror("错误", str(err))

    def view_user_detail(self):
        selected = self.users_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个用户")
            return
            
        user_id = self.users_tree.item(selected[0])['values'][0]
        
        try:
            # 获取用户详细信息
            self.cursor.execute("""
                SELECT *
                FROM 用户表
                WHERE 用户编号 = %s
            """, (user_id,))
            user = self.cursor.fetchone()
            
            if user:
                # 获取用户的认领记录
                self.cursor.execute("""
                    SELECT r.*, i.物品名称
                    FROM 认领记录表 r
                    JOIN 物品表 i ON r.物品编号 = i.物品编号
                    WHERE r.认领人编号 = %s
                    ORDER BY r.认领时间 DESC
                """, (user_id,))
                claims = self.cursor.fetchall()
                
                # 获取用户的投诉记录
                self.cursor.execute("""
                    SELECT *
                    FROM 投诉表
                    WHERE 投诉人编号 = %s
                    ORDER BY 投诉时间 DESC
                """, (user_id,))
                complaints = self.cursor.fetchall()
                
                # 创建详情窗口
                detail_window = tk.Toplevel(self.root)
                detail_window.title("用户详情")
                detail_window.geometry("500x600")
                
                # 创建详情内容
                content = f"""
                用户信息：
                - 用户编号：{user['用户编号']}
                - 用户姓名：{user['用户姓名']}
                - 联系电话：{user['联系电话']}
                - 电子邮箱：{user['电子邮箱']}
                - 住址：{user['住址']}
                - 详细地址：{user['详细地址']}
                - 账号状态：{'已冻结' if user['账号状态'] else '正常'}
                - 违规次数：{user['违规次数']}
                - 加入失信名单时间：{user['加入失信名单时间'].strftime('%Y-%m-%d %H:%M') if user['加入失信名单时间'] else '无'}
                
                认领记录：
                """
                
                if claims:
                    for claim in claims:
                        content += f"""
                        - 物品：{claim['物品名称']}
                          时间：{claim['认领时间'].strftime('%Y-%m-%d %H:%M')}
                          状态：{claim['认领状态']}
                          {'(冒领)' if claim['是否冒领'] else ''}
                        """
                else:
                    content += "无认领记录\n"
                
                content += "\n投诉记录：\n"
                if complaints:
                    for complaint in complaints:
                        content += f"""
                        - 类型：{complaint['投诉类型']}
                          原因：{complaint['投诉原因']}
                          时间：{complaint['投诉时间'].strftime('%Y-%m-%d %H:%M')}
                          状态：{complaint['处理状态']}
                        """
                else:
                    content += "无投诉记录"
                
                # 显示详情
                text_widget = tk.Text(detail_window, wrap=tk.WORD, width=50, height=25)
                text_widget.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
                text_widget.insert('1.0', content)
                text_widget.config(state='disabled')
                
                # 关闭按钮
                ttk.Button(detail_window, text="关闭", command=detail_window.destroy).pack(pady=10)
                
        except mysql.connector.Error as err:
            messagebox.showerror("错误", str(err))

if __name__ == "__main__":
    root = tk.Tk()
    app = LostAndFoundApp(root)
    root.mainloop() 
    root.mainloop() 