DROP DATABASE IF EXISTS student_management;
CREATE DATABASE student_management CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE student_management;

CREATE TABLE major (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(255)
);

CREATE TABLE class (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    grade_year INT NOT NULL,
    major_id INT NOT NULL,
    CONSTRAINT fk_class_major FOREIGN KEY (major_id) REFERENCES major(id)
);

CREATE TABLE admin_user (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash CHAR(64) NOT NULL,
    full_name VARCHAR(100) NOT NULL
);

CREATE TABLE student (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_no VARCHAR(20) NOT NULL UNIQUE,
    password_hash CHAR(64) NOT NULL,
    name VARCHAR(100) NOT NULL,
    gender ENUM('男', '女') NOT NULL,
    phone VARCHAR(30),
    email VARCHAR(100),
    enrollment_year INT NOT NULL,
    status ENUM('在读', '休学', '毕业') NOT NULL DEFAULT '在读',
    major_id INT NOT NULL,
    class_id INT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_student_major FOREIGN KEY (major_id) REFERENCES major(id),
    CONSTRAINT fk_student_class FOREIGN KEY (class_id) REFERENCES class(id)
);

CREATE TABLE course (
    id INT PRIMARY KEY AUTO_INCREMENT,
    course_code VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    credit DECIMAL(4,1) NOT NULL,
    hours INT NOT NULL,
    semester VARCHAR(50) NOT NULL
);

CREATE TABLE course_selection (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    selection_date DATE NOT NULL,
    CONSTRAINT uq_selection UNIQUE (student_id, course_id),
    CONSTRAINT fk_selection_student FOREIGN KEY (student_id) REFERENCES student(id) ON DELETE CASCADE,
    CONSTRAINT fk_selection_course FOREIGN KEY (course_id) REFERENCES course(id) ON DELETE CASCADE
);

CREATE TABLE score (
    id INT PRIMARY KEY AUTO_INCREMENT,
    selection_id INT NOT NULL UNIQUE,
    usual_score DECIMAL(5,2) NOT NULL,
    final_score DECIMAL(5,2) NOT NULL,
    total_score DECIMAL(5,2) NOT NULL,
    grade_level VARCHAR(20) NOT NULL,
    last_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_score_selection FOREIGN KEY (selection_id) REFERENCES course_selection(id) ON DELETE CASCADE
);

CREATE TABLE score_audit_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    selection_id INT NOT NULL,
    old_total_score DECIMAL(5,2),
    new_total_score DECIMAL(5,2),
    changed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    note VARCHAR(255)
);

CREATE TABLE reward_punishment (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    record_type ENUM('奖励', '惩罚') NOT NULL,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    record_date DATE NOT NULL,
    CONSTRAINT fk_reward_student FOREIGN KEY (student_id) REFERENCES student(id) ON DELETE CASCADE
);

CREATE TABLE student_status_change (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    change_type ENUM('专业变更', '班级变更', '状态变更') NOT NULL,
    old_value VARCHAR(100) NOT NULL,
    new_value VARCHAR(100) NOT NULL,
    change_reason VARCHAR(255),
    change_date DATE NOT NULL,
    CONSTRAINT fk_change_student FOREIGN KEY (student_id) REFERENCES student(id) ON DELETE CASCADE
);

CREATE TABLE student_attachment (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_type ENUM('图片', '视频', '文件') NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    description VARCHAR(255),
    uploaded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_attachment_student FOREIGN KEY (student_id) REFERENCES student(id) ON DELETE CASCADE
);

CREATE INDEX idx_student_name ON student(name);
CREATE INDEX idx_student_major ON student(major_id);
CREATE INDEX idx_course_code ON course(course_code);
CREATE INDEX idx_reward_student ON reward_punishment(student_id);
CREATE INDEX idx_change_student ON student_status_change(student_id);
CREATE INDEX idx_attachment_student ON student_attachment(student_id);

DELIMITER $$

CREATE FUNCTION fn_calculate_total_score(p_usual DECIMAL(5,2), p_final DECIMAL(5,2))
RETURNS DECIMAL(5,2)
DETERMINISTIC
BEGIN
    RETURN ROUND(p_usual * 0.4 + p_final * 0.6, 2);
