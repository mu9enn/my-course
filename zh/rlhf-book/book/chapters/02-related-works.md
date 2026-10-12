<!--
  Copyright (c) 2025-2026 Nathan Lambert.
  Licensed under CC BY-NC-SA 4.0:
  https://creativecommons.org/licenses/by-nc-sa/4.0/
  Full license: https://github.com/natolambert/rlhf-book/blob/main/LICENSE-CHAPTERS
-->
---
prev-chapter: "引言"
prev-url: "01-introduction"
page-title: RLHF 简史
search-title: "第 2 章：RLHF 简史"
meta-description: "RLHF、奖励建模、偏好学习与大模型后训练背后的关键论文和历史里程碑。"
next-chapter: "训练总览"
next-url: "03-training-overview"
lectures:
  - video: "https://www.youtube.com/watch?v=MMDNaeIFVy8&list=PLL1tdVxB1CpVpEtMHxwuR4uI4Lxjw00_y&index=2"
    label: "讲座 0：先修知识"
  - video: "https://www.youtube.com/watch?v=o6l6tJQgUg4&list=PLL1tdVxB1CpVpEtMHxwuR4uI4Lxjw00_y&index=2"
    label: "讲座 1：总览（第 1–3 章）"
---

# RLHF 简史

基于人类反馈的强化学习（RLHF）及其相关方法都还很新。
我们梳理这段历史，是为了说明这些方法被形式化的时间有多晚，以及有多少内容记录在学术文献之中。
借此我们希望强调：RLHF 正在快速演进，因此本书对某些方法会保持审慎态度，并预期围绕少数核心实践的细节还可能发生调整。
另一方面，本章列出的论文和方法也解释了为什么 RLHF 流水线中的许多环节会是这样——因为其中一些奠基性论文最初解决的问题，与现代大语言模型的应用场景完全不同。

在本章中，我们详细介绍推动 RLHF 领域发展到今天的关键论文和项目。
这不打算成为对 RLHF 及其相关领域的全面综述，而是一个起点，讲述我们是如何一步步走到今天的。
本章有意聚焦于催生 ChatGPT 的近期工作。
在强化学习（RL）领域，关于从偏好中学习的文献还有很多，值得进一步探索 [@wirth2017survey]。
如果你需要更详尽的论文列表，建议查阅专门的综述论文 [@kaufmann2023survey], [@casper2023open]。

