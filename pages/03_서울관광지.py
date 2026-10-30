
import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster, Fullscreen
from streamlit_folium import st_folium

# ---------------------------------------
# 1. 페이지 설정
# ---------------------------------------

st.set_page_config(
    page_title="서울 관광 명소 TOP 10",
    page_icon="🗺️",
    layout="wide"
)

st.title("🗺️ 서울 외국인 관광 명소 TOP 10")
st.markdown(
    "서울을 방문하는 외국인 관광객을 위한 주요 관광지를 "
    "인터랙티브 지도에서 확인해 보세요!"
)

st.info(
    "2025년 서울 주요 명소 외국인 유동인구 분석을 참고한 목록입니다. "
    "실시간 선호도 투표 순위와는 다를 수 있습니다."
)

# ---------------------------------------
# 2. 관광지 데이터
# ---------------------------------------

PLACES = [
    {
        "rank": 1,
        "name": "명동",
        "english": "Myeongdong",
        "category": "쇼핑·먹거리",
        "lat": 37.5636,
        "lon": 126.9869,
        "description": "쇼핑과 길거리 음식으로 유명한 서울 대표 번화가입니다.",
        "tip": "저녁 시간대 길거리 음식과 쇼핑을 즐겨보세요."
    },
    {
        "rank": 2,
        "name": "N서울타워",
        "english": "N Seoul Tower",
        "category": "전망·랜드마크",
        "lat": 37.5512,
        "lon": 126.9882,
        "description": "남산에서 서울 도심을 한눈에 볼 수 있는 대표 랜드마크입니다.",
        "tip": "해 질 무렵 방문하면 서울의 야경도 감상할 수 있습니다."
    },
    {
        "rank": 3,
        "name": "삼성역·코엑스",
        "english": "Samseong Station & COEX",
        "category": "쇼핑·문화",
        "lat": 37.5117,
        "lon": 127.0592,
        "description": "대형 쇼핑몰과 별마당도서관이 있는 복합문화공간입니다.",
        "tip": "코엑스몰과 별마당도서관을 함께 둘러보세요."
    },
    {
        "rank": 4,
        "name": "강남역",
        "english": "Gangnam Station",
        "category": "쇼핑·도심",
        "lat": 37.4979,
        "lon": 127.0276,
        "description": "쇼핑, 음식점, 카페가 밀집한 서울의 대표 번화가입니다.",
        "tip": "강남역 주변의 다양한 음식점과 카페를 즐겨보세요."
    },
    {
        "rank": 5,
        "name": "홍대",
        "english": "Hongdae",
        "category": "문화·야간",
        "lat": 37.5563,
        "lon": 126.9236,
        "description": "버스킹, 음악, 패션 등 젊은 문화를 즐길 수 있는 거리입니다.",
        "tip": "주말에는 거리 공연과 다양한 상점을 구경해 보세요."
    },
    {
        "rank": 6,
        "name": "남대문시장",
        "english": "Namdaemun Market",
        "category": "시장·쇼핑",
        "lat": 37.5592,
        "lon": 126.9777,
        "description": "다양한 생활용품과 먹거리, 기념품을 만날 수 있는 전통시장입니다.",
        "tip": "시장 골목을 걸으며 한국의 전통시장 분위기를 경험해 보세요."
    },
    {
        "rank": 7,
        "name": "동대문디자인플라자",
        "english": "Dongdaemun Design Plaza",
        "category": "건축·문화",
        "lat": 37.5671,
        "lon": 127.0095,
        "description": "독특한 건축물과 전시·디자인 행사로 유명한 복합문화공간입니다.",
        "tip": "방문 전 전시와 행사 일정을 확인해 보세요."
    },
    {
        "rank": 8,
        "name": "북촌한옥마을",
        "english": "Bukchon Hanok Village",
        "category": "전통·거리",
        "lat": 37.5826,
        "lon": 126.9830,
        "description": "전통 한옥이 모여 있는 아름다운 골목입니다.",
        "tip": "실제 주민들이 거주하는 곳이므로 조용히 관람해 주세요."
    },
    {
        "rank": 9,
        "name": "경복궁",
        "english": "Gyeongbokgung Palace",
        "category": "역사·문화",
        "lat": 37.5796,
        "lon": 126.9770,
        "description": "조선 왕조의 법궁으로 한국의 전통 건축을 감상할 수 있습니다.",
        "tip": "방문 전 휴궁일과 관람 시간을 확인하세요."
    },
    {
        "rank": 10,
        "name": "서울숲·성수",
        "english": "Seoul Forest & Seongsu",
        "category": "공원·문화",
        "lat": 37.5445,
        "lon": 127.0374,
        "description": "서울숲의 자연과 성수동의 카페, 편집숍을 함께 즐길 수 있습니다.",
        "tip": "서울숲 산책 후 성수동 골목을 둘러보세요."
    }
]

