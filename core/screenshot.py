import tkinter as tk
from PIL import ImageGrab, ImageTk, Image
import os
import tempfile
import time

class ScreenshotManager:
    # 替换原来的 __init__ 方法中的DPI获取代码
    def __init__(self):
        self.dpi_scale = 1.0
        self.size_text_id = None  # 初始化 size_text_id
        self.current_rect = None  # 初始化 current_rect
        self.current_screenshot = None  # 初始化 current_screenshot
        try:
            import ctypes
            shcore = ctypes.windll.shcore
            shcore.SetProcessDpiAwareness(2)  # 使用PerMonitorV2模式
            hwnd = ctypes.windll.user32.GetDesktopWindow()
            dpi = ctypes.c_uint()
            shcore.GetDpiForWindow(hwnd, ctypes.byref(dpi))
            self.dpi_scale = dpi.value / 96.0
        except:
            pass
        print(f"当前DPI缩放: {self.dpi_scale}")

        
    def start_region_selection(self):
        """开始区域选择"""
        # 创建全屏窗口
        # self.selection_window = tk.Tk()
        # self.selection_window.attributes('-fullscreen', True, '-alpha', 0.3, '-topmost', True)
        # self.selection_window.configure(cursor="crosshair")

        self.selection_window = tk.Tk()
        # 使用更可靠的全屏实现
        self.selection_window.attributes('-fullscreen', True)
        self.selection_window.attributes('-alpha', 0.3)
        self.selection_window.attributes('-topmost', True)
        self.selection_window.update()  # 强制窗口立即完成布局

        # 创建画布
        self.canvas = tk.Canvas(
            self.selection_window,
            highlightthickness=0,
            bg='gray11'
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # 绑定事件
        self.canvas.bind('<Button-1>', self._on_mouse_down)
        self.canvas.bind('<B1-Motion>', self._on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self._on_mouse_up)
        self.selection_window.bind('<Escape>', self._on_escape)
        
        # 创建工具栏
        self.create_toolbar()
        
        # 运行窗口
        self.selection_window.mainloop()

    def create_toolbar(self):
        """创建工具栏"""
        self.toolbar = tk.Toplevel(self.selection_window)
        self.toolbar.overrideredirect(True)
        self.toolbar.attributes('-topmost', True)
        self.toolbar.withdraw()  # 初始时隐藏工具栏

        # 创建按钮
        confirm_btn = tk.Button(
            self.toolbar,
            text="确认",
            command=lambda: self._confirm_selection(self.selection_window),
            state=tk.DISABLED
        )
        confirm_btn.pack(side=tk.LEFT, padx=5, pady=5)

        cancel_btn = tk.Button(
            self.toolbar,
            text="取消",
            command=lambda: self._cancel_selection(self.selection_window)
        )
        cancel_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 保存按钮引用以便后续启用/禁用
        self.confirm_btn = confirm_btn

    def _on_mouse_down(self, event):
        """鼠标按下事件处理"""
        # 记录起始位置（使用相对坐标）
        self.start_x = event.x
        self.start_y = event.y
        print(f"Mouse down at: ({self.start_x}, {self.start_y})")  # Debug output
        
        # 创建选择框
        self.current_rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline='#1E90FF',  # 蓝色边框
            fill='#ADD8E6',     # 浅蓝色填充
            stipple='gray50'    # 半透明效果
        )

    def _on_mouse_drag(self, event):
        """鼠标拖动事件处理"""
        if self.current_rect:
            # 更新选择框（使用相对坐标）
            current_x = event.x
            current_y = event.y
            print(f"Mouse drag to: ({current_x}, {current_y})")  # Debug output
            
            self.canvas.coords(
                self.current_rect,
                self.start_x, self.start_y,
                current_x, current_y
            )
            
            # 更新尺寸文本
            width = abs(current_x - self.start_x)
            height = abs(current_y - self.start_y)
            if self.size_text_id is not None:  # 检查 size_text_id 是否为 None
                self.canvas.delete(self.size_text_id)
            self.size_text_id = self.canvas.create_text(
                min(self.start_x, current_x) + width/2,
                min(self.start_y, current_y) - 10,
                text=f'{width} x {height}',
                fill='white'
            )

            # 更新工具栏位置
            self.toolbar.geometry(f'+{event.x_root}+{event.y_root-40}')
            self.toolbar.deiconify()
            
            # 启用确认按钮（如果选择区域足够大）
            if width > 10 and height > 10:
                self.confirm_btn.config(state=tk.NORMAL)
            else:
                self.confirm_btn.config(state=tk.DISABLED)
        else:
            self.size_text_id = None  # 重置 size_text_id

    def _on_mouse_up(self, event):
        """鼠标释放事件处理"""
        if self.current_rect is None:  # 检查 current_rect 是否为 None
            return
        # 获取选择区域的相对坐标
        x1 = min(self.start_x, event.x)
        y1 = min(self.start_y, event.y)
        x2 = max(self.start_x, event.x)
        y2 = max(self.start_y, event.y)
        print(f"选择区域: ({x1}, {y1}) -> ({x2}, {y2})")
        
        # 如果选择区域太小，取消选择
        if abs(x2-x1) < 10 or abs(y2-y1) < 10:
            self._cancel_selection(self.selection_window)
            return
        
        try:
            # 获取窗口物理坐标
            root_x = self.selection_window.winfo_x()
            root_y = self.selection_window.winfo_y()
            
            # 转换为物理像素坐标
            screen_x1 = int((root_x + x1) * self.dpi_scale)
            screen_y1 = int((root_y + y1) * self.dpi_scale)
            screen_x2 = int((root_x + x2) * self.dpi_scale)
            screen_y2 = int((root_y + y2) * self.dpi_scale)
            
            # 添加边界检查（防止超出屏幕）
            screen_width = self.selection_window.winfo_screenwidth()
            screen_height = self.selection_window.winfo_screenheight()
            
            screen_x1 = max(0, min(screen_x1, screen_width))
            screen_y1 = max(0, min(screen_y1, screen_height))
            screen_x2 = max(0, min(screen_x2, screen_width))
            screen_y2 = max(0, min(screen_y2, screen_height))
            print(f"截图区域: ({screen_x1}, {screen_y1}) -> ({screen_x2}, {screen_y2})")
            
            # 截图前确保窗口已隐藏
            self.selection_window.withdraw()
            time.sleep(0.1)  # 给窗口一点时间来隐藏
            
            # 进行截图
            self.current_screenshot = ImageGrab.grab(bbox=(
                screen_x1,
                screen_y1,
                screen_x2,
                screen_y2
            ))
            
            print(f"截图尺寸: {self.current_screenshot.size}")
            
        except Exception as e:
            print(f"截图时发生错误: {e}")
            self._cancel_selection(self.selection_window)
        finally:
            self.current_rect = None  # 重置 current_rect


    def _on_escape(self, event):
        """ESC键按下事件处理"""
        self._cancel_selection(self.selection_window)

    def _confirm_selection(self, window):
        """确认截图"""
        window.destroy()

    def _cancel_selection(self, window):
        """取消截图"""
        self.current_screenshot = None
        window.destroy()

    def save_screenshot(self):
        """保存截图到临时文件"""
        if self.current_screenshot:
            # 创建临时文件
            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, 'screenshot.png')
            
            # 保存截图
            self.current_screenshot.save(temp_file, 'PNG')
            return temp_file
            
        return None

    def show_preview(self):
        """显示截图预览"""
        if self.current_screenshot:
            # 创建预览窗口
            preview_window = tk.Toplevel()
            preview_window.title("截图预览")
            preview_window.attributes('-topmost', True)
            
            # 获取屏幕尺寸
            screen_width = preview_window.winfo_screenwidth()
            screen_height = preview_window.winfo_screenheight()
            
            # 获取图片尺寸
            img_width, img_height = self.current_screenshot.size
            
            # 计算预览窗口的合适大小（不超过屏幕的75%）
            max_width = int(screen_width * 0.75)
            max_height = int(screen_height * 0.75)
            
            # 如果图片太大，等比例缩小
            scale = 1.0
            if img_width > max_width:
                scale = max_width / img_width
            if img_height * scale > max_height:
                scale = max_height / img_height
                
            preview_width = int(img_width * scale)
            preview_height = int(img_height * scale)
            
            # 调整预览窗口大小
            preview_window.geometry(f"{preview_width}x{preview_height}")
            
            # 转换PIL图片为PhotoImage
            preview_image = self.current_screenshot
            if scale != 1.0:
                preview_image = preview_image.resize((preview_width, preview_height))
            photo = ImageTk.PhotoImage(preview_image)
            
            # 创建标签显示图片
            label = tk.Label(preview_window, image=photo)
            label.image = photo  # 保持引用防止被垃圾回收
            label.pack(fill=tk.BOTH, expand=True)
            
            # 添加关闭按钮
            close_button = tk.Button(
                preview_window,
                text="关闭预览",
                command=preview_window.destroy
            )
            close_button.pack(pady=5)
            
            # 运行预览窗口
            preview_window.mainloop()
        else:
            print("没有可预览的截图")