![本章讨论的 RLHF 关键发展时间线，从早期基于偏好的强化学习到 RLHF 在大语言模型中的采用。](images/rlhf_timeline.png){#fig:rlhf_timeline data-dark-src="images/rlhf_timeline-dark.png"}

## 起源至 2018 年：基于偏好的强化学习

近年来，随着深度强化学习（Deep Reinforcement Learning）的兴起，这个领域逐渐走入大众视野，并扩展为各大科技公司对大语言模型（LLM）应用研究的组成部分。
尽管如此，今天使用的许多技术仍然与早期"从偏好中学习强化学习"的核心技术密切相关。

第一篇与现代 RLHF 思路相近的论文是 *TAMER*。
*TAMER: Training an Agent Manually via Evaluative Reinforcement* 提出了一种方法：人类迭代地对智能体（agent）的行为进行评分，从而学习一个奖励模型（reward model），再利用该奖励模型来学习动作策略（policy）[@knox2008tamer]。

几乎在同一时期或稍后，另一项工作提出了 COACH 这一 actor-critic 算法，利用人类反馈（正向和负向）来调节优势函数（advantage function）[@macglashan2017interactive]。

其中最重要的一篇文献是 Christiano 等人 2017 年的工作，他们将 RLHF 应用于 Atari 游戏中智能体轨迹（trajectory）的偏好比较 [@christiano2017deep]。
这项工作紧随 DeepMind 在深度 Q 网络（DQN）方面的奠基性强化学习研究之后——DQN 证明，RL 智能体可以从头学会玩热门电子游戏。
Christiano 等人的工作表明，在某些领域，让人类在轨迹之间做选择，可能比让人类直接与环境交互更有效。这虽然依赖一些巧妙的实验设计，但成果令人印象深刻。

![Christiano 等人（2017）中核心 RLHF 循环：奖励预测器通过与轨迹片段的比较异步训练，智能体则最大化预测奖励。](images/rlhf_schematic.png){#fig:rlhf_schematic width=66% data-dark-src="images/rlhf_schematic-dark.png"}

此后，这一方法通过更直接的奖励建模得到了扩展 [@ibarz2018reward]，而在早期 RLHF 工作中采用深度学习技术的里程碑，则在一年之后出现——TAMER 被扩展为使用神经网络模型 [@warnell2018deep]。

这一时代开始转变，因为"奖励模型"这一通用概念不再仅仅被视为解决 RL 问题的工具，而是被提出作为一种研究对齐（alignment）问题的方法 [@leike2018scalable]。

## 2019 至 2022 年：基于人类偏好对语言模型的强化学习

基于人类反馈的强化学习（在其早期也被称为"基于人类偏好的强化学习"）很快被越来越多转向扩展大语言模型的人工智能实验室所采纳。
其中相当一部分工作启动于 2019 年的 GPT-2 与 2020 年的 GPT-3 之间。
2019 年的最早期工作 *Fine-Tuning Language Models from Human Preferences*（从人类偏好中微调语言模型）与现代 RLHF 工作及本书将讨论的内容有许多惊人的相似之处 [@ziegler2019fine]。
许多经典术语——例如学习奖励模型、KL 距离、反馈回路图等——正是在这篇论文中得到了形式化定义，尽管当时最终模型的评估任务和模型能力与今天的标准有所不同。
此后，RLHF 被应用于多种任务。
其中重要的例子包括：通用摘要 [@stiennon2020learning]、书籍的递归摘要 [@wu2021recursively]、指令遵循（InstructGPT）[@ouyang2022training]、浏览器辅助问答（WebGPT）[@nakano2021webgpt]、附带引用的答案生成（GopherCite）[@menick2022teaching]，以及通用对话系统（Sparrow）[@glaese2022improving]。

除应用之外，还有多篇奠基性论文为 RLHF 的未来定义了关键方向，包括：

1. 奖励模型过优化（Reward model over-optimization）[@gao2023scaling]：RL 优化器可能对偏好数据训练的模型产生过拟合，
2. 语言模型作为对齐的通用研究领域 [@askell2021general]，以及
3. 红队测试（Red teaming）[@ganguli2022red]——即评估语言模型安全性的过程。

此后，相关工作继续在改进 RLHF 以应用于聊天模型。
Anthropic 在其早期 Claude 版本中持续广泛地使用了 RLHF [@bai2022training]，同时一些早期的 RLHF 开源工具也陆续涌现 [@ramamurthy2022reinforcement], [@havrilla-etal-2023-trlx], [@vonwerra2022trl]。

## 2023 年至今：ChatGPT 时代

ChatGPT 的发布对 RLHF 在其训练中的作用说得非常清楚 [@openai2022chatgpt]：

> 我们使用基于人类反馈的强化学习（RLHF）训练了这个模型，方法与 InstructGPT 相同，只是在数据收集的设置上略有不同。

自那以后，RLHF 一直在领先语言模型中被广泛使用。
人们熟知 RLHF 也被用于 Anthropic 的 Constitutional AI（Claude）[@bai2022constitutional]、Meta 的 Llama 2 [@touvron2023llama] 和 Llama 3 [@dubey2024llama]、NVIDIA 的 Nemotron [@adler2024nemotron]、Ai2 的 Tülu 3 [@lambert2024t] 等。

今天，RLHF 正在扩展为一个更广泛的偏好微调（PreFT, preference fine-tuning）领域，包括诸多新应用：如中间推理步骤的过程奖励（process rewards）[@lightman2023let]（第 5 章介绍）；受直接偏好优化（DPO, Direct Preference Optimization）[@rafailov2024direct]启发的直接对齐算法（第 8 章介绍）；从代码或数学的执行反馈中学习 [@kumar2024training], [@singh2023beyond]，以及受 OpenAI o1 [@openai2024o1] 启发的其他在线推理方法（第 7 章介绍）。
