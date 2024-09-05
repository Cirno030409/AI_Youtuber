import requests
import json
import soundfile as sf

# VOICEVOXエンジンのURL（デフォルトのポート番号は50021）
BASE_URL = "http://localhost:50021"


def generate_voice(text, speaker=1, output_path="resources/voice/", speed=1.0):
    """
    VOICEVOXで音声を生成します。VOICEVOXのエンジンを立ち上げておく必要があります。

    Args:
        text (str): 音声合成するテキスト
        speaker (int, optional): 声の種類. Defaults to 1.
        output_file (str, optional): 音声ファイルの出力先. Defaults to "output.wav".
        speed (float, optional): 話す速さ. Defaults to 1.0.
        style (int, optional): 声の種類. Defaults to 0. 
        
    話者: ずんだもん
    Speaker: 3, 名前: ノーマル
    Speaker: 1, 名前: あまあま
    Speaker: 7, 名前: ツンツン
    Speaker: 5, 名前: セクシー
    Speaker: 22, 名前: ささやき
    Speaker: 38, 名前: ヒソヒソ
    Speaker: 75, 名前: ヘロヘロ
    Speaker: 76, 名前: なみだめ
    """
    # 音声合成用のクエリを作成
    query_payload = {"text": text, "speaker": speaker}

    query_response = requests.post(f"{BASE_URL}/audio_query", params=query_payload)
    query_data = query_response.json()


    # 話す速さを設定
    query_data["speedScale"] = speed

    # 音声合成を実行
    synthesis_payload = {"speaker": speaker}
    synthesis_response = requests.post(
        f"{BASE_URL}/synthesis",
        headers={"Content-Type": "application/json"},
        params=synthesis_payload,
        data=json.dumps(query_data)
    )

    # 音声データを保存
    with open(output_path, "wb") as f:
        f.write(synthesis_response.content)


if __name__ == "__main__":
    generate_voice("こんにちは、ずんだもんなのだ！", speaker=22, output_file="resources/voicevox.wav", speed=1.2)
    response = requests.get(f"{BASE_URL}/speakers")
    speakers_data = response.json()

    # for speaker in speakers_data:
    #     print(f"話者: {speaker['name']}")
    #     for style in speaker['styles']:
    #         print(f"  スタイルID: {style['id']}, 名前: {style['name']}")
    #     print()