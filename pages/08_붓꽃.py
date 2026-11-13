
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from pathlib import Path
from collections import Counter

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score


# ==========================================
# 1. 페이지 설정
# ==========================================

st.set_page_config(
    page_title="붓꽃 품종 예측 AI",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 붓꽃 품종 예측 AI")
st.markdown(
    "꽃잎의 길이와 너비를 입력하면 "
    "**3가지 머신러닝 알고리즘**이 붓꽃 품종을 예측합니다."
)

st.divider()


# ==========================================
# 2. CSV 데이터 불러오기
# ==========================================

@st.cache_data
def load_data():

    base_dir = Path(__file__).resolve().parent

    candidates = [
        base_dir / "iris.csv",
        base_dir.parent / "iris.csv"
    ]

    file_path = next(
        (p for p in candidates if p.exists()),
        None
    )

    if file_path is None:
        raise FileNotFoundError(
            "iris.csv 파일을 찾을 수 없습니다. "
            "프로젝트 최상위 폴더에 CSV 파일을 넣어 주세요."
        )

    encodings = [
        "cp949",
        "euc-kr",
        "utf-8-sig",
        "utf-8"
    ]

    raw = None

    for encoding in encodings:
        try:
            raw = pd.read_csv(
                file_path,
                encoding=encoding
            )
            break
        except UnicodeDecodeError:
            continue

    if raw is None:
        raise ValueError("CSV 인코딩을 확인해 주세요.")

    # 열 이름의 앞뒤 공백 제거
    raw.columns = raw.columns.astype(str).str.strip()

    required = [
        "꽃잎 길이",
        "꽃잎 너비",
        "꽃 품종"
    ]

    if not all(col in raw.columns for col in required):
        raise ValueError(
            "CSV에 꽃잎 길이, 꽃잎 너비, 꽃 품종 열이 필요합니다."
        )

    data = raw[required].copy()

    data.columns = [
        "꽃잎 길이",
        "꽃잎 너비",
        "품종"
    ]

    # 숫자형으로 변환
    data["꽃잎 길이"] = pd.to_numeric(
        data["꽃잎 길이"],
        errors="coerce"
    )

    data["꽃잎 너비"] = pd.to_numeric(
        data["꽃잎 너비"],
        errors="coerce"
    )

    # 품종 이름 정리
    data["품종"] = (
        data["품종"]
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace("iris-", "", regex=False)
    )

    data["품종"] = data["품종"].map({
        "setosa": "Setosa",
        "versicolor": "Versicolor",
        "virginica": "Virginica"
    })

    data = data.dropna().reset_index(drop=True)

    if len(data) == 0:
        raise ValueError("분석할 수 있는 데이터가 없습니다.")

    if data["품종"].nunique() != 3:
        raise ValueError("붓꽃 3개 품종의 데이터가 필요합니다.")

    return data


try:
    df = load_data()

except Exception as e:
    st.error(f"데이터 불러오기 오류: {e}")
    st.stop()


# ==========================================
# 3. 데이터 기본 정보
# ==========================================

X = df[["꽃잎 길이", "꽃잎 너비"]]
y = df["품종"]

species_names = {
    "Setosa": "아이리스 세토사",
    "Versicolor": "아이리스 버시컬러",
    "Virginica": "아이리스 버지니카"
}

colors = {
    "Setosa": "#F5A623",
    "Versicolor": "#4389DB",
    "Virginica": "#B06ACB"
}

class_names = sorted(y.unique())

length_min = float(X["꽃잎 길이"].min())
length_max = float(X["꽃잎 길이"].max())

width_min = float(X["꽃잎 너비"].min())
width_max = float(X["꽃잎 너비"].max())

st.subheader("📊 학습 데이터 정보")

c1, c2, c3 = st.columns(3)

c1.metric("전체 데이터", f"{len(df)}개")
c2.metric("붓꽃 품종", f"{len(class_names)}종")
c3.metric("분석 변수", "2개")

st.info(
    f"""
    **입력 가능한 범위**

    - 🌷 꽃잎 길이: {length_min:.1f} ~ {length_max:.1f} cm
    - 🌷 꽃잎 너비: {width_min:.1f} ~ {width_max:.1f} cm

    위 범위는 CSV에 저장된 실제 데이터의 최솟값과 최댓값입니다.
    """
)


# ==========================================
# 4. 학습용 / 테스트용 데이터 분리
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    random_state=42,
    stratify=y
)


# ==========================================
# 5. 머신러닝 알고리즘 3개 생성
# ==========================================

