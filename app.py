from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium

HERE = Path(__file__).parent
st.set_page_config(page_title="국회의원 지역구 인구와 표의 등가성 분석", page_icon="🗳️", layout="wide")

@st.cache_data
def load_data():
    districts = pd.read_csv(HERE / "data" / "demo_constituencies.csv")
    history = pd.read_csv(HERE / "data" / "demo_history.csv")
    regions = pd.read_csv(HERE / "data" / "demo_region_seats.csv")
    return districts, history, regions

districts, history, regions = load_data()

st.title("국회의원 지역구 인구와 표의 등가성 분석")
st.caption("산업데이터시각화 프로젝트 · 인터랙티브 대시보드")

st.warning(
    "현재는 화면과 위젯 연동을 확인하는 예시 데이터 버전입니다. "
    "실제 선거구 통계나 실제 선거구 경계가 아니므로 분석 결과를 사실로 인용하면 안 됩니다."
)

# ── 공통 입력 위젯: 사용자가 정한 화면 설계에 따라 상단 배치 ──
with st.container(border=True):
    st.subheader("공통 입력 위젯")
    w1, w2, w3 = st.columns([1, 1, 1.4])
    with w1:
        election = st.selectbox("총선 시기 선택", ["제22대 총선(지도 시연)", "역대 총선 추세 보기"])
    with w2:
        region_options = ["전체"] + sorted(districts["시도"].unique().tolist())
        selected_region = st.selectbox("지역 선택", region_options)
    with w3:
        district_options = ["전체 선거구"] + districts["선거구"].tolist()
        selected_district = st.selectbox("선거구 검색", district_options)

filtered = districts.copy()
if selected_region != "전체":
    filtered = filtered[filtered["시도"] == selected_region]
if selected_district != "전체 선거구":
    filtered = filtered[filtered["선거구"] == selected_district]

# Map and chart display controls, side-by-side as in the agreed wireframe.
map_col, chart_col = st.columns([1, 1])

with map_col:
    with st.container(border=True):
        st.subheader("지도 영역")
        map_metric_label = st.selectbox(
            "지도 표시 기준 선택",
            ["주민등록인구", "선거인수", "투표자수", "표의 등가성 지수(예시 계산)"],
            key="map_metric"
        )
        st.caption("선거구별 색상 변화 · 마커를 선택하면 아래 상세정보가 갱신됩니다.")

        map_df = filtered.copy()
        if map_df.empty:
            st.info("선택 조건에 해당하는 선거구가 없습니다.")
            selected_map_name = None
        else:
            m = folium.Map(location=[36.3, 127.8], zoom_start=6, tiles="OpenStreetMap")
            metric_col = map_metric_label
            if map_metric_label == "표의 등가성 지수(예시 계산)":
                avg_pop = districts["주민등록인구"].mean()
                map_df[metric_col] = avg_pop / map_df["주민등록인구"]
            vals = map_df[metric_col]
            lo, hi = float(vals.min()), float(vals.max())
            for _, row in map_df.iterrows():
                val = float(row[metric_col])
                ratio = (val - lo) / (hi - lo) if hi != lo else 0.5
                color = "#2166ac" if ratio < 0.34 else ("#fdae61" if ratio < 0.67 else "#b2182b")
                popup_text = (
                    f"<b>{row['선거구']}</b><br>지역: {row['시도']}<br>"
                    f"주민등록인구: {row['주민등록인구']:,}<br>"
                    f"선거인수: {row['선거인수']:,}<br>투표자수: {row['투표자수']:,}"
                )
                folium.CircleMarker(
                    [row["위도"], row["경도"]], radius=9, color=color,
                    fill=True, fill_color=color, fill_opacity=0.78,
                    tooltip=row["선거구"], popup=folium.Popup(popup_text, max_width=260)
                ).add_to(m)
            map_result = st_folium(m, height=470, use_container_width=True, returned_objects=["last_object_clicked"])
            clicked = map_result.get("last_object_clicked") if map_result else None
            selected_map_name = None
            if clicked:
                lat, lon = clicked.get("lat"), clicked.get("lng")
                if lat is not None and lon is not None:
                    nearest = ((map_df["위도"] - lat) ** 2 + (map_df["경도"] - lon) ** 2).idxmin()
                    selected_map_name = map_df.loc[nearest, "선거구"]
            st.caption("현재 지도는 실제 경계 폴리곤이 아닌 예시 좌표 마커입니다. 실제 제22대 선거구 GeoJSON으로 교체할 예정입니다.")

