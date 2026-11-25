# 국회의원 지역구 인구와 표의 등가성 분석 대시보드

## 실행
```bash
pip install -r requirements.txt
streamlit run app.py
```

## 배포
GitHub 저장소 루트에 `app.py`, `requirements.txt`, `data/` 폴더를 둡니다. Streamlit Community Cloud의 Main file path는 `app.py`입니다.

## 이번 버전
- 제20·21·22대 선거구획정 기준 최대·최소·평균 인구 요약을 공식 자료에 따라 반영
- 역대 추세 차트의 연도축을 정수 연도로 고정해 2023.5 같은 중간 눈금 문제 수정
- 지도에 CartoDB Positron 배경을 적용하고 대한민국 영역 중심으로 맞춤
- 실제 원자료가 없는 차트는 가짜 값 대신 데이터 필요 안내를 표시

세부 데이터 출처와 미확보 원자료 목록은 `data/README_data_sources.md`를 확인하세요.