END $$

CREATE FUNCTION fn_score_to_level(p_score DECIMAL(5,2))
RETURNS VARCHAR(20)
DETERMINISTIC
BEGIN
    DECLARE v_level VARCHAR(20);
    IF p_score >= 90 THEN
        SET v_level = '优秀';
    ELSEIF p_score >= 80 THEN
        SET v_level = '良好';
    ELSEIF p_score >= 70 THEN
        SET v_level = '中等';
    ELSEIF p_score >= 60 THEN
        SET v_level = '及格';
    ELSE
        SET v_level = '不及格';
    END IF;
    RETURN v_level;
END $$

CREATE PROCEDURE sp_upsert_student_profile(
    IN p_student_no VARCHAR(20),
    IN p_password VARCHAR(100),
    IN p_name VARCHAR(100),
    IN p_gender VARCHAR(10),
    IN p_phone VARCHAR(30),
    IN p_email VARCHAR(100),
    IN p_enrollment_year INT,
    IN p_status VARCHAR(20),
    IN p_major_id INT,
    IN p_class_id INT
)
BEGIN
    DECLARE v_count INT DEFAULT 0;
    SELECT COUNT(*) INTO v_count FROM student WHERE student_no = p_student_no;

    IF v_count = 0 THEN
        INSERT INTO student
        (student_no, password_hash, name, gender, phone, email, enrollment_year, status, major_id, class_id)
        VALUES
        (p_student_no, SHA2(p_password, 256), p_name, p_gender, p_phone, p_email, p_enrollment_year, p_status, p_major_id, p_class_id);
    ELSE
        UPDATE student
        SET name = p_name,
            gender = p_gender,
            phone = p_phone,
            email = p_email,
            enrollment_year = p_enrollment_year,
            status = p_status,
            major_id = p_major_id,
            class_id = p_class_id,
            password_hash = IF(p_password = '', password_hash, SHA2(p_password, 256))
        WHERE student_no = p_student_no;
    END IF;
END $$

CREATE TRIGGER trg_score_before_update
BEFORE UPDATE ON score
FOR EACH ROW
BEGIN
    SET NEW.last_updated = NOW();
END $$

CREATE TRIGGER trg_score_after_update
AFTER UPDATE ON score
FOR EACH ROW
BEGIN
    INSERT INTO score_audit_log (selection_id, old_total_score, new_total_score, note)
    VALUES (NEW.selection_id, OLD.total_score, NEW.total_score, '成绩更新触发日志');
END $$

DELIMITER ;

INSERT INTO major (name, description) VALUES
('计算机科学与技术', '培养软件与系统开发能力'),
('信息管理与信息系统', '培养信息资源管理与系统分析能力');

INSERT INTO class (name, grade_year, major_id) VALUES
('计科2301', 2023, 1),
('信管2301', 2023, 2);

INSERT INTO admin_user (username, password_hash, full_name) VALUES
('admin', SHA2('Admin@123', 256), '系统管理员');

INSERT INTO student (student_no, password_hash, name, gender, phone, email, enrollment_year, status, major_id, class_id) VALUES
('PB23111001', SHA2('Stu@123', 256), '张明远', '男', '13800001001', 'pb23111001@example.com', 2023, '在读', 1, 1),
('PB23111002', SHA2('Stu@123', 256), '李思雨', '女', '13800001002', 'pb23111002@example.com', 2023, '在读', 1, 1),
('PB23111003', SHA2('Stu@123', 256), '王子涵', '男', '13800001003', 'pb23111003@example.com', 2023, '在读', 1, 1),
('PB23111004', SHA2('Stu@123', 256), '赵清雅', '女', '13800001004', 'pb23111004@example.com', 2023, '在读', 1, 1),
('PB23111005', SHA2('Stu@123', 256), '陈宇航', '男', '13800001005', 'pb23111005@example.com', 2023, '在读', 2, 2),
('PB23111006', SHA2('Stu@123', 256), '刘芷晴', '女', '13800001006', 'pb23111006@example.com', 2023, '在读', 2, 2),
('PB23111007', SHA2('Stu@123', 256), '周嘉诚', '男', '13800001007', 'pb23111007@example.com', 2023, '休学', 2, 2),
('PB23111008', SHA2('Stu@123', 256), '孙若宁', '女', '13800001008', 'pb23111008@example.com', 2023, '在读', 2, 2);

