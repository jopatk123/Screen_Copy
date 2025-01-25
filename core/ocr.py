import requests
import base64
import json
from config.settings import Settings
import os

class OCRManager:
    def __init__(self):
        self.settings = Settings()
        self.access_token = None
        
    def _get_access_token(self):
        """获取百度API access token"""
        if not self.access_token:
            self.access_token = self.settings.get_access_token()
            if not self.access_token:
                print("获取access token失败，请检查API_KEY和SECRET_KEY是否正确")
            else:
                print(f"成功获取access token: {self.access_token[:10]}...")
        return self.access_token
        
    def recognize_text(self, image_path):
        """
        识别图片中的文字
        :param image_path: 图片文件路径
        :return: 识别到的文字列表
        """
        try:
            # 检查图片文件是否存在
            if not os.path.exists(image_path):
                raise Exception(f"图片文件不存在: {image_path}")
                
            # 获取access token
            access_token = self._get_access_token()
            if not access_token:
                raise Exception("无法获取access token")

            # 读取图片文件
            with open(image_path, 'rb') as f:
                image = base64.b64encode(f.read())

            # 设置请求参数
            params = {
                'access_token': access_token
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'image': image,
                'language_type': 'CHN_ENG',  # 中英文混合
                'detect_direction': 'true',   # 检测文字方向
                'probability': 'true'         # 返回识别结果的置信度
            }

            print("正在发送OCR请求...")
            # 发送OCR请求
            response = requests.post(
                self.settings.OCR_REQUEST_URL,
                params=params,
                headers=headers,
                data=data
            )

            # 处理响应
            if response.ok:
                result = response.json()
                print(f"OCR响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
                
                # 检查错误码
                if 'error_code' in result:
                    error_msg = result.get('error_msg', '未知错误')
                    raise Exception(f"OCR API返回错误: {error_msg} (错误码: {result['error_code']})")
                    
                return self.process_result(result)
            else:
                print(f"OCR请求失败: HTTP {response.status_code}")
                print(f"响应内容: {response.text}")
                return []

        except Exception as e:
            print(f"OCR识别出错: {str(e)}")
            return []

    def process_result(self, result):
        """
        处理OCR返回结果
        :param result: OCR API返回的JSON结果
        :return: 提取的文字列表
        """
        texts = []
        try:
            # 提取识别到的文字
            words_result = result.get('words_result', [])
            if not words_result:
                print("未识别到任何文字")
                return texts
                
            print(f"识别到 {len(words_result)} 个文本区域")
            for item in words_result:
                text = item['words']
                probability = item.get('probability', {}).get('average', 0)
                print(f"文本: {text} (置信度: {probability:.2f})")
                texts.append(text)
                
        except Exception as e:
            print(f"处理OCR结果出错: {str(e)}")
        return texts

    def save_to_clipboard(self, texts):
        """
        将文字保存到剪贴板
        :param texts: 要保存的文字列表
        """
        if not texts:
            print("没有文字需要保存到剪贴板")
            return False
            
        text = '\n'.join(texts)
        try:
            import pyperclip
            pyperclip.copy(text)
            print(f"已将以下文字保存到剪贴板:\n{text}")
            return True
        except Exception as e:
            print(f"保存到剪贴板失败: {str(e)}")
            return False