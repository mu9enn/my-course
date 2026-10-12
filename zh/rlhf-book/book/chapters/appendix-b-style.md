<!--
  Copyright (c) 2025-2026 Nathan Lambert.
  Licensed under CC BY-NC-SA 4.0:
  https://creativecommons.org/licenses/by-nc-sa/4.0/
  Full license: https://github.com/natolambert/rlhf-book/blob/main/LICENSE-CHAPTERS
-->
---
prev-chapter: "Definitions"
prev-url: "appendix-a-definitions"
page-title: "附录 B：超越'只是风格'"
search-title: "附录 B：超越'只是风格'"
meta-description: "RLHF 和后训练在语言模型中塑造的风格、校准和信息呈现问题。"
next-chapter: "Practical Issues"
next-url: "appendix-c-practical"
lectures:
  - video: "https://www.youtube.com/watch?v=y04JhXpiI4s&list=PLL1tdVxB1CpVpEtMHxwuR4uI4Lxjw00_y"
    label: "第 9 讲：过度优化与 RLHF 的不良声誉"
---

# 附录 B：超越"只是风格"

RLHF 早期的发展为它赢得了"只是风格迁移"的声誉；其他一些尖锐的批评则关注 RLHF 如何操纵模型输出中信息的呈现方式。

本附录将解释：为什么风格对于理解 RLHF 所提供的价值至关重要——以及它如何切实地提升模型能力和用户体验。

认为 RLHF 仅仅涉及风格迁移，这一观念从两个方面阻碍了人们对 RLHF 的正确认识。

