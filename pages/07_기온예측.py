
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor


# --------------------------------------------------
# 1. 페이지 설정
# --------------------------------------------------

st.set_page_config(
    page_title="월별 평균기온 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 평균기온 예측 및 회귀 알고리즘 비교")
st.markdown(
    "과거 기온 데이터를 바탕으로 미래의 평균기온을 예측하고, "
    "세 가지 회귀 알고리즘의 결과를 비교해 보는 프로그램입니다."
)

st.divider()


# --------------------------------------------------
# 2. CSV 파일 경로 설정
# --------------------------------------------------

# 현재 파이썬 파일은 pages 폴더 안에 있음
# CSV 파일은 프로젝트 최상위 폴더에 있음

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "temperature.csv"


# --------------------------------------------------
# 3. 데이터 불러오기
# --------------------------------------------------

@st.cache_data
def load_data(file_path):

    data = pd.read_csv(file_path, encoding="utf-8-sig")

    # 필요한 열 확인
    required_columns = ["일시", "평균기온(℃)"]

    for col in required_columns:
        if col not in data.columns:
            raise ValueError(f"CSV 파일에서 '{col}' 열을 찾을 수 없습니다.")

    data = data[required_columns].copy()

    # 날짜 형식 처리: Oct-07 형태
    date_parts = data["일시"].astype(str).str.strip().str.extract(
        r"^([A-Za-z]{3})-(\d{2})$"
    )

    month_map = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
        "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
        "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
    }

    if date_parts[0].notna().all() and date_parts[1].notna().all():

        months = date_parts[0].str.title().map(month_map)
        short_years = pd.to_numeric(date_parts[1], errors="coerce")

        # 두 자리 연도 변환
        # 00~68은 2000년대, 69~99는 1900년대로 처리
        years = np.where(
            short_years <= 68,
            short_years + 2000,
            short_years + 1900
        )

        data["연도"] = years
        data["월"] = months

    else:
        # 다른 날짜 형식일 경우를 위한 보조 처리
        parsed_dates = pd.to_datetime(
            data["일시"],
            errors="coerce"
        )

        data["연도"] = parsed_dates.dt.year
        data["월"] = parsed_dates.dt.month

    data["평균기온(℃)"] = pd.to_numeric(
        data["평균기온(℃)"],
        errors="coerce"
    )

    data = data.dropna(
        subset=["연도", "월", "평균기온(℃)"]
    )

    data["연도"] = data["연도"].astype(int)
    data["월"] = data["월"].astype(int)

    data = data.sort_values(
        by=["연도", "월"]
    ).reset_index(drop=True)

    return data


try:
    df = load_data(CSV_PATH)

except FileNotFoundError:
    st.error(
        "temperature.csv 파일을 찾을 수 없습니다. "
        "CSV 파일이 프로젝트 최상위 폴더에 있는지 확인해 주세요."
    )
    st.stop()

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()


# --------------------------------------------------
# 4. 사용자 입력
# --------------------------------------------------

st.sidebar.header("⚙️ 예측 설정")

selected_month = st.sidebar.selectbox(
    "예측할 월을 선택하세요.",
    list(range(1, 13)),
    format_func=lambda x: f"{x}월"
)

month_names = {
    1: "1월", 2: "2월", 3: "3월", 4: "4월",
    5: "5월", 6: "6월", 7: "7월", 8: "8월",
    9: "9월", 10: "10월", 11: "11월", 12: "12월"
}

st.sidebar.subheader("예측 알고리즘 선택")

algorithm_names = [
    "선형회귀",
    "랜덤 포레스트 회귀",
    "그래디언트 부스팅 회귀"
]

selected_algorithm = st.sidebar.selectbox(
    "사용할 알고리즘을 선택하세요.",
    algorithm_names
)


# --------------------------------------------------
# 5. 선택한 월의 데이터 추출
# --------------------------------------------------

month_df = df[df["월"] == selected_month].copy()

month_df = month_df.sort_values("연도")

if len(month_df) < 3:
    st.warning("선택한 월의 데이터가 충분하지 않습니다.")
    st.stop()

X = month_df[["연도"]]
y = month_df["평균기온(℃)"]

