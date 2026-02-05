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
            "🏖️ 휴가 (종일)": "#FF6B6B",   # 빨강
            "🌅 오전 반차": "#FFB347",    # 주황
            "🌇 오후 반차": "#FFCC00",    # 노랑
            "✈️ 출장/외근": "#4D96FF",    # 파랑
            "📑 제안": "#9C27B0",    # 보라
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
        return pd.DataFrame(columns=["이름", "시작일", "종료일", "유형", "내용"])
    df = pd.read_csv(DATA_FILE)
    # 날짜 문자열을 바르게 처리하기 위해 변환
    df['시작일'] = df['시작일'].astype(str)
    df['종료일'] = df['종료일'].astype(str)
    return df

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

df = load_data()

# 공통 설정: 일정 유형 및 색상
type_options = {
    "🏖️ 휴가 (종일)": "#FF6B6B",   # 빨강
    "🌅 오전 반차": "#FFB347",    # 주황
    "🌇 오후 반차": "#FFCC00",    # 노랑
    "✈️ 출장/외근": "#4D96FF",    # 파랑
    "📑 제안": "#9C27B0",    # 보라
    "💻 프로젝트": "#6BCB77",     # 초록
    "🔥 긴급/야근": "#E91E63",    # 진분홍
    "📅 기타": "#A2A2A2"         # 회색
}

# 3. 사이드바: 탭으로 기능 분리
with st.sidebar:
    st.header("관리 메뉴")
    # 탭을 만들어 등록과 수정을 분리
    tab1, tab2 = st.tabs(["📝 일정 등록", "🛠️ 수정/삭제"])

    # --- [탭 1] 일정 등록 ---
    with tab1:
        with st.form("add_event"):
            st.subheader("새 일정 추가")
            name = st.text_input("이름", placeholder="예: 홍길동")
            schedule_type = st.selectbox("일정 유형", list(type_options.keys()))
            
            today = datetime.date.today()
            d = st.date_input("기간 (시작 ~ 종료)", (today, today))
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
                    df = pd.concat([df, new_row], ignore_index=True)
                    save_data(df)
                    st.success("등록되었습니다!")
                    st.rerun()
                else:
                    st.error("종료 날짜까지 선택해주세요.")

    # --- [탭 2] 일정 수정 및 삭제 ---
    with tab2:
        st.subheader("일정 고치기")
        if not df.empty:
            # 수정할 일정을 선택하는 박스
            # (사람 이름과 내용을 합쳐서 보여줌)
            edit_idx = st.selectbox(
                "수정할 일정 선택",
                df.index,
                format_func=lambda x: f"[{df.loc[x,'유형']}] {df.loc[x,'이름']} - {df.loc[x,'내용']}"
            )

            # 선택된 데이터 가져오기
            target_row = df.loc[edit_idx]

            with st.form("edit_form"):
                # 기존 값으로 미리 채워넣기 (Pre-fill)
                st.write("🔻 내용 수정")
                new_name = st.text_input("이름", value=target_row['이름'])
                
                # 기존 유형이 옵션에 있으면 그걸 기본값으로 설정
                try:
                    type_index = list(type_options.keys()).index(target_row['유형'])
                except ValueError:
                    type_index = 0
                new_type = st.selectbox("일정 유형", list(type_options.keys()), index=type_index)

                # 날짜 변환 (문자열 -> 날짜 객체)
                try:
                    s_date = datetime.datetime.strptime(target_row['시작일'], "%Y-%m-%d").date()
                    e_date = datetime.datetime.strptime(target_row['종료일'], "%Y-%m-%d").date()
                except:
                    s_date = datetime.date.today()
                    e_date = datetime.date.today()
                
                new_dates = st.date_input("기간", (s_date, e_date))
                new_content = st.text_input("내용", value=target_row['내용'])

                # 버튼 배치
                col_edit, col_del = st.columns(2)
                update_submit = col_edit.form_submit_button("수정 저장", type="primary")
                delete_submit = col_del.form_submit_button("🗑️ 삭제")

                if update_submit:
                    if len(new_dates) == 2:
                        # 데이터 업데이트
                        df.at[edit_idx, '이름'] = new_name
                        df.at[edit_idx, '유형'] = new_type
                        df.at[edit_idx, '시작일'] = new_dates[0]
                        df.at[edit_idx, '종료일'] = new_dates[1]
                        df.at[edit_idx, '내용'] = new_content
                        save_data(df)
                        st.success("수정 완료!")
                        st.rerun()
                    else:
                        st.error("날짜를 정확히 선택해주세요.")

                if delete_submit:
                    df = df.drop(edit_idx)
                    save_data(df)
                    st.success("삭제되었습니다.")
                    st.rerun()
        else:
            st.info("수정할 일정이 없습니다.")

# 4. 메인 화면: 달력 표시
events = []
if not df.empty:
    for _, row in df.iterrows():
        color = type_options.get(row["유형"], "#3788d8")
        
        # 날짜 형식 안전 변환
        start_str = str(row["시작일"])
        end_str = str(row["종료일"])
        
        # 종료일에 +1일 (달력 표시용)
        try:
            end_date_obj = pd.to_datetime(end_str) + datetime.timedelta(days=1)
            end_date_str = end_date_obj.strftime("%Y-%m-%d")
        except:
            end_date_str = end_str

        events.append({
            "title": f"[{row['이름']}] {row['내용']}",
            "start": start_str,
            "end": end_date_str,
            "backgroundColor": color,
            "borderColor": color,
            "allDay": True
        })

# 달력 설정 (깔끔한 사이즈 유지)
calendar_options = {
    "editable": "true",
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

calendar(events=events, options=calendar_options, custom_css="""
    .fc-event-title {
        font-weight: bold;
        font-size: 0.85em;
    }
    .fc-toolbar-title {
        font-size: 1.5em !important;
    }
""")

# 5. 하단 데이터 리스트
st.divider()
with st.expander("📊 전체 데이터 목록 보기"):
    st.dataframe(df, use_container_width=True)