第一，RLHF 被绑定在了对模型的小幅、无关紧要的改动上。当人们讨论风格迁移时，通常不会将其视为重要或令人兴奋的事情——而是认为它肤浅。然而，风格实际上是人类价值的无尽源泉：重讲故事可以催生出新的畅销书（例如[《人类简史》](https://en.wikipedia.org/wiki/Sapiens:_A_Brief_History_of_Humankind)），并且风格是我们智力生态持续进步的基本组成部分。风格与信息本身密不可分。

第二，许多人忽略了这样一个事实：做得好的 RLHF 确实能提升主流 LLM 评估的分数。我们已经看到，不同的风格调整实际上可以通过 Llama 3 [@dubey2024llama] 对评估带来有意义的提升。Llama 3 Instruct 模型在 Arena 上取得了极高的分数，而这被认为得益于它们更具趣味的个性——它们比同时代的其他模型更加简洁和机智。无论许多 LLM 用户多么执着于基准测试分数，即便 RLHF 的唯一效果是让语言模型变得更有趣，这也是一种可交付的价值。

在本附录中，术语"话多"（chattiness）用来涵盖 RLHF 训练出的模型响应不断增长的长度，但它同时也涵盖了诸如大量使用 Markdown、表情符号、将答案格式化为项目列表等技术手段。

为让讨论更具体，下面展示了 Tülu 3 系列中同一家族两个模型在同一提示词下的完成输出——一个仅经过监督微调（SFT），另一个通过长度控制 DPO 应用了偏好微调（preference fine-tuning）。

首先，对提示词 `What is reinforcement learning from human feedback?`（精确模型为 [Llama 3.1 Tulu 3 70B SFT](https://huggingface.co/allenai/Llama-3.1-Tulu-3-70B-SFT)）的 SFT 模型输出 [@lambert2024t]：

```text
Reinforcement learning from human feedback, also known as human-in-the-loop reinforcement learning, is a subfield of machine learning where the primary goal is to train reinforcement learning agents to perform tasks by incorporating feedback from humans. This feedback can come in various forms, such as binary rewards (e.g., right or wrong), scalar rewards, preferences between actions, demonstrations, natural language instructions, or corrections to the agent's behavior.

The idea behind reinforcement learning from human feedback is to leverage human intuition and decision-making abilities to guide the learning process of the agent. In traditional reinforcement learning, an agent learns to make decisions by interacting with an environment and receiving rewards or punishments based on the outcomes of those interactions. However, defining a suitable reward function can be challenging and time-consuming, often leading to reward shaping or reward hacking, where the agent finds unexpected and often unintended ways to maximize the reward.

By using human feedback, reinforcement learning can address some of these issues by allowing humans to directly influence the learning process. Human trainers can provide real-time feedback, scale their feedback to match the complexity of the task, and update their feedback based on the agent's progress. This approach can lead to more robust and generalized agents, as they are guided not by handcrafted reward functions but by the nuanced understanding and experience of human trainers.

However, reinforcement learning from human feedback faces several challenges, such as the high cost of obtaining human feedback, subjective and inconsistent feedback, scaling issues, and methods for efficient and effective integration of human feedback into learning algorithms. Despite these challenges, the research in this area has shown promising results in various applications, including robotics, video games, prosthetics control, natural language processing, and many more.
```

以及经过 RLHF 处理后的 [Llama 3.1 Tulu 3 70B DPO](https://huggingface.co/allenai/Llama-3.1-Tulu-3-70B-DPO) 输出：

```text
Reinforcement learning from human feedback (RLHF) is a subset of reinforcement learning (RL) where the rewards that guide the learning process are provided by humans, rather than a pre-specified numerical reward function. This is particularly useful in situations where it is hard or infeasible to design a suitable reward function, or where the desired performance involves subjective judgments that humans are uniquely equipped to provide.

In traditional reinforcement learning, an agent interacts with an environment. With each interaction, the agent performs an action, receives an observation, and gets a numerical reward that tells it how well it performed in that situation. Through many such interactions, the agent learns to maximize the cumulative reward.

In contrast, in reinforcement learning from human feedback:

1. **Human Input:** Instead of a predefined reward function, the feedback comes from human evaluators, who provide qualitative, subjective judgments about the agent's performance. This feedback can be in various forms, such as numerical ratings, binary preference signals, natural language feedback, or even demonstrations showing how to improve.

2. **Feedback Loop:** Human evaluators observe the agent's actions or outcomes and provide feedback in real-time (or close to real-time). The agent learns through this iterative feedback loop, gradually adapting its behavior to align more closely with human preferences.

3. **Reward Shaping:** Because raw human feedback is not always directly usable in learning algorithms due to variability and potential bias, a reward shaping process may be involved, whereby human feedback is converted into a more stable signal that guides learning.

4. **Preference-based RL:** One common approach within RLHF is preference-based reinforcement learning, where the agent is trained by comparing pairs of actions (or outcomes) and receiving human feedback on which one is better. From these pairwise comparisons, the agent infers a reward function that it can use to guide its actions.

5. **Inverse Reinforcement Learning (IRL):** Another technique used in RLHF is IRL, which aims to infer the underlying reward function that could explain human actions or decisions, and then use that reward function to train the agent.

**Applications:**

Reinforcement Learning from human feedback has found applications in:

- **Robotics:** Teaching robots to perform tasks that are difficult to specify with predefined reward functions.
- **Game playing:** Human feedback can guide AI agents to better emulate human-like strategies or behaviors.
- **Language and content generation:** For example, suggestively guiding AI models to generate more coherent, creative, or helpful content.
- **Recommendation systems:** Human feedback can help adjust and refine the recommendations provided to users.

**Challenges:**

Using human feedback introduces some specific challenges:

1. **Scalability:** Human feedback is time-consuming and expensive to collect, and it's hard to scale to complex or high-dimensional tasks.
2. **Bias and Noise:** Human feedback can be noisy, inconsistent, and biased, leading to suboptimal learning outcomes.
3. **Alignment:** Ensuring that the reinforcement learning agent aligns with the true preferences of the human evaluator(s) and not just the superficial feedback is difficult.
4. **Safety and Misuse:** There can be concerns about the safety and ethical implications of using potentially flawed human feedback, especially if the feedback process is corrupted or gamed.

Researchers are actively working on techniques to mitigate these challenges and improve RLHF approaches. One such approach is leveraging machine learning models to amplify the efficacy of the human feedback, for example, by learning to generalize from sparse human input or by synthesizing plausible feedback in situations where direct human input is not available.
```

两个模型的回答包含相似的信息（因为都训练于同一个预训练基础模型），但偏好微调增加了更多的结构、格式和长度。这些变化反复被证明与人类对语言模型的整体偏好正相关。更多此类示例，请参考本书配套的完成输出库 [https://www.rlhfbook.com/library](https://rlhfbook.com/library)。

## 话多的平衡

RLHF 或偏好微调方法被无数人用于提升 AlpacaEval 和其他自动聊天排行榜上的分数（这些排行榜使用 LLM-as-a-judge 来近似衡量智能体在简单对话任务中的有益性、无害性和诚实性），但 RLHF 在此类指标上的巨大提升，并没有在对更难被操纵的评估（如 Arena）上产生同比例的增长。

其中的张力在于：虽然 RLHF 方法确实带来了可测量的改进，但这种训练并不总是能转化为人们真正关心的性能表现。

通过 RLHF 文献的发展，大量模型以相关方法发布，声称通过 RLHF 提升了模型的"对齐"程度，但它们往往用力过猛，发布的评估分数从误导性到毫无意义不等。

这些以对齐为动机的 RLHF 方法，如果做得好，会让模型更容易使用、更令人愉悦。这通常会反映在 MT-Bench 或 AlpacaEval 等评估工具上的明显改善上。

2023 年秋季，围绕直接偏好优化（DPO）与近端策略优化（PPO）及其他基于 RL 的偏好微调方法之间角色的争论达到了高潮——聊天评估与真实世界性能之间的平衡是争论的核心（关于权衡的技术性讨论，见第 8 章、Ivison 等人 2024 [@ivison2024unpacking]，或[这场演讲](https://youtu.be/YJMCSVLRUNs)）。

问题在于，你也可以利用 DPO 和 PPO 等技术，结合反馈循环或大量数据，在换取聊天性能的同时，严重损害模型在其他任务（如数学或编码）上的表现。

在 DPO 与 PPO 争论的爆发期间，出现了一些基准测试成绩惊人但缺乏实际意义的论文。如果这些论文发布了模型权重，它们也未能在公开使用中流行起来，因为这些模型在通用场景中并不稳健。

2023 年秋季或此后不久应用 RLHF 时，没有任何方法能让一个 70 亿参数的对齐模型在综合基准测试上真正击败 GPT-4（这种比较是必然成立的：当时的小模型不可能稳健地击败当时最好的大型前沿模型）。这似乎是不言自明的，但总有一些论文声称能做到这一点。

@fig:DNO 来自一篇名为《Direct Nash Optimization》（DNO）的论文 [@rosset2024direct]，它声称其模型在 2024 年 4 月的 7B 参数模型中，在 AlpacaEval 上达到了 state-of-the-art 的水平。

作为上下文补充，DNO 是一种批处理的、同策略的*迭代式*奖励模型 + PPO（经典 RLHF）或一次性 DPO 的替代方案，它通过将"对齐"表述为对抗偏好 oracle 寻找纳什均衡，直接优化成对偏好（胜率差距）。

当学术激励与社会广泛关注技术产生交汇时，这类挑战便会出现。

![Direct Nash Optimization（DNO）论文结果，突出显示了其小模型超越 GPT-4 等模型。Rosset 等人 2024。CC-BY 许可。](images/dno-figure.png){#fig:DNO width=550px}

即使是 2024 年 1 月的开创性论文《Self Rewarding Language Models》[@yuan2025selfrewardinglanguagemodels]，也披露了 Llama 2 70B 上 unrealistic 的高分。

当然，在那个时候，70B 模型确实能比 7B 模型更接近 GPT-4（正如我们在 2024 年令人印象深刻的 Llama 3 发布中所见），但将模型的实际情况与现代 RLHF 论文中的主张区分开来非常重要。

这些模型针对狭窄的测试集进行了调优，在与它们声称要超越的远大规模模型相比时，在实际使用中表现不佳。

许多与此类似的方法来来去去，分享了有价值的见解但也做出了过度宣传的结果，这使得 RLHF 更难被理解。

"应用了奇怪 RLHF 的模型"的一个症状往往是长度偏好（length bias）。

这种情况变得如此普遍，以至于 AlpacaEval 和 WildBench 等多个评估系统都内置了线性长度校正机制。这修补了通过增加"话多"来击败 GPT-4 或当日领先前沿模型的激励机制，创造了一种更不易被操纵的动态——较短但有用的模型也能获胜。

尽管如此，仅针对"话多"对齐聊天模型在文献中多少背负了一些声誉代价，人们承认这类狭隘的方法可能在其他方面损害模型。

阿里巴巴在 2023 年 Qwen 模型发布时的一句说明，在早期的对齐实验中多次被观察到，它放大了"话多"与性能之间的权衡 [@qwen]：

> 我们使用大量数据对模型进行了预训练，并通过监督微调和直接偏好优化对模型进行了后训练。然而，DPO 在人类偏好评估中带来了提升，却在基准测试评估中造成了性能下降。

一个做得好的权衡早期典范是 2024 年 3 月的 Starling Beta 模型 [@zhu2024starling]。该模型从另一个聊天模型 OpenChat [@wang2023openchat]（实际上由另一个完全不同的组织训练）微调而来。它的训练完全聚焦于 k-wise 奖励模型训练和 PPO 优化，使其在 Arena 上上升了 10 个名次。

模型的平均响应长度有所增加，但以一种对人工评估者确实有帮助的方式。

后续的示例，如 Olmo 3，文献中记载其经历了大量的聊天训练，但作者更倾向于选择一个在数学、编码和推理分数上更高的最终模型检查点，而不是在基于 LLM-as-a-judge 的聊天基准上分数最高的检查点 [@teamolmo2025olmo3]。

一个自然的问题是：为什么 RLHF 会让模型的回答变得更长？

从根本上说，Arena 等评估向我们表明：与简短的回答相比，模型的平均用户通常更喜欢更长、更完整的答案。对于快速评估它们的用户来说，较长的答案可能显得更详尽、更有帮助，甚至更值得信赖。

但这并不代表*每一个*用户的偏好——这些模型是训练来匹配大量数据标注者的平均偏好的，因此 RLHF 往往会让模型更加冗长。

译者注：在 RLHF 实践中，"话多"与质量的权衡是一个持续的挑战。一方面，人类标注者倾向于偏好更完整、更详细的回答；另一方面，过度扩展的回答可能引入噪音、幻觉或无关信息。现代训练方法（如长度控制的 DPO、基于过程奖励的评估）正试图在两者之间找到平衡，而非一味增加长度。

<!-- 译者新增自测题 -->

## 自测题（译者新增）

1. **概念理解**：原文指出"风格与信息本身密不可分"（"Style is intertwined with what the information is."）。请用自己的话解释这一观点，并举一个你使用 LLM 的经验中的例子。

2. **批判性思考**：DNO 论文声称其 7B 模型在 AlpacaEval 上超越了 GPT-4。结合原文讨论，分析为什么这类声明可能存在误导？哪些因素导致了这种"评估作弊"现象？

3. **技术讨论**：原文提到 AlpacaEval 和 WildBench 都引入了"线性长度校正机制"（linear length correction）。你认为这种机制为什么有效？它可能带来什么新的副作用？