last_year = int(month_df["연도"].max())
first_year = int(month_df["연도"].min())

# 기본 예측연도는 마지막 데이터 다음 해
default_year = last_year + 1

forecast_year = st.sidebar.number_input(
    "예측할 연도",
    min_value=first_year,
    max_value=2100,
    value=default_year,
    step=1
)

forecast_year = int(forecast_year)


# --------------------------------------------------
# 6. 회귀 알고리즘 3가지 생성
# --------------------------------------------------

models = {
    "선형회귀": LinearRegression(),

    "랜덤 포레스트 회귀": RandomForestRegressor(
        n_estimators=200,
        max_depth=5,
        min_samples_leaf=2,
        random_state=42
    ),

    "그래디언트 부스팅 회귀": GradientBoostingRegressor(
        n_estimators=100,
        learning_rate=0.05,
        max_depth=2,
        loss="squared_error",
        random_state=42
    )
}


# --------------------------------------------------
# 7. 모델 학습 및 예측
# --------------------------------------------------

predictions = {}
trained_models = {}
r2_scores = {}

for name, model in models.items():

    model.fit(X, y)

    predicted_value = model.predict(
        pd.DataFrame({"연도": [forecast_year]})
    )[0]

    predictions[name] = float(predicted_value)
    trained_models[name] = model

    r2_scores[name] = model.score(X, y)


# --------------------------------------------------
# 8. 선택한 알고리즘의 예측 결과
# --------------------------------------------------

selected_prediction = predictions[selected_algorithm]

st.subheader(f"📌 {forecast_year}년 {month_names[selected_month]} 평균기온 예측")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "선택한 알고리즘",
        selected_algorithm
    )

with col2:
    st.metric(
        "예측 평균기온",
        f"{selected_prediction:.2f} ℃"
    )

with col3:
    st.metric(
        "학습 데이터 개수",
        f"{len(month_df):,}개"
    )


# --------------------------------------------------
# 9. 세 가지 알고리즘 예측 결과 비교
# --------------------------------------------------

st.subheader("📊 알고리즘별 예측 결과 비교")

comparison_df = pd.DataFrame({
    "알고리즘": list(predictions.keys()),
    "예측 평균기온(℃)": [
        round(value, 2)
        for value in predictions.values()
    ],
    "학습 데이터 R²": [
        round(value, 4)
        for value in r2_scores.values()
    ]
})

st.dataframe(
    comparison_df,
    use_container_width=True,
    hide_index=True
)


# --------------------------------------------------
# 10. 실제 기온과 세 가지 예측 그래프
# --------------------------------------------------

st.subheader("📈 과거 기온 및 알고리즘별 예측 그래프")

fig, ax = plt.subplots(figsize=(13, 6))

# 실제 기온 데이터
ax.scatter(
    month_df["연도"],
    month_df["평균기온(℃)"],
    color="black",
    label="실제 평균기온",
    s=35,
    zorder=5
)

# 예측선을 그릴 연도 범위
plot_years = np.arange(
    first_year,
    forecast_year + 1
)

plot_X = pd.DataFrame({
    "연도": plot_years
})

line_colors = {
    "선형회귀": "red",
    "랜덤 포레스트 회귀": "blue",
    "그래디언트 부스팅 회귀": "green"
}

for name, model in trained_models.items():

    line_predictions = model.predict(plot_X)

    # 선택한 알고리즘은 더 굵게 표시
    line_width = 3 if name == selected_algorithm else 1.8

    ax.plot(
        plot_years,
        line_predictions,
        color=line_colors[name],
        linewidth=line_width,
        label=f"{name} 예측"
    )

    # 미래 예측 지점 표시
    ax.scatter(
        forecast_year,
        predictions[name],
        color=line_colors[name],
        s=100,
        edgecolors="white",
        linewidths=1.5,
        zorder=6
    )

# 실제 데이터 마지막 연도 표시
ax.axvline(
    last_year,
    color="gray",
    linestyle="--",
    alpha=0.7,
    label="과거 데이터 마지막 연도"
)

ax.set_title(
    f"{month_names[selected_month]} 평균기온 회귀 예측 비교",
    fontsize=15
)

ax.set_xlabel("연도")
ax.set_ylabel("평균기온(℃)")

