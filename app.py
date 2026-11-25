from pathlib import Path
import json
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium

BASE = Path(__file__).parent
DATA = BASE / "data"
GEOJSON_URL = "https://raw.githubusercontent.com/OhmyNews/2024_22_elec_map/main/2024_22_Elec_simplify.json"
FILES = {
    "constituency_population.csv": "제22대 선거구별 인구·선거인수",
    "constituency_population_23rd.csv": "제23대 가정용 인구(제22대 경계 고정)",
    "election_history_summary.csv": "역대 총선별 최대·최소·평균 인구",
    "historical_constituencies.csv": "역대 총선 선거구별 인구",
    "adjacency_population.csv": "인접 선거구 인구 관계",
    "region_population_seats.csv": "시도별 주민등록인구·지역구 수",
    "election_voters.csv": "역대 총선 선거인수·투표자수",
}

st.set_page_config(page_title="국회의원 지역구 인구와 표의 등가성 분석", page_icon="🗳️", layout="wide")
st.markdown("""<style>
.block-container{padding-top:1.1rem;padding-bottom:2rem;max-width:1800px}
h1{font-size:2rem} h2{font-size:1.45rem}
[data-testid="stVerticalBlockBorderWrapper"]{border-radius:12px}
div[data-testid="stMetric"]{background:#f5f8fc;padding:12px;border-radius:10px}
</style>""", unsafe_allow_html=True)
st.title("국회의원 지역구 인구와 표의 등가성 분석")
st.caption("산업데이터시각화 프로젝트 · 인터랙티브 대시보드")
st.warning("자료가 연결되지 않은 분석은 임의의 숫자로 채우지 않습니다. 실제 CSV를 추가하면 해당 차트와 지도 색상이 자동으로 갱신됩니다.")

@st.cache_data

def read_local(name):
    p=DATA/name
    if not p.exists(): return pd.DataFrame()
    try: d=pd.read_csv(p,encoding="utf-8-sig")
    except Exception: d=pd.read_csv(p)
    d.columns=[str(c).replace("\ufeff","").strip() for c in d.columns]
    aliases={"시도명":"시도","지역명":"지역","인구수":"주민등록인구","주민등록인구(명)":"주민등록인구","선거인 수":"선거인수","투표자 수":"투표자수","지역구 수":"지역구수","인접 선거구":"인접선거구","선거구 인구":"선거구인구","인접 선거구 인구":"인접선거구인구"}
    return d.rename(columns={k:v for k,v in aliases.items() if k in d.columns and v not in d.columns})

@st.cache_data(ttl=86400,show_spinner=False)
def load_geo():
    import requests
    r=requests.get(GEOJSON_URL,timeout=25); r.raise_for_status()
    j=r.json()
    if not j.get("features"): raise ValueError("GeoJSON에 feature가 없습니다")
    return j

def num(s): return pd.to_numeric(s,errors="coerce")
def valid(d,cols): return not d.empty and all(c in d.columns for c in cols)
def load_data(name):
    # 업로드된 파일은 현재 세션에서 로컬 파일보다 우선 적용
    return st.session_state.get("uploaded_"+name, read_local(name))

def clean(d):
    d=d.copy(); d.columns=[str(c).replace("\ufeff","").strip() for c in d.columns]
    aliases={"시도명":"시도","인구수":"주민등록인구","주민등록인구(명)":"주민등록인구","선거인 수":"선거인수","투표자 수":"투표자수","지역명":"지역","지역구 수":"지역구수"}
    d=d.rename(columns={k:v for k,v in aliases.items() if k in d.columns and v not in d.columns})
    return d

with st.expander("실제 데이터 CSV 업로드 / 연결",expanded=False):
    st.markdown("파일을 업로드하면 이 세션에서 즉시 분석에 반영됩니다. 계속 보존하려면 같은 파일을 GitHub 저장소의 `data/` 폴더에도 올려주세요.")
    uploads=st.file_uploader("CSV 파일 여러 개 선택 가능",type=["csv"],accept_multiple_files=True,key="csv_uploads")
    if uploads:
        for f in uploads:
            try:
                d=pd.read_csv(f,encoding="utf-8-sig"); st.session_state["uploaded_"+f.name]=clean(d)
            except Exception as e: st.error(f"{f.name} 읽기 실패: {e}")
        st.success(f"{len(uploads)}개 파일을 현재 세션에 반영했습니다.")
    st.caption("필수 파일명: "+" · ".join(FILES.keys()))

