/*==============================================================*/
/* DBMS name:      MySQL 5.0                                    */
/* Created on:     2024/12/14 16:38:03                          */
/*==============================================================*/


drop trigger Υ���������;

drop trigger ��Ʒ״̬���;

drop procedure if exists ������������;

drop procedure if exists ����������Ʒ;

drop table if exists ��Ʒ������ͼ;

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
/* Table: ����                                                    */
/*==============================================================*/
create table ����
(
   ֪ͨ���                 char(20) not null,
   user_id              char(10) not null,
   ����֪ͨ                 text,
   primary key (֪ͨ���, user_id)
);

/*==============================================================*/
/* Table: ʧ��������                                                 */
/*==============================================================*/
create table ʧ��������
(
   Ʒ�����                 char(20) not null,
   ʰȡʱ��                 datetime,
   ʧ��ԭ��                 varchar(50),
   user_id              char(10) not null,
   primary key (Ʒ�����)
);

/*==============================================================*/
/* Table: Ͷ�߱�                                                   */
/*==============================================================*/
create table Ͷ�߱�
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
/* Table: ��Ʒ��                                                   */
/*==============================================================*/
create table ��Ʒ��
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
/* Table: �û���¼��                                                 */
/*==============================================================*/
create table �û���¼��
(
   "Login id"           char(10) not null,
   user_id              char(10) not null,
   Login_time           datetime not null,
   Login_state          char(10) not null,
   primary key ("Login id")
);

/*==============================================================*/
/* Table: ϵͳ֪ͨ��                                                 */
/*==============================================================*/
create table ϵͳ֪ͨ��
(
   ֪ͨ���                 char(20) not null,
   ����                   varchar(100),
   ����                   text,
   ����ʱ��                 datetime,
   ��Ч����                 datetime,
   primary key (֪ͨ���)
);

/*==============================================================*/
/* Table: �����¼                                                  */
/*==============================================================*/
create table �����¼
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
/* Table: ���ص�����                                                 */
/*==============================================================*/
create table ���ص�����
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
/* View: ��Ʒ������ͼ                                                 */
/*==============================================================*/
create VIEW  ��Ʒ������ͼ
as
SELECT 
    ��Ʒ��.item_id, 
    ��Ʒ��.item_name, 
    ��Ʒ��.item_category, 
    ��Ʒ��.Location, 
    ��Ʒ��.Time, 
    ��Ʒ��.item_state, 
    ��Ʒ��.valuable,
    �����¼.Claimer_status
FROM 
    ��Ʒ��
INNER JOIN 
    �����¼ ON ��Ʒ��.item_id = �����¼.item_id;

alter table ���� add constraint FK_����2 foreign key (֪ͨ���)
      references ϵͳ֪ͨ�� (֪ͨ���) on delete restrict on update restrict;

alter table ���� add constraint FK_����3 foreign key (user_id)
      references student (user_id) on delete restrict on update restrict;

alter table ʧ�������� add constraint FK_��¼ foreign key (user_id)
      references student (user_id) on delete restrict on update restrict;

alter table Ͷ�߱� add constraint FK_�ٱ� foreign key (user_id)
      references student (user_id) on delete restrict on update restrict;

alter table Ͷ�߱� add constraint FK_���� foreign key (ClaimFormID)
      references �����¼ (ClaimFormID) on delete restrict on update restrict;

alter table ��Ʒ�� add constraint FK_���� foreign key (user_id)
      references student (user_id) on delete restrict on update restrict;

alter table ��Ʒ�� add constraint FK_������Ʒ foreign key ("Valuable simplex number")
      references ���ص����� ("Valuable simplex number") on delete restrict on update restrict;

alter table �û���¼�� add constraint FK_�û�_��¼ foreign key (user_id)
      references student (user_id) on delete restrict on update restrict;

alter table �����¼ add constraint FK_���� foreign key (user_id)
      references student (user_id) on delete restrict on update restrict;

alter table �����¼ add constraint FK_��Ӧ foreign key (item_id)
      references ��Ʒ�� (item_id) on delete restrict on update restrict;

