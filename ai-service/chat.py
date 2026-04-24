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



import os
import re
from youtube_analyzer import analyze_youtube_url_with_gemini, analyze_video_with_gemini

with st.sidebar:
    st.header("📂 로컬 영상 분석")
    st.caption("유튜브 링크 대신 직접 블랙박스 영상을 업로드할 수 있습니다.")
    uploaded_file = st.file_uploader("동영상 파일 첨부 (mp4, mov 등)", type=["mp4", "mov", "avi"])
    analyze_btn = st.button("첨부한 영상으로 분석 시작", use_container_width=True)

# 파일 업로드 분석 처리
if analyze_btn and uploaded_file is not None:
    # 1. 채팅창에 사용자 요청 표시
    user_msg = f"📁 업로드된 영상 분석 요청: `{uploaded_file.name}`"
    with st.chat_message("user"):
        st.write(user_msg)
    st.session_state.message_list.append({"role": "user", "content": user_msg})

    import time
    # 2. 임시 파일로 저장 (한글 파일명 오류 방지를 위해 타임스탬프 기반 영문 파일명 사용)
    safe_ext = uploaded_file.name.split('.')[-1] if '.' in uploaded_file.name else 'mp4'
    temp_file_path = f"temp_upload_{int(time.time())}.{safe_ext}"
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # 3. 분석 시작
    with st.spinner("Gemini API가 업로드된 영상을 분석하는 중입니다. ⏳"):
        try:
            video_summary = analyze_video_with_gemini(temp_file_path)
            
            summary_message = f"🎥 **영상 분석 결과 (Gemini)** 🎥\n\n{video_summary}"
            with st.chat_message("ai"):
                st.markdown(summary_message)
            st.session_state.message_list.append({"role": "ai", "content": summary_message})
            
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
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

if user_question := st.chat_input(placeholder="교통사고에 관련된 궁금한 내용이나 유튜브 블랙박스 영상 링크를 말씀해주세요!"):
    with st.chat_message("user"):
        st.write(user_question)
    st.session_state.message_list.append({"role": "user", "content": user_question})

    # 유튜브 링크 정규표현식 검사 (쇼츠 포함)
    youtube_pattern = re.compile(r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/(watch\?v=|shorts/|embed/|v/)?([a-zA-Z0-9_\-]{11})')
    match = youtube_pattern.search(user_question)

    if match:
        youtube_url = match.group(0)
        
        with st.spinner("Gemini API가 유튜브 영상을 시청하고 분석하는 중입니다. ⏳"):
            try:
                # 제미나이 영상 분석 (다이렉트 URL)
                video_summary = analyze_youtube_url_with_gemini(youtube_url)
                
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
