"""
チャットGPTの機能を提供します。
@Author: Yuta Tanimura
"""

from openai import OpenAI
import json
import base64

class ChatGPT:
    def __init__(self, api_key:str, model:str, init_prompt:str="", n_memorise:int=1):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.conversation_history = [{"role": "system", "content": init_prompt}]
        self.n_memorise = n_memorise
        
    def _convert_img2base64(self, image_path:str) -> str:
        """
        画像をbase64に変換します。

        Args:
            image_path (str): 画像のパス。

        Returns:
            str: base64に変換した画像
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
        
    def send_message(self, message:str, image_path:str=None) -> str:
        """
        ChatGPTにメッセージを送信します。

        Args:
            message (str): 送信するメッセージ
            image_path (str): 画像のパス。形式はJPGである必要があります。

        Returns:
            str: ChatGPTからの回答
        """
        
        # 会話の履歴を含めてメッセージを構築
        if image_path is not None:
            image64 = self._convert_img2base64(image_path)
            messages = self.conversation_history + [
                {"role": 
                "user", 
                "content": [
                    {"type": "text", "text": message},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image64}"}}
                    ]
                }
            ]
        else:
            messages = self.conversation_history + [
                {"role": "user", "content": message}
            ]
            
        if len(self.conversation_history) > self.n_memorise:
            self.conversation_history.pop(0)

        # ChatGPTにリクエストを送信
        try:
            response = self.client.chat.completions.create(model=self.model, messages=messages)
        except Exception as e:
            print("[Error]: ChatGPTへのリクエストに失敗しました．")
            print(e)
            return ""
        # 応答を取得
        response_text = response.choices[0].message.content

        # 今回のユーザーのプロンプトとChatGPTの応答を会話履歴に追加
        self.conversation_history.append({"role": "user", "content": message})
        self.conversation_history.append({"role": "assistant", "content": response_text})

        return response_text
    
if __name__ == "__main__":
    with open("ChatGPT_params.json", "r") as f:
        params = json.load(f)
    gpt = ChatGPT(params["api_key"], params["model"])
    print(gpt.send_message("この画像を説明してください", "APEX.jpg"))




