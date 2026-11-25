# 국회의원 지역구 인구와 표의 등가성 분석

## 실행
```bash
pip install -r requirements.txt
streamlit run app.py
```

## 데이터 주의
현재 CSV는 화면과 위젯 상호작용 확인을 위한 임의의 예시 데이터입니다.
실제 통계나 실제 선거구 경계가 아닙니다. 최종 분석·발표 전 공식 공개 데이터와
제22대 선거구 경계 GeoJSON으로 교체해야 합니다.

## 배포
GitHub 저장소 루트에 app.py, requirements.txt, data/ 폴더를 올린 뒤
Streamlit Community Cloud에서 app.py를 Main file path로 지정합니다.
