from moviepy.editor import AudioFileClip
import datetime
import shutil
import whisper
import ollama
import os

input_video_path="./RPReplay.mp4"
whisper_model = "medium"
whisper_language = "zh"
llm_model="ClipVividSnap-qwen-7b"
sys_prompt="""
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
  ]
}

```
下面，我将给你需要处理的文本内容：
"""


def create_directories():
    # 定义目录路径
    video_dir = "./src/video/"
    voice_dir = "./src/voice/"
    
    try:
        # 创建视频目录
        os.makedirs(video_dir, exist_ok=True)
        print(f"视频目录 {video_dir} 创建成功！")
        
        # 创建音频目录
        os.makedirs(voice_dir, exist_ok=True)
        print(f"音频目录 {voice_dir} 创建成功！")
    except Exception as e:
        print("创建目录失败:", e)

def generate_timestamp():
    # 获取当前时间
    current_time = datetime.datetime.now()
    # 格式化时间戳字符串
    timestamp_str = current_time.strftime("%Y%m%d%H%M%S")
    return timestamp_str

def generate_filename(timestamp_str):
    video_path="src/video/"+timestamp_str+".mp4"
    voice_path="src/voice/"+timestamp_str+".mp3"
    return (video_path,voice_path)

def copy_video_file(input_video_path, video_path):
    try:
        shutil.copy(input_video_path, video_path)
        print("文件复制成功！")
    except Exception as e:
        print("文件复制失败:", e)

def extract_audio(video_path, voice_path):
    try:
        # 加载视频文件
        my_video_clip = AudioFileClip(video_path)
        # 提取音频并保存
        my_video_clip.write_audiofile(voice_path)
        print("音频提取成功！")
    except Exception as e:
        print("提取音频失败:", e)

def asr(voice_path):
    print("ASR Processing...")
    model = whisper.load_model(whisper_model)
    result = model.transcribe(voice_path, language=whisper_language)
    print(result["text"])
    return(result["text"])

def generate_summary(voice_text):
    print("Generating Summary...")
    text_summary=ollama.generate(model=llm_model, prompt=voice_text)
    text_summary=text_summary['response']
    return(text_summary)

if __name__ == "__main__":
    create_directories()
    timestamp_str=generate_timestamp()
    video_path,voice_path=generate_filename(timestamp_str)
    copy_video_file(input_video_path,video_path)
    extract_audio(video_path,voice_path)
    voice_text=asr(voice_path)
    text_summary=generate_summary(sys_prompt+voice_text)
    print(text_summary)