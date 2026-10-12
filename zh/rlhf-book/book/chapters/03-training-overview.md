<!--
  Copyright (c) 2025-2026 Nathan Lambert.
  Licensed under CC BY-NC-SA 4.0:
  https://creativecommons.org/licenses/by-nc-sa/4.0/
  Full license: https://github.com/natolambert/rlhf-book/blob/main/LICENSE-CHAPTERS
-->
---
prev-chapter: "RLHF 简史"
prev-url: "02-related-works"
page-title: 训练概览
search-title: "第 3 章: 训练概览"
meta-description: "现代后训练方法的概览，涵盖指令微调、RLHF、RLVR 和直接对齐方法。"
next-chapter: "指令微调"
next-url: "04-instruction-tuning"
lectures:
  - video: "https://www.youtube.com/watch?v=MMDNaeIFVy8&list=PLL1tdVxB1CpVpEtMHxwuR4uI4Lxjw00_y&index=2"
    label: "讲座 0：先修知识"
  - video: "https://www.youtube.com/watch?v=o6l6tJQgUg4&list=PLL1tdVxB1CpVpEtMHxwuR4uI4Lxjw00_y&index=2"
    label: "讲座 1：总览（第 1–3 章）"
---

# 训练概览

本章对基于人类反馈的强化学习（RLHF, *Reinforcement Learning from Human Feedback*）的训练流程做一个概览性介绍，更细致的内容会在本书后面逐步展开。
RLHF 虽然优化的只是一个"简单"的损失函数，但它需要在序列上训练多个不同的 AI 模型，并将它们串连起来进行一个复杂的在线优化过程。

在这里，我们会介绍 RLHF 的核心目标——用一个基于距离的正则化项来优化一个衡量人类偏好的代理奖励（同时也会说明它与经典强化学习问题的关系）。
然后我们会展示几种用 RLHF 训练顶级模型的"经典配方"（canonical recipes），展示 RLHF 如何与其余后训练（post-training）方法配合。
这些例子配方会在本书后半部分反复被引用——那时我们会详细讨论在做 RLHF 时你可以做出的不同优化选择，并且回顾各个知名模型在训练过程中使用了哪些不同的步骤。

## 问题建模

基于人类反馈的强化学习（RLHF）建立在标准强化学习（RL, *Reinforcement Learning*）框架之上。
在 RL 中，一个智能体（agent）在环境状态 $s_t$ 下，从策略 $\pi(a_t\mid s_t)$ 采样得到动作 $a_t$，以最大化奖励 $r(s_t,a_t)$ [@sutton2018reinforcement]。
策略是一个将每个状态映射为动作上概率分布的函数。
演化到现代 RLHF 文献中的早期策略属于人们常说的**深度强化学习**（deep reinforcement learning）——即使用神经网络来学习上述函数。
传统上，环境按照转移（动力学）$p(s_{t+1}\mid s_t, a_t)$ 和初始状态分布 $\rho_0(s_0)$ 演化。
策略和动力学共同产生了一个轨迹（trajectory）分布。
一个轨迹的整体概率等于初始状态概率、策略做出的每一个动作选择、以及环境产生的每一个状态转移的乘积：

