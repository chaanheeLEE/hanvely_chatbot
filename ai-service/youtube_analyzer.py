import os
import time
from google import genai

def analyze_video_with_gemini(video_path):
    """
    Google Gemini API를 이용해 로컬 동영상 파일(mp4 등)을 업로드하고 분석합니다.
    (사용자가 직접 동영상 파일을 첨부할 때 사용)
    """
    client = genai.Client()
    
    print("Gemini에 영상을 업로드하고 있습니다...")
    video_file = client.files.upload(file=video_path)
    
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

def analyze_youtube_url_with_gemini(youtube_url):
    """
    Google Gemini API를 이용해 다운로드 없이 YouTube 링크를 직접 분석합니다.
    """
    from google.genai import types
    # 환경변수에 GEMINI_API_KEY 가 설정되어 있어야 합니다.
    client = genai.Client()
    
    print("Gemini API에 YouTube 링크를 전송하여 분석을 시작합니다...")

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
        contents=types.Content(
            parts=[
                types.Part(
                    file_data=types.FileData(file_uri=youtube_url)
                ),
                types.Part.from_text(text=prompt)
            ]
        )
    )
    
    return response.text
