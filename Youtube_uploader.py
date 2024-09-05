"""
Youtubeに動画をアップロードする機能を提供します。

@author: Yuta Tanimura
"""
import os
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient import errors  # この行を追加
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


class Youtube_uploader:
    def __init__(self, key_path):
        self.scopes = ["https://www.googleapis.com/auth/youtube.upload"]
        self.credentials = None
        
        # トークンファイルが存在する場合は読み込む
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.credentials = pickle.load(token)
        
        # 有効な認証情報がない場合は新しく取得する
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    key_path, self.scopes)  # ファイル名を実際のものに置き換えてください
                self.credentials = flow.run_local_server(port=0)
            
            # 認証情報を保存
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.credentials, token)

        # YouTube API クライアントを作成
        self.youtube = build("youtube", "v3", credentials=self.credentials)

    def upload_video(self, video_path, title, description, tags):
        """
        Youtubeに動画をアップロードします

        Args:
            video_path (str): 動画ファイルのパス
            title (str): 動画のタイトル
            description (str): 動画の説明
            tags (list): 動画のタグ
        """
        # 動画のアップロード
        request_body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': '22'
            },
            'status': {
                'privacyStatus': 'public',
                'selfDeclaredMadeForKids': False
            }
        }

        media_file = MediaFileUpload(video_path)

        try:
            response = self.youtube.videos().insert(
                part='snippet,status',
                body=request_body,
                media_body=media_file
            ).execute()
            print(f"動画がアップロードされました。Video ID: {response['id']}")
        except errors.HttpError as e:  # googleapiclient.errors を errors に変更
            print(f"エラーが発生しました: {e}")
            response = None
            
if __name__ == "__main__":
    uploader = Youtube_uploader("keys/client_secret_170252295818-u0p1ncb82ou8otmkv0q7hvlpc72hq22b.apps.googleusercontent.com.json")
    uploader.upload_video("movie.mp4", "YOUR_VIDEO_TITLE", "YOUR_VIDEO_DESCRIPTION", ["YOUR_VIDEO_TAG1", "YOUR_VIDEO_TAG2"])