$$p_{\pi}(\tau)=\rho_0(s_0)\prod_{t=0}^{T-1}\pi(a_t\mid s_t)\,p(s_{t+1}\mid s_t,a_t).$$ {#eq:rl_dynam}

对于一个步数上限（horizon）为 $T$ 的有限回合（episode），RL 智能体的目标是求解如下优化问题，其中 $\gamma$ 是一个介于 0 到 1 之间的折扣因子（discount factor），用于平衡近期奖励与远期奖励的重要性：

$$\max_\pi \; \mathbb{E}_{\tau \sim p_{\pi}} \left[ \sum_{t=0}^{T-1} \gamma^t r(s_t, a_t) \right].$$ {#eq:rl_opt}

给定策略的期望回报通常记作 $J(\pi)$，最优值记为 $J^* = \max_\pi J(\pi)$。

对于持续进行（continuing）的任务，通常取 $T\to\infty$ 并依赖折扣因子（$\gamma<1$）来保证目标函数是有定义的。
优化该表达式的多种方法见第 6 章。

![标准 RL 循环](images/rl.png){#fig:rl width=320px .center data-dark-src="images/rl-dark.png"}

@fig:rl 是 RL 循环的标准示意图（可与后续 @fig:rlhf 中的 RLHF 循环对比）。

### 一个简单的例子：恒温器 {#example-rl-thermostat}

为了建立对 RL 运作方式的直观理解，考虑一个试图将房间维持在目标温度 70$^\circ$F（约 21$^\circ$C）的恒温器。
在 RL 中，智能体从零开始、对任务没有任何先验知识，必须通过试错来发现一个好策略。
恒温器例子包含以下几个组件（参见 @fig:thermostat-equation，它展示了每个组件如何映射到 @eq:rl_dynam 中的轨迹分布）：

- **状态（$s_t$）**：当前的房间温度，例如 65$^\circ$F。
- **动作（$a_t$）**：打开或关闭加热器。
- **奖励（$r$）**：当温度距目标值在 2$^\circ$F 以内时奖励 +1，否则为 0。
- **策略（$\pi$）**：根据当前温度决定打开或关闭加热器的规则。以下是恒温器可能学到的一个策略——根据环境具体的转移动力学，这个策略未必是最优的：

$$\pi(a_t = \text{on} \mid s_t) = \begin{cases} 1 & \text{if } s_t < 70^{\circ}\text{F} \\ 0 & \text{otherwise} \end{cases}$$ {#eq:thermostat_policy}

- **转移（Transition）**：加热器打开时房间升温，关闭时房间降温。智能体可以通过动作影响这些动力学过程，但底层的物理规律（房间升温或降温有多快）并不在其控制范围内。

![轨迹分布 (@eq:rl_dynam) 的每一项与恒温器 RL 例子的对应关系。](images/thermostat_equation.png){#fig:thermostat-equation .center data-dark-src="images/thermostat_equation-dark.png"}

起初，恒温器的策略几乎是随机的——它会不考虑当前温度就随意开关加热器，导致房间温度剧烈波动。
经过大量回合的试错，智能体发现"室温低时打开加热器、室温高时关闭加热器"能获得更多奖励，并逐渐收敛到一个合理的策略。
这就是 RL 的核心循环：观察状态、选择动作、获得奖励、更新策略以在时间上积累更多奖励。

> 译者注：恒温器例子中的策略是一个确定性规则（deterministic policy），即给定状态 $s_t$ 后动作被完全确定。实际语言模型中的策略是概率性的，同一个 prompt 可能产生多个不同的回复。不过这个简化例子很好地展示了 RL 中"状态→动作→奖励"的基本逻辑。

### 经典 RL 例子：CartPole

为了获得一个具有连续动力学的更丰富的例子，我们来看经典的 *CartPole*（倒立摆）控制任务——它出现在许多 RL 教科书、课程甚至研究论文中。
恒温器只有一个状态变量和二元动作，而 CartPole 涉及四个连续的状态变量和基于物理的转移，这使得它成为 RL 算法的一个标准基准。

![CartPole 环境，展示状态变量（$x$, $\dot{x}$, $\theta$, $\dot{\theta}$）和动作（$\pm F$）。](images/cartpole.png){#fig:cartpole width=400px .center data-dark-src="images/cartpole-dark.png"}

- **状态（$s_t$）**：小车的位移/速度以及摆杆的角度/角速度：

  $$s_t = (x_t,\,\dot{x}_t,\,\theta_t,\,\dot{\theta}_t).$$ {#eq:cartpole_state}

- **动作（$a_t$）**：给小车施加向左或向右的水平力，例如 $a_t \in \{-F, +F\}$。

- **奖励（$r$）**：一个简单的奖励规则是：只要摆杆保持平衡且小车仍在轨道上（例如 $|x_t| \le 2.4$ 且 $|\theta_t| \le 12^\circ$），每一步给予 $r_t = 1$；一旦超出任一边界则 episode 终止。

- **动力学 / 转移（$p(s_{t+1}\mid s_t,a_t)$）**：在许多环境中动力学是确定性的（即 $p$ 是一个点质量分布），可以写成 $s_{t+1} = f(s_t,a_t)$，使用步长 $\Delta t$ 的欧拉积分。一个标准的简化版 CartPole 更新使用了以下常量：小车质量 $m_c$、摆杆质量 $m_p$、摆杆半长 $l$、重力加速度 $g$（$\alpha$ 是一个具有加速度单位的归一化中间变量）：

  $$\alpha = \frac{a_t + m_p l\,\dot{\theta}_t^2\sin\theta_t}{m_c + m_p}$$ {#eq:cartpole_temp}

  $$\ddot{\theta}_t = \frac{g\sin\theta_t - \cos\theta_t\,\alpha}{l\left(\tfrac{4}{3} - \frac{m_p\cos^2\theta_t}{m_c + m_p}\right)}$$ {#eq:cartpole_angular_accel}

  $$\ddot{x}_t = \alpha - \frac{m_p l\,\ddot{\theta}_t\cos\theta_t}{m_c + m_p}$$ {#eq:cartpole_linear_accel}

  $$x_{t+1}=x_t+\Delta t\,\dot{x}_t,\quad \dot{x}_{t+1}=\dot{x}_t+\Delta t\,\ddot{x}_t,$$ {#eq:cartpole_pos_update}
  $$\theta_{t+1}=\theta_t+\Delta t\,\dot{\theta}_t,\quad \dot{\theta}_{t+1}=\dot{\theta}_t+\Delta t\,\ddot{\theta}_t.$$ {#eq:cartpole_angle_update}

这就是上述一般框架的一个具体实例：策略选择 $a_t$，转移函数推动状态前进，奖励则在整个 episode 中累积。

### 改造标准 RL 设置

RLHF 所采用的 RL 公式被视为一个"更不开放"的问题——为了让语言模型能够适配，RL 的若干关键部分被设定为特定的定义。
从标准 RL 到 RLHF，有几个核心的改动：
表 @tbl:rl-vs-rlhf 总结了标准 RL 与用于语言模型的 RLHF 设置之间的差异。

1. **从奖励函数变为奖励模型。** 在 RLHF 中，使用一个学习出来的人类偏好模型 $r_\theta(s_t, a_t)$（或任何其他分类模型）来代替环境中的奖励函数。这让设计者在方法的灵活性和对最终结果的控制上有了大幅提升，但代价是实现的复杂性。在标准 RL 中，奖励被视为环境的一个静态组成部分，设计学习智能体的人无法对其修改或操控。
2. **不存在状态转移。** 在 RLHF 中，该领域的初始状态是从训练数据集中采样的 prompt（提示），而"动作"即对该 prompt 的 completion（补全）。在标准 RLHF 设置中，prompt 是固定的，模型的补全不会决定下一个 prompt。一个 prompt 加一个 completion 就构成一个完整的 episode（或 rollout）；而在经典 RL 问题中，这相当于大量重复的"状态-动作、状态-动作"链。
3. **响应级奖励与无折扣。** RLHF 对奖励的分配是对一整段动作序列（由多个生成的 token 组成）进行的，而不是细粒度地逐动作分配（这种单步结构在 RL 文献中有时被称为"赌博机问题"，bandit problem）。为了让 RLHF 的 RL 算法将每个 token 视为同一个动作的一部分，实现中通常使用折扣因子 $\gamma = 1$（即无折扣），这与标准 RL 中 $\gamma < 1$ 用于平衡短期和长期奖励形成对比。

::: {.table-wrap}
| 方面 | 标准 RL | RLHF（语言模型） |
|---|---|---|
| 策略 | 从零学起（随机初始化） | 从预训练语言模型微调而来 |
| 奖励信号 | 环境奖励函数 $r(s_t,a_t)$ | 学习到的奖励/偏好模型 $r_\theta(x,y)$（prompt $x$，补全 $y$） |
| 状态转移 | 有：动力学 $p(s_{t+1}\mid s_t,a_t)$ | 通常无：prompt $x$ 从数据集中采样；补全不会决定下一个 prompt |
| 动作 | 单个环境动作 $a_t$ | 一个补全 $y$（token 序列），从 $\pi_\theta(\cdot\mid x)$ 中采样 |
| 奖励粒度 | 常常是逐步的/细粒度的 | 通常为响应级别（赌博机风格），针对完整补全，通常无折扣（$\gamma = 1$） |
| 回合长度 | 多步 episode（$T>1$） | 通常单步（$T=1$），但多轮对话可建模为更长 horizon |
表: 标准 RL 与用于语言模型的 RLHF 之间的关键差异。{#tbl:rl-vs-rlhf}
:::

鉴于问题是单轮（single-turn）的，优化目标可以重写为不含时间 horizon 和折扣因子的形式（并显式包含奖励模型）：
$$\max_\pi \; \mathbb{E}_{\tau \sim \pi} \left[r_\theta(s_t, a_t) \right].$$ {#eq:rl_opt_int}

在很多意义上，结果是：虽然 RLHF 大量借鉴了 RL 优化器和问题公式，但其实际实现与传统 RL 非常不同。

![标准 RLHF 循环](images/rlhf.png){#fig:rlhf data-dark-src="images/rlhf-dark.png"}

> 译者注：这里重写后的公式中，$\tau$ 实际上代表一个"prompt-completion"对，而非传统 RL 中的一条多步轨迹。$s_t$ 是 prompt，$a_t$ 是整个补全序列。这个简化是理解 RLHF 与语言模型适配关系的关键。

### 微调与正则化

在传统 RL 问题中，智能体必须从零初始化策略开始学习；但在 RLHF 中，我们从一个强大的预训练基础模型出发，它已经具备丰富的初始能力。
这种强大的先验意味着 RLHF 需要防止优化过程偏离初始策略过远。
为了在微调（fine-tuning）范式下取得成功，RLHF 技术使用了多种类型的正则化（regularization）来控制优化。
目标是让奖励最大化仍然能够发生，同时防止模型出现过度优化（over-optimization）——正如第 14 章所讨论的那样。
对优化目标最常见的改动是增加一个 KL 散度惩罚项，用以约束当前 RLHF 策略与优化起点之间的距离。
超参数 $\beta$ 在训练模型时设置，控制该约束的强度——较大的 $\beta$ 让模型更靠近其起点，较小的 $\beta$ 则给优化器更多的自由去追逐奖励：

$$\max_\pi \; \mathbb{E}_{\tau \sim \pi} \left[r_\theta(s_t, a_t)\right] - \beta  \mathcal{D}_{\text{KL}}(\pi(\cdot|s_t) \| \pi_{\text{ref}}(\cdot|s_t)).$$ {#eq:rlhf_opt_eq}

在这个公式框架下，大量关于 RLHF 训练的研究致力于理解如何在距初始模型的一定"KL 预算"内进行花费。
更多细节见第 15 章（正则化）。

> 译者注：KL 散度 $\mathcal{D}_{\text{KL}}$ 在这里衡量两个概率分布之间的差异——当前策略 $\pi$ 与参考策略 $\pi_{\text{ref}}$（即预训练模型，或在 SFT 阶段训练出的模型）。
> 当 $\beta \to 0$ 时，优化器可以任意偏离预训练分布来追求奖励，可能导致奖励投机（reward hacking）或生成质量退化；当 $\beta$ 过大时，模型又无法充分优化奖励。调节 $\beta$ 是 RLHF 实践中最重要的调参工作之一。


### 优化工具

在本章及全书中，我们会详细讨论解决这一优化问题的多种流行技术。
后训练中常用的工具有：

- **奖励建模**（第 5 章）：训练一个模型来捕捉收集到的偏好数据中的信号，然后可以输出一个标量奖励来指示后续文本的质量。
- **指令微调**（第 4 章）：RLHF 的前置步骤，通过模仿预先选定的样本来教会模型在当下绝大多数语言建模交互中使用的问答格式。
- **拒绝采样**（第 9 章）：最基础的 RLHF 技术——用模仿人类偏好的奖励模型来过滤指令微调的候选补全。
- **策略梯度**（第 6 章）：RLHF 开创性示例中使用的强化学习算法，用于根据奖励模型的信号来更新语言模型的参数。
- **直接对齐算法**（第 8 章）：直接从成对偏好数据优化策略的算法，而非先学习一个中间奖励模型再在后续优化它。

现代的 RLHF 训练模型总是先使用指令微调，然后结合其他优化选项中的若干种。

### RL 在语言模型后训练中的隐性优势

在接下来的章节中，我们会覆盖后训练的多种优化工具。
其中不少方法——如拒绝采样（第 9 章）和直接对齐算法（如 DPO，第 8 章）——远比实现 RL 简单得多。
然而，尽管替代方案更简单，基于 RL 的方法依然屡获优势。
一些趋势（如可验证奖励的强化学习 RLVR 在推理时扩展）是显而易见的，但 RL 最终被证明是语言模型一个非常适合的优化工具。
与指令微调或 DPO 类算法相比，实现 RL 需要大得多的基础设施投入，但说得通俗一点，它所提供的梯度更新"确实能帮模型大幅进步"。
这一点很难精确量化，但体现在几种反复出现的形式中：

- RL 阶段可以"修补"模型的不完美之处，使模型更容易对话或更加鲁棒（这可能是因为训练它在使用 vLLM 等推理工具时具备数值稳定性）。文献中对这一现象的确切原因尚不清楚，但其真实性已反映在 RL 在当代的日益普及中。
- RL 可以"外科手术式"地施加——模型能够很好地学习 prompt 分布所在的位置，而 RL 往往不会"压缩"模型的一般能力。Tülu 3 就是一个很好的例子：仅对数学 prompt 进行 RL 训练，同时在广泛的任务集中保持各项能力 [@lambert2024t]。

总之，语言模型上的 RL 损失函数是鲁棒的、可扩展的、有效的、灵活的——这为大量新实验开辟了广阔空间。
而开启这一道路的原始方法就是 RLHF。

## 经典训练配方

随着时间推移，各种模型被确认为专门针对 RLHF 或一般后训练的"经典配方"（canonical recipes）。
这些配方反映了它们诞生时的数据实践和模型能力。
随着配方逐渐"过时"，用相同特征训练模型会变得更简单、所需数据也更少。
整体趋势是：后训练涉及更多的优化步骤、更多的训练算法，以及更多样化的训练数据集和评估方式。

### InstructGPT：RLHF 的基础工具

在 ChatGPT 刚刚问世前后，被广泛接受的（"经典"）对语言模型进行后训练的方法有三个主要步骤，其中 RLHF 是核心环节 [@lambert2022illustrating] [@ouyang2022training] [@bai2022training]。
这三个步骤是在"基础"语言模型（即在大规模网络文本上训练的下一个 token 预测模型）之上执行的，总结如下 @fig:rlhf-basic-repeat：

1. **在 ~10K 样本上进行指令微调**：教会模型遵循问答格式，并从主要为人类编写的数据中学习一些基本技能。
2. **在 ~100K 个 prompt 及其配对补全上训练奖励模型**（论文中使用了 33K 个 prompt）：该模型从指令微调的检查点训练而来，用于捕捉你希望在最终训练中建模的多样化价值观。奖励模型即为 RLHF 的优化目标。
3. **在另外的 ~100K 个 prompt 上用 RLHF 训练指令微调后的模型**（论文中恰好使用了 31K 个，且未说明这些 prompt 是否与其他阶段中的重复）：模型在（可能与前面阶段不同的）一组 prompt 上针对奖励模型进行优化——模型先生成回答，然后接受评分。

完成 RLHF 后，模型就可以部署给使用了。
这个配方是现代 RLHF 的基础，但配方本身已经发生了显著演变——加入了更多阶段、更多数据。

![早期三阶段 RLHF 流程的示意图：SFT → 奖励模型 → 优化。](images/rlhf-basic.png){#fig:rlhf-basic-repeat}

### Tülu 3：为指令模型引入 RLVR

现代版本的后训练涉及多得多模型版本和训练阶段（即远多于 Llama 2 文档中记录的 5 个 RLHF 步骤 [@touvron2023llama]）。
@fig:rlhf-complex 展示了一个例子：模型在收敛之前经历了大量的训练迭代轮次。

![多轮次现代后训练的示意图。](images/rlhf-complex.png){#fig:rlhf-complex}

在这一时期及以后训练的最复杂模型中，大多数并未公开其训练流程的全部细节。
截至 2026 年，ChatGPT 或 Claude 等领先模型涉及大量迭代式的训练轮次。
这甚至包括训练专用模型然后合并权重的技术，以获得一个能胜任多种子任务的最终模型 [@li2022branch]（例如 Cohere 的 Command A [@cohere2025command]）。

![Tülu 3 配方摘要，包含目标技能和多步训练配方。Lambert et al. 2024, License CC-BY.](images/tulu3.png){#fig:tulu-3}

一个完全公开的、在 RLHF 中扮演重要角色的多阶段后训练示例是 Tülu 3。
Tülu 3 配方包含三个阶段：

1. **在 ~100 万条样本上进行指令微调**：这是一个主要由合成数据构成的数据集，来自 GPT-4o 和 Llama 3.1 405B 等前沿模型的混合，教会模型通用的指令遵循能力，并作为数学和编码等能力的基础。
2. **在同策略偏好数据上训练 ~100 万对偏好对**：此阶段大幅提升了模型的多话性（chattiness，如在 Arena（原 Chatbot Arena）或 AlpacaEval 2 等基准上），同时也提升了指令微调阶段中提到的各项技能。
3. **在 ~10K 个 prompt 上进行可验证奖励的强化学习（RLVR）**：这是一个小规模强化学习运行，用于提升数学等核心能力，同时维持整体性能（并且现在被视为现代推理模型如 DeepSeek R1 的前身）。

该配方已成功应用于 Llama 3.1 [@lambert2024t]、OLMo 2 [@olmo20242] 和 SmolLM 模型 [@alrashed2024smoltulu]。

### DeepSeek R1：扩展 RLVR 用于推理

随着推理语言模型（如 OpenAI 的 o1）的兴起，后训练的最佳实践再次演进，重新排序和重新分配了各训练阶段的计算资源。
推理模型后训练配方中最清晰的文档记录来自 DeepSeek R1 [@guo2025deepseek]，这一配方已被阿里巴巴的 Qwen 3 更大模型（即仅 32B 和 225B MoE 模型）[@yang2025qwen3] 和小米的 MiMo 7B [@xia2025mimo] 等模型所效仿。

![DeepSeek-R1 的多阶段流程。源自 *Nature* 上的 DeepSeek R1 论文，[图 2](https://www.nature.com/articles/s41586-025-09422-z/figures/2)，[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) [@guo2025deepseek]。](images/deepseek-r1-pipeline.png){#fig:deepseek-r1-pipeline .center}

@fig:deepseek-r1-pipeline 中展示的 DeepSeek 配方如下：

1. **使用 10 万+ 同策略推理样本进行"冷启动"（"Cold-start"）**：这些数据从一个早期的 RL 检查点 R1-Zero 中采样，并经过大量过滤，以在 DeepSeek-V3-Base 上灌输特定的推理过程。DeepSeek 用"cold-start"一词来描述如何从少量有监督数据中启动 RL 训练。
2. **大规模强化学习训练**：此阶段用模型反复覆盖推理问题，在各种基准上运行 RLVR "直到收敛"。
3. **拒绝采样与 SFT**：接近收敛时，他们对 RL 检查点应用拒绝采样以构建一个约 800K 条样本的 SFT 数据集，然后在过滤后的混合数据上微调模型——大约 3/4 是推理问题、1/4 是一般查询——从而生成一个通用模型。
4. **混合强化学习训练**：对推理问题（可验证奖励）使用一般偏好调优奖励模型，以打磨模型。

如上所述，此配方还有进一步的演变，尤其在步骤 3 和 4 中以在模型面向用户之前做最后的完善。
许多模型从精心设计的指令数据集起步，其中包含从已有模型中提取并经过大量过滤和打磨的 chain-of-thought 序列，仅通过 SFT 即可获得良好行为，然后再进入 RL 阶段 [@seed2025seed]。

### 向 MOPD 和智能体的转变

推理模型实现产品市场匹配（product-market-fit）的关键一环是向编码智能体的演进——这也伴随着经典后训练配方的又一轮变化。
这里有两个关键变化。
首先，一种新的训练方法——多教师同策略蒸馏（MOPD, Multi-Teacher On-Policy Distillation，第 12 章介绍）——成为了一种流行的工具，用于将多种多样的技能融合到一个最终模型中。
第二个变化则更简单：随着后训练计算量（compute）的持续快速扩展，尤其在强化学习阶段。

小米的 MiMo-V2-Flash 是首份记录现代 MOPD 流程的技术报告 [@mimo2025flash]，之后该团队又为此主题撰写了一篇独立的论文 [@ma2026mopd]。该技术报告以简洁的形式总结了这种后训练配方（见 @fig:rlhf-mopd）：通用 SFT 之后是领域专用的教师训练（更多 SFT 和广泛的 RL），然后使用多教师同策略蒸馏（MOPD）将它们融合为一个最终模型。
其他模型也使用这种形式的配方，例如 NVIDIA 的 Nemotron 3 Ultra [@nvidia2026nemotron3ultra]，其整体类似，但在专家（experts）上有两个连续的 MOPD 阶段。
总体而言，这些配方在"深度"（即配方的迭代模型版本）上复杂度较低，但在需要专门化许多关键专家（一种"广度"）上复杂度更高。需要注意的是，前代后训练同样覆盖了广泛的技能范围，但它在训练流程中不那么细分——即大多数任务在同一训练阶段中被训练。

![MOPD 专用后训练示意图：共享 SFT → 领域专用 SFT 和 RL → 多教师同策略蒸馏为一个（最终）学生。](images/rlhf-mopd.png){#fig:rlhf-mopd data-dark-src="images/rlhf-mopd-dark.png"}

以 MOPD 作为最终阶段的各个模型使用的专家数量各不相同：Nemotron 3 Ultra 超过十个 [@nvidia2026nemotron3ultra]、Kimi K3 九个 [@kimiteam2026kimik3]、DeepSeek V4 超过十个 [@deepseekai2026deepseekv4]（小米 MiMo V2 未报告专家数量）。

后训练配方在模型之间仍然差异巨大。
MOPD 是一种流行的新工具，但实验室之间在使用上远非一致。随着后训练逐渐成熟、工具箱中进入更多工具，配方的变异性已经增大。
例如，GLM-5 使用了 MOPD，但在 MOPD 之前详细描述了更复杂的三阶段 RL 流程，如 @fig:rlhf-sequential-rl 所示 [@glm5team2026glm5]。

![GLM-5 的整体训练流程。源自 GLM-5 团队的论文，[图 5](https://arxiv.org/pdf/2602.15763v2#page=4)，[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) [@glm5team2026glm5]。](images/glm5-pipeline.png){#fig:rlhf-sequential-rl}

随着后训练在现代模型性能中变得越来越核心，配方将继续演变，以反映这一过程中难度、任务和野心的新扩展。
