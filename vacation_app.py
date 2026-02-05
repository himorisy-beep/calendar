import streamlit as st
import pandas as pd
import datetime
import os
from streamlit_calendar import calendar

# 1. 페이지 설정 (레이아웃을 'wide'로 유지하되, 제목 여백을 줄임)
st.set_page_config(page_title="팀 캘린더", layout="wide")
st.title("📅 우리 팀 통합 달력")

# 데이터 파일
DATA_FILE = "team_calendar.csv"

# 2. 데이터 관리 함수
def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=["이름", "시작일", "종료일", "유형", "내용"])
    df = pd.read_csv(DATA_FILE)
    return df

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

df = load_data()

# 3. 사이드바: 일정 등록
with st.sidebar:
    st.header("📝 일정 추가하기")
    with st.form("add_event"):
        name = st.text_input("이름", placeholder="예: 홍길동")
        
        type_options = {
            "📑 제안": "#9C27B0",    # 보라
            "🏖️ 휴가 (종일)": "#FF6B6B",   # 빨강
            "🌅 오전 반차": "#FFB347",    # 주황
            "🌇 오후 반차": "#FFCC00",    # 노랑
            "✈️ 출장/외근": "#4D96FF",    # 파랑
            "💻 프로젝트": "#6BCB77",     # 초록
            "🔥 긴급/야근": "#E91E63",    # 진분홍
            "📅 기타": "#A2A2A2"         # 회색
        }
        
        schedule_type = st.selectbox("일정 유형", list(type_options.keys()))
        
        today = datetime.date.today()
        d = st.date_input("기간 (시작일 ~ 종료일)", (today, today))
        content = st.text_input("내용", placeholder="예: 인니 보건인력 PMC 제안서 작성")
        
        if st.form_submit_button("등록"):
            if len(d) == 2:
                start, end = d
                new_row = pd.DataFrame({
                    "이름": [name],
                    "시작일": [start],
                    "종료일": [end],
                    "유형": [schedule_type],
                    "내용": [content]
                })
                df = pd.concat([df, new_row], ignore_index=True)
                save_data(df)
                st.success("등록되었습니다!")
                st.rerun()

# 4. 메인 화면: 달력 표시
events = []
if not df.empty:
    for _, row in df.iterrows():
        color = type_options.get(row["유형"], "#3788d8")
        end_date_obj = pd.to_datetime(row["종료일"]) + datetime.timedelta(days=1)
        
        events.append({
            "title": f"[{row['이름']}] {row['내용']}",
            "start": str(row["시작일"]),
            "end": end_date_obj.strftime("%Y-%m-%d"),
            "backgroundColor": color,
            "borderColor": color,
            "allDay": True 
        })

# --- 여기가 핵심 수정 부분입니다! ---
calendar_options = {
    "editable": "true",
    "navLinks": "true",
    "headerToolbar": {
        "left": "today prev,next",
        "center": "title",
        "right": "dayGridMonth,listMonth"
    },
    "initialView": "dayGridMonth",
    "height": 700,        # ★ 높이를 700px로 고정 (화면에 딱 맞춤)
    "contentHeight": 650, # ★ 내용물 높이 조절
    "aspectRatio": 1.8,   # ★ 가로를 더 넓게 써서 세로 길이를 줄임
}

st.markdown("### 🗓️ 월별 스케줄")

# 범례
st.markdown("""
<div style="display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 10px; font-size: 0.9em;">
    <span style="color:#FF6B6B">■ 휴가</span>
    <span style="color:#FFB347">■ 반차</span>
    <span style="color:#9C27B0; font-weight:bold;">■ 제안</span>
    <span style="color:#4D96FF">■ 출장</span>
    <span style="color:#6BCB77">■ 프로젝트</span>
</div>
""", unsafe_allow_html=True)

# 달력 출력
calendar(events=events, options=calendar_options, custom_css="""
    .fc-event-title {
        font-weight: bold;
        font-size: 0.85em; /* 글자 크기 살짝 줄여서 깔끔하게 */
    }
    .fc-toolbar-title {
        font-size: 1.5em !important; /* 달력 제목 크기 조절 */
    }
""")

# 5. 리스트 및 삭제
st.divider()
with st.expander("🗑️ 등록된 일정 목록"):
    st.dataframe(df, use_container_width=True)
    
    if not df.empty:
        del_idx = st.selectbox("삭제할 일정 선택", df.index, 
                               format_func=lambda x: f"[{df.loc[x,'유형']}] {df.loc[x,'이름']} - {df.loc[x,'내용']}")
        if st.button("삭제하기"):
            df = df.drop(del_idx)
            save_data(df)
            st.success("삭제되었습니다.")
            st.rerun()

