/* ───────────────────────────────────────────
   LTK SPRING PROJECT – FULL DDL (camelCase) 
   ─────────────────────────────────────────── */

DROP DATABASE IF EXISTS ltk_spring_project;
CREATE DATABASE ltk_spring_project
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE ltk_spring_project;

/* ───────────── MASTER ───────────── */
CREATE TABLE member
(
    id           BIGINT PRIMARY KEY AUTO_INCREMENT,
    regDate      DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updateDate   DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    loginId      CHAR(30)            NOT NULL UNIQUE,
    loginPw      CHAR(100)           NOT NULL,
    authLevel    SMALLINT(2) UNSIGNED         DEFAULT 3,
    name         CHAR(20)            NOT NULL,
    nickname     CHAR(20)            NOT NULL UNIQUE,
    cellphoneNum CHAR(20)            NOT NULL,
    email        CHAR(50)            NOT NULL,
    gender       CHAR(1),
    birthDate    DATE,
    age          SMALLINT(3) UNSIGNED,
    delStatus    TINYINT(1) UNSIGNED NOT NULL DEFAULT 0,
    delDate      DATETIME
);

CREATE TABLE series
(
    id            BIGINT PRIMARY KEY AUTO_INCREMENT,
    regDate       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updateDate    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    titleKr       VARCHAR(255) NULL,
    titleOriginal VARCHAR(255),
    description   TEXT,
    thumbnailUrl  VARCHAR(255),
    coverImageUrl VARCHAR(255),
    author        VARCHAR(100),
    publisher     VARCHAR(100),
    studios       VARCHAR(255)
);

/* ───────────── WORK ───────────── */
CREATE TABLE work
(
    id               BIGINT PRIMARY KEY AUTO_INCREMENT,
    seriesId         BIGINT              NULL,
    anilistId        BIGINT UNIQUE       NULL,
    regDate          DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updateDate       DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    titleKr          VARCHAR(255)        NULL,
    titleOriginal    VARCHAR(255),
    isOriginal       BOOLEAN             NOT NULL DEFAULT FALSE,
    releaseDate      DATE                NULL,
    watchedCount     INT UNSIGNED        NOT NULL DEFAULT 0,
    averageRating    DECIMAL(4, 2)       NOT NULL DEFAULT 0.00,
    ratingCount      INT UNSIGNED        NOT NULL DEFAULT 0,
    episodes         INT UNSIGNED,
    duration         INT UNSIGNED,
    creators         VARCHAR(255),
    studios          VARCHAR(255),
    releaseSequence  INT UNSIGNED,
    timelineSequence INT UNSIGNED,
    isCompleted      TINYINT(1) UNSIGNED NOT NULL DEFAULT 0,
    description      TEXT,
    thumbnailUrl     VARCHAR(255),
    trailerUrl       VARCHAR(255),
    CONSTRAINT fk_work_series FOREIGN KEY (seriesId) REFERENCES series (id) ON DELETE SET NULL
);

