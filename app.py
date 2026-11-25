from pathlib import Path
import pandas as pd
import requests
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium

HERE = Path(__file__).parent
DATA = HERE / "data"

st.set_page_config(
    page_title="국회의원 지역구 인구와 표의 등가성 분석",
    page_icon="🗳️",
    layout="wide"
)

# Reduce visual clutter and keep the two main panels aligned.
st.markdown("""
<style>
.block-container {padding-top: 1.3rem; padding-bottom: 2rem;}
div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 12px;
}
h1 {font-size: 2.15rem;}
h2 {font-size: 1.55rem;}
</style>
""", unsafe_allow_html=True)

st.title("국회의원 지역구 인구와 표의 등가성 분석")
st.caption("산업데이터시각화 프로젝트 · 인터랙티브 대시보드")
st.warning(
    "현재는 기능 점검용 예시 데이터 버전입니다. 예시 수치와 좌표는 실제 선거구 통계·경계가 아니므로 "
    "분석 결과로 인용할 수 없습니다. 공식 공개자료 연결 후 실제 분석에 사용하세요."
)

@st.cache_data
def load_data():
    return (
        pd.read_csv(DATA / "demo_constituencies.csv"),
        pd.read_csv(DATA / "demo_history.csv"),
        pd.read_csv(DATA / "demo_region_seats.csv")
    )


districts, history, regions = load_data()

GEOJSON_URL = "https://raw.githubusercontent.com/OhmyNews/2024_22_elec_map/main/2024_22_Elec_simplify.json"

@st.cache_data(ttl=86400, show_spinner=False)
def load_constituency_geojson():
    response = requests.get(GEOJSON_URL, timeout=25)
    response.raise_for_status()
    geo = response.json()
    if geo.get("type") != "FeatureCollection" or not geo.get("features"):
        raise ValueError("GeoJSON 형식이 올바르지 않습니다.")
    return geo

# Common widgets
with st.container(border=True):
    st.subheader("공통 입력 위젯")
    c1, c2, c3 = st.columns([1, 1, 1.4])
    with c1:
        election = st.selectbox(
            "총선 시기 선택",
            ["제22대 총선", "제23대 총선 가정", "제21대 이전 총선(자료 확보분)"],
            key="election_period"
        )
    with c2:
        region_options = ["전체"] + sorted(districts["시도"].dropna().unique().tolist())
        selected_region = st.selectbox("지역 선택", region_options, key="region_filter")
    with c3:
        search_options = ["전체 선거구"] + sorted(districts["선거구"].dropna().unique().tolist())
        selected_district = st.selectbox("선거구 검색", search_options, key="district_search")

if election == "제23대 총선 가정":
    st.info("제23대 가정은 제22대 선거구 경계를 고정하고 인구 기준일만 갱신하는 방식입니다. 현재는 갱신 인구자료가 없어 예시 수치를 표시합니다.")
elif election == "제21대 이전 총선(자료 확보분)":
    st.info("과거 총선은 해당 총선 당시 선거구 경계와 인구자료가 확보된 연도만 분석합니다. 현재 예시 자료는 실제 과거 통계가 아닙니다.")

view = districts.copy()
if selected_region != "전체":
    view = view[view["시도"] == selected_region]
if selected_district != "전체 선거구":
    view = view[view["선거구"] == selected_district]

map_options = ["선거구별 주민등록인구", "표의 등가성 지수", "인접 선거구 인구편차"]
chart_options = [
    "선거구별 인구 순위",
    "역대 최대·최소 인구편차 비율",
    "역대 최대·최소·평균 인구 변화",
    "표의 등가성 지수 분포",
    "선거구별 표의 등가성 지수",
    "주민등록인구와 선거인수 관계",
    "선거인수 ÷ 주민등록인구 비율",
    "주민등록인구와 투표자수 관계",
    "지역별 주민등록인구와 지역구 수 관계",
    "지역구 1석당 주민등록인구",
]

# Map and chart columns retain the same visual width; map uses real 22nd-election polygons.
map_col, chart_col = st.columns([1, 1], gap="large")