with chart_col:
    with st.container(border=True):
        st.subheader("차트 영역")
        chart_options = [
            "선거구별 인구 순위",
            "역대 총선별 최대·최소·평균 인구",
            "표의 등가성 지수 분포",
            "주민등록인구와 선거인수 관계",
            "지역별 주민등록인구와 지역구 수 관계",
            "지역구 1석당 주민등록인구"
        ]
        c1, c2 = st.columns(2)
        with c1:
            chart1 = st.selectbox("차트 1 선택", chart_options, index=0, key="chart1")
        with c2:
            chart2 = st.selectbox("차트 2 선택", chart_options, index=1, key="chart2")

        def draw_chart(choice, key_suffix):
            st.markdown(f"**{choice}**")
            if choice == "선거구별 인구 순위":
                if filtered.empty:
                    st.info("표시할 데이터가 없습니다.")
                else:
                    fig = px.bar(filtered.sort_values("주민등록인구", ascending=True),
                                 x="주민등록인구", y="선거구", color="시도",
                                 orientation="h", title="선거구별 주민등록인구(예시 데이터)")
                    fig.update_xaxes(tickformat=",")
                    st.plotly_chart(fig, use_container_width=True, key=f"plot_{key_suffix}")
            elif choice == "역대 총선별 최대·최소·평균 인구":
                fig = go.Figure()
                for col, label in [("최대인구", "최대"), ("최소인구", "최소"), ("평균인구", "평균")]:
                    fig.add_trace(go.Scatter(x=history["연도"], y=history[col], mode="lines+markers", name=label))
                fig.update_layout(title="역대 총선별 선거구 인구 변화(예시 데이터)",
                                  xaxis_title="총선 연도", yaxis_title="인구", yaxis_tickformat=",")
                st.plotly_chart(fig, use_container_width=True, key=f"plot_{key_suffix}")
            elif choice == "표의 등가성 지수 분포":
                if filtered.empty:
                    st.info("표시할 데이터가 없습니다.")
                else:
                    temp = filtered.copy()
                    temp["표의 등가성 지수"] = districts["주민등록인구"].mean() / temp["주민등록인구"]
                    fig = px.histogram(temp, x="표의 등가성 지수", nbins=8,
                                       title="전국 평균 대비 표의 등가성 지수(예시 데이터)")
                    fig.add_vline(x=1, line_dash="dash", line_color="red")
                    st.plotly_chart(fig, use_container_width=True, key=f"plot_{key_suffix}")
            elif choice == "주민등록인구와 선거인수 관계":
                if filtered.empty:
                    st.info("표시할 데이터가 없습니다.")
                else:
                    fig = px.scatter(filtered, x="주민등록인구", y="선거인수",
                                     color="시도", hover_name="선거구",
                                     trendline="ols", title="주민등록인구와 선거인수(예시 데이터)")
                    fig.update_xaxes(tickformat=",")
                    fig.update_yaxes(tickformat=",")
                    st.plotly_chart(fig, use_container_width=True, key=f"plot_{key_suffix}")
            elif choice == "지역별 주민등록인구와 지역구 수 관계":
                fig = px.scatter(regions, x="주민등록인구", y="지역구수",
                                 text="지역", trendline="ols",
                                 title="지역별 주민등록인구와 지역구 수(예시 데이터)")
                fig.update_xaxes(tickformat=",")
                st.plotly_chart(fig, use_container_width=True, key=f"plot_{key_suffix}")
            elif choice == "지역구 1석당 주민등록인구":
                temp = regions.copy()
                temp["1석당 인구"] = temp["주민등록인구"] / temp["지역구수"]
                fig = px.bar(temp.sort_values("1석당 인구"),
                             x="지역", y="1석당 인구",
                             title="지역구 1석당 주민등록인구(예시 데이터)")
                fig.update_yaxes(tickformat=",")
                st.plotly_chart(fig, use_container_width=True, key=f"plot_{key_suffix}")

        draw_chart(chart1, "one")
        st.divider()
        draw_chart(chart2, "two")

# ── 상세정보: 지도 클릭 또는 검색 선택 반영 ──
detail_name = selected_map_name
if selected_district != "전체 선거구":
    detail_name = selected_district
elif not detail_name and not filtered.empty:
    detail_name = filtered.iloc[0]["선거구"]

with st.container(border=True):
    st.subheader("선거구 상세정보")
    if detail_name:
        row = districts[districts["선거구"] == detail_name].iloc[0]
        avg_pop = districts["주민등록인구"].mean()
        index_value = avg_pop / row["주민등록인구"]
        d1, d2, d3, d4 = st.columns(4)
        d1.metric("선거구", row["선거구"])
        d2.metric("주민등록인구", f"{row['주민등록인구']:,.0f}명")
        d3.metric("선거인수", f"{row['선거인수']:,.0f}명")
        d4.metric("표의 등가성 지수", f"{index_value:.3f}")
        st.caption(f"지역: {row['시도']} · 예시 데이터 기준 전국 평균 인구: {avg_pop:,.0f}명")
    else:
        st.info("지역 또는 선거구를 선택하면 상세정보가 표시됩니다.")

with st.expander("현재 사용 중인 예시 데이터 확인"):
    st.dataframe(districts, use_container_width=True)
    st.dataframe(regions, use_container_width=True)
