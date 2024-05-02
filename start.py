from moviepy.editor import AudioFileClip
import datetime
import shutil
import whisper

input_video_path="./RPReplay.mp4"
whisper_model = "medium"
whisper_language = "zh"

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

if __name__ == "__main__":
    timestamp_str=generate_timestamp()
    video_path,voice_path=generate_filename(timestamp_str)
    copy_video_file(input_video_path,video_path)
    extract_audio(video_path,voice_path)
    voice_text=asr(voice_path)