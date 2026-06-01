from briefing import BriefingResult
from dry_run_output import save_briefing_json


def test_save_briefing_json(tmp_path):
    result = BriefingResult(
        articles=[
            {
                "category": "일반",
                "tier": "일반",
                "title": "Test",
                "summary": "Summary",
                "link": "https://example.com",
                "date": "2025-01-01",
                "color": 0x888888,
            }
        ],
        match_analysis=None,
        fallback_mode=False,
        skipped_count=0,
        article_count=1,
    )
    path = save_briefing_json(result, tmp_path / "out.json")
    assert path.exists()
    content = path.read_text(encoding="utf-8")
    assert "Test" in content
    assert "https://example.com" in content
