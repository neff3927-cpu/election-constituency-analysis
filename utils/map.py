import folium
from folium.plugins import Fullscreen

def constituency_demo_map(df, metric="주민등록인구"):
    # 실제 선거구 경계가 아닌 시도 중심 부근의 예시 좌표 마커입니다.
    center = [36.3, 127.8]
    m = folium.Map(location=center, zoom_start=7, tiles="CartoDB positron")
    Fullscreen().add_to(m)
    min_v, max_v = df[metric].min(), df[metric].max()
    for _, row in df.iterrows():
        ratio = (row[metric] - min_v) / (max_v - min_v) if max_v != min_v else 0.5
        color = "#2166ac" if ratio < 0.33 else ("#fdae61" if ratio < 0.66 else "#b2182b")
        popup = (f"<b>{row['선거구']}</b><br>시도: {row['시도']}<br>"
                 f"주민등록인구: {row['주민등록인구']:,}<br>"
                 f"선거인수: {row['선거인수']:,}<br>투표자수: {row['투표자수']:,}")
        folium.CircleMarker(
            location=[row["위도"], row["경도"]], radius=8 + ratio * 10,
            color=color, fill=True, fill_color=color, fill_opacity=0.75,
            tooltip=row["선거구"], popup=folium.Popup(popup, max_width=260)
        ).add_to(m)
    return m
