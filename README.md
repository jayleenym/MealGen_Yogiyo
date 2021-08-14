# Yogiyo

this repository is for crawling restaurant's menu & reviews in yogiyo, and preprocessing data.

### TABLE 1: restaurant_info
- _id (PK)
- restaurant_id : yogiyo 식당 고유 번호(unique)
- company_id : 사업자등록번호
- created_at : 생성 일시
- updated_at : 업데이트 일시
- name : 식당호
- phone : 전화번호
- address : 주소
- si : 시도 구분
- franchise_yn : 프랜차이즈 여부
- franchise_id : 프랜차이즈 ID
- delivery_yn : 배달 가능 여부
- delivery_time : 배달 시간
- delivery_fee : 배달료
- loc : 좌표(경도, 위도)
- avg : 평균 평점
- review_count : 리뷰수

### TABLE 2: menu_info
- _id(PK)
- menu_id : yogiyo 메뉴 고유 번호(unique)
- created_at : 생성 일시
- updated_at : 업데이트 일시
- restaurant_id (FK)
- name : 메뉴 이름
- description : 설명
- price : 가격


### TABLE 3: reviews
- _id(PK)
- created_at : 작성 일시
- nickname : 유저 닉네임
- user_id : yogiyo 유저 번호
- restaurant_id(FK)
- menu_id(FK)
- menu : 주문 내용
- comment : 리뷰 내용
- quantity_rating : 양 평점
- taste_rating : 맛 평점
- delivery_rating : 배달 평점
- rating : 평점
- like_dislike : 2.5이상 1, 미만 0
