/*==============================================================*/
/* DBMS name:      MySQL 5.0                                    */
/* Created on:     2024/12/14 16:38:03                          */
/*==============================================================*/


drop trigger 违规次数更新;

drop trigger 物品状态检查;

drop procedure if exists 处理认领申请;

drop procedure if exists 申请认领物品;

drop table if exists 物品认领视图;

/*==============================================================*/
/* Table: student                                               */
/*==============================================================*/
create table student
(
   user_id              char(10) not null,
   user_name            char(10) not null,
   address              char(50),
   user_phone           char(11) not null,
   "email box"          char(50) not null,
   Detailed_address     char(50),
   user_type            char(50) not null,
   AccountStatus        char(10) not null,
   user_password        char(15) not null,
   violation            char(15) not null,
   Dishonest_list       datetime,
   primary key (user_id)
);

/*==============================================================*/
/* Table: 发布                                                    */
/*==============================================================*/
create table 发布
(
   通知编号                 char(20) not null,
   user_id              char(10) not null,
   发布通知                 text,
   primary key (通知编号, user_id)
);

/*==============================================================*/
/* Table: 失物名单表                                                 */
/*==============================================================*/
create table 失物名单表
(
   品名编号                 char(20) not null,
   拾取时间                 datetime,
   失物原因                 varchar(50),
   user_id              char(10) not null,
   primary key (品名编号)
);

/*==============================================================*/
/* Table: 投诉表                                                   */
/*==============================================================*/
create table 投诉表
(
   ComplaintID          char(10) not null,
   ClaimFormID          char(10) not null,
   user_id              char(10),
   ComplaintCategory    char(10) not null,
   ComplaintReason      char(50),
   AdminResponse        char(10) not null,
   primary key (ComplaintID)
);

/*==============================================================*/
/* Table: 物品表                                                   */
/*==============================================================*/
create table 物品表
(
   item_id              char(10) not null,
   user_id              char(10) not null,
   "Valuable simplex number" char(10),
   item_name            char(10) not null,
   item_category        char(10) not null,
   item_description     char(50),
   Location             char(10) not null,
   Time                 datetime not null,
   PublisherID          char(10) not null,
   ClaimerID            char(10),
   item_state           char(10),
   valuable             smallint,
   primary key (item_id)
);

/*==============================================================*/
/* Table: 用户登录表                                                 */
/*==============================================================*/
create table 用户登录表
(
   "Login id"           char(10) not null,
   user_id              char(10) not null,
   Login_time           datetime not null,
   Login_state          char(10) not null,
   primary key ("Login id")
);

/*==============================================================*/
/* Table: 系统通知表                                                 */
/*==============================================================*/
create table 系统通知表
(
   通知编号                 char(20) not null,
   标题                   varchar(100),
   内容                   text,
   发布时间                 datetime,
   有效期限                 datetime,
   primary key (通知编号)
);

/*==============================================================*/
/* Table: 认领记录                                                  */
/*==============================================================*/
create table 认领记录
(
   ClaimFormID          char(10) not null,
   user_id              char(10),
   item_id              char(10) not null,
   Claimer_number       char(10) not null,
   Time_of_claimant     datetime not null,
   Claimer_status       char(10) not null,
   fraudulent           char(10),
   primary key (ClaimFormID)
);

/*==============================================================*/
/* Table: 贵重单征表                                                 */
/*==============================================================*/
create table 贵重单征表
(
   "Valuable simplex number" char(10) not null,
   user_id              char(10) not null,
   item_id              char(10) not null,
   "Receiver number"    char(20) not null,
   "boarding time"      datetime,
   remarks              text,
   primary key ("Valuable simplex number")
);

/*==============================================================*/
/* View: 物品认领视图                                                 */
/*==============================================================*/
create VIEW  物品认领视图
as
SELECT 
    物品表.item_id, 
    物品表.item_name, 
    物品表.item_category, 
    物品表.Location, 
    物品表.Time, 
    物品表.item_state, 
    物品表.valuable,
    认领记录.Claimer_status
FROM 
    物品表
INNER JOIN 
    认领记录 ON 物品表.item_id = 认领记录.item_id;

alter table 发布 add constraint FK_发布2 foreign key (通知编号)
      references 系统通知表 (通知编号) on delete restrict on update restrict;

alter table 发布 add constraint FK_发布3 foreign key (user_id)
      references student (user_id) on delete restrict on update restrict;

alter table 失物名单表 add constraint FK_记录 foreign key (user_id)
      references student (user_id) on delete restrict on update restrict;

alter table 投诉表 add constraint FK_举报 foreign key (user_id)
      references student (user_id) on delete restrict on update restrict;

alter table 投诉表 add constraint FK_关联 foreign key (ClaimFormID)
      references 认领记录 (ClaimFormID) on delete restrict on update restrict;

alter table 物品表 add constraint FK_发布 foreign key (user_id)
      references student (user_id) on delete restrict on update restrict;

alter table 物品表 add constraint FK_贵重物品 foreign key ("Valuable simplex number")
      references 贵重单征表 ("Valuable simplex number") on delete restrict on update restrict;

alter table 用户登录表 add constraint FK_用户_登录 foreign key (user_id)
      references student (user_id) on delete restrict on update restrict;

alter table 认领记录 add constraint FK_发起 foreign key (user_id)
      references student (user_id) on delete restrict on update restrict;

alter table 认领记录 add constraint FK_对应 foreign key (item_id)
      references 物品表 (item_id) on delete restrict on update restrict;

alter table 贵重单征表 add constraint FK_标注 foreign key (user_id)
      references student (user_id) on delete restrict on update restrict;


CREATE DEFINER=`root`@`localhost` PROCEDURE `处理认领申请`(IN claim_id CHAR(20),
    IN new_status ENUM('待处理', '已通过', '已拒绝'))
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
END;


CREATE DEFINER=`root`@`localhost` PROCEDURE `申请认领物品`(IN item_id CHAR(20),
    IN claimer_id CHAR(10))
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
END;


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


DROP TRIGGER IF EXISTS `物品状态检查`;
DELIMITER //
CREATE TRIGGER `物品状态检查` BEFORE UPDATE ON `物品表`
FOR EACH ROW
BEGIN
    IF NEW.物品状态 = '已认领' AND OLD.物品状态 = '丢失' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = '丢失状态的物品不能直接设置为已认领';
    END IF;
END //
DELIMITER ;
