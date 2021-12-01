# Yogiyo crawling
## restaurant_info
|column|comment|
|--|--|
|_id|auto_increment|
|restaurant_id|요기요에서 부여한 식당id(FK)|
|company_id|사업자등록번호|
|name|식당 이름|
|categories|요기요에서 부여한 식당 카테고리|
|phone|요기요에 등록된 전화번호|
|address|전처리된 요기요 등록 식당 주소|
|sido, sigungu|주소에서 추출한 시군구|
|franchise_yn|프랜차이즈 식당 여부|
|francise_id|요기요에 등록된 프랜차이즈 id|
|franchise_name|프랜차이즈 이름|
|delivery_yn|배달가능 여부|
|delivery_time|배달 예상 시간|
|delivery_fee|배달 금액|
|lat, lng|식당 좌표|
|avg|식당 평균 평점|
|review_count|식당 리뷰 수|
<br>

## menu_info
|column|comment|
|--|--|
|_id|auto_increment|
|menu_id|요기요에서 부여한 메뉴id(PK)|
|restaurant_id|요기요에서 부여한 식당id(FK, restaurant_info)|
|name|요기요에 등록된 메뉴 이름|
|description|요기요에 등록된 메뉴 설명|
|price|메뉴 가격|
<br>

## reviews
|column|comment|
|--|--|
|review_id|요기요에서 부여한 리뷰id(PK)|
|nickname|요기요 리뷰 작성자 별명|
|user_name|식당위치 + 작성자 별명으로 새로 부여된 리뷰 작성자 이름(FK, user_info)|
|user_id|새로 부여된 리뷰 작성자의 번호(FK, user_info)|
|restaurant_id|요기요에서 부여한 식당id(FK, restaurant_info)|
|menu|리뷰 작성시 주문한 메뉴 중 첫 번째 메뉴|
|menu_id|요기요에서 부여한 메뉴id(FK, menu_info), -1은 현재 메뉴 테이블에 없는 메뉴|
|review|리뷰 내용|
|quantity|양 평점(2015년~2019년 댓글은 0일 수 있음)|
|taste|맛 평점|
|delivery|배달 평점|
|rating|전체 평점(0점 없음)|
|like_dislike|전체 평점이 2.5이상이면 1, 미만이면 0|
