
"""
🍱 AI 기반 대학생 식비 절약 도우미 - 웹 버전
================================================
Streamlit을 활용한 인터랙티브 웹 애플리케이션
실행 방법: streamlit run food_helper_web.py
================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from datetime import datetime, timedelta
import platform
import random

# ============================================================
# 한글 폰트 설정
# ============================================================
if platform.system() == 'Windows':
    plt.rcParams['font.family'] = 'Malgun Gothic'
elif platform.system() == 'Darwin':
    plt.rcParams['font.family'] = 'AppleGothic'
else:
    plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

# ============================================================
# 페이지 기본 설정
# ============================================================
st.set_page_config(
    page_title="AI 식비 절약 도우미",
    page_icon="🍱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 커스텀 CSS (예쁜 디자인)
# ============================================================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #FF6B6B 0%, #FFA07A 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 5px solid #FF6B6B;
    }
    .recommendation-card {
        background: linear-gradient(135deg, #f6f9fc 0%, #e9f0f7 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #4ECDC4;
    }
    .tip-box {
        background: #FFF9E6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #FFD93D;
        margin: 0.5rem 0;
    }
    .success-box {
        background: #E8F5E9;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #4CAF50;
    }
    .warning-box {
        background: #FFEBEE;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #F44336;
    }
    h1, h2, h3 { color: #2C3E50; }
    .stButton>button {
        background: linear-gradient(90deg, #FF6B6B 0%, #FFA07A 100%);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 25px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# AI 추천 데이터베이스
# ============================================================
RECIPE_DB = {
    '간편식': [
        {'name': '계란볶음밥', 'cost': 2000, 'time': 10, 'difficulty': '하',
         'ingredients': ['밥', '계란', '대파', '간장'], 'kcal': 450},
        {'name': '김치볶음밥', 'cost': 2500, 'time': 15, 'difficulty': '하',
         'ingredients': ['밥', '김치', '계란', '참기름'], 'kcal': 520},
        {'name': '참치마요덮밥', 'cost': 3000, 'time': 10, 'difficulty': '하',
         'ingredients': ['밥', '참치캔', '마요네즈', '김'], 'kcal': 580},
    ],
    '국물요리': [
        {'name': '계란국', 'cost': 1500, 'time': 15, 'difficulty': '하',
         'ingredients': ['계란', '대파', '간장', '참기름'], 'kcal': 180},
        {'name': '된장찌개', 'cost': 3000, 'time': 25, 'difficulty': '중',
         'ingredients': ['된장', '두부', '애호박', '양파'], 'kcal': 220},
        {'name': '김치찌개', 'cost': 3500, 'time': 30, 'difficulty': '중',
         'ingredients': ['김치', '돼지고기', '두부', '대파'], 'kcal': 350},
    ],
    '면요리': [
        {'name': '간장비빔국수', 'cost': 2000, 'time': 10, 'difficulty': '하',
         'ingredients': ['소면', '간장', '참기름', '계란'], 'kcal': 480},
        {'name': '잔치국수', 'cost': 2500, 'time': 20, 'difficulty': '중',
         'ingredients': ['소면', '멸치육수', '계란', '김'], 'kcal': 420},
    ]
}

SAVING_TIPS = [    {'title': '🛒 마감 할인 활용', 'desc': '대형마트는 저녁 8시 이후 신선식품 30∼50% 할인',     'saving': 30000, 'difficulty': '쉬움'},    {'title': '📅 주간 메뉴 계획', 'desc': '일주일 식단을 미리 짜면 충동구매 방지',     'saving': 40000, 'difficulty': '보통'},    {'title': '🥗 도시락 싸기', 'desc': '점심 도시락으로 외식비 70% 절감',     'saving': 80000, 'difficulty': '보통'},    {'title': '🍚 대용량 구매', 'desc': '쌀, 라면 등은 대용량이 25% 저렴',     'saving': 20000, 'difficulty': '쉬움'},    {'title': '☕ 카페 줄이기', 'desc': '하루 1잔 카페 → 주 2회로 줄이기',     'saving': 60000, 'difficulty': '어려움'},    {'title': '🥬 제철 식재료', 'desc': '제철 채소/과일은 40% 저렴하고 영양가도 높음',     'saving': 25000, 'difficulty': '쉬움'},    {'title': '👥 공동구매', 'desc': '룸메이트/친구와 식재료 공동구매',     'saving': 35000, 'difficulty': '보통'},    {'title': '📱 앱 쿠폰 활용', 'desc': '배달앱 쿠폰, 편의점 1+1 행사 적극 활용',     'saving': 30000, 'difficulty': '쉬움'},]

# ============================================================
# 헤더
# ============================================================
st.markdown("""
<div class="main-header">
    <h1 style="margin:0; color:white;">🍱 AI 식비 절약 도우미</h1>
    <p style="margin:0.5rem 0 0 0; font-size:1.1rem;">대학생을 위한 똑똑한 식비 관리 솔루션</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# 사이드바: 사용자 정보 입력
