from dotenv import load_dotenv
from llm import get_ai_response
from youtube_analyzer import download_youtube_video, analyze_video_with_gemini

def main():
    load_dotenv()
    
    print("===================================")
    print("🚗 한블리 파이썬 터미널 챗봇 🚗")
    print("===================================")
    print("유튜브 영상을 분석하고 싶으시다면 링크(http)를 입력하시고,")
    print("그저 질문하시려면 궁금한 점을 입력해주세요. (종료하려면 'exit' 입력)")
    
    while True:
        user_input = input("\n사용자: ")
        
        if user_input.lower() == 'exit':
            print("챗봇을 종료합니다.")
            break
            
        if user_input.startswith("http"):
            # 1. 유튜브 영상 다운로드 및 Gemini로 요약
            try:
                video_path = download_youtube_video(user_input, "temp_video.mp4")
                print(">> 비디오 분석 중...")
                
                # Gemini 영상 분석
                video_summary = analyze_video_with_gemini(video_path)
                
                print("\n[AI의 영상 사고 상황 분석]")
                print(video_summary)
                
                # 2. 분석된 영상 요약 내용을 RAG 기반 llm (기존 챗봇 체인) 에 넘겨 과실 비율 계산
                print("\n[이제 기존 RAG 챗봇을 활용해 정리된 상황에 맞는 과실비율을 검색합니다...]")
                ai_query = f"다음은 사고 영상의 분석 내용입니다. 상황에 알맞은 과실비율과 유의해야할 점을 판례와 더불어 설명해주세요.\n\n[사고상황요약]: {video_summary}"
                
                ai_response_stream = get_ai_response(ai_query)
                
                print("\nAI(과실비율 평가): ", end="")
                for chunk in ai_response_stream:
                    print(chunk, end="", flush=True)
                print()
                
            except Exception as e:
                print(f"영상 분석 중 오류가 발생했습니다: {e}")
        else:
            # 기존 일반 질문 처리 (RAG)
            ai_response_stream = get_ai_response(user_input)
            
            print("AI: ", end="")
            for chunk in ai_response_stream:
                print(chunk, end="", flush=True)
            print()

if __name__ == "__main__":
    main()
