# restaurant_info
|column|comment|
|--|--|
|_id|auto_increment|
|restaurant_id|요기요에서 부여한 식당id|
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

# menu_info
|column|comment|
|--|--|
|_id|auto_increment|
|menu_id|요기요에서 부여한 메뉴id|
|restaurant_id|요기요에서 부여한 식당id|
|name|요기요에 등록된 메뉴 이름|
|description|요기요에 등록된 메뉴 설명|
|price|메뉴 가격|