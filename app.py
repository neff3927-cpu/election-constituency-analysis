import streamlit as st
from streamlit_folium import st_folium

from utils.loader import load_constituencies, load_history, load_regions
from utils.charts import (
    history_chart, population_bar, voter_scatter,
    regional_seats_scatter, seats_per_population
)
from utils.map import constituency_demo_map

st.set_page_config(page_title="국회의원 지역구 인구와 표의 등가성 분석", layout="wide")
st.title("국회의원 지역구 인구와 표의 등가성 분석")
st.caption("산업데이터시각화 프로젝트 프로토타입")

st.warning(
    "현재 화면은 기능 확인을 위한 예시 데이터 기반 프로토타입입니다. "
    "실제 선거구 통계·경계 데이터가 아니며, 분석 결과를 사실로 인용하면 안 됩니다."
)

constituencies = load_constituencies()
history = load_history()
regions = load_regions()

with st.sidebar:
    st.header("분석 조건")
    selected_region = st.selectbox("시도 선택", ["전체"] + sorted(constituencies["시도"].unique().tolist()))
    map_metric = st.selectbox("지도 표시 기준", ["주민등록인구", "선거인수", "투표자수"])
    top_n = st.selectbox("차트 표시 선거구 수", [5, 10, 20], index=1)

filtered = constituencies.copy()
if selected_region != "전체":
    filtered = filtered[filtered["시도"] == selected_region]

st.subheader("제22대 총선 선거구 현황 — 지도 기능 시연")
left, right = st.columns([1.1, 1])
with left:
    st.markdown("**선거구 위치 예시 지도**")
    st_folium(constituency_demo_map(filtered, map_metric), height=520, use_container_width=True)
    st.caption("주의: 실제 선거구 폴리곤 경계가 아닌 예시 좌표 마커입니다. 실제 경계 GeoJSON 연결 후 교체합니다.")
with right:
    st.markdown("**선거구 인구 비교**")
    st.plotly_chart(population_bar(filtered, top_n), use_container_width=True)
    st.markdown("**역대 총선별 인구 변화**")
    st.plotly_chart(history_chart(history), use_container_width=True)

st.divider()
st.subheader("유권자 및 지역별 의석 배분 분석")
c1, c2 = st.columns(2)
with c1:
    st.markdown("**주민등록인구와 선거인수의 관계**")
    st.plotly_chart(voter_scatter(filtered), use_container_width=True)
with c2:
    st.markdown("**지역별 주민등록인구와 지역구 수의 관계**")
    st.plotly_chart(regional_seats_scatter(regions), use_container_width=True)

st.markdown("**지역구 1석당 주민등록인구 비교**")
st.plotly_chart(seats_per_population(regions), use_container_width=True)

with st.expander("현재 사용 중인 예시 데이터 확인"):
    st.markdown("**선거구별 예시 데이터**")
    st.dataframe(constituencies, use_container_width=True)
    st.markdown("**지역별 인구·의석수 예시 데이터**")
    st.dataframe(regions, use_container_width=True)

st.info(
    "다음 단계: 공식 주민등록인구·선거인수 자료와 제22대 선거구 경계 GeoJSON을 확보해 "
    "예시 데이터를 실제 데이터로 교체합니다."
)
