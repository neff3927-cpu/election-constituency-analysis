from pathlib import Path
import json
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium

HERE = Path(__file__).parent
DATA = HERE / "data"
GEOJSON_URL = "https://raw.githubusercontent.com/OhmyNews/2024_22_elec_map/main/2024_22_Elec_simplify.json"

st.set_page_config(page_title="국회의원 지역구 인구와 표의 등가성 분석", page_icon="🗳️", layout="wide")
st.markdown("""<style>
.block-container{padding-top:1.2rem;padding-bottom:2rem;max-width:1600px}
h1{font-size:2.05rem} h2{font-size:1.45rem}
[data-testid="stVerticalBlockBorderWrapper"]{border-radius:12px}
div[data-testid="stMetric"]{background:#f7f9fc;padding:12px;border-radius:10px}
</style>""", unsafe_allow_html=True)

st.title("국회의원 지역구 인구와 표의 등가성 분석")
st.caption("산업데이터시각화 프로젝트 · 인터랙티브 대시보드")

# ---------- data loading ----------
@st.cache_data

def read_csv(name):
    p=DATA/name
    if not p.exists(): return pd.DataFrame()
    try: return pd.read_csv(p, encoding="utf-8-sig")
    except Exception: return pd.read_csv(p)

@st.cache_data(ttl=86400, show_spinner=False)
def load_geojson():
    import requests
    r=requests.get(GEOJSON_URL,timeout=30); r.raise_for_status()
    g=r.json()
    if g.get("type")!="FeatureCollection" or not g.get("features"): raise ValueError("GeoJSON FeatureCollection이 비어 있습니다.")
    return g

current=read_csv("constituency_population.csv")
pop23=read_csv("constituency_population_23rd.csv")
history_summary=read_csv("election_history_summary.csv")
history_districts=read_csv("historical_constituencies.csv")
region_data=read_csv("region_population_seats.csv")
voters=read_csv("election_voters.csv")

# Demo data is retained for UI testing only; never mixed with official datasets.
demo=read_csv("demo_constituencies.csv")
demo_history=read_csv("demo_history.csv")
demo_regions=read_csv("demo_region_seats.csv")

def has_cols(df, cols): return not df.empty and set(cols).issubset(df.columns)
def clean_num(s): return pd.to_numeric(s,errors="coerce")

# Standardize expected current-district columns.
if has_cols(current,["시도","선거구","주민등록인구"]):
    for c in ["주민등록인구","선거인수","투표자수","이전인구","인구증감률"]:
        if c in current: current[c]=clean_num(current[c])
    for c in ["선거인수","투표자수","이전인구","인구증감률"]:
        if c not in current: current[c]=np.nan
    current["자료구분"]="실제 자료"
else:
    current=pd.DataFrame()

if has_cols(history_summary,["총선","연도","최대인구","최소인구","평균인구"]):
    for c in ["총선","연도","최대인구","최소인구","평균인구"]: history_summary[c]=clean_num(history_summary[c])
else: history_summary=pd.DataFrame()

if has_cols(history_districts,["총선","연도","시도","선거구","주민등록인구"]):
    for c in ["총선","연도","주민등록인구"]: history_districts[c]=clean_num(history_districts[c])
else: history_districts=pd.DataFrame()

if has_cols(region_data,["지역","주민등록인구","지역구수"]):
    region_data["주민등록인구"]=clean_num(region_data["주민등록인구"])
    region_data["지역구수"]=clean_num(region_data["지역구수"])
else: region_data=pd.DataFrame()

if has_cols(voters,["총선","시도","선거구","선거인수","투표자수"]):
    for c in ["총선","선거인수","투표자수"]: voters[c]=clean_num(voters[c])
else: voters=pd.DataFrame()

# ---------- common controls ----------
with st.container(border=True):
    st.subheader("공통 입력 위젯")
    a,b,c=st.columns([1,1,1.35])
    with a: election=st.selectbox("총선 시기 선택",["제22대 총선","제23대 총선 가정","역대 총선 비교"],key="period")
    available_regions=sorted(current["시도"].dropna().astype(str).unique()) if not current.empty else []
    with b: region=st.selectbox("지역 선택",["전체"]+available_regions,key="region")
    available_districts=sorted(current["선거구"].dropna().astype(str).unique()) if not current.empty else []
    with c: district=st.selectbox("선거구 검색",["전체 선거구"]+available_districts,key="district")

