import streamlit as st
import pandas as pd
import datetime
import os
import altair as alt

# 1. 페이지 설정
st.set_page_config(page_title="통합 업무 일정표", layout="wide")
st.title("📊 팀 통합 업무 & 일정 관리 시스템")

# 데이터 저장 파일명 (새로운 파일로 저장됩니다)
DATA_FILE = "work_schedule.csv"

# 2. 데이터 불러오기 및 저장 함수
def load_data():
    # 파일이 없으면 기본 데이터프레임 생성 (컬럼 추가됨)
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=["이름", "시작일", "종료일", "유형", "내용", "진행률", "메모"])
    
    df = pd.read_csv(DATA_FILE)
    df['시작일'] = pd.to_datetime(df['시작일']).dt.date
    df['종료일'] = pd.to_datetime(df['종료일']).dt.date
    return df

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# 데이터 로드
df = load_data()

# 3. 사이드바: 일정 및 업무 등록
with st.sidebar:
    st.header("📝 일정/업무 등록")
    with st.form("work_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("이름", placeholder="예: 홍길동")
        with col2:
            schedule_type = st.selectbox(
                "유형", 
                ["🏖️ 휴가/연차", "✈️ 출장/외근", "💻 프로젝트 업무", "🔥 긴급/야근", "📅 기타"]
            )
        
        # 날짜
        today = datetime.date.today()
        d = st.date_input("기간", (today, today))
        
        # 상세 내용
        content = st.text_input("업무명/제목", placeholder="예: KOICA 캄보디아 PMC 제안서 작성")
        
        # 추가된 기능: 진행률 & 메모
        st.write("---")
        progress = st.slider("업무 진행률 (%)", min_value=0, max_value=100, value=0, step=10)
        memo = st.text_area("📌 업무 포인트 / 상세 메모", placeholder="예: 1/30 제출 마감, 인력 구성표 확인 필요", height=100)
        
        submitted = st.form_submit_button("등록하기")
        
        if submitted:
            if len(d) == 2:
                start_date, end_date = d
                new_data = pd.DataFrame({
                    "이름": [name],
                    "시작일": [start_date],
                    "종료일": [end_date],
                    "유형": [schedule_type],
                    "내용": [content],
                    "진행률": [progress],
                    "메모": [memo]
                })
                # 기존 데이터와 합치기
                df = pd.concat([df, new_data], ignore_index=True)
                save_data(df)
                st.success("등록 완료!")
                st.rerun()
            else:
                st.error("시작일과 종료일을 정확히 선택해주세요.")

# 4. 메인 대시보드
col_main, col_stat = st.columns([3, 1])

with col_main:
    st.subheader("📅 스케줄 타임라인")
    if not df.empty:
        # 색상 설정
        color_scale = alt.Scale(
            domain=["🏖️ 휴가/연차", "✈️ 출장/외근", "💻 프로젝트 업무", "🔥 긴급/야근", "📅 기타"],
            range=["#2ecc71", "#3498db", "#9b59b6", "#e74c3c", "#95a5a6"]
        )

        # 차트 (툴팁에 진행률과 메모 추가)
        chart = alt.Chart(df).mark_bar(cornerRadius=5, height=25).encode(
            x=alt.X('시작일', title='날짜'),
            x2='종료일',
            y=alt.Y('이름', title='담당자', sort=None),
            color=alt.Color('유형', scale=color_scale, legend=alt.Legend(title="구분")),
            tooltip=['이름', '유형', '내용', '진행률', '메모', '시작일', '종료일']
        ).properties(
            height=350
        ).interactive()

        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("데이터가 없습니다.")

with col_stat:
    st.subheader("📈 업무 현황")
    if not df.empty:
        # 진행 중인 업무(진행률 1~99%) 개수 세기
        working_count = len(df[(df['진행률'] > 0) & (df['진행률'] < 100)])
        st.metric("진행 중인 업무", f"{working_count}건")
        
        # 오늘 날짜 기준 휴가자 확인
        today_date = pd.to_datetime(datetime.date.today())
        # (날짜 비교 로직은 복잡해질 수 있어 간단히 전체 휴가 건수만 표시)
        vacation_count = len(df[df['유형'].str.contains("휴가")])
        st.metric("등록된 휴가 계획", f"{vacation_count}건")

# 5. 상세 리스트 (업그레이드됨)
st.divider()
st.subheader("📋 상세 업무 리스트")

if not df.empty:
    # 데이터프레임 보여주기 (컬럼 설정 적용)
    st.dataframe(
        df.sort_values(by="시작일", ascending=False),
        column_config={
            "시작일": st.column_config.DateColumn("시작일", format="YYYY-MM-DD"),
            "종료일": st.column_config.DateColumn("종료일", format="YYYY-MM-DD"),
            "진행률": st.column_config.ProgressColumn(
                "진행상황", 
                format="%d%%", 
                min_value=0, 
                max_value=100,
            ),
            "메모": st.column_config.TextColumn("Point/메모", width="large")
        },
        use_container_width=True,
        hide_index=True
    )

    # 삭제 기능
    with st.expander("🗑️ 항목 삭제하기"):
        del_idx = st.selectbox(
            "삭제할 항목을 선택하세요", 
            df.index, 
            format_func=lambda x: f"[{df.loc[x,'이름']}] {df.loc[x,'내용']} (진행률: {df.loc[x,'진행률']}%)"
        )
        if st.button("삭제 실행"):
            df = df.drop(del_idx)
            save_data(df)
            st.success("삭제되었습니다.")
            st.rerun()