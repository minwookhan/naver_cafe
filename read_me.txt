* 파일설명
  logging_config.json: 로깅 환경 설정용 파일
  naver_cafe_cnf.json : 동작 환경용 설정파일
 - date: all, 1d, 1w, 1m, 6m, 1y, 2017-09-012017-12-10
 - searchBy = 1(전체), 3(작성자), 4(댓글내용), 5(댓글작성자) 
* 사용법:
  grab_violin79 -c naver_cafe_cnf.json
* 주의사항
  해상도는 FHD로 해라 화며에 다 안잡히면 메뉴 클릭이 제대로 안된다
  - 검색결과 페이지 이동이 안 될 수 있다.
* 설치 유의사항
  - xvfb 설치
  - xauth 설치
  - 데비안용 firefox 설치 (command line 용) 