/* ───────────── REFERENCE ───────────── */
CREATE TABLE workType
(
    id         BIGINT PRIMARY KEY AUTO_INCREMENT,
    regDate    DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updateDate DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    name       VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE workTypeMapping
(
    id      BIGINT PRIMARY KEY AUTO_INCREMENT,
    regDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    workId  BIGINT   NOT NULL,
    typeId  BIGINT   NOT NULL,
    CONSTRAINT fk_wtm_work FOREIGN KEY (workId) REFERENCES work (id) ON DELETE CASCADE,
    CONSTRAINT fk_wtm_type FOREIGN KEY (typeId) REFERENCES workType (id) ON DELETE CASCADE,
    UNIQUE KEY UK_workType (workId, typeId)
);

CREATE TABLE workIdentifier
(
    id         BIGINT PRIMARY KEY AUTO_INCREMENT,
    regDate    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updateDate DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    workId     BIGINT       NOT NULL,
    sourceName VARCHAR(50)  NOT NULL,
    sourceId   VARCHAR(255) NOT NULL,
    CONSTRAINT fk_wid_work FOREIGN KEY (workId) REFERENCES work (id) ON DELETE CASCADE,
    UNIQUE KEY UK_source (sourceName, sourceId)
);

CREATE TABLE genre
(
    id         BIGINT PRIMARY KEY AUTO_INCREMENT,
    regDate    DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updateDate DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    name       VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE workGenre
(
    id      BIGINT PRIMARY KEY AUTO_INCREMENT,
    regDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    workId  BIGINT   NOT NULL,
    genreId BIGINT   NOT NULL,
    CONSTRAINT fk_wg_work FOREIGN KEY (workId) REFERENCES work (id) ON DELETE CASCADE,
    CONSTRAINT fk_wg_genre FOREIGN KEY (genreId) REFERENCES genre (id) ON DELETE CASCADE,
    UNIQUE KEY UK_workGenre (workId, genreId)
);

/* ───────────── VIEWING GUIDE ───────────── */
CREATE TABLE viewingGuide
(
    id               BIGINT PRIMARY KEY AUTO_INCREMENT,
    regDate          DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updateDate       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    seriesId         BIGINT       NOT NULL,
    guideName        VARCHAR(100) NOT NULL,
    guideDescription TEXT,
    CONSTRAINT fk_vg_series FOREIGN KEY (seriesId) REFERENCES series (id) ON DELETE CASCADE
);

CREATE TABLE viewingGuideItem
(
    id              BIGINT PRIMARY KEY AUTO_INCREMENT,
    guideId         BIGINT       NOT NULL,
    workId          BIGINT       NOT NULL,
    stepNumber      INT UNSIGNED NOT NULL,
    stepDescription TEXT,
    CONSTRAINT fk_vgi_guide FOREIGN KEY (guideId) REFERENCES viewingGuide (id) ON DELETE CASCADE,
    CONSTRAINT fk_vgi_work FOREIGN KEY (workId) REFERENCES work (id) ON DELETE CASCADE
);

/* ───────────── MEMBER × WORK ───────────── */
CREATE TABLE memberWishlistWork
(
    id       BIGINT PRIMARY KEY AUTO_INCREMENT,
    regDate  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    memberId BIGINT   NOT NULL,
    workId   BIGINT   NOT NULL,
    CONSTRAINT fk_mww_member FOREIGN KEY (memberId) REFERENCES member (id) ON DELETE CASCADE,
    CONSTRAINT fk_mww_work FOREIGN KEY (workId) REFERENCES work (id) ON DELETE CASCADE,
    UNIQUE KEY UK_memberWork (memberId, workId)
);

CREATE TABLE memberWatchedWork
(
    id          BIGINT PRIMARY KEY AUTO_INCREMENT,
    regDate     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updateDate  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    memberId    BIGINT   NOT NULL,
    workId      BIGINT   NOT NULL,
    watchedDate DATE     NULL,
    CONSTRAINT fk_mww2_member FOREIGN KEY (memberId) REFERENCES member (id) ON DELETE CASCADE,
    CONSTRAINT fk_mww2_work FOREIGN KEY (workId) REFERENCES work (id) ON DELETE CASCADE,
    UNIQUE KEY UK_memberWatched (memberId, workId)
);

CREATE TABLE memberWorkRating
(
    id         BIGINT PRIMARY KEY AUTO_INCREMENT,
    regDate    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updateDate DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    memberId   BIGINT        NOT NULL,
    workId     BIGINT        NOT NULL,
    score      DECIMAL(3, 1) NOT NULL,
    comment    TEXT,
    CONSTRAINT fk_mwr_member FOREIGN KEY (memberId) REFERENCES member (id) ON DELETE CASCADE,
    CONSTRAINT fk_mwr_work FOREIGN KEY (workId) REFERENCES work (id) ON DELETE CASCADE,
    UNIQUE KEY UK_memberRating (memberId, workId)
);

CREATE TABLE memberWishlistSeries
(
    id       BIGINT PRIMARY KEY AUTO_INCREMENT,
    regDate  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    memberId BIGINT   NOT NULL,
    seriesId BIGINT   NOT NULL,
    CONSTRAINT fk_mws_member FOREIGN KEY (memberId) REFERENCES member (id) ON DELETE CASCADE,
    CONSTRAINT fk_mws_series FOREIGN KEY (seriesId) REFERENCES series (id) ON DELETE CASCADE,
    UNIQUE KEY UK_memberSeries (memberId, seriesId)
);

/* ───────────── CONTENT PROVIDER ───────────── */
CREATE TABLE conpro
(
    id             BIGINT PRIMARY KEY AUTO_INCREMENT,
    workId         BIGINT       NOT NULL,
    providerType   VARCHAR(50)  NOT NULL,
    providerName   VARCHAR(100) NOT NULL,
    contentUrl     VARCHAR(255),
    appScheme      VARCHAR(255),
    additionalInfo TEXT,
    CONSTRAINT fk_conpro_work FOREIGN KEY (workId) REFERENCES work (id) ON DELETE CASCADE
);

/* ───────────── BOARD / ARTICLE / REPLY ───────────── */
CREATE TABLE board
(
    id         BIGINT PRIMARY KEY AUTO_INCREMENT,
    regDate    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updateDate DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    seriesId   BIGINT       NOT NULL UNIQUE,
    name       VARCHAR(255) NOT NULL,
    code       CHAR(50)     NOT NULL UNIQUE,
    CONSTRAINT fk_board_series FOREIGN KEY (seriesId) REFERENCES series (id) ON DELETE CASCADE
);

CREATE TABLE article
(
    id                BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    regDate           DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updateDate        DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    memberId          BIGINT       NOT NULL,
    boardId           BIGINT       NOT NULL,
    title             VARCHAR(255) NOT NULL,
    body              TEXT         NOT NULL,
    hitCount          INT UNSIGNED NOT NULL DEFAULT 0,
    goodReactionPoint INT UNSIGNED NOT NULL DEFAULT 0,
    badReactionPoint  INT UNSIGNED NOT NULL DEFAULT 0,
    CONSTRAINT fk_article_member FOREIGN KEY (memberId) REFERENCES member (id) ON DELETE CASCADE,
    CONSTRAINT fk_article_board FOREIGN KEY (boardId) REFERENCES board (id) ON DELETE CASCADE
);

CREATE TABLE articleViewLog
(
    id        BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    regDate   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    memberId  BIGINT          NOT NULL,
    articleId BIGINT UNSIGNED NOT NULL,
    CONSTRAINT fk_avl_member FOREIGN KEY (memberId) REFERENCES member (id) ON DELETE CASCADE,
    CONSTRAINT fk_avl_article FOREIGN KEY (articleId) REFERENCES article (id) ON DELETE CASCADE,
    UNIQUE KEY UK_memberArticle (memberId, articleId)
);

CREATE TABLE reply
(
    id                BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    regDate           DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updateDate        DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    memberId          BIGINT          NOT NULL,
    relTypeCode       CHAR(50)        NOT NULL,
    relId             BIGINT UNSIGNED NOT NULL,
    parentId          BIGINT UNSIGNED,
    body              TEXT            NOT NULL,
    goodReactionPoint INT UNSIGNED    NOT NULL DEFAULT 0,
    badReactionPoint  INT UNSIGNED    NOT NULL DEFAULT 0,
    CONSTRAINT fk_reply_member FOREIGN KEY (memberId) REFERENCES member (id) ON DELETE CASCADE,
    CONSTRAINT fk_reply_article FOREIGN KEY (relId) REFERENCES article (id) ON DELETE CASCADE,
    CONSTRAINT fk_reply_parent FOREIGN KEY (parentId) REFERENCES reply (id) ON DELETE CASCADE
);

CREATE TABLE reactionPoint
(
    id           BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    regDate      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updateDate   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    memberId     BIGINT          NOT NULL,
    relTypeCode  CHAR(50)        NOT NULL,
    relId        BIGINT UNSIGNED NOT NULL,
    reactionType CHAR(10)        NOT NULL,
    point        INT             NOT NULL,
    CONSTRAINT fk_rp_member FOREIGN KEY (memberId) REFERENCES member (id) ON DELETE CASCADE,
    UNIQUE KEY UK_memberRel (memberId, relTypeCode, relId)
);

/* ───────────── INITIAL DATA ───────────── */
INSERT INTO workType (regDate, updateDate, name)
VALUES (NOW(), NOW(), 'Movie'),
       (NOW(), NOW(), 'Drama'),
       (NOW(), NOW(), 'Animation'),
       (NOW(), NOW(), 'Live-Action');

INSERT INTO member (regDate, updateDate, loginId, loginPw, authLevel, name, nickname,
                    cellphoneNum, email, delStatus)
VALUES (NOW(), NOW(), 'admin',
        '$2a$10$N.x2nE0r2e.2G5.8iG5.8u7a2L6E2o3W8a6L2G5.8iG5.8u7a2L6E2o', -- bcrypt('admin')
        7, 'admin', 'admin', '010-0000-0000', 'admin@admin.com', 0);
