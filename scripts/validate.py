#!/usr/bin/env python3
"""Interview Analyzer Skill validator.

只做本地 JSON 解析、归一化和校验，不调用任何模型、不读取 API Key。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from itertools import combinations
from pathlib import Path

PROBLEM_TYPES = ("止血型", "建设型", "转型型", "补位型")
DIMENSIONS = (
    "行业场景迁移",
    "0→1建设",
    "规模化与效率",
    "质量与验收",
    "商业化与增长",
    "跨团队复杂协作",
)
JARGON = ("赋能", "闭环", "抓手", "沉淀", "协同", "可落地", "可复用", "全链路", "打法", "方法论", "降本增效")


class ValidationError(Exception):
    def __init__(self, code: str, message: str, hint: str = ""):
        super().__init__(message)
        self.code = code
        self.message = message
        self.hint = hint


def load_json(value: str) -> object:
    text = value.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
    text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start >= 0 and end > start:
            try:
                return json.loads(re.sub(r",\s*([}\]])", r"\1", text[start : end + 1]))
            except json.JSONDecodeError:
                pass
    raise ValidationError("BAD_JSON", "输入不是合法 JSON", "让模型只输出 JSON 对象")


def read_input(path: str) -> object:
    if path == "-":
        return load_json(sys.stdin.read())
    return load_json(Path(path).read_text(encoding="utf-8"))


def read_resume(path: str) -> str:
    if not path:
        return ""
    return Path(path).read_text(encoding="utf-8")


def numbers(text: str) -> list[str]:
    return [n.replace(",", "") for n in re.findall(r"\d[\d,]*(?:\.\d+)?", text or "") if len(n.replace(".", "")) >= 2]


def dict_of(value: object) -> dict:
    return value if isinstance(value, dict) else {}


def list_of(value: object) -> list:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def text_of(value: object) -> str:
    return str(value or "").strip()


def validate_jd(raw: object) -> dict:
    data = dict_of(raw)
    warnings = []
    facts = dict_of(data.get("jd_facts"))
    keywords = dict_of(data.get("keywords"))
    triad = dict_of(data.get("triad"))
    why = dict_of(data.get("why_now"))
    card = {
        "jd_facts": {
            "company": text_of(facts.get("company")),
            "title": text_of(facts.get("title")),
            "city": text_of(facts.get("city")),
            "salary_text": text_of(facts.get("salary_text")),
            "experience": text_of(facts.get("experience")),
            "education": text_of(facts.get("education")),
            "published_hint": text_of(facts.get("published_hint")),
        },
        "hard_requirements": list_of(data.get("hard_requirements")),
        "duties": list_of(data.get("duties")),
        "duty_intents": list_of(data.get("duty_intents")),
        "keywords": {"high_freq": list_of(keywords.get("high_freq")), "implicit": list_of(keywords.get("implicit"))},
        "surface_problem": text_of(data.get("surface_problem")),
        "real_problem": text_of(data.get("real_problem")),
        "problem_type": text_of(data.get("problem_type")),
        "triad": {k: text_of(triad.get(k)) for k in ("problem", "symptom", "cost")},
        "why_now": {
            "hypothesis": text_of(why.get("hypothesis")),
            "evidence": list_of(why.get("evidence")),
            "confidence": text_of(why.get("confidence")) or "low",
            "confidence_reason": text_of(why.get("confidence_reason")),
        },
        "ideal_candidate": text_of(data.get("ideal_candidate")),
        "validation_hook": text_of(data.get("validation_hook")),
        "risks": list_of(data.get("risks")),
    }
    if card["problem_type"] not in PROBLEM_TYPES:
        warnings.append("problem_type 不在四类中，请检查")
    if card["why_now"]["confidence"] not in ("high", "medium", "low"):
        card["why_now"]["confidence"] = "low"
        warnings.append("confidence 非法，已降为 low")
    if not card["real_problem"]:
        warnings.append("real_problem 为空")
    return {"problem_card": card, "warnings": warnings}


def validate_match(raw: object, resume: str) -> dict:
    data = dict_of(raw)
    score = dict_of(data.get("score"))
    def clamp(value, low, high):
        try:
            return max(low, min(high, int(float(value))))
        except (TypeError, ValueError):
            return 0

    dims = {
        "problem_fit": clamp(score.get("problem_fit"), 0, 40),
        "method_fit": clamp(score.get("method_fit"), 0, 30),
        "evidence_fit": clamp(score.get("evidence_fit"), 0, 20),
        "risk_score": clamp(score.get("risk_score"), 0, 10),
    }
    total = sum(dims.values())
    match = {
        "score": {
            **dims,
            "total": total,
            "verdict": "主攻" if total >= 75 else "可投" if total >= 60 else "谨慎" if total >= 40 else "不建议",
            "risk_notes": list_of(score.get("risk_notes")),
        },
        "strengths": list_of(data.get("strengths")),
        "gaps": list_of(data.get("gaps")),
        "suggestions": list_of(data.get("suggestions")),
        "differentiation": text_of(data.get("differentiation")),
        "one_liner": text_of(data.get("one_liner")),
    }
    warnings = []
    if resume.strip():
        resume_numbers = set(numbers(resume))
        for item in match["strengths"]:
            if not isinstance(item, dict):
                continue
            evidence = text_of(item.get("evidence"))
            missing = [n for n in numbers(evidence) if n not in resume_numbers]
            if missing:
                item["evidence"] = ""
                warnings.append(f"优势项证据含简历中没有的数字：{'、'.join(missing)}，已清空证据")
    return {"match": match, "warnings": warnings}


def _flat(value: str) -> str:
    return re.sub(r"\s+", "", value or "")


def _similarity(a: str, b: str) -> float:
    def grams(text: str) -> set[str]:
        flat = _flat(text)
        return {flat[i : i + 3] for i in range(max(0, len(flat) - 2))}

    ga, gb = grams(a), grams(b)
    return len(ga & gb) / len(ga | gb) if ga and gb else 0.0


def select_diverse(candidates: list[dict], limit: int = 3) -> tuple[list[dict], list[str]]:
    pool = []
    seen = set()
    for item in candidates:
        key = _flat(item.get("opening_20", ""))
        if key and key not in seen:
            seen.add(key)
            pool.append(item)
    if len(pool) <= limit:
        return pool, ([] if len(pool) == limit else [f"候选不足 {limit} 条"])
    best, best_score = [], -1.0
    for combo in combinations(pool, limit):
        dims = {x.get("capability_dimension") for x in combo if x.get("capability_dimension")}
        sources = {x.get("evidence_source") for x in combo if x.get("evidence_source")}
        evidence_sets = [set(x.get("evidence_used") or []) for x in combo]
        disjoint = all(not (evidence_sets[i] & evidence_sets[j]) for i in range(limit) for j in range(i + 1, limit))
        prefixes = {x.get("opening_20", "")[:8] for x in combo}
        max_sim = max((_similarity(combo[i].get("opening_20", ""), combo[j].get("opening_20", "")) for i in range(limit) for j in range(i + 1, limit)), default=0.0)
        score = len(dims) * 100 + len(sources) * 80 + (30 if disjoint else 0) + (20 if len(prefixes) == limit else 0) - max_sim * 30
        if score > best_score:
            best, best_score = combo, score
    warnings = []
    if len({x.get("capability_dimension") for x in best if x.get("capability_dimension")}) < limit:
        warnings.append("三条候选的能力维度未完全分开")
    if len({x.get("evidence_source") for x in best if x.get("evidence_source")}) < limit:
        warnings.append("三条候选的经历来源未完全分开")
    return list(best), warnings


def validate_greetings(raw: object, resume: str) -> dict:
    data = dict_of(raw)
    items = data.get("candidates") if isinstance(data.get("candidates"), list) else raw if isinstance(raw, list) else []
    accepted, warnings = [], []
    resume_flat = _flat(resume)
    resume_numbers = set(numbers(resume))
    for index, item in enumerate(items, 1):
        if not isinstance(item, dict):
            continue
        opening = text_of(item.get("opening_20"))
        one = text_of(item.get("one_sentence")) or text_of(item.get("full_text"))
        full = text_of(item.get("full_text")) or one
        if not opening or len(opening) > 20:
            warnings.append(f"候选 {index}：opening 为空或超过 20 字，已剔除")
            continue
        if re.search(r"[？?]", opening + one + full) or re.search(r"(吗|呢|是否|还是|如何|怎么|为什么|能不能|可不可以)", opening + one + full):
            warnings.append(f"候选 {index}：出现疑问句/疑问词，已剔除")
            continue
        if any(word in one + full for word in JARGON):
            warnings.append(f"候选 {index}：出现套话，已剔除")
            continue
        if not one.startswith(opening):
            one = f"{opening}，{one}" if one else opening
            full = f"{opening}。{full}" if full else opening
        if len(one) > 120:
            warnings.append(f"候选 {index}：一句话超过 120 字，已剔除")
            continue
        evidence = [text_of(x) for x in list_of(item.get("evidence_used")) if text_of(x)]
        if resume_flat:
            kept = []
            for quote in evidence:
                if _flat(quote) and _flat(quote) in resume_flat:
                    kept.append(quote)
                else:
                    warnings.append(f"候选 {index}：证据无法逐字回溯，已移除")
            evidence = kept
            if not evidence:
                warnings.append(f"候选 {index}：没有可回溯证据，已剔除")
                continue
            missing = [n for n in numbers(one + full) if n not in resume_numbers]
            if missing:
                warnings.append(f"候选 {index}：数字无法溯源：{'、'.join(missing)}，已剔除")
                continue
        accepted.append(
            {
                "opening_20": opening,
                "one_sentence": one,
                "full_text": full,
                "angle": text_of(item.get("angle")),
                "capability_dimension": text_of(item.get("capability_dimension")),
                "evidence_source": text_of(item.get("evidence_source")),
                "cta": text_of(item.get("cta")),
                "evidence_used": evidence[:3],
                "why_it_works": text_of(item.get("why_it_works")),
            }
        )
    selected, select_warnings = select_diverse(accepted, 3)
    return {"candidates": selected, "warnings": warnings + select_warnings}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="校验 interview-analyzer skill 的 JSON 输出")
    parser.add_argument("--mode", choices=["jd", "match", "greeting"], required=True)
    parser.add_argument("--input", required=True, help="JSON 文件路径，或 - 从 stdin 读取")
    parser.add_argument("--resume", default="", help="简历文本路径（match/greeting 用于证据校验）")
    parser.add_argument("--output", default="")
    args = parser.parse_args(argv)
    try:
        raw = read_input(args.input)
        resume = read_resume(args.resume)
        if args.mode == "jd":
            result = validate_jd(raw)
        elif args.mode == "match":
            result = validate_match(raw, resume)
        else:
            result = validate_greetings(raw, resume)
        output = json.dumps(result, ensure_ascii=False, indent=2)
        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
        print(output)
        return 0
    except ValidationError as exc:
        print(json.dumps({"error": {"code": exc.code, "message": exc.message, "hint": exc.hint}}, ensure_ascii=False), file=sys.stderr)
        return 2
    except FileNotFoundError as exc:
        print(json.dumps({"error": {"code": "FILE_NOT_FOUND", "message": str(exc)}}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
