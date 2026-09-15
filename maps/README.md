# 오키나와 가족여행 지도

`day-1.svg`–`day-8.svg`: 날짜별 이미지. `overview.svg`: 전체 이동 경로.

모든 지도는 외부 글꼴 없이 한글이 표시되고 확대해도 선명한 SVG 이미지입니다.
지리 좌표를 투영했으며, 선은 실제 도로가 아닌 방문 순서를 나타냅니다.
숙소·주유소·반납 장소는 확정 전 대표 지점입니다.

## 출처

- 해안선: 일본 국토교통성 National Land Numerical Information, geoBoundaries JPN ADM0. [원본 데이터](https://github.com/wmgeolab/geoBoundaries/blob/9469f09/releaseData/gbOpen/JPN/ADM0/geoBoundaries-JPN-ADM0.geojson), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). 오키나와 구역 추출, 투영, 스타일 변경, 한글 표기 및 경로 추가.
- 한글: Noto Sans KR, SIL Open Font License. 글자 윤곽을 이미지에 포함했습니다.
- 도카도카 위치: [공식 사이트](https://dokadoka.jp/)의 구글 지도 좌표.
- 요미탄 도자기 마을 위치: [MapFan](https://mapfan.com/spots/SC545%2CJ%2C0).
- 카페 차하야부란 위치: NAVITIME 지도 안내. 매장 운영은 일정표의 공식 안내 재확인.

## 다시 만들기

Python 3와 `fonttools` 설치 후 저장소 루트에서:

```sh
python scripts/build_maps.py
```

처음 실행하면 공개 지리 자료와 글꼴을 다운로드해 임시 캐시에 저장합니다.
`itinerary-data.js`의 날짜별 `map` 목록을 수정한 뒤 재생성하세요.
방문지가 늘어나면 라벨 배치와 글자 겹침을 다시 확인해야 합니다.
