# 贡献说明

## 改动范围

- `SKILL.md`：工作流与红线
- `prompts/`：提示词
- `references/`：规则与结构
- `scripts/validate.py`：本地校验

## 本地测试

```bash
python -m pytest -q
```

## 红线

- 不提交 API Key、简历、真实截图。
- 不引入外部模型 API 调用。
- 不自动发送消息。
- 改话术规则时同步更新 `references/rules.md` 和 `scripts/validate.py`。
