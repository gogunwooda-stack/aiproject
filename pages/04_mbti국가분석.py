
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ==========================================
# 1. 페이지 기본 설정
# ==========================================

st.set_page_config(
    page_title="세계 MBTI 분석",
    page_icon="🌍",
    layout="wide"
)

# ==========================================
# 2. 디자인 CSS
# ==========================================

st.markdown("""
<style>
    .main {
        background-color: #F8FAFC;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .main-title {
        font-size: 35px;
        font-weight: 800;
        color: #172554;
        margin-bottom: 5px;
    }

    .sub-title {
        font-size: 15px;
        color: #64748B;
        margin-bottom: 25px;
    }

    .info-card {
        background: white;
        padding: 22px;
        border-radius: 16px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 3px 12px rgba(0,0,0,0.04);
    }

    .info-label {
        font-size: 14px;
        color: #64748B;
    }

    .info-value {
        font-size: 30px;
        font-weight: 800;
        color: #1E293B;
    }

    .winner-card {
        background: linear-gradient(135deg, #FFF1F2, #FFFFFF);
        padding: 22px;
        border-radius: 16px;
        border: 1px solid #FECDD3;
    }

    .winner-title {
        font-size: 14px;
        color: #BE123C;
    }

    .winner-value {
        font-size: 30px;
        font-weight: 800;
        color: #E11D48;
    }

    div[data-testid="stSelectbox"] {
        background: white;
        border-radius: 12px;
    }

    h2, h3 {
        color: #1E293B;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. 데이터 불러오기
# ==========================================

@st.cache_data
def load_data():

    current_dir = Path(__file__).resolve().parent

    candidates = [
        current_dir.parent / "countriesMBTI_16types.csv",
        current_dir / "countriesMBTI_16types(1).csv",
        current_dir.parent / "data" / "countriesMBTI_16types(1).csv",
        Path.cwd() / "countriesMBTI_16types.csv",
    ]

    csv_path = next(
        (p for p in candidates if p.is_file()),
        None
    )

    if csv_path is None:
        raise FileNotFoundError(
            "CSV 파일을 찾을 수 없습니다. "
            "GitHub 저장소 최상위 폴더에 "
            "countriesMBTI_16types(1).csv를 업로드해 주세요."
        )

    df = pd.read_csv(
        csv_path,
        encoding="utf-8-sig"
    )

    df.columns = df.columns.str.strip()

    if "Country" not in df.columns:
        raise ValueError("CSV에 Country 열이 없습니다.")

    mbti_types = [
        "INFJ", "ISFJ", "INTP", "ISFP",
        "ENTP", "INFP", "ENTJ", "ISTP",
        "INTJ", "ESFP", "ESTJ", "ENFP",
        "ESTP", "ISTJ", "ENFJ", "ESFJ"
    ]

    missing = [
        t for t in mbti_types
        if t not in df.columns
    ]

    if missing:
        raise ValueError(
            f"CSV에서 MBTI 열을 찾을 수 없습니다: {missing}"
        )

    for t in mbti_types:
        df[t] = pd.to_numeric(
            df[t], errors="coerce"
        )

    df["Country"] = df["Country"].astype(str).str.strip()

    df = df.dropna(subset=["Country"])

    return df, mbti_types


try:
    df, mbti_types = load_data()

except Exception as e:
    st.error("⚠️ 데이터를 불러오는 중 오류가 발생했습니다.")
    st.code(str(e))
    st.info(
        "GitHub 저장소의 CSV 파일 위치와 이름을 확인해 주세요."
    )
    st.stop()

# ==========================================
# 4. 제목
# ==========================================

st.markdown(
    '<div class="main-title">🌍 WORLD MBTI ANALYSIS</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    '국가를 선택하고 16가지 MBTI 유형의 비율을 한눈에 비교해 보세요.'
    '</div>',
    unsafe_allow_html=True
)

st.divider()

# ==========================================
# 5. 국가 선택
# ==========================================

countries = sorted(df["Country"].unique())

default_index = (
    countries.index("South Korea")
    if "South Korea" in countries else 0
)

country = st.selectbox(
    "🌎 분석할 국가 선택",
    countries,
    index=default_index
)

selected = df[df["Country"] == country].iloc[0]

# ==========================================
# 6. 그래프 데이터 정리
# ==========================================

chart_data = pd.DataFrame({
    "MBTI": mbti_types,
    "비율": [
        selected[t] * 100
        for t in mbti_types
    ]
})

chart_data = chart_data.dropna(
    subset=["비율"]
)

chart_data = chart_data.sort_values(
    "비율",
    ascending=False
).reset_index(drop=True)

if chart_data.empty:
    st.warning("선택한 국가의 MBTI 데이터가 없습니다.")
    st.stop()

# ==========================================
# 7. 상위 MBTI 정보
# ==========================================

top = chart_data.iloc[0]

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f"""
        <div class="info-card">
            <div class="info-label">🌍 선택 국가</div>
            <div class="info-value">{country}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div class="winner-card">
            <div class="winner-title">🏆 가장 높은 MBTI</div>
            <div class="winner-value">{top['MBTI']}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div class="info-card">
            <div class="info-label">📊 최고 비율</div>
            <div class="info-value">{top['비율']:.2f}%</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.write("")

# ==========================================
# 8. 막대그래프 색상
# ==========================================

# 1위 빨간색
# 2~16위 파란색 그라데이션

blue_colors = px.colors.sample_colorscale(
    "Blues",
    [0.95 - i * (0.75 / 14) for i in range(15)]
)

colors = ["#E53935"] + blue_colors

# ==========================================
# 9. 그래프 생성
# ==========================================

fig = px.bar(
    chart_data,
    x="MBTI",
    y="비율",
    text=chart_data["비율"].apply(
        lambda x: f"{x:.2f}%"
    )
)

fig.update_traces(
    marker_color=colors,
    textposition="outside",
    textfont=dict(
        size=12,
        color="#334155"
    ),
    cliponaxis=False,
    hovertemplate=(
        "<b>%{x}</b><br>"
        "비율: %{y:.2f}%"
        "<extra></extra>"
    )
)

fig.update_layout(
    title=dict(
        text=f"{country}의 MBTI 유형별 분포",
        font=dict(size=21, color="#172554"),
        x=0.02
    ),
    xaxis=dict(
        title="MBTI 유형",
        categoryorder="array",
        categoryarray=chart_data["MBTI"].tolist(),
        tickfont=dict(size=12)
    ),
    yaxis=dict(
        title="비율 (%)",
        rangemode="tozero",
        gridcolor="#E2E8F0",
        zeroline=False
    ),
    plot_bgcolor="white",
    paper_bgcolor="white",
    showlegend=False,
    margin=dict(
        t=80,
        b=60,
        l=50,
        r=30
    ),
    height=520
)

# ==========================================
# 10. 그래프 출력
# ==========================================

st.markdown("### 📊 MBTI 비율 분석")

st.plotly_chart(
    fig,
    use_container_width=True,
    config={
        "displayModeBar": False,
        "responsive": True
    }
)

# ==========================================
# 11. 순위표
# ==========================================

with st.expander("🏆 MBTI 전체 순위 자세히 보기"):

    ranking = chart_data.copy()
    ranking.insert(
        0,
        "순위",
        range(1, len(ranking) + 1)
    )

    ranking["비율"] = ranking["비율"].map(
        lambda x: f"{x:.2f}%"
    )

    st.dataframe(
        ranking,
        use_container_width=True,
        hide_index=True
    )

# ==========================================
# 12. 안내
# ==========================================

st.divider()

st.caption(
    "WORLD MBTI ANALYSIS | "
    "원본 CSV 데이터를 기반으로 국가별 MBTI 비율을 시각화합니다."
)