current=clean(load_data("constituency_population.csv"))
pop23=clean(load_data("constituency_population_23rd.csv"))
hist=clean(load_data("election_history_summary.csv"))
hist_d=clean(load_data("historical_constituencies.csv"))
adj=clean(load_data("adjacency_population.csv"))
regions=clean(load_data("region_population_seats.csv"))

# 숫자형 열 정리
for frame, cols in [(current,["주민등록인구","선거인수","투표자수","이전인구","인구증감률"]),(pop23,["주민등록인구","선거인수","투표자수","이전인구"]),(hist,["연도","최대인구","최소인구","평균인구"]),(hist_d,["총선","연도","주민등록인구"]),(regions,["주민등록인구","지역구수"]),(adj,["선거구인구","인접선거구인구"])]:
    for c in cols:
        if c in frame: frame[c]=num(frame[c])

# 공통 조건
with st.container(border=True):
    st.subheader("공통 입력 위젯")
    c1,c2,c3=st.columns([1,1,1.4])
    with c1: election=st.selectbox("총선 시기 선택",["제22대 총선","제23대 총선 가정","역대 총선 비교"],key="election")
    source=current
    if election=="제23대 총선 가정": source=pop23
    available_regions=sorted(source["시도"].dropna().astype(str).unique()) if valid(source,["시도"]) else []
    with c2: region=st.selectbox("지역 선택",["전체"]+available_regions,key="region")
    available_districts=sorted(source["선거구"].dropna().astype(str).unique()) if valid(source,["선거구"]) else []
    with c3: district=st.selectbox("선거구 검색",["전체 선거구"]+available_districts,key="district")

if election=="역대 총선 비교":
    view=pd.DataFrame()
else:
    view=source.copy()
    if not view.empty:
        if region!="전체" and "시도" in view: view=view[view["시도"].astype(str)==region]
        if district!="전체 선거구" and "선거구" in view: view=view[view["선거구"].astype(str)==district]

if election=="제23대 총선 가정":
    st.info("제23대 총선 가정은 제22대 선거구 경계를 그대로 두고 인구만 바꾸어 보는 시나리오입니다. 실제 선거구 획정 결과가 아닙니다.")

map_options=["선거구별 주민등록인구","표의 등가성 지수","인접 선거구 인구편차"]
chart_options=["역대 최대·최소 인구편차 비율","역대 최대·최소·평균 인구 변화","선거구별 인구 순위","인접 선거구 인구 비교","표의 등가성 지수 분포","총선별 지수 1 초과·미만 비율","주민등록인구와 선거인수 관계","지역별 주민등록인구와 지역구 수 관계"]

# 현재 선택자료 기준 지표
if valid(view,["주민등록인구"]):
    view["주민등록인구"]=num(view["주민등록인구"])
    avg=view["주민등록인구"].mean()
    view["표의 등가성 지수"]=avg/view["주민등록인구"].replace(0,np.nan)
else: avg=np.nan

