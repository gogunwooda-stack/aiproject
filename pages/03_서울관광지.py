
import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(
    page_title="서울 관광 명소 TOP 10",
    page_icon="🗺️",
    layout="wide"
)

# 서울 주요 외국인 관광 명소 데이터
PLACES = [
    {
        "rank": 1, "name": "명동",
        "name_en": "Myeongdong",
        "category": "쇼핑·먹거리",
        "lat": 37.5636, "lon": 126.9869,
        "description": "쇼핑과 길거리 음식으로 유명한 서울 대표 번화가입니다.",
        "tip": "저녁 시간대 길거리 음식과 쇼핑을 즐겨보세요."
    },
    {
        "rank": 2, "name": "N서울타워",
        "name_en": "N Seoul Tower",
        "category": "전망·랜드마크",
        "lat": 37.5512, "lon": 126.9882,
        "description": "남산에서 서울 도심을 한눈에 볼 수 있는 대표 랜드마크입니다.",
        "tip": "해 질 무렵 방문하면 서울의 야경도 감상할 수 있습니다."
    },
    {
        "rank": 3, "name": "삼성역·코엑스",
        "name_en": "Samseong Station & COEX",
        "category": "쇼핑·문화",
        "lat": 37.5117, "lon": 127.0592,
        "description": "대형 쇼핑몰과 별마당도서관이 있는 복합문화공간입니다.",
        "tip": "코엑스몰과 별마당도서관을 함께 둘러보세요."
    },
    {
        "rank": 4, "name": "강남역",
        "name_en": "Gangnam Station",
        "category": "쇼핑·도심",
        "lat": 37.4979, "lon": 127.0276,
        "description": "쇼핑, 음식점, 카페가 밀집한 서울의 대표 번화가입니다.",
        "tip": "강남역 주변의 다양한 음식점과 카페를 즐겨보세요."
    },
    {
        "rank": 5, "name": "홍대",
        "name_en": "Hongdae",
        "category": "문화·야간",
        "lat": 37.5563, "lon": 126.9236,
        "description": "버스킹, 음악, 패션 등 젊은 문화를 즐길 수 있는 거리입니다.",
        "tip": "주말에는 거리 공연과 다양한 상점을 구경해 보세요."
    },
    {
        "rank": 6, "name": "남대문시장",
        "name_en": "Namdaemun Market",
        "category": "시장·쇼핑",
        "lat": 37.5592, "lon": 126.9777,
        "description": "다양한 생활용품과 먹거리, 기념품을 만날 수 있는 전통시장입니다.",
        "tip": "시장 골목을 걸으며 한국의 전통시장 분위기를 경험해 보세요."
    },
    {
        "rank": 7, "name": "동대문디자인플라자",
        "name_en": "Dongdaemun Design Plaza",
        "category": "건축·문화",
        "lat": 37.5671, "lon": 127.0095,
        "description": "독특한 건축물과 전시·디자인 행사로 유명한 복합문화공간입니다.",
        "tip": "방문 전 전시와 행사 일정을 확인해 보세요."
    },
    {
        "rank": 8, "name": "북촌한옥마을",
        "name_en": "Bukchon Hanok Village",
        "category": "전통·거리",
        "lat": 37.5826, "lon": 126.9830,
        "description": "전통 한옥이 모여 있는 아름다운 골목입니다.",
        "tip": "실제 주민들이 거주하는 곳이므로 조용히 관람해 주세요."
    },
    {
        "rank": 9, "name": "경복궁",
        "name_en": "Gyeongbokgung Palace",
        "category": "역사·문화",
        "lat": 37.5796, "lon": 126.9770,
        "description": "조선 왕조의 법궁으로 한국의 전통 건축을 감상할 수 있습니다.",
        "tip": "방문 전 휴궁일과 관람 시간을 확인하세요."
    },
    {
        "rank": 10, "name": "서울숲·성수",
        "name_en": "Seoul Forest & Seongsu",
        "category": "공원·문화",
        "lat": 37.5445, "lon": 127.0374,
        "description": "서울숲의 자연과 성수동의 카페, 편집숍을 함께 즐길 수 있습니다.",
        "tip": "서울숲 산책 후 성수동 골목을 둘러보세요."
    }
]

df = pd.DataFrame(PLACES)

# 제목
st.title("🗺️ 서울 외국인 관광 명소 TOP 10")
st.write("서울을 방문하는 외국인 관광객에게 인기 있는 주요 명소를 지도에서 확인해 보세요!")

st.info(
    "2025년 서울 주요 명소 외국인 유동인구 분석을 참고한 목록입니다. "
    "선호도 투표 순위와는 다를 수 있습니다."
)

# 관광지 유형 필터
categories = ["전체"] + sorted(df["category"].unique().tolist())

selected_category = st.selectbox(
    "🔎 관광지 유형 선택",
    categories
)

if selected_category == "전체":
    filtered = df
else:
    filtered = df[df["category"] == selected_category]

# 화면 구성
left, right = st.columns([1.5, 1])

with left:
    st.subheader("📍 서울 관광 명소 지도")

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=filtered,
        get_position="[lon, lat]",
        get_radius=105,
        radius_min_pixels=7,
        radius_max_pixels=18,
        get_fill_color=[235, 91, 65, 210],
        get_line_color=[255, 255, 255, 230],
        line_width_min_pixels=1,
        pickable=True,
        auto_highlight=True
    )

    text_layer = pdk.Layer(
        "TextLayer",
        data=filtered,
        get_position="[lon, lat]",
        get_text="rank",
        get_size=14,
        get_color=[30, 30, 30, 255],
        get_text_anchor='"middle"',
        get_alignment_baseline='"bottom"',
        get_pixel_offset=[0, -12]
    )

    view_state = pdk.ViewState(
        latitude=37.5665,
        longitude=126.9850,
        zoom=11,
        pitch=0
    )

    deck = pdk.Deck(
        layers=[layer, text_layer],
        initial_view_state=view_state,
        tooltip={
            "html": "<b>{rank}. {name}</b><br/>{name_en}<br/>{category}",
            "style": {"color": "white"}
        },
        map_style="light"
    )

    st.pydeck_chart(deck, use_container_width=True)

with right:
    st.subheader("⭐ 관광지 TOP 10")

    for _, place in filtered.sort_values("rank").iterrows():

        with st.expander(
            f"{int(place['rank'])}. {place['name']}"
        ):
            st.markdown(f"**{place['name_en']}**")
            st.write(place["description"])
            st.caption(f"📌 유형: {place['category']}")
            st.info(f"💡 여행 팁: {place['tip']}")

# 관광지 목록
st.divider()
st.subheader("📋 관광지 전체 목록")

show_df = filtered[
    ["rank", "name", "name_en", "category", "description"]
].rename(columns={
    "rank": "순위",
    "name": "관광지",
    "name_en": "영문명",
    "category": "유형",
    "description": "소개"
})

st.dataframe(
    show_df,
    use_container_width=True,
    hide_index=True
)

st.caption(
    "※ 지도 좌표는 관광지의 대표 위치이며 실제 출입구 위치와 다를 수 있습니다."
)