use_demo=st.toggle("화면 점검용 예시 데이터 미리보기 (실제 통계 아님)",value=True)
if election=="제23대 총선 가정":
    st.info("제23대는 제22대 선거구 경계를 고정하고 인구수만 갱신하는 가정 분석입니다.")
    if has_cols(pop23,["시도","선거구","주민등록인구"]):
        current=pop23.copy()
        for c in ["주민등록인구","선거인수","투표자수","이전인구"]:
            if c in current: current[c]=clean_num(current[c])
        for c in ["선거인수","투표자수","이전인구"]:
            if c not in current: current[c]=np.nan
        current["자료구분"]="제23대 가정자료"
    else:
        current=pd.DataFrame(columns=["시도","선거구","주민등록인구","선거인수","투표자수","자료구분"])
        st.warning("제23대 가정용 인구자료가 아직 없습니다. data/constituency_population_23rd.csv에 제22대와 동일한 선거구 이름으로 인구만 입력하면 됩니다.")
        use_demo=False
elif current.empty and use_demo and has_cols(demo,["시도","선거구","주민등록인구"]):
    st.warning("현재 화면은 가상 예시자료 미리보기입니다. 실제 통계·분석 결과로 인용하면 안 됩니다.")
    current=demo.copy()
    for c in ["선거인수","투표자수"]:
        if c not in current: current[c]=np.nan
    current["자료구분"]="예시 데이터"

if history_summary.empty and use_demo: history_summary=demo_history.copy()
if region_data.empty and use_demo: region_data=demo_regions.copy()

view=current.copy()
if not view.empty:
    if region!="전체": view=view[view["시도"].astype(str)==region]
    if district!="전체 선거구": view=view[view["선거구"].astype(str)==district]

map_options=["선거구별 주민등록인구","표의 등가성 지수","인접 선거구 인구편차"]
chart_options=[
"선거구별 인구 순위","역대 최대·최소 인구편차 비율","역대 최대·최소·평균 인구 변화",
"역대 선거구 인구분포(Box Plot)","표의 등가성 지수 분포","선거구별 표의 등가성 지수",
"총선별 지수 1 초과·미만 비율","인접 선거구 인구 비교","주민등록인구와 선거인수 관계",
"선거인수 ÷ 주민등록인구 비율","주민등록인구와 투표자수 관계",
"지역별 주민등록인구와 지역구 수 관계","지역구 1석당 주민등록인구",
"인구증감률과 표의 등가성 지수 관계"]

# ---------- derived metrics ----------
def add_equity(df):
    d=df.copy()
    if d.empty: return d
    avg=d["주민등록인구"].mean()
    d["표의 등가성 지수"]=avg/d["주민등록인구"].replace(0,np.nan)
    d["전국 평균 대비 인구편차(%)"]=(d["주민등록인구"]/avg-1)*100
    d["선거인수 비율(%)"]=d["선거인수"]/d["주민등록인구"]*100
    return d
view=add_equity(view)