df = pd.DataFrame(PLACES)

# ---------------------------------------
# 3. 관광지 유형 필터
# ---------------------------------------

st.subheader("🔎 관광지 검색")

categories = ["전체"] + sorted(df["category"].unique().tolist())

selected_category = st.selectbox(
    "관광지 유형을 선택하세요.",
    categories
)

if selected_category == "전체":
    filtered = df.copy()
else:
    filtered = df[df["category"] == selected_category].copy()

st.caption(f"현재 {len(filtered)}개의 관광지가 표시됩니다.")

# ---------------------------------------
# 4. Folium 지도 생성
# ---------------------------------------

st.subheader("📍 서울 관광 명소 지도")

# 서울 중심 좌표
m = folium.Map(
    location=[37.5665, 126.9850],
    zoom_start=11,
    tiles="OpenStreetMap",
    control_scale=True
)

# 전체 화면 버튼
Fullscreen(
    position="topright",
    title="전체 화면",
    title_cancel="전체 화면 종료"
).add_to(m)

# 마커 그룹
marker_cluster = MarkerCluster().add_to(m)

# 관광지별 마커 생성
for _, place in filtered.iterrows():

    # 순위 숫자가 들어간 마커 디자인
    marker_html = f"""
    <div style="
        background-color:#e74c3c;
        color:white;
        border-radius:50%;
        width:32px;
        height:32px;
        text-align:center;
        line-height:32px;
        font-weight:bold;
        font-size:14px;
        border:2px solid white;
        box-shadow:0 2px 5px rgba(0,0,0,0.4);
    ">
        {int(place['rank'])}
    </div>
    """

    custom_icon = folium.DivIcon(
        html=marker_html,
        icon_size=(32, 32),
        icon_anchor=(16, 16)
    )

    # 클릭 시 나타나는 관광지 정보
    popup_html = f"""
    <div style="width:230px; font-family:Arial;">
        <h3 style="color:#e74c3c;">
            {int(place['rank'])}. {place['name']}
        </h3>

        <h4>{place['english']}</h4>

        <p><b>유형:</b> {place['category']}</p>

        <p>{place['description']}</p>

        <hr>

        <p>
            <b>💡 여행 팁</b><br>
            {place['tip']}
        </p>
    </div>
    """

    folium.Marker(
        location=[place["lat"], place["lon"]],
        tooltip=f"{int(place['rank'])}위. {place['name']}",
        popup=folium.Popup(
            popup_html,
            max_width=280
        ),
        icon=custom_icon
    ).add_to(marker_cluster)

# 지도 표시
st_folium(
    m,
    width=1200,
    height=650,
    returned_objects=[],
    key="seoul_tourism_map"
)

st.caption(
    "📌 지도 위 숫자 마커를 클릭하면 관광지 상세 정보를 확인할 수 있습니다."
)

# ---------------------------------------
# 5. 관광지 상세 정보
# ---------------------------------------

st.divider()

st.subheader("⭐ 관광지 TOP 10 상세 정보")

for _, place in filtered.sort_values("rank").iterrows():

    with st.expander(
        f"{int(place['rank'])}위 | {place['name']} ({place['english']})"
    ):

        col1, col2 = st.columns([1, 2])

        with col1:
            st.metric(
                label="관광지 순위",
                value=f"{int(place['rank'])}위"
            )

            st.write(f"📍 유형: {place['category']}")

            st.write(
                f"🧭 좌표: {place['lat']}, {place['lon']}"
            )

        with col2:
            st.markdown("**관광지 소개**")
            st.write(place["description"])

            st.markdown("**💡 여행 팁**")
            st.write(place["tip"])

# ---------------------------------------
# 6. 관광지 목록
# ---------------------------------------

st.divider()

st.subheader("📋 관광지 전체 목록")

show_df = filtered[
    ["rank", "name", "english", "category", "description"]
].rename(columns={
    "rank": "순위",
    "name": "관광지",
    "english": "영문명",
    "category": "유형",
    "description": "소개"
})

st.dataframe(
    show_df,
    use_container_width=True,
    hide_index=True
)

# ---------------------------------------
# 7. 마무리
# ---------------------------------------

st.divider()

st.markdown(
    """
    ### 🌏 Enjoy Your Seoul Trip!

    서울의 다양한 매력을 직접 경험해 보세요.

    🏯 역사와 전통  
    🛍️ 쇼핑과 먹거리  
    🎨 문화와 예술  
    🌃 아름다운 서울의 야경
    """
)

st.caption(
    "관광지 위치는 지도 표시용 대표 좌표입니다. "
    "지도 타일을 불러오려면 인터넷 연결이 필요합니다."
)
