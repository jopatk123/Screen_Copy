import threading
import os
import time
from pynput import keyboard
from core.screenshot import ScreenshotManager
from core.ocr import OCRManager
from ui.tray import SystemTray
from ui.main_window import MainWindow
from config.settings import Settings
import sys

class ScreenOCR:
    def __init__(self):
        # 添加资源路径处理
        self.base_path = self._get_base_path()
        # 验证环境变量
        self._verify_api_keys()
        
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
        
    def _verify_api_keys(self):
        """验证百度 API 密钥是否正确设置"""
        # 首先尝试直接获取环境变量
        api_key = os.getenv('BAIDU_API_KEY')
        secret_key = os.getenv('BAIDU_SECRET_KEY')
        
        if not api_key or not secret_key:
            # 尝试通过不同方式获取环境变量
            try:
                # 方法1：使用 winreg 读取注册表（仅 Windows）
                import winreg
                def get_env_from_registry(name):
                    try:
                        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                           r'Environment', 
                                           0, 
                                           winreg.KEY_READ)
                        value, _ = winreg.QueryValueEx(key, name)
                        winreg.CloseKey(key)
                        return value
                    except:
                        return None

                api_key = get_env_from_registry('BAIDU_API_KEY')
                secret_key = get_env_from_registry('BAIDU_SECRET_KEY')
                
                # 如果注册表中没有，尝试系统环境变量
                if not api_key or not secret_key:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                       r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 
                                       0, 
                                       winreg.KEY_READ)
                    if not api_key:
                        api_key, _ = winreg.QueryValueEx(key, 'BAIDU_API_KEY')
                    if not secret_key:
                        secret_key, _ = winreg.QueryValueEx(key, 'BAIDU_SECRET_KEY')
                    winreg.CloseKey(key)

                # 如果还是没有找到，抛出异常
                if not api_key or not secret_key:
                    raise ValueError("未在注册表中找到环境变量")

            except Exception as e:
                print(f"从注册表读取失败: {str(e)}")
                try:
                    # 方法2：通过 subprocess 从 CMD 获取
                    import subprocess
                    api_key = subprocess.check_output('echo %BAIDU_API_KEY%', 
                                                   shell=True).decode('utf-8').strip()
                    secret_key = subprocess.check_output('echo %BAIDU_SECRET_KEY%', 
                                                      shell=True).decode('utf-8').strip()
                    
                    # 检查是否获取到了实际的值而不是环境变量名称
                    if api_key == '%BAIDU_API_KEY%' or secret_key == '%BAIDU_SECRET_KEY%':
                        raise ValueError("环境变量未设置")
                        
                except Exception as sub_e:
                    raise ValueError(
                        f"无法获取环境变量。请确保已正确设置 BAIDU_API_KEY 和 BAIDU_SECRET_KEY。\n"
                        f"错误详情：{str(sub_e)}"
                    )
        
        # 确保值有效并设置到当前进程的环境变量中
        if api_key and secret_key:
            os.environ['BAIDU_API_KEY'] = api_key.strip()
            os.environ['BAIDU_SECRET_KEY'] = secret_key.strip()
            print(f"API 密钥验证成功：\nAPI_KEY: {api_key[:8]}...\nSECRET_KEY: {secret_key[:8]}...")
        else:
            raise ValueError("环境变量验证失败")

    def _get_base_path(self):
        """获取程序运行时的基础路径"""
        if getattr(sys, 'frozen', False):
            # 如果是打包后的exe
            return os.path.dirname(sys.executable)
        else:
            # 如果是开发环境
            return os.path.dirname(os.path.abspath(__file__))

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
            
            # 关闭系统托盘
            if self.system_tray:
                self.system_tray.cleanup()  # 确保SystemTray类中实现了cleanup方法
            
            # 关闭主窗口
            if self.main_window:
                self.main_window.close()
            
            # 标记程序结束
            self.running = False
            
            # 确保所有资源都被释放
            import gc
            gc.collect()
            
        except Exception as e:
            print(f"清理资源时出错: {e}")
        finally:
            # 确保程序状态被正确设置为结束
            self.running = False

if __name__ == "__main__":
    app = ScreenOCR()
    app.run()
