
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from pathlib import Path
import re

# 페이지 설정
st.set_page_config(
    page_title="월별 평균기온 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 평균기온 분석 및 예측")
st.write("과거 기온 데이터를 분석하고 선형회귀 알고리즘으로 미래 기온을 예측합니다.")

# 한글 폰트 및 그래프 설정
plt.rcParams["axes.unicode_minus"] = False

# CSV 파일 불러오기
@st.cache_data
def load_data():
    base_dir = Path(__file__).resolve().parent

    file_candidates = [
        base_dir / "temperature.csv",
        base_dir / "temperrature.csv"
    ]

    csv_path = next((p for p in file_candidates if p.exists()), None)

    if csv_path is None:
        raise FileNotFoundError(
            "temperature.csv 파일을 app.py와 같은 폴더에 넣어주세요."
        )

    for encoding in ["cp949", "euc-kr", "utf-8-sig", "utf-8"]:
        try:
            data = pd.read_csv(csv_path, encoding=encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError("CSV 파일의 인코딩을 확인해주세요.")

    # 필요한 열 확인
    if "일시" not in data.columns or "평균기온(℃)" not in data.columns:
        raise ValueError(
            "CSV에 '일시'와 '평균기온(℃)' 열이 필요합니다."
        )

    # 날짜 분석: Oct-07 형식
    dates = data["일시"].astype(str).str.strip()
    extracted = dates.str.extract(r"^([A-Za-z]{3})-(\d{2})$")

    month_dict = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
        "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
        "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
    }

    data["월"] = extracted[0].str.title().map(month_dict)
    year_numbers = pd.to_numeric(extracted[1], errors="coerce")

    # CSV의 시간 순서에 따라 세기를 계산
    full_years = []
    century = 1900
    previous_year = None

    for value in year_numbers:
        if pd.isna(value):
            full_years.append(np.nan)
            continue

        value = int(value)

        if previous_year is not None and value < previous_year:
            century += 100

        full_years.append(century + value)
        previous_year = value

    data["연도"] = full_years

    data["평균기온(℃)"] = pd.to_numeric(
        data["평균기온(℃)"], errors="coerce"
    )

    data = data.dropna(
        subset=["연도", "월", "평균기온(℃)"]
    ).copy()

    data["연도"] = data["연도"].astype(int)
    data["월"] = data["월"].astype(int)

    return data.sort_values(["연도", "월"]).reset_index(drop=True)


try:
    df = load_data()
except Exception as e:
    st.error(f"데이터를 불러오지 못했습니다: {e}")
    st.stop()

# 사이드바
st.sidebar.header("📌 예측 조건")

selected_month = st.sidebar.selectbox(
    "분석할 월 선택",
    list(range(1, 13)),
    format_func=lambda x: f"{x}월"
)

last_year = int(df["연도"].max())

forecast_year = st.sidebar.number_input(
    "예측할 연도",
    min_value=last_year + 1,
    max_value=2100,
    value=last_year + 1,
    step=1
)

# 선택한 월의 전체 데이터
month_df = df[df["월"] == selected_month].copy()
month_df = month_df.sort_values("연도")

if len(month_df) < 2:
    st.error("선택한 월의 데이터가 부족합니다.")
    st.stop()

# 선형회귀 학습
X = month_df[["연도"]].values
y = month_df["평균기온(℃)"].values

model = LinearRegression()
model.fit(X, y)

# 예측
predicted_temp = model.predict(
    np.array([[int(forecast_year)]])
)[0]

# 모델 정보
slope = model.coef_[0]
intercept = model.intercept_
r2 = model.score(X, y)

# 회귀 직선 생성
line_years = np.arange(
    int(month_df["연도"].min()),
    int(forecast_year) + 1
)

line_temps = model.predict(line_years.reshape(-1, 1))

# 결과 표시
st.subheader(f"📊 {selected_month}월 평균기온 분석 결과")

c1, c2, c3 = st.columns(3)

c1.metric(
    "🔮 예측 평균기온",
    f"{predicted_temp:.2f} ℃"
)

c2.metric(
    "📚 학습 데이터",
    f"{len(month_df)}개"
)

c3.metric(
    "📈 결정계수 R²",
    f"{r2:.3f}"
)

st.divider()

# 그래프
st.subheader("📈 실제 기온과 선형회귀 예측 그래프")

fig, ax = plt.subplots(figsize=(12, 6))

