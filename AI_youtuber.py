from gtts import gTTS
import pydub
from pydub import effects
import time
import simpleaudio as sa

def generate_voice(text, output_file="yukkuri_voice.wav", speed=1.0):
    # 通常の音声を生成
    tts = gTTS(text=text, lang='ja')
    tts.save("temp.wav")
    
    
    # SimpleAudioで再生
    wave_obj = sa.WaveObject.from_wave_file("temp.wav")
    play_obj = wave_obj.play()
    play_obj.wait_done()  # 再生が終わるまで待機

# 使用例
text = "こんにちは、ゆっくりです。"
generate_voice(text, speed=1.5)