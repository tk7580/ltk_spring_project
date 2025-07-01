-- 기존 스키마가 있다면 삭제 (모든 데이터 파괴)
DROP
DATABASE IF EXISTS `ltk_spring_project`;
CREATE
DATABASE `ltk_spring_project`;
USE
`ltk_spring_project`;

-- ======== 기존 테이블 생성 ========
CREATE TABLE `member`
(
    `id`           BIGINT    NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `regDate`      DATETIME  NOT NULL,
    `updateDate`   DATETIME  NOT NULL,
    `loginId`      CHAR(30)  NOT NULL UNIQUE,
    `loginPw`      CHAR(100) NOT NULL,
    `authLevel`    SMALLINT(2) UNSIGNED DEFAULT 3,
    `name`         CHAR(20)  NOT NULL,
    `nickname`     CHAR(20)  NOT NULL UNIQUE,
    `cellphoneNum` CHAR(20)  NOT NULL,
    `email`        CHAR(50)  NOT NULL,
    `gender`       CHAR(1),
    `birthDate`    DATE,
    `age`          SMALLINT(3) UNSIGNED,
    `delStatus`    TINYINT(1) UNSIGNED NOT NULL DEFAULT 0,
    `delDate`      DATETIME
);

CREATE TABLE `series`
(
    `id`            BIGINT       NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `regDate`       DATETIME     NOT NULL,
    `updateDate`    DATETIME     NOT NULL,
    `titleKr`       VARCHAR(255) NOT NULL,
    `titleOriginal` VARCHAR(255),
    `description`   TEXT,
    `thumbnailUrl`  VARCHAR(255),
    `coverImageUrl` VARCHAR(255),
    `author`        VARCHAR(100),
    `publisher`     VARCHAR(100),
    `studios`       VARCHAR(255)
);

CREATE TABLE `work`
(
    `id`               BIGINT        NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `seriesId`         BIGINT        NOT NULL,
    `regDate`          DATETIME      NOT NULL,
    `updateDate`       DATETIME      NOT NULL,
    `titleKr`          VARCHAR(255)  NOT NULL,
    `titleOriginal`    VARCHAR(255),
    `isOriginal`       BOOLEAN       NOT NULL DEFAULT FALSE,
    `releaseDate`      DATE,
    `watchedCount`     INT UNSIGNED  NOT NULL DEFAULT 0,
    `averageRating`    DECIMAL(4, 2) NOT NULL DEFAULT 0.00,
    `ratingCount`      INT UNSIGNED  NOT NULL DEFAULT 0,
    `episodes`         INT UNSIGNED,
    `duration`         INT UNSIGNED,
    `creators`         VARCHAR(255),
    `studios`          VARCHAR(255),
    `releaseSequence`  INT UNSIGNED,
    `timelineSequence` INT UNSIGNED,
    `isCompleted`      TINYINT(1) UNSIGNED DEFAULT 0,
    `description`      TEXT,
    `thumbnailUrl`     VARCHAR(255),
    `trailerUrl`       VARCHAR(255),
    FOREIGN KEY (`seriesId`) REFERENCES `series` (`id`) ON DELETE CASCADE
);

CREATE TABLE `work_type`
(
    `id`         BIGINT      NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `regDate`    DATETIME    NOT NULL,
    `updateDate` DATETIME    NOT NULL,
    `name`       VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE `work_type_mapping`
(
    `id`      BIGINT   NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `regDate` DATETIME NOT NULL,
    `workId`  BIGINT   NOT NULL,
    `typeId`  BIGINT   NOT NULL,
    FOREIGN KEY (`workId`) REFERENCES `work` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`typeId`) REFERENCES `work_type` (`id`) ON DELETE CASCADE,
    UNIQUE KEY `UK_workId_typeId` (`workId`, `typeId`)
);

CREATE TABLE `work_identifier`
(
    `id`         BIGINT       NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `regDate`    DATETIME     NOT NULL,
    `updateDate` DATETIME     NOT NULL,
    `workId`     BIGINT       NOT NULL,
    `sourceName` VARCHAR(50)  NOT NULL,
    `sourceId`   VARCHAR(255) NOT NULL,
    FOREIGN KEY (`workId`) REFERENCES `work` (`id`) ON DELETE CASCADE,
    UNIQUE KEY `UK_source` (`sourceName`, `sourceId`)
);

