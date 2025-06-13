-- 데이터베이스가 존재하면 삭제 (모든 데이터 파괴)
DROP
DATABASE IF EXISTS `ltk-spring-project`;

-- 데이터베이스 생성
CREATE
DATABASE `ltk-spring-project`;

-- 생성한 데이터베이스 사용
USE
`ltk-spring-project`;

-- 테이블 생성

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
    `author`        VARCHAR(100)
);

CREATE TABLE `board`
(
    `id`         BIGINT   NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `regDate`    DATETIME NOT NULL,
    `updateDate` DATETIME NOT NULL,
    `code`       CHAR(50) NOT NULL UNIQUE,
    `name`       CHAR(20) NOT NULL UNIQUE,
    `delStatus`  TINYINT(1) UNSIGNED NOT NULL DEFAULT 0,
    `delDate`    DATETIME
);

CREATE TABLE `work`
(
    `id`               BIGINT       NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `seriesId`         BIGINT       NOT NULL,
    `regDate`          DATETIME     NOT NULL,
    `updateDate`       DATETIME     NOT NULL,
    `titleKr`          VARCHAR(255) NOT NULL,
    `titleOriginal`    VARCHAR(255),
    `type`             VARCHAR(50)  NOT NULL,
    `releaseDate`      DATE,
    `releaseSequence`  INT UNSIGNED,
    `timelineSequence` INT UNSIGNED,
    `isCompleted`      TINYINT(1) UNSIGNED DEFAULT 0,
    `description`      TEXT,
    `thumbnailUrl`     VARCHAR(255),
    FOREIGN KEY (`seriesId`) REFERENCES `series` (`id`) ON DELETE CASCADE
);

CREATE TABLE `article`
(
    `id`                BIGINT       NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `regDate`           DATETIME     NOT NULL,
    `updateDate`        DATETIME     NOT NULL,
    `memberId`          BIGINT       NOT NULL,
    `seriesId`          BIGINT       NOT NULL,
    `title`             VARCHAR(255) NOT NULL,
    `body`              TEXT         NOT NULL,
    `hitCount`          INT UNSIGNED NOT NULL DEFAULT 0,
    `goodReactionPoint` INT UNSIGNED NOT NULL DEFAULT 0,
    `badReactionPoint`  INT UNSIGNED NOT NULL DEFAULT 0,
    FOREIGN KEY (`memberId`) REFERENCES `member` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`seriesId`) REFERENCES `series` (`id`) ON DELETE CASCADE
);

CREATE TABLE `reactionPoint`
(
    `id`           BIGINT   NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `regDate`      DATETIME NOT NULL,
    `updateDate`   DATETIME NOT NULL,
    `memberId`     BIGINT   NOT NULL,
    `relTypeCode`  CHAR(50) NOT NULL,
    `relId`        BIGINT   NOT NULL,
    `reactionType` CHAR(10) NOT NULL,
    `point`        INT      NOT NULL,
    FOREIGN KEY (`memberId`) REFERENCES `member` (`id`) ON DELETE CASCADE
);

CREATE TABLE `reply`
(
    `id`                BIGINT   NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `regDate`           DATETIME NOT NULL,
    `updateDate`        DATETIME NOT NULL,
    `memberId`          BIGINT   NOT NULL,
    `relTypeCode`       CHAR(50) NOT NULL,
    `relId`             BIGINT   NOT NULL,
    `parentId`          BIGINT,
    `body`              TEXT     NOT NULL,
    `goodReactionPoint` INT UNSIGNED NOT NULL DEFAULT 0,
    `badReactionPoint`  INT UNSIGNED NOT NULL DEFAULT 0,
    FOREIGN KEY (`memberId`) REFERENCES `member` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`relId`) REFERENCES `article` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`parentId`) REFERENCES `reply` (`id`) ON DELETE CASCADE
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