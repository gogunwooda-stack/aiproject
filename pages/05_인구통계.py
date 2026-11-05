from pathlib import Path
from io import BytesIO

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# ==========================================
# 페이지 설정
# ==========================================

st.set_page_config(
    page_title="서울시 연령별 인구 분석",
    page_icon="📊",
    layout="wide"
)

PINK = "#FF1493"


# ==========================================
# CSV 파일 불러오기 및 한글 인코딩
# ==========================================

@st.cache_data
def load_data(uploaded_file=None):

    # 직접 CSV를 업로드한 경우
    if uploaded_file is not None:

        raw = uploaded_file.getvalue()

        for encoding in ["cp949", "euc-kr", "utf-8-sig", "utf-8"]:
            try:
                return pd.read_csv(
                    BytesIO(raw),
                    encoding=encoding,
                    thousands=","
                )
            except UnicodeDecodeError:
                continue

        raise ValueError("CSV 파일의 인코딩을 확인해 주세요.")

    # 현재 파일은 pages 폴더 안에 있음
    page_folder = Path(__file__).resolve().parent

    # CSV는 pages 폴더의 상위 폴더에 있음
    project_root = page_folder.parent

    csv_name = "202012_202512_연령별인구현황_연간.csv"

    possible_paths = [
        project_root / csv_name,
        Path.cwd() / csv_name,
        page_folder / csv_name
    ]

    csv_path = next(
        (path for path in possible_paths if path.exists()),
        None
    )

    if csv_path is None:
        raise FileNotFoundError(
            "CSV 파일을 찾을 수 없습니다. "
            "pages 폴더의 상위 폴더에 CSV 파일을 넣어주세요."
        )

    # 한글 인코딩 자동 처리
    for encoding in ["cp949", "euc-kr", "utf-8-sig", "utf-8"]:
        try:
            return pd.read_csv(
                csv_path,
                encoding=encoding,
                thousands=","
            )
        except UnicodeDecodeError:
            continue

    raise ValueError("CSV 파일의 한글 인코딩을 확인해 주세요.")


# ==========================================
# 화면 제목
# ==========================================

st.title("📊 서울시 연령별 인구 분석")

st.caption(
    "행정구역, 성별, 연도를 선택하여 "
    "서울시의 연령별 인구 분포를 분석합니다."
)


# ==========================================
# 사이드바
# ==========================================

with st.sidebar:

    st.header("🔎 분석 설정")

    uploaded_csv = st.file_uploader(
        "CSV 파일 업로드 (선택)",
        type=["csv"]
    )


# ==========================================
# 데이터 불러오기
# ==========================================

try:

    df = load_data(uploaded_csv)

except Exception as e:

    st.error(f"데이터를 불러오지 못했습니다: {e}")

    st.info(
        "pages 폴더의 상위 폴더에 CSV 파일이 있는지 확인해 주세요."
    )

    st.stop()


# ==========================================
# 행정구역 데이터 정리
# ==========================================

if "행정구역" not in df.columns:

    st.error("행정구역 열을 찾을 수 없습니다.")

    st.stop()


# 행정구역 코드 제거
df["행정구역명"] = (
    df["행정구역"]
    .astype(str)
    .str.replace(r"\s*\(\d+\)\s*$", "", regex=True)
    .str.strip()
)


# ==========================================
# 연령대 설정
# ==========================================

age_labels = [
    "0~9세",
    "10~19세",
    "20~29세",
    "30~39세",
    "40~49세",
    "50~59세",
    "60~69세",
    "70~79세",
    "80~89세",
    "90~99세",
    "100세 이상"
]


# 성별 설정
sex_prefix = {
    "전체": "",
    "남성": "남_",
    "여성": "여_"
}


# ==========================================
# 연도 확인
# ==========================================

years = [str(y) for y in range(2020, 2026)]

available_years = [
    year
    for year in years
    if f"{year}년_거주자_0~9세" in df.columns
]

if not available_years:

    st.error("연도별 인구 데이터를 찾을 수 없습니다.")

    st.stop()


# ==========================================
# 행정구역 목록
# ==========================================

districts = df["행정구역명"].dropna().unique().tolist()

districts = sorted(
    districts,
    key=lambda x: (x != "서울특별시", x)
)


# ==========================================
# 사용자 선택
# ==========================================

st.subheader("📌 분석 조건 선택")

col1, col2, col3 = st.columns(3)


with col1:

    selected_district = st.selectbox(
        "행정구역 선택",
        districts,
        index=(
            districts.index("서울특별시")
            if "서울특별시" in districts
            else 0
        )
    )


with col2:

    selected_sex = st.selectbox(
        "성별 선택",
        ["전체", "남성", "여성"]
    )


with col3:

    selected_year = st.selectbox(
        "연도 선택",
        available_years,
        index=len(available_years) - 1
    )


