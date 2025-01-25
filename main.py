import threading
import os
import time
from pynput import keyboard
from core.screenshot import ScreenshotManager
from core.ocr import OCRManager
from ui.tray import SystemTray
from ui.main_window import MainWindow
from config.settings import Settings

class ScreenOCR:
    def __init__(self):
        self.settings = Settings()
        self.screenshot_manager = ScreenshotManager()
        self.ocr_manager = OCRManager()
        self.main_window = MainWindow(
            screenshot_callback=self.capture_and_recognize,
            hotkey_callback=self.register_hotkey
        )
        self.system_tray = SystemTray(
            screenshot_callback=self.capture_and_recognize,
            show_window_callback=self.show_window,
            exit_callback=self.cleanup
        )
        self.running = True
        self.keyboard_listener = None
        
    def show_window(self):
        """显示主窗口"""
        self.main_window.show()
        
    def capture_and_recognize(self):
        """截图并识别文字"""
        # 开始截图
        self.screenshot_manager.start_region_selection()
        
        # 如果有截图，进行识别
        if self.screenshot_manager.current_screenshot:
            # 保存截图到临时文件
            temp_file = self.screenshot_manager.save_screenshot()
            if temp_file:
                # 识别文字
                texts = self.ocr_manager.recognize_text(temp_file)
                
                # 保存到剪贴板
                if texts:
                    self.ocr_manager.save_to_clipboard(texts)
                
                # 清理临时文件
                try:
                    os.remove(temp_file)
                except:
                    pass

    def register_hotkey(self):
        """注册快捷键"""
        try:
            # 如果已存在监听器，先停止它
            if self.keyboard_listener:
                self.keyboard_listener.stop()
                
            # 解析快捷键
            hotkey_parts = self.settings.SCREENSHOT_HOTKEY.lower().split('+')
            # 转换为pynput格式的热键字符串
            formatted_parts = []
            for part in hotkey_parts:
                if part == 'ctrl':
                    formatted_parts.append('<ctrl>')
                elif part == 'alt':
                    formatted_parts.append('<alt>')
                elif part == 'shift':
                    formatted_parts.append('<shift>')
                else:
                    formatted_parts.append(part)
            
            hotkey_str = '+'.join(formatted_parts)
            print(f"注册热键: {hotkey_str}")  # 调试信息
            
            # 创建热键监听器
            self.keyboard_listener = keyboard.GlobalHotKeys({
                hotkey_str: self.capture_and_recognize
            })
            self.keyboard_listener.start()
                
        except Exception as e:
            print(f"注册快捷键失败: {e}")
            
    def run(self):
        """运行程序"""
        # 注册快捷键
        self.register_hotkey()
        
        # 创建并启动主窗口线程
        window_thread = threading.Thread(target=self.main_window.run)
        window_thread.daemon = True
        window_thread.start()
        
        # 运行系统托盘
        self.system_tray.run()
        
        # 主线程保持运行
        try:
            while self.running:
                time.sleep(0.1)  # 减少CPU使用
        except KeyboardInterrupt:
            self.cleanup()
        finally:
            pass

    def cleanup(self):
        """清理资源"""
        try:
            # 停止键盘监听
            if self.keyboard_listener:
                self.keyboard_listener.stop()
            
            # 关闭主窗口
            if self.main_window:
                self.main_window.close()
                
            # 标记程序结束
            self.running = False
            
        except Exception as e:
            print(f"清理资源时出错: {e}")

if __name__ == "__main__":
    app = ScreenOCR()
    app.run()
