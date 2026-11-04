# Interview Analyzer Skill

一个**不依赖外部模型 API、不需要 API Key**的求职分析 skill。

宿主 agent 用自己的模型完成 JD 拆解、简历匹配和打招呼话术；这个仓库提供：

- `SKILL.md`：何时使用、工作流、红线
- `prompts/`：JD / 匹配 / 话术三套提示词
- `references/`：规则、输出结构、示例
- `scripts/validate.py`：本地 JSON 归一化、评分重算、证据/数字校验、话术去重

> 只生成草稿，不自动发送 BOSS 消息。

## 为什么需要它

BOSS 插件/求职工具常见的两种极端：

- 只算「我配不配」
- 只批量发「您好，我是…」

这个 skill 补中间层：**这个岗位现在要解决什么问题 → 我的哪段经历能对上 → 一句话让对方愿意要简历**。

## 安装

### 方式 1：复制到宿主 skill 目录

```bash
git clone https://github.com/s63388951-design/interview-analyzer-skill.git
```

然后把整个目录复制到宿主对应位置，例如：

```text
~/.claude/skills/interview-analyzer/
~/.config/opencode/skills/interview-analyzer/
```

不同宿主目录不同；不确定时直接让 agent 读取本仓库的 `SKILL.md`。

### 方式 2：只在当前项目使用

把 `SKILL.md`、`prompts/`、`references/`、`scripts/` 复制到项目内，例如：

```text
.agents/skills/interview-analyzer/
```

## 使用

```text
用户：帮我分析这个岗位，顺便写句打招呼。

Agent：
1. 读 SKILL.md
2. 读 prompts/jd.md，分析 JD
3. 有简历时读 prompts/match.md
4. 读 prompts/greeting.md，生成 5 条候选
5. 用 scripts/validate.py 校验
6. 输出问题卡、匹配度、3 条话术
```

### 校验

```bash
python scripts/validate.py --mode jd --input out.json
python scripts/validate.py --mode match --input out.json --resume resume.md
python scripts/validate.py --mode greeting --input out.json --resume resume.md
```

校验脚本只使用 Python 标准库，不联网、不读 Key。

## 目录

```text
.
├─ SKILL.md
├─ prompts/
│  ├─ jd.md
│  ├─ match.md
│  └─ greeting.md
├─ references/
│  ├─ rules.md
│  ├─ schemas.md
│  └─ examples.md
├─ scripts/
│  └─ validate.py
├─ examples/
│  ├─ sample-jd.md
│  └─ sample-resume.md
└─ tests/
```

## 示例

`examples/sample-jd.md` 和 `examples/sample-resume.md` 是虚构样例，可直接用来试 prompt 和校验脚本。

## 没有简历

- JD 拆解正常执行
- 匹配跳过，标注「未结合简历」
- 话术仍可生成，但提示「回复率会下降」

## 设计边界

- 不调用任何模型 API，不要用户 API Key
- 不编造公司内幕、简历经历、数字
- 不自动发送消息
- 不做联网公司调研（后续版本）

## License

MIT
