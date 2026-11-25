# 데이터 출처 및 기준 안내 (v13)

## 이번 버전에 반영한 공식 확인 자료

`election_history_summary.csv`에는 제20대~제22대 국회의원선거의 선거구획정 기준 인구 요약을 반영했습니다.

| 총선 | 기준일 | 최대 인구 | 최소 인구 | 평균 인구 | 지역구 수 |
|---|---|---:|---:|---:|---:|
| 제20대 | 2015-10-31 | 278,982 | 140,126 | 204,847 | 253 |
| 제21대 | 2019-01-31 | 277,912 | 139,027 | 204,914 | 253 |
| 제22대 | 2023-01-31 | 273,177 | 136,629 | 202,480.4 | 254 |

주의: 위 수치는 각 총선의 선거구획정에 사용된 기준 인구 요약이며, 서로 다른 기준일의 값입니다. 제23대 총선은 아직 확정된 선거구/기준 인구가 없으므로 가상 시나리오로만 취급합니다.

## 공식·주요 출처
- 제20대 총람: 중앙선거관리위원회, https://www.nec.go.kr/files/B0000215/201611/BBS_201611300149552650.pdf
- 제21대 총람: 중앙선거관리위원회, https://ok.nec.go.kr/common/board/Download.do?bcIdx=138933&cbIdx=1129&streFileNm=a5dc3bae-a62d-4d60-8e99-1194db10967c.pdf
- 제22대 총람: 중앙선거관리위원회, https://daigyeo.com/post_file_download.cm?c=YTo1OntzOjEwOiJib2FyZF9jb2RlIjtzOjIyOiJiMjAyMzA4MjJmNzI2MDhmODM2NzZhIjtzOjk6InBvc3RfY29kZSI7czoyMjoicDIwMjQxMjA2NmYwNzQxNGZkY2YzOCI7czo5OiJmaWxlX2NvZGUiO3M6MjI6InAyMDI0MTIwNmRhMmMyYWE2MDcyODYiO3M6MTk6InBvc3RfdG9rZW4iO3M6MTM6IjZhMDg1OTVmNzIzY2YiO3M6MTE6Im1lbWJlcl9jb2RlIjtOO30%3D
- 행정안전부 주민등록 인구통계: https://jumin.mois.go.kr/ (월말 기준, 2008년 이후)
- 중앙선거관리위원회 선거인수 정보: https://www.data.go.kr/data/15094967/openapi.do
- 중앙선거관리위원회 제19~22대 국회의원선거 투표구별 개표결과: https://data.nec.go.kr/open-data/file.do?dataId=9
- 제22대 선거구 경계 GeoJSON: https://github.com/OhmyNews/2024_22_elec_map

## 아직 별도 원자료가 필요한 분석
다음 파일은 헤더만 제공되어 있습니다. 실제 분석 전 공식 원자료를 확보해 채워야 합니다.
- `constituency_population.csv`: 제22대 254개 선거구별 주민등록인구·선거인수·투표자수 및 지도명
- `constituency_population_23rd.csv`: 제22대 경계 고정 후 동일 읍면동 기준으로 집계한 제23대 가정 인구
- `historical_constituencies.csv`: 역대 총선별 선거구 단위 전체 인구 원자료
- `adjacency_population.csv`: 인접 선거구 쌍과 각 인구
- `region_population_seats.csv`: 각 총선 기준일에 맞춘 시도별 주민등록인구 및 의석수
- `election_voters.csv`: 총선별 선거구 단위 선거인수·투표자수

이 파일들을 빈칸 또는 예시값으로 채우지 않았습니다. 공식 원자료가 들어오면 대시보드가 계산하도록 구성했습니다.
