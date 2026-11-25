from pathlib import Path
import json
import pandas as pd
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

st.title("국회의원 지역구 인구와 표의 등가성 분석")
st.caption("산업데이터시각화 프로젝트 · 인터랙티브 대시보드")

st.warning(
    "현재 화면은 기능 구현·점검용 예시 데이터 버전입니다. "
    "예시 수치와 좌표는 실제 선거구 통계·경계가 아니므로 분석 결과로 인용할 수 없습니다. "
    "공식 공개자료 연결 후 실제 분석에 사용하세요."
)

@st.cache_data
def load_data():
    districts = pd.read_csv(DATA / "demo_constituencies.csv")
    history = pd.read_csv(DATA / "demo_history.csv")
    regions = pd.read_csv(DATA / "demo_region_seats.csv")
    return districts, history, regions

districts, history, regions = load_data()

# ---- Common controls ----
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
    st.info(
        "제23대 가정은 제22대 선거구 경계를 유지하고 인구 기준일만 갱신하는 분석 설계입니다. "
        "현재는 실제 기준일 인구자료가 연결되지 않아 예시 자료를 표시합니다."
    )
elif election == "제21대 이전 총선(자료 확보분)":
    st.info(
        "과거 총선은 해당 총선 당시의 선거구 경계·인구 기준 자료가 확보된 연도만 분석해야 합니다. "
        "현재 예시 파일은 실제 과거 통계가 아니므로 실제 시계열 비교에는 사용할 수 없습니다."
    )

view = districts.copy()
if selected_region != "전체":
    view = view[view["시도"] == selected_region]
if selected_district != "전체 선거구":
    view = view[view["선거구"] == selected_district]

# ---- Chart options ----
chart_options = [
    "선거구별 인구 순위",
    "역대 최대·최소 인구편차 비율",
    "역대 최대·최소·평균 인구 변화",
    "인접 선거구 인구 비교",
    "표의 등가성 지수 분포",
    "총선별 표의 등가성 지수 분포 비율",
    "주민등록인구와 선거인수 관계",
    "지역별 주민등록인구와 지역구 수 관계",
    "지역구 1석당 주민등록인구",
    "역대 총선별 선거구 인구분포(Box Plot)",
    "인구증감률과 표의 등가성 지수 관계",
]
map_options = [
    "선거구별 주민등록인구",
    "표의 등가성 지수",
    "인접 선거구 인구편차",
]

map_col, chart_col = st.columns([1, 1], gap="large")

# ---- Map area ----
with map_col:
    with st.container(border=True):
        st.header("지도 영역")
        map_metric = st.selectbox("지도 표시 기준 선택", map_options, key="map_metric")
        st.caption("선거구별 색상 변화 · 마커를 선택하면 아래 상세정보가 갱신됩니다.")

        map_view = view.copy()
        selected_map_name = None
        if map_view.empty:
            st.info("선택 조건에 해당하는 선거구가 없습니다.")
        else:
            # Current sample data has point coordinates, not constituency polygons.
            m = folium.Map(location=[36.3, 127.8], zoom_start=6, tiles="OpenStreetMap")
            if map_metric == "선거구별 주민등록인구":
                metric_values = map_view["주민등록인구"]
            elif map_metric == "표의 등가성 지수":
                national_mean = districts["주민등록인구"].mean()
                metric_values = national_mean / map_view["주민등록인구"]
            else:
                # Adjacency is not inferred from point coordinates.
                metric_values = pd.Series([0] * len(map_view), index=map_view.index)
                st.caption("인접 선거구 편차는 실제 경계 GeoJSON과 인접성 계산자료를 연결한 뒤 표시합니다.")

            lo, hi = float(metric_values.min()), float(metric_values.max())
            for idx, row in map_view.iterrows():
                value = float(metric_values.loc[idx])
                ratio = (value - lo) / (hi - lo) if hi != lo else 0.5
                color = "#2166ac" if ratio < 1/3 else ("#fdae61" if ratio < 2/3 else "#b2182b")
                popup = (
                    f"<b>{row['선거구']}</b><br>지역: {row['시도']}<br>"
                    f"주민등록인구: {row['주민등록인구']:,}명<br>"
                    f"선거인수: {row['선거인수']:,}명"
                )
                folium.CircleMarker(
                    [row["위도"], row["경도"]], radius=9, color=color,
                    fill=True, fill_color=color, fill_opacity=0.8,
                    tooltip=row["선거구"], popup=folium.Popup(popup, max_width=260)
                ).add_to(m)
            map_result = st_folium(
                m, height=490, use_container_width=True,
                returned_objects=["last_object_clicked"]
            )
            clicked = map_result.get("last_object_clicked") if map_result else None
            if clicked and clicked.get("lat") is not None and clicked.get("lng") is not None:
                nearest_idx = (
                    (map_view["위도"] - clicked["lat"]) ** 2 +
                    (map_view["경도"] - clicked["lng"]) ** 2
                ).idxmin()
                selected_map_name = map_view.loc[nearest_idx, "선거구"]

            st.caption(
                "현재 지도는 예시 좌표 마커입니다. 실제 제22대 선거구 경계 GeoJSON 연결 후 "
                "폴리곤 지도와 선거구 클릭 기능으로 교체합니다."
            )

