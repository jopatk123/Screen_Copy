import pystray
from PIL import Image, ImageDraw
import sys
from config.settings import Settings

class SystemTray:
    def __init__(self, screenshot_callback=None, show_window_callback=None, exit_callback=None):
        self.settings = Settings()
        self.screenshot_callback = screenshot_callback
        self.show_window_callback = show_window_callback
        self.exit_callback = exit_callback
        self.setup_tray()

    def create_tray_icon(self):
        """创建托盘图标"""
        # 创建一个32x32的图像
        width = 32
        height = 32
        image = Image.new('RGB', (width, height), '#1DA1F2')  # 蓝色背景
        draw = ImageDraw.Draw(image)
        
        # 绘制简单的OCR文字
        draw.text((5, 10), "OCR", fill='white')
        
        return image

    def setup_tray(self):
        """设置系统托盘"""
        # 创建托盘图标
        image = self.create_tray_icon()

        # 创建菜单
        menu_items = [
            pystray.MenuItem(
                "显示主窗口",
                self.on_show_window,
                default=True  # 设为默认项，双击托盘图标时触发
            ),
            pystray.MenuItem(
                "截图识别",
                self.on_screenshot
            ),
            pystray.MenuItem(
                f"快捷键: {self.settings.SCREENSHOT_HOTKEY}",
                lambda: None,
                enabled=False
            ),
            pystray.MenuItem(
                "退出",
                self.on_exit
            )
        ]

        # 创建托盘
        self.tray = pystray.Icon(
            "screen_ocr",
            image,
            "屏幕文字识别",
            menu=pystray.Menu(*menu_items)
        )

    def on_show_window(self):
        """显示主窗口回调"""
        if self.show_window_callback:
            self.show_window_callback()

    def on_screenshot(self):
        """截图回调"""
        if self.screenshot_callback:
            self.screenshot_callback()

    def on_exit(self):
        """退出程序回调"""
        self.cleanup()
        # 调用退出回调
        if self.exit_callback:
            self.exit_callback()
        # 退出程序
        sys.exit(0)

    def cleanup(self):
        """清理系统托盘资源"""
        try:
            # 确保托盘图标被移除
            if hasattr(self, 'tray'):
                self.tray.stop()
                self.tray = None
        except Exception as e:
            print(f"清理系统托盘时出错: {e}")

    def run(self):
        """运行系统托盘"""
        self.tray.run()