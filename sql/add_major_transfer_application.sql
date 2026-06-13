USE student_management;

CREATE TABLE IF NOT EXISTS major_transfer_application (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    target_major_id INT NOT NULL,
    reason VARCHAR(500) NOT NULL,
    status ENUM('待审核', '已通过', '已驳回') NOT NULL DEFAULT '待审核',
    apply_date DATE NOT NULL,
    review_comment VARCHAR(255),
    reviewed_at DATETIME,
    CONSTRAINT fk_transfer_application_student FOREIGN KEY (student_id) REFERENCES student(id) ON DELETE CASCADE,
    CONSTRAINT fk_transfer_application_major FOREIGN KEY (target_major_id) REFERENCES major(id)
);

DELIMITER $$

DROP PROCEDURE IF EXISTS add_major_transfer_index_if_missing$$
CREATE PROCEDURE add_major_transfer_index_if_missing(
    IN p_index_name VARCHAR(64),
    IN p_index_sql TEXT
)
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.statistics
        WHERE table_schema = DATABASE()
          AND table_name = 'major_transfer_application'
          AND index_name = p_index_name
    ) THEN
        SET @ddl = p_index_sql;
        PREPARE stmt FROM @ddl;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
    END IF;
END $$

DELIMITER ;

CALL add_major_transfer_index_if_missing(
    'idx_transfer_application_student',
    'CREATE INDEX idx_transfer_application_student ON major_transfer_application(student_id)'
);
CALL add_major_transfer_index_if_missing(
    'idx_transfer_application_status',
    'CREATE INDEX idx_transfer_application_status ON major_transfer_application(status)'
);

DROP PROCEDURE IF EXISTS add_major_transfer_index_if_missing;