left,right=st.columns([1,1],gap="large")
with left:
    with st.container(border=True):
        st.header("지도 영역")
        map_metric=st.selectbox("지도 표시 기준 선택",map_options,key="map_metric")
        st.caption("제22대 국회의원 지역구 경계 · 선거구 명칭은 마우스를 올리면 확인할 수 있습니다.")
        try:
            geo=load_geo()
            # GeoJSON 속성의 선거구 식별자와 CSV의 지도명(우선), 선거구명을 매칭
            lookup={}
            if valid(view,["선거구","주민등록인구"]):
                for _,r in view.iterrows():
                    v=r.get("주민등록인구",np.nan)
                    for key in [r.get("지도명",None),r.get("선거구",None)]:
                        if pd.notna(key) and str(key).strip(): lookup[str(key).strip()]=v
            def coords_walk(obj,out):
                if isinstance(obj,(list,tuple)):
                    if len(obj)>=2 and isinstance(obj[0],(int,float)) and isinstance(obj[1],(int,float)):
                        out.append((float(obj[0]),float(obj[1])))
                    else:
                        for x in obj: coords_walk(x,out)
            pts=[]
            for ft in geo["features"]: coords_walk(ft.get("geometry",{}).get("coordinates",[]),pts)
            if not pts: raise ValueError("경계 좌표를 확인할 수 없습니다")
            xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
            # 경계 GeoJSON은 경위도 좌표여야 함. 대한민국 범위 밖이면 데이터 오류로 중단.
            if not (120<min(xs)<max(xs)<135 and 30<min(ys)<max(ys)<45): raise ValueError("GeoJSON 좌표계가 경위도(EPSG:4326)가 아닙니다")
            vals=[v for v in lookup.values() if pd.notna(v)]
            lo=min(vals) if vals else 0; hi=max(vals) if vals else 1
            def get_name(ft):
                p=ft.get("properties",{})
                for k in ["SIDO_SGG","SGG_NM","SIG_KOR_NM","NAME","name"]:
                    if p.get(k): return str(p[k])
                return "선거구"
            def style(ft):
                nm=get_name(ft); value=lookup.get(nm,np.nan)
                if pd.isna(value): fill="#e8eef4"
                elif map_metric=="표의 등가성 지수":
                    score=avg/value if value else np.nan
                    fill="#2563eb" if pd.notna(score) and score>1 else "#ef4444"
                elif map_metric=="인접 선거구 인구편차": fill="#e8eef4"
                else:
                    t=(value-lo)/(hi-lo) if hi>lo else .5
                    colors=["#eff6ff","#bfdbfe","#60a5fa","#2563eb","#1e3a8a"]
                    fill=colors[min(4,max(0,int(t*5)))]
                return {"fillColor":fill,"color":"#6f8da7","weight":0.6,"fillOpacity":0.88}
            m=folium.Map(location=[36.3,127.8],zoom_start=6,tiles=None,control_scale=False,prefer_canvas=True)
            folium.GeoJson(geo,name="제22대 지역구",style_function=style,highlight_function=lambda f:{"weight":2,"color":"#172b4d","fillOpacity":1},tooltip=folium.GeoJsonTooltip(fields=[next((k for k in ["SIDO_SGG","SGG_NM","SIG_KOR_NM","NAME","name"] if k in geo["features"][0].get("properties",{})),list(geo["features"][0].get("properties",{}).keys())[0])],aliases=["선거구:"])).add_to(m)
            m.fit_bounds([[min(ys),min(xs)],[max(ys),max(xs)]],padding=(12,12))
            st_folium(m,height=610,use_container_width=True,returned_objects=[])
            st.caption("지도 경계: 제22대 선거구 GeoJSON. 인구 색상은 CSV의 지도명 또는 선거구명이 GeoJSON 속성과 일치하는 경우에만 표시됩니다.")
            if not vals: st.info("경계는 표시 중입니다. 실제 선거구 인구 CSV를 연결하면 선거구별 색상이 표시됩니다.")
            if map_metric=="인접 선거구 인구편차": st.info("인접 선거구 관계 CSV를 연결하면 인접 평균 대비 편차를 색상으로 표시하도록 확장할 수 있습니다.")
        except Exception as e:
            st.error("선거구 지도를 불러오지 못했습니다. GeoJSON 주소 또는 좌표계를 확인해 주세요.")
            st.caption(f"오류 유형: {type(e).__name__} — {e}")