# ---- Chart area ----
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

            if choice == "선거구별 인구 순위":
                if view.empty:
                    st.info("표시할 데이터가 없습니다.")
                    return
                fig = px.bar(
                    view.sort_values("주민등록인구"),
                    x="주민등록인구", y="선거구", color="시도",
                    orientation="h", title="선거구별 주민등록인구(예시 데이터)"
                )
                fig.update_xaxes(tickformat=",")
                st.plotly_chart(fig, use_container_width=True, key=key)

            elif choice == "역대 최대·최소 인구편차 비율":
                temp = history.copy()
                temp["최대·최소 인구비율"] = temp["최대인구"] / temp["최소인구"]
                fig = px.line(
                    temp, x="연도", y="최대·최소 인구비율", markers=True,
                    title="역대 총선별 최대 인구 ÷ 최소 인구(예시 데이터)"
                )
                fig.update_yaxes(tickformat=".2f")
                st.plotly_chart(fig, use_container_width=True, key=key)

            elif choice == "역대 최대·최소·평균 인구 변화":
                fig = go.Figure()
                for col, label in [("최대인구", "최대"), ("최소인구", "최소"), ("평균인구", "평균")]:
                    fig.add_trace(go.Scatter(x=history["연도"], y=history[col], mode="lines+markers", name=label))
                fig.update_layout(title="역대 총선별 선거구 인구 변화(예시 데이터)",
                                  xaxis_title="총선 연도", yaxis_title="인구", yaxis_tickformat=",")
                st.plotly_chart(fig, use_container_width=True, key=key)

            elif choice == "인접 선거구 인구 비교":
                st.info("실제 선거구 경계 GeoJSON에서 공유 경계를 계산한 뒤 구현합니다. 현재는 인접관계를 임의로 만들지 않습니다.")

            elif choice == "표의 등가성 지수 분포":
                if view.empty:
                    st.info("표시할 데이터가 없습니다.")
                    return
                temp = view.copy()
                temp["표의 등가성 지수"] = districts["주민등록인구"].mean() / temp["주민등록인구"]
                fig = px.histogram(temp, x="표의 등가성 지수", nbins=10,
                                   title="전국 평균 인구 ÷ 선거구 인구(예시 데이터)")
                fig.add_vline(x=1, line_dash="dash", line_color="red")
                st.plotly_chart(fig, use_container_width=True, key=key)

            elif choice == "총선별 표의 등가성 지수 분포 비율":
                st.info("총선별 실제 선거구 인구 원자료를 연결한 뒤 지수 1 초과·미만 비율을 계산합니다.")

            elif choice == "주민등록인구와 선거인수 관계":
                if view.empty:
                    st.info("표시할 데이터가 없습니다.")
                    return
                fig = px.scatter(view, x="주민등록인구", y="선거인수", color="시도",
                                 hover_name="선거구", trendline="ols",
                                 title="주민등록인구와 선거인수(예시 데이터)")
                fig.update_xaxes(tickformat=",")
                fig.update_yaxes(tickformat=",")
                st.plotly_chart(fig, use_container_width=True, key=key)

            elif choice == "지역별 주민등록인구와 지역구 수 관계":
                temp = regions.copy()
                if selected_region != "전체":
                    temp = temp[temp["지역"] == selected_region]
                fig = px.scatter(temp, x="주민등록인구", y="지역구수",
                                 text="지역", trendline="ols",
                                 title="지역별 주민등록인구와 지역구 수(예시 데이터)")
                fig.update_xaxes(tickformat=",")
                st.plotly_chart(fig, use_container_width=True, key=key)

            elif choice == "지역구 1석당 주민등록인구":
                temp = regions.copy()
                if selected_region != "전체":
                    temp = temp[temp["지역"] == selected_region]
                temp["1석당 인구"] = temp["주민등록인구"] / temp["지역구수"]
                fig = px.bar(temp.sort_values("1석당 인구"), x="지역", y="1석당 인구",
                             title="지역구 1석당 주민등록인구(예시 데이터)")
                fig.update_yaxes(tickformat=",")
                st.plotly_chart(fig, use_container_width=True, key=key)

            elif choice == "역대 총선별 선거구 인구분포(Box Plot)":
                st.info("총선별 선거구 단위 원자료가 연결되면 중앙값·사분위수·이상치를 비교합니다.")

            elif choice == "인구증감률과 표의 등가성 지수 관계":
                st.info("동일한 공간 범위로 재집계한 과거·현재 인구자료를 연결한 뒤 산점도와 추세선을 표시합니다.")

        draw_chart(chart1, "chart_one")
        st.divider()
        draw_chart(chart2, "chart_two")

# ---- Detailed information ----
detail_name = selected_district if selected_district != "전체 선거구" else selected_map_name
if not detail_name and not view.empty:
    detail_name = view.iloc[0]["선거구"]

with st.container(border=True):
    st.header("선거구 상세정보")
    if detail_name:
        row = districts[districts["선거구"] == detail_name].iloc[0]
        mean_pop = districts["주민등록인구"].mean()
        eq_index = mean_pop / row["주민등록인구"]
        d1, d2, d3, d4 = st.columns(4)
        d1.metric("선거구", row["선거구"])
        d2.metric("주민등록인구", f"{row['주민등록인구']:,.0f}명")
        d3.metric("선거인수", f"{row['선거인수']:,.0f}명")
        d4.metric("표의 등가성 지수", f"{eq_index:.3f}")
        st.caption(f"지역: {row['시도']} · 예시 데이터 기준")
        st.info("전국 순위와 인접 선거구 정보는 실제 선거구별 인구·경계 자료 연결 후 추가합니다.")
    else:
        st.info("지역 또는 선거구를 선택하면 상세정보가 표시됩니다.")

with st.expander("현재 사용 중인 예시 데이터 확인"):
    st.caption("아래 자료는 임의로 만든 화면 점검용 데이터이며 실제 선거 통계가 아닙니다.")
    st.dataframe(districts, use_container_width=True)
    st.dataframe(history, use_container_width=True)
    st.dataframe(regions, use_container_width=True)
