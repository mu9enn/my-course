<!--
  Copyright (c) 2025-2026 Nathan Lambert.
  Licensed under CC BY-NC-SA 4.0:
  https://creativecommons.org/licenses/by-nc-sa/4.0/
  Full license: https://github.com/natolambert/rlhf-book/blob/main/LICENSE-CHAPTERS
-->
---
prev-chapter: "基于人类反馈的奖励建模"
prev-url: "05-reward-models"
page-title: 强化学习
search-title: "第 6 章：强化学习"
meta-description: "用于 RLHF 和大模型后训练的基于策略梯度的强化学习方法，包括 PPO、REINFORCE、RLOO、GRPO 及其实现细节。"
next-chapter: "推理与推理时扩展"
next-url: "07-reasoning"
lectures:
  - video: "https://www.youtube.com/watch?v=K_Sj_-1BUMM&list=PLL1tdVxB1CpVpEtMHxwuR4uI4Lxjw00_y&index=4"
    label: "第 3 讲：理解大模型 RL 中的基于策略梯度的算法"
  - video: "https://www.youtube.com/watch?v=i-AIMpZHgeg&list=PLL1tdVxB1CpVpEtMHxwuR4uI4Lxjw00_y&index=5"
    label: "第 4 讲：为大模型实现 RL 算法"
---

# 强化学习

在 RLHF 过程中，强化学习算法根据奖励模型的反馈缓慢地更新模型的权重。策略——即被训练的模型——会为训练集中的提示生成补全，然后奖励模型对这些补全进行打分，强化学习优化器基于这些信息执行梯度更新（概述参见 @fig:rlhf-overview）。本章将详细解释各种算法在从同策略数据中学习奖励模型信号时所涉及的数学原理和各种权衡。这些算法在大量 epoch 上运行，通常涉及数千乃至数百万个批次上的更大规模提示集合，并在每次运行之间进行梯度更新。

## 强化学习在 RLHF 中的角色

普及 RLHF 用于语言模型的算法是策略梯度的强化学习算法。这些算法，如近端策略优化（Proximal Policy Optimization, PPO）、分组相对策略优化（Group Relative Policy Optimization, GRPO）和 REINFORCE，使用最近生成的样本来更新模型（而非像 AlphaGo 等项目中使用的深度 Q 网络（Deep Q-Networks, DQN）等算法那样将得分存储在回放缓冲区中）。在本节中，我们将介绍策略梯度算法的基础知识及其在现代 RLHF 框架中的用法。

从机器学习层面来说，本节是 RLHF 流程中复杂度最高的部分。但如同大多数现代 AI 模型一样，决定其成功与否的最大因素是输入到流程中的数据。

