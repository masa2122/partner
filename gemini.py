import os
import google.generativeai as genai
from dotenv import load_dotenv


class GeminiApi():
    def __init__(self) -> None:
        load_dotenv('./.env')
        GEMINI_API_KEY = os.environ['GEMINI_API_KEY']
        genai.configure(api_key=GEMINI_API_KEY)

        self.model_name = "gemini-pro"
        self.model = genai.GenerativeModel(self.model_name)
        self.chat = self.model.start_chat(history=[])


    def run(self, text, file=None):
        try:
            if self.model_name =="gemini-pro":
                response = self.chat.send_message(text)
            else:
                if text == "":
                    response = self.model.generate_content(file)
                else:
                    response = self.model.generate_content([text, file])
        except:
            return "通信失敗！"
        
        return response.text

    # ボタンを押されたらチャットをクリアする
    def clear_chat(self):
        self.chat = self.model.start_chat(history=[])

    # modelの変更
    def change_model(self, model_name):
        self.model_name = model_name
        # 文字プロンプト
        if self.model_name == "gemini-pro":
            self.model = genai.GenerativeModel(model_name)
            self.chat = self.model.start_chat(history=[])
        # 画像プロンプト
        else:
            self.model = genai.GenerativeModel('gemini-pro-vision')