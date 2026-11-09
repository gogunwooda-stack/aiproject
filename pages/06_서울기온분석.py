
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

# =====================================
# 1. 페이지 기본 설정
# =====================================

st.set_page_config(
    page_title="월별 기온 분석",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 기온 분석")
st.write("원하는 월을 선택하여 연도별 최고기온과 최저기온을 비교해 보세요.")

# =====================================
# 2. 한글 폰트 설정
# =====================================

plt.rcParams["axes.unicode_minus"] = False

# =====================================
# 3. CSV 파일 경로 설정
# =====================================

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "temperature(2).csv"

# =====================================
# 4. CSV 파일 불러오기
# =====================================

def load_data():

    encodings = ["euc-kr", "cp949", "utf-8-sig", "utf-8"]

    for encoding in encodings:
        try:
            return pd.read_csv(CSV_PATH, encoding=encoding)
        except UnicodeDecodeError:
            continue

    raise ValueError("CSV 파일의 인코딩을 확인해 주세요.")

try:
    df = load_data()

except FileNotFoundError:
    st.error("CSV 파일을 찾을 수 없습니다.")
    st.info("temperature(2).csv 파일이 프로젝트 상위 폴더에 있는지 확인하세요.")
    st.stop()

except Exception as e:
    st.error(f"데이터 불러오기 오류: {e}")
    st.stop()

# =====================================
# 5. 필요한 데이터 확인
# =====================================

required_columns = [
    "일시",
    "최고기온(℃)",
    "최저기온(℃)"
]

if not all(col in df.columns for col in required_columns):
    st.error("CSV 파일의 열 이름이 올바르지 않습니다.")
    st.write("현재 열 이름:", df.columns.tolist())
    st.stop()

# =====================================
# 6. 날짜 데이터 변환
# =====================================

dates = []
previous = None

try:
    for value in df["일시"].astype(str).str.strip():

        month_text, year_text = value.split("-")

        month_num = datetime.strptime(
            month_text.title(), "%b"
        ).month

        short_year = int(year_text)

        candidates = [
            1900 + short_year,
            2000 + short_year
        ]

        valid_years = [
            year for year in candidates
            if previous is None
            or datetime(year, month_num, 1) >= previous
        ]

        if not valid_years:
            raise ValueError(f"날짜 순서 오류: {value}")

        selected_year = min(valid_years)

        current_date = datetime(
            selected_year,
            month_num,
            1
        )

        dates.append(current_date)
        previous = current_date

    df["날짜"] = pd.to_datetime(dates)

except Exception as e:
    st.error(f"날짜 변환 오류: {e}")
    st.stop()

df["연도"] = df["날짜"].dt.year
df["월"] = df["날짜"].dt.month

# =====================================
# 7. 기온 데이터 숫자 변환
# =====================================

df["최고기온(℃)"] = pd.to_numeric(
    df["최고기온(℃)"], errors="coerce"
)

df["최저기온(℃)"] = pd.to_numeric(
    df["최저기온(℃)"], errors="coerce"
)

# =====================================
# 8. 월 선택 기능
# =====================================

st.subheader("📅 분석할 월 선택")

selected_month = st.selectbox(
    "월을 선택하세요.",
    options=list(range(1, 13)),
    format_func=lambda x: f"{x}월"
)

# =====================================
# 9. 선택한 월 데이터 추출
# =====================================

month_df = df[
    df["월"] == selected_month
].copy()

month_df = month_df.dropna(
    subset=["최고기온(℃)", "최저기온(℃)"]
)

month_df = month_df.sort_values("연도")

if month_df.empty:
    st.warning("선택한 월에 데이터가 없습니다.")
    st.stop()

# =====================================
# 10. 기온 분석 그래프
# =====================================

fig, ax = plt.subplots(figsize=(14, 6))

# 최고기온 - 핫핑크
ax.plot(
    month_df["연도"],
    month_df["최고기온(℃)"],
    color="#FF1493",
    marker="o",
    markersize=4,
    linewidth=2,
    label="최고기온"
)

# 최저기온 - 하늘색
ax.plot(
    month_df["연도"],
    month_df["최저기온(℃)"],
    color="#87CEEB",
    marker="o",
    markersize=4,
    linewidth=2,
    label="최저기온"
)

# 그래프 제목 및 축
ax.set_title(
    "월별 기온 분석",
    fontsize=20,
    fontweight="bold",
    pad=20
)

ax.set_xlabel("연도", fontsize=13)
ax.set_ylabel("온도 (℃)", fontsize=13)

# 범례
ax.legend(
    fontsize=12,
    loc="best"
)

# 격자
ax.grid(
    True,
    linestyle="--",
    alpha=0.3
)

plt.tight_layout()

st.pyplot(fig, use_container_width=True)

plt.close(fig)

# =====================================
# 11. 선택한 월의 데이터 확인
# =====================================

st.subheader("📊 기온 데이터")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "평균 최고기온",
        f"{month_df['최고기온(℃)'].mean():.1f} ℃"
    )

with col2:
    st.metric(
        "평균 최저기온",
        f"{month_df['최저기온(℃)'].mean():.1f} ℃"
    )

with st.expander("연도별 상세 데이터 확인"):

    st.dataframe(
        month_df[
            ["연도", "최고기온(℃)", "최저기온(℃)"]
        ].reset_index(drop=True),
        use_container_width=True,
        hide_index=True
    )

st.caption(
    f"현재 {selected_month}월의 "
    f"{len(month_df)}개 연도 데이터를 분석했습니다."
)