models = {
    "KNN": Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", KNeighborsClassifier(n_neighbors=5))
    ]),

    "Decision Tree": DecisionTreeClassifier(
        max_depth=4,
        random_state=42
    ),

    "Random Forest": RandomForestClassifier(
        n_estimators=200,
        random_state=42
    )
}

algorithm_descriptions = {
    "KNN": "가장 가까운 데이터 5개의 품종을 비교하여 다수결로 결정합니다.",
    "Decision Tree": "꽃잎의 길이와 너비를 기준으로 질문을 반복하여 품종을 결정합니다.",
    "Random Forest": "여러 의사결정나무의 예측 결과를 종합하여 품종을 결정합니다."
}


# ==========================================
# 6. 정확도 평가 및 전체 데이터 재학습
# ==========================================

accuracies = {}

for name, model in models.items():

    # 학습용 데이터로 학습
    model.fit(X_train, y_train)

    # 테스트 데이터 예측
    test_prediction = model.predict(X_test)

    # 정확도 계산
    accuracies[name] = accuracy_score(
        y_test,
        test_prediction
    )

    # 최종 예측을 위해 전체 데이터로 재학습
    model.fit(X, y)


# ==========================================
# 7. 정확도 비교
# ==========================================

st.divider()
st.subheader("🏆 알고리즘 정확도 비교")

st.write(
    "전체 데이터 중 75%를 학습에, 25%를 테스트에 사용했습니다. "
    "세 알고리즘 모두 동일한 테스트 데이터를 기준으로 평가합니다."
)

accuracy_df = pd.DataFrame({
    "알고리즘": list(accuracies.keys()),
    "정확도": [
        value * 100 for value in accuracies.values()
    ]
}).sort_values(
    "정확도",
    ascending=False
)

best_algorithm = accuracy_df.iloc[0]["알고리즘"]
best_accuracy = accuracy_df.iloc[0]["정확도"]

a1, a2, a3 = st.columns(3)

for col, name in zip(
    [a1, a2, a3],
    ["KNN", "Decision Tree", "Random Forest"]
):
    col.metric(
        name,
        f"{accuracies[name] * 100:.1f}%"
    )

fig_accuracy = go.Figure(
    go.Bar(
        x=accuracy_df["알고리즘"],
        y=accuracy_df["정확도"],
        text=[
            f"{v:.1f}%"
            for v in accuracy_df["정확도"]
        ],
        textposition="outside",
        marker_color=[
            "#16A36A" if name == best_algorithm else "#6C9CEB"
            for name in accuracy_df["알고리즘"]
        ]
    )
)

fig_accuracy.update_layout(
    title="머신러닝 알고리즘별 정확도",
    xaxis_title="분류 알고리즘",
    yaxis_title="정확도 (%)",
    yaxis=dict(range=[0, 110]),
    height=400
)

st.plotly_chart(
    fig_accuracy,
    use_container_width=True
)

st.success(
    f"현재 테스트 데이터에서 가장 높은 정확도를 보인 알고리즘은 "
    f"{best_algorithm}입니다. 정확도는 {best_accuracy:.1f}%입니다."
)


# ==========================================
# 8. 사용자 입력
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
        "🔍 세 가지 AI로 품종 예측하기",
        use_container_width=True
    )


# ==========================================
# 9. 예측 결과
# ==========================================

