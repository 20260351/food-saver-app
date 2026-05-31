"""
AI 식비 절약 도우미 v2.0
- 한글 폰트 문제 해결 (matplotlib + Plotly 사용)
- 카테고리별 1회 평균 지출 금액 입력
- 신규 기능: 절약 챌린지, 식단 추천, 지출 패턴 분석, 알림, 데이터 내보내기 등
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
import io
import random

# ============================================================
# 페이지 설정
# ============================================================
st.set_page_config(
    page_title="AI 식비 절약 도우미 v2.0",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 커스텀 CSS (한글 폰트 적용)
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif !important;
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: 900;
        background: linear-gradient(120deg, #FF6B6B, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .warning-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    
    .success-box {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    
    .info-box {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    
    .challenge-card {
        background: white;
        border: 2px solid #FF6B6B;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-family: 'Noto Sans KR', sans-serif !important;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# Plotly 한글 폰트 기본 설정
# ============================================================
PLOTLY_FONT = dict(family="Noto Sans KR, Malgun Gothic, AppleGothic, sans-serif", size=13)

def apply_korean_font(fig):
    """Plotly 그래프에 한글 폰트 적용"""
    fig.update_layout(
        font=PLOTLY_FONT,
        title_font=dict(family="Noto Sans KR, Malgun Gothic, sans-serif", size=18, color="#333"),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    return fig

# ============================================================
# 세션 상태 초기화
# ============================================================
if 'expenses' not in st.session_state:
    st.session_state.expenses = []
if 'goals_set' not in st.session_state:
    st.session_state.goals_set = False
if 'challenges' not in st.session_state:
    st.session_state.challenges = []

# ============================================================
# 헬퍼 함수
# ============================================================
def format_won(amount):
    """원화 포맷팅"""
    return f"{int(amount):,}원"

def get_ai_feedback(usage_count, avg_cost, category):
    """카테고리별 AI 피드백"""
    monthly_cost = usage_count * avg_cost
    feedbacks = {
        "외식": [
            f"외식 1회 평균 {format_won(avg_cost)} × 월 {usage_count}회 = {format_won(monthly_cost)}",
            "🍽️ 외식 1∼2회를 집밥으로 바꾸면 월 평균 30∼50% 절약 가능해요!",
        ],
        "학식": [
            f"학식 1회 평균 {format_won(avg_cost)} × 월 {usage_count}회 = {format_won(monthly_cost)}",
            "🎓 학식은 가성비 최고! 외식 대신 학식 이용을 늘려보세요.",
        ],
        "편의점": [
            f"편의점 1회 평균 {format_won(avg_cost)} × 월 {usage_count}회 = {format_won(monthly_cost)}",
            "🏪 편의점은 자주 가면 누적 비용이 큽니다. 주 1회 마트 장보기로 대체해보세요!",
        ],
        "카페": [
            f"카페 1회 평균 {format_won(avg_cost)} × 월 {usage_count}회 = {format_won(monthly_cost)}",
            "☕ 카페 음료를 텀블러+홈카페로 바꾸면 연 50∼100만원 절약!",
        ],
        "배달": [
            f"배달 1회 평균 {format_won(avg_cost)} × 월 {usage_count}회 = {format_won(monthly_cost)}",
            "🛵 배달비+최소주문금액 때문에 외식보다 비쌀 수 있어요. 주 1회로 제한해보세요!",
        ],
    }
    return feedbacks.get(category, [f"{category}: {format_won(monthly_cost)}"])

# ============================================================
# 메인 헤더
# ============================================================
st.markdown('<h1 class="main-header">💰 AI 식비 절약 도우미 v2.0</h1>', unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#666;'>스마트한 소비 습관으로 한 달 식비를 줄여보세요! 🚀</p>", unsafe_allow_html=True)

# ============================================================
# 사이드바: 사용자 정보 입력
# ============================================================
with st.sidebar:
    st.header("👤 내 정보")
    
    user_name = st.text_input("이름 (선택)", value="사용자")
    monthly_budget = st.number_input(
        "💵 월 식비 예산 (원)",
        min_value=100000,
        max_value=2000000,
        value=400000,
        step=10000,
        help="한 달에 식비로 사용 가능한 금액"
    )
    
    saving_goal = st.slider(
        "🎯 절약 목표 비율 (%)",
        min_value=5,
        max_value=50,
        value=20,
        step=5,
        help="이번 달 절약하고 싶은 비율"
    )
    
    st.divider()
    
    st.header("📅 분석 기간")
    period = st.selectbox(
        "기준 기간",
        ["월간 (30일)", "주간 (7일)", "일일 (1일)"],
        index=0
    )
    
    period_days = {"월간 (30일)": 30, "주간 (7일)": 7, "일일 (1일)": 1}[period]
    
    st.divider()
    st.caption("💡 Tip: 정확한 분석을 위해\n실제 소비 패턴을 솔직하게 입력하세요!")

# ============================================================
# 메인 컨텐츠: 탭 구성
# ============================================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📝 소비 입력",
    "📊 지출 분석",
    "🎯 절약 챌린지",
    "🍱 식단 추천",
    "💡 AI 조언",
    "📥 데이터 관리"
])

# ============================================================
# 탭 1: 소비 입력 (카테고리별 횟수 + 평균 금액)
# ============================================================
with tab1:
    st.header("📝 한 달 식비 소비 패턴 입력")
    st.markdown("각 카테고리별로 **이용 횟수**와 **1회 평균 지출 금액**을 입력해주세요.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🍽️ 외식")
        eat_out_count = st.number_input("월 외식 횟수", 0, 100, 8, key="eat_out_c")
        eat_out_avg = st.number_input("1회 평균 금액 (원)", 0, 100000, 12000, step=500, key="eat_out_a")
        st.caption(f"💰 월 외식비: **{format_won(eat_out_count * eat_out_avg)}**")
        
        st.subheader("🎓 학식/구내식당")
        school_count = st.number_input("월 학식 이용 횟수", 0, 100, 12, key="school_c")
        school_avg = st.number_input("1회 평균 금액 (원)", 0, 20000, 5000, step=500, key="school_a")
        st.caption(f"💰 월 학식비: **{format_won(school_count * school_avg)}**")
        
        st.subheader("🏪 편의점")
        cvs_count = st.number_input("월 편의점 이용 횟수", 0, 100, 15, key="cvs_c")
        cvs_avg = st.number_input("1회 평균 금액 (원)", 0, 50000, 4500, step=500, key="cvs_a")
        st.caption(f"💰 월 편의점비: **{format_won(cvs_count * cvs_avg)}**")
    
    with col2:
        st.subheader("☕ 카페")
        cafe_count = st.number_input("월 카페 이용 횟수", 0, 100, 10, key="cafe_c")
        cafe_avg = st.number_input("1회 평균 금액 (원)", 0, 30000, 5500, step=500, key="cafe_a")
        st.caption(f"💰 월 카페비: **{format_won(cafe_count * cafe_avg)}**")
        
        st.subheader("🛵 배달")
        delivery_count = st.number_input("월 배달 횟수", 0, 100, 6, key="del_c")
        delivery_avg = st.number_input("1회 평균 금액 (원)", 0, 100000, 18000, step=500, key="del_a")
        st.caption(f"💰 월 배달비: **{format_won(delivery_count * delivery_avg)}**")
        
        st.subheader("🛒 마트/장보기")
        mart_count = st.number_input("월 장보기 횟수", 0, 30, 4, key="mart_c")
        mart_avg = st.number_input("1회 평균 금액 (원)", 0, 300000, 50000, step=5000, key="mart_a")
        st.caption(f"💰 월 장보기비: **{format_won(mart_count * mart_avg)}**")
    
    # 총합 계산
    expense_data = {
        "외식": {"count": eat_out_count, "avg": eat_out_avg, "total": eat_out_count * eat_out_avg},
        "학식": {"count": school_count, "avg": school_avg, "total": school_count * school_avg},
        "편의점": {"count": cvs_count, "avg": cvs_avg, "total": cvs_count * cvs_avg},
        "카페": {"count": cafe_count, "avg": cafe_avg, "total": cafe_count * cafe_avg},
        "배달": {"count": delivery_count, "avg": delivery_avg, "total": delivery_count * delivery_avg},
        "마트": {"count": mart_count, "avg": mart_avg, "total": mart_count * mart_avg},
    }
    
    total_expense = sum([v["total"] for v in expense_data.values()])
    total_count = sum([v["count"] for v in expense_data.values()])
    
    st.divider()
    
    # 요약 카드
    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        st.metric("💰 총 예상 지출", format_won(total_expense))
    with col_b:
        st.metric("📅 예산 대비", f"{total_expense/monthly_budget*100:.1f}%",
                  delta=f"{format_won(monthly_budget - total_expense)}",
                  delta_color="normal" if total_expense <= monthly_budget else "inverse")
    with col_c:
        st.metric("🍴 총 소비 횟수", f"{total_count}회")
    with col_d:
        daily_avg = total_expense / 30
        st.metric("📆 일 평균", format_won(daily_avg))
    
    # 예산 초과 경고
    if total_expense > monthly_budget:
        over = total_expense - monthly_budget
        st.markdown(f"""
        <div class="warning-box">
        ⚠️ <b>예산 초과 경고!</b><br>
        설정 예산보다 <b>{format_won(over)}</b> 초과 지출 예상됩니다.
        </div>
        """, unsafe_allow_html=True)
    else:
        saved = monthly_budget - total_expense
        st.markdown(f"""
        <div class="success-box">
        ✅ <b>예산 내 지출!</b> 약 <b>{format_won(saved)}</b> 여유가 있어요. 👍
        </div>
        """, unsafe_allow_html=True)
    
    # 세션에 저장
    st.session_state.expense_data = expense_data
    st.session_state.total_expense = total_expense
    st.session_state.monthly_budget = monthly_budget
    st.session_state.saving_goal = saving_goal

# ============================================================
# 탭 2: 지출 분석 (그래프 - 한글 적용)
# ============================================================
with tab2:
    st.header("📊 지출 분석 대시보드")
    
    if 'expense_data' not in st.session_state:
        st.info("먼저 '소비 입력' 탭에서 정보를 입력해주세요!")
    else:
        data = st.session_state.expense_data
        df = pd.DataFrame([
            {"카테고리": k, "횟수": v["count"], "1회평균": v["avg"], "총지출": v["total"]}
            for k, v in data.items()
        ])
        
        # 1. 카테고리별 지출 파이차트
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🥧 카테고리별 지출 비율")
            fig_pie = px.pie(
                df, values='총지출', names='카테고리',
                color_discrete_sequence=px.colors.qualitative.Set2,
                hole=0.4
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie = apply_korean_font(fig_pie)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            st.subheader("📊 카테고리별 총 지출")
            fig_bar = px.bar(
                df.sort_values('총지출', ascending=True),
                x='총지출', y='카테고리', orientation='h',
                color='총지출', color_continuous_scale='Sunset',
                text='총지출'
            )
            fig_bar.update_traces(texttemplate='%{text:,.0f}원', textposition='outside')
            fig_bar.update_layout(showlegend=False)
            fig_bar = apply_korean_font(fig_bar)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # 2. 횟수 vs 평균금액 버블차트
        st.subheader("🎯 소비 패턴 분석 (횟수 × 평균 금액)")
        fig_bubble = px.scatter(
            df, x='횟수', y='1회평균', size='총지출', color='카테고리',
            hover_name='카테고리', size_max=80,
            labels={'횟수': '월 이용 횟수', '1회평균': '1회 평균 금액 (원)'},
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig_bubble.update_layout(height=500)
        fig_bubble = apply_korean_font(fig_bubble)
        st.plotly_chart(fig_bubble, use_container_width=True)
        
        st.markdown("""
        <div class="info-box">
        💡 <b>버블이 클수록 총 지출이 큰 카테고리입니다.</b><br>
        오른쪽 상단(고빈도×고단가)은 우선 절약 대상이에요!
        </div>
        """, unsafe_allow_html=True)
        
        # 3. 예산 게이지
        st.subheader("⛽ 예산 사용률")
        usage_rate = st.session_state.total_expense / st.session_state.monthly_budget * 100
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=usage_rate,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "예산 사용률 (%)", 'font': PLOTLY_FONT},
            number={'suffix': "%", 'font': PLOTLY_FONT},
            delta={'reference': 100, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
            gauge={
                'axis': {'range': [None, 150], 'tickfont': PLOTLY_FONT},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 70], 'color': "lightgreen"},
                    {'range': [70, 100], 'color': "yellow"},
                    {'range': [100, 150], 'color': "lightcoral"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75, 'value': 100
                }
            }
        ))
        fig_gauge.update_layout(height=350, font=PLOTLY_FONT)
        st.plotly_chart(fig_gauge, use_container_width=True)
        
        # 4. 데이터 테이블
        st.subheader("📋 상세 데이터")
        df_display = df.copy()
        df_display['1회평균'] = df_display['1회평균'].apply(lambda x: f"{x:,}원")
        df_display['총지출'] = df_display['총지출'].apply(lambda x: f"{x:,}원")
        df_display['횟수'] = df_display['횟수'].apply(lambda x: f"{x}회")
        st.dataframe(df_display, use_container_width=True, hide_index=True)

# ============================================================
# 탭 3: 절약 챌린지 (신규!)
# ============================================================
with tab3:
    st.header("🎯 절약 챌린지")
    st.markdown("재미있는 챌린지로 식비를 줄여보세요! 🔥")
    
    challenges = [
        {"name": "☕ 노카페 위크", "desc": "1주일 동안 카페 0회 도전!", "saving": "약 22,000원"},
        {"name": "🏪 편의점 단식", "desc": "5일 동안 편의점 안 가기!", "saving": "약 25,000원"},
        {"name": "🍱 도시락 챌린지", "desc": "주 3회 도시락 싸기!", "saving": "약 36,000원"},
        {"name": "🛵 배달 ZERO", "desc": "한 달 배달 안 시키기!", "saving": "약 108,000원"},
        {"name": "💧 물텀블러 챌린지", "desc": "음료 대신 물 마시기 (2주)", "saving": "약 30,000원"},
        {"name": "🛒 1주 1장보기", "desc": "주 1회 마트 가서 일주일치 준비", "saving": "약 40,000원"},
    ]
    
    st.markdown("### 🔥 추천 챌린지")
    cols = st.columns(3)
    for i, ch in enumerate(challenges):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="challenge-card">
            <h4>{ch['name']}</h4>
            <p>{ch['desc']}</p>
            <p style="color:#27ae60; font-weight:bold;">💰 예상 절약: {ch['saving']}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"참여하기", key=f"ch_{i}"):
                if ch['name'] not in [c['name'] for c in st.session_state.challenges]:
                    st.session_state.challenges.append({
                        "name": ch['name'],
                        "start": datetime.now().strftime("%Y-%m-%d"),
                        "status": "진행중"
                    })
                    st.success(f"✅ '{ch['name']}' 챌린지 시작!")
    
    st.divider()
    
    # 참여 중인 챌린지
    if st.session_state.challenges:
        st.markdown("### 📌 내 참여 챌린지")
        for ch in st.session_state.challenges:
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.markdown(f"**{ch['name']}**")
            with col2:
                st.caption(f"시작일: {ch['start']} | 상태: {ch['status']}")
            with col3:
                if st.button("완료", key=f"done_{ch['name']}"):
                    ch['status'] = "✅ 완료"
                    st.rerun()
    
    st.divider()
    
    # 절약 목표 진행률
    st.markdown("### 🏆 이번 달 절약 목표")
    if 'total_expense' in st.session_state:
        target_save = st.session_state.monthly_budget * st.session_state.saving_goal / 100
        current_save = max(0, st.session_state.monthly_budget - st.session_state.total_expense)
        progress = min(current_save / target_save, 1.0) if target_save > 0 else 0
        
        st.progress(progress)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🎯 목표 절약액", format_won(target_save))
        with col2:
            st.metric("💰 현재 절약액", format_won(current_save))
        with col3:
            st.metric("📈 달성률", f"{progress*100:.1f}%")

# ============================================================
# 탭 4: 식단 추천 (신규!)
# ============================================================
with tab4:
    st.header("🍱 가성비 식단 추천")
    st.markdown("저렴하고 건강한 식단을 추천해드려요!")
    
    meal_type = st.radio("어떤 식단이 필요하세요?",
                        ["🌅 아침", "🌞 점심", "🌙 저녁", "🍪 간식"],
                        horizontal=True)
    
    meals = {
        "🌅 아침": [
            {"name": "🥣 오트밀+바나나", "cost": 1500, "time": "5분", "tip": "포만감 최고!"},
            {"name": "🍞 토스트+계란후라이", "cost": 2000, "time": "10분", "tip": "단백질 풍부"},
            {"name": "🥛 시리얼+우유", "cost": 1800, "time": "3분", "tip": "간편식 끝판왕"},
            {"name": "🍌 그릭요거트+과일", "cost": 3000, "time": "5분", "tip": "건강 만점"},
        ],
        "🌞 점심": [
            {"name": "🍙 김밥 도시락", "cost": 3000, "time": "20분", "tip": "재료 다양화 가능"},
            {"name": "🍜 비빔국수", "cost": 2500, "time": "10분", "tip": "여름 별미"},
            {"name": "🍱 볶음밥 도시락", "cost": 2800, "time": "15분", "tip": "냉장고 털기 굿"},
            {"name": "🥪 샌드위치", "cost": 3500, "time": "10분", "tip": "휴대성 최고"},
        ],
        "🌙 저녁": [
            {"name": "🍲 김치찌개+밥", "cost": 3500, "time": "20분", "tip": "한식 정석"},
            {"name": "🍝 토마토 파스타", "cost": 4000, "time": "15분", "tip": "분위기 UP"},
            {"name": "🍛 카레라이스", "cost": 3500, "time": "25분", "tip": "2∼3끼 가능"},
            {"name": "🥘 두부김치", "cost": 3000, "time": "15분", "tip": "단백질 보충"},
        ],
        "🍪 간식": [
            {"name": "🍎 과일 한 접시", "cost": 2000, "time": "3분", "tip": "비타민 가득"},
            {"name": "🥜 견과류 한줌", "cost": 1500, "time": "1분", "tip": "건강 간식"},
            {"name": "🍵 홈카페 (티+쿠키)", "cost": 1000, "time": "5분", "tip": "카페 대신!"},
            {"name": "🍿 팝콘", "cost": 800, "time": "5분", "tip": "넷플릭스 친구"},
        ],
    }
    
    selected_meals = meals[meal_type]
    
    cols = st.columns(2)
    for i, meal in enumerate(selected_meals):
        with cols[i % 2]:
            st.markdown(f"""
            <div style="background:white; border:1px solid #ddd; padding:15px; 
                        border-radius:10px; margin:10px 0;">
            <h4>{meal['name']}</h4>
            <p>💰 예상 비용: <b>{format_won(meal['cost'])}</b></p>
            <p>⏱️ 조리 시간: {meal['time']}</p>
            <p style="color:#666;">💡 {meal['tip']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # 일주일 식단 계획
    st.subheader("📅 1주일 식단 계획 (예시)")
    week_plan = pd.DataFrame({
        "요일": ["월", "화", "수", "목", "금", "토", "일"],
        "아침": ["오트밀", "토스트", "시리얼", "오트밀", "토스트", "그릭요거트", "팬케이크"],
        "점심": ["김밥", "학식", "도시락", "학식", "비빔국수", "외식", "라면"],
        "저녁": ["김치찌개", "카레", "파스타", "두부김치", "치킨(배달)", "외식", "남은 카레"],
        "예상비용": ["8,000원", "7,500원", "9,000원", "7,500원", "22,000원", "30,000원", "5,000원"],
    })
    st.dataframe(week_plan, use_container_width=True, hide_index=True)
    st.caption("💡 주말에 외식/배달을 몰아서 평일은 저렴하게 운영하는 것이 효율적이에요!")

# ============================================================
# 탭 5: AI 조언
# ============================================================
with tab5:
    st.header("💡 AI 맞춤형 절약 조언")
    
    if 'expense_data' not in st.session_state:
        st.info("먼저 '소비 입력' 탭에서 정보를 입력해주세요!")
    else:
        data = st.session_state.expense_data
        total = st.session_state.total_expense
        budget = st.session_state.monthly_budget
        
        # 가장 큰 지출 카테고리 찾기
        sorted_cats = sorted(data.items(), key=lambda x: x[1]['total'], reverse=True)
        top_cat = sorted_cats[0]
        
        st.markdown(f"""
        <div class="info-box">
        🔍 <b>{user_name}님의 소비 패턴 분석 결과</b><br>
        가장 큰 지출은 <b>{top_cat[0]}</b>이며, 총 <b>{format_won(top_cat[1]['total'])}</b>를 사용하셨어요.
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("📌 카테고리별 맞춤 조언")
        for cat, info in sorted_cats:
            if info['total'] > 0:
                with st.expander(f"{cat} - {format_won(info['total'])} ({info['count']}회)"):
                    feedbacks = get_ai_feedback(info['count'], info['avg'], cat)
                    for fb in feedbacks:
                        st.write(f"• {fb}")
        
        st.divider()
        
        # 전체 조언
        st.subheader("🎯 종합 절약 전략")
        
        strategies = []
        if data["카페"]["count"] > 8:
            strategies.append(f"☕ 카페 이용 {data['카페']['count']}회 → 5회로 줄이면 월 **{format_won((data['카페']['count']-5)*data['카페']['avg'])}** 절약")
        if data["배달"]["count"] > 4:
            strategies.append(f"🛵 배달 {data['배달']['count']}회 → 3회로 줄이면 월 **{format_won((data['배달']['count']-3)*data['배달']['avg'])}** 절약")
        if data["편의점"]["count"] > 10:
            strategies.append(f"🏪 편의점 {data['편의점']['count']}회 → 7회로 줄이면 월 **{format_won((data['편의점']['count']-7)*data['편의점']['avg'])}** 절약")
        if data["외식"]["count"] > 6:
            strategies.append(f"🍽️ 외식 {data['외식']['count']}회 → 5회로 줄이면 월 **{format_won((data['외식']['count']-5)*data['외식']['avg'])}** 절약")
        
        if strategies:
            for s in strategies:
                st.markdown(f"- {s}")
            
            # 총 절약 가능액
            total_saving = sum([
                max(0, data['카페']['count']-5) * data['카페']['avg'],
                max(0, data['배달']['count']-3) * data['배달']['avg'],
                max(0, data['편의점']['count']-7) * data['편의점']['avg'],
                max(0, data['외식']['count']-5) * data['외식']['avg'],
            ])
            st.markdown(f"""
            <div class="success-box">
            🎉 <b>위 전략 실행 시 월 최대 {format_won(total_saving)} 절약 가능!</b><br>
            연간 환산: 약 <b>{format_won(total_saving*12)}</b> 💰
            </div>
            """, unsafe_allow_html=True)
        else:
            st.success("✨ 이미 매우 합리적인 소비를 하고 계세요!")
        
        st.divider()
        
        # 절약 꿀팁
        st.subheader("💎 절약 꿀팁 BEST 7")
        tips = [
            "🎫 **학식/구내식당 적극 활용** - 외식 대비 60% 저렴",
            "🥡 **도시락 싸기** - 점심값 50% 절감, 건강 보너스",
            "☕ **텀블러 사용** - 카페 할인 + 환경 보호",
            "🛒 **마트 1주일치 장보기** - 편의점 충동구매 방지",
            "📱 **앱 할인쿠폰 활용** - 배달, 카페 5∼30% 할인",
            "💳 **체크카드 캐시백** - 식비 카테고리 적립률 확인",
            "🍳 **밀프렙(Meal Prep)** - 주말에 평일 식사 미리 준비",
        ]
        for tip in tips:
            st.markdown(f"- {tip}")

# ============================================================
# 탭 6: 데이터 관리 (신규!)
# ============================================================
with tab6:
    st.header("📥 데이터 관리")
    
    if 'expense_data' not in st.session_state:
        st.info("먼저 '소비 입력' 탭에서 정보를 입력해주세요!")
    else:
        data = st.session_state.expense_data
        
        st.subheader("💾 데이터 내보내기")
        
        # CSV 다운로드
        df_export = pd.DataFrame([
            {
                "카테고리": k,
                "월 이용 횟수": v["count"],
                "1회 평균 금액(원)": v["avg"],
                "월 총 지출(원)": v["total"]
            }
            for k, v in data.items()
        ])
        
        col1, col2 = st.columns(2)
        
        with col1:
            csv = df_export.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📄 CSV로 다운로드",
                data=csv,
                file_name=f"식비내역_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        with col2:
            json_data = {
                "user": user_name,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "monthly_budget": st.session_state.monthly_budget,
                "saving_goal_percent": st.session_state.saving_goal,
                "total_expense": st.session_state.total_expense,
                "categories": data
            }
            json_str = json.dumps(json_data, ensure_ascii=False, indent=2)
            st.download_button(
                label="📋 JSON으로 다운로드",
                data=json_str.encode('utf-8'),
                file_name=f"식비데이터_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
        
        st.divider()
        
        # 데이터 미리보기
        st.subheader("👀 데이터 미리보기")
        st.dataframe(df_export, use_container_width=True, hide_index=True)
        
        st.divider()
        
        # 월별 비교 시뮬레이션
        st.subheader("📈 절약 시뮬레이션 (6개월 예측)")
        months = ['이번달', '+1개월', '+2개월', '+3개월', '+4개월', '+5개월']
        current = st.session_state.total_expense
        target_reduction = st.session_state.saving_goal / 100
        
        # 점진적 절약 시나리오
        scenarios = {
            "현재 패턴 유지": [current] * 6,
            "목표 절약 달성": [current * (1 - target_reduction * (i/5)) for i in range(6)],
            "적극 절약 (30%)": [current * (1 - 0.3 * (i/5)) for i in range(6)],
        }
        
        fig_sim = go.Figure()
        colors = ['#FF6B6B', '#4ECDC4', '#95E1D3']
        for (name, values), color in zip(scenarios.items(), colors):
            fig_sim.add_trace(go.Scatter(
                x=months, y=values, mode='lines+markers',
                name=name, line=dict(color=color, width=3),
                marker=dict(size=10)
            ))
        
        fig_sim.update_layout(
            title="6개월 식비 시나리오 비교",
            xaxis_title="기간",
            yaxis_title="월 식비 (원)",
            height=450,
            hovermode='x unified'
        )
        fig_sim = apply_korean_font(fig_sim)
        st.plotly_chart(fig_sim, use_container_width=True)
        
        # 6개월 누적 절약액
        save_total = sum(scenarios["현재 패턴 유지"]) - sum(scenarios["목표 절약 달성"])
        save_aggressive = sum(scenarios["현재 패턴 유지"]) - sum(scenarios["적극 절약 (30%)"])
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("🎯 목표 달성 시 6개월 절약", format_won(save_total))
        with col2:
            st.metric("🔥 적극 절약 시 6개월 절약", format_won(save_aggressive))
        
        st.divider()
        
        # 데이터 초기화
        st.subheader("🔄 데이터 초기화")
        if st.button("⚠️ 모든 데이터 초기화", type="secondary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.success("✅ 초기화 완료! 페이지를 새로고침해주세요.")
            st.rerun()

# ============================================================
# 푸터
# ============================================================
st.divider()
st.markdown("""
<div style='text-align:center; color:#888; padding:20px;'>
    <p>💰 <b>AI 식비 절약 도우미 v2.0</b> | Made with ❤️ using Streamlit</p>
    <p style='font-size:0.85rem;'>
    ✨ 신규 기능: 한글 폰트 지원 · 카테고리별 평균 금액 · 절약 챌린지 · 식단 추천 · 데이터 내보내기
    </p>
</div>
""", unsafe_allow_html=True)
