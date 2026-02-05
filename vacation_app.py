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
    df['시작일'] = df['시작일'].astype(str)
    df['종료일'] = df['종료일'].astype(str)
    return df

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

df = load_data()

# 공통 설정: 일정 유형 및 색상 (이름 변경됨: 제안 작업 -> 제안)
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

# 3. 사이드바: 탭으로 기능 분리
with st.sidebar:
    st.header("관리 메뉴")
    tab1, tab2 = st.tabs(["📝 일정 등록", "🛠️ 수정/삭제"])

    # --- [탭 1] 일정 등록 ---
    with tab1:
        with st.form("add_event"):
            st.subheader("새 일정 추가")
            # 예시 이름 변경 (홍길동)
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
                    st.error("기간을 정확히 선택해주세요.")

    # --- [탭 2] 일정 수정 및 삭제 ---
    with tab2:
        st.subheader("일정 고치기")
        if not df.empty:
            edit_idx = st.selectbox(
                "수정할 일정 선택",
                df.index,
                format_func=lambda x: f"[{df.loc[x,'유형']}] {df.loc[x,'이름']} - {df.loc[x,'내용']}"
            )

            target_row = df.loc[edit_idx]

            with st.form("edit_form"):
                st.write("🔻 내용 수정")
                new_name = st.text_input("이름", value=target_row['이름'])
                
                try:
                    type_index = list(type_options.keys()).index(target_row['유형'])
                except ValueError:
                    type_index = 0
                new_type = st.selectbox("일정 유형", list(type_options.keys()), index=type_index)

                try:
                    s_date = datetime.datetime.strptime(str(target_row['시작일']), "%Y-%m-%d").date()
                    e_date = datetime.datetime.strptime(str(target_row['종료일']), "%Y-%m-%d").date()
                except:
                    s_date = datetime.date.today()
                    e_date = datetime.date.today()
                
                new_dates = st.date_input("기간", (s_date, e_date))
                new_content = st.text_input("내용", value=target_row['내용'])

                col_edit, col_del = st.columns(2)
                update_submit = col_edit.form_submit_button("수정 저장", type="primary")
                delete_submit = col_del.form_submit_button("🗑️ 삭제")

                if update_submit:
                    if len(new_dates) == 2:
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
        
        start_str = str(row["시작일"])
        end_str = str(row["종료일"])
        
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

# 범례 업데이트 (제안)
st.markdown("""
<div style="display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 10px; font-size: 0.9em;">
    <span style="color:#9C27B0; font-weight:bold;">■ 제안</span>
    <span style="color:#6BCB77">■ 프로젝트</span>
    <span style="color:#FF6B6B">■ 휴가</span>
    <span style="color:#FFB347">■ 반차</span>
    <span style="color:#4D96FF">■ 출장</span>
</div>
""", unsafe_allow_html=True)

calendar(events=events, options=calendar_options, custom_css="""
    .fc-event-title {
        font-weight: bold;
        font-size: 0.85em;
    }
    .fc-toolbar-
