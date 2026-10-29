
import streamlit as st

st.set_page_config(
    page_title="MBTI 진로 탐험소",
    page_icon="🧭",
    layout="wide"
)

# -------------------------------
# 🎨 화면 디자인
# -------------------------------
st.markdown("""
<style>
    .main {
        background-color: #F7F9FC;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1000px;
    }
    .hero {
        padding: 28px;
        border-radius: 20px;
        background: linear-gradient(120deg, #DCEBFF, #F0E4FF);
        margin-bottom: 20px;
    }
    .career-card {
        background-color: white;
        border: 1px solid #E3E8F0;
        border-radius: 16px;
        padding: 22px;
        min-height: 280px;
    }
    .salary {
        color: #2859B8;
        font-size: 23px;
        font-weight: bold;
    }
    .small-note {
        color: #667085;
        font-size: 13px;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------
# 🧭 MBTI별 진로 데이터
# 연봉은 국내 직업의 대략적인 참고 범위
# -------------------------------
career_data = {
    "ISTJ": {
        "intro": "차근차근 계획을 세우고 책임감 있게 실행하는 현실적인 유형!",
        "careers": [
            {
                "name": "회계사",
                "emoji": "📊",
                "work": "기업의 재무제표를 검토하고 회계 및 세무 관련 업무를 수행해요.",
                "major": "회계학과, 경영학과, 세무학과",
                "personality": "꼼꼼하고 숫자를 분석하는 것을 좋아하며 책임감이 강한 사람",
                "salary": "약 5,000만~1억 원 이상",
            },
            {
                "name": "품질관리 전문가",
                "emoji": "🔍",
                "work": "제품과 서비스가 정해진 기준을 만족하는지 검사하고 개선해요.",
                "major": "산업공학과, 화학공학과, 식품공학과",
                "personality": "세부 사항을 잘 확인하고 기준과 절차를 지키는 사람",
                "salary": "약 3,500만~6,000만 원",
            },
        ],
    },
    "ISFJ": {
        "intro": "세심하게 주변을 살피고 다른 사람을 챙기는 따뜻한 유형!",
        "careers": [
            {
                "name": "간호사",
                "emoji": "🩺",
                "work": "환자의 상태를 확인하고 치료와 회복을 도와요.",
                "major": "간호학과",
                "personality": "배려심이 있고 세심하며 책임감이 강한 사람",
                "salary": "약 3,500만~5,500만 원",
            },
            {
                "name": "영양사",
                "emoji": "🥗",
                "work": "건강 상태와 목적에 맞는 식단을 계획하고 급식을 관리해요.",
                "major": "식품영양학과, 영양학과",
                "personality": "꼼꼼하고 사람들의 건강을 챙기는 데 관심이 있는 사람",
                "salary": "약 2,800만~4,500만 원",
            },
        ],
    },
    "INFJ": {
        "intro": "사람의 마음을 이해하고 의미 있는 변화를 만들고 싶은 유형!",
        "careers": [
            {
                "name": "상담심리 전문가",
                "emoji": "💬",
                "work": "사람들의 고민을 듣고 감정과 문제를 이해하도록 도와요.",
                "major": "심리학과, 상담학과, 상담심리학과",
                "personality": "공감 능력이 좋고 다른 사람의 이야기를 잘 듣는 사람",
                "salary": "약 2,800만~4,500만 원",
            },
            {
                "name": "작가",
                "emoji": "✍️",
                "work": "소설, 에세이, 콘텐츠 등 다양한 글을 기획하고 작성해요.",
                "major": "국어국문학과, 문예창작학과, 미디어학과",
                "personality": "관찰력이 좋고 생각과 감정을 글로 표현하는 사람",
                "salary": "약 2,500만~5,000만 원",
            },
        ],
    },
    "INTJ": {
        "intro": "큰 그림을 보고 논리적으로 계획하며 문제를 해결하는 전략가!",
        "careers": [
            {
                "name": "데이터 분석가",
                "emoji": "📈",
                "work": "데이터를 분석해 문제의 원인을 찾고 의사결정을 도와요.",
                "major": "통계학과, 데이터사이언스학과, 산업공학과",
                "personality": "논리적이고 분석적이며 혼자 깊이 탐구하는 것을 좋아하는 사람",
                "salary": "약 3,500만~7,000만 원",
            },
            {
                "name": "소프트웨어 개발자",
                "emoji": "💻",
                "work": "웹사이트, 앱, 프로그램 등을 설계하고 개발해요.",
                "major": "컴퓨터공학과, 소프트웨어학과, AI학과",
                "personality": "문제 해결을 즐기고 새로운 기술을 배우는 사람",
                "salary": "약 3,500만~7,000만 원",
            },
        ],
    },
    "ISTP": {
        "intro": "직접 만지고 실험하며 문제를 해결하는 실전형 유형!",
        "careers": [
            {
                "name": "자동차 정비사",
                "emoji": "🚗",
                "work": "자동차의 고장 원인을 진단하고 부품을 점검하거나 수리해요.",
                "major": "자동차공학과, 미래자동차학과",
                "personality": "기계를 다루는 데 흥미가 있고 침착하게 문제를 해결하는 사람",
                "salary": "약 3,000만~5,000만 원",
            },
            {
                "name": "조리사",
                "emoji": "👨‍🍳",
                "work": "식재료를 손질하고 조리 기술을 활용해 메뉴를 완성해요.",
                "major": "조리학과, 호텔조리학과, 외식조리학과",
                "personality": "손으로 직접 작업하는 것을 좋아하고 상황에 유연하게 대처하는 사람",
                "salary": "약 2,800만~4,500만 원",
            },
        ],
    },
    "ISFP": {
        "intro": "감각이 섬세하고 자신만의 취향과 표현을 중요하게 생각하는 유형!",
        "careers": [
            {
                "name": "제품 디자이너",
                "emoji": "🎨",
                "work": "사용하기 편하고 보기 좋은 제품의 형태와 기능을 디자인해요.",
                "major": "산업디자인학과, 제품디자인학과",
                "personality": "미적 감각이 있고 관찰력과 표현력이 좋은 사람",
                "salary": "약 3,000만~5,000만 원",
            },
            {
                "name": "파티시에",
                "emoji": "🧁",
                "work": "케이크, 빵, 디저트를 만들고 새로운 제품을 개발해요.",
                "major": "제과제빵과, 제과제빵학과, 호텔제과제빵학과",
                "personality": "섬세하고 감각적이며 반복 연습을 통해 완성도를 높이는 사람",
                "salary": "약 2,700만~4,500만 원",
            },
        ],
    },
    "INFP": {
        "intro": "자신만의 가치관과 상상력을 바탕으로 의미를 찾는 이상주의자!",
        "careers": [
            {
                "name": "콘텐츠 기획자",
                "emoji": "📱",
                "work": "사람들이 흥미를 느낄 영상, 글, 디지털 콘텐츠를 기획해요.",
                "major": "미디어학과, 광고홍보학과, 문화콘텐츠학과",
                "personality": "상상력이 풍부하고 새로운 아이디어를 떠올리는 사람",
                "salary": "약 3,000만~5,000만 원",
            },
            {
                "name": "사회복지사",
                "emoji": "🤝",
                "work": "도움이 필요한 사람들의 생활과 복지 문제를 지원해요.",
                "major": "사회복지학과, 사회복지과",
                "personality": "공감 능력이 좋고 사회 문제에 관심이 있는 사람",
                "salary": "약 2,800만~4,000만 원",
            },
        ],
    },
    "INTP": {
        "intro": "호기심이 많고 원리를 파고들며 새로운 가능성을 탐구하는 유형!",
        "careers": [
            {
                "name": "연구원",
                "emoji": "🔬",
                "work": "전문 분야의 질문을 세우고 실험과 분석을 통해 새로운 지식을 찾아요.",
                "major": "자연과학 계열, 공학 계열, 관련 전공",
                "personality": "호기심이 많고 논리적으로 생각하며 탐구를 즐기는 사람",
                "salary": "약 3,500만~6,500만 원",
            },
            {
                "name": "AI 엔지니어",
                "emoji": "🤖",
                "work": "인공지능 모델과 서비스를 개발하고 성능을 개선해요.",
                "major": "컴퓨터공학과, 인공지능학과, 수학과",
                "personality": "논리적 사고와 실험을 좋아하고 새로운 기술에 관심이 많은 사람",
                "salary": "약 4,000만~8,000만 원",
            },
        ],
    },
    "ESTP": {
        "intro": "행동이 빠르고 현장 대응력이 뛰어난 에너지 넘치는 유형!",
        "careers": [
            {
                "name": "영업 전문가",
                "emoji": "🤝",
                "work": "고객의 요구를 파악하고 제품이나 서비스의 가치를 전달해요.",
                "major": "경영학과, 마케팅학과, 유통학과",
                "personality": "적극적이고 순발력이 좋으며 사람과 대화하는 것을 즐기는 사람",
                "salary": "약 3,000만~6,000만 원",
            },
            {
                "name": "응급구조사",
                "emoji": "🚑",
                "work": "응급 상황에서 환자의 상태를 확인하고 응급처치를 수행해요.",
                "major": "응급구조학과",
                "personality": "침착하고 판단이 빠르며 긴급한 상황에 대응할 수 있는 사람",
                "salary": "약 3,000만~4,500만 원",
            },
        ],
    },
    "ESFP": {
        "intro": "사람들과 어울리는 것을 좋아하고 즐거운 분위기를 만드는 유형!",
        "careers": [
            {
                "name": "호텔리어",
                "emoji": "🏨",
                "work": "호텔을 방문한 고객에게 안내와 서비스, 숙박 관련 업무를 제공해요.",
                "major": "호텔경영학과, 호텔관광학과",
                "personality": "친화력이 좋고 서비스 정신과 현장 대처 능력이 있는 사람",
                "salary": "약 2,800만~4,500만 원",
            },
            {
                "name": "방송인·MC",
                "emoji": "🎤",
                "work": "방송과 행사에서 사람들과 소통하며 프로그램을 진행해요.",
                "major": "방송연예과, 미디어학과, 신문방송학과",
                "personality": "표현력이 좋고 사람들 앞에서 소통하는 것을 즐기는 사람",
                "salary": "수입 편차가 커서 일률적인 평균 제시가 어려워요.",
            },
        ],
    },
    "ENFP": {
        "intro": "새로운 아이디어와 사람에게서 에너지를 얻는 열정적인 유형!",
        "careers": [
            {
                "name": "광고 기획자",
                "emoji": "💡",
                "work": "브랜드를 알리기 위한 광고 아이디어와 캠페인을 기획해요.",
                "major": "광고홍보학과, 경영학과, 미디어학과",
                "personality": "아이디어가 풍부하고 소통을 즐기며 변화에 유연한 사람",
                "salary": "약 3,000만~5,500만 원",
            },
            {
                "name": "이벤트 기획자",
                "emoji": "🎉",
                "work": "축제, 행사, 전시 등 다양한 이벤트를 기획하고 운영해요.",
                "major": "이벤트학과, 관광학과, 문화콘텐츠학과",
                "personality": "활동적이고 기획력과 대인관계 능력이 좋은 사람",
                "salary": "약 2,800만~4,500만 원",
            },
        ],
    },
    "ENTP": {
        "intro": "익숙한 방식에 질문을 던지고 새로운 해결책을 찾는 아이디어형!",
        "careers": [
            {
                "name": "창업가",
                "emoji": "🚀",
                "work": "새로운 사업 아이디어를 구체화하고 제품이나 서비스를 시장에 선보여요.",
                "major": "경영학과, 창업학과, 산업공학과 등",
                "personality": "도전을 즐기고 기회를 발견하며 문제 해결을 좋아하는 사람",
                "salary": "사업 성과에 따라 편차가 매우 커요.",
            },
            {
                "name": "브랜드 마케터",
                "emoji": "📣",
                "work": "브랜드의 이미지를 만들고 고객에게 효과적으로 알리는 전략을 세워요.",
                "major": "경영학과, 광고홍보학과, 마케팅학과",
                "personality": "분석력과 아이디어를 함께 활용하고 변화를 즐기는 사람",
                "salary": "약 3,200만~6,000만 원",
            },
        ],
    },
    "ESTJ": {
        "intro": "목표를 세우고 사람과 일을 체계적으로 이끄는 실행형 유형!",
        "careers": [
            {
                "name": "프로젝트 매니저",
                "emoji": "📋",
                "work": "프로젝트의 일정과 예산, 인력을 관리해 목표를 달성하도록 이끌어요.",
                "major": "경영학과, 산업공학과, 정보시스템학과",
                "personality": "조직적이고 책임감이 강하며 계획을 실행하는 데 능숙한 사람",
                "salary": "약 4,000만~7,000만 원",
            },
            {
                "name": "물류관리 전문가",
                "emoji": "📦",
                "work": "상품의 보관과 운송, 재고 흐름을 효율적으로 관리해요.",
                "major": "물류학과, 유통학과, 산업공학과",
                "personality": "계획적이고 실용적이며 문제를 체계적으로 해결하는 사람",
                "salary": "약 3,200만~5,500만 원",
            },
        ],
    },
    "ESFJ": {
        "intro": "사람들과 협력하고 주변을 챙기며 안정적인 분위기를 만드는 유형!",
        "careers": [
            {
                "name": "교사",
                "emoji": "📚",
                "work": "학생의 학습과 성장을 돕고 수업과 생활지도를 담당해요.",
                "major": "교육학과, 사범대학 관련 학과, 교직 이수 전공",
                "personality": "책임감이 있고 설명을 잘하며 다른 사람의 성장을 돕는 사람",
                "salary": "약 3,000만~6,000만 원 이상",
            },
            {
                "name": "인사 담당자",
                "emoji": "👥",
                "work": "채용, 교육, 조직문화 등 회사의 인력 관련 업무를 맡아요.",
                "major": "경영학과, 심리학과, 행정학과",
                "personality": "소통을 잘하고 협력과 조직 운영에 관심이 있는 사람",
                "salary": "약 3,200만~5,500만 원",
            },
        ],
    },
    "ENFJ": {
        "intro": "사람의 가능성을 발견하고 함께 성장하도록 이끄는 유형!",
        "careers": [
            {
                "name": "HRD·교육 기획자",
                "emoji": "🌱",
                "work": "조직 구성원의 역량을 높이는 교육 프로그램을 기획하고 운영해요.",
                "major": "교육학과, 경영학과, 심리학과",
                "personality": "소통 능력이 좋고 사람의 성장과 협업에 관심이 있는 사람",
                "salary": "약 3,200만~5,500만 원",
            },
            {
                "name": "홍보 전문가",
                "emoji": "📢",
                "work": "기업이나 기관의 소식을 전달하고 긍정적인 이미지를 만들어 가요.",
                "major": "미디어학과, 광고홍보학과, 경영학과",
                "personality": "표현력이 좋고 사람들과 관계를 맺는 데 능숙한 사람",
                "salary": "약 3,000만~5,500만 원",
            },
        ],
    },
    "ENTJ": {
        "intro": "목표를 향해 전략을 세우고 도전을 이끄는 리더형 유형!",
        "careers": [
            {
                "name": "경영 컨설턴트",
                "emoji": "🧩",
                "work": "기업의 문제를 분석하고 성과를 높일 수 있는 전략을 제안해요.",
                "major": "경영학과, 경제학과, 산업공학과",
                "personality": "분석적이고 목표 지향적이며 복잡한 문제 해결을 좋아하는 사람",
                "salary": "약 4,000만~8,000만 원 이상",
            },
            {
                "name": "기업 경영자",
                "emoji": "🏢",
                "work": "기업의 방향과 사업 전략을 정하고 조직과 자원을 관리해요.",
                "major": "경영학과, 경제학과 등 다양한 전공",
                "personality": "의사결정에 적극적이고 책임감과 조직 운영 능력이 있는 사람",
                "salary": "직위와 기업 성과에 따라 편차가 매우 커요.",
            },
        ],
    },
}

# -------------------------------
# 🏠 첫 화면
# -------------------------------
st.markdown("""
<div class="hero">
    <h1>🧭 MBTI 진로 탐험소</h1>
    <h3>나를 알아보고, 나에게 어울리는 미래를 탐험해 보자!</h3>
    <p>16가지 MBTI 유형별 추천 진로 2가지와 학과, 성향, 연봉 정보를 확인해 봐.</p>
</div>
""", unsafe_allow_html=True)

st.info(
    "💡 MBTI는 진로를 결정하는 정답이 아니야! "
    "추천 결과를 참고하되, 네가 좋아하는 활동과 실제 경험도 함께 생각해 봐."
)

mbti_list = [
    "ISTJ", "ISFJ", "INFJ", "INTJ",
    "ISTP", "ISFP", "INFP", "INTP",
    "ESTP", "ESFP", "ENFP", "ENTP",
    "ESTJ", "ESFJ", "ENFJ", "ENTJ"
]

col1, col2 = st.columns([2, 1])

with col1:
    selected_mbti = st.selectbox(
        "🔮 너의 MBTI를 선택해 줘!",
        mbti_list,
        index=0
    )

with col2:
    st.write("")
    st.write("")
    st.metric("추천 진로", "2가지")

info = career_data[selected_mbti]

st.markdown("---")
st.subheader(f"✨ {selected_mbti} 유형의 진로 탐험")
st.write(info["intro"])
st.caption("아래 직업은 해당 유형에 어울릴 수 있는 예시야. 개인의 성격과 경험에 따라 달라질 수 있어!")

# -------------------------------
# 💼 추천 직업 카드
# -------------------------------
career_col1, career_col2 = st.columns(2)

for col, career in zip(
    [career_col1, career_col2],
    info["careers"]
):
    with col:
        st.markdown(
            f"""
            <div class="career-card">
                <h2>{career['emoji']} {career['name']}</h2>
                <p>{career['work']}</p>
                <hr>
                <p><b>🎓 관련 학과</b><br>{career['major']}</p>
                <p><b>🧠 잘 맞을 수 있는 성향</b><br>{career['personality']}</p>
                <p><b>💰 참고 연봉</b></p>
                <p class="salary">{career['salary']}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown("---")
st.subheader("📝 진로 탐험 미션")

st.write("추천 직업 중 더 궁금한 직업을 골라서 생각해 보자!")

all_careers = [
    career["name"] for career in info["careers"]
]

favorite = st.radio(
    "가장 관심이 가는 직업은?",
    all_careers,
    horizontal=True
)

reason = st.text_area(
    "그 직업이 궁금한 이유나 해 보고 싶은 활동을 적어 봐!",
    placeholder="예: 직접 요리를 개발하고 사람들에게 새로운 맛을 소개하고 싶어."
)

if st.button("🌟 나의 진로 관심 정리하기", use_container_width=True):
    st.success(f"좋아! 오늘의 관심 직업은 '{favorite}'이네.")
    if reason.strip():
        st.write("💬 내가 적은 관심 이유")
        st.write(reason)
    else:
        st.write("관심을 가진 이유도 천천히 생각해 봐. 작은 호기심이 좋은 출발점이 될 수 있어!")

st.markdown("---")
st.subheader("🔎 더 자세히 알아보기")

st.markdown(
    "- [커리어넷 직업백과](https://www.career.go.kr/) — 직업 정보와 관련 학과 탐색\n"
    "- [워크넷 임금직업포털 워크피디아](https://www.wagework.go.kr/) — 임금 및 직업 관련 통계 확인"
)

st.caption(
    "※ 연봉은 직업별 공식 통계값을 실시간으로 불러오는 기능이 없는 참고용 추정 범위야. "
    "신입·경력, 근무 지역, 기업 규모, 자격 및 성과에 따라 실제 연봉은 달라질 수 있어. "
    "창업가와 방송인처럼 수입 편차가 큰 직업은 일률적인 평균을 제시하기 어려워."
)

st.caption("Made with 💙 for your future")
