# 示例流程

```text
1. 读取 prompts/jd.md
2. 把 JD 交给宿主模型，得到 card.json
3. python scripts/validate.py --mode jd --input card.json
4. 读取 prompts/match.md，把简历 + card.json 交给宿主模型，得到 match.json
5. python scripts/validate.py --mode match --input match.json --resume resume.md
6. 读取 prompts/greeting.md，把简历 + card.json 交给宿主模型，得到 greetings.json
7. python scripts/validate.py --mode greeting --input greetings.json --resume resume.md
8. 展示问题卡、匹配结果、3 条话术
```

没有简历时：

```text
1. 只跑 JD 拆解
2. 跳过 match
3. greeting 仍可跑，但必须提示“未结合简历，回复率会下降”
```
