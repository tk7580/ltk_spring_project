-- 데이터베이스가 존재하면 삭제 (모든 데이터 파괴)
DROP
DATABASE IF EXISTS ltk-spring-project;

-- 데이터베이스 생성
CREATE
DATABASE ltk-spring-project;

-- 생성한 데이터베이스 사용
USE
ltk-spring-project;

-- 테이블 삭제 (순서 중요: 외래 키 제약 조건 때문에 역순으로 삭제)
DROP TABLE IF EXISTS conpro;
DROP TABLE IF EXISTS reply;
DROP TABLE IF EXISTS reactionPoint;
DROP TABLE IF EXISTS article;
DROP TABLE IF EXISTS work; -- 일관성을 위해 소문자로 변경
DROP TABLE IF EXISTS board;
DROP TABLE IF EXISTS series;
DROP TABLE IF EXISTS member;
-- 일관성을 위해 소문자로 변경

-- 1. member 테이블 (회원)
CREATE TABLE member
(                                                                                  -- 테이블명 소문자로 표준화
    id           BIGINT    NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '회원 고유 번호', -- INT(10) UNSIGNED -> BIGINT
    regDate      DATETIME  NOT NULL COMMENT '회원 가입 날짜',
    updateDate   DATETIME  NOT NULL COMMENT '회원 정보 최종 수정 날짜',
    loginId      CHAR(30)  NOT NULL UNIQUE COMMENT '로그인 아이디',
    loginPw      CHAR(100) NOT NULL COMMENT '로그인 비밀번호',
    authLevel    SMALLINT(2) UNSIGNED DEFAULT 3 COMMENT '권한 레벨 (3=일반, 7=관리자)',
    name         CHAR(20)  NOT NULL COMMENT '회원 이름',                               -- 원본 DDL의 name 컬럼명 유지 (대소문자 구분 없음)
    nickname     CHAR(20)  NOT NULL UNIQUE COMMENT '회원 닉네임',
    cellphoneNum CHAR(20)  NOT NULL COMMENT '휴대폰 번호',
    email        CHAR(50)  NOT NULL COMMENT '이메일 주소',
    gender       CHAR(1) COMMENT '성별 (M: 남성, F: 여성 등)',
    birthDate    DATE COMMENT '생년월일 (YYYY-MM-DD)',
    age          SMALLINT(3) UNSIGNED COMMENT '만 나이 (생년월일 기준 계산)',
    delStatus    TINYINT(1) UNSIGNED NOT NULL DEFAULT 0 COMMENT '탈퇴 여부 (0=탈퇴 전, 1=탈퇴 후)',
    delDate      DATETIME COMMENT '탈퇴 날짜'
);

-- 2. series 테이블 (시리즈 최상위 묶음이자 게시판 기준)
CREATE TABLE series
(
    id            INT(10) UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '시리즈 고유 번호 (게시판 ID로 활용)',
    regDate       DATETIME     NOT NULL COMMENT '시리즈 정보 등록 날짜',
    updateDate    DATETIME     NOT NULL COMMENT '시리즈 정보 최종 수정 날짜',
    titleKr       VARCHAR(255) NOT NULL COMMENT '시리즈 한글 대표 제목',
    titleOriginal VARCHAR(255) COMMENT '시리즈 원어 대표 제목',
    description   TEXT COMMENT '시리즈 전체 개요/줄거리', -- 원본 DDL의 description 컬럼명 유지 (대소문자 구분 없음)
    thumbnailUrl  VARCHAR(255) COMMENT '시리즈 대표 썸네일 이미지 URL',
    coverImageUrl VARCHAR(255) COMMENT '시리즈 대표 커버 이미지 URL',
    author        VARCHAR(100) COMMENT '원작자'
);

-- 3. board 테이블 (게시판)
CREATE TABLE board
(
    id         INT(10) UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '게시판 고유 번호',
    regDate    DATETIME NOT NULL COMMENT '등록 날짜',
    updateDate DATETIME NOT NULL COMMENT '수정 날짜',
    code       CHAR(50) NOT NULL UNIQUE COMMENT '게시판 코드 (예: notice, free, QnA)', -- 원본 DDL의 code 컬럼명 유지
    name       CHAR(20) NOT NULL UNIQUE COMMENT '게시판 이름',                        -- 원본 DDL의 name 컬럼명 유지
    delStatus  TINYINT(1) UNSIGNED NOT NULL DEFAULT 0 COMMENT '삭제 여부 (0=삭제 전, 1=삭제 후)',
    delDate    DATETIME COMMENT '삭제 날짜'
);

-- 4. work 테이블 (개별 작품/미디어 형태)
CREATE TABLE work
(                                                                                                       -- 테이블명 소문자로 표준화
    id               INT(10) UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '개별 작품 고유 번호',
    seriesId         INT(10) UNSIGNED NOT NULL COMMENT '어떤 시리즈에 속하는지 (series.id 참조)',
    regDate          DATETIME     NOT NULL COMMENT '개별 작품 정보 등록 날짜',
    updateDate       DATETIME     NOT NULL COMMENT '개별 작품 정보 최종 수정 날짜',
    titleKr          VARCHAR(255) NOT NULL COMMENT '개별 작품 한글 제목 (예: 나혼렙 웹툰, 나혼렙 애니메이션)',
    titleOriginal    VARCHAR(255) COMMENT '개별 작품 원어 제목',
    type             VARCHAR(50)  NOT NULL COMMENT '작품 유형 (Movie, Drama, Webtoon, Comic, Animation 등)', -- 원본 DDL의 type 컬럼명 유지
    releaseDate      DATE COMMENT '최초 공개일 (영화 개봉일, 웹툰 연재 시작일, 애니 방영 시작일 등)',
    releaseSequence  INT(10) UNSIGNED COMMENT '시리즈 내 발매/공개 순서 (NULL 허용)',                               -- NOT NULL DEFAULT 0 제거
    timelineSequence INT(10) UNSIGNED COMMENT '시리즈 내 내부 시간 흐름 순서 (NULL 허용)',                            -- NOT NULL DEFAULT 0 제거
    isCompleted      TINYINT(1) UNSIGNED DEFAULT 0 COMMENT '개별 작품 완결 여부 (0=미완결, 1=완결)',
    description      TEXT COMMENT '개별 작품 상세 설명/시놉시스',                                                   -- 원본 DDL의 description 컬럼명 유지
    FOREIGN KEY (seriesId) REFERENCES series (id) ON DELETE CASCADE
);

