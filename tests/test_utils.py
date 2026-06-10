import unittest

from app.utils.score import calculate_total_score, classify_file_type, score_to_level


class ScoreUtilsTestCase(unittest.TestCase):
    def test_calculate_total_score(self):
        self.assertEqual(calculate_total_score(80, 90), 86.0)

    def test_score_to_level(self):
        self.assertEqual(score_to_level(95), "优秀")
        self.assertEqual(score_to_level(82), "良好")
        self.assertEqual(score_to_level(74), "中等")
        self.assertEqual(score_to_level(60), "及格")
        self.assertEqual(score_to_level(59), "不及格")

    def test_classify_file_type(self):
        self.assertEqual(classify_file_type(".png"), "图片")
        self.assertEqual(classify_file_type(".mp4"), "视频")
        self.assertEqual(classify_file_type(".zip"), "文件")


if __name__ == "__main__":
    unittest.main()