with map_col:
    with st.container(border=True):
        st.header("지도 영역")
        map_metric = st.selectbox("지도 표시 기준 선택", map_options, key="map_metric")
        st.caption("제22대 실제 선거구 경계 · 외부 지도 타일 없이 표시합니다. 선거구 이름은 마우스를 올리면 확인할 수 있습니다.")

        try:
            geojson = load_constituency_geojson()
            m = folium.Map(
                location=[36.15, 127.85],
                zoom_start=7,
                min_zoom=6,
                max_zoom=10,
                tiles=None,
                control_scale=False,
                prefer_canvas=True
            )
            # No external tile server: no API-key watermark and less visual clutter.
            m.get_root().html.add_child(folium.Element(
                "<style>.leaflet-container { background: #f7f9fb !important; }</style>"
            ))
            korea_bounds = [[33.0, 124.5], [38.7, 131.0]]
            m.fit_bounds(korea_bounds, padding=(12, 12))

            def style_feature(feature):
                return {
                    "fillColor": "#dce8f2",
                    "color": "#58758f",
                    "weight": 0.65,
                    "fillOpacity": 0.58
                }

            folium.GeoJson(
                geojson,
                name="제22대 국회의원 지역구",
                style_function=style_feature,
                highlight_function=lambda feature: {
                    "weight": 2.2,
                    "color": "#173f5f",
                    "fillColor": "#8db8d8",
                    "fillOpacity": 0.78
                },
                tooltip=folium.GeoJsonTooltip(
                    fields=["SIDO_SGG"],
                    aliases=["선거구:"],
                    sticky=True,
                    localize=True,
                    style="background-color: white; color: #222; font-family: sans-serif; font-size: 12px; padding: 6px;"
                ),
                popup=folium.GeoJsonPopup(
                    fields=["SIDO_SGG", "SGG_Code"],
                    aliases=["선거구:", "선거구 코드:"],
                    labels=True
                )
            ).add_to(m)

            st_folium(
                m,
                height=625,
                use_container_width=True,
                returned_objects=[]
            )
            st.caption(
                "경계 자료: OhmyNews 공개 제22대 선거구 GeoJSON(254개 지역구, EPSG:4326). "
                "현재 통계 CSV는 예시자료이므로 경계 색상은 실제 인구수에 따른 단계구분이 아닙니다."
            )
            if map_metric == "인접 선거구 인구편차":
                st.info("인접 선거구 편차는 경계 공유 관계와 실제 인구자료를 연결한 뒤 계산합니다.")
            elif map_metric == "표의 등가성 지수":
                st.info("표의 등가성 지수별 색상은 실제 선거구 인구자료 연결 후 표시합니다.")
            else:
                st.info("선거구별 인구에 따른 색상은 실제 선거구 인구자료 연결 후 표시합니다.")
            selected_map_name = None

        except Exception as exc:
            st.error("실제 선거구 경계 파일을 불러오지 못했습니다. 인터넷 연결 또는 원본 저장소 상태를 확인해 주세요.")
            st.caption(f"오류 내용: {type(exc).__name__}")
            selected_map_name = None

