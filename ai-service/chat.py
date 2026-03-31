import streamlit as st


from dotenv import load_dotenv


from llm import get_ai_response

st.set_page_config(page_title="한블리 챗봇", page_icon="🤖")

st.title("🤖 한블리 챗봇")
st.caption("교통사고에 관련된 과실비율을 알려드립니다!")

load_dotenv()

if 'message_list' not in st.session_state:
    st.session_state.message_list = []

# print(f"before: {st.session_state.message_list}")
for message in st.session_state.message_list:
    with st.chat_message(message["role"]):
        st.write(message["content"])



import re
from youtube_analyzer import download_youtube_video, analyze_video_with_gemini

if user_question := st.chat_input(placeholder="교통사고에 관련된 궁금한 내용이나 유튜브 블랙박스 영상 링크를 말씀해주세요!"):
    with st.chat_message("user"):
        st.write(user_question)
    st.session_state.message_list.append({"role": "user", "content": user_question})

    # 유튜브 링크 정규표현식 검사 (쇼츠 포함)
    youtube_pattern = re.compile(r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/(watch\?v=|shorts/|embed/|v/)?([a-zA-Z0-9_\-]{11})')
    match = youtube_pattern.search(user_question)

    if match:
        youtube_url = match.group(0)
        
        with st.spinner("유튜브 영상을 다운로드하고 AI로 분석하는 중입니다. (1~2분 정도 소요될 수 있습니다) ⏳"):
            try:
                # 1. 유튜브 다운로드
                video_path = download_youtube_video(youtube_url, "temp_video.mp4")
                
                # 2. 제미나이 영상 분석
                video_summary = analyze_video_with_gemini(video_path)
                
                # 영상 분석 결과 중간 출력
                summary_message = f"🎥 **영상 분석 결과 (Gemini)** 🎥\n\n{video_summary}"
                with st.chat_message("ai"):
                    st.markdown(summary_message)
                st.session_state.message_list.append({"role": "ai", "content": summary_message})
                
                # 3. 모델에 최종 질문 (과실비율 및 판례 검색)
                ai_query = f"다음은 사고 영상의 분석 내용입니다. 이 상황과 가장 유사한 사례나 판례를 문서에서 찾아서, 과실비율과 유의해야할 점을 함께 설명해주세요.\n\n[사고상황요약]: {video_summary}"
                
                with st.spinner("분석된 내용을 바탕으로 과실비율을 계산하는 중입니다..."):
                    ai_response = get_ai_response(ai_query)
                    with st.chat_message("ai"):
                        ai_message = st.write_stream(ai_response)
                        st.session_state.message_list.append({"role": "ai", "content": ai_message})

            except Exception as e:
                error_msg = f"영상을 분석하는 중 오류가 발생했습니다: {e}"
                with st.chat_message("ai"):
                    st.error(error_msg)
                st.session_state.message_list.append({"role": "ai", "content": error_msg})
    else:
        # 일반 질문일 경우 (기존 체인 동작)
        with st.spinner("답변을 생성하는 중입니다"):
            ai_response = get_ai_response(user_question)
            with st.chat_message("ai"):
                ai_message = st.write_stream(ai_response)
                st.session_state.message_list.append({"role": "ai", "content": ai_message})