![RLHF 训练循环概述。数据集中的一个提示被送入被调优的策略，策略生成一段补全。奖励模型对这段补全进行打分，同时冻结的初始模型（通常是 RL 之前的指令调优模型）在同一段文本上计算对数概率以计算 KL 惩罚，防止过度漂移。结合后的奖励信号驱动策略参数的强化学习更新。](images/rlhf-overview.png){#fig:rlhf-overview}

当 ChatGPT 带着 RLHF 登上舞台时，人们普遍知道其使用了 PPO 的变体，许多早期工作也围绕此展开。但随着时间推移，多项研究项目展示了 REINFORCE 类算法的潜力 [@ahmadian2024back] [@wang2024helpsteer2p]，因其相较于 PPO 更为简单（无需单独的价值模型，节省显存从而减少所需 GPU 数量）且优势估计更为简洁（无需广义优势估计 Generalized Advantage Estimation, GAE，GAE 是用于策略梯度算法中方差缩减的优势计算方法）。更多算法应运而生，包括在推理任务中尤为流行的分组相对策略优化，但总体而言这些算法大多可通过调参来适配特定任务。本章将介绍核心的策略梯度设定以及上述三种算法，因为它们在建构典范 RLHF 文献中发挥着核心作用。

在最简形式下，RLHF 的强化学习阶段需要两个模型：策略（即被训练的模型）和为其输出打分（见上一章）的奖励模型。RL 开始之前的策略副本被用作参考模型以计算 KL 惩罚（该模型是冻结的，即不会通过自动微分引擎进行梯度更新）。本章介绍的最复杂算法 PPO 额外引入了第四个模型——一个通过学习得到的价值函数，用于估计动作序列中每个 token 的好坏程度，同样也是一个大语言模型，在训练过程中会一并更新。本章中的算法主要在两个方面有所不同：一是如何估计称为**优势（advantage）**的量化指标——用于衡量模型当前的动作（补全）相对于平均水平有多好；二是如何约束策略更新，以使优化在数值上保持稳定。RLHF 流程的可视化概览（不包含价值模型）见 @fig:rlhf-overview。

符号定义参见问题设定章节。

*本章使用来自强化学习文献的 $(s, a)$ 记号，其中 $s$ 表示状态，$a$ 表示动作。在语言模型语境中，你也会经常看到 $(x, y)$，其中 $x$ 是提示，$y$ 是补全。$(s, a)$ 框架更为通用——这些算法最初是为序列决策问题设计的，在每个时间步采取动作。但许多 RLHF 实现在整个补全上视为单个动作，使得 $(x, y)$ 记号同样适用。*

***RL 速查表：**本章中所有核心 RL 损失函数的一页参考见 [rlhfbook.com/rl-cheatsheet](https://rlhfbook.com/rl-cheatsheet)。*

## 策略梯度算法

本章的核心在于理解以下形式的方程。这个方程计算的是我们训练的 $\pi_\theta$ 语言模型的梯度 $\Delta \theta$：

$$\Delta \theta \propto \Psi_t \, \nabla_\theta \log \pi_\theta(a_t \mid s_t)$$ {#eq:policy_gradient_intuition}

其中方程由两个关键成分组成：
1. $\nabla_\theta \log \pi_\theta(a_t \mid s_t)$ —— 在参数空间中让动作 $a_t$ 更可能发生的方向。
2. $\Psi_t$ —— 有多好？对结果打分的一个标量。

将它们组合起来，通过相乘，你就得到了策略梯度更新。有些内容是简单的，比如 $\Psi_t > 0$ 更新参数使 $a_t$ 更可能，$\Psi_t < 0$ 则更新使它更不可能。策略梯度计算的是哪些参数对动作有贡献以及未来是否应让该动作更可能或更不可能发生。本章后续会深入探讨不同方法及其让其在 LLM 上生效的具体技巧。

现在让我们进一步形式化这些内容。强化学习算法旨在最大化一个状态轨迹 $s \in \mathcal{S}$、动作 $a \in \mathcal{A}$ 上的未来折扣奖励（更多符号参见附录 A，定义）。智能体的目标（通常称为**回报**）是从给定时间 $t$ 开始折扣奖励之和（其中 $\gamma\in [0,1]$ 是一个优先短期奖励的因子）：

$$G_t = r_t + \gamma r_{t+1} + \cdots = \sum_{k=0}^\infty \gamma^k r_{t+k}.$$ {#eq:return_definition}

回报定义也可以递归地写为：
$$G_{t} = r_t + \gamma G_{t+1}.$$ {#eq:recursive_return}

这个回报是学习价值函数 $V(s)$ 的基础，$V(s)$ 是在给定当前状态下对未来回报的估计：

$$V(s) = \mathbb{E}\left[G_t \mid S_t = s \right].$$ {#eq:value_function}

所有策略梯度算法都优化策略 $\pi_\theta(a\mid s)$ 以最大化期望回报；这个目标可以用诱导的价值函数 $V^{\pi_\theta}(s)$ 来表达。

设 $d_0(s)$ 为初始状态分布。我们最大化的回合目标可写为：
$$
J(\theta)
\;=\;
\sum_{s} d_0(s) V^{\pi_\theta}(s),
$$ {#eq:policy_objective}

在有限马尔可夫决策过程（MDP）中，这是对可能起始状态的求和，但在实践中我们从不精确计算它。相反，我们通过从当前策略中采样 rollout 来从数据中估计它。在 RLHF 中，这通常意味着从数据集中采样提示 $x_i$ 并生成补全 $y_i \sim \pi_\theta(\cdot\mid x_i)$。设 $R(x_i, y_i)$ 表示分配给提示-补全对的标量序列级奖励；如果 $\tau_i$ 是对应的回合，这就是轨迹奖励 $R(\tau_i)$。然后我们取一个经验平均，例如：

$$
\hat{J}(\theta) = \frac{1}{B}\sum_{i=1}^{B} R(x_i, y_i),
$$ {#eq:empirical_batch_estimate}

或者，在一个每一步有奖励的 MDP 视角下，

$$
\hat{J}(\theta) = \frac{1}{B}\sum_{i=1}^{B} \sum_{t=0}^{T_i} \gamma^t r_{i,t}.
$$ {#eq:empirical_mdp_estimate}

在实践中，语言模型的 RLHF 设 $\gamma = 1$（不进行折扣），因为优化的单位是整体补全而非单独的 token——这一点将在本章后文的 MDP 与 Bandit 部分进一步讨论。

策略梯度算法的核心是计算在当前策略上有限时间期望回报的梯度。利用该期望回报 $J$，参数更新可按如下方式计算，其中 $\alpha$ 是学习率：

$$\theta \leftarrow \theta + \alpha \nabla_\theta J(\theta)$$ {#eq:policy_update}

关键实现细节在于如何计算该梯度。

### 推导策略梯度

设 $p_\theta(\tau)$ 为由初始状态分布 $d_0$、策略 $\pi_\theta$ 和环境转移动力学诱导的轨迹分布，如 @eq:trajectory_probability 中展开所示。我们想要最大化的 RL 目标的另一种表述如下：
$$
J(\theta) = \mathbb{E}_{\tau \sim p_\theta} \left[ R(\tau) \right],
$$ {#eq:policy_objective_expectation}

其中 $\tau = (s_0, a_0, s_1, a_1, \ldots)$ 是一条轨迹，$R(\tau) = \sum_{t=0}^\infty r_t$ 是该轨迹的总奖励。或者，我们可以将期望写为对所有可能轨迹的积分：
$$
J(\theta) = \int_\tau p_\theta (\tau) R(\tau) d\tau
$$ {#eq:policy_objective_integral}

注意到我们可以将轨迹概率表示为如下形式，其中 $\pi_\theta(a_t|s_t) p(s_{t+1}|s_t, a_t)$ 将策略概率与环境从状态-动作对转移到下一状态的概率相结合：
$$
p_\theta (\tau) = d_0(s_0) \prod_{t=0}^\infty \pi_\theta(a_t|s_t) p(s_{t+1}|s_t, a_t),
$$ {#eq:trajectory_probability}

如果我们对策略参数 $\theta$ 取目标 (@eq:policy_objective_expectation) 的梯度：
$$
\nabla_\theta J(\theta) = \int_\tau \nabla_\theta p_\theta (\tau) R(\tau) d\tau
$$ {#eq:policy_gradient_integral}

注意到我们可以使用[对数导数技巧](https://andrewcharlesjones.github.io/journal/log-derivative.html)将梯度的积分改写为期望：
$$
\begin{aligned}
\nabla_\theta \log p_\theta(\tau) &= \frac{\nabla_\theta p_\theta(\tau)}{p_\theta(\tau)} &\text{(from chain rule)} \\
\implies \nabla_\theta p_\theta(\tau) &= p_\theta(\tau) \nabla_\theta \log p_\theta(\tau) &\text{(rearranging)}
\end{aligned}
$$ {#eq:log_chain_rule}

使用这个对数导数技巧：
$$
\begin{aligned}
\nabla_\theta J(\theta) &= \int_\tau \nabla_\theta p_\theta (\tau) R(\tau) d\tau \\
&= \int_\tau p_\theta (\tau) R(\tau) \nabla_\theta \log p_\theta (\tau) d\tau \\
&= \mathbb{E}_{\tau \sim p_\theta} \left[ R(\tau) \nabla_\theta \log p_\theta (\tau) \right]
\end{aligned}
$$ {#eq:policy_gradient_expectation}

其中最后一步使用了轨迹分布 $p_\theta(\tau)$ 下期望的定义：对于任意函数 $f$，$\mathbb{E}_{\tau \sim p_\theta}[f(\tau)] = \int_\tau f(\tau)\,p_\theta(\tau)\,d\tau$（或在离散情况下为求和）。写成期望形式很有用，因为我们可以用 Monte Carlo rollout 来近似它，例如对于由当前策略诱导的轨迹 $\tau_i \sim p_\theta$，可以用 $\frac{1}{B}\sum_{i=1}^{B} f(\tau_i)$ 来近似。

回到推导，展开轨迹的对数概率：

$$
\log p_\theta (\tau) = \log d_0(s_0) + \sum_{t=0}^\infty \log \pi_\theta(a_t|s_t) + \sum_{t=0}^\infty \log p(s_{t+1}|s_t, a_t)
$$ {#eq:trajectory_log_prob}

现在，如果我们取上式的梯度，我们会得到：

- $\nabla_\theta \log d_0(s_0) = 0$（初始状态分布不依赖于 $\theta$）
- $\nabla_\theta \log p(s_{t+1}|s_t, a_t) = 0$（环境转移动力学不依赖于 $\theta$）
- 只有 $\nabla_\theta \log \pi_\theta(a_t|s_t)$ 存活

因此，轨迹对数概率的梯度简化为：
$$
\nabla_\theta \log p_\theta (\tau) = \sum_{t=0}^\infty \nabla_\theta \log \pi_\theta(a_t|s_t)
$$ {#eq:trajectory_log_grad}

达到这个方程是实现上的一个重要节点。这里我们看到，轨迹分布的梯度简化为来自语言模型策略概率（即我们正在训练的模型给出的 token 概率）的梯度之和。在实践中，这导致了策略梯度方程的常见形式。它们最终看起来像损失函数中的对数概率之和，然后通过自动微分计算梯度。一个你会反复看到的简短代码片段大致如下：

```python
seq_log_probs = (token_log_probs * completion_mask).sum(dim=-1)
loss = -(seq_log_probs * advantages).mean()
loss.backward()
```

你会在本章中反复看到这种形式。现在回到正式的策略梯度数学。

将其代回 @eq:policy_gradient_expectation，我们得到：
$$
\nabla_\theta J(\theta) = \mathbb{E}_{\tau \sim p_\theta} \left[ \sum_{t=0}^\infty R(\tau) \nabla_\theta \log \pi_\theta(a_t|s_t) \right]
$$ {#eq:policy_gradient_returns}

很多时候，人们使用更通用的策略梯度公式：
$$
g = \nabla_\theta J(\theta) = \mathbb{E}_{\tau \sim p_\theta} \left[ \sum_{t=0}^\infty \Psi_t \nabla_\theta \log \pi_\theta(a_t|s_t) \right]
$$ {#eq:general_gradient}

其中 $\Psi_t$ 可以是以下内容（奖励也可以由 $\gamma$ 折扣），分类学采纳自 Schulman 等人 2015 [@schulman2015high]：

1. $R(\tau) = \sum_{t=0}^{\infty} r_t$：轨迹的总奖励。
2. $\sum_{t'=t}^{\infty} r_{t'}$：在动作 $a_t$ 之后的奖励，也被称为从时间 $t$ 开始的回报 $G_t$。
3. $\sum_{t'=t}^{\infty} r_{t'} - b(s_t)$：以前公式的去基线版本。
4. $Q^{\pi}(s_t, a_t)$：状态-动作价值函数。
5. $A^{\pi}(s_t, a_t)$：优势函数，如果精确计算，它会产生最低的理论方差。
6. $r_t + \gamma V^{\pi}(s_{t+1}) - V^{\pi}(s_t)$：时序差分（Temporal Difference, TD）残差。

*基线（baseline）* 是一个用于降低策略更新方差的值（更多内容见下文）。

对于语言模型，其中一些概念并不那么适用。例如，对于确定性策略 $\pi$，状态值为 $V^{\pi}(s_t) = Q^{\pi}(s_t, \pi(s_t))$（对于最优价值函数，有 $V^*(s_t)=\max_{a_t} Q^*(s_t,a_t)$）。对于随机策略，相应的恒等式为 $V^{\pi}(s_t) = \mathbb{E}_{a_t \sim \pi(\cdot\mid s_t)}\!\left[Q^{\pi}(s_t,a_t)\right]$。Bellman 方程将 Q 和 V 联系起来：一般而言 $Q^\pi(s_t,a_t) = \mathbb{E}\!\left[r_t + \gamma V^\pi(s_{t+1}) \mid s_t, a_t\right]$，但对于状态转移是确定性的语言模型，这简化为 $Q(s_t,a_t) = r_t + \gamma V(s_{t+1})$。优势函数衡量动作 $a_t$ 相比于平均水平要好多少：

$$A(s_t,a_t) = Q(s_t,a_t) - V(s_t) = r_t + \gamma V(s_{t+1}) - V(s_t)$$ {#eq:advantage_trick}

最终这个形式恰好是时序差分（TD）残差（即上面的第 6 项）——RL 中的一个基本量，衡量价值函数的预测与实际发生之间的差距，推动价值函数更新朝向更准确的估计。在实践中，一个学习得到的价值函数 $\hat{V}$ 通过此 TD 误差来估计优势。

### 原始策略梯度（Vanilla Policy Gradient）

原始策略梯度实现通过对策略参数求导来优化 $J(\theta)$ 的上述表达式。关于时间 $t$ 回报的一个简单版本为：

$$\nabla_\theta J(\theta) = \mathbb{E}_{\tau \sim p_\theta} \left[ \sum_{t=0}^T G_t \nabla_\theta \log \pi_\theta(a_t|s_t) \right]$$ {#eq:vanilla_policy_gradient}

原始策略梯度算法的一个常见问题是梯度更新的高方差，这可以通过多种方式缓解。高方差来自通过从环境中通常数量较少的 rollout 来估计回报 $G$ 计算梯度更新，而这些估计往往容易受到噪声影响（例如，在温度 $>0$ 的情况下从语言模型生成具有随机性）。在奖励稀疏的领域中，回报估计的方差更高，因为更多的样本是 0 或 1，而非紧密聚集在一起。为了缓解这一问题，使用了各种技术来规范化价值估计，称为*基线*。基线通过多种方式实现这一目标，本质上是通过状态值相对于下游动作进行归一化（例如在优势中，即 Q 值与价值之差）。最简单的基线是奖励的批次平均或移动平均。即使是这些与动作无关的基线也可以通过不改变期望梯度来降低方差，因为对于任意状态相关的 $b(s)$，有 $\mathbb{E}_{a \sim \pi(a|s)}\!\left[b(s) \nabla_\theta \log \pi_\theta(a|s)\right] = 0$，从而大幅改善学习信号。

本章讨论的许多策略梯度算法构建在策略梯度的优势公式之上：

$$\nabla_\theta J(\theta) = \mathbb{E}_{\tau \sim p_\theta} \left[ \sum_{t=0}^T A^{\pi_\theta}(s_t, a_t) \nabla_\theta \log \pi_\theta(a_t|s_t) \right]$$ {#eq:advantage_policy_gradient}


### REINFORCE

算法 REINFORCE 可能是一个回缩词（backronym），但其所代表的算法组件对现代强化学习算法非常相关。该算法在开创性论文 *Simple statistical gradient-following algorithms for connectionist reinforcement learning* [@williams1992simple] 中定义：

> 这个名字是"REward Increment = Nonnegative Factor X Offset Reinforcement X Characteristic Eligibility"的缩略词。

这三个部分定义了如何进行*奖励增量*，即策略梯度更新。它的更新规则有三部分：

1. 非负因子：这是学习率（步长），必须为正数，例如下面的 $\alpha$。
2. 偏移强化（Offset Reinforcement）：这是奖励的基线 $b$ 或其他归一化因子，用于提高稳定性。
3. 特征可及性（Characteristic Eligibility）：将标量奖励信号分配给产生该动作的参数。Williams 将该可及性项记为 $e$（不是指数函数）。在现代策略梯度记号中，它对应于 $\nabla_\theta \log \pi_\theta(a_t \mid s_t)$。

因此，其形式看起来很熟悉：

$$ \Delta_\theta = \alpha(r - b)e $$ {#eq:REINFORCE_BASIC}

使用更现代的记号和广义回报 $G$，REINFORCE 算子表现为：

$$
\nabla_{\theta}\,J(\theta)
\;=\;
\mathbb{E}_{\tau \sim p_{\theta}}\!\left[
    \sum_{t=0}^{T}
    (G_t - b(s_t))\,\nabla_{\theta} \log \pi_{\theta}(a_t \mid s_t)
\right],
$$ {#eq:REINFORCE_with_baseline}

这里，$G_t - b(s_t)$ 是策略在当前状态下的*优势*，因此我们可以用优势 $A$ 重新表述策略梯度：

$$
\nabla_{\theta}\,J(\theta)
\;=\;
\mathbb{E}_{\tau \sim p_{\theta}}\!\left[
    \sum_{t=0}^{T}
    A_t\,\nabla_{\theta} \log \pi_{\theta}(a_t \mid s_t)
\right],
$$ {#eq:REINFORCE_with_advantage}

REINFORCE 是一种使用梯度 Monte Carlo 估计器的原始策略梯度的具体实现。

![语言模型的基本 REINFORCE 架构。塑造奖励结合了奖励模型评分和来自参考模型的 KL 惩罚。我们将在本章中基于这一结构。](images/reinforce_tikz.png){#fig:reinforce-arch data-dark-src="images/reinforce_tikz-dark.png"}

### REINFORCE Leave One Out（RLOO）

REINFORCE Leave One Out 与标准 REINFORCE 的核心实现差异在于，它使用批次中*其他*样本的平均奖励来计算基线——而不是对批次中的所有奖励取平均 [@huang2024putting] [@ahmadian2024back] [@kool2019buy]。通过从其自身的基线中排除当前样本的奖励，RLOO 基线与所评估的动作独立，这使梯度估计器精确无偏。

关键的是，这只有在为每个状态（提示）生成多个轨迹（补全）时才有效，这在语言模型强化学习的多个领域中是常见的做法。

具体而言，对于 REINFORCE Leave-One-Out（RLOO）基线，给定 $K$ 个采样的轨迹（基于一个提示采取的动作）$a_1, \dots, a_K$，针对给定提示 $s$，我们将基线明确定义为以下*逐提示*形式：

$$
b(s, a_k) = \frac{1}{K-1}\sum_{i=1, i\neq k}^{K} R(s, a_i),
$$ {#eq:RLOO_baseline}

从而得到优势：

$$
A(s, a_k) = R(s, a_k) - b(s, a_k).
$$ {#eq:RLOO_advantage}

等价地，这也可以表示为：

$$
A(s, a_k) = \frac{K}{K - 1}\left(R(s, a_k) - \frac{1}{K}\sum_{i=1}^{K} R(s, a_i)\right).
$$ {#eq:RLOO_advantage_alt}

这是一个简单、低方差的*逐提示*优势估计，与分组相对策略优化（GRPO，接下来在 PPO 之后讨论）中使用的组内相对优势密切相关。在实践中，GRPO 式训练主要在如何应用 KL 正则化方面有所不同（作为显式损失项 vs. 折叠入奖励）以及是否使用 PPO 式的比率裁剪。具体来说，规范的 GRPO 实现在损失级别应用 KL 惩罚，而 RLOO 或传统策略梯度的推导将 KL 惩罚应用于奖励本身。随着 RLHF 向可验证奖励的推理和强化学习（RLVR）转变，KL 惩罚的使用整体下降了，许多 RLHF 代码的推理变体完全关闭了它们。尽管如此，RLOO 的优势可以与 PPO 的裁剪相结合，展示了这些算法的相似之处。

RLOO 和其他不使用价值网络——即额外的模型副本（批评者），为每个 token 预测标量值 $V(s_t)$——的算法在计算损失时为每个 token 分配相同的序列级优势（或奖励）。使用学习价值网络的算法（如 PPO）为每个 token 单独分配不同的价值，从 EOS token 处达到的最终奖励进行折扣。在存在 KL 距离惩罚的情况下，RLOO 将逐 token 的 KL 累积到补全中并将该标量折叠到序列奖励中，因此最终的优势会广播到所有 token。PPO 在计算 $A_t$ 之前从逐 token 奖励中减去逐 token 的 KL，给出 token 级别的信用分配。GRPO 通常保留序列级优势，但向损失中添加单独的逐 token 项，而不是从奖励中减去它。这些细节和权衡将在本章后文讨论。

![REINFORCE Leave-One-Out（RLOO）架构。每个提示的多个补全提供无价值函数的优势估计的 leave-one-out 基线。](images/rloo_tikz.png){#fig:rloo-arch data-dark-src="images/rloo_tikz-dark.png"}

<!-- A nice formulation of LM RL loss functions is found here https://arxiv.org/pdf/2502.01600 -->

### 近端策略优化（Proximal Policy Optimization, PPO）

近端策略优化（Proximal Policy Optimization, PPO）[@schulman2017proximal] 是 Deep RL 成功背后的基础算法之一（例如 OpenAI Five，它精通 Dota 2 [@berner2019dota] 和大量研究）。PPO 最大化的目标，关于优势和策略概率，如下所示：

$$J(\theta) = \min\left(\frac{\pi_\theta(a|s)}{\pi_{\theta_{\text{old}}}(a|s)}A, \text{clip} \left( \frac{\pi_\theta(a|s)}{\pi_{\theta_{\text{old}}}(a|s)}, 1-\varepsilon, 1+\varepsilon \right) A \right).$$ {#eq:PPO_EQN}

这里，$\pi_\theta(a|s)$ 是被优化的当前策略，$\pi_{\theta_{\text{old}}}(a|s)$ 是用于收集训练数据的策略（即上一次迭代的策略）。这两个策略之间的比率来自*重要性采样（importance sampling）*，它允许我们重用基于旧策略收集的数据来估计新策略的梯度。

回顾策略梯度的优势公式 (@eq:advantage_policy_gradient)：
$$\nabla_\theta J(\theta) = \mathbb{E}_{\tau \sim p_\theta} \left[ \sum_{t=0}^T A^{\pi_\theta}(s_t, a_t) \nabla_\theta \log \pi_\theta(a_t|s_t) \right].$$ {#eq:advantage_policy_gradient_recall}

这个期望是在由 $\pi_\theta$ 诱导的轨迹分布上对轨迹采样的，但在实践中我们希望在一个从固定策略 $\pi_{\theta_{\text{old}}}$ 收集的数据批次上执行多个梯度步骤。为了纠正这种分布不匹配，我们乘以重要性权重 $\frac{\pi_\theta(a|s)}{\pi_{\theta_{\text{old}}}(a|s)}$，重新加权样本以解释它们在当前策略下相对于数据收集策略的似然差异。如果没有约束，优化这个重要性加权的目标在比率远偏离 1 时可能导致破坏性的过大策略更新。PPO 通过将比率裁剪到范围 $[1-\varepsilon, 1+\varepsilon]$ 来解决这个问题，确保策略在一个更新中不会发生过大改变。

注意，随着我们进入 PPO 及其同类算法，我们通常处理的是*目标（objective）*而非显式的梯度。这是因为 PPO 目标一旦包含 $\min$ 和裁剪操作后*没有*易于解释的分析梯度（梯度有约 4 个项，对应 @fig:ppo-obj 中的各个区域，具体取决于写法）；写出目标是传达这些算法的更清晰方式。

为完整起见，PPO 通常写为关于时间步的*期望*裁剪代理目标：

$$
J(\theta)
=
\mathbb{E}_{t}\left[
\min\left(\rho_t(\theta)A_t,\ \text{clip}(\rho_t(\theta),1-\varepsilon,1+\varepsilon)A_t\right)
\right],
\qquad
\rho_t(\theta)=\frac{\pi_\theta(a_t\mid s_t)}{\pi_{\theta_{\text{old}}}(a_t\mid s_t)}.
$$ {#eq:PPO_EQN_EXPECTED}

目标通常只需添加一个负号即可转化为损失函数，这使优化器寻求使其尽可能负。

对于语言模型，目标（或损失）是逐 token 计算的，直觉上可以基于如何计算整个自回归预测序列的概率来理解——通过对概率求积。从那里，常见的实现是使用*对数概率（log-probabilities）*来使计算在现代语言建模框架中更简便。在实践中，我们计算 token 对数概率的差并取指数以恢复策略比率 $\rho_t$。

$$ J(\theta) = \frac{1}{|a|} \sum_{t=0}^{|a|} \min\left(\frac{\pi_\theta(a_{t}|s_t)}{\pi_{\theta_{\text{old}}}(a_{t}|s_t)}A_{t}, \text{clip} \left( \frac{\pi_\theta(a_{t}|s_t)}{\pi_{\theta_{\text{old}}}(a_{t}|s_t)}, 1-\varepsilon, 1+\varepsilon \right) A_{t} \right).  $$  {#eq:PPO_EQN_EXPANDED}

这是 PPO 的逐 token 版本，也适用于其他策略梯度方法，但在本章的实现部分将进一步探讨。这里，按动作中 token 数量平均的项 $\frac{1}{|a|}$ 来自常见的实现实践，但不在损失的正式推导中（参见 [@liu2025understanding]）。

![PPO 框架。学习得到的价值函数使广义优势估计（GAE）可实现逐 token 优势，与裁剪代理目标一起使用。](images/ppo_tikz.png){#fig:ppo-arch data-dark-src="images/ppo_tikz-dark.png"}

下面我们将解释在各种优势和策略比率下该损失函数触发的不同情况。在实现层面，PPO 的内部计算涉及两个主要部分：1) 具有学习优势的标准策略梯度和 2) 基于最大步长的裁剪策略梯度。

为了理解不同情境如何出现，我们可以将策略比率定义为：

$$\rho(\theta) = \frac{\pi_\theta(a|s)}{\pi_{\theta_{\text{old}}}(a|s)}$$ {#eq:PPO_POL_RATIO}

策略比率是 PPO 和相关算法的核心。它出现在策略梯度的计算中，并以一种直观的方式控制参数更新。对于任意数据批次，策略比率在该批次的第一个梯度步骤时从 1 开始，因为此时 $\pi_{\theta}$ 与 $\pi_{\theta_{\text{old}}}$ 相同。然后，在下一个梯度步骤中，如果该梯度步骤增加了具有正优势的某些 token 的似然，则策略比率将大于 1，否则小于 1。一种常见做法是在更新 $\pi_{\theta_{\text{old}}}$ 之前，在策略梯度算法的每个批次上执行 1-4 个梯度步骤。

### 理解 PPO 目标

总体而言，PPO 目标可以通过将目标与策略比率的图绘制为两条线来可视化，如 @fig:ppo-obj 所示。PPO 目标通过改变采样动作的概率来最大化。数值上，目标通过巧妙地使用最小运算来处理正负优势情况，使得更新最多被推到距离策略比率 1 一个 epsilon 的距离。

在信任区域（trust region）内，PPO 的运行方式与其他策略梯度算法相同。这是有意的！信任区域是一个用于限制 PPO 及其同类算法的最大步长的概念，以确保更新的稳定性。PPO 算法的核心——clip 和 min/max 运算——定义了该区域。在该区域外目标变为平坦。

"信任区域"的概念来自数值优化文献 [@nocedal2006numerical]，但在深度强化学习中因算法信任区域策略优化（Trust Region Policy Optimization, TRPO）而普及，TRPO 被认为是 PPO 的前身 [@schulman2015trust]。信任区域是应用完整策略梯度步骤的区域，因为这些更新没有被 PPO 目标的 max/min 运算"裁剪"。

![PPO 目标 $J(\theta)$ 作为策略比率 $\rho(\theta)$ 的函数的可视化，适用于正优势和负优势。在每个面板中，三个比率区域均标注了其未裁剪项、裁剪项、最终目标和梯度。](images/ppo-clip-viz.png){#fig:ppo-obj}

策略比率和优势可以出现在几种不同的配置中，@fig:ppo-obj 通过优势 $A_t$ 的符号和策略比率 $\rho(\theta)$ 落入三个区域中的哪个来枚举这些情况。决定每个区域结果的有两个事实：优势的符号决定了我们是否希望增加或减少动作的可能性，以及 $\min$ 运算选择未裁剪项 $\rho(\theta) A_t$ 还是其裁剪版本。

裁剪操作仅在策略*已经*在所需方向上移动了采样动作、超过信任区域边缘的两个区域中将梯度置零：

- **正优势和 $\rho(\theta) > 1+\varepsilon$**：在 $\pi_\theta$ 下动作已经比在 $\pi_{\theta_{\text{old}}}$ 下更可能得多。目标饱和于 $(1+\varepsilon)A_t$，梯度为零，不进行更新——我们避免过度强化已经更频繁出现的动作。
- **负优势和 $\rho(\theta) < 1-\varepsilon$**：在 $\pi_\theta$ 下动作已经比在 $\pi_{\theta_{\text{old}}}$ 下更不可能得多。目标饱和于 $(1-\varepsilon)A_t$，梯度再次为零，不进行更新——我们避免过度抑制已经不鼓励的动作。

在其他所有地方，未裁剪项 $\rho(\theta) A_t$ 生效，PPO 执行标准策略梯度步骤：当 $A_t > 0$ 时增加动作概率，当 $A_t < 0$ 时减少它。我们可以从 @fig:ppo-obj 读出每个区域对更新策略 $\pi_\theta$ 的要求：

- 正优势下的倾斜未裁剪区域（绿色）**增加**采样动作的概率；
- 负优势下的倾斜未裁剪区域（红色）**减少**它；
- 平坦的裁剪区域（灰色）保持策略**不变**，因为其梯度为零。

将各个区域逐项写出：

#### 正优势（$A_t > 0$）

这意味着根据价值函数所采取的动作是有益的，我们希望增加在未来采取该动作的可能性。现在，让我们看看策略比率 $\rho(\theta)$ 的不同情况：

1. $\rho(\theta) < 1 - \varepsilon$：

    - **解释**：在新策略下动作比在旧策略下更不可能
    - **未裁剪项**：$\rho(\theta) A_t$
    - **裁剪项**：$(1 - \varepsilon) A_t$
    - **目标**：$\rho(\theta) A_t$
    - **梯度**：$\nabla_\theta \rho(\theta) A_t \neq 0$
    - **发生什么**：标准策略梯度更新——增加动作的可能性

2. $1 - \varepsilon \leq \rho(\theta) \leq 1 + \varepsilon$：

    - **解释**：在新策略和旧策略下动作几乎同样可能
    - **未裁剪项**：$\rho(\theta) A_t$
    - **裁剪项**：$\rho(\theta) A_t$
    - **目标**：$\rho(\theta) A_t$
    - **梯度**：$\nabla_\theta \rho(\theta) A_t \neq 0$
    - **发生什么**：标准策略梯度更新——增加动作的可能性

3. $1 + \varepsilon < \rho(\theta)$：

    - **解释**：在新策略下动作比在旧策略下更可能
    - **未裁剪项**：$\rho(\theta) A_t$
    - **裁剪项**：$(1 + \varepsilon) A_t$
    - **目标**：$(1 + \varepsilon) A_t$
    - **梯度**：$\nabla_\theta (1 + \varepsilon) A_t = 0$
    - **发生什么**：**无更新**——动作在新策略下已经更可能

总结如下，当优势为正（$A_t>0$）时，我们希望提升动作的概率。因此：

- 我们仅在新策略概率 $\pi_{\text{new}}(a) \leq (1+\varepsilon) \pi_{\text{old}}(a)$ 的情况下执行梯度步骤。直觉上，我们希望提升动作的概率，因为优势为正，但不要提升到使它在很大程度上更可能的程度。
- 关键的是，当 $\pi_{\text{new}}(a) > (1+\varepsilon) \pi_{\text{old}}(a)$ 时，我们不执行任何更新，裁剪目标的梯度为 $0$。直觉上，动作在新策略下已经更多地出现，因此我们不希望过度强化它。

#### 负优势（$A_t < 0$）

这意味着根据价值函数所采取的动作是不利的，我们希望减少在未来采取该动作的可能性。现在，让我们看看策略比率 $\rho(\theta)$ 的不同情况：

1. $\rho(\theta) < 1 - \varepsilon$：

    - **解释**：在新策略下动作比在旧策略下更不可能
    - **未裁剪项**：$\rho(\theta) A_t$
    - **裁剪项**：$(1 - \varepsilon) A_t$
    - **目标**：$(1 - \varepsilon) A_t$
    - **梯度**：$\nabla_\theta (1 - \varepsilon) A_t = 0$
    - **发生什么**：**无更新**——动作在新策略下已经更不可能

2. $1 - \varepsilon \leq \rho(\theta) \leq 1 + \varepsilon$：

    - **解释**：在新策略和旧策略下动作几乎同样可能
    - **未裁剪项**：$\rho(\theta) A_t$
    - **裁剪项**：$\rho(\theta) A_t$
    - **目标**：$\rho(\theta) A_t$
    - **梯度**：$\nabla_\theta \rho(\theta) A_t \neq 0$
    - **发生什么**：标准策略梯度更新——降低动作的可能性

3. $1 + \varepsilon < \rho(\theta)$：

    - **解释**：在新策略下动作比在旧策略下更可能
    - **未裁剪项**：$\rho(\theta) A_t$
    - **裁剪项**：$(1 + \varepsilon) A_t$
    - **目标**：$\rho(\theta) A_t$
    - **梯度**：$\nabla_\theta \rho(\theta) A_t \neq 0$
    - **发生什么**：标准策略梯度更新——降低动作的可能性

总结如下，当优势为负（$A_t < 0$）时，我们希望降低动作的概率。因此：

- 我们仅在新策略概率 $\pi_{\text{new}}(a) \geq (1-\varepsilon) \pi_{\text{old}}(a)$ 的情况下执行梯度步骤。直觉上，我们希望降低动作的概率，因为优势为负，且按优势比例进行。
- 关键的是，当 $\pi_{\text{new}}(a) < (1-\varepsilon) \pi_{\text{old}}(a)$ 时，我们不执行任何更新，裁剪目标的梯度为 $0$。直觉上，动作在新策略下已经更不可能，因此我们不希望过度抑制它。

务必记住，信任区域内的 PPO 大致与标准形式的策略梯度相同。


### 价值函数与 PPO

PPO 中的价值函数是模型的额外副本，用于预测每个 token 的价值。传统 RL 中 token（或状态）的价值是预测从该时刻开始的未来回报，通常进行折扣。在 PPO 中，这个值被用作学习的基线，代表了 REINFORCE 中使用的简单 Monte Carlo 版本（不需要学习价值网络）的进化。这凸显了 PPO 在优化形式、基线等多个方面是 REINFORCE 和原始策略梯度的进化。在实践中，使用 PPO 和其他语言模型算法时，这是预测扣除 KL 惩罚后的每个 token 的回报（如讨论的，每 token 的损失传统上包括来自奖励的 KL）。

有几种不同的方法（或目标）用于学习价值函数。广义优势估计（Generalized Advantage Estimation, GAE）被认为是现代系统中的最先进和典范实现，但它通过计算多步价值预测误差而带来更高的复杂度——参见本章后文的 GAE 部分。价值函数也可以使用用于更新策略的 rollout 中的 Monte Carlo 估计来学习。PPO 有两个损失——一个用于学习价值函数，另一个使用该价值函数来更新策略。

![价值函数训练使用同策略 rollout 计算目标。模型在每个 token 处预测 $V_t$，通过均方误差训练以匹配目标回报 $\hat{V}_t$。优势 $A_t = \hat{V}_t - V_t$ 随后加权策略梯度更新。](images/value_fn_training.png){#fig:value_fn_training data-dark-src="images/value_fn_training-dark.png"}

下面展示价值网络损失的一个简单示例实现。

```python
# Basic PPO critic targets & loss (no GAE)
#
# B: Batch Size
# L: Completion Length
# Inputs:
#   rewards: (B, L) post-KL per-token rewards; EOS row includes outcome
#   done_mask: (B, L) 1.0 at terminal token (EOS or truncation if penalized), else 0.0
#   completion_mask: (B, L) 1.0 on response tokens to supervise (ignore the prompt)
#   values: (B, L) current critic predictions V_theta(s_t)
#       because a value network is a running update
#   old_values: (B, L) critic predictions at rollout time V_{theta_old}(s_t)
#   gamma: discount factor, float (often 1.0 for LM RLHF)
#   epsilon_v: float value clip range (e.g., 0.2), similar to PPO Loss Update itself, optional
#
# Returns:
#   value_loss: scalar; advantages: (B, L) detached (for policy loss)

B, L = rewards.shape

# 1) Monte Carlo returns per token (reset at terminals)
# Apply discounting, if enabled
returns = torch.zeros_like(rewards)
running = torch.zeros(B, device=rewards.device, dtype=rewards.dtype)
for t in reversed(range(L)):
    running = rewards[:, t] + gamma * (1.0 - done_mask[:, t]) * running
    returns[:, t] = running

targets = returns  # y_t = G_t (post-KL)

# 2) PPO-style value clipping (optional)
v_pred = values
v_old  = old_values
v_clip = torch.clamp(v_pred, v_old - epsilon_v, v_old + epsilon_v)

vf_unclipped = 0.5 * (v_pred - targets) ** 2
vf_clipped   = 0.5 * (v_clip - targets) ** 2
vf_loss_tok  = torch.max(vf_unclipped, vf_clipped)

# 3) Mask to response tokens and aggregate
denom = completion_mask.sum(dim=1).clamp_min(1)
value_loss = ((vf_loss_tok * completion_mask).sum(dim=1) / denom).mean()

# 4) Advantages for policy loss (no GAE): A_t = G_t - V(s_t)
advantages = (targets - v_pred).detach()

# The value loss is applied later, often with the PG loss, e.g.
# total_loss = policy_loss + vf_coef * value_loss
```

### 分组相对策略优化（Group Relative Policy Optimization, GRPO）

分组相对策略优化（Group Relative Policy Optimization, GRPO）在 DeepSeekMath [@shao2024deepseekmath] 中引入，并被其他 DeepSeek 工作使用，例如 DeepSeek-V3 [@deepseekai2025deepseekv3technicalreport] 和 DeepSeek-R1 [@guo2025deepseek]。GRPO 可以看作是一个受 PPO 启发的算法，具有非常相似的代理损失，但它避免了使用另一个原始策略语言模型的副本（或另一个用于初始化的检查点）来学习价值函数。这带来了两个推测性好处：

1. 避免从 LM backbone 学习价值函数的挑战，研究尚未确立最佳实践。
2. 通过不需要在内存中保留额外的模型权重来节省内存（从需要当前策略、参考策略和价值函数三份减少到只需前两份）。

GRPO 通过简化价值估计并为回合中的每个 token 分配相同的价值（即，在针对一个提示的补全中，每个 token 获得相同的值，而非标准价值函数中的折扣奖励）来做到这一点，方法是估计优势或基线。该估计是通过从相同的初始状态 / 提示（$s$）收集多个补全（$a_i$）和奖励（$r_i$）——即 Monte Carlo 估计——完成的。

正式地说，GRPO 目标与上述 PPO 目标非常相似。对于 GRPO，目标（或损失）累加给定提示 $s$ 的一组补全 $\{a_1, a_2, ..., a_G\}$。这里我们展示 GRPO 目标：

$$J(\theta) = \frac{1}{G}\sum_{i=1}^G \left(\min\left(\frac{\pi_\theta(a_i|s)}{\pi_{\theta_{\text{old}}}(a_i|s)}A_i, \text{clip} \left( \frac{\pi_\theta(a_i|s)}{\pi_{\theta_{\text{old}}}(a_i|s)}, 1-\varepsilon, 1+\varepsilon \right) A_i \right) - \beta \mathcal{D}_{\text{KL}}(\pi_\theta||\pi_{\text{ref}})\right).$$ {#eq:GRPO}

注意，相较于 PPO，GRPO 的标准实现将 KL 距离包含在损失中。如上所述，我们可以将其展开为逐 token 的计算：

$$\begin{aligned}
J(\theta) = \frac{1}{G}\sum_{i=1}^G  \frac{1}{|a_i|} \sum_{t=1}^{|a_i|} \Bigg( &\min\!\left(\frac{\pi_\theta(a_{i,t}|s_{i})}{\pi_{\theta_{\text{old}}}(a_{i,t}|s_{i})}A_{i,t},\; \text{clip} \left( \frac{\pi_\theta(a_{i,t}|s_{i})}{\pi_{\theta_{\text{old}}}(a_{i,t}|s_{i})}, 1-\varepsilon, 1+\varepsilon \right) A_{i,t} \right) \\
&- \beta \mathcal{D}_{\text{KL}}\!\left(\pi_\theta(\cdot|s_{i})\|\pi_{\text{ref}}(\cdot|s_{i})\right) \Bigg)
\end{aligned}$$ {#eq:GRPO_token}


补全索引 $i$ 的优势计算为：

$$A_i = \frac{r_i - \text{mean}({r_1, r_2, \cdots, r_G})}{\text{std}({r_1, r_2, \cdots, r_G})}.$$ {#eq:GRPO_ADV}

![GRPO 架构。优势相对于组的均值和标准差进行归一化。KL 惩罚直接应用于损失而非塑造奖励。](images/grpo_tikz.png){#fig:grpo-arch data-dark-src="images/grpo_tikz-dark.png"}

直观地说，GRPO 更新是在批次中比较对一个问题的多个答案。模型学习变得更像被标记为正确的答案，而更少像其他答案。这是一种非常简单的优势计算方法，即衡量特定动作在给定状态下比平均水平好多少的程度。相较于 PPO、REINFORCE 以及广泛使用奖励模型评分（相对于输出奖励）执行的 RLHF，GRPO 通常以更高采样数 per prompt 运行，因为优势完全取决于补全相对于来自该提示的同侪的相对价值。在这里，当前策略为给定提示生成多个响应，组级的 GRPO 优势估计提供了宝贵的上下文。PPO 和原始策略梯度算法旨在准确估计每个补全的奖励（事实上，在某些情况下，更多补全可能对改善价值估计没有帮助）。GRPO 及其变体特别适合现代语言模型工具，因为为给定提示拥有多个补全是非常自然的（相较于，例如，从设定环境状态中的多个动作的机器人任务）。

GRPO 的优势计算在其偏差中存在权衡。批次中对答案正确性变化低的问题除以标准差会获得较高优势。对于几乎全部正确或全部错误的问题，标准差会更低，优势会更高。Liu 等人 2025 [@liu2025understanding] 建议去除标准差项来解决这一偏差，但这以较低加权全部错误但少数正确的问题为代价，后者可能被视为模型的有价值学习信号。那些高方差的提示可能恰好是最难的情况，其中只有少数采样的补全找到正确答案并提供强烈的训练信号。

@eq:GRPO_ADV 是在与结果监督（标准奖励模型或单一可验证奖励）一起工作时 GRPO 的实现，而在过程监督的情况下需要不同的实现。在这种情况下，GRPO 将优势计算为以下推理步骤中归一化奖励之和。

最后，GRPO 的优势估计也可以在不使用 PPO 裁剪的情况下应用于更原始形式的策略梯度（例如 REINFORCE），但这不是规范形式。作为这些算法交织的一个例子，我们可以展示 GRPO 的一个变体——Dr. GRPO（GRPO Done Right）[@liu2025understanding]——中的优势估计等价于 RLOO 估计（使用其他样本的平均奖励作为其基线），相差一个常数缩放因子（由于归一化优势的 implementatio 细节，这通常不重要）。Dr. GRPO 从 @eq:GRPO_ADV 中移除了标准差归一化项——注意这也*放大*了优势，这等价于对答案分数有方差的样本提高 GRPO 学习率。这解决了偏向低奖励方差问题——即几乎全部答案正确或错误——的偏差，但如果从仅有一个样本答对的问题中学习很重要，则可能存在潜在成本。大小为 $G$ 的组中补全 $i$ 的 Dr. GRPO 优势定义为：

$$ \tilde{A}_i = r_i - \text{mean}({r_1, r_2, \cdots, r_G}) = r_i - \frac{1}{G}\sum_{j=1}^G r_j $$ {#eq:DrGRPO_ADV}

这里，使用相同的记号，我们可以回顾 RLOO 优势估计为：

$$ A_i^\text{RLOO} = r_i - \frac{1}{G-1}\sum_{j=1, i\neq j}^G r_j $$ {#eq:RLOO_ADV_AGAIN}

因此，如果我们将 Dr. GRPO 优势定义乘以 $\frac{G}{G-1}$，我们可以看到缩放的等价性：

$$
\begin{aligned}
\frac{G}{G-1} \tilde{A}_i &= \frac{G}{G-1} \left( r_i - \frac{1}{G}\sum_{j=1}^G r_j \right) \\
&= \frac{G}{G-1} r_i - \frac{1}{G-1} \sum_{j=1}^G r_j \\
&= \frac{G}{G-1} r_i - \frac{1}{G-1} \sum_{j=1, j\neq i}^G r_j - \frac{1}{G-1} r_i \\
&= r_i \left( \frac{G}{G-1} - \frac{1}{G-1} \right) - \frac{1}{G-1} \sum_{j=1, j\neq i}^G r_j \\
&= r_i - \frac{1}{G-1} \sum_{j=1, j\neq i}^G r_j \\
&= A_i^{\text{RLOO}}
\end{aligned}
$$ {#eq:RLOO_GRPO_EQUIV}

### 分组序列策略优化（Group Sequence Policy Optimization, GSPO）

当对从先前策略收集的数据批次执行多个梯度步骤时，需要进行重要性采样以纠正数据收集策略与被优化当前策略之间的分布不匹配。标准重要性采样恒等式允许我们使用来自另一个分布的样本来估计一个分布下的期望：

$$
\mathbb{E}_{p}[f(x)] = \mathbb{E}_{q}\left[f(x) \frac{p(x)}{q(x)}\right],
$$ {#eq:IS_identity}

其中 $p$ 是目标分布，$q$ 是采样分布，$\frac{p(x)}{q(x)}$ 是重要性权重。在策略梯度方法中，$p = \pi_\theta$ 是我们想要优化的当前策略，$q = \pi_{\theta_{\text{old}}}$ 是生成训练数据的策略。这允许我们重新加权基于 $\pi_{\theta_{\text{old}}}$ 收集的样本来估计 $\pi_\theta$ 的梯度，从而在每个 rollout 批次上启用多个梯度步骤。

这种分布不匹配在两种常见场景中出现：（1）对单个批次执行多个梯度步骤，其中 $\pi_\theta$ 在每次更新后从 $\pi_{\theta_{\text{old}}}$ 漂移；（2）在异步训练系统中，推理后端（例如 vLLM）和训练后端（例如 FSDP）可能由于同步延迟而拥有不同的模型权重（参见本章后文的异步部分，这在关注可验证奖励 RL 时尤为突出，但也用于 RLHF 设置）。

PPO 和 GRPO 在 token 级别应用重要性采样并通过裁剪*代理目标*来稳定学习。然而，这种方法有一个微妙的失效模式：当 token 的重要性比率移出裁剪范围 $[1-\varepsilon, 1+\varepsilon]$ 时，该 token 接收零梯度。对于稀有但重要的 token——如模型最初分配低概率的关键推理步骤——这种"token 丢弃"可能阻止模型更可靠地产生它们。

分组序列策略优化（Group Sequence Policy Optimization, GSPO）[@zheng2025gspo] 扩展了 GRPO，在序列级别而非 token 级别计算重要性比率。该算法及其同类 CISPO（我们稍后将讨论，它修改了策略梯度算法中重要性采样的计算方式）的实际动机是，逐 token 的重要性采样比率通常数值不稳定。概念动机是，当奖励在序列级别分配时（如在大多数 RLHF 和 RLVR 设置中），重要性采样校正应与该粒度相匹配。

逐 token 比率对于长序列和/或大型稀疏模型（例如现代混合专家（MoE）模型）可能行为异常：单个具有大比率的 token 可能主导策略更新，或许多 token 可能在响应内独立被裁剪，将学习信号碎片化到单个响应中。GSPO 通过在每条响应中计算单个重要性权重来解决这个问题。

回想一个完整响应的概率自回归地分解为：

$$
\pi_\theta(a \mid s) = \prod_{t=1}^{|a|} \pi_\theta(a_t \mid s, a_{<t}).
$$ {#eq:response_factorization}

注意，为简化起见，我们通常将条件策略 $\pi_\theta(a_t \mid s, a_{<t})$ 简写为 $\pi_\theta(a_t \mid s)$，其中隐式包含了补全中的先前动作（token）。GSPO 使用几何平均定义长度归一化的序列级重要性比率（以避免长序列的数值问题）：

$$
\rho_i(\theta) = \left( \frac{\pi_\theta(a_i \mid s)}{\pi_{\theta_{\text{old}}}(a_i \mid s)} \right)^{\frac{1}{|a_i|}} = \exp\left( \frac{1}{|a_i|} \sum_{t=1}^{|a_i|} \log \frac{\pi_\theta(a_{i,t} \mid s, a_{i,<t})}{\pi_{\theta_{\text{old}}}(a_{i,t} \mid s, a_{i,<t})} \right).
$$ {#eq:GSPO_ratio}

GSPO 目标与 GRPO 类似，但使用此序列级比率：

$$
J_{\text{GSPO}}(\theta) = \mathbb{E}_{s \sim \mathcal{D},\, \{a_i\}_{i=1}^G \sim \pi_{\theta_{\text{old}}}(\cdot \mid s)} \left[ \frac{1}{G} \sum_{i=1}^G \min\left( \rho_i(\theta) A_i,\, \text{clip}(\rho_i(\theta), 1-\varepsilon, 1+\varepsilon) A_i \right) \right].
$$ {#eq:GSPO_objective}

由于比率是长度归一化的，裁剪范围 $\varepsilon$ 在每 token 平均规模上运行，使有效约束在不同长度的响应之间可比较。在实现中，序列级权重 $\rho_i$ 均匀地应用于响应 $a_i$ 中的所有 token，简化了梯度计算同时保持序列级 IS 校正。

优势计算与 GRPO 相同（@eq:GRPO_ADV），使用组内相对均值和标准差归一化，可以如其他 GRPO 衍生研究中所做的那样进行修改。GSPO 可以总结为"使用序列级重要性比率的 GRPO"——IS 校正的粒度与奖励粒度相匹配。

### 裁剪重要性采样策略优化（Clipped Importance Sampling Policy Optimization, CISPO）

裁剪重要性采样策略优化（Clipped Importance Sampling Policy Optimization, CISPO）[@minimax2025minimax_m1] 采取了不同的方法：与其裁剪代理目标，CISPO 裁剪重要性权重本身，同时保留所有 token 的梯度。该目标在对裁剪重要性权重的停止梯度上使用，回归到 REINFORCE 式公式而非 PPO 式的两侧裁剪：

$$
J_{\text{CISPO}}(\theta) = \mathbb{E}_{s \sim \mathcal{D},\, \{a_i\}_{i=1}^K \sim \pi_{\theta_{\text{old}}}(\cdot \mid s)} \left[ \frac{1}{\sum_{i=1}^K |a_i|} \sum_{i=1}^K \sum_{t=1}^{|a_i|} \text{sg}\left( \hat{\rho}_{i,t}(\theta) \right) A_{i,t} \log \pi_\theta(a_{i,t} \mid s, a_{i,<t}) \right],
$$ {#eq:CISPO_objective}

其中 $\text{sg}(\cdot)$ 表示停止梯度（权重被使用但不被微分），裁剪的重要性比率为：

$$
\hat{\rho}_{i,t}(\theta) = \text{clip}\left( \rho_{i,t}(\theta),\, 1 - \varepsilon_{\text{low}},\, 1 + \varepsilon_{\text{high}} \right), \quad \rho_{i,t}(\theta) = \frac{\pi_\theta(a_{i,t} \mid s, a_{i,<t})}{\pi_{\theta_{\text{old}}}(a_{i,t} \mid s, a_{i,<t})}.
$$ {#eq:CISPO_ratio}

与 PPO/GRPO 的关键区别微妙但重要：裁剪权重（而非目标）意味着每个 token 仍然接收到与其优势成比例的梯度信号——权重只是限制了重要性比率对信号放大或抑制的程度。这是一个偏差-方差权衡：裁剪权重引入偏差但控制方差，且关键地避免完全丢弃 token 梯度。

CISPO 和 GSPO 均由在大规模 MoE 模型上应用 RL 的组织开发，这些模型以其数值问题而闻名。论文强调逐 token 重要性采样比率不稳定且可能为梯度增加大量方差，从而减缓学习。这可能使这些算法在大型模型上特别有影响力，但在较小的学术实验中则研究较少且收益较少。

CISPO 也允许非对称裁剪边界（$\varepsilon_{\text{low}} \neq \varepsilon_{\text{high}}$），类似于本章后文讨论的 DAPO 的"higher 裁剪"修改，可以通过允许更大的更新来鼓励探索。相关工作包括锥形离策略 REINFORCE（Tapered Off-Policy REINFORCE, TOPR）[@leroux2025topr]，它也直接裁剪 IS 权重（如 CISPO）而非在目标内裁剪（如 PPO/GRPO），但在序列级别运行（如 GSPO）并使用基于奖励符号的非对称裁剪——对正奖励不应用 IS 校正，而对负奖励将比率裁剪到 $[0, 1]$——实现稳定的离策略学习。


### 算法比较

本章中的每个算法共享相同的核心梯度形式（@eq:policy_gradient_intuition），但在优势估计和控制优化方面有所不同：

- **REINFORCE**：最简单的策略梯度实现，使用蒙特卡洛奖励估计和基于状态的基线来降低方差。
- **RLOO**：REINFORCE 的每个提示多个样本版本，每个样本的基线是其余样本的平均奖励（leave-one-out）以降低梯度方差。
- **PPO**：添加了学习价值函数和裁剪策略比率以获得更准确和稳定的梯度更新。
- **GRPO**：PPO 的简化变体，将多个补全分组到每个提示并以组内归一化奖励来计算优势，无需价值函数。
- **CISPO**：一种 REINFORCE 式算法，裁剪重要性采样权重（而非如 PPO/GRPO 中裁剪目标），使用停止梯度以确保稳定性，使每个 token 接收梯度信号。
- **GSPO**：类似于 GRPO，但以补全长度归一化策略比率，防止长度偏差。
- **DPO**：不是 RL 算法，而是一种通过完全绕过单独的奖励模型来求解相同偏好优化问题的方法，直接从偏好对中进行优化（参见第 8 章）。

以上所有策略梯度算法在推导中都是同策略的，尽管大多数在实践中略微离策略执行。DPO 和第 8 章中的其他直接对齐算法默认是离策略的。所有算法都可以与学习奖励模型或可验证奖励配对。只有 PPO 需要学习价值函数。REINFORCE 和 RLOO 没有重要性采样比率——其余算法各引入一个以在每个 rollout 批次上启用多个梯度步骤，在粒度和裁剪策略上有所不同，总结如下。

| 方法 | IS 粒度 | 裁剪方式 | 优势 |
| :----- | :-----------: | :------------------: | :-------------------: |
| **REINFORCE** | 无 | 无 | Monte Carlo 基线 |
| **RLOO** | 无 | 无 | Leave-one-out |
| **PPO** | Token | 目标（双边） | 学习价值函数 |
| **GRPO** | Token | 目标（双边） | 组内相对 |
| **GSPO** | 序列 | 目标（双边） | 组内相对 |
| **CISPO** | Token | 权重（停止梯度） | 组内相对 |

表格：策略梯度算法比较。 {#tbl:pg_compare}

每种方法的核心损失 $\mathcal{L}(\theta)$ 为：

$$\begin{aligned}
\textbf{REINFORCE:}\quad & -\frac{1}{T}\sum_{t=1}^{T}\log \pi_\theta(a_t\mid s_t)\,\big(G_t - b(s_t)\big) \\[6pt]
\textbf{RLOO:}\quad & -\frac{1}{K}\sum_{i=1}^{K}\sum_t \log \pi_\theta(a_{i,t}\mid s_{i,t})\left(R_i-\frac{1}{K-1}\sum_{j\neq i}R_j\right) \\[6pt]
\textbf{CISPO:}\quad & -\sum_{i,t} \mathrm{sg}(\hat{\rho}_{i,t})\, A_{i,t} \log \pi_\theta(a_{i,t}\mid s_{i,t}) \\
& \quad \hat{\rho}_{i,t} = \mathrm{clip}(\rho_{i,t},\, 1-\varepsilon,\, 1+\varepsilon) \\[6pt]
\textbf{PPO:}\quad & -\frac{1}{T}\sum_{t=1}^{T}\min\!\big(\rho_t A_t,\ \mathrm{clip}(\rho_t,1-\varepsilon,1+\varepsilon)\, A_t\big) \\
& \quad \rho_t = \frac{\pi_\theta(a_t\mid s_t)}{\pi_{\theta_{\text{old}}}(a_t\mid s_t)} \\[6pt]
\textbf{GRPO:}\quad & -\frac{1}{G}\sum_{i=1}^{G}\min\!\big(\rho_i A_i,\ \mathrm{clip}(\rho_i,1-\varepsilon,1+\varepsilon)\, A_i\big) \\
& \quad \rho_i = \frac{\pi_\theta(a_i\mid s)}{\pi_{\theta_{\text{old}}}(a_i\mid s)},\quad A_i = \frac{r_i-\mathrm{mean}(r_{1:G})}{\mathrm{std}(r_{1:G})} \\[6pt]
\textbf{GSPO:}\quad & -\frac{1}{G}\sum_{i=1}^{G}\min\!\big(\rho_i A_i,\ \mathrm{clip}(\rho_i,1-\varepsilon,1+\varepsilon)\, A_i\big) \\
& \quad \rho_i = \left(\frac{\pi_\theta(a_i\mid s)}{\pi_{\theta_{\text{old}}}(a_i\mid s)}\right)^{1/|a_i|} \\[6pt]
\textbf{DPO:}\quad & -\mathbb{E}_{(x,y^{w},y^{l})}\!\left[\log \sigma\!\big(\beta[\Delta\log \pi_\theta(x)-\Delta\log \pi_{\mathrm{ref}}(x)]\big)\right]
\end{aligned}$$


## 实现

与这些算法最初开发的大量原始深度 RL 文献相比，实现用于优化语言模型或其他大型 AI 模型的 RL 需要许多小的实现细节。在本节中，我们突出显示区分流行算法实现的一些关键因素。

还有更多小的细节进入此训练。例如，在使用语言模型进行 RLHF 时，一个关键步骤是生成将被奖励模型评分的文本。正常情况下，模型应生成一个序列结束（EOS）token 表明它完成了生成，但一种常见做法是对生成长度施加硬性上限以有效利用基础设施。RLHF 的一个失效模式是模型的答案经常被截断，驱动来自奖励模型的评分超出分布且分数不可预测。解决这个问题的方法是*仅*在 `eos_token` 上运行奖励模型评分，否则对模型生成过长施加惩罚。

流行的开源 RLHF 工具在不同算法的实现细节方面存在巨大差异（参见 [@ivison2024unpacking] 中的表 10）。以下是不在此涵盖的一些决策：

- **价值网络初始化**：PPO 和其他类似算法使用的内部学习价值网络可以从相同架构的不同模型或随机选择的权重开始。这对性能可能有巨大影响。InstructGPT [@ouyang2022training]（并重新用于 Tülu 3 在其 RLVR 工作中 [@lambert2024t]）中建立的标准是从 RLHF 期间使用的奖励模型初始化价值网络。其他人使用 RLHF 训练的前一个检查点（通常为 SFT 模型）附加随机初始化的价值头，或完全重新初始化的语言模型（较少见，因为 RLHF 收敛会更慢，但可行）。
- **奖励归一化、奖励白化和/或优势白化**：归一化将所有来自 RM（或环境）的值限定在 0 到 1 之间，这有助于学习稳定性。[白化（Whitening）](https://en.wikipedia.org/wiki/Whitening_transformation)更进一步，通过将奖励或优势估计转换为具有零均值和单位方差，为稳定性提供更强的提升。
- **不同的 KL 估计器**：对于复杂语言模型，精确计算模型之间的 KL 散度可能很复杂，因此使用多种近似来替代精确计算 [@schulman2016klapprox]。
- **KL 控制器**：PPO 和相关算法的原始实现具有动态控制器，针对特定的 KL 值并根据最近的测量改变惩罚。大多数现代 RLHF 实现使用静态 KL 惩罚，但这也可以有所不同。

关于 RLHF 实现细节的更多内容，参见 [@huang2024n]。关于算法的更多信息，参见 [@weng2018PG]。

### 策略梯度基础

使用优势来估计梯度以准备 PPO 和 GRPO 等高级策略梯度的简单实现如下：
```python
pg_loss = -advantages * ratio
```
这里的比率是（逐 token 的）概率比率（通常通过对数概率差计算），即新策略模型概率相对于生成批次的旧策略的概率比。

理解这个方程，需要理解可以落在更新批次中的不同情况。请记住，我们希望损失*降低*，因为模型在任务上做得更好。

情况 1：正优势，所以动作比状态的期望值更好。我们希望强化它。在这种情况下，负号会使模型更可能这样做。为此，它将增加 logratio。正的 logratio，或 token 对数概率之和，意味着模型更可能生成这些 token。

情况 2：负优势，所以动作比状态的期望值更差。这与上面非常类似。在这里，如果新模型更可能，损失将为正，所以模型将尝试让策略参数使该补全更不可能。

情况 3：零优势，不需要更新。损失为零，不改变策略模型。

### 损失聚合权衡

在实现任何语言模型策略梯度算法时的问题是：如何将逐 token 损失聚合成最终标量损失？给定样本 $i$ 在 token $t$ 处的逐 token 损失 $\ell_{i,t}$，补全长度为 $|a_i|$，批次大小为 $B$，有三种主要策略：

**策略 1：逐序列归一化**（标准 GRPO；也在一些 PPO 实现中使用）

$$L = \frac{1}{B} \sum_{i=1}^{B} \frac{1}{|a_i|} \sum_{t=1}^{|a_i|} \ell_{i,t}$$ {#eq:loss_per_sequence}

每个序列在批次损失中贡献相等，无论长度如何。在代码中：

```python
# Strategy 1: Per-sequence normalization
sequence_loss = ((per_token_loss * completion_mask).sum(dim=1) / \
             completion_mask.sum(dim=1)).mean()
```

**策略 2：逐 token 归一化**（DAPO [@yu2025dapo]）

$$L = \frac{\sum_{i=1}^{B} \sum_{t=1}^{|a_i|} \ell_{i,t}}{\sum_{i=1}^{B} |a_i|}$$ {#eq:loss_per_token}

每个 token 贡献相等；较长的序列对梯度有比例上更大的影响。在代码中：

```python
# Strategy 2: Per-token normalization
token_loss = ((per_token_loss * completion_mask).sum() / \
            completion_mask.sum())
```

**策略 3：固定长度归一化**（Dr. GRPO [@liu2025understanding]）

$$L = \frac{1}{B} \sum_{i=1}^{B} \frac{1}{L_{\max}} \sum_{t=1}^{|a_i|} \ell_{i,t}$$ {#eq:loss_fixed_length}

通过最大序列长度 $L_{\max}$ 归一化，在序列之间平衡每 token 规模，同时仍让较长序列贡献更多总梯度，因为它们包含更多活跃 token。在代码中：

```python
# Strategy 3: Fixed-length normalization 
fixed_len_loss = ((per_token_loss * completion_mask).sum(dim=1) / \
            L_max).mean()
```

其中 $L_{\max}$ 在整个训练过程中通常是全局常数，指定最大生成 token 数。

注意，上述代码中的 `completion_mask` 是一个 1 和 0 的矩阵，其中提示 token 被掩码掉（0），因为我们不希望模型从预测提示 token 中学习。

#### 这为什么重要？

直观地说，逐序列归一化（策略 1）似乎最好，因为我们关心的是*结果*而非单独的 token。然而，这引入了基于序列长度的微妙偏差，可能导致模型过度思考或降低自然需要使用更多 token 的策略的权重，具体取决于偏差方向。考虑两个不同长度的序列及其逐 token 损失：

```python
seq_1_losses = [1, 1, 1, 1, 10]  # 5 tokens, mean = 2.8
seq_2_losses = [1, 1, 1, 1, 1, 1, 1, 1, 1, 10]  # 10 tokens, mean = 1.9
```

对于**策略 1**（逐序列）：批次损失为 $(2.8 + 1.9)/2 = 2.35$，关键的是，短序列中的每个 token 接收的梯度比长序列中的 token 更大。

对于**策略 2**（逐 token）：批次损失为 $(14 + 19)/15 = 2.2$，所有 token 接收相等的梯度量级。

对于**策略 3**（固定长度，$L_{\max}=10$）：短序列贡献 $1.4$，长序列贡献 $1.9$，在平衡每 token 梯度的同时仍按序列加权。

有关展示这些策略如何影响梯度的更完整示例，请参见下面的脚本。

```python
from typing import Optional
import torch

def masked_mean(values: torch.Tensor, mask: torch.Tensor, axis: Optional[int] = None) -> torch.Tensor:
    """Compute mean of tensor with masked values."""
    if axis is not None:
        return (values * mask).sum(axis=axis) / mask.sum(axis=axis)
    else:
        return (values * mask).sum() / mask.sum()

def masked_sum(
        values: torch.Tensor,
        mask: torch.Tensor,
        axis: Optional[int] = None,
        constant_normalizer: float = 1.0,
    ) -> torch.Tensor:
    """Compute sum of tensor with masked values. Use a constant to normalize."""
    if axis is not None:
        return (values * mask).sum(axis=axis) / constant_normalizer
    else:
        return (values * mask).sum() / constant_normalizer

ratio = torch.tensor([
    [1., 1, 1, 1, 1, 1, 1,],
    [1, 1, 1, 1, 1, 1, 1,],
], requires_grad=True)


advs = torch.tensor([
    [2, 2, 2, 2, 2, 2, 2,],
    [2, 2, 2, 2, 2, 2, 2,],
])

masks = torch.tensor([
    # generation 1: 4 tokens
    [1, 1, 1, 1, 0, 0, 0,],
    # generation 2: 7 tokens
    [1, 1, 1, 1, 1, 1, 1,],
])

max_gen_len = 7

masked_mean_result = masked_mean(ratio * advs, masks, axis=1)
masked_mean_token_level = masked_mean(ratio, masks, axis=None)
masked_sum_result = masked_sum(ratio * advs, masks, axis=1, constant_normalizer=max_gen_len)

print("masked_mean", masked_mean_result)
print("masked_sum", masked_sum_result)
print("masked_mean_token_level", masked_mean_token_level)

# masked_mean tensor([2., 2.], grad_fn=<DivBackward0>)
# masked_sum tensor([1.1429, 2.0000], grad_fn=<DivBackward0>)
# masked_mean_token_level tensor(1., grad_fn=<DivBackward0>)

masked_mean_result.mean().backward()
print("ratio.grad", ratio.grad)
ratio.grad.zero_()
# ratio.grad tensor([[0.2500, 0.2500, 0.2500, 0.2500, 0.0000, 0.0000, 0.0000],
# [0.1429, 0.1429, 0.1429, 0.1429, 0.1429, 0.1429, 0.1429]])

masked_sum_result.mean().backward()
print("ratio.grad", ratio.grad)
ratio.grad.zero_()
# ratio.grad tensor([[0.1429, 0.1429, 0.1429, 0.1429, 0.0000, 0.0000, 0.0000],
# [0.1429, 0.1429, 0.1429, 0.1429, 0.1429, 0.1429, 0.1429]])

masked_mean_token_level.mean().backward()
print("ratio.grad", ratio.grad)
# ratio.grad tensor([[0.0909, 0.0909, 0.0909, 0.0909, 0.0000, 0.0000, 0.0000],
# [0.0909, 0.0909, 0.0909, 0.0909, 0.0909, 0.0909, 0.0909]])
```

输出显示，使用策略 1（`masked_mean`），短序列的每 token 梯度（0.25）比长序列（0.14）更大。策略 2 和 3 使序列间的每 token 梯度均衡。请注意，如果使用梯度累积，这些结果可能变化很大，梯度在取反向步骤之前跨多个 minibatch 求和——在这种情况下，短序列和长序列之间的平衡可能翻转。

在实践中，最佳策略取决于具体的训练设置。在 RLHF 中，通常优先数值稳定性最好或损失方差最小的方法。

#### 相关：MDP 与 Bandit 框架

损失聚合的选择连接到我们在如何框定 RL 问题上更深层的区分。**MDP（token 级）**视角将每个 token $a_t$ 视为一个动作，状态 $s_t$ 是运行中的前缀。在实践中，这是在计算带有学习价值函数 $V(s_t)$（例如 GAE [@schulman2015high]）的逐 token 优势并逐 token 应用 KL 惩罚时使用的框架。带有学习价值网络的 PPO 是典范例子 [@schulman2017proximal]。

相比之下，**bandit（序列级）**视角将整个补全视为具有单个标量奖励 $R$ 的单个动作。在代码中，这意味着计算序列级优势 $A_{\text{seq}}$ 并将其广播到所有 token。RLOO 和 GRPO 式优势通常在这种 bandit 式设置中使用 [@kool2019buy] [@ahmadian2024back] [@shao2024deepseekmath]。直接对齐方法如 DPO 和 A-LoL 也定义序列级目标，尽管它们不是策略梯度估计器 [@baheti2023leftover]。

注意，许多 GRPO 实现在 bandit 式优势*和*在损失中添加单独的逐 token KL 项方面都有使用，而许多 PPO/RLOO 实现在计算优势之前将 KL 折叠到奖励中；实践中这两种约定都存在。

下面是一个突出显示两种方法的示例比较：

```python
# === Bandit-style (sequence-level) ===
# One scalar reward per sequence; advantage broadcast to all tokens
reward = torch.tensor([3.0, 1.0])       # (B,) e.g., reward model scores
baseline = reward.mean()                 # simple baseline (RLOO uses leave-one-out)
advantage_seq = reward - baseline        # (B,)
advantages = advantage_seq[:, None].expand(-1, seq_len)  # (B, L)
# tensor([[ 1.,  1.,  1.,  1.],    <- same advantage for all tokens
#         [-1., -1., -1., -1.]])

# === MDP-style (token-level) ===
# Per-token rewards + learned V(s_t); each token gets its own advantage
# (could also use per-token KL shaping, format rewards, or other token-level signals)
advantages = gae(per_token_rewards, values, done_mask, gamma=1.0, lam=0.95)
# tensor([[ 0.2,  0.5,  0.8,  1.5],    <- varies by position
#         [-0.3, -0.5, -0.8, -1.4]])
```

这种框架区分也解释了为什么折扣因子 $\gamma$ 在几乎所有 RLHF 实现中设为 1.0。在标准 RL 中，折扣（$\gamma < 1$）至关重要：它在多步回合中平衡短期和长期奖励之间的优化，这对于智能体学习有效行为至关重要。但在 RLHF 设置中，即使使用 token 级 MDP 视角，优化的归纳偏置是整体补全的质量——奖励信号对整个响应打分，而非单独的 token。折扣较早的 token 将任意降低其对奖励的贡献，而没有原则性理由。随着 agent RL 设置的成熟——其中模型采取真正的多步动作如工具调用、代码执行和网页浏览——折扣可能再次变得相关，因为这些涉及真正不同的序列决策，其长期后果各不相同。

### 异步 RL 系统

策略梯度算法的默认实现被称为**同策略（on-policy）**执行，即智能体（语言模型）采取的动作（生成）在更新模型之前评分。策略梯度的理论推导依赖于所有动作严格同策略，其中模型始终与最新试验/roll-out 的结果保持最新。在实践中，维护精确的同策略执行大幅减缓训练 [@noukhovitch2024asynchronous]——无论怎样，完美的同步在技术上都是不可能的。因此，所有最近的与语言模型的实证结果往往略微偏离理论证明。在实践中发生的事情是为实际有效的情况设计算法和系统。

![同步或异步 RL 训练的生成-更新阶段比较，遵循 Noukhovitch 等人 2024。](images/async_v_synch_rl.png){#fig:async}

常用的解决方案是在不同的 GPU 节点上持续运行推理和训练，并使用专为同时高效运行两者而设计的软件，如 @fig:async 底部所示。在语言模型的流行开源 RL 工具中，常见的做法是使用 Ray 等分布式进程管理库来在策略梯度学习循环和推理循环之间传递信息，使用高效的推理引擎，例如 vLLM。在这些设置中，专门用于执行 RL 步骤的 GPU 称为"学习者（learners）"，专门用于从语言模型采样的 GPU 称为"演员（actors）"。使训练更异步时面临的主要挑战是保持训练稳定和维护学习信号。

![一个分布式 RL 系统的示例，其中管理两个队列以将数据传递给学习者 GPU 和演员 GPU，两者都可以使用分布式计算库如 Ray 进行同步。Olmo Team 2025，许可证 CC-BY。](images/distributed-rl.png){#fig:async_system}

这些系统的设计和实现基于几乎同策略数据足够稳定学习的假设。在这里，生成和更新阶段可以轻松同步以避免训练系统中任何部分的空闲计算，这将是在 @fig:async_system 中将模型权重从学习者传递给演员。对于推理模型，需要每答案 10K 到 100K+ token 的极端长推理特性使 rollout 生成为更强的瓶颈。在更同步的 RL 基础设施上训练推理模型时的一个常见问题是，批次中一个提示的答案可能需要更长时间来生成（通过更多 token 或更多工具调用），导致大多数分配的算力在等待完成时空闲。解决这个长度不匹配问题的第二种方案，称为序列级打包，是在批次中将较短样本堆叠并通过巧妙的掩码来启用来自模型的持续 rollout 并更好地在批次中的样本之间分配长度归一化。分布式 RL 基础设施的完整复杂性超出了本书范围，因为它可能导致许多其他微妙问题，减缓训练或导致不稳定。

随着这些推理模型的出现，对将训练和推理循环完全离策略产生了进一步兴趣，其中策略梯度更新训练批次填充来自多个实例生成答案的最近完成 rollout [@wu2025llamarl] [@fu2025areal]。完全异步训练也将通过增加学习者节点（执行策略梯度步骤）和演员（尝试解决问题）之间权重同步的时间间隔，更容易在多个数据中心之间扩展 RL 训练运行 [@primeintellectteam2025intellect2reasoningmodeltrained]。

相关方法正在探索完全离策略的策略梯度算法 [@leroux2025topr]。

### 截断重要性采样

截断重要性采样（Truncated Importance Sampling, TIS）是在现代异步 RL 框架中与语言模型一起稳定训练的关键工具。重要性采样是一种校正，重新加权从一个分布中绘制的样本来估计另一个分布下的期望（如 @eq:IS_identity 中介绍）。截断重要性采样 [@ionides2008truncated] 使用 $\min(\rho, C)$ 对这些权重施加上限，以一定的微小偏差换取策略梯度中方差的有界性。

这是一种应用于策略梯度的重要性采样校正，但与 PPO 和 CISPO 中的双边裁剪（将比率约束在 1 附近）不同，TIS 使用单边上界：比率可以在 1 以下自由下降，但被上限 $C$ 限制以防止极端加权。在 PPO、GRPO、CISPO（和相关算法）中，比率 $\rho_t^{\text{policy}} = \pi_\theta(a_t \mid s) / \pi_{\theta_{\text{old}}}(a_t \mid s)$ 校正在一个 RL 批次内多个梯度步骤之间的策略漂移。随着我们转向基于上文中异步思想的现实 RL 框架，还有更多来源的数值差异（也需要重要性采样的数值校正）。即使采样器和学习者共享相同的参数 $\theta$，它们的有效 token 分布也可能不同，因为推理引擎（例如 vLLM）和训练框架（例如 FSDP）使用不同的内核、精度和并行策略 [@yao2025offpolicy]。因此，区分同一策略在两个系统上的评估 $\pi_\theta^{\text{sampler}}$ 和 $\pi_\theta^{\text{learner}}$ 并定义相应的比率和其截断形式是有用的：

$$
\rho_t^{\text{learner}} = \frac{\pi_\theta^{\text{learner}}(a_t \mid s, a_{<t})}{\pi_\theta^{\text{sampler}}(a_t \mid s, a_{<t})}, \qquad \tilde{\rho}_t^{\text{learner}} = \min(\rho_t^{\text{learner}},\; C).
$$ {#eq:tis_backend}

这两种校正是互补的，但它们出现在策略梯度实现中的原因不同——一个补偿一个 RL 批次训练内的策略漂移，另一个补偿实现引发的发散——可以同时应用。它们如何组合取决于算法：

#### 带 TIS 的 REINFORCE（单步梯度）

没有策略漂移（$\pi_\theta = \pi_{\theta_\text{old}}$），唯一的失配在学习者和采样器之间。这里 $\pi_{\theta_\text{old}} = \pi_\text{gen}$，TIS 直接校正学习者-采样器差距：

$$
\nabla_\theta J \approx \mathbb{E}_{a \sim \pi_\theta^{\text{sampler}}} \left[ \tilde{\rho}_t^{\text{learner}} \cdot A_t \cdot \nabla_\theta \log \pi_\theta^{\text{learner}}(a_t \mid s, a_{<t}) \right].
$$ {#eq:reinforce_tis}

#### 带 TIS 的 PPO/GRPO（多步梯度）

现在两个比率都生效。在仔细的实现中，策略比率中的"旧对数概率"在学习者上重新计算（GSPO 论文讨论了这一点），因此策略比率 $\rho_t^{\text{policy}} = \pi_\theta^{\text{learner}} / \pi_{\theta_\text{old}}^{\text{learner}}$ 捕获纯策略漂移，而 $\tilde{\rho}_t^{\text{learner}} = \min(\pi_{\theta_\text{old}}^{\text{learner}} / \pi_{\theta_\text{old}}^{\text{sampler}},\; C)$ 单独在生成检查点校正后端失配：

$$
J_{\text{PPO+TIS}}(\theta) = \mathbb{E}\left[ \min\!\left( \rho_t^{\text{policy}}\, A_t,\; \text{clip}\!\left(\rho_t^{\text{policy}}, 1-\varepsilon, 1+\varepsilon\right) A_t \right) \cdot \tilde{\rho}_t^{\text{learner}} \right].
$$ {#eq:ppo_tis}

这里 $\pi_{\theta_\text{old}} \neq \pi_\text{gen}$：旧对数概率来自学习者，而非采样器。如果框架跳过此重新计算并直接使用采样器对数概率作为 $\pi_{\theta_{\text{old}}}$，策略比率已经捕获后端失配，不需要单独的 TIS 校正——但裁剪操作在一个起始偏离 1.0 的更嘈杂的比率上。这是 Yao 等人 [-@yao2025offpolicy] 的"你的框架暗中给你带来离策略 RL"的观察。

在实践中，LLM RL 系统将 TIS 作为策略梯度损失上的逐 token 校正权重应用：

```python
# Shape: (B*G, L)
C = 2.0  # TIS cap

logratio = learner_logprobs - sampler_logprobs
logratio = logratio.clamp(-10.0, 10.0)              # numerical safety
tis_weight = torch.exp(logratio).clamp(max=C)        # one-sided truncation

# Use as a fixed correction weight on the per-token PG loss
per_token_pg_loss = per_token_pg_loss * tis_weight.detach()
```

$[-10, 10]$ 的钳位仅在指数化之前用于数值稳定性；实际的截断重要性采样步骤是 $C$ 的单边上界。在实践中，关于这些对数概率的簿记——从生成中存储采样器对数概率、在旧检查点重新计算学习者对数概率以及在梯度步骤期间跟踪当前对数概率——是分布式 RL 框架脚手架的大部分。与 GSPO 不同，此校正是逐 token 的，因为它解决的是逐 token 的数值失配而非序列级奖励粒度。学习者-采样器比率的 TIS 已被主要的开源 RL 框架广泛采用（VeRL、TRL、OpenRLHF、SkyRL、OAT 和 Open Instruct，后者使用 $C = 2$），并且对于长推理轨迹（第 7 章）变得越来越重要，因为小的逐 token 差异会在数千个生成的 token 上累积。


### 示例：PPO

有许多 PPO 的实现。核心*损失*计算如下所示。稳定性能的关键也在于*价值*计算，其中存在多种选项（包括价值模型*损失*的多种选项）。

注意，这里的参考策略（或旧对数概率）来自采样生成时的状态，不一定是参考策略。参考策略仅用于 KL 距离约束/惩罚。

```python
# B: Batch Size, L: Sequence Length, G: Num of Generations
# Apply KL penalty to rewards
rewards = rewards - self.beta * per_token_kl  # Shape: (B*G, L)

# Get value predictions
values = value_net(completions)  # Shape: (B*G, L)

# Compute returns via backward pass (gamma typically 1.0 for LM RLHF)
# Mask rewards to avoid padding tokens (which may have KL penalties) leaking into returns
returns = torch.zeros_like(rewards)
running = torch.zeros(rewards.shape[0], device=rewards.device, dtype=rewards.dtype)
for t in reversed(range(rewards.shape[1])):
    # Zero out padding: only accumulate rewards/returns for valid completion tokens
    running = (rewards[:, t] + self.gamma * running) * completion_mask[:, t]
    returns[:, t] = running

# Compute advantages: A_t = G_t - V(s_t)
advantages = returns - values.detach()  # Shape: (B*G, L)
# Note: We detach the value network here to not update the parameters of
# the value function when computing the policy-gradient loss

# Normalize advantages (optional but stable)
advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

# Compute probability ratio between new and old policies
ratio = torch.exp(new_per_token_logps - per_token_logps)  # Shape: (B*G, L)

# PPO clipping objective
eps = self.cliprange  # e.g. 0.2
pg_losses1 = -advantages * ratio  # Shape: (B*G, L)
pg_losses2 = -advantages * torch.clamp(ratio, 1.0 - eps, 1.0 + eps)  # Shape: (B*G, L)
pg_loss_max = torch.max(pg_losses1, pg_losses2)  # Shape: (B*G, L)

# Value function loss: predict returns
vf_loss = 0.5 * ((returns - values) ** 2)  # Shape: (B*G, L)

# Combine policy and value losses
per_token_loss = pg_loss_max + self.vf_coef * vf_loss  # Shape: (B*G, L)

# Apply completion mask and compute final loss
loss = ((per_token_loss * completion_mask).sum(dim=1) / completion_mask.sum(dim=1)).mean()
 # Scalar

# Compute metrics for logging
with torch.no_grad():
    # Compute clipping fraction
    clip_frac = ((pg_losses2 > pg_losses1).float() * completion_mask).sum() / completion_mask.sum()
    
    # Compute approximate KL
    approx_kl = (0.5 * ((new_per_token_logps - per_token_logps)**2) * completion_mask).sum() / completion_mask.sum()
    
    # Compute value loss for logging
    value_loss = vf_loss.mean()
```

理解 PPO 的关键在于理解策略梯度损失如何更新。专注于这三行：
```python
pg_losses1 = -advantages * ratio  # Shape: (B*G, L)
pg_losses2 = -advantages * torch.clamp(ratio, 1.0 - eps, 1.0 + eps)  # Shape: (B*G, L)
pg_loss_max = torch.max(pg_losses1, pg_losses2)  # Shape: (B*G, L)
```
`pg_losses1` 是原始优势加权策略梯度损失。`pg_losses2` 应用相同公式但概率比率被钳位到范围 $[1-\varepsilon, 1+\varepsilon]$，限制策略在一个更新中能改变多少。

关键洞察在于对两个损失取 `torch.max`。因为我们最小化的是一个*负*损失（回顾优势前面的负号），取最大值会选择更悲观的梯度——即产生较小策略更新的梯度。当优势为正时（好动作），裁剪防止策略太激进地增加该动作的概率。当优势为负时（坏动作），裁剪防止另一方向的过度修正。

通过对对数概率比率进行钳位，PPO 限制了策略从生成训练数据的版本漂移多远，从而稳定学习而不需要显式的信任区域计算。

上面的代码还显示了 PPO 与策略一起学习价值函数，这增加了实现复杂度，但裁剪目标是核心机制。

#### 每个样本单梯度步的 PPO/GRPO 简化（无裁剪）

如果超参数"每个样本的梯度步数"等于 1，PPO（和 GRPO）实现可以更优雅地处理。许多典型值从 2-4 或更高。在主要 PPO 或 GRPO 方程中，参见 @eq:PPO_EQN，"参考"策略是上一个参数——用于生成补全或动作的参数。因此，如果只取一个梯度步骤，$\pi_\theta = \pi_{\theta_{\text{old}}}$，更新规则简化为以下形式（记号 $[]_\nabla$ 表示停止梯度）：

$$J(\theta) = \frac{1}{G}\sum_{i=1}^G \left(\frac{\pi_\theta(a_i|s)}{\left[\pi_{\theta}(a_i|s)\right]_\nabla}A_i - \beta \mathcal{D}_{\text{KL}}(\pi_\theta||\pi_{\text{ref}})\right). $$ {#eq:ppo_1step}

这导致 PPO 或 GRPO 实现可以省略第二个策略梯度和裁剪逻辑，使优化器更接近标准策略梯度。


### 示例：GRPO

DeepSeekMath 论文描述了 GRPO 的一些实现细节，与 PPO 不同 [@shao2024deepseekmath]，特别是与从深度 RL 而非语言模型中对 PPO 的标准应用进行比较时。例如，RLHF 优化中的 KL 惩罚（回顾 KL 惩罚也用于在没有奖励模型的情况下在推理模型上训练）直接应用于损失更新而非奖励函数。标准 RLHF 的 KL 惩罚应用为 $r=r_\theta - \beta \mathcal{D}_{\text{KL}}$，GRPO 实现沿如下方向：

$$ L = L_{\text{policy gradient}} + \beta * \mathcal{D}_{\text{KL}} $$ {#eq:grpo_loss_kl}

然而，有多种方式实现这一点。传统上，KL 距离是相对于提示 $s$ 补全中的每个 token 计算的。对于推理训练，从一个提示采样多个补全，且一个批次中有多个提示，KL 距离将具有 $[B, L, N]$ 的形状，其中 B 是批次大小，L 是序列长度，N 是每个提示的补全数。

将其结合起来，使用第一种损失累加方式，伪代码可以写为如下。

```python
# B: Batch Size, L: Sequence Length, G: Number of Generations
# Compute group-wise rewards # Shape: (B,)
mean_grouped_rewards = rewards.view(-1, self.num_generations).mean(dim=1)
std_grouped_rewards = rewards.view(-1, self.num_generations).std(dim=1)    


# Normalize the rewards to compute the advantages
mean_grouped_rewards = mean_grouped_rewards.repeat_interleave(self.num_generations, dim=0)
std_grouped_rewards = std_grouped_rewards.repeat_interleave(self.num_generations, dim=0)
# Shape: (B*G,)

# Compute advantages
advantages = (rewards - mean_grouped_rewards) / (std_grouped_rewards + 1e-4)
advantages = advantages.unsqueeze(1)
# Shape: (B*G, 1)

# Compute probability ratio between new and old policies
ratio = torch.exp(new_per_token_logps - per_token_logps)  # Shape: (B*G, L)

# PPO clipping objective
eps = self.cliprange  # e.g. 0.2
pg_losses1 = -advantages * ratio  # Shape: (B*G, L)
pg_losses2 = -advantages * torch.clamp(ratio, 1.0 - eps, 1.0 + eps)  # Shape: (B*G, L)
pg_loss_max = torch.max(pg_losses1, pg_losses2)  # Shape: (B*G, L)

# important to GRPO -- PPO applies this in reward traditionally
# Combine with KL penalty
per_token_loss = pg_loss_max + self.beta * per_token_kl  # Shape: (B*G, L)

# Apply completion mask and compute final loss
loss = ((per_token_loss * completion_mask).sum(dim=1) / completion_mask.sum(dim=1)).mean()
 # Scalar

# Compute core metric for logging (KL, reward, etc. also logged)
with torch.no_grad():
    # Compute clipping fraction
    clip_frac = ((pg_losses2 > pg_losses1).float() * completion_mask).sum() / completion_mask.sum()
    
    # Compute approximate KL
    approx_kl = (0.5 * ((new_per_token_logps - per_token_logps)**2) * completion_mask).sum() / completion_mask.sum()
```

关于如何解释此代码的更多内容，请参见上述 PPO 部分。与 PPO 示例的核心区别是：

- **优势计算**：GRPO 相对于组（相同提示的各生成之间的均值和标准差）归一化奖励，而非使用学习价值函数作为基线。
- **无价值网络**：GRPO 完全移除价值模型，消除 `vf_loss` 和相关复杂度。
- **KL 惩罚位置**：GRPO 将 KL 惩罚直接添加到损失中而非从奖励中减去（这是标准实现，但关于 KL 如何应用存在更多版本）。

#### RLOO 与 GRPO

RLOO 的优势更新非常接近 GRPO，突出了算法在不考虑 PPO 式裁剪和 KL 惩罚细节时的概念相似性。具体来说，对于 RLOO，优势是相对于与 GRPO 非常相似的基线计算的——该问题的补全奖励相对于其他补全的奖励。简洁地说，RLOO 优势估计如下（扩展自 [TRL](https://github.com/huggingface/trl/blob/bfe20756082488350091352d1cdc19c172e42cd8/trl/trainer/rloo_trainer.py#L433) 的实现）：

```python
# rloo_k --> number of completions per prompt 
# rlhf_reward --> Initially a flat tensor of total rewards for all completions. Length B = N x k
rlhf_reward = rlhf_reward.reshape(rloo_k, -1) # 
# Now, Shape: (k, N), each column j contains the k rewards for prompt j.

baseline = (rlhf_reward.sum(0) - rlhf_reward) / (rloo_k - 1)
# baseline --> Leave-one-out baseline rewards. Shape: (k, N)
#  baseline[i, j] is the avg reward of samples i' != i for prompt j.

advantages = rlhf_reward - baseline
# advantages --> Same Shape: (k, N)

advantages = advantages.flatten() # Same shape as original tensor
```

RLOO 的其他实现细节遵循实现策略梯度的其他权衡。

## 辅助主题

为了掌握策略梯度算法的应用，有无数其他考虑因素。这里我们考虑成功部署策略梯度 RL 算法的一些长尾复杂度。

### 广义优势估计（GAE）

广义优势估计（Generalized Advantage Estimation, GAE）是用于策略梯度算法的优势计算的替代方法 [@schulman2015high]，更好地平衡偏差-方差权衡。传统的单步优势估计可能引入过多偏差，而使用完整轨迹可能遭受高方差。GAE 计算多步优势估计的指数加权平均，其中 $\lambda$ 超参数控制偏差-方差权衡——范围从单步 TD（$\lambda=0$）到完整轨迹回报（$\lambda=1$）；$\lambda=0.95$ 是 LLM 微调的常见默认值。

优势估计可以有许多形式，但我们可以定义一个 $n$ 步优势估计器（类似于本章开头引入的 TD 残差）如下：

$$
\hat{A}_t^{(n)} = \begin{cases}
r_t + \gamma V(s_{t+1}) - V(s_t), & n = 1 \\
r_t + \gamma r_{t+1} + \gamma^2 V(s_{t+2}) - V(s_t), & n = 2 \\
\vdots \\
r_t + \gamma r_{t+1} + \gamma^2 r_{t+2} + \cdots - V(s_t), & n = \infty
\end{cases}
$$ {#eq:K_STEP_ADV}

这里，较短的 $n$ 方差较低但偏差更高，因为我们给每条轨迹分配更多学习能力——它可能过拟合。GAE 尝试将此公式泛化为加权多步平均而非特定 $n$。首先，我们必须定义预测价值的时序差分（TD）残差。

$$
\delta_t^V = r_t + \gamma V(s_{t+1}) - V(s_t)
$$ {#eq:TD_RESIDUAL}

为了利用它，我们引入另一个变量 $\lambda$ 作为 GAE 混合参数。这折叠到我们要估计的未来优势的指数衰减中：

$$
\begin{array}{l}
\hat{A}_t^{GAE(\gamma,\lambda)} = (1-\lambda)(\hat{A}_t^{(1)} + \lambda\hat{A}_t^{(2)} + \lambda^2\hat{A}_t^{(3)} + \cdots) \\
= (1-\lambda)(\delta_t^V + \lambda(\delta_t^V + \gamma\delta_{t+1}^V) + \lambda^2(\delta_t^V + \gamma\delta_{t+1}^V + \gamma^2\delta_{t+2}^V) + \cdots) \\
= (1-\lambda)(\delta_t^V(1 + \lambda + \lambda^2 + \cdots) + \gamma\delta_{t+1}^V(\lambda + \lambda^2 + \cdots) + \cdots) \\
= (1-\lambda)\left(\delta_t^V\frac{1}{1-\lambda} + \gamma\delta_{t+1}^V\frac{\lambda}{1-\lambda} + \cdots\right) \\
= \sum_{l=0}^{\infty}(\gamma\lambda)^l\delta_{t+l}^V
\end{array}
$$ {#eq:GAE_DFN}

直观地说，这可以用来优雅地平均多步优势估计。下面的示例实现展示了这一点：

```python
# GAE (token-level) for LM RLHF
#
# B: Batch Size
# L: Length
# Inputs:
#   rewards: (B, L) post-KL per-token rewards
#   values:  (B, L) current V_theta(s_t)
#   done_mask: (B, L) 1.0 at terminal token (EOS or penalized trunc), else 0.0
#   gamma: float (often 1.0), 
#   lam (short for lambda): float in [0,1]
#   (Padding beyond terminal should have rewards=0, values=0)
B, L = rewards.shape
advantages = torch.zeros_like(rewards)
next_v = torch.zeros(B, device=rewards.device, dtype=rewards.dtype)
gae = torch.zeros(B, device=rewards.device, dtype=rewards.dtype)

for t in reversed(range(L)):
    not_done = 1.0 - done_mask[:, t]
    delta = rewards[:, t] + gamma * not_done * next_v - values[:, t]
    gae = delta + gamma * lam * not_done * gae
    advantages[:, t] = gae
    next_v = values[:, t]

targets = advantages + values      # y_t for value regression
advantages = advantages.detach()   # for policy loss
```

后向循环累积时序差分（TD）误差（$\delta_t = r_t + \gamma V(s_{t+1}) - V(s_t)$），衡量实际结果与价值函数预测相比好多少或差多少，以指数衰减 $(\gamma\lambda)^l$。在终止 token 处，`not_done=0` 防止从未来状态自举并重置 GAE 累加器，所以每个回合的优势独立计算（由于循环反向运行，终止 token 干净地停止指数加权累加在回合边界——这使得实现易于打包，正确处理拼接到一个中的多个序列）。最终的 `targets` 作为在 GAE 循环之外学习的单独价值函数的回归目标，而解耦的 `advantages` 加权策略梯度——解耦以便策略更新不通过价值网络反向传播。在语言模型的 RLHF 中，$\gamma=1.0$ 很常见，因为回合是短的 token 序列，其中更偏好无折扣信用分配（且通常一个中所有的 token）。

*更多内容参见 [@seita2017gae]。*

### 双重正则化

我们在本章中看到了两种类型的正则化。一种是构建在 PPO 等算法中的步长约束，另一种是基于相对于优化开始的 KL 散度距离惩罚。

来自深度强化学习的许多流行策略梯度算法，包括 PPO 及其前身，因需要控制智能体的学习过程而起源。在 RLHF 中，如第 15 章关于正则化和第 3 章关于训练概述中广泛讨论的，存在通过距离惩罚的内置正则化，相对于一个正在微调的原始策略。从这个角度看，PPO（具有内部步长正则化）和 REINFORCE（更简单，在某些超参数下 PPO 简化为它）等算法之间的区别对于微调语言模型而言比从头训练智能体而言意义小得多。

在 PPO 中，负责限制更新步长的目标是所谓的[代理目标](https://huggingface.co/blog/deep-rl-ppo#introducing-the-clipped-surrogate-objective)。要监控 PPO 正则化在 RLHF 中对更新的影响，可以查看许多流行实现中的 clip fraction 变量，这是批次中概率比率落在裁剪区间外的样本百分比。这是一个有用的代理指标，用于衡量 PPO 正则器可能激活的频率，但并非每个这样的样本都有零梯度：仅在选择了裁剪分支时代理变为平坦，例如正优势样本中比率高于 $1+\varepsilon$ 或负优势样本中比率低于 $1-\varepsilon$。

在实践中，对于语言模型，PPO 和 GRPO 等算法通常每个批次仅运行一个梯度步骤，这意味着 PPO 原生正则化从不应用（因为裁剪只能在策略发生大变化时在一个批次内发生），KL 距离惩罚占主导地位。然而，这不是普遍的。例如，DAPO 使用每个批次 16 个梯度步骤 [@yu2025dapo]，Tülu 3 对 8B 和 70B 模型使用每个批次 4 个 PPO 更新迭代，但对 405B 减少到 1 以保持训练稳定 [@lambert2024t]。

### 延伸阅读

随着 RLHF 在现代后训练中稳固其核心地位，其他策略梯度 RL 算法和 RL 算法一般被提出以改进训练过程，但它们未在指导最佳实践中发挥核心作用。延伸阅读的示例包括：

- **成对近端策略优化（Pairwise Proximal Policy Optimization, P3O；Wu 等人，2023）** [@wu2023pairwise] 直接在 PPO 式策略更新中使用成对数据，无需学习中间奖励模型。
- **软自适应策略优化（Soft Adaptive Policy Optimization, SAPO）** [@gao2025sapo] 用平滑的、温度控制的门控替代硬 PPO/GRPO 式裁剪，旨在为连续的信任区域，保留近同策略学习信号同时降低离策略 token 的权重。
- 离策略策略梯度算法可以启用进一步异步训练，如**对比策略梯度（Contrastive Policy Gradient, CoPG）** [@flet2024contrastive]（直接对齐算法 IPO 和原始策略梯度的泛化），被 Cohere 用于其 Command A 模型 [@cohere2025command]。
- 为语言模型设计的其他 REINFORCE 算法实现包括 **ReMax** [@li2023remax]，其实现了一种专门设计用于容纳奖励模型推理来源不确定性的基线归一化。
- 一些基础模型，如 Apple Intelligence Foundation Models [@gunter2024apple] 或 Kimi k1.5 推理模型 [@team2025kimi]，使用了**镜像下降策略优化（Mirror Descent Policy Optimization, MDPO）** [@tomar2020mirror] 的变体。相关基础研究仍在推进 [@zhang2025improving]，但镜像下降是一种优化方法，并不直接等同于策略梯度算法。这里重要的是，它可以以非常相似的方式接入已有的 RL 基础设施。
- **解耦裁剪和动态采样策略优化（Decoupled Clip and Dynamic sAmpling Policy Optimization, DAPO）** 提出了对 GRPO 的 4 项修改以更好地适合推理语言模型，其中需要长轨迹且需要增加新未充分利用 token 的概率 [@yu2025dapo]。这些变化是：1，有两个不同的裁剪超参数 $\varepsilon_\text{low}$ 和 $\varepsilon_\text{high}$，所以 logratio 正侧的裁剪可以采取更大步骤以更好探索；2，动态采样，移除批次中所有奖励=0 或奖励=1 的样本（无学习信号）；3，使用上面实现部分讨论的逐 token 损失；4，对过长样本施加软惩罚以避免尝试从不完整答案中学习。
- **基于价值增强的近端策略优化（Value-based Augmented Proximal Policy Optimization, VAPO）** [@yuan2025vapo] 将来自 DAPO 的优化（包括 clip-higher、token 级策略梯度和不同的长度归一化）与来自 Value-Calibrated PPO [@yuan2025s] 的见解相结合，预训练价值函数和长度自适应 GAE，以展示基于价值方法相对于 GRPO 的潜力。

## 建议实验

配套实现在 `code/policy_gradients/` 中，设计用于小型、可观察的 RL 运行。默认配置在 `reasoning-gym` 的 `spell_backward` 过程任务上训练 `Qwen/Qwen3-1.7B`，这是一个很好的首练，因为失败和部分进展易于检查。

1. **用 GRPO 运行单词反转任务。**

   ```bash
   cd code/
   uv run python -m policy_gradients.train --config policy_gradients/configs/grpo.yaml
   ```

   跟踪 `avg_correctness`、`avg_format` 和 `avg_binary`。第一个有用的问题是每个提示组是否包含对比：如果所有采样补全都正确或都错误，组内相对更新几乎没有学习信号。

2. **比较组内相对估计器和单样本估计器。**
   运行匹配的起始配置：

   ```bash
   cd code/
   uv run python -m policy_gradients.train --config policy_gradients/configs/reinforce.yaml
   uv run python -m policy_gradients.train --config policy_gradients/configs/rloo.yaml
   uv run python -m policy_gradients.train --config policy_gradients/configs/grpo.yaml
   ```

   比较正确性信号改善的速度以及损失的噪声程度。RLOO 和 GRPO 应使组内基线的角色比方程本身更具体。

3. **扫描对比调节旋钮。**
   复制 `policy_gradients/configs/grpo.yaml` 并更改 `num_rollouts`、`temperature`、`data.size` 和 `format_weight`。小 `num_rollouts` 减少组对比；非常低的温度可能使样本崩溃；非常高的温度可能生成太多格式错误的回答。这是理解为什么 RLVR 配方在接触优化器之前花费如此多精力在采样设置上的最简单方式。

4. **从玩具奖励转向数学。**
   对于 GSM8K 风格实验，从 `code/reward_models/train_orm.py` 和 `code/rejection_sampling/` 示例开始，然后再添加新的在线 RL 环境。一个好的贡献是小型 `reasoning-gym` 或 GSM8K 策略梯度配置，在小于 1B 的 Qwen 模型上运行并报告相同的组对比诊断。

<!-- 译者新增：自测题 -->

## 自测题（译者新增）

1. 策略梯度公式 $\Delta \theta \propto \Psi_t \, \nabla_\theta \log \pi_\theta(a_t \mid s_t)$ 中，$\Psi_t$ 和 $\nabla_\theta \log \pi_\theta(a_t \mid s_t)$ 各自的作用是什么？如果 $\Psi_t$ 始终为正，策略会如何变化？
2. PPO 中的裁剪机制（$\varepsilon$ 参数）如何防止策略在一次更新中发生过大改变？请结合正优势和负优势两种情况说明裁剪区域的作用。
3. 与 PPO 相比，GRPO 在优势计算和价值函数方面有哪些主要简化？这些简化带来了哪些实际好处？
4. 策略梯度算法中的"重要性采样"解决的是什么问题？为什么在取多个梯度步骤时需要它？
5. 为什么在 RLHF 中折扣因子 $\gamma$ 通常设为 1？这与标准 RL 中的折扣设定有何不同？
6. 三种损失聚合策略（逐序列归一化、逐 token 归一化、固定长度归一化）各自有什么优缺点？在什么场景下哪种策略更合适？
