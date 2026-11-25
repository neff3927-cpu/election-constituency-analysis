# 국회의원 지역구 인구와 표의 등가성 분석

## 실행
```bash
pip install -r requirements.txt
streamlit run app.py
```

## 배포
GitHub 저장소의 `app.py`, `requirements.txt`, `data/` 폴더를 함께 업로드하세요. Streamlit Community Cloud의 Main file path는 `app.py`입니다.

## 데이터
`data/`의 CSV 파일에 실제 자료를 입력하면 앱이 자동으로 차트와 상세정보를 갱신합니다. 앱 내 CSV 업로더는 현재 세션에 즉시 반영하는 임시 연결이며, 지속 배포를 위해서는 CSV를 GitHub의 `data/` 폴더에 커밋해야 합니다. 예시값을 실제 통계처럼 표시하지 않으며 자료가 비어 있으면 안내문을 표시합니다.

자세한 열 이름은 앱 하단의 'CSV 열 구성 및 데이터 출처'를 확인하세요.
