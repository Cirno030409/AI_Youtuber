"""
動画を作成する機能を提供します。

@author: Yuta Tanimura
"""
import numpy as np
from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.editor import (ColorClip, ImageClip, TextClip, VideoFileClip,
                            concatenate_videoclips)
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.io.bindings import mplfig_to_npimage
from moviepy.video.VideoClip import ColorClip
from PIL import Image, ImageDraw
from pydub import AudioSegment


class Movie_maker:
    def __init__(self, duration:float, bg_color=(0,0,0), size=(1920, 1080), fps=60):
        """
        新規のクリップを作成します。
        
        Args:
            duration (float): クリップの長さ\n
            bg_color (tuple, optional): クリップの背景色. Defaults to (0,0,0).\n
            size (tuple, optional): クリップのサイズ. Defaults to (1920, 1080).\n
            fps (int, optional): クリップのフレームレート. Defaults to 60.\n
            
        Returns:
            clip(Movie_maker): 新規のクリップをもったMovie_makerインスタンス
            
        Methods:
            export_clip(output_path): 
                クリップをエクスポートします。\n
            add_text(text, fontsize=50, color=(255,255,255), position="center", start_time=0, end_time=None): 
                テキストを追加します。\n
            get_clip(): 
                クリップを取得します。\n
            concatenate_clips(clip): 
                このクリップに、引数のクリップを連結します。\n
            add_image(image_path, position="center", start_time=0, end_time=1, resize_ratio_x=1, resize_ratio_y=1): 
                画像を追加します。\n
            add_audio(audio_path, start_time=0, end_time=None): 
                音声をクリップの指定した時点に追加します。\n
            add_video(video_path, position="center", start_time=0, end_time=None, resize_ratio_x=1, resize_ratio_y=1): 
                動画を追加します。\n
            add_rectangle(position=(0, 0), size=(100, 100), color=(255, 255, 255), start_time=0, end_time=None): 
                矩形を追加します。\n
            add_circle(position=(0, 0), radius=50, color=(255, 255, 255), start_time=0, end_time=None): 
                円を追加します。\n
        """
        self.clip = ColorClip(size=size, color=bg_color, duration=duration).set_fps(fps)
        self.duration = duration

    def export_clip(self, output_path, **kwargs):
        """
        クリップをエクスポートして、動画として保存します。
        
        Args:
            clip (VideoFileClip): エクスポートするクリップ
            output_path (str): エクスポートするパス
        """
        print("クリップをエクスポートしています...")
        self.clip.write_videofile(output_path, audio=True, **kwargs)
        print(f"クリップをエクスポートしました。 > {output_path}")
        
    def add_text(self, text, fontsize=50, color="white", position="center", start_time=0, end_time=None, stroke_color=None, stroke_width=None, font="fonts/MSGOTHIC.TTC"):
        """
        テキストを追加します。
        
        Args:
            text (str): 追加するテキスト\n
            fontsize (int, optional): フォントサイズ. デフォルトは50.\n
            color (str, optional): テキストの色. デフォルトは"white".\n
            position (str or tuple, optional): テキストの位置. デフォルトは"center".\n
            start_time (float, optional): テキストの開始時間. デフォルトは0.\n
            end_time (float, optional): テキストの終了時間. デフォルトはNone（クリップの終わりまで）.
            stroke_color (str, optional): テキストの輪郭の色. デフォルトはNone.
            stroke_width (int, optional): テキストの輪郭の幅. デフォルトはNone.
            font (str, optional): フォントのパス. デフォルトは"fonts/MSGOTHIC.TTC".
        """
        if text == "":
            print("Movie_maker.add_text: テキストが空なので、テキストは追加されません。")
            return
        if end_time is None:
            end_time = self.clip.duration
        else:
            end_time = end_time

        if stroke_color is not None and stroke_width is not None:
            text_clip = TextClip(text, fontsize=fontsize, color=color, font=font, stroke_color=stroke_color, stroke_width=stroke_width)
        else:
            text_clip = TextClip(text, fontsize=fontsize, color=color, font=font)
        text_clip = text_clip.set_position(position).set_start(start_time).set_end(end_time)
        self.clip = CompositeVideoClip([self.clip, text_clip])
        
    def add_image(self, image_path, end_time=None, position="center", start_time=0, resize_ratio_x=1, resize_ratio_y=1):
        """
        画像を追加します。透過PNGの場合は背景を透過して表示します。
        
        Args:
            image_path (str): 追加する画像のパス\n
            position (str, optional): 画像の位置. Defaults to "center".\n
            start_time (float, optional): 画像の開始時間. Defaults to 0.\n
            end_time (float, optional): 画像の終了時間. Defaults to None（クリップの終わりまで）.\n
            resize_ratio_x (float, optional): 画像の横幅のリサイズ比率. Defaults to 1.\n
            resize_ratio_y (float, optional): 画像の縦幅のリサイズ比率. Defaults to 1.
        """
        image_clip = ImageClip(image_path)
        image_clip = image_clip.resize(width=self.clip.size[0]*resize_ratio_x, height=self.clip.size[1]*resize_ratio_y)
        image_clip = image_clip.set_position(position)
        image_clip = image_clip.set_start(start_time)
        if end_time is not None:
            image_clip = image_clip.set_end(end_time)
        else:
            image_clip = image_clip.set_end(self.clip.duration)
        self.clip = CompositeVideoClip([self.clip, image_clip])
        
    def add_audio(self, audio_path, start_time=0, end_time=None):
        """
        音声を追加します。
        
        Args:
            audio_path (str): 追加する音声のパス\n
            start_time (float): クリップに音声を追加する開始時間\n
            end_time (float, optional): クリップに音声を追加する終了時間. Defaults to None（クリップの終わりまで）.
        """
        audio = AudioFileClip(audio_path)
        
        # クリップの終了時間を設定
        if end_time is None:
            end_time = self.clip.duration

        # 音声をクリップの長さに合わせてトリミング
        audio = audio.subclip(0, min(audio.duration, end_time - start_time))

        # 元のクリップの音声を取得（音声がない場合はNone）
        original_audio = self.clip.audio
        
        if original_audio is None:
            # 元のクリップに音声がない場合、新しい音声クリップを作成
            new_audio = audio.set_start(start_time)
        else:
            # 元のクリップに音声がある場合、既存の音声と新しい音声を合成
            new_audio = CompositeAudioClip([original_audio, audio.set_start(start_time)])
        
        # 新しい音声をクリップに設定
        self.clip = self.clip.set_audio(new_audio)
        
    def add_video(self, video_path, position="center", start_time=0, end_time=None, resize_ratio_x=1, resize_ratio_y=1):
        """
        動画を追加します。
        
        Args:
            video_path (str): 追加する動画のパス\n
            position (str, optional): 動画の位置. Defaults to "center".\n
            start_time (float, optional): 動画の開始時間. Defaults to 0.\n
            end_time (float, optional): 動画の終了時間. Defaults to None（クリップの終わりまで）.\n
            resize_ratio_x (float, optional): 動画の横幅のリサイズ比率. Defaults to 1.\n
            resize_ratio_y (float, optional): 動画の縦幅のリサイズ比率. Defaults to 1.
        """
        video_clip = VideoFileClip(video_path)
        video_clip = video_clip.resize(width=self.clip.size[0]*resize_ratio_x, height=self.clip.size[1]*resize_ratio_y)
        video_clip = video_clip.set_position(position)
        video_clip = video_clip.set_start(start_time)
        if end_time is not None:
            video_clip = video_clip.set_end(end_time)
        else:
            video_clip = video_clip.set_end(self.clip.duration)
        self.clip = CompositeVideoClip([self.clip, video_clip])
    
    def add_rectangle(self, position=(0, 0), size=(100, 100), color=(255, 255, 255), start_time=0, end_time=None):
        """
        矩形を追加します。
        
        Args:
            position (tuple, optional): 矩形の位置. Defaults to (0, 0).\n
            size (tuple, optional): 矩形のサイズ. Defaults to (100, 100).\n
            color (tuple, optional): 矩形の色. Defaults to (255, 255, 255).\n
            start_time (float, optional): 矩形の開始時間. Defaults to 0.\n
            end_time (float, optional): 矩形の終了時間. Defaults to None（クリップの終わりまで）.
        """
        rectangle_clip = ColorClip(size=size, color=color)
        rectangle_clip = rectangle_clip.set_position(position)
        rectangle_clip = rectangle_clip.set_start(start_time)
        if end_time is not None:
            rectangle_clip = rectangle_clip.set_end(end_time)
        else:
            rectangle_clip = rectangle_clip.set_end(self.clip.duration)
        self.clip = CompositeVideoClip([self.clip, rectangle_clip])
        
    def add_circle(self, position=(0, 0), radius=50, color=(255, 255, 255), start_time=0, end_time=None):
        """
        円を追加します。
        
        Args:
            position (tuple, optional): 円の位置. Defaults to (0, 0).\n
            radius (int, optional): 円の半径. Defaults to 50.\n
            color (tuple, optional): 円の色. Defaults to (255, 255, 255).\n
            start_time (float, optional): 円の開始時間. Defaults to 0.\n
            end_time (float, optional): 円の終了時間. Defaults to None（クリップの終わりまで）.
        """
        # 透明な背景の画像を作成
        img = Image.new('RGBA', self.clip.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 円を描画
        draw.ellipse([position[0]-radius, position[1]-radius,
                    position[0]+radius, position[1]+radius],
                    fill=color + (255,))  # アルファ値255を追加
        
        # PIL ImageをNumPy配列に変換
        img_array = np.array(img)
        
        # ImageClipを作成
        circle_clip = ImageClip(img_array)
        circle_clip = circle_clip.set_duration(end_time - start_time)
        circle_clip = circle_clip.set_start(start_time)
        if end_time is not None:
            circle_clip = circle_clip.set_end(end_time)
        else:
            circle_clip = circle_clip.set_end(self.clip.duration)
        
        # 既存のクリップに円を合成
        self.clip = CompositeVideoClip([self.clip, circle_clip])
        
    def get_clip(self):
        """
        クリップを取得します。
        
        Returns:
            VideoFileClip: クリップ
        """
        return self.clip
    
    def concatenate_clips(self, clip):
        """
        このクリップに、引数のクリップを後ろに連結します。

        Args:
            clip (moviepy.video.io.VideoFileClip): 連結するクリップ
        """
        self.clip = concatenate_videoclips([self.clip, clip])
        
if __name__ == "__main__":
    test_clip = Movie_maker(duration=5, bg_color=(0,0,0), size=(1920, 1080), fps=60)
    test_clip.add_text("ようこそ。語りのずんだなのだ。", position="center", fontsize=50, color="white", start_time=0, end_time=1)
    test_clip.export_clip("test.mp4")







    
    