-- 5. article 테이블 (게시글)
CREATE TABLE article
(
    id                INT(10) UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '게시글 고유 번호',
    regDate           DATETIME     NOT NULL COMMENT '등록 날짜',
    updateDate        DATETIME     NOT NULL COMMENT '수정 날짜',
    memberId          BIGINT       NOT NULL COMMENT '게시글을 작성한 회원 ID', -- INT(10) UNSIGNED -> BIGINT
    seriesId          INT(10) UNSIGNED NOT NULL COMMENT '게시글이 속한 시리즈 ID (게시판 ID 역할)',
    title             VARCHAR(255) NOT NULL COMMENT '게시글 제목',
    body              TEXT         NOT NULL COMMENT '게시글 내용',
    hitCount          INT(10) UNSIGNED NOT NULL DEFAULT 0 COMMENT '조회수',
    goodReactionPoint INT(10) UNSIGNED NOT NULL DEFAULT 0 COMMENT '좋아요 수',
    badReactionPoint  INT(10) UNSIGNED NOT NULL DEFAULT 0 COMMENT '싫어요 수',
    FOREIGN KEY (memberId) REFERENCES member (id) ON DELETE CASCADE,  -- 참조 테이블명 소문자 member로 수정
    FOREIGN KEY (seriesId) REFERENCES series (id) ON DELETE CASCADE
);

-- 6. reactionPoint 테이블 (반응 기록)
CREATE TABLE reactionPoint
(
    id           INT(10) UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '반응 기록 고유 번호',
    regDate      DATETIME NOT NULL COMMENT '등록 날짜',
    updateDate   DATETIME NOT NULL COMMENT '수정 날짜',
    memberId     BIGINT   NOT NULL COMMENT '반응을 남긴 회원 ID',          -- INT(10) UNSIGNED -> BIGINT
    relTypeCode  CHAR(50) NOT NULL COMMENT '관련 데이터 타입 (예: article, reply)',
    relId        INT(10) NOT NULL COMMENT '관련 데이터 번호',
    reactionType CHAR(10) NOT NULL COMMENT '반응 종류 (GOOD: 좋아요, BAD: 싫어요)',
    point        INT(10) NOT NULL COMMENT '반응 점수 (일반적으로 reactionType에 따라 1 또는 -1 사용)',
    FOREIGN KEY (memberId) REFERENCES member (id) ON DELETE CASCADE -- 참조 테이블명 소문자 member로 수정
);

-- 7. reply 테이블 (댓글)
CREATE TABLE reply
(
    id                INT(10) UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '댓글 고유 번호',
    regDate           DATETIME NOT NULL COMMENT '등록 날짜',
    updateDate        DATETIME NOT NULL COMMENT '수정 날짜',
    memberId          BIGINT   NOT NULL COMMENT '댓글을 작성한 회원 ID',     -- INT(10) UNSIGNED -> BIGINT
    relTypeCode       CHAR(50) NOT NULL COMMENT '관련 데이터 타입 (이 경우 항상 article)',
    relId             INT(10) UNSIGNED NOT NULL COMMENT '관련 게시물 (article) 번호',
    parentId          INT(10) UNSIGNED COMMENT '부모 댓글의 ID (최상위 댓글은 NULL)',
    body              TEXT     NOT NULL COMMENT '댓글 내용',
    goodReactionPoint INT(10) UNSIGNED NOT NULL DEFAULT 0 COMMENT '좋아요 수',
    badReactionPoint  INT(10) UNSIGNED NOT NULL DEFAULT 0 COMMENT '싫어요 수',
    FOREIGN KEY (memberId) REFERENCES member (id) ON DELETE CASCADE, -- 참조 테이블명 소문자 member로 수정
    FOREIGN KEY (relId) REFERENCES article (id) ON DELETE CASCADE,
    FOREIGN KEY (parentId) REFERENCES reply (id) ON DELETE CASCADE
);

-- 8. conpro 테이블 (콘텐츠 제공처 정보)
CREATE TABLE conpro
(
    id             INT(10) UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '제공처 정보 고유 번호',
    workId         INT(10) UNSIGNED NOT NULL COMMENT '해당 콘텐츠가 속한 개별 작품 ID',
    providerType   VARCHAR(50)  NOT NULL COMMENT '제공처 유형 (예: OTT, Platform, Website, App, Distributor 등)',
    providerName   VARCHAR(100) NOT NULL COMMENT '제공처 이름 (예: Netflix, Naver Series On, YouTube, Apple TV, Wavve)',
    contentUrl     VARCHAR(255) COMMENT '해당 작품의 제공처 내 상세 페이지 URL',
    appScheme      VARCHAR(255) COMMENT '해당 작품으로 바로 연결되는 앱 스킴 (모바일 앱 연동용)',
    additionalInfo TEXT COMMENT '추가적인 정보 (예: 유료/무료, 대여/구매 가능 여부 등)',
    FOREIGN KEY (workId) REFERENCES work (id) ON DELETE CASCADE -- 참조 테이블명 소문자 work로 수정
);