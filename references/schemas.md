# 输出结构

校验脚本输出：

- `jd`：`{ "problem_card": {}, "warnings": [] }`
- `match`：`{ "match": {}, "warnings": [] }`
- `greeting`：`{ "candidates": [], "warnings": [] }`

错误统一为：

```json
{ "error": { "code": "...", "message": "...", "hint": "..." } }
```

退出码：成功 0，参数/结构错误 2。
