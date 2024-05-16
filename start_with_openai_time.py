import os
import shutil
import datetime
import requests
from moviepy.editor import AudioFileClip
from pydub import AudioSegment
from pydub.silence import split_on_silence
import api_config

input_video_path = "./RPReplay.mp4"
sys_prompt = """
你是一个视频总结机器人，而且你是精通json数据格式生成的专家。你已稳定运行多年，从未出现过错误。
你会收到一段从视频的音频中提取的文字。
你的能力是对文本内容进行分析，并总结出json格式的数据。
在“title”中生成全文总结，然后把全文分为数个part概括，在parts中的每个part生成每个部分的标题，并在对应的“description”中生成小结描述这个part。
请严格按照json格式输出，不需要输出其他内容。
json格式示例如下：

```json
{
  "title": "",
  "parts": [
    {
      "part": "",
      "description": ""
    },
    {
      "part": "",
      "description": ""
    },
    {
      "part": "",
      "description": ""
    },
    // Increase or decrease parts according to needs
  ]
}

```
下面，我将给你需要处理的文本内容：
"""

def create_directories():
    video_dir = "./src/video/"
    voice_dir = "./src/voice/"
    
    try:
        os.makedirs(video_dir, exist_ok=True)
        os.makedirs(voice_dir, exist_ok=True)
    except Exception as e:
        print("创建目录失败:", e)

def generate_timestamp():
    current_time = datetime.datetime.now()
    timestamp_str = current_time.strftime("%Y%m%d%H%M%S")
    return timestamp_str

def generate_filename(timestamp_str):
    video_path = "src/video/" + timestamp_str + ".mp4"
    voice_path = "src/voice/" + timestamp_str + ".mp3"
    return video_path, voice_path

def copy_video_file(input_video_path, video_path):
    try:
        shutil.copy(input_video_path, video_path)
    except Exception as e:
        print("文件复制失败:", e)

def extract_audio(video_path, voice_path):
    try:
        my_video_clip = AudioFileClip(video_path)
        my_video_clip.write_audiofile(voice_path)
    except Exception as e:
        print("提取音频失败:", e)

def asr(voice_path):
    headers = {'Authorization': f'Bearer {api_config.APIKEY}'}
    url = api_config.asr_url
    files = {'file': open(voice_path, "rb")}
    query = {
        "model": "whisper-1",
        "language": "zh",
        "response_format": "json",
    }
    response = requests.post(url=url, data=query, files=files, headers=headers)
    response_json = response.json()
    print("ASR Response:", response_json)  # 打印ASR响应进行调试
    return response_json.get('text', '')

def split_audio_on_silence(audio_path):
    audio = AudioSegment.from_file(audio_path)
    chunks = split_on_silence(audio, min_silence_len=500, silence_thresh=-40)

    segments = []
    start_time = 0

    for chunk in chunks:
        end_time = start_time + len(chunk)
        segments.append((chunk, start_time / 1000.0, end_time / 1000.0))
        start_time = end_time

    return segments

def generate_summary(voice_text):
    url = api_config.chat_url
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_config.APIKEY}'
    }

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": voice_text},
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    response_json = response.json()
    print("Summary API Response:", response_json)  # 打印API响应进行调试

    if 'choices' not in response_json:
        raise KeyError(f"API响应中缺少'choices'键：{response_json}")

    for choice in response_json["choices"]:
        content = choice["message"]["content"]
    
    return content

if __name__ == "__main__":
    create_directories()
    timestamp_str = generate_timestamp()
    video_path, voice_path = generate_filename(timestamp_str)
    copy_video_file(input_video_path, video_path)
    extract_audio(video_path, voice_path)

    voice_segments = split_audio_on_silence(voice_path)
    summaries = []

    for chunk, start_time, end_time in voice_segments:
        chunk.export("temp_chunk.wav", format="wav")
        voice_text = asr("temp_chunk.wav")
        if not voice_text:
            print(f"无法从音频段落中获取文字: 开始时间 {start_time}, 结束时间 {end_time}")
            continue
        summary = generate_summary(voice_text)
        summaries.append({
            'start_time': start_time,
            'end_time': end_time,
            'summary': summary
        })
        os.remove("temp_chunk.wav")

    output = {
        "title": "视频总结",
        "parts": [{"part": f"Part {i+1}", "description": s['summary'], "start_time": s['start_time'], "end_time": s['end_time']} for i, s in enumerate(summaries)]
    }

    print(output)