alter table ���ص����� add constraint FK_��ע foreign key (user_id)
      references student (user_id) on delete restrict on update restrict;


CREATE DEFINER=`root`@`localhost` PROCEDURE `������������`(IN claim_id CHAR(20),
    IN new_status ENUM('������', '��ͨ��', '�Ѿܾ�'))
BEGIN
    DECLARE item_id CHAR(20);
    DECLARE item_status VARCHAR(10);
    DECLARE current_claim_status VARCHAR(10);
    
    -- ��ȡ�����¼����Ʒ��Ϣ
    SELECT ��Ʒ���, ����״̬ INTO item_id, current_claim_status
    FROM �����¼��
    WHERE ������ = claim_id;
    
    SELECT ��Ʒ״̬ INTO item_status
    FROM ��Ʒ��
    WHERE ��Ʒ��� = item_id;
    
    -- �����Ʒ״̬�Ƿ�Ϊʰ��
    IF item_status != 'ʰ��' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'ֻ�ܴ���ʰ��״̬����Ʒ��������';
    END IF;
    
    -- ��������¼״̬
    IF current_claim_status != '������' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'ֻ�ܴ��������״̬����������';
    END IF;
    
    -- ��ʼ����
    START TRANSACTION;
    
    -- ���������¼״̬
    UPDATE �����¼��
    SET ����״̬ = new_status
    WHERE ������ = claim_id;
    
    -- ���ͨ�����죬������Ʒ״̬
    IF new_status = '��ͨ��' THEN
        UPDATE ��Ʒ��
        SET 
            ��Ʒ״̬ = '������',
            �����˱�� = (SELECT �����˱�� FROM �����¼�� WHERE ������ = claim_id)
        WHERE ��Ʒ��� = item_id;
    END IF;
    
    COMMIT;
END;


CREATE DEFINER=`root`@`localhost` PROCEDURE `����������Ʒ`(IN item_id CHAR(20),
    IN claimer_id CHAR(10))
BEGIN
    DECLARE item_status VARCHAR(10);
    DECLARE claim_id CHAR(20);
    
    -- �����Ʒ״̬
    SELECT ��Ʒ״̬ INTO item_status
    FROM ��Ʒ��
    WHERE ��Ʒ��� = item_id;
    
    IF item_status != 'ʰ��' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'ֻ������ʰ��״̬����Ʒ';
    END IF;
    
    -- ���������� (C + ������ʱ�� + ��λ���)
    SET claim_id = CONCAT(
        'C',
        DATE_FORMAT(NOW(), '%y%m%d%H%i'),
        LPAD((
            SELECT IFNULL(MAX(CAST(RIGHT(������, 2) AS UNSIGNED)), 0) + 1
            FROM �����¼��
            WHERE LEFT(������, 11) = CONCAT('C', DATE_FORMAT(NOW(), '%y%m%d%H%i'))
        ), 2, '0')
    );
    
    -- ���������¼
    INSERT INTO �����¼�� (
        ������,
        ��Ʒ���,
        �����˱��,
        ����ʱ��,
        ����״̬
    ) VALUES (
        claim_id,
        item_id,
        claimer_id,
        NOW(),
        '������'
    );
END;


DELIMITER //
CREATE TRIGGER `Υ���������` AFTER UPDATE ON `�û���`
FOR EACH ROW
BEGIN
    IF NEW.Υ����� >= 3 AND OLD.Υ����� < 3 THEN
        UPDATE �û��� SET 
            �˺�״̬ = TRUE,
            ����ʧ������ʱ�� = NOW()
        WHERE �û���� = NEW.�û����;
    END IF;
END //
DELIMITER ;


DROP TRIGGER IF EXISTS `��Ʒ״̬���`;
DELIMITER //
CREATE TRIGGER `��Ʒ״̬���` BEFORE UPDATE ON `��Ʒ��`
FOR EACH ROW
BEGIN
    IF NEW.��Ʒ״̬ = '������' AND OLD.��Ʒ״̬ = '��ʧ' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = '��ʧ״̬����Ʒ����ֱ������Ϊ������';
    END IF;
END //
DELIMITER ;
