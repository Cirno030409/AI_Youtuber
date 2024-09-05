"""
Youtubeに自動で動画投稿を行います。

@author: Yuta Tanimura
"""
import json
import os
import pickle
import time
from datetime import datetime

import win10toast
from moviepy.editor import VideoFileClip
from pydub import AudioSegment
from tqdm import tqdm

from ChatGPT import ChatGPT
from Movie_maker import Movie_maker
from VoiceVox import generate_voice
from Youtube_uploader import Youtube_uploader

story_title = ""

def main():
    toast = win10toast.ToastNotifier()
    while True: # 毎日繰り返す
        save_path = f"resources/output/movie_{datetime.now().strftime('%Y%m%d%H%M')}.mp4"
        if os.path.exists("resources/param/date.pickle"):
            with open("resources/param/date.pickle", "rb") as f:
                date = pickle.load(f)
            if date >= datetime.now().strftime('%Y%m%d'):
                print("日付が変わるまで待機しています...")
            while date >= datetime.now().strftime('%Y%m%d'): # 日付が変わるまで待機
                time.sleep(10)
        toast.show_toast("動画投稿プロセス進行中", "語りのずんだチャンネルの動画投稿プロセスが始まります。", duration=10, threaded=True)
        print("物語を生成しています...")
        retry_count = 0
        while True: # 物語生成が成功するまでリトライする
            try:
                stories = create_story()
                print(stories)
                story_kanji_lines = stories[0].split('\n')
                story_hiragana_lines = stories[1].split('\n')
                
                # 空の要素を削除
                story_kanji_lines = [line for line in story_kanji_lines if line.strip()]
                story_hiragana_lines = [line for line in story_hiragana_lines if line.strip()]
                
                assert len(story_kanji_lines) == len(story_hiragana_lines), "通常バージョンとひらがなとカタカナのバージョンの行数が一致しません。"
            except AssertionError as e:
                retry_count += 1
                print("ChatGPTが不正な物語を生成しました。リトライします。リトライ回数：", retry_count)
                if retry_count > 4:
                    toast.show_toast("物語生成エラー", "ChatGPTが不正な物語を生成しました。リトライ回数が4回を超えたため、プログラムを終了します。", duration=10)
                    exit()
                else:
                    continue
            break
        
        print("\nボイスを生成しています...")
        # resources/textフォルダとvoiceフォルダの中にあるファイルを削除
        for folder in ["resources/text", "resources/voice"]:
            for file in os.listdir(folder):
                file_path = os.path.join(folder, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        print("既存のファイルを削除しました。")
        
        # ファイルに書き出し
        for i in tqdm(range(len(story_hiragana_lines))):
            with open("resources/text/"+str(i)+".txt", "w", encoding="utf-8") as f:
                f.write(story_kanji_lines[i])
            try:
                generate_voice(story_hiragana_lines[i], output_path="resources/voice/"+str(i+10)+".wav", speaker=22, speed=0.75)
            except:
                print("ボイス生成エラーです。VOICEVOXXエンジンを起動してください。")
                toast.show_toast("ボイス生成エラー", "ボイスを生成できませんでした。VOICEVOXXエンジンが起動されていない可能性があります。プログラムを終了します。", duration=10)
                exit()
        print("ボイスを生成しました。")
        print("動画を生成しています...")
        
        # 動画を生成
        create_movie(save_path=save_path)
        print("動画を生成しました。")
        print("動画をアップロードしています...")
        uploader = Youtube_uploader("keys/client_secret_170252295818-u0p1ncb82ou8otmkv0q7hvlpc72hq22b.apps.googleusercontent.com.json")

        # 動画をアップロード
        uploader.upload_video(video_path=save_path,
                            title=f"【睡眠導入】ずんだもんがささやき声で物語を読み聞かせるのだ【{story_title}】",
                            description=f"こんばんは。ずんだもんなのだ。このチャンネルでは僕が毎日いろんな物語をささやき声で読み聞かせる動画を投稿しているのだ。気に入ったらぜひ高評価とチャンネル登録をしていただけるとうれしいのだ。のだ。",
                            tags=["語りのずんだ", "ずんだもん", "物語", "読み聞かせ", "ささやき声", "ささやき声で物語を読み聞かせるのだ", "ささやき声で物語を読み聞かせるのだ【{story_title}】"])
        print("動画をアップロードしました。")
        toast.show_toast("動画投稿プロセス完了", "語りのずんだチャンネルの動画投稿プロセスが完了しました。", duration=10)
        with open("resources/param/date.pickle", "wb") as f:
            pickle.dump(datetime.now().strftime('%Y%m%d'), f) # 投稿したので日付を保存
    
def create_story() -> str:
    """
    物語を作成します。

    Args:
        description (str): 物語の説明

    Returns:
        str: 物語
    """
    prompt="""
    6000文字程度の長い物語を作成してください。
    最初に物語のタイトルを読み上げてください。「タイトル」という必要はありません。
    
    出力は「通常バージョン」と「ひらがなとカタカナのバージョン」の２つを作成してください。
    「ひらがなとカタカナのバージョン」は、通常バージョンをひらがなとカタカナのみの表記に変換したものです。
    また、どちらのバージョンにおいても必ず「。」のあとで改行するようにしてください。それ以外の箇所では改行しないてください。
    なお、「通常バージョン」と「ひらがなとカタカナのバージョン」で改行する位置は揃えてください。つまり、両バージョンの行数が同じになるはずです。
    また、いかなるマークダウン記法も使用しないでください。この文章は読み上げソフトによって読み上げられるので、その際に変になることは避けなければなりません。
    また、以下の書式を守りなさい。なお、()は、その中身は、出力しないこと。また、「通常バージョン」と「ひらがなとカタカナのバージョン」の間の行には、「;」を入れてください。これがこれらを隔てる合図になります。

    
    
    (通常バージョンの物語)
    ;
    (ひらがなとカタカナのバージョンの物語)


    """
    with open("keys/ChatGPT_params.json", "r") as f:
        params = json.load(f)
    gpt = ChatGPT(params["api_key"], params["model"])
    story = gpt.send_message(prompt)
    stories = story.split(';')
    
    assert len(stories) == 2, "物語のバージョンが2つではありません。"
    return stories

def split_text_by_length(text: str, length: int) -> str:
    """
    指定された文字数で改行で区切る関数

    Args:
        text (str): 入力テキスト
        length (int): 1行あたりの文字数

    Returns:
        str: 指定された文字数で区切られたテキスト
    """
    lines = []
    for i in range(0, len(text), length):
        lines.append(text[i:i+length])
    return '\n'.join(lines)



def create_movie(save_path: str):
    """
    物語の読み聞かせ動画を生成します。
    """
    text = """
    語りのずんだへようこそなのだ。この動画では、ぼくがあなたにいろんなものがたりを、よみきかせるのだ。こんかいのものがたりはこれなのだ。
    """
    generate_voice(text, speaker=22, speed=0.75, output_path="resources/voice/0.wav")
    text_end = """
    これでこのものがたりはおわりなのだ。ぜひほかのものがたりもきいていってもらえるとうれしいのだ。それでは、べつのものがたりでまたあおうなのだ。ばいばい。
    """
    generate_voice(text_end, speaker=22, speed=0.75, output_path="resources/voice/1000.wav")
    # ボイスファイルのリストを生成
    voice_path = [f for f in os.listdir("resources/voice") if f.endswith(".wav")]
    voice_path.sort(key=lambda x: int(x.split('.')[0]))  # ファイル名の数字順にソート
    voice_path = [f"resources/voice/{f}" for f in voice_path]
    
    print(f"合計{len(voice_path)}個のボイスファイルが見つかりました。")

    img_zunda_path = "resources/image/立ち絵.png"
    img_gb_path = "resources/image/background.png"
    text_path = "resources/text/"
    font_path = "fonts/HGRGY.TTC"
    
    clips = [] # クリップのリスト    
    print("クリップを構成しています...")
    for i in tqdm(range(len(voice_path))):
        audio = AudioSegment.from_wav(voice_path[i]) # 音声ファイルを読み込む
        duration_sec = audio.duration_seconds # 音声の長さを取得
        if 0 < i < len(voice_path)-1: # 動画説明とエンディングの分引く
            with open(text_path+str(i-1)+".txt", "r", encoding="utf-8") as f:
                text = f.read()
        if i == 0: # 動画説明
            clips.append(Movie_maker(duration=(duration_sec + 2.5))) # 前口上とタイトルのClipを作成
            clips[i].add_image(img_gb_path, position=(0, 0), resize_ratio_x=1, resize_ratio_y=1)
            clips[i].add_image(img_zunda_path, position=(1250, 400), resize_ratio_x=1.2, resize_ratio_y=1.2)
            clips[i].add_text("「語りのずんだ」へようこそなのだ。", start_time=0, end_time=3.5, position="center", fontsize=50, color="white", stroke_color="black", stroke_width=1, font=font_path)
            clips[i].add_text("この動画では、僕があなたにいろんな物語を読み聞かせるのだ。", start_time=3.5, end_time=11, position="center", fontsize=50, color="white", stroke_color="black", stroke_width=1, font=font_path)
            clips[i].add_text("今回の物語はこれなのだ。", start_time=11, position="center", fontsize=50, color="white", stroke_color="black", stroke_width=1, font=font_path)
        elif i == 1: # 物語タイトル
            global story_title
            story_title = text
            clips.append(Movie_maker(duration=(duration_sec + 1.5))) # 前口上とタイトルのClipを作成
            clips[i].add_image(img_gb_path, position=(0, 0), resize_ratio_x=1, resize_ratio_y=1)
            clips[i].add_image(img_zunda_path, position=(1250, 400), resize_ratio_x=1.2, resize_ratio_y=1.2)
            clips[i].add_text(text, position="center", fontsize=100, color="white", stroke_color="black", stroke_width=2, font=font_path)
        elif i == len(voice_path)-1: # エンディング
            clips.append(Movie_maker(duration=(duration_sec + 1.5))) # 前口上とタイトルのClipを作成
            clips[i].add_image(img_gb_path, position=(0, 0), resize_ratio_x=1, resize_ratio_y=1)
            clips[i].add_image(img_zunda_path, position=(1250, 400), resize_ratio_x=1.2, resize_ratio_y=1.2)
        else: # 物語
            text = split_text_by_length(text, 38)
            clips.append(Movie_maker(duration=(duration_sec + 1))) # 物語のClipを作成
            clips[i].add_image(img_gb_path, position=(0, 0), resize_ratio_x=1, resize_ratio_y=1)
            clips[i].add_image(img_zunda_path, position=(1250, 400), resize_ratio_x=1.2, resize_ratio_y=1.2)
            clips[i].add_text(text, position="center", fontsize=50, color="white", stroke_color="black", stroke_width=1, font=font_path)
        clips[i].add_audio(voice_path[i]) # 音声を追加
    
    # クリップを連結
    for i in range(1, len(clips)):
        clips[0].concatenate_clips(clips[i].get_clip())
        
    # クリップをエクスポート（GPUを使用）
    clips[0].export_clip(save_path, remove_temp=True,
                        codec="h264_nvenc",
                        ffmpeg_params=["-preset", "slow", "-crf", "23"])

if __name__ == "__main__":
    main()