# ============================================================
with st.sidebar:
    st.header("📋 내 정보 입력")
    st.markdown("---")
    
    name = st.text_input("이름", value="대학생")
    
    housing = st.selectbox(
        "🏠 주거 형태",
        ["자취", "기숙사", "통학"]
    )
    
    monthly_budget = st.number_input(
        "💰 월 식비 예산 (원)",
        min_value=100000,
        max_value=1000000,
        value=300000,
        step=10000
    )
    
    cooking_skill = st.select_slider(
        "👨‍🍳 요리 실력",
        options=["초급", "중급", "상급"],
        value="초급"
    )
    
    st.markdown("---")
    st.subheader("📊 현재 소비 패턴")
    
    eat_out = st.slider("🍽️ 외식 횟수 (주)", 0, 21, 7)
    delivery = st.slider("🛵 배달 횟수 (주)", 0, 14, 4)
    convenience = st.slider("🏪 편의점 이용 (주)", 0, 21, 5)
    cook_self = st.slider("🍳 직접 요리 (주)", 0, 21, 5)
    
    st.markdown("---")
    analyze_btn = st.button("🚀 AI 분석 시작!", use_container_width=True)

# ============================================================
# 메인 화면 - 탭 구성
# ============================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 소비 분석",
    "🤖 AI 추천",
    "🍳 맞춤 레시피",
    "💡 절약 팁",
    "📈 절약 시뮬레이션"
])