# 실제 관측값
ax.scatter(
    month_df["연도"],
    month_df["평균기온(℃)"],
    color="#2980B9",
    s=65,
    label="Actual Temperature",
    zorder=3
)

# 회귀 직선
ax.plot(
    line_years,
    line_temps,
    color="#F39C12",
    linewidth=2.5,
    label="Linear Regression Line"
)

# 미래 예측값
ax.scatter(
    forecast_year,
    predicted_temp,
    color="red",
    marker="*",
    s=300,
    edgecolor="black",
    label="Predicted Temperature",
    zorder=5
)

ax.annotate(
    f"{predicted_temp:.2f}℃",
    (forecast_year, predicted_temp),
    xytext=(10, 12),
    textcoords="offset points",
    color="red",
    fontsize=12,
    fontweight="bold"
)

ax.set_title(
    f"{selected_month}월 평균기온 선형회귀 예측",
    fontsize=16
)

ax.set_xlabel("Year")
ax.set_ylabel("Average Temperature (℃)")
ax.grid(alpha=0.3, linestyle="--")
ax.legend()
ax.set_xlim(
    month_df["연도"].min() - 1,
    forecast_year + 1
)

st.pyplot(fig)
plt.close(fig)

# 그래프 해석
st.markdown("""
### 🔍 그래프 읽는 방법

- 🔵 파란색 점: CSV에 기록된 실제 평균기온
- 🟠 주황색 직선: 실제 데이터 전체를 학습하여 만든 회귀 추세선
- ⭐ 빨간색 별: 선택한 미래 연도의 예측 평균기온

주황색 직선은 과거 기온 데이터의 전체적인 변화 경향을 보여줍니다.
직선을 미래 연도까지 연장하여 새로운 연도의 기온을 예측합니다.
""")

st.divider()

# 선형회귀 설명
st.subheader("🧠 선형회귀 알고리즘 알아보기")

st.write("""
선형회귀는 입력값과 결과값 사이의 관계를 직선으로 표현하여
새로운 값을 예측하는 머신러닝 알고리즘입니다.

이 프로그램에서는 연도를 입력값(X)으로 사용하고,
평균기온을 예측값(Y)으로 사용합니다.
""")

st.latex(r"\hat{Y} = aX + b")

st.write("""
- X: 연도
- Ŷ: 예측 평균기온
- a: 직선의 기울기
- b: y절편
""")

st.markdown("### ① 과거 데이터 학습")

st.write(
    f"선택한 {selected_month}월의 모든 연도별 평균기온 "
    f"{len(month_df)}개를 가져와 학습합니다."
)

st.markdown("### ② 가장 적합한 직선 찾기")

st.write("""
선형회귀는 실제 관측값과 직선이 예측하는 값의 차이를 계산합니다.
이 차이를 제곱하여 모두 더한 값이 가장 작아지는 직선을 찾습니다.
이 방법을 최소제곱법이라고 합니다.
""")

st.markdown("### ③ 미래 기온 예측")

st.write(
    f"학습한 직선에 {int(forecast_year)}년을 대입하면 "
    f"예측 평균기온은 {predicted_temp:.2f}℃가 됩니다."
)

st.markdown("### ④ 학습 결과 해석")

st.write(
    f"회귀 직선의 기울기는 {slope:.4f}℃/년입니다. "
    f"따라서 연도가 1년 증가할 때 평균기온이 "
    f"약 {abs(slope):.4f}℃ "
    f"{'상승' if slope > 0 else '하락' if slope < 0 else '변화하지 않는'} "
    f"경향을 보입니다."
)

st.write(
    f"결정계수(R²)는 {r2:.3f}입니다. "
    "이 값은 회귀 직선이 과거 기온 데이터의 변동을 "
    "얼마나 설명하는지 나타냅니다. 1에 가까울수록 "
    "직선이 데이터를 잘 설명합니다."
)

st.info("""
⚠️ 주의사항

이 프로그램은 과거 기온의 직선적인 변화 경향이 미래에도
이어진다고 가정합니다. 실제 기온은 온실가스, 해류,
대기 순환, 강수량 등 여러 요인의 영향을 받습니다.
따라서 이 결과는 통계적인 추정값이며 실제 기온을
정확하게 보장하지는 않습니다.
""")

# 데이터 확인
with st.expander("📋 선택한 월의 전체 데이터 확인"):
    st.dataframe(
        month_df[["일시", "연도", "월", "평균기온(℃)"]],
        use_container_width=True,
        hide_index=True
    )

st.caption("Temperature Analysis | Linear Regression")
