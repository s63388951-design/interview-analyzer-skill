# Getting Started

## 1. 克隆

```bash
git clone https://github.com/s63388951-design/interview-analyzer-skill.git
```

## 2. 放进宿主

常见目录：

```text
~/.claude/skills/interview-analyzer/
~/.config/opencode/skills/interview-analyzer/
```

不确定时，直接把仓库路径告诉 agent，让它读取 `SKILL.md`。

## 3. 跑一次

```text
你：帮我分析这个 JD，顺便写句打招呼。
Agent：读 SKILL.md → 读 prompts/jd.md → 分析 → 读 prompts/greeting.md → 校验 → 输出
```

## 4. 校验

```bash
python scripts/validate.py --mode jd --input out.json
python scripts/validate.py --mode greeting --input out.json --resume resume.md
```
