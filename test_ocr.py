from core.screenshot import ScreenshotManager
from core.ocr import OCRManager
import os
import time

def test_ocr():
    # 创建截图管理器实例
    screenshot_manager = ScreenshotManager()
    ocr_manager = OCRManager()
    
    print("请用鼠标选择要识别的区域...")
    screenshot_manager.start_region_selection()
    
    if screenshot_manager.current_screenshot:
        # 保存截图到调试文件夹
        debug_dir = "debug"
        if not os.path.exists(debug_dir):
            os.makedirs(debug_dir)
            
        debug_file = os.path.join(debug_dir, f"screenshot_{int(time.time())}.png")
        screenshot_manager.current_screenshot.save(debug_file)
        print(f"\n截图已保存到: {debug_file}")
        
        print("正在识别文字...")
        # 识别文字
        texts = ocr_manager.recognize_text(debug_file)
        
        if texts:
            print("\n识别结果:")
            for text in texts:
                print(text)
            
            # 保存到剪贴板
            if ocr_manager.save_to_clipboard(texts):
                print("\n文字已复制到剪贴板!")
        else:
            print("未识别到文字")

if __name__ == "__main__":
    test_ocr()
