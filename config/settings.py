import os
from dotenv import load_dotenv
import requests

# 加载.env文件中的环境变量
load_dotenv()

def load_config():
    load_dotenv()
    
    config = {
        # 优先从系统环境变量读取，如果没有则从.env文件读取
        'BAIDU_API_KEY': os.environ.get('BAIDU_API_KEY') or os.getenv('BAIDU_API_KEY'),
        'BAIDU_SECRET_KEY': os.environ.get('BAIDU_SECRET_KEY') or os.getenv('BAIDU_SECRET_KEY'),
        'SCREENSHOT_HOTKEY': os.getenv('SCREENSHOT_HOTKEY', 'alt+d'),
        'WINDOW_WIDTH': int(os.getenv('WINDOW_WIDTH', 800)),
        'WINDOW_HEIGHT': int(os.getenv('WINDOW_HEIGHT', 600)),
        'TEMP_DIR': os.getenv('TEMP_DIR', 'temp')
    }
    
    return config

class Settings:
    def __init__(self):
        # OCR API配置
        self.API_KEY = os.getenv("BAIDU_API_KEY", "")
        self.SECRET_KEY = os.getenv("BAIDU_SECRET_KEY", "")
        self.OCR_API_URL = "https://aip.baidubce.com/oauth/2.0/token"
        self.OCR_REQUEST_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"
        
        # 快捷键配置
        self.SCREENSHOT_HOTKEY = os.getenv("SCREENSHOT_HOTKEY", "ctrl+alt+z")
        
        # UI配置
        self.WINDOW_WIDTH = int(os.getenv("WINDOW_WIDTH", "800"))
        self.WINDOW_HEIGHT = int(os.getenv("WINDOW_HEIGHT", "600"))
        
        # 临时文件配置
        self.TEMP_DIR = os.getenv("TEMP_DIR", os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp"))
        if not os.path.exists(self.TEMP_DIR):
            os.makedirs(self.TEMP_DIR)
            
    def get_access_token(self):
        """获取百度API access token"""
        params = {
            'grant_type': 'client_credentials',
            'client_id': self.API_KEY,
            'client_secret': self.SECRET_KEY
        }
        try:
            response = requests.get(self.OCR_API_URL, params=params)
            if response.ok:
                return response.json().get('access_token')
        except Exception as e:
            print(f"获取access token失败: {e}")
        return None
        
    def save(self):
        """保存设置到.env文件"""
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        
        # 读取现有的.env文件内容
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        else:
            lines = []
            
        # 更新或添加SCREENSHOT_HOTKEY
        hotkey_found = False
        for i, line in enumerate(lines):
            if line.startswith('SCREENSHOT_HOTKEY='):
                lines[i] = f'SCREENSHOT_HOTKEY={self.SCREENSHOT_HOTKEY}\n'
                hotkey_found = True
                break
                
        if not hotkey_found:
            lines.append(f'SCREENSHOT_HOTKEY={self.SCREENSHOT_HOTKEY}\n')
            
        # 写回.env文件
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)