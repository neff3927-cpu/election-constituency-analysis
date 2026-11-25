# 데이터 입력 안내

이 폴더의 CSV는 실제 원자료를 넣기 위한 빈 템플릿입니다. 데이터가 입력되기 전에는 차트 및 지도 색상 분석이 표시되지 않습니다.

## 제22대 선거구 인구
`constituency_population.csv` 열: 시도, 선거구, 주민등록인구, 선거인수, 투표자수, 위도, 경도, 지도명, 이전인구
- 주민등록인구는 제22대 획정 기준일에 맞는 자료인지 확인하세요.
- 지도명은 GeoJSON의 `SIDO_SGG` 값과 정확히 일치해야 합니다.

## 제23대 가정 인구
`constituency_population_23rd.csv`는 제22대 선거구 경계를 유지하고 인구만 갱신하는 가정 분석용입니다. 실제 확정 선거구 자료가 아닙니다.

## 역대 총선
`historical_constituencies.csv`: 총선, 연도, 시도, 선거구, 주민등록인구
`election_history_summary.csv`: 총선, 연도, 최대인구, 최소인구, 평균인구
각 총선 당시의 선거구 경계와 기준일 인구를 사용해야 합니다.

## 선거인수 및 투표자수
`election_voters.csv`: 총선, 시도, 선거구, 선거인수, 투표자수
선거인수와 주민등록인구는 기준일과 모집단이 다르므로 구분해서 설명하세요.

## 지역별 인구 및 의석
`region_population_seats.csv`: 지역, 주민등록인구, 지역구수
광역시·도 단위 분석을 우선 권장합니다.

## 인접 선거구
`adjacency_population.csv`: 선거구, 인접선거구, 선거구인구, 인접선거구인구
공유 경계 등 인접 기준을 정한 후 작성하세요.

## 출처
- 행정안전부 주민등록 인구통계: https://jumin.mois.go.kr/
- 중앙선거관리위원회 선거통계: https://info.nec.go.kr/
- 공공데이터포털: https://www.data.go.kr/
- 제22대 선거구 GeoJSON: https://github.com/OhmyNews/2024_22_elec_map