# ---------- map & charts, equal-height cards ----------
map_col,chart_col=st.columns([1,1],gap="large")
with map_col:
  with st.container(border=True):
    st.header("지도 영역")
    map_metric=st.selectbox("지도 표시 기준 선택",map_options,key="map_metric")
    st.caption("대한민국 제22대 국회의원 지역구 경계 · 선거구 명칭은 마우스를 올리면 확인할 수 있습니다.")
    try:
      geo=load_geojson()
      # Name key in the public GeoJSON is SIDO_SGG (e.g. 서울 종로).
      vals={}
      if not view.empty:
        for _,r in view.iterrows():
          # Actual data should include the exact GeoJSON name; optionally use 지도명 column.
          nm=str(r.get("지도명",r["선거구"]))
          vals[nm]=r.get("주민등록인구",np.nan)
      numeric=[v for v in vals.values() if pd.notna(v)]
      vmin=min(numeric) if numeric else 0; vmax=max(numeric) if numeric else 1
      def color(v):
        if pd.isna(v): return "#e8eef4"
        if vmax==vmin: t=.5
        else: t=(float(v)-vmin)/(vmax-vmin)
        palette=["#eff6ff","#bfdbfe","#60a5fa","#2563eb","#1e3a8a"]
        return palette[min(4,int(t*5))]
      def style(f):
        props=f.get("properties",{}); name=str(props.get("SIDO_SGG", "")); val=vals.get(name,np.nan)
        if map_metric=="표의 등가성 지수" and pd.notna(val) and numeric:
          avg=float(np.mean(numeric)); score=avg/float(val) if float(val)>0 else np.nan
          # Map color is based on relative population; tooltip states the exact metric.
          fill="#dbeafe" if pd.isna(score) else ("#fca5a5" if score<1 else "#93c5fd")
        elif map_metric=="인접 선거구 인구편차": fill="#e8eef4"
        else: fill=color(val)
        return {"fillColor":fill,"color":"#6b879f","weight":0.55,"fillOpacity":0.85}
      m=folium.Map(location=[36.25,127.8],zoom_start=7,tiles=None,control_scale=True,prefer_canvas=True)
      m.fit_bounds([[33.0,124.5],[38.7,131.0]])
      folium.GeoJson(geo,style_function=style,highlight_function=lambda f:{"weight":2,"color":"#102a43","fillOpacity":.95},
        tooltip=folium.GeoJsonTooltip(fields=["SIDO_SGG"],aliases=["선거구:"],sticky=False)).add_to(m)
      st_folium(m,height=790,use_container_width=True,returned_objects=[])
      st.caption("경계: OhmyNews 공개 제22대 선거구 GeoJSON(254개 지역구). 실제 인구자료의 지도명은 GeoJSON의 SIDO_SGG와 일치해야 색상이 연결됩니다.")
      if map_metric=="인접 선거구 인구편차": st.info("인접 선거구 편차 지도는 공유 경계 분석 결과 파일이 연결되면 색상화합니다. 현재 지도는 중립색으로 표시합니다.")
    except Exception as e:
      st.error("선거구 경계를 불러오지 못했습니다. 인터넷 연결 또는 원본 저장소 상태를 확인하세요.")
      st.caption(type(e).__name__)

