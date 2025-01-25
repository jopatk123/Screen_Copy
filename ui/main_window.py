import tkinter as tk
from tkinter import ttk
import webbrowser
from config.settings import Settings

class MainWindow:
    def __init__(self, screenshot_callback=None, hotkey_callback=None):
        self.settings = Settings()
        self.screenshot_callback = screenshot_callback
        self.hotkey_callback = hotkey_callback
        self.window = None
        self.hotkey_var = None
        
    def setup_window(self):
        """设置主窗口"""
        self.window = tk.Tk()
        self.window.title("屏幕文字识别工具")
        self.window.geometry("600x500")
        self.window.resizable(True, True)
        
        # 设置窗口样式
        style = ttk.Style()
        style.configure('Custom.TButton',
                       padding=10,
                       font=('Microsoft YaHei', 10))
        
        # 创建主框架
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 添加标题
        title_label = ttk.Label(
            main_frame,
            text="屏幕文字识别工具",
            font=('Microsoft YaHei', 18, 'bold')
        )
        title_label.pack(pady=20)
        
        # 添加说明文本
        desc_text = """
使用说明：
1. 点击"开始截图"或按快捷键 {} 开始截图
2. 鼠标框选要识别的区域
3. 点击确认或取消按钮
4. 识别的文字会自动复制到剪贴板
        """.format(self.settings.SCREENSHOT_HOTKEY)
        
        desc_label = ttk.Label(
            main_frame,
            text=desc_text,
            justify=tk.LEFT,
            wraplength=500,
            font=('Microsoft YaHei', 11)
        )
        desc_label.pack(pady=20)
        
        # 添加按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        # 设置按钮
        settings_button = ttk.Button(
            button_frame,
            text="快捷键设置",
            style='Custom.TButton',
            command=self.show_settings_dialog
        )
        settings_button.pack(padx=10)
        
        # 添加底部信息
        footer_frame = ttk.Frame(main_frame)
        footer_frame.pack(side=tk.BOTTOM, pady=10)
        
        footer_text = ttk.Label(
            footer_frame,
            text="Powered by Baidu OCR",
            cursor="hand2",
            foreground="blue",
            font=('Microsoft YaHei', 10)
        )
        footer_text.pack()
        
        # 添加链接点击事件
        footer_text.bind("<Button-1>", lambda e: webbrowser.open("https://ai.baidu.com/tech/ocr"))
            
        # 处理窗口关闭事件
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def show_settings_dialog(self):
        """显示设置对话框"""
        settings_dialog = tk.Toplevel(self.window)
        settings_dialog.title("快捷键设置")
        settings_dialog.geometry("400x250")  # 增加一点高度以适应按钮
        settings_dialog.resizable(False, False)
        settings_dialog.transient(self.window)
        settings_dialog.grab_set()
        
        # 创建设置框架
        settings_frame = ttk.Frame(settings_dialog, padding="20")
        settings_frame.pack(fill=tk.BOTH, expand=True)
        
        # 快捷键设置
        hotkey_label = ttk.Label(
            settings_frame,
            text="截图快捷键:",
            font=('Microsoft YaHei', 10)
        )
        hotkey_label.pack(pady=10)
        
        self.hotkey_var = tk.StringVar(value=self.settings.SCREENSHOT_HOTKEY)
        hotkey_entry = ttk.Entry(
            settings_frame,
            textvariable=self.hotkey_var,
            width=20,
            font=('Microsoft YaHei', 10)
        )
        hotkey_entry.pack(pady=5)
        
        # 说明文本
        hint_label = ttk.Label(
            settings_frame,
            text="提示：输入格式如 'Ctrl+Alt+A'",
            font=('Microsoft YaHei', 9),
            foreground='gray'
        )
        hint_label.pack(pady=5)
        
        # 按钮框架
        button_frame = ttk.Frame(settings_frame)
        button_frame.pack(pady=20)
        
        # 保存按钮
        save_button = ttk.Button(
            button_frame,
            text="保存",
            style='Custom.TButton',
            command=lambda: self.save_settings(settings_dialog)
        )
        save_button.pack(side=tk.LEFT, padx=10)
        
        # 取消按钮
        cancel_button = ttk.Button(
            button_frame,
            text="取消",
            style='Custom.TButton',
            command=settings_dialog.destroy
        )
        cancel_button.pack(side=tk.LEFT, padx=10)
        
    def save_settings(self, dialog):
        """保存设置"""
        new_hotkey = self.hotkey_var.get()
        if new_hotkey and new_hotkey != self.settings.SCREENSHOT_HOTKEY:
            self.settings.SCREENSHOT_HOTKEY = new_hotkey
            self.settings.save()
            
            # 更新主窗口的说明文本
            desc_text = """
使用说明：
1. 点击"开始截图"或按快捷键 {} 开始截图
2. 鼠标框选要识别的区域
3. 点击确认或取消按钮
4. 识别的文字会自动复制到剪贴板
            """.format(self.settings.SCREENSHOT_HOTKEY)
            
            # 找到并更新说明标签的文本
            for child in self.window.winfo_children():
                if isinstance(child, ttk.Frame):
                    for frame_child in child.winfo_children():
                        if isinstance(frame_child, ttk.Label) and frame_child.cget("wraplength") == 500:
                            frame_child.configure(text=desc_text)
                            break
            
            # 重新注册热键
            if self.hotkey_callback:
                self.hotkey_callback()
        
        dialog.destroy()
        
    def on_screenshot(self):
        """截图按钮点击回调"""
        if self.screenshot_callback:
            self.window.withdraw()  # 隐藏窗口
            self.screenshot_callback()
            self.window.deiconify()  # 恢复窗口
            
    def on_closing(self):
        """窗口关闭回调"""
        self.window.withdraw()  # 隐藏窗口而不是关闭
        
    def show(self):
        """显示窗口"""
        if not self.window:
            self.setup_window()
        self.window.deiconify()
        
    def hide(self):
        """隐藏窗口"""
        if self.window:
            self.window.withdraw()
            
    def run(self):
        """运行主窗口"""
        if not self.window:
            self.setup_window()
        self.window.mainloop()