if submitted:

    new_data = pd.DataFrame({
        "꽃잎 길이": [petal_length],
        "꽃잎 너비": [petal_width]
    })

    predictions = {}
    probabilities = {}

    for name, model in models.items():

        predictions[name] = model.predict(new_data)[0]

        probabilities[name] = model.predict_proba(
            new_data
        )[0]

    st.divider()
    st.subheader("🎯 알고리즘별 예측 결과")

    result_cols = st.columns(3)

    for col, name in zip(
        result_cols,
        ["KNN", "Decision Tree", "Random Forest"]
    ):

        result = predictions[name]

        col.markdown(f"### {name}")

        col.success(
            f"🌸 {species_names[result]}"
        )

        col.caption(
            algorithm_descriptions[name]
        )

    # ======================================
    # 10. 세 알고리즘의 의견 비교
    # ======================================

    st.subheader("🤖 AI들의 최종 의견")

    vote_counts = Counter(predictions.values())

    final_species = vote_counts.most_common(1)[0][0]

    if len(vote_counts) == 1:

        st.success(
            f"세 알고리즘 모두 {species_names[final_species]}로 예측했습니다!"
        )

    else:

        st.warning(
            f"알고리즘별 예측이 다릅니다. "
            f"가장 많은 표를 얻은 품종은 {species_names[final_species]}입니다."
        )

    vote_df = pd.DataFrame({
        "품종": [
            species_names[name] for name in class_names
        ],
        "예측한 알고리즘 수": [
            vote_counts.get(name, 0) for name in class_names
        ]
    })

    fig_vote = go.Figure(
        go.Bar(
            x=vote_df["품종"],
            y=vote_df["예측한 알고리즘 수"],
            text=vote_df["예측한 알고리즘 수"],
            textposition="outside",
            marker_color=[
                colors[name] for name in class_names
            ]
        )
    )

    fig_vote.update_layout(
        title="품종별 알고리즘 투표 결과",
        yaxis_title="알고리즘 개수",
        yaxis=dict(
            range=[0, 3.8],
            dtick=1
        ),
        height=350
    )

    st.plotly_chart(
        fig_vote,
        use_container_width=True
    )

    # ======================================
    # 11. 알고리즘별 예측 확률
    # ======================================

    st.subheader("📈 알고리즘별 품종 예측 확률")

    prob_rows = []

    for name in models:

        for species, prob in zip(
            models[name].classes_,
            probabilities[name]
        ):

            prob_rows.append({
                "알고리즘": name,
                "품종": species_names[species],
                "확률": prob * 100
            })

    prob_df = pd.DataFrame(prob_rows)

    fig_prob = go.Figure()

    for name in models:

        subset = prob_df[
            prob_df["알고리즘"] == name
        ]

        fig_prob.add_trace(
            go.Bar(
                x=subset["품종"],
                y=subset["확률"],
                name=name,
                text=[
                    f"{v:.1f}%"
                    for v in subset["확률"]
                ],
                textposition="auto"
            )
        )

    fig_prob.update_layout(
        title="세 알고리즘의 예측 확률 비교",
        xaxis_title="붓꽃 품종",
        yaxis_title="예측 확률 (%)",
        barmode="group",
        yaxis=dict(range=[0, 110]),
        height=450
    )

    st.plotly_chart(
        fig_prob,
        use_container_width=True
    )

    st.caption(
        "KNN은 최근접 이웃의 비율, 의사결정나무와 랜덤 포레스트는 "
        "각 모델의 트리 기반 확률을 표시합니다. "
        "서로 다른 알고리즘의 확률값은 직접적인 신뢰도 비교와 같지는 않습니다."
    )

    # ======================================
    # 12. 분류 영역 시각화 함수
    # ======================================

    def make_classification_chart(
        model,
        title,
        input_length,
        input_width,
        show_neighbors=False
    ):

        x_margin = (length_max - length_min) * 0.12
        y_margin = (width_max - width_min) * 0.12

        x_range = np.linspace(
            length_min - x_margin,
            length_max + x_margin,
            100
        )

        y_range = np.linspace(
            width_min - y_margin,
            width_max + y_margin,
            100
        )

        xx, yy = np.meshgrid(x_range, y_range)

        grid = pd.DataFrame({
            "꽃잎 길이": xx.ravel(),
            "꽃잎 너비": yy.ravel()
        })

        predicted_grid = model.predict(grid)

        class_to_number = {
            species: i
            for i, species in enumerate(class_names)
        }

        zz = np.array([
            class_to_number[value]
            for value in predicted_grid
        ]).reshape(xx.shape)

        fig = go.Figure()

        # AI가 판단한 품종별 영역
        color_scale = []

        for i, species in enumerate(class_names):

            start = i / len(class_names)
            end = (i + 1) / len(class_names)

            color_scale.append([
                start,
                colors[species]
            ])

            color_scale.append([
                end,
                colors[species]
            ])

        fig.add_trace(
            go.Heatmap(
                x=x_range,
                y=y_range,
                z=zz,
                colorscale=color_scale,
                zmin=-0.5,
                zmax=len(class_names) - 0.5,
                showscale=False,
                opacity=0.23,
                hoverinfo="skip",
                name="분류 영역"
            )
        )

        # 기존 학습 데이터
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
                        size=7,
                        opacity=0.8
                    )
                )
            )

        # KNN의 가장 가까운 이웃 5개
        if show_neighbors:

            knn_model = models["KNN"]
            scaler = knn_model.named_steps["scaler"]
            knn = knn_model.named_steps["classifier"]

            user_df = pd.DataFrame({
                "꽃잎 길이": [input_length],
                "꽃잎 너비": [input_width]
            })

            distances, indices = knn.kneighbors(
                scaler.transform(user_df)
            )

            neighbors = df.iloc[indices[0]]

            fig.add_trace(
                go.Scatter(
                    x=neighbors["꽃잎 길이"],
                    y=neighbors["꽃잎 너비"],
                    mode="markers",
                    name="KNN 최근접 이웃 5개",
                    marker=dict(
                        symbol="circle-open",
                        size=17,
                        color="black",
                        line=dict(width=2)
                    )
                )
            )

        # 사용자 입력값: 초록색 별
        fig.add_trace(
            go.Scatter(
                x=[input_length],
                y=[input_width],
                mode="markers+text",
                name="내 입력값 ★",
                text=["내 입력값 ★"],
                textposition="top center",
                marker=dict(
                    symbol="star",
                    size=23,
                    color="#00C853",
                    line=dict(
                        color="black",
                        width=1.5
                    )
                )
            )
        )

        fig.update_layout(
            title=title,
            xaxis_title="꽃잎 길이 (cm)",
            yaxis_title="꽃잎 너비 (cm)",
            height=480,
            hovermode="closest",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="left",
                x=0
            ),
            margin=dict(
                l=30,
                r=20,
                t=80,
                b=40
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

        return fig


    # ======================================
    # 13. 세 알고리즘 분류 영역 비교
    # ======================================

    st.divider()
    st.subheader("🗺️ AI별 붓꽃 품종 분류 지도")

    st.write(
        """
        그래프의 배경색은 각 알고리즘이 해당 위치에서
        어떤 품종으로 판단하는지 보여 줍니다.

        초록색 별은 사용자가 입력한 위치입니다.
        """
    )

    chart_tabs = st.tabs([
        "KNN",
        "Decision Tree",
        "Random Forest"
    ])

    chart_configs = [
        ("KNN", True),
        ("Decision Tree", False),
        ("Random Forest", False)
    ]

    for tab, (name, show_neighbors) in zip(
        chart_tabs,
        chart_configs
    ):

        with tab:

            fig = make_classification_chart(
                models[name],
                f"{name} 품종 분류 영역",
                petal_length,
                petal_width,
                show_neighbors
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            st.info(
                f"이 알고리즘의 예측 결과: "
                f"**{species_names[predictions[name]]}**"
            )

    # ======================================
    # 14. 의사결정나무의 판단 과정
    # ======================================

    st.divider()
    st.subheader("🌳 의사결정나무의 판단 기준")

    tree = models["Decision Tree"]

    tree_structure = tree.tree_

    feature_names = [
        "꽃잎 길이",
        "꽃잎 너비"
    ]

    node = 0
    rule_number = 1
    rules = []

    while tree_structure.children_left[node] != tree_structure.children_right[node]:

        feature_index = tree_structure.feature[node]
        threshold = tree_structure.threshold[node]

        feature_name = feature_names[feature_index]
        value = new_data.iloc[0, feature_index]

        if value <= threshold:

            rules.append(
                f"{rule_number}. {feature_name} "
                f"{threshold:.2f} 이하인가? → 예"
            )

            node = tree_structure.children_left[node]

        else:

            rules.append(
                f"{rule_number}. {feature_name} "
                f"{threshold:.2f} 이하인가? → 아니요"
            )

            node = tree_structure.children_right[node]

        rule_number += 1

    st.write("입력한 값이 의사결정나무를 통과한 과정입니다.")

    for rule in rules:
        st.write("🌿 " + rule)

    st.success(
        f"최종적으로 {species_names[predictions['Decision Tree']]} "
        f"품종으로 분류되었습니다."
    )

    # ======================================
    # 15. 최종 요약
    # ======================================

    st.divider()
    st.subheader("🔎 최종 분석 결과")

    st.write(
        f"""
        입력한 꽃잎 길이: **{petal_length:.1f}cm**

        입력한 꽃잎 너비: **{petal_width:.1f}cm**

        - KNN 예측: **{predictions['KNN']}**
        - Decision Tree 예측: **{predictions['Decision Tree']}**
        - Random Forest 예측: **{predictions['Random Forest']}**

        세 가지 알고리즘의 결과를 비교하면
        **{species_names[final_species]}**가 가장 많은 표를 얻었습니다.

        또한 테스트 데이터에서 가장 높은 정확도를 보인
        알고리즘은 **{best_algorithm}**입니다.
        """
    )

    st.caption(
        "참고: 가장 많은 표를 얻은 품종은 세 알고리즘의 단순 다수결 결과이며, "
        "테스트 정확도가 가장 높은 모델의 예측과 반드시 같지는 않습니다."
    )

else:

    st.info(
        "꽃잎 길이와 너비를 입력한 다음 "
        "'세 가지 AI로 품종 예측하기' 버튼을 눌러 주세요."
    )


# ==========================================
# 16. 하단 안내
# ==========================================

st.divider()

st.caption(
    "🌸 Iris Classification AI | "
    "Pandas · Scikit-learn · KNN · Decision Tree · Random Forest · Plotly"
)
