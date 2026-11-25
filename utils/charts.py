import plotly.express as px
import plotly.graph_objects as go

def history_chart(df):
    fig = go.Figure()
    for col, label in [("최대인구", "최대"), ("최소인구", "최소"), ("평균인구", "평균")]:
        fig.add_trace(go.Scatter(x=df["연도"], y=df[col], mode="lines+markers", name=label))
    fig.update_layout(title="역대 총선별 선거구 인구 변화(예시 데이터)", xaxis_title="총선 연도",
                      yaxis_title="선거구 인구", yaxis_tickformat=",")
    return fig

def population_bar(df, top_n=10):
    view = df.sort_values("주민등록인구", ascending=False).head(top_n)
    fig = px.bar(view.sort_values("주민등록인구"), x="주민등록인구", y="선거구",
                 color="시도", orientation="h", title=f"주민등록인구 상위 {top_n}개(예시 데이터)")
    fig.update_xaxes(tickformat=",")
    return fig

def voter_scatter(df):
    fig = px.scatter(df, x="주민등록인구", y="선거인수", color="시도", hover_name="선거구",
                     trendline="ols", title="주민등록인구와 선거인수의 관계(예시 데이터)")
    fig.update_xaxes(tickformat=",")
    fig.update_yaxes(tickformat=",")
    return fig

def regional_seats_scatter(df):
    fig = px.scatter(df, x="주민등록인구", y="지역구수", text="지역",
                     hover_name="지역", trendline="ols",
                     title="지역별 주민등록인구와 국회의원 지역구 수(예시 데이터)")
    fig.update_traces(textposition="top center")
    fig.update_xaxes(tickformat=",", title="주민등록인구")
    fig.update_yaxes(title="국회의원 지역구 수")
    return fig

def seats_per_population(df):
    view = df.copy()
    view["1석당 인구"] = view["주민등록인구"] / view["지역구수"]
    view = view.sort_values("1석당 인구", ascending=False)
    fig = px.bar(view, x="지역", y="1석당 인구", title="지역구 1석당 주민등록인구(예시 데이터)")
    fig.update_yaxes(tickformat=",")
    return fig