# ============================================================
# TAB 1: 소비 분석
# ============================================================
with tab1:
    st.header("📊 나의 식비 소비 패턴 분석")
    
    # 평균 단가 (원)
    avg_costs = {
        '외식': 8000,
        '배달': 12000,
        '편의점': 5000,
        '직접요리': 3000
    }
    
    weekly_spending = {
        '외식': eat_out * avg_costs['외식'],
        '배달': delivery * avg_costs['배달'],
        '편의점': convenience * avg_costs['편의점'],
        '직접요리': cook_self * avg_costs['직접요리']
    }
    
    monthly_spending = {k: v*4 for k, v in weekly_spending.items()}
    total_monthly = sum(monthly_spending.values())
    
    # 주요 지표
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "💰 월 예상 식비",
            f"{total_monthly:,}원",
            delta=f"{total_monthly - monthly_budget:+,}원 vs 예산",
            delta_color="inverse"
        )
    
    with col2:
        budget_rate = (total_monthly / monthly_budget) * 100
        st.metric(
            "📊 예산 사용률",
            f"{budget_rate:.1f}%",
            delta="초과" if budget_rate > 100 else "여유"
        )
    
    with col3:
        st.metric(
            "🍽️ 외식+배달 비중",
            f"{((monthly_spending['외식']+monthly_spending['배달'])/total_monthly*100):.1f}%"
        )
    
    with col4:
        daily_avg = total_monthly / 30
        st.metric("📅 일평균 식비", f"{daily_avg:,.0f}원")
    
    st.markdown("---")
    
    # 차트 영역
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("💸 월별 카테고리 지출")
        fig1, ax1 = plt.subplots(figsize=(8, 5))
        categories = list(monthly_spending.keys())
        values = list(monthly_spending.values())
        colors = ['#FF6B6B', '#FFA07A', '#FFD93D', '#6BCB77']
        bars = ax1.bar(categories, values, color=colors, edgecolor='white', linewidth=2)
        ax1.set_ylabel('지출액 (원)', fontsize=11)
        ax1.set_title('카테고리별 월 지출', fontsize=13, fontweight='bold')
        for bar, val in zip(bars, values):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                    f'{val:,}원', ha='center', va='bottom', fontsize=9)
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        st.pyplot(fig1)
    
    with col_right:
        st.subheader("🥧 지출 비율")
        fig2, ax2 = plt.subplots(figsize=(8, 5))
        ax2.pie(values, labels=categories, colors=colors, autopct='%1.1f%%',
                startangle=90, wedgeprops={'edgecolor': 'white', 'linewidth': 2})
        ax2.set_title('카테고리 비중', fontsize=13, fontweight='bold')
        st.pyplot(fig2)
    
    # 예산 비교 진행률 바
    st.subheader("🎯 예산 대비 사용률")
    progress = min(total_monthly / monthly_budget, 1.0)
    st.progress(progress)
    
    if total_monthly > monthly_budget:
        st.markdown(f"""
        <div class="warning-box">
            ⚠️ <b>예산 초과!</b> {total_monthly - monthly_budget:,}원 초과 지출 중입니다.
            AI 추천 탭에서 절약 방법을 확인해보세요!
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="success-box">
            ✅ <b>예산 내 사용 중!</b> {monthly_budget - total_monthly:,}원의 여유가 있습니다.
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# TAB 2: AI 추천
# ============================================================
with tab2:
    st.header("🤖 AI 맞춤 절약 전략")
    
    # AI 점수 계산
    risk_score = 0
    if eat_out > 7: risk_score += 30
    if delivery > 4: risk_score += 30
    if convenience > 7: risk_score += 20
    if cook_self < 3: risk_score += 20
    
    health_score = 100 - risk_score
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="margin:0;">🏆 식습관 점수</h3>
            <h1 style="margin:0; color:#FF6B6B;">{health_score}점</h1>
            <p style="margin:0; color:gray;">100점 만점</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        grade = "A" if health_score >= 80 else "B" if health_score >= 60 else "C" if health_score >= 40 else "D"
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="margin:0;">📊 종합 등급</h3>
            <h1 style="margin:0; color:#4ECDC4;">{grade}</h1>
            <p style="margin:0; color:gray;">소비 패턴 평가</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        potential_saving = (eat_out * 5000 + delivery * 8000) * 4
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="margin:0;">💰 절약 가능액</h3>
            <h1 style="margin:0; color:#6BCB77;">{potential_saving:,}원</h1>
            <p style="margin:0; color:gray;">월 기준 예상</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("🎯 AI 맞춤 추천 TOP 5")
    
    recommendations = []
    if eat_out > 7:
        recommendations.append({
            'title': '🍽️ 외식 빈도 조절 필요',
            'desc': f'주 {eat_out}회 외식 → 주 4회로 줄이면 월 **{(eat_out-4)*8000*4:,}원** 절약',
            'priority': '높음'
        })
    if delivery > 3:
        recommendations.append({
            'title': '🛵 배달 음식 줄이기',
            'desc': f'배달비+팁 포함 1회당 평균 2,000원 추가 지출. 주 2회로 줄이면 월 **{(delivery-2)*12000*4:,}원** 절약',
            'priority': '높음'
        })
    if cook_self < 5:
        recommendations.append({
            'title': '🍳 직접 요리 늘리기',
            'desc': f'직접 요리는 외식 대비 60% 저렴. 주 {7-cook_self}회 더 요리하면 영양과 비용 모두 OK!',
            'priority': '중간'
        })
    if convenience > 5:
        recommendations.append({
            'title': '🏪 편의점 의존도 낮추기',
            'desc': '편의점 식품은 마트 대비 30∼40% 비쌉니다. 주말에 마트에서 일주일치 장보기 추천',
            'priority': '중간'
        })
    
    # 기본 추천 추가
    recommendations.append({
        'title': '📱 가계부 앱 활용',
        'desc': '뱅크샐러드, 토스 등으로 실시간 식비 트래킹. 평균 15% 절감 효과',
        'priority': '낮음'
    })
    
    for i, rec in enumerate(recommendations[:5], 1):
        priority_color = {'높음': '#FF6B6B', '중간': '#FFD93D', '낮음': '#4ECDC4'}
        st.markdown(f"""
        <div class="recommendation-card">
            <h4 style="margin:0 0 0.5rem 0;">{i}. {rec['title']} 
                <span style="background:{priority_color[rec['priority']]}; color:white; padding:2px 10px; border-radius:10px; font-size:0.7rem;">
                    {rec['priority']}
                </span>
            </h4>
            <p style="margin:0; color:#555;">{rec['desc']}</p>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# TAB 3: 맞춤 레시피
# ============================================================
with tab3:
    st.header("🍳 AI 추천 맞춤 레시피")
    st.markdown(f"**{cooking_skill}** 수준에 맞는 저렴하고 간편한 레시피를 추천해드려요!")
    
    category = st.radio(
        "원하는 요리 종류를 선택하세요",
        list(RECIPE_DB.keys()),
        horizontal=True
    )
    
    st.markdown("---")
    
    recipes = RECIPE_DB[category]
    cols = st.columns(len(recipes))
    
    for col, recipe in zip(cols, recipes):
        with col:
            st.markdown(f"""
            <div class="recommendation-card" style="height: 280px;">
                <h3 style="margin:0;">🍽️ {recipe['name']}</h3>
                <p style="margin:0.5rem 0;"><b>💰 예상 비용:</b> {recipe['cost']:,}원</p>
                <p style="margin:0.5rem 0;"><b>⏱️ 조리 시간:</b> {recipe['time']}분</p>
                <p style="margin:0.5rem 0;"><b>📊 난이도:</b> {recipe['difficulty']}</p>
                <p style="margin:0.5rem 0;"><b>🔥 칼로리:</b> {recipe['kcal']}kcal</p>
                <p style="margin:0.5rem 0;"><b>🥘 재료:</b><br>{', '.join(recipe['ingredients'])}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("📅 일주일 식단 자동 생성")
    
    if st.button("🎲 이번 주 식단 추천 받기"):
        days = ['월', '화', '수', '목', '금', '토', '일']
        meal_plan = []
        all_recipes = [r for cat in RECIPE_DB.values() for r in cat]
        
        for day in days:
            lunch = random.choice(all_recipes)
            dinner = random.choice(all_recipes)
            meal_plan.append({
                '요일': day,
                '점심': f"{lunch['name']} ({lunch['cost']:,}원)",
                '저녁': f"{dinner['name']} ({dinner['cost']:,}원)",
                '일 비용': lunch['cost'] + dinner['cost']
            })
        
        df = pd.DataFrame(meal_plan)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        total_week = sum(m['일 비용'] for m in meal_plan)
        st.success(f"💰 **주간 총 식비: {total_week:,}원** (월 환산: 약 {total_week*4:,}원)")

# ============================================================
# TAB 4: 절약 팁
# ============================================================
with tab4:
    st.header("💡 식비 절약 꿀팁 모음")
    st.markdown("실제로 검증된 식비 절약 방법들을 난이도별로 정리했어요!")
    
    difficulty_filter = st.multiselect(
        "난이도 필터",
        ["쉬움", "보통", "어려움"],
        default=["쉬움", "보통", "어려움"]
    )
    
    filtered_tips = [t for t in SAVING_TIPS if t['difficulty'] in difficulty_filter]
    
    for tip in filtered_tips:
        diff_color = {'쉬움': '#6BCB77', '보통': '#FFD93D', '어려움': '#FF6B6B'}
        st.markdown(f"""
        <div class="tip-box">
            <h4 style="margin:0;">{tip['title']} 
                <span style="background:{diff_color[tip['difficulty']]}; color:white; padding:2px 10px; border-radius:10px; font-size:0.7rem;">
                    {tip['difficulty']}
                </span>
            </h4>
            <p style="margin:0.3rem 0; color:#555;">{tip['desc']}</p>
            <p style="margin:0; color:#4CAF50;"><b>💰 예상 절약액: 월 {tip['saving']:,}원</b></p>
        </div>
        """, unsafe_allow_html=True)
    
    total_potential = sum(t['saving'] for t in filtered_tips)
    st.markdown(f"""
    <div class="success-box" style="margin-top:1rem;">
        <h3 style="margin:0;">🎯 모든 팁 실천 시 예상 절약액</h3>
        <h1 style="margin:0; color:#4CAF50;">월 {total_potential:,}원 / 연 {total_potential*12:,}원</h1>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# TAB 5: 절약 시뮬레이션
# ============================================================
with tab5:
    st.header("📈 식비 절약 시뮬레이션")
    st.markdown("절약을 시작하면 1년 후 얼마나 모을 수 있을까요?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        saving_rate = st.slider(
            "💰 월 절약 목표 (%)",
            5, 50, 20,
            help="현재 식비에서 몇 % 절약할지 설정"
        )
    
    with col2:
        period = st.slider(
            "📅 시뮬레이션 기간 (개월)",
            3, 24, 12
        )
    
    monthly_saving = int(total_monthly * saving_rate / 100)
    
    # 월별 누적 그래프
    months = list(range(1, period + 1))
    cumulative = [monthly_saving * m for m in months]
    
    fig3, ax3 = plt.subplots(figsize=(12, 5))
    ax3.plot(months, cumulative, marker='o', linewidth=3, markersize=8,
             color='#FF6B6B', markerfacecolor='#FFA07A')
    ax3.fill_between(months, cumulative, alpha=0.3, color='#FFA07A')
    ax3.set_xlabel('개월', fontsize=12)
    ax3.set_ylabel('누적 절약액 (원)', fontsize=12)
    ax3.set_title(f'{period}개월 절약 시뮬레이션 (월 {saving_rate}% 절약)',
                  fontsize=14, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    ax3.spines['top'].set_visible(False)
    ax3.spines['right'].set_visible(False)
    
    # 마지막 포인트 강조
    ax3.annotate(f'{cumulative[-1]:,}원',
                xy=(months[-1], cumulative[-1]),
                xytext=(months[-1]-2, cumulative[-1]),
                fontsize=12, fontweight='bold', color='#FF6B6B')
    
    st.pyplot(fig3)
    
    # 결과 카드
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💰 월 절약액", f"{monthly_saving:,}원")
    with col2:
        st.metric(f"📅 {period}개월 후", f"{monthly_saving*period:,}원")
    with col3:
        st.metric("📊 연간 환산", f"{monthly_saving*12:,}원")
    
    # 절약액으로 할 수 있는 것들
    st.subheader("🎁 절약한 돈으로 할 수 있는 것들")
    total_saved = monthly_saving * period
    
    things = [
        ('📱 최신 스마트폰', 1200000),
        ('💻 노트북', 1500000),
        ('✈️ 일본 여행', 800000),
        ('🎓 어학 학원 등록', 400000),
        ('📚 전공 서적 1년치', 300000),
        ('☕ 카페 라떼', 5000),
    ]
    
    for item, price in things:
        count = total_saved / price
        if count >= 1:
            st.markdown(f"""
            <div class="tip-box">
                {item} <b>{count:.1f}개</b> 구매 가능! 
                ({price:,}원 기준)
            </div>
            """, unsafe_allow_html=True)

# ============================================================
# 푸터
# ============================================================
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:gray; padding:2rem;">
    <p>🍱 <b>AI 식비 절약 도우미</b> | 대학생 SW 프로젝트</p>
    <p style="font-size:0.9rem;">Made with ❤️ using Streamlit & Python</p>
    <p style="font-size:0.8rem;">© 2025 University SW Project</p>
</div>
""", unsafe_allow_html=True)