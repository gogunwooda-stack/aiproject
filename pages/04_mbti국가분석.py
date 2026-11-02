
import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(
    page_title="세계 MBTI 국가별 분석",
    page_icon="🌍",
    layout="wide"
)

# MBTI 데이터
@st.cache_data
def load_data():
    df = pd.read_csv("countriesMBTI_16types(1).csv")
    df.columns = df.columns.str.strip()

    mbti_types = [
        "INFJ", "ISFJ", "INTP", "ISFP",
        "ENTP", "INFP", "ENTJ", "ISTP",
        "INTJ", "ESFP", "ESTJ", "ENFP",
        "ESTP", "ISTJ", "ENFJ", "ESFJ"
    ]

    for mbti in mbti_types:
        df[mbti] = pd.to_numeric(df[mbti], errors="coerce")

    return df, mbti_types


df, mbti_types = load_data()

# 제목
st.title("🌍 세계 국가별 MBTI 분석")
st.write("원하는 국가를 선택하고 MBTI 유형별 비율을 확인해 보세요.")

st.divider()

# 국가 선택
countries = sorted(df["Country"].dropna().unique())

default_index = (
    countries.index("South Korea")
    if "South Korea" in countries else 0
)

country = st.selectbox(
    "🌎 분석할 국가를 선택하세요.",
    countries,
    index=default_index
)

# 선택 국가 데이터
selected = df[df["Country"] == country].iloc[0]

# 그래프 데이터 생성
chart_data = pd.DataFrame({
    "MBTI": mbti_types,
    "비율": [selected[mbti] * 100 for mbti in mbti_types]
})

# 비율 높은 순서로 정렬
chart_data = chart_data.sort_values(
    "비율",
    ascending=False
).reset_index(drop=True)

# 색상 설정
# 1위는 빨간색, 나머지는 파란색 그라데이션
blue_colors = px.colors.sequential.Blues

colors = ["#E53935"] + [
    px.colors.sample_colorscale(
        blue_colors,
        i / 15 * 0.8 + 0.2
    )
    for i in range(15)
]

# 그래프 생성
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
    textfont_size=12,
    hovertemplate=(
        "<b>%{x}</b><br>"
        "비율: %{y:.2f}%<extra></extra>"
    )
)

fig.update_layout(
    title=dict(
        text=f"{country}의 MBTI 유형별 비율",
        x=0.5,
        xanchor="center"
    ),
    xaxis_title="MBTI 유형",
    yaxis_title="비율 (%)",
    showlegend=False,
    plot_bgcolor="white",
    paper_bgcolor="white",
    yaxis=dict(
        rangemode="tozero",
        gridcolor="#EEEEEE"
    ),
    margin=dict(
        t=80,
        b=50,
        l=40,
        r=30
    )
)

# 그래프 출력
st.plotly_chart(
    fig,
    use_container_width=True
)

# 1위 유형 표시
top = chart_data.iloc[0]

st.success(
    f"🏆 {country}에서 가장 높은 비율을 차지하는 MBTI는 "
    f"**{top['MBTI']}**이며, 비율은 **{top['비율']:.2f}%**입니다."
)

# 데이터 표
with st.expander("📊 상세 비율 확인하기"):
    display_data = chart_data.copy()
    display_data.index += 1
    display_data.index.name = "순위"

    st.dataframe(
        display_data.style.format({
            "비율": "{:.2f}%"
        }),
        use_container_width=True
    )

st.caption("※ 비율은 제공된 CSV 원본 데이터를 기준으로 표시합니다.")
