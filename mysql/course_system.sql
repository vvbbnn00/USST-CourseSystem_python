/*
 Navicat Premium Data Transfer

 Source Server         : local
 Source Server Type    : MySQL
 Source Server Version : 50721
 Source Host           : localhost:3306
 Source Schema         : course_system

 Target Server Type    : MySQL
 Target Server Version : 50721
 File Encoding         : 65001

 Date: 03/07/2022 00:37:05
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for courses
-- ----------------------------
DROP TABLE IF EXISTS `courses`;
CREATE TABLE `courses`
(
    `course_id`   varchar(32) COLLATE utf8_bin  NOT NULL COMMENT '课程ID，不重复',
    `title`       varchar(100) COLLATE utf8_bin NOT NULL COMMENT '课程名称',
    `description` varchar(500) COLLATE utf8_bin DEFAULT NULL COMMENT '课程描述',
    `type`        int(11)                       NOT NULL COMMENT '课程类型：0-必修、1-选修、2-公选、3-辅修',
    `semester`    varchar(10) COLLATE utf8_bin  NOT NULL COMMENT '开课学期，一个课程只能选一种开课学期，若有需要，可以在客户端复制之前的课程',
    `schedule`    text COLLATE utf8_bin         NOT NULL COMMENT '上课星期和对应节次，格式为{星期:[节次1,节次2...]}',
    `week_start`  int(11)                       NOT NULL COMMENT '开课周',
    `week_end`    int(11)                       NOT NULL COMMENT '结课周',
    `points`      float                         NOT NULL COMMENT '学分',
    `teacher`     varchar(20) COLLATE utf8_bin  NOT NULL COMMENT '开课教师，外键对应users.uid',
    `max_members` int(11)                       DEFAULT NULL COMMENT '最大选课人数',
    PRIMARY KEY (`course_id`),
    KEY `base` (`course_id`, `semester`),
    KEY `points` (`points`, `semester`, `course_id`),
    KEY `teacher` (`teacher`),
    FULLTEXT KEY `search` (`course_id`, `title`, `description`),
    CONSTRAINT `teacher` FOREIGN KEY (`teacher`) REFERENCES `users` (`uid`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8
  COLLATE = utf8_bin;

-- ----------------------------
-- Records of courses
-- ----------------------------
BEGIN;
INSERT INTO `courses`
VALUES ('2021-01-000003-01', '测试课程（一人）', '测试课程描述。', 0, '2021-1',
        '{\"1\": [], \"2\": [10,11,12], \"3\": [], \"4\": [], \"5\": [], \"6\": [], \"7\": []}', 1, 8, 0.5, '06001', 1);
INSERT INTO `courses`
VALUES ('2022-01-000001-01', '高等数学A(1)-1班',
        '高等数学是由微积分学，较深入的代数学、几何学以及它们之间的交叉内容所形成的一门基础学科。主要内容包括：数列、极限、微积分、空间解析几何与线性代数、级数、常微分方程。工科、理科、财经类研究生考试的基础科目。', 0,
        '2022-1', '{\"1\": [3,4], \"2\": [], \"3\": [1, 2], \"4\": [], \"5\": [3,4], \"6\": [], \"7\": []}', 1, 16, 6,
        '06001', 100);
INSERT INTO `courses`
VALUES ('2022-01-000001-02', '高等数学A(1)-2班',
        '高等数学是由微积分学，较深入的代数学、几何学以及它们之间的交叉内容所形成的一门基础学科。主要内容包括：数列、极限、微积分、空间解析几何与线性代数、级数、常微分方程。工科、理科、财经类研究生考试的基础科目。', 0,
        '2022-1', '{\"1\":[1,2],\"2\":[],\"3\":[3,4],\"4\":[],\"5\":[1,2],\"6\":[],\"7\":[]}', 1, 16, 6, '06002', 100);
INSERT INTO `courses`
VALUES ('2022-01-000002-01', '电路原理-1班',
        '主要内容包括：电路模型和基本定律，线性电阻网络分析，正弦稳态电路分析，三相电路，互感电路与谐振电路，周期性非正弦稳态电路分析，线性动态网络时域分析和复频域分析，双口网络，非线性电路，分布参数电路及均匀传输线，磁路。附录包括网络图论和矩阵形式网络方程，OrCAD/PSpice在电路分析中的应用。',
        0, '2022-1', '{\"1\":[1,2],\"2\":[],\"3\":[6,7],\"4\":[],\"5\":[],\"6\":[],\"7\":[]}', 1, 16, 4, '06001', 80);
INSERT INTO `courses`
VALUES ('2022-01-000003-01', '测试课程(一人)', '测试课程描述。', 0, '2022-1',
        '{\"1\":[],\"2\":[10,11,12],\"3\":[],\"4\":[],\"5\":[],\"6\":[],\"7\":[]}', 1, 8, 0.5, '06001', 1);
INSERT INTO `courses`
VALUES ('2022-01-000004-01', '客户端创建课程', '该课程由客户端创建，用于测试客户端可用性', 2, '2022-1',
        '{\"1\":[1,2],\"2\":[],\"3\":[1,2],\"4\":[],\"5\":[],\"6\":[],\"7\":[]}', 1, 16, 4, '06001', 10);
COMMIT;

-- ----------------------------
-- Table structure for selections
-- ----------------------------
DROP TABLE IF EXISTS `selections`;
CREATE TABLE `selections`
(
    `id`          int(10) unsigned zerofill    NOT NULL AUTO_INCREMENT,
    `uid`         varchar(15) COLLATE utf8_bin NOT NULL COMMENT '用户学工号',
    `course_id`   varchar(32) COLLATE utf8_bin NOT NULL COMMENT '课程编号',
    `select_date` datetime DEFAULT NULL COMMENT '选课时间',
    PRIMARY KEY (`id`),
    KEY `uid_date` (`uid`, `select_date`),
    KEY `course_id` (`course_id`),
    CONSTRAINT `course_id` FOREIGN KEY (`course_id`) REFERENCES `courses` (`course_id`),
    CONSTRAINT `uid` FOREIGN KEY (`uid`) REFERENCES `users` (`uid`)
) ENGINE = InnoDB
  AUTO_INCREMENT = 25
  DEFAULT CHARSET = utf8
  COLLATE = utf8_bin;

-- ----------------------------
-- Records of selections
-- ----------------------------
BEGIN;
INSERT INTO `selections`
VALUES (0000000016, '2135060620', '2022-01-000001-01', '2022-06-29 21:26:01');
INSERT INTO `selections`
VALUES (0000000019, '2135060620', '2022-01-000003-01', '2022-07-02 14:42:18');
INSERT INTO `selections`
VALUES (0000000020, '2135060621', '2022-01-000004-01', '2022-07-02 14:57:39');
INSERT INTO `selections`
VALUES (0000000024, '2135060620', '2022-01-000001-02', '2022-07-02 22:46:59');
COMMIT;

-- ----------------------------
-- Table structure for semester_limits
-- ----------------------------
DROP TABLE IF EXISTS `semester_limits`;
CREATE TABLE `semester_limits`
(
    `semester`  varchar(10) COLLATE utf8_bin NOT NULL COMMENT '学期',
    `max_score` float                        NOT NULL COMMENT '最大可选学分',
    PRIMARY KEY (`semester`),
    KEY `semester` (`semester`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8
  COLLATE = utf8_bin;

-- ----------------------------
-- Records of semester_limits
-- ----------------------------
BEGIN;
INSERT INTO `semester_limits`
VALUES ('2022-1', 19.5);
INSERT INTO `semester_limits`
VALUES ('2022-2', 10.5);
COMMIT;

-- ----------------------------
-- Table structure for settings
-- ----------------------------
DROP TABLE IF EXISTS `settings`;
CREATE TABLE `settings`
(
    `key`   varchar(255) COLLATE utf8_bin NOT NULL COMMENT '设置键',
    `value` varchar(255) COLLATE utf8_bin DEFAULT NULL COMMENT '设置值',
    PRIMARY KEY (`key`),
    KEY `key` (`key`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8
  COLLATE = utf8_bin;

-- ----------------------------
-- Records of settings
-- ----------------------------
BEGIN;
INSERT INTO `settings`
VALUES ('current_semester', '2022-1');
INSERT INTO `settings`
VALUES ('school_name', '上海理工大学');
COMMIT;

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`
(
    `uid`             varchar(15) COLLATE utf8_bin  NOT NULL COMMENT '用户学工号，唯一不重复',
    `passwd`          varchar(256) COLLATE utf8_bin NOT NULL COMMENT '用户密码，SHA256',
    `name`            varchar(20) COLLATE utf8_bin  NOT NULL COMMENT '用户姓名',
    `role`            int(11)                       NOT NULL COMMENT '用户角色，0-学生、1-教师、2-管理员',
    `last_login_time` datetime                      DEFAULT NULL COMMENT '最后一次登录时间',
    `last_login_ip`   varchar(200) COLLATE utf8_bin DEFAULT NULL COMMENT '最后一次登录IP',
    `status`          int(11)                       NOT NULL COMMENT '用户状态：0-启用、1-停用',
    PRIMARY KEY (`uid`),
    KEY `uid` (`uid`) USING HASH
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8
  COLLATE = utf8_bin;

-- ----------------------------
-- Records of users
-- ----------------------------
BEGIN;
INSERT INTO `users`
VALUES ('06001', '123', '教师1', 1, '2022-07-02 22:48:17',
        '192.168.30.41', 0);
INSERT INTO `users`
VALUES ('06002', '123', '教师2', 1, '2022-07-02 15:18:47',
        '192.168.30.41', 0);
INSERT INTO `users`
VALUES ('2135060620', '123', '张三', 0,
        '2022-07-02 22:45:57', '192.168.30.41', 0);
INSERT INTO `users`
VALUES ('2135060621', '123', '李四', 0, NULL, NULL, 0);
INSERT INTO `users`
VALUES ('admin1', '123', '管理员', 2, '2022-07-02 23:40:22',
        '192.168.30.41', 0);
INSERT INTO `users`
VALUES ('admin2', '123', '管理员2', 2, '2022-07-02 15:48:10',
        '192.168.30.41', 1);
COMMIT;

SET FOREIGN_KEY_CHECKS = 1;
