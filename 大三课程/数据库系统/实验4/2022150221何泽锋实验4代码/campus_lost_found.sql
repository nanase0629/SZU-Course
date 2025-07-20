SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;


-- ----------------------------
-- Table structure for 系统通知表
-- ----------------------------
DROP TABLE IF EXISTS `系统通知表`;
CREATE TABLE `系统通知表`  (
  `通知编号` char(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `标题` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `内容` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `发布时间` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `有效期限` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`通知编号`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of 系统通知表
-- ----------------------------

-- ----------------------------
-- Table structure for 失物名单表
-- ----------------------------
DROP TABLE IF EXISTS `失物名单表`;
CREATE TABLE `失物名单表`  (
  `品名编号` char(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `拾入时间` datetime NULL DEFAULT NULL,
  `失物原因` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `用户编号` char(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  PRIMARY KEY (`品名编号`) USING BTREE,
  INDEX `用户编号`(`用户编号` ASC) USING BTREE,
  CONSTRAINT `失物名单表_ibfk_1` FOREIGN KEY (`用户编号`) REFERENCES `用户表` (`用户编号`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of 失物名单表
-- ----------------------------

-- ----------------------------
-- Table structure for 投诉表
-- ----------------------------
DROP TABLE IF EXISTS `投诉表`;
CREATE TABLE `投诉表`  (
  `投诉编号` char(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `认领编号` char(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `投诉人编号` char(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `投诉类型` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `投诉原因` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `处理意见` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `处理状态` enum('待处理','已处理') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT '待处理',
  `投诉时间` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`投诉编号`) USING BTREE,
  INDEX `认领编号`(`认领编号` ASC) USING BTREE,
  INDEX `投诉人编号`(`投诉人编号` ASC) USING BTREE,
  CONSTRAINT `投诉表_ibfk_1` FOREIGN KEY (`认领编号`) REFERENCES `认领记录表` (`认领编号`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `投诉表_ibfk_2` FOREIGN KEY (`投诉人编号`) REFERENCES `用户表` (`用户编号`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of 投诉表
-- ----------------------------
INSERT INTO `投诉表` VALUES ('T231201001', 'C231201001', 'U003', '冒领', '该电脑不是该用户的，我有证据证明', NULL, '待处理', '2024-12-01 16:30:00');
INSERT INTO `投诉表` VALUES ('T231203001', 'C231203001', 'U002', '虚假信息', '钱包描述与实际不符', NULL, '待处理', '2024-12-03 14:00:00');

-- ----------------------------
-- Table structure for 物品表
-- ----------------------------
DROP TABLE IF EXISTS `物品表`;
CREATE TABLE `物品表`  (
  `物品编号` char(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `物品名称` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `物品类别` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `物品描述` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `地点` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `时间` datetime NULL DEFAULT NULL,
  `发布人编号` char(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `认领人编号` char(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `物品状态` enum('丢失','拾获','已认领') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT '丢失',
  `是否贵重` tinyint(1) NULL DEFAULT 0,
  PRIMARY KEY (`物品编号`) USING BTREE,
  INDEX `发布人编号`(`发布人编号` ASC) USING BTREE,
  INDEX `认领人编号`(`认领人编号` ASC) USING BTREE,
  CONSTRAINT `物品表_ibfk_1` FOREIGN KEY (`发布人编号`) REFERENCES `用户表` (`用户编号`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `物品表_ibfk_2` FOREIGN KEY (`认领人编号`) REFERENCES `用户表` (`用户编号`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of 物品表
-- ----------------------------
INSERT INTO `物品表` VALUES ('L231201001', '黑色笔记本电脑', '电子设备', 'ThinkPad X1 Carbon', '图书馆三楼', '2023-12-01 14:30:00', 'U001', NULL, '拾获', 1);
INSERT INTO `物品表` VALUES ('L231202001', '学生证', '证件', '学生证', '教学楼B区', '2023-12-02 09:15:00', 'U002', NULL, '丢失', 0);
INSERT INTO `物品表` VALUES ('L231203001', '蓝色钱包', '个人物品', '含有现金和银行卡', '食堂二楼', '2023-12-03 12:00:00', 'U003', NULL, '拾获', 1);
INSERT INTO `物品表` VALUES ('L231204001', 'AirPods', '电子设备', '白色无线耳机', '体育馆', '2023-12-04 16:45:00', 'U001', NULL, '丢失', 0);
INSERT INTO `物品表` VALUES ('L2412051822', '123', '123', '123', '123', '2024-05-06 00:06:00', 'A001', NULL, '丢失', 1);

-- ----------------------------
-- Table structure for 用户登录表
-- ----------------------------
DROP TABLE IF EXISTS `用户登录表`;
CREATE TABLE `用户登录表`  (
  `登录编号` char(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `用户编号` char(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `登录时间` datetime NULL DEFAULT NULL,
  `登录状态` enum('成功','失败') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT '成功',
  PRIMARY KEY (`登录编号`) USING BTREE,
  INDEX `用户编号`(`用户编号` ASC) USING BTREE,
  CONSTRAINT `用户登录表_ibfk_1` FOREIGN KEY (`用户编号`) REFERENCES `用户表` (`用户编号`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of 用户登录表
-- ----------------------------
INSERT INTO `用户登录表` VALUES ('LG241205182214', 'A001', '2024-12-05 18:22:15', '成功');
INSERT INTO `用户登录表` VALUES ('LG241205182904', 'A001', '2024-12-05 18:29:05', '成功');
INSERT INTO `用户登录表` VALUES ('LG241205182955', 'U001', '2024-12-05 18:29:56', '成功');

-- ----------------------------
-- Table structure for 用户表
-- ----------------------------
DROP TABLE IF EXISTS `用户表`;
CREATE TABLE `用户表`  (
  `用户编号` char(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `用户姓名` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `住址` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `联系电话` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `电子邮箱` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `详细地址` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `用户类型` enum('管理员','普通用户') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `账号状态` tinyint(1) NULL DEFAULT 0 COMMENT '是否冻结',
  `登录密码` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `违规次数` int NULL DEFAULT 0,
  `加入失信名单时间` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`用户编号`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of 用户表
-- ----------------------------
INSERT INTO `用户表` VALUES ('A001', '管理员', '深圳大学', '13728178163', '1732683103@qq.com', '沧海校区', '管理员', 0, 'admin123', 0, NULL);
INSERT INTO `用户表` VALUES ('U001', '张三', '深圳大学', '12345678910', '123@qq.com', '沧海校区', '普通用户', 0, 'user123', 0, NULL);
INSERT INTO `用户表` VALUES ('U002', '李四', '深圳大学', '12345678910', '234@qq.com', '沧海校区', '普通用户', 0, 'user123', 0, NULL);
INSERT INTO `用户表` VALUES ('U003', '王五', '深圳大学', '12345678910', '345@qq.com', '沧海校区', '普通用户', 0, 'user123', 0, NULL);

-- ----------------------------
-- Table structure for 认领记录表
-- ----------------------------
DROP TABLE IF EXISTS `认领记录表`;
CREATE TABLE `认领记录表`  (
  `认领编号` char(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `物品编号` char(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `认领人编号` char(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `认领时间` datetime NULL DEFAULT NULL,
  `认领状态` enum('待处理','已通过','已拒绝') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT '待处理',
  `是否冒领` tinyint(1) NULL DEFAULT 0,
  PRIMARY KEY (`认领编号`) USING BTREE,
  INDEX `物品编号`(`物品编号` ASC) USING BTREE,
  INDEX `认领人编号`(`认领人编号` ASC) USING BTREE,
  CONSTRAINT `认领记录表_ibfk_1` FOREIGN KEY (`物品编号`) REFERENCES `物品表` (`物品编号`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `认领记录表_ibfk_2` FOREIGN KEY (`认领人编号`) REFERENCES `用户表` (`用户编号`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of 认领记录表
-- ----------------------------
INSERT INTO `认领记录表` VALUES ('C231201001', 'L231201001', 'U002', '2023-12-01 15:30:00', '已通过', 0);
INSERT INTO `认领记录表` VALUES ('C231202001', 'L231202001', 'U003', '2023-12-02 10:15:00', '待处理', 0);
INSERT INTO `认领记录表` VALUES ('C231203001', 'L231203001', 'U001', '2023-12-03 13:00:00', '已拒绝', 0);

-- ----------------------------
-- Table structure for 贵重单证表
-- ----------------------------
DROP TABLE IF EXISTS `贵重单证表`;
CREATE TABLE `贵重单证表`  (
  `单证编号` char(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `物品编号` char(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `收据人编号` char(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `登记时间` datetime NULL DEFAULT NULL,
  `备注` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  PRIMARY KEY (`单证编号`) USING BTREE,
  UNIQUE INDEX `物品编号`(`物品编号` ASC) USING BTREE,
  INDEX `收据人编号`(`收据人编号` ASC) USING BTREE,
  CONSTRAINT `贵重单证表_ibfk_1` FOREIGN KEY (`物品编号`) REFERENCES `物品表` (`物品编号`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `贵重单证表_ibfk_2` FOREIGN KEY (`收据人编号`) REFERENCES `用户表` (`用户编号`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of 贵重单证表
-- ----------------------------
INSERT INTO `贵重单证表` VALUES ('G231201001', 'L231201001', 'U001', '2023-12-01 14:35:00', NULL);
INSERT INTO `贵重单证表` VALUES ('G231203001', 'L231203001', 'U003', '2023-12-03 12:05:00', NULL);
INSERT INTO `贵重单证表` VALUES ('G2412051822', 'L2412051822', 'A001', '2024-12-05 18:22:41', NULL);

-- ----------------------------
-- 视图：显示物品和认领状态
-- ----------------------------
CREATE OR REPLACE VIEW `物品认领视图` AS
SELECT 
    p.物品编号,
    p.物品名称,
    p.物品类别,
    p.地点,
    p.时间,
    p.物品状态,
    p.是否贵重,
    CASE 
        WHEN c.认领编号 IS NOT NULL THEN '已申请认领'
        ELSE '未申请认领'
    END AS 认领状态
FROM 物品表 p
LEFT JOIN 认领记录表 c ON p.物品编号 = c.物品编号;

-- ----------------------------
-- 存储过程：生成新用户编号
-- ----------------------------
DROP PROCEDURE IF EXISTS `生成用户编号`;
DELIMITER //
CREATE PROCEDURE `生成用户编号`()
BEGIN
    DECLARE new_id CHAR(10);
    SELECT CONCAT('U', LPAD(IFNULL(MAX(CAST(SUBSTRING(用户编号, 2) AS SIGNED)), 0) + 1, 3, '0'))
    INTO new_id
    FROM 用户表;
    SET @new_id = new_id;
END //
DELIMITER ;

-- ----------------------------
-- 触发器：用户违规次数更新
-- ----------------------------
DROP TRIGGER IF EXISTS `违规次数更新`;
DELIMITER //
CREATE TRIGGER `违规次数更新` AFTER UPDATE ON `用户表`
FOR EACH ROW
BEGIN
    IF NEW.违规次数 >= 3 AND OLD.违规次数 < 3 THEN
        UPDATE 用户表 SET 
            账号状态 = TRUE,
            加入失信名单时间 = NOW()
        WHERE 用户编号 = NEW.用户编号;
    END IF;
END //
DELIMITER ;

-- ----------------------------
-- 存储过程：处理认领申请
-- ----------------------------
DROP PROCEDURE IF EXISTS `处理认领申请`;
DELIMITER //
CREATE PROCEDURE `处理认领申请`(
    IN claim_id CHAR(20),
    IN new_status ENUM('待处理', '已通过', '已拒绝')
)
BEGIN
    DECLARE item_id CHAR(20);
    DECLARE item_status VARCHAR(10);
    DECLARE current_claim_status VARCHAR(10);
    
    -- 获取认领记录和物品信息
    SELECT 物品编号, 认领状态 INTO item_id, current_claim_status
    FROM 认领记录表
    WHERE 认领编号 = claim_id;
    
    SELECT 物品状态 INTO item_status
    FROM 物品表
    WHERE 物品编号 = item_id;
    
    -- 检查物品状态是否为拾获
    IF item_status != '拾获' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = '只能处理拾获状态的物品认领申请';
    END IF;
    
    -- 检查认领记录状态
    IF current_claim_status != '待处理' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = '只能处理待处理状态的认领申请';
    END IF;
    
    -- 开始处理
    START TRANSACTION;
    
    -- 更新认领记录状态
    UPDATE 认领记录表
    SET 认领状态 = new_status
    WHERE 认领编号 = claim_id;
    
    -- 如果通过认领，更新物品状态
    IF new_status = '已通过' THEN
        UPDATE 物品表
        SET 
            物品状态 = '已认领',
            认领人编号 = (SELECT 认领人编号 FROM 认领记录表 WHERE 认领编号 = claim_id)
        WHERE 物品编号 = item_id;
    END IF;
    
    COMMIT;
END //
DELIMITER ;

-- ----------------------------
-- 存储过程：申请认领物品
-- ----------------------------
DROP PROCEDURE IF EXISTS `申请认领物品`;
DELIMITER //
CREATE PROCEDURE `申请认领物品`(
    IN item_id CHAR(20),
    IN claimer_id CHAR(10)
)
BEGIN
    DECLARE item_status VARCHAR(10);
    DECLARE claim_id CHAR(20);
    
    -- 检查物品状态
    SELECT 物品状态 INTO item_status
    FROM 物品表
    WHERE 物品编号 = item_id;
    
    IF item_status != '拾获' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = '只能认领拾获状态的物品';
    END IF;
    
    -- 生成认领编号 (C + 年月日时分 + 两位序号)
    SET claim_id = CONCAT(
        'C',
        DATE_FORMAT(NOW(), '%y%m%d%H%i'),
        LPAD((
            SELECT IFNULL(MAX(CAST(RIGHT(认领编号, 2) AS UNSIGNED)), 0) + 1
            FROM 认领记录表
            WHERE LEFT(认领编号, 11) = CONCAT('C', DATE_FORMAT(NOW(), '%y%m%d%H%i'))
        ), 2, '0')
    );
    
    -- 插入认领记录
    INSERT INTO 认领记录表 (
        认领编号,
        物品编号,
        认领人编号,
        认领时间,
        认领状态
    ) VALUES (
        claim_id,
        item_id,
        claimer_id,
        NOW(),
        '待处理'
    );
END //
DELIMITER ;

SET FOREIGN_KEY_CHECKS = 1;