ax.grid(
    True,
    alpha=0.3
)

ax.legend()
fig.tight_layout()

st.pyplot(fig)


# --------------------------------------------------
# 11. 알고리즘별 설명
# --------------------------------------------------

st.divider()

st.subheader("🧠 회귀 알고리즘 원리 알아보기")

if selected_algorithm == "선형회귀":

    st.markdown("""
    ### 🔴 선형회귀 (Linear Regression)

    선형회귀는 과거의 연도와 평균기온 사이의 관계를
    직선으로 나타내는 알고리즘입니다.

    - 과거 데이터의 전체적인 증가 또는 감소 경향을 분석합니다.
    - 데이터에 가장 잘 맞는 직선을 찾아 예측합니다.
    - 연도가 증가할 때 기온이 얼마나 변하는지 기울기를 통해 확인할 수 있습니다.

    **그래프에서 확인할 점**

    빨간색 직선이 실제 기온 데이터의 전체적인 흐름을
    얼마나 잘 나타내는지 살펴보세요.
    """)

elif selected_algorithm == "랜덤 포레스트 회귀":

    st.markdown("""
    ### 🔵 랜덤 포레스트 회귀 (Random Forest Regression)

    랜덤 포레스트는 여러 개의 의사결정나무를 만들고,
    각 나무의 예측 결과를 평균 내는 알고리즘입니다.

    - 여러 개의 의사결정나무를 학습합니다.
    - 각 나무가 서로 다른 방식으로 데이터를 분석합니다.
    - 여러 나무의 예측값을 평균 내어 최종 결과를 만듭니다.

    **그래프에서 확인할 점**

    파란색 선이 어떻게 변화하는지 확인해 보세요.
    선형회귀와 달리 구간별로 값이 일정하게 유지되거나
    계단 형태로 나타날 수 있습니다.
    """)

elif selected_algorithm == "그래디언트 부스팅 회귀":

    st.markdown("""
    ### 🟢 그래디언트 부스팅 회귀 (Gradient Boosting Regression)

    그래디언트 부스팅은 여러 개의 약한 예측 모델을
    순서대로 학습시키며 예측 성능을 개선하는 알고리즘입니다.

    - 첫 번째 모델이 데이터를 예측합니다.
    - 다음 모델은 이전 모델이 틀린 부분을 보완합니다.
    - 이러한 과정을 반복하여 최종 예측값을 만듭니다.

    **그래프에서 확인할 점**

    초록색 선의 변화 형태를 확인해 보세요.
    이전 모델의 오차를 보완하면서 예측을 개선하는 방식입니다.
    """)


# --------------------------------------------------
# 12. 세 알고리즘의 차이점
# --------------------------------------------------

st.subheader("🔍 세 가지 알고리즘 비교")

st.markdown("""
| 알고리즘 | 예측 방식 | 특징 |
|---|---|---|
| 선형회귀 | 직선의 관계 분석 | 전체적인 증가·감소 경향 파악 |
| 랜덤 포레스트 | 여러 의사결정나무의 평균 | 다양한 데이터 패턴 학습 |
| 그래디언트 부스팅 | 이전 모델의 오차를 순차적으로 보완 | 예측 오차를 줄이는 방식 |

세 알고리즘은 데이터를 학습하는 방법이 다르기 때문에
같은 기온 데이터를 사용하더라도 예측 결과가 달라질 수 있습니다.

특히 랜덤 포레스트와 그래디언트 부스팅 같은 트리 기반 모델은
학습한 연도 범위 밖의 미래를 예측할 때 새로운 추세를
직선처럼 계속 연장하지 못하고 마지막 구간의 예측값을
유지하는 형태가 나타날 수 있습니다.
따라서 미래 예측에서는 알고리즘의 특성을 함께 고려해야 합니다.
""")

st.caption(
    "※ R²는 학습에 사용한 데이터에 대한 결정계수입니다. "
    "미래 예측의 정확도를 직접 보장하는 값은 아닙니다."
)

st.divider()

st.success(
    f"{selected_algorithm}을 사용한 "
    f"{forecast_year}년 {month_names[selected_month]} "
    f"평균기온 예측이 완료되었습니다."
)
