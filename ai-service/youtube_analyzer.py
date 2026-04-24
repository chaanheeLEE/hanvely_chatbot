import os
import time
import yt_dlp
from google import genai

def download_youtube_video(url, output_path="temp_video.mp4"):
    ydl_opts = {
        # 쇼츠(세로 영상)는 높이가 1080, 1280이므로 height 제한을 풀거나 범용적인 mp4 선택
        'format': 'best[ext=mp4]/best', 
        'outtmpl': output_path,
        'noplaylist': True,
        'quiet': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web']
            }
        }
    }
    print("유튜브 영상을 다운로드 중입니다...")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    print("다운로드 완료!")
    return output_path

def analyze_video_with_gemini(video_path):
    """
    Google Gemini API를 이용해 다운로드된 영상을 분석합니다.
    """
    # 환경변수에 GEMINI_API_KEY 가 설정되어 있어야 합니다.
    client = genai.Client()
    
    print("Gemini에 영상을 업로드하고 있습니다...")
    video_file = client.files.upload(file=video_path)
    
    # 업로드가 완료되었으므로 로컬 임시 영상 파일은 삭제합니다.
    try:
        if os.path.exists(video_path):
            os.remove(video_path)
    except Exception as e:
        print(f"임시 파일 삭제 실패: {e}")
        
    # 영상 처리(Processing)가 끝날 때까지 대기
    print("영상을 처리하는 중입니다. 잠시만 기다려주세요...")
    while video_file.state == "PROCESSING":
        time.sleep(2)
        video_file = client.files.get(name=video_file.name)
        
    if video_file.state == "FAILED":
        raise Exception("비디오 처리 실패")
        
    print("영상 처리 완료! 분석을 시작합니다.")

    prompt = """
        당신은 교통사고 전문 분석관입니다. 
        이 블랙박스 또는 영상에서 일어난 교통사고 상황을 아주 자세하게 설명해주세요. 
        - 사고 발생 전 차량들의 움직임
        - 충돌 부위 및 상황 (누가 어떻게 부딪혔는지)
        - 과실을 판단할만한 위험 행동이나 법규 위반 여부 (신호위반, 차선변경 등)
        이를 바탕으로 어떤 상황이었는지 한 문단으로 명확히 요약해주고, 과실 책임을 판단하기 위한 근거 텍스트를 제공해주세요.
    """

    response = client.models.generate_content(
        model='gemini-3-flash-preview',
        contents=[
            video_file,
            prompt
        ]
    )
    
    return response.text
