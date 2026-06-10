from __future__ import annotations


def calculate_total_score(usual_score: float, final_score: float) -> float:
    return round(usual_score * 0.4 + final_score * 0.6, 2)


def score_to_level(score: float) -> str:
    if score >= 90:
        return "优秀"
    if score >= 80:
        return "良好"
    if score >= 70:
        return "中等"
    if score >= 60:
        return "及格"
    return "不及格"


def classify_file_type(suffix: str) -> str:
    suffix = suffix.lower()
    if suffix in {".png", ".jpg", ".jpeg", ".gif", ".bmp"}:
        return "图片"
    if suffix in {".mp4", ".avi", ".mov", ".mkv"}:
        return "视频"
    return "文件"