with right:
    with st.container(border=True):
        st.header("차트 영역")
        q1,q2=st.columns(2)
        with q1: ch1=st.selectbox("차트 1 선택",chart_options,index=0,key="chart1")
        with q2: ch2=st.selectbox("차트 2 선택",chart_options,index=1,key="chart2")
        def missing(msg): st.info(msg)
        def chart(choice,key):
            st.markdown(f"**{choice}**")
            fig=None
            if choice=="역대 최대·최소 인구편차 비율":
                if not valid(hist,["연도","최대인구","최소인구"]): return missing("election_history_summary.csv에 총선별 연도·최대인구·최소인구가 필요합니다.")
                h=hist.dropna(subset=["연도","최대인구","최소인구"]).sort_values("연도").copy()
                h["최대·최소 인구비율"]=h["최대인구"]/h["최소인구"].replace(0,np.nan)
                fig=px.line(h,x="연도",y="최대·최소 인구비율",markers=True,hover_data=["최대인구","최소인구"])
                fig.update_yaxes(title="최대 인구 ÷ 최소 인구(배)")
                if len(h)>=2: fig.add_hline(y=2,line_dash="dash",line_color="gray",annotation_text="2:1 참고선")
                else: st.caption("현재 등록된 총선 자료가 1개이므로 추세 비교는 불가능합니다.")
            elif choice=="역대 최대·최소·평균 인구 변화":
                if not valid(hist,["연도","최대인구","최소인구","평균인구"]): return missing("election_history_summary.csv에 총선별 최대·최소·평균 인구가 필요합니다.")
                h=hist.dropna(subset=["연도"]).sort_values("연도")
                fig=go.Figure()
                for c,n in [("최대인구","최대"),("최소인구","최소"),("평균인구","평균")]: fig.add_trace(go.Scatter(x=h["연도"],y=h[c],mode="lines+markers",name=n))
                fig.update_layout(xaxis_title="총선 연도",yaxis_title="인구(명)",yaxis_tickformat=",")
                if len(h)<2: st.caption("현재 등록된 총선 자료가 1개입니다. 역대 자료를 추가하면 변화 추세가 나타납니다.")
            elif choice=="선거구별 인구 순위":
                if not valid(view,["선거구","주민등록인구"]): return missing("constituency_population.csv에 선거구별 주민등록인구가 필요합니다.")
                t=view.dropna(subset=["주민등록인구"]).sort_values("주민등록인구",ascending=False)
                if t.empty:return missing("표시할 인구 데이터가 없습니다.")
                fig=px.bar(t,x="주민등록인구",y="선거구",color="시도" if "시도" in t else None,orientation="h",hover_data=[c for c in ["시도","선거인수"] if c in t])
                fig.update_yaxes(categoryorder="total ascending"); fig.update_xaxes(title="주민등록인구(명)",tickformat=",")
            elif choice=="인접 선거구 인구 비교":
                if not valid(adj,["선거구","인접선거구","선거구인구","인접선거구인구"]): return missing("adjacency_population.csv에 선거구·인접선거구·양쪽 인구 열을 연결해 주세요.")
                selected=district if district!="전체 선거구" else (str(view.iloc[0]["선거구"]) if valid(view,["선거구"]) else "")
                t=adj[adj["선거구"].astype(str)==selected]
                if t.empty:return missing("선택한 선거구의 인접 선거구 데이터가 없습니다.")
                long=pd.concat([pd.DataFrame({"선거구":t["선거구"],"인구":t["선거구인구"]}),pd.DataFrame({"선거구":t["인접선거구"],"인구":t["인접선거구인구"]})]).dropna()
                fig=px.bar(long,x="인구",y="선거구",orientation="h",color="선거구")
            elif choice=="표의 등가성 지수 분포":
                if not valid(view,["표의 등가성 지수"]):return missing("선거구별 주민등록인구 자료가 있어야 지수를 계산할 수 있습니다.")
                fig=px.histogram(view.dropna(subset=["표의 등가성 지수"]),x="표의 등가성 지수",nbins=20)
                fig.add_vline(x=1,line_dash="dash",line_color="red",annotation_text="전국 평균=1")
            elif choice=="총선별 지수 1 초과·미만 비율":
                if not valid(hist_d,["총선","주민등록인구"]):return missing("historical_constituencies.csv에 역대 총선별 선거구 인구 원자료가 필요합니다.")
                h=hist_d.dropna(subset=["총선","주민등록인구"]).copy(); h["평균인구"]=h.groupby("총선")["주민등록인구"].transform("mean"); h["지수"]=h["평균인구"]/h["주민등록인구"].replace(0,np.nan)
                h["분류"]=np.select([h["지수"]>1,h["지수"]<1],["1 초과(평균보다 인구 적음)","1 미만(평균보다 인구 많음)"],default="1")
                p=pd.crosstab(h["총선"],h["분류"],normalize="index").mul(100).reset_index().melt(id_vars="총선",var_name="분류",value_name="비율")
                fig=px.bar(p,x="총선",y="비율",color="분류",barmode="stack"); fig.update_yaxes(title="선거구 비율(%)",range=[0,100])
            elif choice=="주민등록인구와 선거인수 관계":
                if not valid(view,["주민등록인구","선거인수"]):return missing("선거구별 주민등록인구와 선거인수 열이 모두 필요합니다.")
                t=view.dropna(subset=["주민등록인구","선거인수"])
                if t.empty:return missing("선거인수 자료가 아직 없습니다. CSV에 선거인수 열을 추가해 주세요.")
                fig=px.scatter(t,x="주민등록인구",y="선거인수",color="시도" if "시도" in t else None,hover_name="선거구" if "선거구" in t else None,trendline="ols" if len(t)>=3 else None)
                fig.update_xaxes(title="주민등록인구(명)",tickformat=","); fig.update_yaxes(title="선거인수(명)",tickformat=",")
            elif choice=="지역별 주민등록인구와 지역구 수 관계":
                if not valid(regions,["지역","주민등록인구","지역구수"]):return missing("region_population_seats.csv에 시도별 주민등록인구와 지역구수를 입력해 주세요.")
                t=regions.dropna(subset=["주민등록인구","지역구수"])
                if len(t)<3:return missing("시도별 주민등록인구 값이 비어 있습니다. 같은 기준일의 공식 인구를 입력해 주세요.")
                fig=px.scatter(t,x="주민등록인구",y="지역구수",text="지역",trendline="ols")
                fig.update_traces(textposition="top center"); fig.update_xaxes(title="주민등록인구(명)",tickformat=","); fig.update_yaxes(title="지역구 의석수(석)")
            if fig is not None:
                fig.update_layout(height=340,margin=dict(l=8,r=8,t=30,b=8),legend_title_text="")
                st.plotly_chart(fig,use_container_width=True,key=key)
        chart(ch1,"plot_a"); st.divider(); chart(ch2,"plot_b")

