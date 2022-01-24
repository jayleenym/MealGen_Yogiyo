## 기초번호 위치정보DB
- 주소 출처: [도로명주소 개발자센터](https://www.juso.go.kr/addrlink/addressBuildDevNew.do?menu=jusuip)
<!-- - ubuntu 환경에서 파일 다운로드 (202109 기준, 성공여부 모름)
```bash
$ wget https://www.juso.go.kr/dn.do?boardId=JUSUIPDATA&regYmd=2021&num=13&fileNo=91714&stdde=202109&fileName=202109_기초번호위치정보DB_전체분.7z&realFileName=JUSUIP_DB_ALL_2109.7z&logging=Y
``` -->

## Ubuntu Chromedriver 사용
- chrome 설치
```
$ sudo apt-get update
$ wget https://dl.google.com/linux/directgoogle-chrome-stable_current_amd64.deb
$ sudo dpkg -i google-chrome-stable_current_amd64.deb

# dpkg 오류
sudo apt --fix-broken install
```
- chromedriver 설치
```
$ google-chrome --version # 버전확인

$ wget -N https://chromedriver.storage.googleapis.com/94.0.4606.61/chromedriver_linux64.zip
$ unzip chromedriver_linux64.zip
```