with chart_col:
  with st.container(border=True):
    st.header("차트 영역")
    x,y=st.columns(2)
    with x: chart1=st.selectbox("차트 1 선택",chart_options,index=0,key="chart1")
    with y: chart2=st.selectbox("차트 2 선택",chart_options,index=2,key="chart2")

    def no_data(msg="이 분석에 필요한 실제 원자료가 아직 연결되지 않았습니다."):
      st.info(msg)
    def render_chart(choice,slot):
      st.markdown(f"**{choice}**")
      fig=None
      if choice=="선거구별 인구 순위":
        if view.empty: return no_data()
        t=view.sort_values("주민등록인구",ascending=False)
        fig=px.bar(t,x="주민등록인구",y="선거구",color="시도",orientation="h",hover_data=["시도"])
        fig.update_yaxes(categoryorder="total ascending"); fig.update_xaxes(title="주민등록인구(명)",tickformat=",")
      elif choice in ["역대 최대·최소 인구편차 비율","역대 최대·최소·평균 인구 변화"]:
        h=history_summary.copy()
        if h.empty: return no_data("총선별 최대·최소·평균 인구를 담은 election_history_summary.csv가 필요합니다.")
        h=h.sort_values("연도").copy()
        if choice=="역대 최대·최소 인구편차 비율":
          h["최대·최소 인구비율"]=h["최대인구"]/h["최소인구"].replace(0,np.nan)
          fig=px.line(h,x="연도",y="최대·최소 인구비율",markers=True)
          fig.add_hline(y=2,line_dash="dash",line_color="gray",annotation_text="2:1 기준(참고선; 과거 법 적용과 동일시 금지)")
          fig.update_yaxes(title="최대 인구 ÷ 최소 인구(배)")
        else:
          fig=go.Figure()
          for col,label in [("최대인구","최대"),("최소인구","최소"),("평균인구","평균")]: fig.add_trace(go.Scatter(x=h["연도"],y=h[col],mode="lines+markers",name=label))
          fig.update_layout(xaxis_title="총선 연도",yaxis_title="인구(명)",yaxis_tickformat=",")
      elif choice=="역대 선거구 인구분포(Box Plot)":
        if history_districts.empty: return no_data("총선·연도·시도·선거구·주민등록인구 열이 있는 historical_constituencies.csv가 필요합니다.")
        fig=px.box(history_districts,x="총선",y="주민등록인구",color="총선",points="outliers",hover_data=["시도","선거구"])
        fig.update_yaxes(title="선거구 인구(명)",tickformat=",")
      elif choice in ["표의 등가성 지수 분포","선거구별 표의 등가성 지수"]:
        if view.empty or "표의 등가성 지수" not in view: return no_data()
        if choice=="표의 등가성 지수 분포":
          fig=px.histogram(view,x="표의 등가성 지수",nbins=15,color_discrete_sequence=["#2878b5"])
          fig.add_vline(x=1,line_dash="dash",line_color="red",annotation_text="전국 평균=1")
        else:
          t=view.sort_values("표의 등가성 지수")
          fig=px.bar(t,x="표의 등가성 지수",y="선거구",color="시도",orientation="h")
          fig.add_vline(x=1,line_dash="dash",line_color="red")
          fig.update_yaxes(categoryorder="total ascending")
      elif choice=="총선별 지수 1 초과·미만 비율":
        if history_districts.empty: return no_data("총선별 선거구 단위 인구 원자료가 필요합니다.")
        h=history_districts.copy(); h["평균인구"]=h.groupby("총선")["주민등록인구"].transform("mean"); h["지수"]=h["평균인구"]/h["주민등록인구"]
        h["분류"]=np.select([h["지수"]>1,h["지수"]<1],["1 초과(평균보다 인구 적음)","1 미만(평균보다 인구 많음)"],default="1")
        p=pd.crosstab(h["총선"],h["분류"],normalize="index").mul(100).reset_index().melt(id_vars="총선",var_name="분류",value_name="비율")
        fig=px.bar(p,x="총선",y="비율",color="분류",barmode="stack")
        fig.update_yaxes(title="선거구 비율(%)",range=[0,100])
      elif choice=="인접 선거구 인구 비교":
        adj=read_csv("adjacency_population.csv")
        if not has_cols(adj,["선거구","인접선거구","선거구인구","인접선거구인구"]): return no_data("adjacency_population.csv에 선거구·인접선거구·양쪽 인구 열이 필요합니다.")
        selected= district if district!="전체 선거구" else (view.iloc[0]["선거구"] if not view.empty else None)
        t=adj[adj["선거구"]==selected]
        if t.empty: return no_data("선택 선거구의 인접 관계 데이터가 없습니다.")
        long=pd.concat([pd.DataFrame({"구분":t["선거구"],"인구":t["선거구인구"]}),pd.DataFrame({"구분":t["인접선거구"],"인구":t["인접선거구인구"]})])
        fig=px.bar(long,x="인구",y="구분",orientation="h",color="구분")
      elif choice in ["주민등록인구와 선거인수 관계","선거인수 ÷ 주민등록인구 비율","주민등록인구와 투표자수 관계"]:
        t=view.dropna(subset=["주민등록인구"]).copy() if not view.empty else pd.DataFrame()
        if choice=="주민등록인구와 선거인수 관계":
          t=t.dropna(subset=["선거인수"])
          if t.empty:return no_data("선거인수 열이 실제 자료에 있어야 합니다.")
          fig=px.scatter(t,x="주민등록인구",y="선거인수",color="시도",hover_name="선거구",trendline="ols")
          fig.update_yaxes(title="선거인수(명)",tickformat=",")
        elif choice=="선거인수 ÷ 주민등록인구 비율":
          t=t.dropna(subset=["선거인수"])
          if t.empty:return no_data("선거인수 열이 실제 자료에 있어야 합니다.")
          t["선거인수 비율(%)"]=t["선거인수"]/t["주민등록인구"]*100
          fig=px.bar(t.sort_values("선거인수 비율(%)"),x="선거인수 비율(%)",y="선거구",color="시도",orientation="h")
          fig.update_yaxes(categoryorder="total ascending")
        else:
          t=t.dropna(subset=["투표자수"])
          if t.empty:return no_data("투표자수 열이 실제 자료에 있어야 합니다.")
          fig=px.scatter(t,x="주민등록인구",y="투표자수",color="시도",hover_name="선거구",trendline="ols")
          fig.update_yaxes(title="투표자수(명)",tickformat=",")
        fig.update_xaxes(title="주민등록인구(명)",tickformat=",")
      elif choice in ["지역별 주민등록인구와 지역구 수 관계","지역구 1석당 주민등록인구"]:
        if region_data.empty:return no_data("region_population_seats.csv의 실제 시도별 인구·지역구 의석 자료가 필요합니다.")
        t=region_data.copy()
        if choice=="지역별 주민등록인구와 지역구 수 관계":
          fig=px.scatter(t,x="주민등록인구",y="지역구수",text="지역",trendline="ols")
          fig.update_traces(textposition="top center"); fig.update_yaxes(title="지역구 의석수(석)")
        else:
          t["1석당 인구"]=t["주민등록인구"]/t["지역구수"].replace(0,np.nan)
          fig=px.bar(t.sort_values("1석당 인구"),x="지역",y="1석당 인구")
          fig.update_yaxes(title="지역구 1석당 인구(명)",tickformat=",")
        fig.update_xaxes(title="주민등록인구(명)",tickformat=",")
      elif choice=="인구증감률과 표의 등가성 지수 관계":
        if view.empty or view["이전인구"].isna().all():return no_data("현재 인구와 동일한 공간 범위의 이전 인구가 필요합니다. 경계가 달라진 경우 읍면동 단위로 재집계해야 합니다.")
        t=view.dropna(subset=["이전인구","주민등록인구"]).copy(); t["인구증감률(%)"]=(t["주민등록인구"]/t["이전인구"]-1)*100
        t["표의 등가성 지수"]=t["주민등록인구"].mean()/t["주민등록인구"]
        fig=px.scatter(t,x="인구증감률(%)",y="표의 등가성 지수",color="시도",hover_name="선거구",trendline="ols")
        fig.add_hline(y=1,line_dash="dash",line_color="gray")
      if fig is not None:
        fig.update_layout(height=330,margin=dict(l=8,r=8,t=35,b=8),legend_title_text="")
        st.plotly_chart(fig,use_container_width=True,key=slot)
    render_chart(chart1,"chart_1")
    st.divider()
    render_chart(chart2,"chart_2")

