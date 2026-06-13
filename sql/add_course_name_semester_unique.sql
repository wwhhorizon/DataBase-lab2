USE student_management;

DELIMITER $$

DROP PROCEDURE IF EXISTS add_course_name_semester_unique_if_missing$$
CREATE PROCEDURE add_course_name_semester_unique_if_missing()
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.statistics
        WHERE table_schema = DATABASE()
          AND table_name = 'course'
          AND index_name = 'uq_course_name_semester'
    ) THEN
        ALTER TABLE course
        ADD CONSTRAINT uq_course_name_semester UNIQUE (name, semester);
    END IF;
END $$

DELIMITER ;

CALL add_course_name_semester_unique_if_missing();

DROP PROCEDURE IF EXISTS add_course_name_semester_unique_if_missing;
