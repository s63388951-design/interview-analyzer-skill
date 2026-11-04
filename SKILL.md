---
name: interview-analyzer
description: 用宿主 agent 自己的模型做 JD 拆解、简历匹配和 BOSS 打招呼话术。自带 prompts、JSON schema 和校验脚本，不需要 API Key。
---

# Interview Analyzer Skill

## 何时使用

用户要求：

- 分析岗位 JD 真正要解决什么问题
- 判断简历与岗位是否匹配
- 生成 BOSS 直聘打招呼话术
- 把 JD 拆成问题卡 / 方案卡

## 核心原则

- **不要调用外部模型 API，不要向用户要 API Key。**
- 分析由当前宿主 agent 的模型完成。
- 不自动发送 BOSS 消息。
- 不编造公司内幕、简历经历或数字。
- 不把简历全文、手机号、邮箱写进日志。

## 工作流

### 1. 读取材料

- JD：文本或图片。宿主能读图就直接读；不能读图再让用户粘贴文本。
- 简历：可选。没有简历也能做 JD 拆解。
- 用户没提供简历时只问一次；仍不提供就继续，并标注「未结合简历」。

### 2. 选择 Prompt

- 只要岗位问题卡：`prompts/jd.md`
- 岗位 + 简历匹配：`prompts/match.md`
- 打招呼话术：`prompts/greeting.md`

把 prompt 作为 system/instruction，把 JD / 简历作为 user content，交给宿主模型。要求只输出 JSON。

### 3. 校验

把模型输出保存为 `out.json`，运行：

```bash
python scripts/validate.py --mode jd --input out.json
python scripts/validate.py --mode match --input out.json --resume resume.md
python scripts/validate.py --mode greeting --input out.json --resume resume.md
```

校验会：

- 修复 JSON 围栏/前后废话
- 重算评分
- 核对数字是否能从简历追溯
- 检查话术长度、疑问句、证据、维度去重
- 输出 `warnings`

### 4. 呈现

- 先给结论：岗位真实问题 / 匹配度 / 3 条话术。
- 区分「JD 原文」「简历原文」「推断」。
- 话术只给草稿，不自动发送。

## 没有简历

- `jd` 模式正常执行。
- `match` 模式跳过，明确标注「未结合简历」。
- `greeting` 模式可生成，但必须提示回复率会下降。

## 输出结构

见 `references/schemas.md`。规则见 `references/rules.md`，示例见 `references/examples.md`。
