from moviepy.editor import AudioFileClip
import datetime
import shutil
import os
import requests
import json
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
      "description": "",
      "start_time": ""
    },
    {
      "part": "",
      "description": "",
      "start_time": ""
    },
    {
      "part": "",
      "description": "",
      "start_time": ""
    }
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
        print(f"视频目录 {video_dir} 创建成功！")
        os.makedirs(voice_dir, exist_ok=True)
        print(f"音频目录 {voice_dir} 创建成功！")
    except Exception as e:
        print("创建目录失败:", e)

def generate_timestamp():
    current_time = datetime.datetime.now()
    timestamp_str = current_time.strftime("%Y%m%d%H%M%S")
    return timestamp_str

def generate_filename(timestamp_str):
    video_path = "src/video/" + timestamp_str + ".mp4"
    voice_path = "src/voice/" + timestamp_str + ".mp3"
    return (video_path, voice_path)

def copy_video_file(input_video_path, video_path):
    try:
        shutil.copy(input_video_path, video_path)
        print("文件复制成功！")
    except Exception as e:
        print("文件复制失败:", e)

def extract_audio(video_path, voice_path):
    try:
        my_video_clip = AudioFileClip(video_path)
        my_video_clip.write_audiofile(voice_path)
    except Exception as e:
        print("提取音频失败:", e)

def asr(voice_path):
    headers = {
        'Authorization': f'Bearer {api_config.APIKEY}',
    }
    url = api_config.asr_url
    files = {'file': open(voice_path, "rb")}
    query = {
        "model": "whisper-1",
        "language": "zh",
        "response_format": "json",
        "timestamps": True
    }
    response = requests.post(url=url, data=query, files=files, headers=headers)
    return response.json()

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

    for choice in response_json["choices"]:
        content = choice["message"]["content"]

    return content

if __name__ == "__main__":
    create_directories()
    timestamp_str = generate_timestamp()
    video_path, voice_path = generate_filename(timestamp_str)
    copy_video_file(input_video_path, video_path)
    extract_audio(video_path, voice_path)
    voice_response = asr(voice_path)
    
    # Extracting text and timestamps from ASR response
    segments = voice_response['segments']
    paragraphs = []
    current_paragraph = []
    start_time = None
    
    for segment in segments:
        words = segment['words']
        for word in words:
            if start_time is None:
                start_time = word['start']
            current_paragraph.append(word['text'])
            if word['text'].endswith(('.', '!', '?')):
                paragraphs.append((start_time, " ".join(current_paragraph)))
                current_paragraph = []
                start_time = word['end'] if words else None

    summaries = []
    for start_time, paragraph in paragraphs:
        summary_text = generate_summary(paragraph)
        summaries.append({
            'part': paragraph,
            'description': summary_text,
            'start_time': start_time
        })

    # Generate final JSON structure
    final_output = {
        "title": "视频摘要",
        "parts": summaries
    }

    print(json.dumps(final_output, ensure_ascii=False, indent=2))
