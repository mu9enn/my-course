<!--
  Copyright (c) 2025-2026 Nathan Lambert.
  Licensed under CC BY-NC-SA 4.0:
  https://creativecommons.org/licenses/by-nc-sa/4.0/
  Full license: https://github.com/natolambert/rlhf-book/blob/main/LICENSE-CHAPTERS
-->
---
prev-chapter: "Crafting Model Character and Products"
prev-url: "17-product"
page-title: "附录A：术语定义"
search-title: "附录A：术语定义"
meta-description: "RLHF、强化学习、语言模型和后训练中常用术语的定义与背景知识。"
next-chapter: "Beyond \"Just Style\""
next-url: "appendix-b-style"
lectures:
  - video: "https://www.youtube.com/watch?v=MMDNaeIFVy8&list=PLL1tdVxB1CpVpEtMHxwuR4uI4Lxjw00_y&index=2"
    label: "Lecture 0: Prerequisites"
---

# 术语定义

本附录收录 RLHF 过程中频繁出现的定义、符号与运算，并附带语言模型的快速概览——这也是本书的核心应用场景。

## 语言模型概览

大多数现代语言模型以自回归（autoregressive）的方式训练，学习 token（词、子词或字符）序列的联合概率分布。自回归的含义很简单：每个位置的预测都依赖于序列中它之前的所有 token。给定一个 token 序列 $x = (x_1, x_2, \ldots, x_T)$，模型将整个序列的概率分解为一系列条件分布的乘积：