with chart_col:
    with st.container(border=True):
        st.header("차트 영역")
        cc1, cc2 = st.columns(2)
        with cc1:
            chart1 = st.selectbox("차트 1 선택", chart_options, index=0, key="chart1")
        with cc2:
            chart2 = st.selectbox("차트 2 선택", chart_options, index=2, key="chart2")

        def draw_chart(choice, key):
            st.markdown(f"**{choice}**")
            if view.empty:
                st.info("선택한 조건에 해당하는 데이터가 없습니다.")
                return

            if choice == "선거구별 인구 순위":
                temp = view.sort_values("주민등록인구", ascending=False)
                fig = px.bar(temp, x="주민등록인구", y="선거구", color="시도",
                             orientation="h", title="선거구별 주민등록인구 순위")
                fig.update_yaxes(categoryorder="total ascending")
                fig.update_xaxes(tickformat=",", title="주민등록인구(명)")

            elif choice == "역대 최대·최소 인구편차 비율":
                temp = history.copy()
                temp["최대·최소 인구비율"] = temp["최대인구"] / temp["최소인구"]
                fig = px.line(temp, x="연도", y="최대·최소 인구비율", markers=True,
                              text=temp["최대·최소 인구비율"].round(2),
                              title="최대 선거구 인구 ÷ 최소 선거구 인구")
                fig.update_traces(textposition="top center")
                fig.update_yaxes(title="최대·최소 인구비율(배)", tickformat=".2f")

            elif choice == "역대 최대·최소·평균 인구 변화":
                fig = go.Figure()
                for col, label in [("최대인구", "최대"), ("최소인구", "최소"), ("평균인구", "평균")]:
                    fig.add_trace(go.Scatter(x=history["연도"], y=history[col],
                                             mode="lines+markers", name=label))
                fig.update_layout(title="역대 총선별 선거구 인구 변화",
                                  xaxis_title="총선 연도", yaxis_title="인구(명)",
                                  yaxis_tickformat=",")

            elif choice in ["표의 등가성 지수 분포", "선거구별 표의 등가성 지수"]:
                temp = view.copy()
                temp["표의 등가성 지수"] = districts["주민등록인구"].mean() / temp["주민등록인구"]
                if choice == "표의 등가성 지수 분포":
                    fig = px.histogram(temp, x="표의 등가성 지수", nbins=10,
                                       title="전국 평균 인구 ÷ 선거구 인구")
                    fig.add_vline(x=1, line_dash="dash", line_color="red",
                                  annotation_text="전국 평균(1.0)")
                else:
                    temp = temp.sort_values("표의 등가성 지수")
                    fig = px.bar(temp, x="표의 등가성 지수", y="선거구",
                                 color="시도", orientation="h",
                                 title="선거구별 표의 등가성 지수")
                    fig.update_yaxes(categoryorder="total ascending")
                    fig.add_vline(x=1, line_dash="dash", line_color="red",
                                  annotation_text="전국 평균(1.0)")

            elif choice == "주민등록인구와 선거인수 관계":
                fig = px.scatter(view, x="주민등록인구", y="선거인수", color="시도",
                                 hover_name="선거구", trendline="ols",
                                 title="주민등록인구와 선거인수의 관계")
                fig.update_xaxes(title="주민등록인구(명)", tickformat=",")
                fig.update_yaxes(title="선거인수(명)", tickformat=",")

            elif choice == "선거인수 ÷ 주민등록인구 비율":
                temp = view.copy()
                temp["선거인수 비율(%)"] = temp["선거인수"] / temp["주민등록인구"] * 100
                fig = px.bar(temp.sort_values("선거인수 비율(%)"),
                             x="선거인수 비율(%)", y="선거구", color="시도",
                             orientation="h", title="선거인수 ÷ 주민등록인구")
                fig.update_yaxes(categoryorder="total ascending")
                fig.update_xaxes(title="선거인수 비율(%)", ticksuffix="%")

            elif choice == "주민등록인구와 투표자수 관계":
                fig = px.scatter(view, x="주민등록인구", y="투표자수", color="시도",
                                 hover_name="선거구", trendline="ols",
                                 title="주민등록인구와 실제 투표자수의 관계")
                fig.update_xaxes(title="주민등록인구(명)", tickformat=",")
                fig.update_yaxes(title="투표자수(명)", tickformat=",")

            elif choice == "지역별 주민등록인구와 지역구 수 관계":
                temp = regions.copy()
                fig = px.scatter(temp, x="주민등록인구", y="지역구수", text="지역",
                                 trendline="ols",
                                 title="지역별 주민등록인구와 국회의원 지역구 수")
                fig.update_traces(textposition="top center")
                fig.update_xaxes(title="주민등록인구(명)", tickformat=",")
                fig.update_yaxes(title="지역구 수(석)")

            elif choice == "지역구 1석당 주민등록인구":
                temp = regions.copy()
                temp["1석당 인구"] = temp["주민등록인구"] / temp["지역구수"]
                fig = px.bar(temp.sort_values("1석당 인구"),
                             x="지역", y="1석당 인구",
                             title="지역구 1석당 주민등록인구")
                fig.update_yaxes(title="1석당 인구(명)", tickformat=",")

            fig.update_layout(height=350, margin=dict(l=8, r=8, t=48, b=8))
            st.plotly_chart(fig, use_container_width=True, key=key)

        draw_chart(chart1, "chart_one")
        st.divider()
        draw_chart(chart2, "chart_two")
        st.caption(
            "인접 선거구 비교·역대 Box Plot·총선별 지수 분포·인구증감률 분석은 "
            "추가 원자료가 필요해 데이터 확보 후 추가합니다."
        )

# Details
detail_name = selected_district if selected_district != "전체 선거구" else selected_map_name
if not detail_name and not view.empty:
    detail_name = view.iloc[0]["선거구"]

with st.container(border=True):
    st.header("선거구 상세정보")
    if detail_name:
        row = districts[districts["선거구"] == detail_name].iloc[0]
        avg_pop = districts["주민등록인구"].mean()
        d1, d2, d3, d4 = st.columns(4)
        d1.metric("선거구", row["선거구"])
        d2.metric("주민등록인구", f"{row['주민등록인구']:,.0f}명")
        d3.metric("선거인수", f"{row['선거인수']:,.0f}명")
        d4.metric("표의 등가성 지수", f"{avg_pop / row['주민등록인구']:.3f}")
        st.caption(f"지역: {row['시도']} · 예시 데이터 기준")
        st.info("전국 순위와 인접 선거구 정보는 실제 선거구별 인구·경계자료 연결 후 추가합니다.")
    else:
        st.info("지역 또는 선거구를 선택하면 상세정보가 표시됩니다.")

with st.expander("지도 및 데이터 출처"):
    st.markdown(
        "- 제22대 선거구 경계: [OhmyNews/2024_22_elec_map](https://github.com/OhmyNews/2024_22_elec_map) (MIT License)\\n"
        "- 경계 구성: 통계청 행정동 경계를 제22대 254개 지역구 단위로 결합한 GeoJSON\\n"
        "- 인구·선거인수 CSV: 현재 화면 점검용 예시자료이며 실제 통계가 아님"
    )

with st.expander("현재 사용 중인 예시 데이터 확인"):
    st.caption("임의의 화면 점검용 자료이며 실제 선거 통계가 아닙니다.")
    st.dataframe(districts, use_container_width=True)
    st.dataframe(history, use_container_width=True)
    st.dataframe(regions, use_container_width=True)
