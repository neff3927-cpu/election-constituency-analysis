# 국회의원 지역구 인구와 표의 등가성 분석 — v9

## 실행
```bash
pip install -r requirements.txt
streamlit run app.py
```

## 이번 버전
- 지도: 제22대 총선 254개 실제 선거구 GeoJSON, CartoDB Positron 바탕지도 적용, GeoJSON 실제 경계 범위로 자동 확대/축소
- 차트: 최대·최소 인구편차, 최대·최소·평균 변화, Box Plot, 표의 등가성 지수, 지수 1 초과·미만 비율, 선거인수·투표자수 회귀, 지역별 의석 배분, 인구증감률 등
- 지도/차트는 동일한 높이의 좌우 패널로 구성
- 실제 데이터 CSV와 예시 데이터 분리
- 제23대는 제22대 경계 고정 가정으로 설계

## 중요: 데이터 연결 상태
현재 `constituency_population.csv` 등은 헤더만 있는 실제 데이터 입력용 서식입니다. `demo_*.csv`는 기존 화면 점검용 가상 데이터입니다. 실제 데이터가 들어오기 전까지 예시자료로 계산된 결과를 연구 결과로 인용하지 마세요.

## 실제 데이터 CSV 규격
- `data/constituency_population.csv`: `시도,선거구,주민등록인구,선거인수,투표자수,위도,경도,지도명,이전인구`
- `data/election_history_summary.csv`: `총선,연도,최대인구,최소인구,평균인구`
- `data/historical_constituencies.csv`: `총선,연도,시도,선거구,주민등록인구`
- `data/region_population_seats.csv`: `지역,주민등록인구,지역구수`
- `data/election_voters.csv`: `총선,시도,선거구,선거인수,투표자수`
- `data/adjacency_population.csv`: `선거구,인접선거구,선거구인구,인접선거구인구`

`지도명`은 GeoJSON 속성 `SIDO_SGG`와 일치시켜야 지도에 인구 색상이 연결됩니다. 선거구 이름만으로 자동 매칭하지 않습니다.

## 자료 출처
- 제22대 선거구 경계: https://github.com/OhmyNews/2024_22_elec_map
- 주민등록인구: https://jumin.mois.go.kr/
- 중앙선거관리위원회 선거인수 정보: https://www.data.go.kr/data/15094967/openapi.do
- 공공데이터포털: https://www.data.go.kr/

## 지표 해석 주의
표의 등가성 지수 = 전국 평균 선거구 인구 ÷ 해당 선거구 인구. 주민등록인구 기준 상대지표이며 실제 투표 영향력을 직접 측정하지 않습니다. 지역별 의석수 분석은 인구비례성 탐색이며 법적 위법 판정이 아닙니다. 과거 선거구 비교는 해당 총선 당시 경계와 인구를 함께 사용해야 합니다.


## v9 화면 수정
- 지도 바탕이 회색으로 비어 보이던 문제를 해결하기 위해 타일 배경을 추가했습니다.
- 고정된 임의 좌표 범위 대신 GeoJSON 경계 자체의 bounds로 자동 fit합니다.
- 지도 높이를 640px로 조정했습니다.
- 예시 데이터 미리보기 기본값을 OFF로 변경했습니다. 실제 데이터가 없는 상태에서 가상 수치가 기본 화면에 노출되지 않습니다.
- `data/README_data_sources.md`에 각 CSV의 입력 열과 기준일 주의사항을 정리했습니다.