INSERT INTO course (course_code, name, credit, hours, semester) VALUES
('DB101', '数据库原理', 3.0, 48, '2024-2025-2'),
('SE201', '软件工程', 3.0, 48, '2024-2025-2'),
('PY301', 'Python 程序设计', 2.0, 32, '2024-2025-1');

INSERT INTO course_selection (student_id, course_id, selection_date) VALUES
(1, 1, '2025-03-01'),
(1, 2, '2025-03-02'),
(2, 1, '2025-03-01'),
(2, 3, '2025-03-04'),
(3, 1, '2025-03-01'),
(3, 2, '2025-03-02'),
(4, 1, '2025-03-01'),
(4, 3, '2025-03-04'),
(5, 1, '2025-03-01'),
(5, 2, '2025-03-02'),
(6, 2, '2025-03-02'),
(6, 3, '2025-03-04'),
(7, 1, '2025-03-01'),
(8, 1, '2025-03-01'),
(8, 2, '2025-03-02');

INSERT INTO score (selection_id, usual_score, final_score, total_score, grade_level) VALUES
(1, 86, 90, fn_calculate_total_score(86, 90), fn_score_to_level(fn_calculate_total_score(86, 90))),
(2, 80, 84, fn_calculate_total_score(80, 84), fn_score_to_level(fn_calculate_total_score(80, 84))),
(3, 88, 92, fn_calculate_total_score(88, 92), fn_score_to_level(fn_calculate_total_score(88, 92))),
(4, 76, 81, fn_calculate_total_score(76, 81), fn_score_to_level(fn_calculate_total_score(76, 81))),
(5, 92, 94, fn_calculate_total_score(92, 94), fn_score_to_level(fn_calculate_total_score(92, 94))),
(6, 70, 78, fn_calculate_total_score(70, 78), fn_score_to_level(fn_calculate_total_score(70, 78))),
(7, 83, 87, fn_calculate_total_score(83, 87), fn_score_to_level(fn_calculate_total_score(83, 87))),
(8, 90, 89, fn_calculate_total_score(90, 89), fn_score_to_level(fn_calculate_total_score(90, 89))),
(9, 79, 85, fn_calculate_total_score(79, 85), fn_score_to_level(fn_calculate_total_score(79, 85))),
(10, 84, 82, fn_calculate_total_score(84, 82), fn_score_to_level(fn_calculate_total_score(84, 82))),
(11, 87, 91, fn_calculate_total_score(87, 91), fn_score_to_level(fn_calculate_total_score(87, 91))),
(12, 81, 79, fn_calculate_total_score(81, 79), fn_score_to_level(fn_calculate_total_score(81, 79))),
(13, 66, 72, fn_calculate_total_score(66, 72), fn_score_to_level(fn_calculate_total_score(66, 72))),
(14, 93, 95, fn_calculate_total_score(93, 95), fn_score_to_level(fn_calculate_total_score(93, 95))),
(15, 85, 88, fn_calculate_total_score(85, 88), fn_score_to_level(fn_calculate_total_score(85, 88)));

INSERT INTO reward_punishment (student_id, record_type, title, description, record_date) VALUES
(1, '奖励', '三好学生', '2024 学年综合表现优秀', '2024-12-20'),
(2, '奖励', '数据库实验优秀', '数据库实验完成质量高', '2024-12-22'),
(5, '惩罚', '迟到通报', '因多次迟到进行通报批评', '2024-11-02'),
(8, '奖励', '优秀班干部', '班级事务组织表现突出', '2024-12-25');

INSERT INTO student_status_change (student_id, change_type, old_value, new_value, change_reason, change_date) VALUES
(1, '状态变更', '在读', '在读', '初始化示例数据', '2024-09-01'),
(7, '状态变更', '在读', '休学', '因个人原因办理休学', '2025-01-10');