# ---------- detail card ----------
st.divider()
st.header("선거구 상세정보")
if not view.empty:
    chosen=district if district!="전체 선거구" else str(view.iloc[0]["선거구"])
    row=view[view["선거구"].astype(str)==chosen].iloc[0]
    avg=float(view["주민등록인구"].mean())
    d1,d2,d3,d4=st.columns(4)
    d1.metric("선거구",chosen); d2.metric("주민등록인구",f"{row['주민등록인구']:,.0f}명")
    d3.metric("선거인수",f"{row['선거인수']:,.0f}명" if pd.notna(row['선거인수']) else "자료 없음")
    d4.metric("표의 등가성 지수",f"{avg/row['주민등록인구']:.3f}" if row['주민등록인구'] else "계산 불가")
    rank=int(current["주민등록인구"].rank(ascending=False,method="min")[current.index[current["선거구"].astype(str)==chosen][0]]) if len(current)>0 else None
    st.caption(f"시도: {row['시도']} · 전국 인구 순위: {rank if rank else '자료 없음'}위 · 자료 구분: {row['자료구분']}")
else: st.info("실제 선거구 인구 CSV를 연결하면 상세정보가 표시됩니다.")

with st.expander("데이터 파일 형식 및 출처"):
    st.markdown("""**실제 데이터 파일은 `data/` 폴더의 CSV 서식에 맞춰 넣어주세요.**
- `constituency_population.csv`: 시도, 선거구, 주민등록인구, 선거인수, 투표자수, 위도, 경도, 지도명, 이전인구
- `election_history_summary.csv`: 총선, 연도, 최대인구, 최소인구, 평균인구
- `historical_constituencies.csv`: 총선, 연도, 시도, 선거구, 주민등록인구
- `region_population_seats.csv`: 지역, 주민등록인구, 지역구수
- `election_voters.csv`: 총선, 시도, 선거구, 선거인수, 투표자수

지도 경계: [OhmyNews 제22대 선거구 GeoJSON](https://github.com/OhmyNews/2024_22_elec_map) · 선거인수 API: [공공데이터포털 중앙선거관리위원회 선거인수 정보](https://www.data.go.kr/data/15094967/openapi.do) · 인구: [행정안전부 주민등록 인구통계](https://jumin.mois.go.kr/)

**주의:** 표의 등가성 지수는 `전국 평균 선거구 인구 ÷ 해당 선거구 인구`로 계산한 주민등록인구 기준 상대지표이며 실제 투표 영향력을 직접 측정하지 않습니다. 지역별 의석수 분석도 법적 위법 여부 판정이 아닌 인구비례성 탐색입니다.""")
with st.expander("화면 점검용 예시 데이터 보기"):
    st.caption("예시자료는 기능 확인용 가상 데이터이며 연구 결과·발표 근거로 사용하면 안 됩니다.")
    if not demo.empty: st.dataframe(demo,use_container_width=True)
    if not demo_history.empty: st.dataframe(demo_history,use_container_width=True)
