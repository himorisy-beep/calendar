import streamlit as st
import pandas as pd
import datetime
import os
from streamlit_calendar import calendar # 달력 라이브러리

# 1. 페이지 설정
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
        
        # 유형에 따라 달력에 표시될 색상을 미리 정해둡니다
        type_options = {
            "🏖️ 휴가/연차": "#FF6B6B",  # 빨강 (휴가)
            "✈️ 출장/외근": "#4D96FF",  # 파랑 (출장)
            "💻 프로젝트": "#6BCB77",   # 초록 (업무)
            "🔥 긴급/야근": "#FFD93D",  # 노랑 (긴급)
            "📅 기타": "#A2A2A2"       # 회색 (기타)
        }
        schedule_type = st.selectbox("일정 유형", list(type_options.keys()))
        
        # 날짜
        today = datetime.date.today()
        d = st.date_input("기간", (today, today))
        content = st.text_input("내용", placeholder="예: 제안서 마감")
        
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
                st.success("등록 완료!")
                st.rerun()

# 4. 메인 화면: 진짜 달력 그리기
# 데이터프레임을 달력 라이브러리가 이해할 수 있는 리스트 형태로 변환
events = []
if not df.empty:
    for _, row in df.iterrows():
        # 색상 지정
        color = type_options.get(row["유형"], "#3788d8")
        
        # 달력에 표시할 데이터 만들기
        # 주의: 종료일에 +1일을 해야 달력에 꽉 차게 표시됩니다 (라이브러리 특성)
        end_date_obj = pd.to_datetime(row["종료일"]) + datetime.timedelta(days=1)
        
        events.append({
            "title": f"[{row['이름']}] {row['내용']}",
            "start": str(row["시작일"]),
            "end": end_date_obj.strftime("%Y-%m-%d"),
            "backgroundColor": color,
            "borderColor": color,
        })

# 달력 설정 (옵션)
calendar_options = {
    "editable": "true",
    "navLinks": "true",
    "headerToolbar": {
        "left": "today prev,next",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek,timeGridDay,listMonth"
    },
    "initialView": "dayGridMonth", # 기본을 월별 달력으로 설정
}

# 달력 출력
st.markdown("### 🗓️ 월별 스케줄 확인")
calendar(events=events, options=calendar_options, custom_css="""
    .fc-event-title {
        font-weight: bold;
    }
""")

# 5. 리스트 및 삭제 기능
st.divider()
with st.expander("🗑️ 일정 목록 및 삭제"):
    st.dataframe(df, use_container_width=True)
    
    del_idx = st.selectbox("삭제할 일정 선택", df.index, 
                           format_func=lambda x: f"{df.loc[x,'이름']} - {df.loc[x,'내용']}")
    if st.button("삭제하기"):
        df = df.drop(del_idx)
        save_data(df)
        st.success("삭제되었습니다.")
        st.rerun()

