# 국회의원 지역구 인구와 표의 등가성 분석

## 실행
```bash
pip install -r requirements.txt
streamlit run app.py
```

현재 CSV는 화면과 위젯 동작을 확인하기 위한 임의의 예시 데이터입니다.
실제 분석·발표 전 행정안전부, 중앙선거관리위원회 등 공식 공개자료로 교체해야 합니다.

## 데이터 파일
- data/demo_constituencies.csv
- data/demo_history.csv
- data/demo_region_seats.csv

제23대 총선 가정은 제22대 경계를 고정하고 인구 기준일을 갱신하는 분석 설계입니다.
실제 제23대 선거구 획정 결과로 표시하지 않습니다.