st.divider(); st.header("선거구 상세정보")
if valid(view,["선거구","주민등록인구"]) and not view.dropna(subset=["주민등록인구"]).empty:
    chosen=district if district!="전체 선거구" else str(view.iloc[0]["선거구"])
    row=view[view["선거구"].astype(str)==chosen].iloc[0]
    c1,c2,c3,c4=st.columns(4)
    c1.metric("선거구",chosen); c2.metric("주민등록인구",f"{row['주민등록인구']:,.0f}명")
    c3.metric("선거인수",f"{row['선거인수']:,.0f}명" if "선거인수" in row and pd.notna(row["선거인수"]) else "자료 없음")
    c4.metric("표의 등가성 지수",f"{row['표의 등가성 지수']:.3f}" if pd.notna(row.get("표의 등가성 지수",np.nan)) else "계산 불가")
    st.caption(f"시도: {row.get('시도','자료 없음')} · 자료 기준: {election}")
else: st.info("실제 선거구별 인구 CSV를 연결하면 상세정보가 표시됩니다.")

with st.expander("CSV 열 구성 및 데이터 출처"):
    st.markdown("""| 파일 | 필수 열 |
|---|---|
| `constituency_population.csv` | 시도, 선거구, 주민등록인구, 선거인수, 투표자수, 지도명 |
| `constituency_population_23rd.csv` | 시도, 선거구, 주민등록인구 (제22대 선거구명 유지) |
| `election_history_summary.csv` | 총선, 연도, 최대인구, 최소인구, 평균인구 |
| `historical_constituencies.csv` | 총선, 연도, 시도, 선거구, 주민등록인구 |
| `adjacency_population.csv` | 선거구, 인접선거구, 선거구인구, 인접선거구인구 |
| `region_population_seats.csv` | 지역, 주민등록인구, 지역구수 |

**공식 자료 출처**: [행정안전부 주민등록 인구통계](https://jumin.mois.go.kr/) · [중앙선거관리위원회 선거통계시스템](https://info.nec.go.kr/) · [공공데이터포털](https://www.data.go.kr/) · [제22대 선거구 경계 GeoJSON](https://github.com/OhmyNews/2024_22_elec_map)

표의 등가성 지수 = 전국 평균 선거구 인구 ÷ 해당 선거구 인구. 주민등록인구 기준 상대지표이며 실제 투표 영향력을 직접 측정하는 지표는 아닙니다. 제23대 총선 가정은 제22대 경계를 고정한 시나리오입니다.""")
