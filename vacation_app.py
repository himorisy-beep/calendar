import streamlit as st
import pandas as pd
import datetime
import os
from streamlit_calendar import calendar

# 1. 페이지 설정
st.set_page_config(page_title="팀 캘린더", layout="wide")
st.title("📅 해외 팀 통합 달력")

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
        
        # 유형 및 색상 설정 (반차 추가됨)
        type_options = {
            "🏖️ 연차 (종일)": "#FF6B6B",   # 빨강 (하루 종일)
            "🌅 오전 반차": "#FFB347",    # 파스텔 오렌지 (오전에 없음)
            "🌇 오후 반차": "#FFCC00",    # 진한 노랑 (오후에 없음)
            "✈️ 출장/외근": "#4D96FF",    # 파랑
            "💻 프로젝트": "#6BCB77",     # 초록
            "🔥 긴급/야근": "#A068FF",    # 보라 (눈에 띄게 변경)
            "📅 기타": "#A2A2A2"         # 회색
        }
        
        # 선택박스
        schedule_type = st.selectbox("일정 유형", list(type_options.keys()))
        
        # 날짜
        today = datetime.date.today()
        d = st.date_input("기간", (today, today))
        content = st.text_input("내용", placeholder="예: 개인 사정, 병원 진료 등")
        
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

# 4. 메인 화면: 달력 표시
events = []
if not df.empty:
    for _, row in df.iterrows():
        # 유형에 맞는 색상 가져오기 (없으면 기본 파랑)
        color = type_options.get(row["유형"], "#3788d8")
        
        # 종료일 보정 (+1일 해야 달력에 맞게 표시됨)
        end_date_obj = pd.to_datetime(row["종료일"]) + datetime.timedelta(days=1)
        
        events.append({
            "title": f"[{row['이름']}] {row['내용']}",
            "start": str(row["시작일"]),
            "end": end_date_obj.strftime("%Y-%m-%d"),
            "backgroundColor": color,
            "borderColor": color,
            # 반차인 경우 'allDay' 속성을 조절할 수도 있지만, 
            # 간단히 색상으로 구분하는 것이 달력 보기엔 가장 깔끔합니다.
        })

# 달력 옵션
calendar_options = {
    "editable": "true",
    "navLinks": "true",
    "headerToolbar": {
        "left": "today prev,next",
        "center": "title",
        "right": "dayGridMonth,listMonth" 
    },
    "initialView": "dayGridMonth",
}

# 달력 출력
st.markdown("### 🗓️ 월별 스케줄 (반차 포함)")
st.info("💡 팁: '오전 반차'는 주황색, '오후 반차'는 노란색으로 표시됩니다.")

calendar(events=events, options=calendar_options, custom_css="""
    .fc-event-title {
        font-weight: bold;
    }
""")

# 5. 리스트 및 삭제
st.divider()
with st.expander("🗑️ 일정 목록 및 삭제"):
    st.dataframe(df, use_container_width=True)
    
    del_idx = st.selectbox("삭제할 일정 선택", df.index, 
                           format_func=lambda x: f"[{df.loc[x,'유형']}] {df.loc[x,'이름']} - {df.loc[x,'내용']}")
    if st.button("삭제하기"):
        df = df.drop(del_idx)
        save_data(df)
        st.success("삭제되었습니다.")
        st.rerun()

