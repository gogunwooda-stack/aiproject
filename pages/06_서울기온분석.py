
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from io import BytesIO
from pathlib import Path

st.set_page_config(page_title="월별 기온 분석", page_icon="🌡️", layout="wide")

st.title("🌡️ 월별 기온 분석")
st.write("월을 선택하면 해당 월의 연도별 최고기온과 최저기온을 비교합니다.")

# 한글 폰트 설정
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

# CSV 파일 업로드
uploaded_file = st.file_uploader("기온 CSV 파일 업로드", type=["csv"])

def read_csv(file):
    for encoding in ["euc-kr", "cp949", "utf-8-sig", "utf-8"]:
        try:
            if file is not None:
                return pd.read_csv(BytesIO(file.getvalue()), encoding=encoding)
            return pd.read_csv("temperature(2).csv", encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError("CSV 인코딩을 확인해 주세요.")

if uploaded_file is not None:
    df = read_csv(uploaded_file)
else:
    try:
        df = read_csv(None)
    except FileNotFoundError:
        st.info("CSV 파일을 업로드해 주세요.")
        st.stop()

# 날짜 변환
dates = []
previous = None

for value in df["일시"]:
    month, year = value.split("-")
    month_num = datetime.strptime(month, "%b").month
    short_year = int(year)

    candidates = [1900 + short_year, 2000 + short_year]
    valid = [
        y for y in candidates
        if previous is None or
        datetime(y, month_num, 1) >= previous
    ]

    selected_year = min(valid)
    current = datetime(selected_year, month_num, 1)

    dates.append(current)
    previous = current

df["날짜"] = pd.to_datetime(dates)
df["연도"] = df["날짜"].dt.year
df["월"] = df["날짜"].dt.month

df["최고기온(℃)"] = pd.to_numeric(df["최고기온(℃)"], errors="coerce")
df["최저기온(℃)"] = pd.to_numeric(df["최저기온(℃)"], errors="coerce")

# 월 선택
month = st.selectbox(
    "📅 분석할 월을 선택하세요",
    range(1, 13),
    format_func=lambda x: f"{x}월"
)

# 선택한 월 데이터
selected = df[df["월"] == month].dropna(
    subset=["최고기온(℃)", "최저기온(℃)"]
).sort_values("연도")

if selected.empty:
    st.warning("해당 월의 데이터가 없습니다.")
    st.stop()

# 그래프
fig, ax = plt.subplots(figsize=(13, 6))

ax.plot(
    selected["연도"],
    selected["최고기온(℃)"],
    color="hotpink",
    marker="o",
    label="최고기온",
    linewidth=2
)

ax.plot(
    selected["연도"],
    selected["최저기온(℃)"],
    color="skyblue",
    marker="o",
    label="최저기온",
    linewidth=2
)

ax.set_title("월별 기온 분석", fontsize=20)
ax.set_xlabel("연도", fontsize=13)
ax.set_ylabel("온도 (℃)", fontsize=13)

ax.legend()
ax.grid(alpha=0.3)

plt.tight_layout()
st.pyplot(fig)
plt.close(fig)

# 데이터 확인
with st.expander("📊 분석 데이터 확인"):
    st.dataframe(
        selected[["연도", "최고기온(℃)", "최저기온(℃)"]],
        use_container_width=True,
        hide_index=True
    )
