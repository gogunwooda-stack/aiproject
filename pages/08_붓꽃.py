
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from pathlib import Path
from collections import Counter
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier


# ==========================================
# 1. 페이지 설정
# ==========================================

st.set_page_config(
    page_title="붓꽃 품종 예측 AI",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 붓꽃 품종 예측 AI")
st.write(
    "꽃잎의 길이와 너비를 입력하면 "
    "머신러닝이 붓꽃의 품종을 예측합니다."
)

st.divider()


# ==========================================
# 2. CSV 파일 불러오기
# ==========================================

@st.cache_data
def load_data():

    base_dir = Path(__file__).resolve().parent

    file_candidates = [
        base_dir / "iris.csv",
        base_dir.parent / "iris.csv"
    ]

    file_path = next(
        (p for p in file_candidates if p.exists()),
        None
    )

    if file_path is None:
        raise FileNotFoundError(
            "iris.csv 파일을 찾을 수 없습니다."
        )

    encodings = ["cp949", "utf-8-sig", "euc-kr", "latin1"]

    for encoding in encodings:
        try:
            raw = pd.read_csv(
                file_path,
                encoding=encoding
            )

            # 기존 CSV의 열 순서:
            # 0: 꽃받침 길이
            # 1: 꽃받침 너비
            # 2: 꽃잎 길이
            # 3: 꽃잎 너비
            # 4: 꽃 품종

            if raw.shape[1] < 5:
                continue

            data = raw.iloc[:, [2, 3, 4]].copy()

            data.columns = [
                "꽃잎 길이",
                "꽃잎 너비",
                "품종"
            ]

            data["꽃잎 길이"] = pd.to_numeric(
                data["꽃잎 길이"],
                errors="coerce"
            )

            data["꽃잎 너비"] = pd.to_numeric(
                data["꽃잎 너비"],
                errors="coerce"
            )

            data["품종"] = (
                data["품종"]
                .astype(str)
                .str.strip()
                .str.replace("Iris-", "", regex=False)
                .str.lower()
            )

            data["품종"] = data["품종"].map({
                "setosa": "Setosa",
                "versicolor": "Versicolor",
                "virginica": "Virginica"
            })

            data = data.dropna().reset_index(drop=True)

            if len(data) > 0:
                return data

        except Exception:
            continue

    raise ValueError(
        "CSV 데이터를 읽지 못했습니다. 파일의 열 구성을 확인해 주세요."
    )


try:
    df = load_data()

except Exception as e:
    st.error(f"데이터 불러오기 오류: {e}")
    st.stop()


# ==========================================
# 3. 데이터 확인 및 입력 범위 설정
# ==========================================

length_min = float(df["꽃잎 길이"].min())
length_max = float(df["꽃잎 길이"].max())

width_min = float(df["꽃잎 너비"].min())
width_max = float(df["꽃잎 너비"].max())

st.subheader("📊 학습 데이터 정보")

col1, col2, col3 = st.columns(3)

col1.metric("전체 데이터", f"{len(df)}개")
col2.metric("붓꽃 품종", f"{df['품종'].nunique()}종")
col3.metric("사용 데이터", "꽃잎 길이 + 너비")

st.info(
    f"""
    **입력 가능한 범위**

    - 🌷 꽃잎 길이: {length_min:.1f} ~ {length_max:.1f} cm
    - 🌷 꽃잎 너비: {width_min:.1f} ~ {width_max:.1f} cm

    입력 범위는 CSV에 저장된 실제 데이터의
    최솟값과 최댓값을 기준으로 합니다.
    """
)


# ==========================================
# 4. KNN 머신러닝 모델 생성
# ==========================================

X = df[["꽃잎 길이", "꽃잎 너비"]]
y = df["품종"]

# 데이터 표준화 + KNN 분류
model = Pipeline([
    ("scaler", StandardScaler()),
    ("knn", KNeighborsClassifier(n_neighbors=5))
])

model.fit(X, y)


# ==========================================
# 5. 사용자 입력
# ==========================================

st.divider()
st.subheader("✏️ 붓꽃 크기 입력하기")

with st.form("prediction_form"):

    col1, col2 = st.columns(2)

    with col1:
        petal_length = st.number_input(
            "꽃잎 길이 (cm)",
            min_value=length_min,
            max_value=length_max,
            value=round((length_min + length_max) / 2, 1),
            step=0.1
        )

    with col2:
        petal_width = st.number_input(
            "꽃잎 너비 (cm)",
            min_value=width_min,
            max_value=width_max,
            value=round((width_min + width_max) / 2, 1),
            step=0.1
        )

    submitted = st.form_submit_button(
        "🔍 붓꽃 품종 예측하기",
        use_container_width=True
    )


# ==========================================
# 6. 품종 예측 및 결과 출력
# ==========================================

if submitted:

    new_data = pd.DataFrame({
        "꽃잎 길이": [petal_length],
        "꽃잎 너비": [petal_width]
    })

    prediction = model.predict(new_data)[0]

    probabilities = model.predict_proba(new_data)[0]

    class_names = model.classes_

    species_names = {
        "Setosa": "아이리스 세토사",
        "Versicolor": "아이리스 버시컬러",
        "Virginica": "아이리스 버지니카"
    }

    st.divider()

    st.subheader("🎯 AI 예측 결과")

    st.success(
        f"예측된 붓꽃 품종: {species_names[prediction]}"
    )

    st.markdown(
        f"### 🌸 {prediction}"
    )

    result_col1, result_col2 = st.columns(2)

    result_col1.metric(
        "입력한 꽃잎 길이",
        f"{petal_length:.1f} cm"
    )

    result_col2.metric(
        "입력한 꽃잎 너비",
        f"{petal_width:.1f} cm"
    )

    # ======================================
    # 7. 가장 가까운 이웃 5개 찾기
    # ======================================

    scaler = model.named_steps["scaler"]
    knn = model.named_steps["knn"]

    scaled_input = scaler.transform(new_data)

    distances, indices = knn.kneighbors(
        scaled_input
    )

    neighbor_data = df.iloc[indices[0]].copy()

    neighbor_data["거리"] = distances[0]

    vote_counts = Counter(neighbor_data["품종"])

    st.subheader("🧠 AI가 이렇게 판단했어요!")

    st.write(
        "KNN 알고리즘은 입력한 데이터와 가장 가까운 "
        "5개의 데이터를 찾아 품종을 비교합니다."
    )

    vote_cols = st.columns(3)

    for i, species in enumerate(class_names):

        vote_cols[i].metric(
            species_names[species],
            f"{vote_counts.get(species, 0)}표"
        )

    st.write("**가장 가까운 이웃 5개 데이터**")

    display_neighbors = neighbor_data.copy()

    display_neighbors["품종"] = (
        display_neighbors["품종"].map(species_names)
    )

    display_neighbors.index = range(1, 6)

    st.dataframe(
        display_neighbors.round(3),
        use_container_width=True
    )

    st.caption(
        "거리는 표준화된 꽃잎 길이와 너비를 이용해 계산한 값입니다."
    )

    # ======================================
    # 8. 품종별 분류 확률
    # ======================================

    st.subheader("📈 품종별 예측 확률")

    probability_df = pd.DataFrame({
        "품종": [
            species_names[name] for name in class_names
        ],
        "예측 확률": probabilities * 100
    })

    probability_df = probability_df.sort_values(
        "예측 확률",
        ascending=True
    )

    fig_prob = go.Figure(
        go.Bar(
            x=probability_df["예측 확률"],
            y=probability_df["품종"],
            orientation="h",
            text=[
                f"{v:.1f}%"
                for v in probability_df["예측 확률"]
            ],
            textposition="auto",
            marker_color="#6C9CEB"
        )
    )

    fig_prob.update_layout(
        xaxis_title="예측 확률 (%)",
        yaxis_title="붓꽃 품종",
        xaxis=dict(range=[0, 100]),
        height=300
    )

    st.plotly_chart(
        fig_prob,
        use_container_width=True
    )

    st.caption(
        "예측 확률은 KNN의 최근접 이웃 5개 중 "
        "각 품종이 차지하는 비율입니다."
    )

    # ======================================
    # 9. 분류 영역 시각화
    # ======================================

    st.divider()
    st.subheader("🗺️ 붓꽃 품종 분포 및 예측 위치")

    st.write(
        """
        - 배경색: AI가 해당 위치에서 예측하는 품종 영역
        - 원형 점: 기존 학습 데이터
        - 검은색 테두리 원: 입력값과 가장 가까운 5개 데이터
        - 초록색 별: 사용자가 입력한 데이터
        """
    )

    # 그래프 범위 설정
    x_margin = (length_max - length_min) * 0.12
    y_margin = (width_max - width_min) * 0.12

    x_range = np.linspace(
        length_min - x_margin,
        length_max + x_margin,
        130
    )

    y_range = np.linspace(
        width_min - y_margin,
        width_max + y_margin,
        130
    )

    xx, yy = np.meshgrid(x_range, y_range)

    grid_data = pd.DataFrame({
        "꽃잎 길이": xx.ravel(),
        "꽃잎 너비": yy.ravel()
    })

    grid_predictions = model.predict(grid_data)

    class_to_number = {
        name: i for i, name in enumerate(class_names)
    }

    zz = np.array([
        class_to_number[name]
        for name in grid_predictions
    ]).reshape(xx.shape)

    # 품종별 색상
    colors = {
        "Setosa": "#F5A623",
        "Versicolor": "#4389DB",
        "Virginica": "#B06ACB"
    }

    fig = go.Figure()

    # AI 분류 영역
    colorscale = []

    for i, name in enumerate(class_names):
        start = i / len(class_names)
        end = (i + 1) / len(class_names)

        colorscale.append([
            start,
            colors[name]
        ])

        colorscale.append([
            end,
            colors[name]
        ])

    fig.add_trace(
        go.Contour(
            x=x_range,
            y=y_range,
            z=zz,
            colorscale=colorscale,
            contours=dict(
                start=-0.5,
                end=len(class_names) - 0.5,
                size=1,
                coloring="fill",
                showlines=False
            ),
            showscale=False,
            opacity=0.22,
            hoverinfo="skip",
            name="AI 분류 영역"
        )
    )

    # 기존 데이터 표시
    for species in class_names:

        subset = df[df["품종"] == species]

        fig.add_trace(
            go.Scatter(
                x=subset["꽃잎 길이"],
                y=subset["꽃잎 너비"],
                mode="markers",
                name=species_names[species],
                marker=dict(
                    color=colors[species],
                    size=8,
                    opacity=0.8
                )
            )
        )

    # 가장 가까운 이웃 5개 표시
    fig.add_trace(
        go.Scatter(
            x=neighbor_data["꽃잎 길이"],
            y=neighbor_data["꽃잎 너비"],
            mode="markers",
            name="가장 가까운 이웃 5개",
            marker=dict(
                symbol="circle-open",
                size=19,
                color="black",
                line=dict(width=2)
            )
        )
    )

    # 사용자 입력값 표시: 초록색 별
    fig.add_trace(
        go.Scatter(
            x=[petal_length],
            y=[petal_width],
            mode="markers+text",
            name="내가 입력한 데이터",
            text=["내 입력값 ★"],
            textposition="top center",
            marker=dict(
                symbol="star",
                size=24,
                color="#00C853",
                line=dict(
                    color="black",
                    width=1.5
                )
            )
        )
    )

    fig.update_layout(
        title="KNN 붓꽃 품종 분류 지도",
        xaxis_title="꽃잎 길이 (cm)",
        yaxis_title="꽃잎 너비 (cm)",
        height=650,
        hovermode="closest",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0
        )
    )

    fig.update_xaxes(
        range=[
            length_min - x_margin,
            length_max + x_margin
        ]
    )

    fig.update_yaxes(
        range=[
            width_min - y_margin,
            width_max + y_margin
        ]
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ======================================
    # 10. 최종 분석 설명
    # ======================================

    st.subheader("🔎 최종 분석")

    st.write(
        f"""
        입력한 꽃잎 길이는 **{petal_length:.1f}cm**,
        꽃잎 너비는 **{petal_width:.1f}cm**입니다.

        AI는 이 입력값과 가장 가까운 5개의 데이터를 비교했습니다.

        그 결과 **{species_names[prediction]}({prediction})**
        품종이 가장 많이 나타나 해당 품종으로 분류했습니다.

        그래프에서 초록색 별의 위치와 주변 데이터,
        그리고 배경색으로 표시된 분류 영역을 확인해 보세요.
        """
    )

else:

    st.info(
        "꽃잎 길이와 너비를 입력하고 "
        "'붓꽃 품종 예측하기' 버튼을 눌러 주세요."
    )

st.divider()

st.caption(
    "🌸 Iris Classification AI | "
    "Pandas + Scikit-learn + KNN + Plotly"
)