# ==========================================
# 선택한 데이터 추출
# ==========================================

matched = df[
    df["행정구역명"] == selected_district
]


if matched.empty:

    st.warning("선택한 행정구역의 데이터가 없습니다.")

    st.stop()


row = matched.iloc[0]

prefix = sex_prefix[selected_sex]


# 연령별 데이터 열 이름
columns = [
    f"{selected_year}년_{prefix}거주자_{age}"
    for age in age_labels
]


# 데이터 열 존재 여부 확인
missing_columns = [
    col for col in columns
    if col not in df.columns
]


if missing_columns:

    st.error(
        f"필요한 데이터 열이 없습니다: {missing_columns}"
    )

    st.stop()


# 숫자 데이터 변환
values = (
    pd.to_numeric(row[columns], errors="coerce")
    .fillna(0)
    .astype(int)
)


# 그래프용 데이터프레임
chart_df = pd.DataFrame({

    "연령": age_labels,

    "인구수": values.values

})


# ==========================================
# 주요 인구 통계
# ==========================================

total_col = (
    f"{selected_year}년_"
    f"{prefix}거주자_총인구수"
)


if total_col in df.columns and pd.notna(row[total_col]):

    total_population = int(row[total_col])

else:

    total_population = int(chart_df["인구수"].sum())


max_age = chart_df.loc[
    chart_df["인구수"].idxmax(),
    "연령"
]


max_population = int(chart_df["인구수"].max())


# ==========================================
# 핵심 통계 표시
# ==========================================

st.subheader("📈 인구 통계 요약")

m1, m2, m3 = st.columns(3)


m1.metric(
    "총인구",
    f"{total_population:,}명"
)


m2.metric(
    "인구가 가장 많은 연령대",
    max_age
)


m3.metric(
    "해당 연령대 인구",
    f"{max_population:,}명"
)


# ==========================================
# 핫핑크 꺾은선 그래프
# ==========================================

fig = go.Figure()


fig.add_trace(

    go.Scatter(

        x=chart_df["연령"],

        y=chart_df["인구수"],

        mode="lines+markers",

        name="인구수",

        line=dict(
            color=PINK,
            width=4
        ),

        marker=dict(
            color=PINK,
            size=9,
            line=dict(
                color="white",
                width=1
            )
        ),

        hovertemplate=(
            "%{x}<br>"
            "인구수: %{y:,.0f}명"
            "<extra></extra>"
        )

    )

)


# ==========================================
# 그래프 디자인
# ==========================================

fig.update_layout(

    title=dict(

        text=(
            f"{selected_district} "
            f"{selected_sex} 인구 연령별 분포 "
            f"({selected_year}년)"
        ),

        x=0.02,
        xanchor="left"

    ),

    xaxis=dict(

        title="나이",

        type="category",

        categoryorder="array",

        categoryarray=age_labels,

        tickmode="array",

        tickvals=age_labels,

        ticktext=age_labels,

        showgrid=True,

        gridcolor="#E8E8E8",

        gridwidth=1

    ),

    yaxis=dict(

        title="인구수 (명)",

        rangemode="tozero",

        dtick=100000,

        tickformat=",",

        showgrid=True,

        gridcolor="#E8E8E8",

        gridwidth=1

    ),

    plot_bgcolor="white",

    paper_bgcolor="white",

    hovermode="x unified",

    height=570,

    margin=dict(
        l=25,
        r=25,
        t=80,
        b=40
    ),

    font=dict(
        family="Arial, sans-serif",
        size=13,
        color="#333333"
    )

)


# 그래프 출력
st.plotly_chart(
    fig,
    use_container_width=True
)


# ==========================================
# 데이터 표 확인
# ==========================================

with st.expander("📋 연령별 인구 데이터 확인"):

    display_df = chart_df.copy()

    display_df["인구수"] = display_df["인구수"].apply(
        lambda x: f"{x:,}명"
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


# ==========================================
# 결측치 확인
# ==========================================

with st.expander("🧹 데이터 품질 확인"):

    missing_count = int(
        df.isnull().sum().sum()
    )

    st.write(
        f"전체 데이터 결측치: **{missing_count:,}개**"
    )

    if missing_count == 0:

        st.success("결측치가 없습니다!")

    else:

        st.warning(
            "결측치가 포함되어 있습니다."
        )

        missing_by_column = df.isnull().sum()

        st.dataframe(
            missing_by_column[
                missing_by_column > 0
            ].rename("결측치 수"),
            use_container_width=True
        )


# ==========================================
# 하단 안내
# ==========================================

st.caption(
    "자료: 서울시 연령별 인구현황 CSV | "
    "연령 구간은 10세 단위이며, "
    "마지막 구간은 100세 이상입니다."
)