$$P_{\theta}(x) = \prod_{t=1}^{T} P_{\theta}(x_{t} \mid x_{1}, \ldots, x_{t-1}).$$ {#eq:llming}

为了使模型能够准确预测这种分布，常见的目标是最大化训练数据在当前模型下的似然。为此，我们可以最小化负对数似然（negative log-likelihood, NLL）损失：

$$\mathcal{L}_{\text{LM}}(\theta)=-\,\mathbb{E}_{x \sim \mathcal{D}}\left[\sum_{t=1}^{T}\log P_{\theta}\left(x_t \mid x_{<t}\right)\right]. $$ {#eq:nll}

在实践中，人们使用交叉熵损失，针对序列中的每个 next-token（下一个 token）预测，将真实 token 与模型的预测进行比较来计算损失。

语言模型有众多不同的架构，在知识量、速度和其他性能指标上各有权衡。包括 ChatGPT、Claude、Gemini 在内的现代语言模型大多采用 **decoder-only Transformers**（仅解码器 Transformer）[@Vaswani2017AttentionIA]。Transformer 的核心创新在于大量使用 **self-attention**（自注意力）机制[@Bahdanau2014NeuralMT]，使模型能够直接关注上下文中的概念并学习复杂的映射关系。在本书中，特别是在第 5 章讲解奖励模型时，我们会讨论为 Transformer 添加新的 head（输出头）或修改语言建模（LM）head。LM head 是位于模型最末端的线性投影层，将模型内部嵌入空间映射到 tokenizer 空间（即词表）。本书中我们会看到，语言模型的不同 "head" 可以被应用到微调任务中，以实现模型面向不同目的的适配——在 RLHF 中，这通常在对奖励模型进行训练时出现，相关内容在第 5 章重点讨论。

## 机器学习

- **KL 散度（Kullback-Leibler divergence, $\mathcal{D}_{\text{KL}}(P || Q)$）**：衡量两个概率分布之间差异的一种指标。对于定义在同一概率空间 $\mathcal{X}$ 上的离散概率分布 $P$ 和 $Q$，从 $Q$ 到 $P$ 的 KL 散度定义为：

$$ \mathcal{D}_{\text{KL}}(P || Q) = \sum_{x \in \mathcal{X}} P(x) \log \left(\frac{P(x)}{Q(x)}\right) $$ {#eq:def_kl}

> **译者注**：KL 散度是非对称的，即 $\mathcal{D}_{\text{KL}}(P || Q) \neq \mathcal{D}_{\text{KL}}(Q || P)$。在 RLHF 中，它常被用来衡量当前策略与参考策略之间的偏离程度，起到正则化的作用——防止策略过度偏离原始模型的生成能力。

## 自然语言处理

- **偏好胜出回复（Chosen Completion, $y_c$）**：在一组候选中被评为更优的回复，也常记作 $y_{chosen}$。

- **模型回复 / 续写（Completion, $y$）**：语言模型根据 prompt 生成的输出文本。回复常记作 $y\mid x$。奖励和其他指标常以 $r(y\mid x)$ 或 $P(y\mid x)$ 的形式计算。

- **策略（Policy, $\pi$）**：在所有可能回复上的概率分布，由参数 $\theta$ 参数化：$\pi_\theta(y\mid x)$。

- **偏好关系（Preference Relation, $\succ$）**：表示一个回复优于另一个回复的符号，例如 $y_{chosen} \succ y_{rejected}$。例如，奖励模型可以预测偏好关系的概率 $P(y_c \succ y_r \mid x)$。

- **提示词（Prompt, $x$）**：输入给语言模型以生成回复或续写的文本。

- **偏好落败回复（Rejected Completion, $y_r$）**：在成对比较中被认为较差的回复。

## 强化学习

- **动作（Action, $a$）**：智能体在环境中做出的决策或行动，通常表示为 $a \in A$，其中 $A$ 是所有可能动作的集合。

- **优势函数（Advantage Function, $A$）**：优势函数 $A(s,a)$ 量化了在状态 $s$ 下采取动作 $a$ 相对于平均水平的相对收益。它定义为 $A(s,a) = Q(s,a) - V(s)$。优势函数（以及值函数）可以依赖于特定的策略，即 $A^\pi(s,a)$。

- **折扣因子（Discount Factor, $\gamma$）**：一个标量 $0 \le \gamma < 1$，通过对未来奖励进行指数级衰减来折现回报，在即时收益与长期收益之间做权衡，并保证无限视距下求和的收敛性。有时也不使用折扣，这相当于 $\gamma=1$。

- **期望奖励优化（Expectation of Reward Optimization）**：强化学习的首要目标，即最大化期望累积奖励：

  $$\max_{\theta} \mathbb{E}_{s \sim \rho_\pi, a \sim \pi_\theta}\left[\sum_{t=0}^{\infty} \gamma^t r_t\right]$$ {#eq:expect_reward_opt}

  其中 $\rho_\pi$ 是策略 $\pi$ 下的状态分布，$\gamma$ 为折扣因子。

- **有限视距奖励（Finite Horizon Reward, $J(\pi_\theta)$）**：参数化为 $\theta$ 的策略 $\pi_\theta$ 的期望有限视距折扣回报，定义为：

  $$J(\pi_\theta) = \mathbb{E}_{\tau \sim \pi_\theta} \left[ \sum_{t=0}^T \gamma^t r_t \right]$$ {#eq:finite_horizon_return}

  其中 $\tau \sim \pi_\theta$ 表示沿策略 $\pi_\theta$ 采样得到的轨迹，$T$ 为有限视距长度。

- **同策略（On-policy）**：在 RLHF 中，尤其是关于强化学习与直接对齐算法的讨论中，**同策略**数据的概念十分常见。在强化学习文献中，"同策略"意味着数据由当前形态的智能体**精确生成**；但在更广泛的偏好调优文献中，这个概念被扩展到指代来自模型某一版本的生成结果——例如，在运行任何偏好微调之前的指令微调检查点。在这种语境下，离策略（off-policy）则指由后训练中使用其他语言模型生成的数据。

- **策略（Policy, $\pi$）**，在 RLHF 中也称**策略模型**：在强化学习中，策略是智能体在给定状态下决定采取哪个动作的决策规则：$\pi(a\mid s)$。

- **策略条件值（Policy-conditioned Values, $[]^{\pi(\cdot)}$）**：在整个强化学习的推导与实现中，一个关键要素是收集依赖于特定策略的条件数据或条件值。贯穿本书，我们将在简单的值函数符号（$V,A,Q,G$）与具体的策略条件值（$V^\pi,A^\pi,Q^\pi$）之间来回切换。在期望值计算中，从依赖于特定策略的数据 $d_\pi$ 中采样同样至关重要（例如在估计 $\mathbb{E}_{s\sim d_\pi,\,a\sim\pi(\cdot\mid s)}\!\left[A^\pi(s,a)\right]$ 时，取 $s \sim d_\pi$ 且 $a \sim \pi(\cdot\mid s)$）。

- **Q 函数（Q-Function, $Q$）**：估计在给定状态下采取特定动作的期望累积回报的函数：$Q(s,a) = \mathbb{E}\left[\sum_{t=0}^{\infty} \gamma^t r_t \mid s_0 = s, a_0 = a\right]$。

- **奖励（Reward, $r$）**：一个标量值，用于指示某个动作或状态的好坏，通常记作 $r$。

- **状态（State, $s$）**：环境当前的配置或处境，通常记作 $s \in S$，其中 $S$ 为状态空间。

- **轨迹（Trajectory, $\tau$）**：轨迹 $\tau$ 是智能体经历的一系列状态、动作和奖励的序列：$\tau = (s_0, a_0, r_0, s_1, a_1, r_1, ..., s_T, a_T, r_T)$。

- **轨迹分布（Trajectory Distribution, $(\tau\mid\pi)$）**：在策略 $\pi$ 下轨迹出现的概率为 $P(\tau\mid\pi) = p(s_0)\prod_{t=0}^T \pi(a_t\mid s_t)p(s_{t+1}\mid s_t,a_t)$，其中 $p(s_0)$ 为先验状态分布，$p(s_{t+1}\mid s_t,a_t)$ 为转移概率。

- **值函数（Value Function, $V$）**：估计从某个给定状态出发的期望累积回报的函数：$V(s) = \mathbb{E}\left[\sum_{t=0}^{\infty} \gamma^t r_t \mid s_0 = s\right]$。

## 仅适用于 RLHF 的术语

- **参考模型（Reference Model, $\pi_{\text{ref}}$）**：RLHF 中用于正则化优化的一副保存好的模型参数，其输出一般作为 KL 散度正则化的基准。

## 扩展词汇表

- **思维链（Chain-of-Thought, CoT）**：思维链是语言模型的一种特定行为模式，通过引导使模型将问题分解为逐步的形式。最初的版本是通过提示词 "Let's think step-by-step" 实现的 [@wei2022chain]。

- **蒸馏（Distillation）**：蒸馏是指在训练 AI 模型时，使用一个更强模型的输出来训练另一个模型的一系列实践。这种合成数据已被证实能够打造能力强、体积小的模型。大多数模型通过以下方式明确蒸馏相关的规则：开放权重的模型通常通过许可证规定，而只能通过 API 访问的模型则通过服务条款规定。如今，"蒸馏" 一词已被 ML 文献中的一个具体技术定义所占用，存在一词多义的情况。

- **上下文学习（In-context Learning, ICL）**：此处的 "context" 指语言模型上下文窗口内的任何信息，通常是添加到 prompt 中的内容。上下文学习的最简单形式是在 prompt 之前添加若干格式相似的示例。更高级的形式则能够学习特定场景下应包含哪些信息。

- **（教师—学生）知识蒸馏（Knowledge Distillation）**：从特定的教师模型到学生模型的知识蒸馏是上文蒸馏的具体类型，也是该术语的起源。它是一种具体的深度学习方法：神经网络的损失函数被修改为从教师模型在多个候选 token 上的对数概率（logits）中学习，而不是直接从选定的输出中学习 [@hinton2015distilling]。使用知识蒸馏训练的现代模型系列的一个例子是 Gemma 2 [@team2024gemma] 或 Gemma 3。对于语言建模设置，下一个 token 的损失函数可以修改如下 [@agarwal2024policy]，其中学生模型 $P_\theta$ 从教师分布 $P_\phi$ 中学习：

$$\mathcal{L}_{\text{KD}}(\theta) = -\,\mathbb{E}_{x \sim \mathcal{D}}\left[\sum_{t=1}^{T} P_{\phi}(x_t \mid x_{<t}) \log P_{\theta}(x_t \mid x_{<t})\right]. $$ {#eq:knowledge_distillation}

- **合成数据（Synthetic Data）**：指由其他 AI 系统输出所生成的、用于训练 AI 模型的任意训练数据。它可以是从模型的开放 prompt 中生成的文本，也可以是模型改写已有内容的输出。
