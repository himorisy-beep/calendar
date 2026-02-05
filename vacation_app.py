import streamlit as st
import pandas as pd
import datetime
import os
from streamlit_calendar import calendar

# 1. 페이지 설정
st.set_page_config(page_title="팀 캘린더", layout="wide")
st.title("📅 우리 팀 통합 달력")

# 데이터 파일
DATA_FILE = "team_calendar.csv"

# 2. 데이터 관리 함수
def load_data():
    if not os.path.exists(DATA_FILE):
        # 인덱스 관리를 위해 데이터프레임 생성 시 인덱스를 명확히 합니다.
        return pd.DataFrame(columns=["이름", "시작일", "종료일", "유형", "내용"])
    df = pd.read_csv(DATA_FILE)
    df['시작일'] = df['시작일'].astype(str)
    df['종료일'] = df['종료일'].astype(str)
    return df

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# 전역 데이터 로드
if "df" not in st.session_state:
    st.session_state.df = load_data()

# 공통 설정: 일정 유형 및 색상
type_options = {
    "📑 제안": "#9C27B0",         # 보라
    "💻 프로젝트": "#6BCB77",      # 초록
    "🏖️ 휴가 (종일)": "#FF6B6B",   # 빨강
    "🌅 오전 반차": "#FFB347",     # 주황
    "🌇 오후 반차": "#FFCC00",     # 노랑
    "✈️ 출장/외근": "#4D96FF",     # 파랑
    "🔥 긴급/야근": "#E91E63",     # 진분홍
    "📅 기타": "#A2A2A2"          # 회색
}

# --- [기능 1] 팝업창(Dialog) 함수 정의 ---
@st.dialog("✏️ 일정 수정/삭제")
def open_edit_modal(idx, row):
    # 팝업창 내부 디자인
    st.write(f"**{row['이름']}**님의 일정을 수정합니다.")
    
    with st.form("modal_form"):
        new_name = st.text_input("이름", value=row['이름'])
        
        # 유형 선택
        try:
            type_index = list(type_options.keys()).index(row['유형'])
        except ValueError:
            type_index = 0
        new_type = st.selectbox("일정 유형", list(type_options.keys()), index=type_index)

        # 날짜 처리
        try:
            s_date = datetime.datetime.strptime(str(row['시작일']), "%Y-%m-%d").date()
            e_date = datetime.datetime.strptime(str(row['종료일']), "%Y-%m-%d").date()
        except:
            s_date = datetime.date.today()
            e_date = datetime.date.today()
            
        new_dates = st.date_input("기간", (s_date, e_date))
        new_content = st.text_input("내용", value=row['내용'])
        
        col1, col2 = st.columns(2)
        submit = col1.form_submit_button("💾 수정 저장", type="primary")
        delete = col2.form_submit_button("🗑️ 삭제하기")

        if submit:
            if len(new_dates) == 2:
                # 데이터 수정
                st.session_state.df.at[idx, '이름'] = new_name
                st.session_state.df.at[idx, '유형'] = new_type
                st.session_state.df.at[idx, '시작일'] = new_dates[0]
                st.session_state.df.at[idx, '종료일'] = new_dates[1]
                st.session_state.df.at[idx, '내용'] = new_content
                save_data(st.session_state.df)
                st.rerun()
            else:
                st.error("기간을 확인해주세요.")
        
        if delete:
            st.session_state.df = st.session_state.df.drop(idx).reset_index(drop=True)
            save_data(st.session_state.df)
            st.rerun()

# --- [기능 2] 사이드바 (등록 기능만 남김) ---
with st.sidebar:
    st.header("📝 새 일정 등록")
    with st.form("add_event"):
        name = st.text_input("이름", placeholder="예: 홍길동")
        schedule_type = st.selectbox("일정 유형", list(type_options.keys()))
        today = datetime.date.today()
        d = st.date_input("기간", (today, today))
        content = st.text_input("내용", placeholder="예: 제안서 작성")
        
        if st.form_submit_button("등록하기"):
            if len(d) == 2:
                start, end = d
                new_row = pd.DataFrame({
                    "이름": [name],
                    "시작일": [start],
                    "종료일": [end],
                    "유형": [schedule_type],
                    "내용": [content]
                })
                st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
                save_data(st.session_state.df)
                st.success("등록되었습니다!")
                st.rerun()

# --- [기능 3] 메인 화면: 달력 ---
events = []
df = st.session_state.df

if not df.empty:
    for idx, row in df.iterrows():
        color = type_options.get(row["유형"], "#3788d8")
        start_str = str(row["시작일"])
        end_str = str(row["종료일"])

        # 이벤트 객체 생성 (extendedProps에 인덱스 정보 숨겨두기 ★중요)
        event_dict = {
            "title": f"[{row['이름']}] {row['내용']}",
            "backgroundColor": color,
            "borderColor": color,
            "extendedProps": {"index": idx} # 클릭했을 때 몇 번째 데이터인지 알기 위해
        }

        # 반차/종일 구분 로직
        if row["유형"] == "🌅 오전 반차":
            event_dict["start"] = f"{start_str}T09:00:00"
            event_dict["end"] = f"{start_str}T13:00:00"
            event_dict["allDay"] = False
        elif row["유형"] == "🌇 오후 반차":
            event_dict["start"] = f"{start_str}T14:00:00"
            event_dict["end"] = f"{start_str}T18:00:00"
            event_dict["allDay"] = False
        else:
            event_dict["start"] = start_str
            # 종일 일정 날짜 보정
            try:
                end_date_obj = pd.to_datetime(end_str) + datetime.timedelta(days=1)
                event_dict["end"] = end_date_obj.strftime("%Y-%m-%d")
            except:
                event_dict["end"] = end_str
            event_dict["allDay"] = True
            
        events.append(event_dict)

# 달력 옵션
calendar_options = {
    "editable": "true", # 드래그 앤 드롭 가능
    "navLinks": "true",
    "headerToolbar": {
        "left": "today prev,next",
        "center": "title",
        "right": "dayGridMonth,listMonth"
    },
    "initialView": "dayGridMonth",
    "height": 700,
    "contentHeight": 650,
    "aspectRatio": 1.8,
    "selectable": "true",
}

# 범례 표시
st.markdown("""
<div style="display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 10px; font-size: 0.9em;">
    <span style="color:#9C27B0; font-weight:bold;">■ 제안</span>
    <span style="color:#6BCB77">■ 프로젝트</span>
    <span style="color:#FF6B6B">■ 휴가</span>
    <span style="color:#FFB347">■ 반차</span>
    <span style="color:#4D96FF">■ 출장</span>
</div>
""", unsafe_allow_html=True)

# 달력 그리기 & 클릭 이벤트 감지
calendar_state = calendar(
    events=events, 
    options=calendar_options, 
    custom_css="""
    .fc-event-title { font-weight: bold; font-size: 0.85em; }
    .fc-toolbar-title { font-size: 1.5em !important; }
    """,
    key="my_calendar" # 키 값 지정
)

# --- [핵심] 클릭 시 팝업 띄우기 ---
if calendar_state.get("eventClick"):
    # 클릭된 이벤트 정보 가져오기
    clicked_event = calendar_state["eventClick"]["event"]
    
    # 숨겨둔 인덱스(idx) 찾기
    clicked_idx = clicked_event["extendedProps"]["index"]
    
    # 해당 데이터 행 가져오기
    target_row = df.loc[clicked_idx]
    
    # 팝업 함수 실행
    open_edit_modal(clicked_idx, target_row)
