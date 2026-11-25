# 데이터 연결 안내 (v9)

## 현재 상태
- `constituency_population.csv`, `historical_constituencies.csv`, `election_history_summary.csv`,
  `election_voters.csv`, `region_population_seats.csv`, `adjacency_population.csv`,
  `constituency_population_23rd.csv`는 **실제 자료 입력용 템플릿**입니다.
- `demo_*.csv`는 화면 테스트용 가상자료입니다. 실제 분석·발표에 사용하지 마세요.
- v9에서는 예시자료 미리보기가 기본적으로 꺼져 있습니다.

## 제22대 선거구 인구 자료
`constituency_population.csv` 열:
- `시도`: 서울, 부산, 경기 등
- `선거구`: 사람이 읽는 선거구명
- `주민등록인구`: 제22대 획정 기준일인 2023-01-31 주민등록인구
- `선거인수`, `투표자수`: 선관위의 선거구별 값 (없는 경우 빈칸)
- `위도`, `경도`: 선택 사항
- `지도명`: GeoJSON의 `SIDO_SGG` 값과 정확히 일치하는 지도 결합키
- `이전인구`: 비교 기준일 인구(동일한 선거구 공간범위로 재집계한 값)

제22대 GeoJSON 출처:
https://github.com/OhmyNews/2024_22_elec_map
GeoJSON 속성 `SIDO_SGG`와 CSV의 `지도명`을 연결합니다.

## 역대 총선 선거구별 인구
`historical_constituencies.csv` 열:
`총선,연도,시도,선거구,주민등록인구`
각 총선 당시의 실제 선거구 경계와 기준일 인구를 사용해야 합니다.
선거구 명칭만으로 서로 다른 시기의 경계를 같은 공간으로 간주하지 마세요.

## 역대 총선 요약
`election_history_summary.csv` 열:
`총선,연도,최대인구,최소인구,평균인구`
요약값은 동일 총선의 선거구별 원자료에서 계산하는 것을 권장합니다.

## 선거인수·투표자수
`election_voters.csv` 열:
`총선,시도,선거구,선거인수,투표자수`
선거인수와 주민등록인구는 모집단·기준일이 다를 수 있으므로 데이터 기준일을 함께 기록하세요.

## 지역별 인구와 지역구 의석수
`region_population_seats.csv` 열:
`지역,주민등록인구,지역구수`
광역시·도 단위부터 분석하는 것을 권장합니다. 주민등록인구 기준일을 명시하세요.

## 제23대 가정
`constituency_population_23rd.csv`는 제22대와 동일한 254개 선거구 경계를 유지하고,
새로운 기준일 인구만 입력하는 가정 분석용입니다. 실제 확정 선거구가 아니라는 점을 표시하세요.

## 인접 선거구
`adjacency_population.csv` 열:
`선거구,인접선거구,선거구인구,인접선거구인구`
공유 경계 길이 등 지리적 인접 기준을 먼저 정한 뒤 생성하세요.

## 공개 자료 출처
- 행정안전부 주민등록 인구통계: https://jumin.mois.go.kr/
- 공공데이터포털: https://www.data.go.kr/
- 중앙선거관리위원회 선거통계: https://info.nec.go.kr/
- 제22대 선거구 GeoJSON: https://github.com/OhmyNews/2024_22_elec_map
