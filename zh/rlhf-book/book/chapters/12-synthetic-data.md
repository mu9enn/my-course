<!--
  Copyright (c) 2025-2026 Nathan Lambert.
  Licensed under CC BY-NC-SA 4.0:
  https://creativecommons.org/licenses/by-nc-sa/4.0/
  Full license: https://github.com/natolambert/rlhf-book/blob/main/LICENSE-CHAPTERS
-->
---
prev-chapter: "Preference Data"
prev-url: "11-preference-data"
page-title: 合成数据与蒸馏
search-title: "第 12 章：合成数据与蒸馏"
meta-description: "合成数据、蒸馏、Constitutional AI 以及贯穿现代后训练的 AI 反馈方法。"
next-chapter: "Tool Use and Function Calling"
next-url: "13-tools"
lectures:
  - video: "https://www.youtube.com/watch?v=6nyJ8y8ghsE&list=PLL1tdVxB1CpVpEtMHxwuR4uI4Lxjw00_y&index=10"
    label: "讲座 7：合成数据与现代后训练方法"
---

# 合成数据与蒸馏

基于人类反馈的强化学习（RLHF）的根基在于，始终让人类对正在构建的模型施加影响。
当第一批模型首次成功使用 RLHF 进行训练时，人类数据是*唯一*可行的提升模型的方式。

人类是创造高质量问答训练的*唯一*手段。
人类是收集可靠且细致的反馈数据以训练奖励模型的*唯一*手段。

然而，随着 AI 模型变得越来越强，这一假设迅速被打破。
合成数据的可能性——它们成本低得多、迭代也快得多——使得 RLHF 的广泛应用成为可能，因为它大幅降低了实验和研究的成本。
这也让 RLHF 在更广泛的"后训练"方法中长期占据核心地位。
本章对合成数据如何替代或扩展 RLHF 流水线的许多环节，给出一个概览。

## 合成数据的角色

合成数据常受到一个批评——**模型崩溃**（model collapse）——即反复用模型自身的生成品进行训练，会使有效训练分布逐步收窄 [@shumailov2024ai]。
随着多样性下降，罕见事实和风格会被欠表示，微小的错误也可能在迭代中被放大，最终导致泛化能力下降。
在实践中，这些失败主要出现在对未过滤、重复、单一模型的输出进行自训练时；加入真实/人类数据、使用多样化的教师模型、去重以及严格的品质过滤器，在很大程度上可以避免崩溃。
对于当今前沿的训练流水线，有证据表明合成数据可以在大规模下使用，且应当使用，而不会导致崩溃叙事中最极端版本所暗示的那种灾难性退化 [@gerstgrasser2024model] [@feng2024beyond]。

当前最领先的模型**需要合成数据**才能达到最佳性能。
现代后训练中的合成数据涵盖了训练的许多环节——语言模型被用来从种子示例生成新的训练提示 [@wang2022self]、修改现有提示、为提示生成补全 [@numina_math_7b]、提供 AI 反馈以生成偏好数据 [@cui2023ultrafeedback]、过滤补全结果 [@li2024superfiltering] 等等。
合成数据是后训练的关键所在。

合成数据之所以能以如此深度产生影响力，与 GPT-4 级模型的涌现密切相关。
在早期的语言模型（如 Llama 2 和 GPT-3.5-Turbo）阶段，这些模型在生成或监督数据流水线方面还不够可靠。
在 1–2 年内，语言模型在生成答案方面已远超人类。
在从 GPT-3.5 到 GPT-4 级模型的过渡中，模型执行"LLM 即裁判"（LLM-as-a-judge）任务的能力也随之出现。
GPT-4 或更好的模型在生成反馈或评分时，对于某段内容的评价远为稳健和一致。

自 2022 年底 ChatGPT 发布以来，我们见证了诸多有影响力的合成数据集。
其中包括：UltraFeedback [@cui2023ultrafeedback]——首个引人注目的合成偏好数据集，开启了 DPO 革命；Stanford Alpaca（2023 年）——最早一批聊天风格的微调数据集之一；Tülu 3 [@lambert2024t] 中专注于特定技能（如数学、代码、指令遵循）的合成数据集；以及 2025 年为训练思维型模型而发布的 OpenThoughts 3 等众多合成推理数据集 [@guha2025openthoughts]。
如今入门工业级后训练时，大多数经典参考文献都涉及 Tülu 3 或 OpenThoughts 3 这类数据集，而快速入门指南通常以 Alpaca 等规模更小、更简单的数据集开始，因为训练速度快得多。

数据集规模的巨大变化也与微调数据集中提示词数量的增长有关：Alpaca 包含 5.2 万个样本，OpenThoughts 和 Tülu 3 则各有超过 100 万个样本，同时响应长度也在增长。
由于响应更长、提示更多，Alpaca 数据集的训练 token 量大约在 1000 万量级，而 Tülu 3 的规模是其 50 倍，约 5 亿；OpenThoughts 3 更大，达到约 100 亿 token。

在此过程中，合成数据并未在流水线的所有环节均匀替代人类数据。
对于**指令数据（SFT）**，合成生成已基本胜出——从更强的模型蒸馏出来的补全现在大多数的情况下，质量超过了人类编写者在大规模下的产出（在最前沿推理问题上有少量例外）。
对于 **RLHF 中的偏好数据**，情况更为复杂：学术研究表明合成偏好数据表现相当，但前沿实验室仍将人类偏好数据视为竞争壁垒。
对于**评估**，格局又有不同：LLM 即裁判以成本有效的方式扩展了*评分*规模，但底层的基准测试和事实标签仍需人类创建。
总体模式是：在模型超越人类可靠性的环节，合成数据占据主导；而在能力前沿、确立事实真相以及引导训练方面，人类仍然不可或缺。

## 使用合成数据进行蒸馏

蒸馏（distillation）一词是在关于合成数据在语言模型中角色的讨论中最有影响力的概念。
蒸馏作为术语来源于深度学习文献中教师-学生的知识蒸馏（Knowledge Distillation, KD）的技术定义 [@hinton2015distilling]。

