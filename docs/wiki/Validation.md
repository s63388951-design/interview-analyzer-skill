# Validation

`scripts/validate.py` 只使用 Python 标准库。

## 模式

```bash
python scripts/validate.py --mode jd --input card.json
python scripts/validate.py --mode match --input match.json --resume resume.md
python scripts/validate.py --mode greeting --input greetings.json --resume resume.md
```

## 会检查

- JSON 围栏 / 前后废话
- `problem_type` 是否四类之一
- `confidence` 是否合法
- 评分重算
- 简历数字是否可追溯
- 话术：20 字预览、疑问句、套话、证据逐字、维度/来源去重

## 输出

- `jd`：`{problem_card, warnings}`
- `match`：`{match, warnings}`
- `greeting`：`{candidates, warnings}`

有 warning 不代表失败；它表示需要人工复核。