CREATE TABLE `genre`
(
    `id`         BIGINT      NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `regDate`    DATETIME    NOT NULL,
    `updateDate` DATETIME    NOT NULL,
    `name`       VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE `work_genre`
(
    `id`      BIGINT   NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `regDate` DATETIME NOT NULL,
    `workId`  BIGINT   NOT NULL,
    `genreId` BIGINT   NOT NULL,
    FOREIGN KEY (`workId`) REFERENCES `work` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`genreId`) REFERENCES `genre` (`id`) ON DELETE CASCADE,
    UNIQUE KEY `UK_workId_genreId` (`workId`, `genreId`)
);

CREATE TABLE `viewing_guide`
(
    `id`               BIGINT       NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `regDate`          DATETIME     NOT NULL,
    `updateDate`       DATETIME     NOT NULL,
    `seriesId`         BIGINT       NOT NULL,
    `guideName`        VARCHAR(100) NOT NULL,
    `guideDescription` TEXT,
    FOREIGN KEY (`seriesId`) REFERENCES `series` (`id`) ON DELETE CASCADE
);

CREATE TABLE `viewing_guide_item`
(
    `id`              BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `guideId`         BIGINT NOT NULL,
    `workId`          BIGINT NOT NULL,
    `stepNumber`      INT UNSIGNED      NOT NULL,
    `stepDescription` TEXT,
    FOREIGN KEY (`guideId`) REFERENCES `viewing_guide` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`workId`) REFERENCES `work` (`id`) ON DELETE CASCADE
);

CREATE TABLE `memberWishlistWork`
(
    `id`       BIGINT   NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `regDate`  DATETIME NOT NULL,
    `memberId` BIGINT   NOT NULL,
    `workId`   BIGINT   NOT NULL,
    FOREIGN KEY (`memberId`) REFERENCES `member` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`workId`) REFERENCES `work` (`id`) ON DELETE CASCADE,
    UNIQUE KEY (`memberId`, `workId`)
);

CREATE TABLE `memberWatchedWork`
(
    `id`          BIGINT   NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `regDate`     DATETIME NOT NULL,
    `updateDate`  DATETIME NOT NULL,
    `memberId`    BIGINT   NOT NULL,
    `workId`      BIGINT   NOT NULL,
    `watchedDate` DATE NULL,
    FOREIGN KEY (`memberId`) REFERENCES `member` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`workId`) REFERENCES `work` (`id`) ON DELETE CASCADE,
    UNIQUE KEY (`memberId`, `workId`)
);

CREATE TABLE `memberWorkRating`
(
    `id`         BIGINT        NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `regDate`    DATETIME      NOT NULL,
    `updateDate` DATETIME      NOT NULL,
    `memberId`   BIGINT        NOT NULL,
    `workId`     BIGINT        NOT NULL,
    `score`      DECIMAL(3, 1) NOT NULL,
    `comment`    TEXT NULL,
    FOREIGN KEY (`memberId`) REFERENCES `member` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`workId`) REFERENCES `work` (`id`) ON DELETE CASCADE,
    UNIQUE KEY (`memberId`, `workId`)
);

CREATE TABLE `memberWishlistSeries`
(
    `id`       BIGINT   NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `regDate`  DATETIME NOT NULL,
    `memberId` BIGINT   NOT NULL,
    `seriesId` BIGINT   NOT NULL,
    FOREIGN KEY (`memberId`) REFERENCES `member` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`seriesId`) REFERENCES `series` (`id`) ON DELETE CASCADE,
    UNIQUE KEY (`memberId`, `seriesId`)
);

CREATE TABLE `conpro`
(
    `id`             BIGINT       NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `workId`         BIGINT       NOT NULL,
    `providerType`   VARCHAR(50)  NOT NULL,
    `providerName`   VARCHAR(100) NOT NULL,
    `contentUrl`     VARCHAR(255),
    `appScheme`      VARCHAR(255),
    `additionalInfo` TEXT,
    FOREIGN KEY (`workId`) REFERENCES `work` (`id`) ON DELETE CASCADE
);