![传统知识蒸馏训练一个较小的学生模型，使用 KL 散度损失使其软概率分布逼近较大的教师模型。两个模型同时处理相同的输入，温度缩放（$\tau > 1$）使分布更柔和，从而揭示更多类间关系信息。](images/knowledge_distillation_tikz.png){#fig:knowledge-distillation data-dark-src="images/knowledge_distillation_tikz-dark.png"}

通俗地说，蒸馏是指使用更强模型的输出训练较弱模型。

![LLM 后训练中的合成数据生成：提示被输入到强模型中以生成补全，然后将这些补全配对形成训练数据集。该数据集随后用于通过标准监督学习微调较小的模型。更复杂的流水线可能涉及多个模型编辑补全、生成偏好对或过滤品质。](images/synthetic_data_distillation_tikz.png){#fig:synthetic-data-generation data-dark-src="images/synthetic_data_distillation_tikz-dark.png"}

在后训练中，这种蒸馏的广义概念通常表现为两种形式：

1. 作为贯穿后训练多个环节的数据引擎：为指令生成补全、生成偏好数据（或 Constitutional AI 数据）、为 RL 提供验证信号等。
2. 从更强模型向较弱模型传递特定技能——这常常针对数学推理或编码等具体技能。

第一种策略随着语言模型在撰写各类任务答案方面变得比人类更可靠而日益流行。
GPT-4 级模型将蒸馏的范围扩展到使用更强模型进行数学和代码等复杂任务的蒸馏（如上所述）。
在这种思路下，蒸馏促使我们拥有一个模型体系，其中实验室通常会训练一个大型内部模型（如 Claude Opus 或 Gemini Ultra），这些模型不会公开发布，而仅用于内部蒸馏以制作更强的模型。
对于开源模型，常见的做法是从闭源 API 模型蒸馏训练数据，到更小、权重公开的模型中 [@tunstall2023zephyr]。
在此过程中，策展高质量的提示并从教师模型输出中过滤回复，对于最大化性能至关重要。

将特定技能传递到较小语言模型同样使用蒸馏的原则——尽可能获取最好的训练数据。
在此方向上，已有许多论文研究了使用来自更强模型的有限数据集来改进对齐 [@zhou2023lima]、数学推理 [@shridhar2023distilling] [@hsieh2023distilling] 以及测试时扩展（test-time scaling）[@muennighoff2025s1]。

本章其余部分介绍的所有合成数据方法，都是在训练中直接使用语言模型输出来制作数据配方的各种方式。

## 走向同策略教师-学生蒸馏

虽然蒸馏已经成为后训练语言模型的一种标准方法，但后训练配方朝着推理和智能体模型的转变，伴随着人们对教师-学生知识蒸馏这一特定子领域的兴趣复兴。
采用新型知识蒸馏训练的领先模型包括：阿里巴巴的 Qwen3 [@yang2025qwen3]、小米的 MiMo-V2-Flash [@mimo2025flash]、智谱的 GLM-5 [@glm5team2026glm5] 以及 DeepSeek-V4-Pro [@deepseekai2026deepseekv4]。

蒸馏被归入本章，是因为在实践中的许多现代后训练合成数据用法都是蒸馏启发的流水线——一个更强的模型生成标签、补全、logits、批评或其他监督信号，学生模型在这些信号上进行训练。
同时，蒸馏方面的技术文献正在发展出属于自己的后训练方法集，尤其是同策略和自蒸馏配方越来越普遍。
目前，我们将它作为合成数据工具包的一部分来介绍，但本书未来版本可能会专门为蒸馏（与指令微调、强化学习等并列）开辟独立章节。

### 为语言模型适配知识蒸馏

原始文献将知识蒸馏专门引入，作为从已经训练好的、更强且/或更大的*教师*网络中训练*学生*模型的一种方式 [@hinton2015distilling]。
KD 是一种使用*软*训练标签的技术，与交叉熵损失等标准目标中使用的独热标签形成对比。
基于软标签的目标考察的是所有可能的下一个 token 或预测上的分布，而不是仅仅判断单个预测 token 是否正确，并训练学生分布以匹配教师分布。

KD 通常可以应用于任何深度学习问题，例如预测输入的单个类别。
为了将其专门适配于语言模型的自回归风格，损失函数可以分解为每个 token 的分布匹配损失。
2016 年，Kim & Rush 将 KD 应用到让一个学生模型从教师模型生成的*序列*中学习 [@kim-rush-2016-sequence]。

设 $s$ 为源句或提示，$u = (u_1,\ldots,u_J)$ 为教师模型的完整输出序列，$\mathcal{V}$ 为输出词汇表（tokenizer 中可能的 token），$q$ 为教师模型对下一个 token 的分布，$p$ 为学生模型的分布。
此处我们使用 $u$ 作为完整教师输出序列的通用符号，在后续同策略/RL 记号中保留 $a$ 给学生采样的补全/动作序列。
需要注意的是，他们的论文将此称为词级蒸馏（word-level distillation），但对现代语言模型而言，这应理解为在 tokenizer 词汇表上的每个 token 分布匹配，因为这篇论文早于现代子词 tokenizer 的出现：

$$
\mathcal{L}_{\mathrm{WORD-KD}}
= -\sum_{j=1}^{J}\sum_{k=1}^{|\mathcal{V}|}
q(u_j = k \mid s, u_{<j})\log p(u_j = k \mid s, u_{<j}).
$$ {#eq:word_kd}

WORD-KD 是将经典的 Hinton 式教师-学生知识蒸馏应用于语言模型。这通常会在训练语料中已有的固定文本上进行。

它具有标准交叉熵的形式 $-\sum_z q(z)\log p(z)$。
在每个位置 $j$，教师分布 $q$ 为每个可能的下一个 token $k \in \mathcal{V}$ 赋予概率，当学生分布 $p$ 在教师认为概率较高的 token 上分配低概率时，学生就会受到惩罚。

序列级蒸馏则将 $\mathcal{U}$ 视为可能输出序列的空间，并在完整序列上将学生与教师分布进行匹配。
由于对所有完整序列 $u \in \mathcal{U}$ 求和是不可行的（需要对指数数量的可能序列求和），Kim & Rush 用单一高概率教师输出 $\hat{u}$ 上的点质量来近似教师序列分布。
此处 $\hat{u}$ 是使用教师模型通过束搜索（beam search）产生的序列，即 $\hat{u} = \mathrm{BeamSearch}_q(s) \approx \arg\max_{u \in \mathcal{U}} q(u \mid s)$：

$$
\begin{aligned}
\mathcal{L}_{\mathrm{SEQ-KD}}(s)
= -\sum_{u \in \mathcal{U}} q(u \mid s)\log p(u \mid s)
\approx -\log p(\hat{u} \mid s) \\
= -\sum_{j=1}^{|\hat{u}|}\log p(\hat{u}_j \mid s, \hat{u}_{<j}).
\end{aligned}
$$ {#eq:sequence_kd}

SEQ-KD 迈向了现代方法的一步：教师模型生成 token 作为学生的信号。这是解锁我们将要看到的前瞻性同策略蒸馏的核心步骤，也是使所有可能序列的计算可行所必需的。
在我们过渡到现代模型的流行 KD 变体时，我们将这种风格的训练称为*离线* KD——因为用于训练学生模型的生成是事先产生的。

在继续之前，有两个关联点值得注意。

首先，有一系列流行模型使用离线 KD 进行训练，如分类器 DistilBERT [@sanh2019distilbert] 和 TinyBERT [@jiao2020tinybert]，它们将语言模型的其他改进与离线蒸馏相结合（显然，这些编码器模型没有进行*序列*蒸馏，因为它们是编码器模型而非自回归多 token 预测模型）。

其次，我们可以将本章 15 章中详尽讨论的 KL 散度联系起来，因为此处使用的交叉熵目标与 KL 散度密切相关。
对于教师分布 $q$ 和学生分布 $p$，交叉熵定义为

$$
H(q,p) = -\sum_z q(z)\log p(z).
$$ {#eq:kd_cross_entropy}

它与 @eq:word_kd 的形式相同，也与 @eq:sequence_kd 的第一项相同。
交叉熵还可以分解为教师分布的熵和一个 KL 散度：

$$
\begin{aligned}
H(q,p)
&= H(q) + D_{\mathrm{KL}}(q\|p) \\
&= -\sum_z q(z)\log q(z)
+ \sum_z q(z)\log\frac{q(z)}{p(z)}.
\end{aligned}
$$ {#eq:kd_forward_kl}

第一项 $H(q)$ 仅依赖于教师。
因此，当教师固定且作为训练数据源时，最小化交叉熵等价于最小化从教师到学生的正向 KL 散度 $D_{\mathrm{KL}}(q\|p)$。
这正是离线 KD 和类 SFT 训练所使用的 KL 方向。

### 从离线到同策略蒸馏

这些*离线* KD 算法有几个局限性，催生了同策略变体。
离线学习的性质意味着学生模型可能面临教师模型与学生推理时生成序列之间的分布不匹配问题。
例如，正向 KL 目标可能导致学生模型过高估计教师分布的低概率区域。
这些问题共同构成了*同策略*蒸馏（On-Policy Distillation, OPD）的切入点。

这种训练-测试差距被称为**暴露偏差**（exposure bias）[@arora-etal-2022-exposure] [@song2026surveyonpolicydistillationlarge]。
离线 KD 采样教师轨迹 $u \sim \pi_T(\cdot \mid s)$，并在结果前缀上最小化每个 token 的 KL，

$$
\mathcal{L}_{\mathrm{KD}}(\theta)
= \mathbb{E}_{s \sim \mathcal{D},\, u \sim \pi_T(\cdot \mid s)}
\sum_t D_{\mathrm{KL}}\!\left(
\pi_T(\cdot \mid s, u_{<t})
\;\|\;
\pi_\theta(\cdot \mid s, u_{<t})
\right).
$$ {#eq:exposure_train}

而在推理时，学生按照自身的策略展开，因此实际需要考虑的是沿*自身*轨迹的期望任务损失，

$$
\mathcal{L}_{\mathrm{eval}}(\theta)
= \mathbb{E}_{s \sim \mathcal{D}_{\mathrm{test}},\, a \sim \pi_\theta(\cdot \mid s)}
\ell_{\mathrm{task}}(s, a)
$$ {#eq:exposure_test}

此处，$\ell_{\mathrm{task}}(s, a)$ 表示完成后的学生响应的任何下游任务损失，如答案错误、测试用例失败或裁判/评分标准损失。
暴露偏差是 $\pi_T(\cdot \mid s) \neq \pi_\theta(\cdot \mid s)$ 的直接后果：训练中访问的前缀 $(s, u_{<t})$ 和测试时访问的前缀 $(s, a_{<t})$ 来自不同的状态访问分布，因此学生在与其实际操作的状态不同的状态下受到监督。

同策略蒸馏的核心转变是：我们可以通过从学生模型采样并测量其与教师分布的距离来调整优化，而不是从教师模型采样。
MiniLLM 注意到需要转向反向 KL 优化（我们在第 15 章直观地解释了为什么这个目标可能更好），并提出了在在线策略梯度 RL 框架内使用 KD 损失函数 [@gu2024minillm]。
其他同期工作 [@agarwal2024policy] 展示了同策略 KD 的前景，并将从学生生成和由教师评分的迭代过程与 RL 文献中的模仿学习工作联系起来。
为了建立这一关联，一种模仿学习算法 DAgger 迭代地训练一个用其学习策略在世界中行动的代理，并由 oracle 策略提供应执行动作的反馈，然后用于更新其策略 [@ross2011reduction]。

这一差距的成本可以通过 DAgger 背后的监督模仿学习界限来量化。
在原始的离散动作设定中，假设学习策略在教师诱导的训练分布上的期望每步动作误差为 $\epsilon$，其中 $\mathbb{I}[\cdot]$ 是指示函数，当条件为真时返回 1，否则返回 0，

$$
\mathbb{E}_{s_t \sim d_{\pi_T}}\!\left[
\mathbb{I}\!\left(\pi_\theta(s_t) \neq \pi_T(s_t)\right)
\right] \leq \epsilon.
$$ {#eq:dagger_perstep}

监督模仿学习分析 [@ross2011reduction] 表明，沿学生采样的长度为 $L$ 的轨迹积累的期望损失在 $L$ 上可以以二次方缩放 [@song2026surveyonpolicydistillationlarge]：

$$
\mathbb{E}_{a \sim \pi_\theta(\cdot \mid s)}\!\left[\sum_{t=1}^{L} \ell\!\left(s, a_{<t}\right)\right] \leq O(\epsilon L^2).
$$ {#eq:dagger_trajectory}

对于语言模型而言，这一离散动作界限应被理解为一种类比，而非理论保证。
在实践中，语言模型会在长视界上预测完整的下一个 token 分布，因此 @eq:dagger_perstep 中的 0-1 动作不一致假设不能直接适用。
提示或前缀自然映射到状态，采样 token 映射到动作，但 token 级蒸馏通常使用 KL 或交叉熵等分布损失来衡量，因此经典 DAgger 的数学并不能完全转移过来。

这种 $O(\epsilon L^2)$ 的误差累积在现代语言模型中尤为明显——这些模型通常生成跨越数千 token 的序列。
一个次优 token 会使前缀稍微偏离分布，而模型由于从未见过这种扰动前缀，更可能再次出错，导致退化或产生幻觉文本。
同策略蒸馏通过*迭代地*从当前学生采样补全并让学生在被访问的状态下接受教师监督来解决这个问题。
学生直面自己的错误，在特定的离分布状态处接收教师反馈，并学习恢复行为。
在 DAgger 的交互式模仿学习分析下，这一迭代程序可以将误差累积从 $O(\epsilon L^2)$ 降低到 $O(\epsilon L)$ [@ross2011reduction]。
对于语言模型，这解释了同策略蒸馏背后的动机：确切界限可能不会逐条转移到每个 token 级蒸馏设置，但同策略方法在实践中获得的成功支持了这一基本直觉。

译者注：此处关于 DAgger 界限到语言模型的类比需要谨慎理解。原论文中的动作空间是离散的，而语言模型的 token 空间不仅巨大而且是嵌套结构（token 级错误会导致后续整个前缀偏离），因此 $O(\epsilon L^2)$ 这一理论界限在语言模型中更多是定性类比而非严格定理。但经验上，暴露偏差导致的误差累积确实是同策略方法的强动机。

对于同策略蒸馏，设 $s$ 为提示，$a = (a_1,\ldots,a_L)$ 为从当前学生策略 $\pi_\theta(\cdot \mid s)$ 采样的补全，$s_t = (s, a_{<t})$ 为步骤 $t$ 的 token 级状态。
教师策略 $\pi_T$ 是固定的，因此目标衡量的是学生策略在自身诱导的状态下与教师策略下一个 token 分布的距离。
由于期望从 $\pi_\theta$ 采样，且学生分布在 $D_{\mathrm{KL}}(\pi_\theta \| \pi_T)$ 的左侧，这是一个反向 KL 目标：

$$
\mathcal{L}_{\mathrm{OPD}}(\theta)
= \mathbb{E}_{s, a \sim \pi_\theta(\cdot \mid s)}
\sum_t D_{\mathrm{KL}}\left(\pi_\theta(\cdot \mid s_t) \;\|\; \pi_T(\cdot \mid s_t)\right).
$$ {#eq:opd_reverse_kl}

此处我们转向期望记号——正如第 6 章中广泛使用的符号，该章涵盖了基础的 RL 策略梯度算法——因为此优化通过采样轨迹并数值估计梯度来求解。
转向这种采样框架自然地过渡到现代 LLM 的 RL 训练基础设施，这种基础设施被设计为在当前训练策略生成 token 和进行参数更新之间快速交替。

事实上，最近的 OPD 实现将 KD 与 RL 的整合推进了一步：直接将 KD 距离作为 RL 优化中的奖励信号使用。
一个典型做法是在 RL 算法中，将反向 KL 距离的负 per-token 贡献替代为优势信号 [@lu2025onpolicy]。
对于状态 $s_t$ 处采样的 token $a_t$，token 级的 log-prob 差距可以写成类似优势的信号：

$$
A_t^{\mathrm{OPD}}
= \log \pi_T(a_t \mid s_t) - \log \pi_\theta(a_t \mid s_t).
$$ {#eq:opd_kl_advantage}

使用负的 per-token KL 贡献将最小化转为最大化信号：教师评分高于学生的 token 获得正向优势，教师评分低于学生的 token 获得负向优势。
教师 log-prob 差距提供了一种密集的 token 级反馈，可能比稀疏的可验证奖励或奖励模型输出提供更有效的学习信号。

### 现代 OPD 变体

此设置还可以进一步扩展：使用多个教师模型来训练一个最终模型，或在生成中插入额外信息以帮助模型识别错误。
首先，我们将介绍如何将多个教师整合到单次训练中。
这些教师可以是特定领域的专家模型（如数学或代码领域），或前一次训练的中间检查点。
对于每个教师，可以在训练批次中为每个提示或任务类型选择贡献权重，从而构建多教师同策略蒸馏（Multi-Teacher On-Policy Distillation, MOPD）[@mimo2025flash]。
对于多个教师，设 $\pi_{T_k}$ 为教师 $k$，$w_k(s)$ 为提示相关的混合权重（满足 $\sum_k w_k(s) = 1$），反向 KL 损失如下：

$$
\mathcal{L}_{\mathrm{MOPD}}(\theta)
= \mathbb{E}_{s, a \sim \pi_\theta(\cdot \mid s)}
\sum_t \sum_k w_k(s) D_{\mathrm{KL}}\left(\pi_\theta(\cdot \mid s_t) \;\|\; \pi_{T_k}(\cdot \mid s_t)\right).
$$ {#eq:mopd_objective}

在大规模后训练中，这可以让不断扩大规模的组织在不同的配方上进一步扩展。
多个团队可以致力于高质量专家模型的训练，这些模型可以作为最终学生模型后续的教师模型——如 [@deepseekai2026deepseekv4] 和 [@mimo2025flash] 的做法。

OPD 有许多与其他章节研究内容的结合方式，例如将反向 KL 作为优势，与其他形式优势计算（如 GRPO 的组级归一化）一起使用，从而实现更复杂的奖励塑造。
KD 方法在后训练方法中比较特殊，因为它们通常要求学生和教师共享一个 tokenizer，因为监督信号可以是来自另一个 LLM 的 per-token 反馈。

扩展方法中，如同策略自蒸馏（On-Policy Self-Distillation, OPSD），是让语言模型用自身或外部工具验证一个补全结果，充当拥有特权信息的教师，从而无需一个明确更强的教师即可提升自身性能 [@zhao2026selfdistilled]（OPSD 的训练流程见 @fig:sdpo）。
例如，Cursor 以针对性的文本反馈形式在 RL 轨迹上使用自蒸馏来训练其 Composer 2.5 代码模型 [@cursor2026composer25]，该模型从 Kimi K2.5 微调而来。
以下是简化后的直觉理解——在实际部署中，以下设置与其他损失函数（如代码正确性损失）结合使用。
在此设置中，Cursor 让模型以评估提示（包含常见 bug 列表）审查 RL 轨迹。
遇到 bug 时，评判模型会在 RL 过程中修改生成的序列——插入一个提示供模型未来学习——然后继续蒸馏损失计算。
这形成了一个循环：首先用标准语言模型生成在 RL 中产生一个补全，然后运行评判模型并可选地插入 hint token，最后为新的补全生成 logprobs 以部署知识蒸馏损失。
token 空间中的提示足以帮助模型纠正自身输出，即使在性能的最前沿也是如此（目前仍有大量工作致力于如何最好地构建和使用这些提示，通常称为*特权信息* [@penaloza2026privileged]）。

这使得同策略蒸馏成为一项核心后训练方法，用于将多种技能组合到一个通用模型中，或在特定部署中推至能力前沿。

![三种蒸馏范式的对比，依据 rollout 的来源和监督信号的流向。**序列 KD**（左）：教师离线生成输出，学生使用交叉熵（CE）损失进行匹配训练。**同策略蒸馏（OPD）**（中）：学生在同策略下（如在 RL 框架内）生成 rollout，独立教师对每个访问的 token 进行评分，学生使用 per-token KL 散度（KL）进行训练。**同策略自蒸馏（OPSD）**（右）：一个模型同时承担两种角色——向上下文中添加特权信息（hint）形成教师轨迹，无 hint 的生成则通过 KL 损失向该轨迹蒸馏，无需独立的教师模型。](images/distillation_directionality_tikz.png){#fig:distillation-directionality data-dark-src="images/distillation_directionality_tikz-dark.png"}

![在字符串反转任务上的同策略自蒸馏（OPSD）。一个策略 $\pi_\theta$ 对同一学生采样补全 $y$ 执行两次前向传播：一个**教师** pass 在问题加上正确示例演示的条件下进行（黄色），一个**学生** pass 仅在有问题的条件下进行（绿色）。两个 pass 之间的 per-token 反向 KL（教师端带有 stop-gradient）将仅条件问题的策略拉向带演示的策略；高亮列是采样错误导致两个分布差异最大的 token。](images/sdpo_tikz.png){#fig:sdpo data-dark-src="images/sdpo_tikz-dark.png"}

### 建议实验

`code/distillation/` 中的配套代码实现了 SDPO [@hubotter2026reinforcement]——即在 @fig:sdpo 中展示的同策略自蒸馏设置（同期 OPSD 论文 [@zhao2026selfdistilled] 与之密切相关）：一个策略同时充当带演示的教师和仅问题的学生，使用 per-token 反向 KL 进行训练。
该实验在一个小型字符串反转任务上运行，这使得同策略蒸馏的循环足够便宜，可以在单个 GPU 上端到端观察。

1. **运行 SDPO 字符串反转示例。**

   ```bash
   cd code/
   uv run python -m distillation.train --config distillation/configs/sdpo.yaml
   ```

   观察 `reward`、`loss` 和 `skipped`，以及循环中打印的教师/学生 rollout 样例。
   `skipped` 计数是被取样的提示中，采样组不包含任何正确 rollout 的数量；随着学生进步，被跳过的提示会减少，`reward` 逐渐接近 1。

2. **调节同策略超参数。**
   复制 `distillation/configs/sdpo.yaml`，在固定任务的情况下依次调整 `num_rollouts`、`kl_top_k` 和 `prompts_per_step`。
   每个提示更多的 rollout 会让更容易找到正确示例演示（降低 `skipped`），代价是每个步骤需要更多生成；`kl_top_k` 则在反向 KL 匹配的教师分布范围和计算开销之间权衡。

## AI 反馈

在 RLHF 爆发式增长之后不久，来自 AI 反馈的强化学习（RL from AI Feedback, RLAIF）作为一种替代方法出现，其中 AI 可以近似流水线中人类数据的部分，加速实验和进展。
广义上说，AI 反馈是一系列使用 AI 增强或生成数据的技术，用来解释特定输入的质量（这些数据可用于不同训练方式或评估），其起点是成对偏好数据 [@lee2023rlaif] [@sharma2024critical] [@castricato2024suppressing]。
使用 RLAIF 完全替代人类反馈或对其增强的动机有很多。
在 RLHF 流程中，AI 反馈最广为人知的作用是在偏好数据收集和相关的奖励模型训练阶段（其中 Constitutional AI 是其特定类型的实现）。
在本章中，我们关注广义的 AI 反馈以及它在 RLHF 训练流水线中的这一特定用法，本书后面还会介绍理解和使用合成数据的更多方式。

随着 AI 反馈日趋成熟，其应用范围超出了简单替代人类偏好标签。
使偏好数据收集更便宜的同一套 LLM 即裁判基础设施，也实现了可扩展的评估（参见第 16 章），而最近，基于评分标准（rubric）的奖励将 RL 训练扩展到了无法验证答案的领域——这一点将在本章后半部分深入探索。

### 平衡 AI 和人类反馈数据

AI 模型生成特定数量反馈的成本远低于人类：截至 2026 年，一条人类偏好数据的成本约为 1 美元或更高（有些甚至超过每条提示 10 美元），而使用前沿 AI 模型（如 GPT-4o）的 AI 反馈成本不到 0.01 美元。
此外，人类劳动的成本大致不变，而这些任务中领先模型的性能持续提升，每单位性能的价格则不断下降。
这种成本差异将 RLHF 方法的实验市场向整个此前因价格被挡在门外的群体开放了。

除了价格，AI 反馈在性能上引入了与人类反馈不同的*权衡*，这些仍在更广泛的文献中被研究。
在评估我们训练的语言模型方面，AI 反馈在评估角色中占主导地位，因为它的低价使其可以在各种大规模任务中使用，而人类数据在这里的成本（或时间延迟）是不切实际的。
所有这些话题都深度交织在一起——AI 反馈数据永远不会完全替代人类数据，即使在评估中也是如此；而评估中的 AI 反馈量将远超训练中的量，因为评估模型的人远多于训练模型的人。

AI 反馈数据在哪些具体领域和应用——如聊天、安全、推理、数学等——比人类数据更出色，目前尚未完全确定。
一些 RLAIF 早期工作表明 AI 反馈可以完全替代人类数据，称其为有效的替代品 [@lee2023rlaif]，尤其是在仅评估聊天任务时 [@cui2023ultrafeedback] [@yuan2025selfrewardinglanguagemodels]。
ChatGPT 之后研究 RLHF 的早期文献，其评估套件较为狭窄，主要关注充当各领域有用助手的模型的"对齐"（详见第 17 章）。
后来的工作给出了更精细的图景：在更广泛的评估集（如包含部分推理任务）上，最优均衡需要将有挑战性的数据点路由给人来进行准确标注，而大部分数据则交由 AI 反馈处理 [@miranda2024hybrid] [@xu2025rlthf]。
虽然尚无研究专门关注更广泛领域中 RLHF 的人类与 AI 反馈数据之间的平衡，但已有许多技术报告显示 RLHF 通常能改进这一广泛的评估集，其中一些使用 DPO，如 Ai2 的 Tülu 3 [@lambert2024t] 和 Olmo 3 [@teamolmo2025olmo3]，以及 Hugging Face 的 SmolLM 3 [@bakouch2025smollm3]；另一些使用在线 RLHF 流水线，如 NVIDIA 的工作，使用了来自 Scale AI 的人类偏好数据和基于 LLM 的反馈的混合（通过 HelpSteer 系列工作 [@wang2024helpsteer] [@wang2024helpsteer2] [@wang2024helpsteer2p] [@wang2025helpsteer3]）：Nemotron Nano 3 [@nvidia2025nemotron3nano]、Nemotron-Cascade [@wang2025nemotron] 或 Llama-Nemotron 推理模型 [@bercovich2025llamanemotron]。

总体而言，虽然 AI 反馈及相关方法对该领域显然极其有用，但人类数据并没有被这些更便宜的替代方案完全取代。
目前存在多种假设，但人类数据是否能在真实产品设置中提供模型更精细的控制，或者对角色训练（一种新兴技术集，允许你精确控制模型的个性，详见第 17 章）等新训练方法是否有益，尚无研究。
对于入门者来说，AI 反馈应当是首选尝试方案，但对扩展到更大规模运营的流水线而言，最终过渡到包含人类反馈是可能的。

RLAIF 这一术语由 Anthropic 的论文《Constitutional AI：来自 AI 反馈的安全性》[@bai2022constitutional] 引入，最初导致 AI 社区对论文标题中的两种方法（Constitutional AI 和 AI 反馈）之间的关系产生了一些混淆。
自 Constitutional AI（CAI）论文发布和 RLAIF 的正式化以来，RLAIF 已成为后训练和 RLHF 文献中的默认方法——其示例多得难以一一列举。
这种关系应该被理解为：CAI 是开启更广泛 RLAIF 领域的先行示例。

区分人类数据和 AI 反馈数据的一条经验法则如下：

1. 人类数据是高噪声、低偏置。这意味着数据的收集和过滤会更困难，但一旦处理完毕，它能提供非常可靠的信号。
2. 合成偏好数据是低噪声、高偏置。这意味着 AI 反馈数据更容易起步，但可能因在数据中系统性存在的、难以预见的二阶效应而对模型产生意想不到的影响。

本书强调了众多学术成果，展示了如何用 AI 偏好数据替代 RLHF 工作流中的方法并获得强劲的评估分数 [@miranda2024hybrid]，但更广泛的行业趋势表明，RLHF 文献与更不透明的最佳实践之间存在差异。
在行业中，人类数据通常被视为重要的竞争壁垒和技术优势。

### 构建专门的评判 LLM

随着 RLAIF 方法越来越普遍，许多人开始思考：我们是否应该使用相同的模型来生成响应和生成评判/评分？
具体来说，所使用的 LLM 即裁判的校准性一直受到质疑。
多项研究已表明 LLM 是不一致的评判者 [@wang2023large]，且更偏好自身响应（称为自我偏好偏差）[@panickssery2024llm]。

因此，许多人问：一个解决方案是不是训练一个专门的模型仅用于这个标注任务？
已有多个模型旨在代替前沿模型充当数据标注工具，例如批评模型 Shepherd [@wang2023shepherd] 和 CritiqueLLM [@ke2023critiquellm]，以及用于评估回复表现的 Auto-J [@li2023generative]、Prometheus [@kim2023prometheus]、Prometheus 2 [@kim2024prometheus] 和 Prometheus-Vision [@lee2024prometheus]；不过，它们在公开记录的训练配方中尚未被广泛采用。
有人认为，通过对推理进行重复采样 [@brown2024large] [@zhao2025sample] [@kalra2025verdict]、自我修正 [@madaan2023self] 或锦标赛排名 [@pace2024west]，可以得到对真实评判更好的估计或更高质量的偏好对。
其他校准技术让模型的生成和评判能力协同进化 [@wu2024meta]。
学界普遍接受：尽管偏差确实存在，但领先语言模型已经为此任务进行了大量训练——因为它既需要 AI 实验室的内部操作，也被客户广泛使用——因此除非你的任务涉及大量未在公开互联网上暴露的私密信息，否则通常不需要训练你自己的评判模型。

## Constitutional AI

Anthropic 在 Claude 模型中使用的 Constitutional AI（CAI）方法，是 RLHF 训练中最早记录的、大规模使用合成数据的方法。
Constitutional AI 通过两种方式生成合成数据：

1. 对指令微调数据生成评判，以遵循一组原则，如"回答是否在鼓励暴力？"或"回答是否真实？"当模型回答问题时，它会对照宪法的原則列表检查结果，并逐步优化回答。然后，模型在此数据集上进行微调。
2. 通过语言模型回答哪个补全更好（给定宪法中的随机原则作为上下文），生成成对偏好数据（与原则引导的奖励模型研究 [@sun2024salmon] 类似）。然后，如同常理，使用合成数据进行 RLHF，这也是 RLAIF 名称的由来。

大体上，CAI 以上述第 2 部分——偏好数据——为人所知，但用于指令数据的方法被广泛用于后训练中的通用数据过滤和合成数据生成方法。

CAI 可以形式化如下。

通过采用一套人类编写原则（他们称为*宪法*），Bai et al. 2022 使用一个独立 LLM 生成用于微调的偏好和指令合成数据 [@bai2022constitutional]。
一部宪法 $\mathcal{C}$ 是一组书面原则，指示在评判阶段应关注的特定方面。
指令数据的策展是通过反复采样一个原则 $c_i \in \mathcal{C}$，并要求模型修改其对提示 $x$ 的最新输出 $y^i$，使其与 $c_i$ 对齐来实现的。
这产生了一系列指令变体 $\{y^0, y^1, \cdots, y^n\}$，使用了来自原则 $\{c_{0}, c_{1}, \cdots, c_{n-1}\}$ 的评判。
最终的数据点是提示 $x$ 加上最终补全 $y^n$，其中 $n$ 为某个值。

偏好数据则以相似但更简单的方式构建：使用 $\mathcal{C}$ 中的一部分原则作为反馈模型的上下文。
反馈模型接受一个提示 $x$、一组原则 $\{c_0, \cdots, c_n\}$，以及两个来自先前 RLHF 数据集的补全 $y_0$ 和 $y_1$（标注为回答 A 和 B）。
新的数据点由一个语言模型生成，它会选择质量更高且更符合所述原则的输出（A 或 B）。
在早期模型中，可以通过提示 `The answer is: `，然后查看哪个 token（A 或 B）具有更高概率来实现，但现在更常见的方式是由一个会解释推理过程然后再选择答案的模型来完成——通常被称为一种生成式奖励模型（generative reward model）[@mahan2024generative]。

### CAI 延伸阅读

Constitutional AI 有许多相关研究方向和扩展，但其中很少有被明确记录为 RLHF 和后训练配方中的清晰改进。

- OpenAI 发布了一份 Model Spec [@openai2024modelspec]，声明了对其模型的预期行为，并表示他们正在探索模型直接引用该文件的方式进行对齐的方法（这可以看作 CAI 的近亲）。OpenAI 持续更新其 spec，并使用一种称为" deliberative Alignment "的方法训练其推理模型（如 o1）[@guan2024deliberative]，在引用这些安全或行为政策时对齐模型。
- Anthropic 继续在模型训练中使用 CAI，更新了 Claude 使用的宪法 [@Anthropic2023ClaudesConstitution]，并探索群体如何在原则方面收敛、以及当外部群体自行创建原则然后分享给 Anthropic 以训练模型时模型行为如何变化 [@ganguli2023]。
- 开源社区探索了对开放数据集应用 CAI 的复现 [@Huang2024cai] 以及探索 LLM 之间创建对话数据 [@lambert2024self]。
- 其他工作使用原则驱动的偏好或反馈配合不同的优化方法。
  Sun et al. 2023 [@sun2023principledriven] 将原则作为奖励模型的上下文，这些模型被用于训练 Dromedary 模型 [@sun2024salmon]。
  Glaese et al. 2022 [@glaese2022improving] 使用原则改进 RLHF 过程中人类评判的准确性。
  Liu et al. 2025 [@liu2025inference] 训练一个奖励模型在推理时生成自己的原则，并使用这些原则给出最终评分。
  Franken et al. 2024 [@franken2024self] 将原则遵循表述为一个互信息最大化问题，预训练模型可以在无标签的情况下学习。

## 评分标准：面向提示的特定 AI 反馈

AI 反馈在训练中的角色在 2024 年末到 2025 年间增长，当时业界在寻求扩展具有可验证奖励的强化学习的途径（参见第 7 章）。
评分标准（rubric）的概念应运而生，作为获取那些没有明确可验证答案的提示的近可验证标准的一种方式。
这将允许一个模型尝试为一个问题生成多个答案，并使用 RL 朝最佳答案进行更新。
这个想法与本章讨论的其他方法密切相关，很可能随着业界 LLM 评判者和合成数据实践的改进而自然涌现。
如今，使用评分标准作为奖励的 RL 已经在科学推理、事实性等多项技能中确立了有意义的改进 [@gunjal2025rubrics; @viswanathan2025checklists; @rezaei2025onlinerubrics; @liu2025openrubrics]。

以下展示了一个评分标准示例及其对应的提示 [@liu2025openrubrics]：
```text
**Prompt**: As a museum curator, can you suggest five obscure artifacts that would be perfect for a "Mysteries of the Ancient World" exhibit? Each artifact should come from a different culture and time period, with a brief description of their historical significance and mysterious origins. These artifacts should leave visitors wondering about the secrets and lost knowledge of our past. Thank you for your expertise in bringing this exhibit to life.

** Rubric**: 
1. The response includes exactly five distinct artifacts as requested. [Hard Rule] 
2. The response ensures each artifact originates from a different culture and time period. [Hard Rule] 
3. The response provides a brief description of each artifact's historical significance. [Hard Rule] 
4. The response provides a brief description of each artifact's mysterious origins or unexplained aspects. [Hard Rule] 
5. The response conveys a sense of intrigue and mystery that aligns with the theme of the exhibit. [Hard Rule] 
6. The response clearly and accurately communicates information in a well-organized and coherent manner. [Principle] 
7. The response demonstrates precision and clarity by avoiding unnecessary or irrelevant details. [Principle] 
8. The response uses informative and engaging language that stimulates curiosity and critical thinking. [Principle] 
9. The response shows thoughtful selection by ensuring each example contributes uniquely to the overall theme without redundancy. [Principle] 
10. The response maintains consistency in style and format to enhance readability and comprehension. [Principle]
```

`[Hard Rule]`（硬规则）和 `[Principle]`（原则）是用于表示某条反馈优先级的特定标记。也可以使用其他表示重要性的方式，如简单的优先级数字。

评分标准的生成通常在训练数据的每个提示级别进行，这会在准备阶段积累有意义的合成数据成本。
为缓解这一问题，通常针对每个领域应用一个通用评分标准作为起点，然后由监督语言模型为每个提示分配细粒度的评分标准分数，以指导训练反馈。
以下是一个为科学任务生成评分标准的提示示例 [@gunjal2025rubrics]：

```text
You are an expert rubric writer for science questions in the domains of Biology, Physics, and Chemistry. 
Your job is to generate a self-contained set of evaluation criteria ("rubrics") for judging how good a response is to a given question in one of these domains. 
Rubrics can cover aspects such as factual correctness, depth of reasoning, clarity, completeness, style, helpfulness, and common pitfalls. 
Each rubric item must be fully self-contained so that non-expert readers need not consult
any external information.

Inputs:
- question: The full question text.
- reference_answer: The ideal answer, including any key facts or explanations.

Total items:
- Choose 7-20 rubric items based on question complexity.

Each rubric item must include exactly three keys:
1. title (2-4 words)
2. description: One sentence beginning with its category prefix, explicitly stating what to look for. 

For example:
- Essential Criteria: States that in the described closed system, the total mechanical energy (kinetic plus potential)
before the event equals the total mechanical energy after the event.
- Important Criteria: Breaks down numerical energy values for each stage, demonstrating that initial kinetic
energy plus initial potential energy equals final kinetic energy plus final potential energy.
- Optional Criteria: Provides a concrete example, such as a pendulum converting between kinetic and potential
energy, to illustrate how energy shifts within the system.
- Pitfall Criteria: Does not mention that frictional or air-resistance losses are assumed negligible when applying
conservation of mechanical energy.

3. weight: For Essential/Important/Optional, use 1-5 (5 = most important); for Pitfall, use -1 or -2.

Category guidance:
- Essential: Critical facts or safety checks; omission invalidates the response.
- Important: Key reasoning or completeness; strongly affects quality.
- Optional: Nice-to-have style or extra depth.
- Pitfall: Common mistakes or omissions; highlight things often missed.

Format notes:
- When referring to answer choices, explicitly say "Identifies (A)", "Identifies (B)", etc.
- If a clear conclusion is required (e.g. "The final answer is (B)"), include an Essential Criteria for it.
- If reasoning should precede the final answer, include an Important Criteria to that effect.
- If brevity is valued, include an Optional Criteria about conciseness.

Output: Provide a JSON array of rubric objects. Each object must contain exactly three keys-title, description, and weight.
Do not copy large blocks of the question or reference_answer into the text. Each description must begin with its category
prefix, and no extra keys are allowed.
Now, given the question and reference_answer, generate the rubric as described. 
The reference answer is an ideal response but not necessarily exhaustive; use it only as guidance.
```

另一个更简单的示例如下 [@rezaei2025onlinerubrics]：

```text
SYSTEM:
You generate evaluation rubrics for grading an assistant's response to a user prompt.

Rubric design rules:
- Each criterion must be atomic (one thing), objective as possible, and written so a grader can apply it consistently.
- Avoid redundant/overlapping criteria; prefer criteria that partition different failure modes.
- Make criteria self-contained (don't rely on unstated context).
- Include an importance weight for each criterion.

Output format (JSON only):
{
  "initial_reasoning": "<brief rationale for what matters for this prompt>",
  "rubrics": [
    {
      "reasoning": "<why this criterion matters>",
      "criterion": "<clear, testable criterion>",
      "weight": <integer 1-10>
    },
    ...
  ]
}

USER:
User prompt:
{prompt}

Generate the rubric JSON now.
```

正如你所见，这些提示可以非常详细，且针对训练设置进行了调整。

带 RL 训练的评分标准将继续超越其早期应用，扩展到指令遵循 [@he2025advancedif]、深度研究 [@shao2025drtulu]、评估深度研究智能体 [@sharma2025researchrubrics] 和长文生成 [@ruan2025expertlongbench] 等领域。
