# SALA 2026

**活动：** [SALA '26](https://lasala.ai/)（南美洲语言与人工智能会议），厄瓜多尔基多
**日期：** 2026 年 3 月 11 日
**形式：** 约 60 分钟演讲（含问答环节）

## 演讲：RLHF 与后训练入门

面向具备机器学习基础但可能对后训练（post-training）或基于人类反馈的强化学习（RLHF）了解不深的读者，提供一个自成体系的入门介绍。内容涵盖从经典强化学习到现代大语言模型对齐的发展脉络、后训练究竟改变了什么、关键论文，以及 RLHF、基于验证的强化学习（RLVR）与经典强化学习之间的区别。

## 幻灯片（colloquium 格式）

幻灯片使用 Markdown 编写，并通过 [colloquium](https://github.com/natolambert/colloquium) 渲染。从仓库根目录安装教学依赖，然后在其所在目录启动幻灯片服务：

```bash
uv sync --extra teach
cd teach/SALA-2026
uv run --extra teach colloquium serve talk.md
```