-- ======== 게시판 관련 테이블 생성 ========
CREATE TABLE `board`
(
    `id`         BIGINT       NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `regDate`    DATETIME     NOT NULL,
    `updateDate` DATETIME     NOT NULL,
    `seriesId`   BIGINT       NOT NULL UNIQUE COMMENT '시리즈와 1:1 관계',
    `name`       VARCHAR(255) NOT NULL COMMENT '게시판 이름',
    `code`       CHAR(50)     NOT NULL UNIQUE COMMENT '게시판 코드',
    FOREIGN KEY (`seriesId`) REFERENCES `series` (`id`) ON DELETE CASCADE
);

CREATE TABLE `article`
(
    `id`                BIGINT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `regDate`           DATETIME     NOT NULL,
    `updateDate`        DATETIME     NOT NULL,
    `memberId`          BIGINT       NOT NULL,
    `boardId`           BIGINT       NOT NULL COMMENT '게시판 ID',
    `title`             VARCHAR(255) NOT NULL,
    `body`              TEXT         NOT NULL,
    `hitCount`          INT UNSIGNED    NOT NULL DEFAULT 0,
    `goodReactionPoint` INT UNSIGNED    NOT NULL DEFAULT 0,
    `badReactionPoint`  INT UNSIGNED    NOT NULL DEFAULT 0,
    FOREIGN KEY (`memberId`) REFERENCES `member` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`boardId`) REFERENCES `board` (`id`) ON DELETE CASCADE
);

CREATE TABLE `article_view_log`
(
    `id`        BIGINT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `regDate`   DATETIME NOT NULL,
    `memberId`  BIGINT   NOT NULL,
    `articleId` BIGINT UNSIGNED NOT NULL,
    FOREIGN KEY (`memberId`) REFERENCES `member` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`articleId`) REFERENCES `article` (`id`) ON DELETE CASCADE,
    UNIQUE KEY `UK_memberId_articleId` (`memberId`, `articleId`)
);

CREATE TABLE `reply`
(
    `id`                BIGINT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `regDate`           DATETIME NOT NULL,
    `updateDate`        DATETIME NOT NULL,
    `memberId`          BIGINT   NOT NULL,
    `relTypeCode`       CHAR(50) NOT NULL COMMENT '관련 타입 (article)',
    `relId`             BIGINT UNSIGNED NOT NULL COMMENT '게시글 ID',
    `parentId`          BIGINT UNSIGNED COMMENT '부모 댓글 ID',
    `body`              TEXT     NOT NULL,
    `goodReactionPoint` INT UNSIGNED    NOT NULL DEFAULT 0,
    `badReactionPoint`  INT UNSIGNED    NOT NULL DEFAULT 0,
    FOREIGN KEY (`memberId`) REFERENCES `member` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`relId`) REFERENCES `article` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`parentId`) REFERENCES `reply` (`id`) ON DELETE CASCADE
);

CREATE TABLE `reactionPoint`
(
    `id`           BIGINT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `regDate`      DATETIME NOT NULL,
    `updateDate`   DATETIME NOT NULL,
    `memberId`     BIGINT   NOT NULL,
    `relTypeCode`  CHAR(50) NOT NULL COMMENT '관련 타입 (article, reply)',
    `relId`        BIGINT UNSIGNED NOT NULL COMMENT '관련 데이터 ID',
    `reactionType` CHAR(10) NOT NULL COMMENT '반응 종류 (GOOD, BAD)',
    `point`        INT      NOT NULL,
    FOREIGN KEY (`memberId`) REFERENCES `member` (`id`) ON DELETE CASCADE,
    UNIQUE KEY `UK_memberId_relTypeCode_relId` (`memberId`, `relTypeCode`, `relId`)
);

-- ======== 초기 데이터 추가 ========
INSERT INTO `work_type` (`regDate`, `updateDate`, `name`)
VALUES (NOW(), NOW(), 'Movie'),
       (NOW(), NOW(), 'Drama'),
       (NOW(), NOW(), 'Animation'),
       (NOW(), NOW(), 'Live-Action');

-- 관리자 계정 INSERT 쿼리
INSERT INTO `member` (regDate, updateDate, loginId, loginPw, authLevel, `name`, nickname, cellphoneNum, email,
                      delStatus)
VALUES (NOW(), NOW(), 'admin', '$2a$10$N.x2nE0r2e.2G5.8iG5.8u7a2L6E2o3W8a6L2G5.8iG5.8u7a2L6E2o', 7, 'admin', 'admin',
        'admin', 'admin@admin.com', 0);
