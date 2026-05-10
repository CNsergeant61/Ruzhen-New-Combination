import tkinter as tk
from tkinter import ttk, messagebox
from backend import VocabManager

class VocabApp:
    def __init__(self, root):
        self.root = root
        self.root.title("我的专属单词本 - 完整版")
        self.root.geometry("550x500") # 稍微调大了窗口以适应表格
        
        self.manager = VocabManager()
        self.quiz_data = []
        self.current_q_index = 0
        
        self.create_widgets()

    def create_widgets(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # ==========================================
        # 标签页 1：录入新词
        # ==========================================
        # ==========================================
        # 标签页 1：录入新词 (修改版)
        # ==========================================
        self.add_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.add_frame, text=" 📝 录入新词 ")
        
        ttk.Label(self.add_frame, text="英文单词:", font=("Microsoft YaHei", 12)).pack(pady=(30, 5))
        
        # 把输入框和翻译按钮放在同一行
        en_input_frame = ttk.Frame(self.add_frame)
        en_input_frame.pack(pady=5)
        self.en_entry = ttk.Entry(en_input_frame, font=("Arial", 12), width=20)
        self.en_entry.pack(side='left', padx=5)
        # 【新增的翻译按钮】绑定到了 self.auto_translate 函数
        ttk.Button(en_input_frame, text="✨ 自动翻译", command=self.auto_translate).pack(side='left')
        
        ttk.Label(self.add_frame, text="中文释义:", font=("Microsoft YaHei", 12)).pack(pady=(10, 5))
        self.cn_entry = ttk.Entry(self.add_frame, font=("Microsoft YaHei", 12), width=30)
        self.cn_entry.pack(pady=5)
        
        ttk.Button(self.add_frame, text="保存单词", command=self.save_word).pack(pady=20)
        self.status_label = ttk.Label(self.add_frame, text="")
        self.status_label.pack(pady=5)
        
        # ==========================================
        # 标签页 2：单词测试
        # ==========================================
        self.quiz_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.quiz_frame, text=" 🎯 单词测试 ")
        
        self.word_label = ttk.Label(self.quiz_frame, text="点击下方按钮开始", font=("Arial", 18, "bold"))
        self.word_label.pack(pady=(30, 20))
        
        self.option_buttons = []
        for i in range(4):
            btn = ttk.Button(self.quiz_frame, text=f"选项 {i+1}", command=lambda idx=i: self.check_answer(idx))
            btn.pack(fill='x', padx=60, pady=5)
            btn.state(['disabled'])
            self.option_buttons.append(btn)
            
        self.start_btn = ttk.Button(self.quiz_frame, text="生成新测试 (5题)", command=self.start_quiz)
        self.start_btn.pack(pady=20)
        self.progress_label = ttk.Label(self.quiz_frame, text="")
        self.progress_label.pack(pady=5)

        # ==========================================
        # 标签页 3：词库管理 (本次新增核心)
        # ==========================================
        self.manage_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.manage_frame, text=" ⚙️ 词库管理 ")

        # 3.1 表格展示区
        columns = ("en", "cn")
        self.tree = ttk.Treeview(self.manage_frame, columns=columns, show="headings", height=10)
        self.tree.heading("en", text="英文单词")
        self.tree.heading("cn", text="中文释义")
        self.tree.column("en", width=200, anchor='center')
        self.tree.column("cn", width=250, anchor='center')
        self.tree.pack(fill='both', expand=True, padx=10, pady=(10, 5))
        
        # 绑定表格行点击事件
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

        # 3.2 底部编辑区 (默认禁用，选中表格行后启用)
        self.edit_frame = ttk.LabelFrame(self.manage_frame, text="编辑选中单词")
        self.edit_frame.pack(fill='x', padx=10, pady=10)
        
        # 记录被选中的“原单词”，防止用户修改英文拼写时找不到原数据
        self.selected_old_word = tk.StringVar() 

        ttk.Label(self.edit_frame, text="英文:").grid(row=0, column=0, padx=5, pady=5)
        self.edit_en_entry = ttk.Entry(self.edit_frame, width=20)
        self.edit_en_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.edit_frame, text="中文:").grid(row=0, column=2, padx=5, pady=5)
        self.edit_cn_entry = ttk.Entry(self.edit_frame, width=20)
        self.edit_cn_entry.grid(row=0, column=3, padx=5, pady=5)

        btn_frame = ttk.Frame(self.edit_frame)
        btn_frame.grid(row=1, column=0, columnspan=4, pady=10)
        
        ttk.Button(btn_frame, text="保存修改", command=self.update_word).pack(side='left', padx=10)
        ttk.Button(btn_frame, text="删除此词", command=self.delete_word).pack(side='left', padx=10)
        ttk.Button(btn_frame, text="刷新列表", command=self.refresh_manage_list).pack(side='right', padx=10)

        # 程序启动时，自动加载一次表格数据
        self.refresh_manage_list()

    # ==========================================
    # 交互逻辑：录入与测试 (原有逻辑)
    # ==========================================
    def save_word(self):
        en = self.en_entry.get()
        cn = self.cn_entry.get()
        success, msg = self.manager.add_word(en, cn)
        if success:
            self.status_label.config(text=msg, foreground="green")
            self.en_entry.delete(0, tk.END)
            self.cn_entry.delete(0, tk.END)
            self.refresh_manage_list() # 录入新词后自动更新管理页面的表格
        else:
            self.status_label.config(text=msg, foreground="red")
    
    # 【新增功能】点击自动翻译按钮的逻辑
    def auto_translate(self):
        en_word = self.en_entry.get()
        
        # 给用户一点等待提示
        self.status_label.config(text="正在联网翻译中...", foreground="blue")
        self.root.update() # 强制刷新界面显示提示
        
        # 调用后端翻译功能
        success, result = self.manager.fetch_translation(en_word)
        
        if success:
            # 翻译成功：清空现有的中文输入框，把翻译结果填进去
            self.cn_entry.delete(0, tk.END)
            self.cn_entry.insert(0, result)
            self.status_label.config(text="翻译成功！你可以核对后点击保存。", foreground="green")
        else:
            # 翻译失败：弹窗报错
            self.status_label.config(text="")
            messagebox.showerror("翻译出错", result)

    def start_quiz(self):
        success, result = self.manager.generate_quiz(num_questions=5)
        if not success:
            messagebox.showerror("错误", result)
            return
        self.quiz_data = result
        self.current_q_index = 0
        self.load_question()
        
    def load_question(self):
        if self.current_q_index >= len(self.quiz_data):
            messagebox.showinfo("测试结束", "测试完成！")
            self.word_label.config(text="测试完成！")
            for btn in self.option_buttons:
                btn.config(text="-")
                btn.state(['disabled'])
            self.progress_label.config(text="")
            return
        q = self.quiz_data[self.current_q_index]
        self.word_label.config(text=q["word"])
        for i in range(4):
            self.option_buttons[i].config(text=q["options"][i])
            self.option_buttons[i].state(['!disabled'])
        self.progress_label.config(text=f"当前进度: {self.current_q_index + 1} / {len(self.quiz_data)}")

    def check_answer(self, selected_index):
        q = self.quiz_data[self.current_q_index]
        if q["options"][selected_index] == q["answer"]:
            self.current_q_index += 1
            self.load_question()
        else:
            messagebox.showerror("选错啦", f"正确答案应该是：【{q['answer']}】\n\n请再试一次！")

    # ==========================================
    # 交互逻辑：词库管理 (新增逻辑)
    # ==========================================
    def refresh_manage_list(self):
        """清空现有表格，并重新从后端拉取数据填充"""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        all_words = self.manager.get_all_words()
        for en, cn in all_words.items():
            # 将数据插入表格
            self.tree.insert("", tk.END, values=(en, cn))
            
        # 清空底部的输入框
        self.edit_en_entry.delete(0, tk.END)
        self.edit_cn_entry.delete(0, tk.END)
        self.selected_old_word.set("")

    def on_tree_select(self, event):
        """当用户点击表格的某一行时触发"""
        selected_items = self.tree.selection()
        if not selected_items:
            return
            
        # 获取选中的第一行数据
        item = selected_items[0]
        word_values = self.tree.item(item, "values")
        
        # 将数据填入底部的编辑框中
        self.edit_en_entry.delete(0, tk.END)
        self.edit_en_entry.insert(0, word_values[0])
        
        self.edit_cn_entry.delete(0, tk.END)
        self.edit_cn_entry.insert(0, word_values[1])
        
        # 记住被点选的原始英文单词（作为修改和删除的凭据）
        self.selected_old_word.set(word_values[0])

    def update_word(self):
        """处理修改操作"""
        old_word = self.selected_old_word.get()
        new_en = self.edit_en_entry.get()
        new_cn = self.edit_cn_entry.get()
        
        if not old_word:
            messagebox.showwarning("提示", "请先在表格中选择要修改的单词！")
            return
            
        success, msg = self.manager.edit_word(old_word, new_en, new_cn)
        if success:
            messagebox.showinfo("成功", msg)
            self.refresh_manage_list() # 刷新表格
        else:
            messagebox.showerror("错误", msg)

    def delete_word(self):
        """处理删除操作"""
        target_word = self.selected_old_word.get()
        if not target_word:
            messagebox.showwarning("提示", "请先在表格中选择要删除的单词！")
            return
            
        # 弹出确认对话框
        if messagebox.askyesno("确认", f"确定要删除单词 '{target_word}' 吗？"):
            if self.manager.delete_word(target_word):
                self.refresh_manage_list()
            else:
                messagebox.showerror("错误", "删除失败，找不到该单词。")

if __name__ == "__main__":
    root = tk.Tk()
    app = VocabApp(root)
    root.mainloop()