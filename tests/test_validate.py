from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate  # noqa: E402


def test_jd_normalize():
    result = validate.validate_jd({"real_problem": "缺验收", "problem_type": "建设型", "why_now": {"confidence": "high"}})
    assert result["problem_card"]["real_problem"] == "缺验收"
    assert result["problem_card"]["why_now"]["confidence"] == "high"


def test_match_score_recomputed():
    result = validate.validate_match(
        {
            "score": {"problem_fit": 36, "method_fit": 27, "evidence_fit": 18, "risk_score": 6},
            "strengths": [{"evidence": "覆盖1500+项目"}],
        },
        "覆盖1500+项目，建了约2000条评测集。",
    )
    assert result["match"]["score"]["total"] == 87
    assert result["match"]["score"]["verdict"] == "主攻"


def test_match_untraceable_number_cleared():
    result = validate.validate_match(
        {"score": {}, "strengths": [{"evidence": "覆盖3000+项目"}]},
        "覆盖1500+项目。",
    )
    assert result["match"]["strengths"][0]["evidence"] == ""
    assert result["warnings"]


def test_greeting_rejects_question():
    result = validate.validate_greetings(
        {"candidates": [{"opening_20": "座舱验收我建过2000条评测集", "one_sentence": "座舱验收我建过2000条评测集，你们怎么做？"}]},
        "",
    )
    assert result["candidates"] == []
    assert any("疑问" in w for w in result["warnings"])


def test_greeting_selects_three():
    base = {
        "angle": "业务结果前置",
        "cta": "简历可以发您",
        "evidence_used": ["覆盖1500+项目"],
        "why_it_works": "x",
    }
    candidates = [
        {**base, "opening_20": "座舱验收我建过2000条评测集", "one_sentence": "座舱验收我建过2000条评测集，简历可以发您。", "capability_dimension": "质量与验收", "evidence_source": "A", "evidence_used": ["建了约2000条评测集"]},
        {**base, "opening_20": "座舱项目我做到1500+覆盖", "one_sentence": "座舱项目我做到1500+覆盖，简历可以发您。", "capability_dimension": "规模化与效率", "evidence_source": "B", "evidence_used": ["覆盖1500+项目"]},
        {**base, "opening_20": "座舱平台我从0到1做过", "one_sentence": "座舱平台我从0到1做过，简历可以发您。", "capability_dimension": "0→1建设", "evidence_source": "C", "evidence_used": ["参与AI质检平台从0到1"]},
        {**base, "opening_20": "座舱交付我做过全量覆盖", "one_sentence": "座舱交付我做过全量覆盖，简历可以发您。", "capability_dimension": "跨团队复杂协作", "evidence_source": "D", "evidence_used": ["覆盖1500+项目"]},
    ]
    resume = "建了约2000条评测集，覆盖1500+项目，参与AI质检平台从0到1。"
    result = validate.validate_greetings({"candidates": candidates}, resume)
    assert len(result["candidates"]) == 3
    assert len({x["capability_dimension"] for x in result["candidates"]}) == 3
