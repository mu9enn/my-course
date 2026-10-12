<!--
  Copyright (c) 2025-2026 Nathan Lambert.
  Licensed under CC BY-NC-SA 4.0:
  https://creativecommons.org/licenses/by-nc-sa/4.0/
  Full license: https://github.com/natolambert/rlhf-book/blob/main/LICENSE-CHAPTERS
-->
---
prev-chapter: "过度优化"
prev-url: "14-over-optimization"
page-title: 正则化
search-title: "第 15 章：正则化"
meta-description: "保持 RLHF 和后训练更新有价值而不削弱基座模型的正则化方法。"
next-chapter: "评估"
next-url: "16-evaluation"
lectures:
  - video: "https://www.youtube.com/watch?v=IwpYxANrpUs&list=PLL1tdVxB1CpVpEtMHxwuR4uI4Lxjw00_y&index=15"
    label: "第 10 讲：RL 中的正则化、为什么 RL 会泛化、以及为什么 SFT 会遗忘"
---

# 正则化

在本书中，我们学习了许多工具，用于让模型从人类偏好、可验证奖励以及其他有价值的信号中学习。我们介绍的所有方法都非常强大，但如果相对于前一个训练阶段得到的强大通用模型（通常称为参考模型，reference model）变化过多，就可能造成问题。当模型从某个特定奖励中学到太多、导致分布外（out-of-distribution）性能下降时，这就被称为"过度优化"（over-optimization）——我们在上一章中已经讨论过这个问题。

在整个 RLHF 优化过程中，会多次使用正则化手段来防止对奖励模型的过度优化。这些场景下的过度优化表现为模型输出无意义的文本。偏离正常优化轨道的例子包括：模型输出看似合理的数学推理过程但答案极其错误、重复生成相同文本、语言切换、或大量使用特殊字符。本章将介绍用于控制模型优化的不同方法。

截至 2026 年，RLHF 实现中最流行的变体是一种 KL 距离——衡量当前策略（policy）与参考策略（reference policy）在生成样本上的距离。"KL 距离"（KL distance）是一个口语化说法，用来表达训练过程中的*优化距离*，尽管 KL 散度（KL divergence，衡量两个概率分布分离程度的底层数学方法）并不满足成为真正距离度量的形式化性质（直接称呼它为距离，比起称之为"分布差异的数值度量"要简单得多）。文献中涌现出许多其他的正则化技术，但大多在后续模型迭代中就消失了。也就是说，除了核心的生成 KL 距离之外，其他正则化手段往往用来稳定实验配置，而这些配置在下一代模型中可以简化。尽管如此，理解约束 RLHF 中优化的工具仍然很重要。

*在本章中，我们使用 $x$ 表示 prompts（提示），使用 $y$ 表示 completions（补全）。这一符号在语言模型文献中很常见，因为相关方法操作的是完整的 prompt-completion 对，而非单个 token。*

当在带有奖励模型 $r_\theta$ 的 RLHF 框架中使用正则化时，其一般形式如下：

$$ r = r_\theta - \lambda r_{\text{reg.}} $$ {#eq:rl_start}

参考实现为：

$$
r = r_\theta - \lambda_{\text{KL}} \mathcal{D}_{\text{KL}} \left( \pi_{\text{RL}}(y \mid x) \, \| \, \pi_{\text{ref}}(y \mid x) \right)
$$ {#eq:kl_standard}

## RL 优化中的 KL 散度

关于数学定义，参见附录 A（定义）。

KL 散度衡量一个概率分布相对于另一个分布漂移了多少——当 KL 为零时，两个分布产生相同的输出。回忆一下它的定义为：

$$ \mathcal{D}_{\text{KL}}(P || Q) = \sum_{x \in \mathcal{X}} P(x) \log \left(\frac{P(x)}{Q(x)}\right) $$ {#eq:kl_distance_regularization}

在 RLHF 中，我们关心的两个分布通常分别是新模型版本的分布（设为 $P(x)$）和参考策略的分布（设为 $Q(x)$）。不同的优化器使用不同方向的 KL。全书中最常用的 KL 惩罚称为对参考策略的*反向 KL*（reverse KL）。在实践中，这等价于蒙特卡洛估计：从 RL 模型中采样 token，然后从参考模型中计算概率。从直觉上看，这种反向 KL 具有一个数值性质——当新模型 $P$（或 $\pi_{\text{RL}}$）在原始参考模型赋予低概率的区域放置了大量概率质量时，它会施加较大的惩罚。

另一种 KL 方向在机器学习中仍然经常被使用，例如在一些 RL 算法的内部信任域计算中。这种惩罚的直觉是：当新模型的更新*没有*对 $Q$ 或 $\pi_{\text{ref}}$ 中大概率区域施加概率时，它就会受到惩罚。这更接近于蒸馏（distillation）或行为克隆（behavioral cloning）所使用的目标。

### 参考模型与生成文本

KL 惩罚最常见的实现方式是将训练过程中生成的 token 与一个静态参考模型之间的距离进行比较。直觉是：你从中训练的模型有一种你希望保持的风格。这个参考模型通常是指令微调（instruction tuned）后的模型，也可以是前一个 RL 检查点。通过简单的代入，我们从中采样的模型变为 $\pi_{\text{RL}}(x)$ 和 $\pi_{\text{ref}}(x)$，如 @eq:kl_standard 所示（在标准定义中，当应用于 RL KL 惩罚时，通常记为 $P$ 和 $Q$）。这种 KL 散度惩罚早在大型语言模型流行之前就已应用于对话智能体 [@jaques2017sequence]，而 KL 控制很快就被确立为微调预训练模型的核心技术 [@jaques2020human]。

### 实现示例

在实践中，KL 散度的实现通常会被近似 [@schulman2016klapprox]，使得实现远为简洁。根据上述定义，当直接从分布 $P$ 采样时，KL 的求和可以转化为期望（这里的 $x$ 是样本空间上的通用随机变量，不是本书其他地方使用的 prompt 符号）。这里 $P$ 是当前正在训练的模型的生成分布（即参考模型之外的模型）。那么，KL 散度的计算变为：

$$
\mathcal{D}_{\text{KL}}(P \,||\, Q) = \mathbb{E}_{x \sim P} \left[ \log P(x) - \log Q(x) \right].
$$ {#eq:kl_expectation}

这种基于采样的形式更容易实现，尤其是在语言模型训练中频繁使用的对数概率直接处理上。

```python
# Step 1: generate() autoregressively samples a full sequence token by token
generated_tokens = model.generate(inputs)

# Step 2: forward() runs a single pass over the sequence to get per-token logits (no sampling)
logits       = model.forward(generated_tokens[:, :-1]).logits
ref_logits   = ref_model.forward(generated_tokens[:, :-1]).logits

# Step 3: Convert logits to log-probabilities
logprobs     = F.log_softmax(logits, dim=-1)
ref_logprobs = F.log_softmax(ref_logits, dim=-1)

# Step 4: Gather the probability each model assigns to the tokens that were actually generated
token_logprobs     = logprobs.gather(-1, generated_tokens[:, 1:].unsqueeze(-1)).squeeze(-1)
ref_token_logprobs = ref_logprobs.gather(-1, generated_tokens[:, 1:].unsqueeze(-1)).squeeze(-1)

# Step 5: Sum to get sequence-level log-probs; their difference approximates KL
seq_logprob     = token_logprobs.sum(dim=-1)
ref_seq_logprob = ref_token_logprobs.sum(dim=-1)

kl_approx = seq_logprob - ref_seq_logprob
kl_full   = F.kl_div(ref_logprobs, logprobs, reduction='batchmean')
```

一些参考实现包括 [TRL](https://github.com/huggingface/trl/blob/5c21de30ae210e4251ead85517ba8dfe3f210e81/trl/trainer/ppo_trainer.py#L1150) 和 [Hamish Ivison 的 JAX 代码](https://github.com/hamishivi/EasyLM/blob/main/EasyLM/models/llama/llama_train_ppo.py#L278)。


## 控制优化的其他工具

在后训练文献中，许多知名模型包含了其他正则化方法，帮助在其配置下达到领先性能。举这些例子是为了描绘一些领先模型是如何通过后训练设置来操纵以获得稳定优化的图景，而不是说这些工具在每个设置中都应该直接适用。还有无数种更有创意的解决方案可以被找到并且将会被找到！

### RL 中的预训练梯度

另一种看待正则化的方式是：你可能拥有一个希望模型保持接近的*数据集*，正如 InstructGPT [@ouyang2022training] 中所做的那样，"以修复在公共 NLP 数据集上的性能回退"。为了实现这一点，他们修改了 RLHF 的训练目标。从 @eq:rl_start 出发，我们可以将其转换为一个优化目标函数：通过对用于 RLHF 的 RL 数据集中的提示 $x$ 和补全 $y$ 从 RL 策略模型中采样，得到：

$$
J(\theta) = \mathbb{E}_{(x,y) \sim \mathcal{D}_{\pi_{\text{RL},\theta}}} \left[ r_{\theta}(y \mid x) - \lambda r_{\text{reg.}} \right]
$$ {#eq:objective_regularization}

然后，我们可以增加一个额外奖励，即在预训练期间使用的标准自回归逐 token 预测损失上获得更高的概率，通过对来自预训练语料库（或其他数据集）的一组文档进行采样，以维持文本连贯性：

$$
J(\theta) = \mathbb{E}_{(x,y) \sim \mathcal{D}_{\pi_{\text{RL},\theta}}} \left[ r_{\theta}(y \mid x) - \lambda r_{\text{reg.}} \right] + \gamma \mathbb{E}_{x \sim \mathcal{D}_{\text{pretrain}}} \left[ \log(\pi_{\text{RL},\theta}(x)) \right]
$$ {#eq:objective_pretraining}

### DPO 中的逐 token 准确率

最近的工作提出使用负对数似然（negative log-likelihood）项来平衡直接偏好优化（Direct Preference Optimization, DPO）的优化 [@pang2024iterative]。鉴于 DPO 损失具有成对特性，相同的损失修改也可以应用于奖励模型训练，约束模型预测准确的文本。

优化过程如下是对 DPO 的修改：

$$\mathcal{L}_{\text{DPO+NLL}} = \mathcal{L}_{\text{DPO}}(c_i^w, y_i^w, c_i^l, y_i^l \mid x_i) + \alpha \mathcal{L}_{\text{NLL}}(c_i^w, y_i^w \mid x_i)
$$ {#eq:dpo_nll}

$$
= -\log \sigma \left( \beta \log \frac{P_\theta(c_i^w, y_i^w \mid x_i)}{P_{\text{ref.}}(c_i^w, y_i^w \mid x_i)} - \beta \log \frac{P_\theta(c_i^l, y_i^l \mid x_i)}{P_{\text{ref.}}(c_i^l, y_i^l \mid x_i)} \right) - \alpha \frac{\log P_\theta(c_i^w, y_i^w \mid x_i)}{|c_i^w| + |y_i^w|},
$$ {#eq:dpo_nll_expanded}

其中 $P_{\theta}$ 是可训练的策略模型，$P_{\text{ref.}}$ 是固定的参考模型（通常是 SFT 检查点），$(c_i^w, y_i^w)$ 和 $(c_i^l, y_i^l)$ 分别表示提示 $x_i$ 对应的获胜补全和失败补全。第一项是标准的 DPO logistic 损失：它使用对数似然比 $\log \tfrac{P_{\theta}}{P_{\text{ref.}}}$ 的差异来增大获胜与失败之间的边距，$\beta$ 控制这一偏好信号将模型从参考状态拉离的强度。第二项是对获胜补全的长度归一化负对数似然惩罚，由 $\alpha$ 加权，它帮助保持偏好文本在绝对语言建模意义上的高概率，而不仅仅是在拒绝样本的相对比较中更好。

### 奖励建模中的基于边距的正则化

RLHF 栈的其他部分对优化的控制定义得不够明确。大多数奖励模型除了标准对比损失函数外没有任何正则化。直接对齐算法（Direct Alignment Algorithms）通过 $\beta$ 参数以不同的方式处理对 KL 散度的正则化（参见[直接对齐章节](https://rlhfbook.com/c/08-direct-alignment)）。

Llama 2 为奖励模型训练提出了一个边距损失（margin loss）[@touvron2023llama]：

$$
\mathcal{L}(\theta) = - \log \left( \sigma \left( r_{\theta}(y_c \mid x) - r_{\theta}(y_r \mid x) - m(y_c, y_r) \right) \right)
$$ {#eq:margin_loss}

其中 $m(y_c, y_r)$ 是两个数据点 $y_c$ 和 $y_r$ 之间的边距，表示两位标注员对两个输出的评分差值的数值差异。这可以通过让标注员在数值量表上对输出进行评分来实现，或者使用量化排名方法，如 [Likert 量表](https://en.wikipedia.org/wiki/Likert_scale)。

奖励边距在直接对齐文献中得到了大量使用，例如 Reward-weighted DPO；Reward-aware Preference Optimization（RPO），它在 DPO 损失之后将奖励模型分数整合到更新规则中 [@adler2024nemotron]；以及 REBEL [@gao2024rebel]，后者在回归损失公式中具有奖励差值加权。

## 隐式正则化

本章的其他部分描述的是*显式*正则化：KL 惩罚、预训练梯度和边距损失，这些是从业者有意添加到训练目标中的。越来越多的经验研究表明，基于 RL 的后训练也提供了*隐式*正则化——一种源于同策略优化结构本身的、对过拟合和灾难性遗忘的内在抵抗力。即使没有任何用于控制 RL 训练的显式工具（如 KL 惩罚或回放缓冲区），这种抵抗也会因损失更新的性质而出现。

### SFT 记忆，RL 泛化

后训练社区面临的一个核心问题是：当在单一任务上训练时，模型是学到了一种可以迁移到未见变体的可泛化规则，还是仅仅记住了训练分布的表面模式？Chu 等人 2025 [@chu2025sft] 通过一项受控的经验研究回答了这个问题，直接隔离了后训练方法——SFT 与 RL——对分布外（OOD）泛化的影响。答案很明确：RL 学习到的是可迁移的规则，而 SFT 记住了训练数据，在分布偏移时性能崩塌。

该研究使用了两个具有内置规则变化的环境来理解这种权衡：

- **GeneralPoints** 是一款算术纸牌游戏，模型收到四张扑克牌，必须用运算符（+、-、*、/）组合它们的数值来达到目标数字（默认为 24）。OOD 测试改变了人脸牌的计分方式：训练时使用一种规则（J、Q、K 均计为 10），评估时使用另一种规则（J = 11、Q = 12、K = 13）。

- **V-IRL** 是一个真实的视觉导航任务，模型按照语言指令穿越城市街道路线，并在途中识别地标。OOD 偏移将动作空间从绝对方向（北、东）切换为相对方向（左、右）。

在所有任务变体中，随着训练算力增加，RL 持续改善 OOD 性能，而 SFT 尽管在分布内性能上有所提升，却持续*降低* OOD 性能。差异幅度令人瞩目：在 V-IRL 中，仅使用语言输入，OOD 偏移从绝对方向到相对方向坐标，RL 将 OOD 逐步准确率从 80.8% 提高到 91.8%，而 SFT 将其从 80.8% 崩溃至 1.3%。SFT 模型的表现不仅仅是未能泛化：它摧毁了基座模型已经具备的空间推理能力，退化为从指令短语到绝对方向的查找表。

### 以做代守：同策略数据缓解遗忘

上一节展示了 RL 在 SFT 记忆的场景中能够泛化。Chen 等人 2025 [@chen2025retainingdoingroleonpolicy] 提出了一个互补的问题：当*依次*在多个任务上训练时，模型是否保留了过去所学？他们发现，RL 在目标任务上取得了相当甚至更高的提升，同时比 SFT 遗忘得少得多，并将这一优势追溯到了两种目标函数在优化本质上的根本差异。

为了理解为什么这两种方法表现出如此大的差异，我们可以从 KL 散度的视角来看待它们的目标。在这一节中，我们首先展示两种常见的后训练方法可以映射到 KL 散度的两个方向，然后解释将这些作为损失函数时的数值行为如何转化为不同的模型行为。

KL 散度定义为两个分布之间的期望对数比：$\mathbb{E}_{x \sim P}\!\left[\log \frac{P(x)}{Q(x)}\right]$，可以写成两个方向上的对数差：

- **前向 KL**（Forward KL）：$\text{KL}(P \| Q) = \mathbb{E}_{x \sim P}\!\left[\log P(x) - \log Q(x)\right]$
- **反向 KL**（Reverse KL）：$\text{KL}(Q \| P) = \mathbb{E}_{x \sim Q}\!\left[\log Q(x) - \log P(x)\right]$

其中 $P$ 是目标分布，$Q$ 是我们使用参数 $\theta$ 建模的分布。关键区别在于我们从哪个分布采样：前向 KL 从目标（或最优）分布 $P$ 采样，而反向 KL 从我们的策略 $Q$ 采样。在下方的推导中，$P$ 对应目标 $\pi_\star$（分析 SFT 时是训练数据分布，分析 RL 时是奖励最优策略），$Q$ 对应学习到的策略 $\pi_\theta$（我们正在训练的模型）。SFT 将目标放在前面——$\text{KL}(\pi_\star \| \pi_\theta)$——而 RL 翻转了顺序——$\text{KL}(\pi_\theta \| \pi_\star)$——改变了我们从哪个分布采样的方式。样本提供了用于学习的数据。目标函数，SFT 或 RL，塑造了模型。

#### SFT 前向 KL

从前向 KL 的定义开始：

$$
\text{KL}(\pi_\star \| \pi_\theta) = \mathbb{E}_{(x,y) \sim \mathcal{D}} \left[ \log \pi_\star(y \mid x) - \log \pi_\theta(y \mid x) \right]
$$

将期望拆分为对数差的两项：

$$
= \mathbb{E}_{(x,y) \sim \mathcal{D}} \left[ \log \pi_\star(y \mid x) \right] - \mathbb{E}_{(x,y) \sim \mathcal{D}} \left[ \log \pi_\theta(y \mid x) \right]
$$

第一项 $\mathbb{E}\!\left[\log \pi_\star(y \mid x)\right]$ 仅依赖于数据分布，等于负熵 $-H(\pi_\star)$——一个不随 $\theta$ 变化的常数。第二项 $-\mathbb{E}\!\left[\log \pi_\theta(y \mid x)\right]$ 是数据集上的负对数似然，即标准的 SFT 交叉熵损失 $\mathcal{L}_\text{SFT}(\theta)$。代入后得到：

$$
= \underbrace{-H(\pi_\star)}_\text{const} + \mathcal{L}_\text{SFT}(\theta) \propto \mathcal{L}_\text{SFT}(\theta)
$$ {#eq:sft_forward_kl}

由于熵项相对于 $\theta$ 是常数，两种损失共享相同的梯度和相同的最小值——最小化 SFT 损失等价于最小化**前向 KL**散度 $\text{KL}(\pi_\star \| \pi_\theta)$。

#### RL 反向 KL

让我们从标准的 KL 正则化 RL 目标开始：

$$
\max_\pi \; \mathcal{J}_\text{RL}(\theta) = \mathbb{E}_{x \sim \mathcal{D},\, y \sim \pi(\cdot \mid x)} \left[ r(x, y) \right] - \beta \cdot \text{KL}\!\left(\pi(\cdot \mid x) \| \pi_\text{ref}(\cdot \mid x)\right)
$$ {#eq:rl_objective_retaining}

提取 $-\beta$ 将最大化转为最小化：

$$
= \min_\pi \; \mathbb{E}_{x \sim \mathcal{D},\, y \sim \pi(\cdot \mid x)} \left[ \log \frac{\pi(y \mid x)}{\pi_\text{ref}(y \mid x)} - \frac{1}{\beta} r(x, y) \right]
$$ {#eq:rl_min_form}

引入配分函数 $Z(x) = \sum_y \pi_\text{ref}(y \mid x) \exp\!\left(\frac{1}{\beta} r(x,y)\right)$ 来将奖励偏置的参考分布归一化为一个合法的分布，并加上并减去 $\log Z(x)$，内部期望变为 KL 散度：

$$
= \min_\pi \; \mathbb{E}_{x \sim \mathcal{D}} \left[ \text{KL}\!\left(\pi(\cdot \mid x) \;\middle\|\; \frac{1}{Z(x)} \pi_\text{ref}(\cdot \mid x) \exp\!\left(\tfrac{1}{\beta} r(x,y)\right) \right) - \log Z(x) \right]
$$ {#eq:rl_kl_form}

由于 $\log Z(x)$ 不依赖于 $\pi$，且 KL 散度非负且当且仅当两个分布完全相同时为零，当 $\pi$ 等于奖励偏置分布时，KL 最小化为零。因此在奖励 $r(x,y)$ 下的最优策略为：

$$
\pi_\star(y \mid x) = \frac{1}{Z(x)} \pi_\text{ref}(y \mid x) \exp\!\left(\frac{1}{\beta} r(x,y)\right)
$$ {#eq:optimal_policy_retaining}

现在我们可以通过直接展开 $\text{KL}(\pi_\theta \| \pi_\star)$ 并代入 $\log \pi_\star(y \mid x) = \log \pi_\text{ref}(y \mid x) - \log Z(x) + \frac{1}{\beta} r(x, y)$ 来展示与反向 KL 的联系：

$$
\begin{aligned}
\text{KL}(\pi_\theta \| \pi_\star) &= \mathbb{E}_{x \sim \mathcal{D},\, y \sim \pi_\theta(\cdot \mid x)} \left[ \log \pi_\theta(y \mid x) - \log \pi_\star(y \mid x) \right] \\
&= \mathbb{E}_{x \sim \mathcal{D},\, y \sim \pi_\theta(\cdot \mid x)} \left[ \log \pi_\theta(y \mid x) - \log \pi_\text{ref}(y \mid x) + \log Z(x) - \frac{1}{\beta} r(x, y) \right] \\
&= - \frac{1}{\beta} \mathbb{E}_{x,y}\!\left[r(x,y)\right] + \text{KL}\!\left(\pi_\theta(\cdot \mid x) \;\middle\|\; \pi_\text{ref}(\cdot \mid x)\right) + \underbrace{\log Z(x)}_\text{const} \\
&\propto - \frac{1}{\beta} \mathbb{E}_{x,y}\!\left[r(x,y)\right] + \text{KL}\!\left(\pi_\theta(\cdot \mid x) \;\middle\|\; \pi_\text{ref}(\cdot \mid x)\right) \\
&= -\frac{1}{\beta} \mathcal{J}_\text{RL}(\theta)
\end{aligned}
$$

等价地，最大化 RL 目标 $\mathcal{J}_\text{RL}(\theta)$ 等同于最小化**反向 KL**散度 $\text{KL}(\pi_\theta \| \pi_\star)$。

上述推导表明，SFT 和 RL 优化的是根本不同的目标：SFT 最小化前向 KL，RL 最小化反向 KL。

![前向 KL（SFT）与反向 KL（RL）的遗忘动力学。"旧模式"代表先验知识，"新模式"代表目标任务。前向 KL 将策略拉伸以覆盖目标，并将质量从旧模式中拉出（右上），而反向 KL 将新模式向目标偏移而不扰动旧模式（右下）。来源：Chen et al. 2025，经作者许可。](images/retaining_by_doing_mode_intuition.png){#fig:retaining-mode-intuition}

两种方向的 KL 散度诱导了不同的优化压力。

**前向 KL**在目标分布有质量而模型没有的区域对模型施加惩罚，这倾向于鼓励**模式覆盖**（mode covering）——模型广泛分布概率以覆盖目标的所有主要模式。为什么会这样：前向 KL 的期望是在 $\pi_\star$ 下计算的，因此当模型未能为目标分布有质量的区域分配概率时，它会受到严重惩罚。

**反向 KL**仅在模型实际放置质量的区域对模型施加惩罚，这倾向于鼓励**模式寻求**（mode seeking）——模型可以集中于一个高概率模式而忽略其他。这里的期望是在 $\pi_\theta$——模型自身的分布——下计算的，因此即使 $\pi_\star$ 在那里分配了大量质量，$\pi_\theta(y \mid x) \approx 0$ 的区域对损失的贡献也很少。同时，它对模型在目标不存在的区域放置质量施加惩罚。

基于这一区别，我们可能会天真地认为 SFT 应该比 RL *遗忘得更少*：模式覆盖的前向 KL 应当维持所有目标模式的概率质量，从而保留先验知识，而模式寻求的反向 KL 可能会坍缩到单个高奖励模式上并放弃其他模式。然而，事实恰恰相反。这种直觉假设策略是单模态的，但预训练语言模型包含多个模式——而对于多模态分布，动力学翻转了。

考虑一个具有两个模式的策略：一个代表先验知识的"旧"模式和一个代表目标任务的"新"模式（@fig:retaining-mode-intuition）。前向 KL（SFT）试图覆盖目标分布的所有模式，这迫使策略拉伸并重新分配来自旧模式的概率质量，从而破坏其形状并导致遗忘。相比之下，反向 KL（RL）只需要在某些高奖励区域放置质量，因此它可以将从其采样出的新模式向目标偏移，而完全不触碰旧模式，保持先验知识完整。

RL 的模式寻求行为——反向 KL 的一个结构性质——保留了模型先验知识的广度，并实现了更好的泛化。

总结如下：

- **SFT（前向 KL）**：$\text{KL}(\pi_\star \| \pi_\theta)$——采样来自目标 $\pi_\star$，即一份由人类编写的补全的固定数据集。对于每个示例，我们问：我们的模型 $\pi_\theta$ 为这个示例分配了多少概率？模型从不生成任何东西；它只是学习模仿。这种模式覆盖的压力迫使策略广泛重新分配概率质量，这可能会破坏先验知识。

- **RL（反向 KL）**：$\text{KL}(\pi_\theta \| \pi_\star)$——采样来自我们自己的策略 $\pi_\theta$。对于模型生成的每个补全，我们问：这个补全距离奖励最优策略 $\pi_\star$ 有多近？因为模型只在它自己的生成上进行训练，更新保持在它已经放置概率质量的区域附近——奖励信号告诉它应该强化哪些生成，将概率向 $\pi_\star$ 偏移，同时不扰动分布的其余部分。

### RL 剃刀：为什么在线 RL 遗忘更少

上一节展示了同策略采样驱动了 RL 对抗遗忘的抵抗力，并将机制追溯到了前向 KL 与反向 KL 的动态。对于给定任务，存在许多实现高性能的截然不同的策略。Shenfeld 等人 2026 [@shenfeld2026rls] 对 RL 的泛化提供了互补的视角，引入了 **RL 剃刀**（RL's Razor）论点，其核心主张如下：

> 在对于新任务的许多高奖励解决方案中，RL 等同策略方法本质上倾向于在 KL 散度上更接近原始策略的解决方案。

![偏向 KL 最小化方案可减少遗忘。（左）在解决新任务的策略中，RL 收敛到与基座模型在 KL 意义上最近的策略。（右）与 SFT 相比，这种 KL 偏向在匹配新任务性能的同时实现了更高的先验任务保留率。来源：Shenfeld, Pari, and Agrawal 2026。许可证 CC-BY。](images/rl_razor_motivation.png){#fig:rl-razor-motivation}


作者发现，过去任务的遗忘量与微调策略相对于初始模型的漂移程度（由 KL 散度衡量）成正比：

$$
\text{Forgetting} \approx f\!\left(\mathbb{E}_{x \sim \tau}\!\left[\text{KL}\!\left(\pi_0(\cdot \mid x) \| \pi(\cdot \mid x)\right)\right]\right)
$$ {#eq:rl_razor_forgetting}


在 RL 和 SFT 的多种训练方式中，作者通过经验证明遗忘与训练后和初始策略之间的 KL 散度强相关（$R^2 = 0.96$），**且测量使用的是新任务数据**。这令人惊讶，因为 KL 是在*新任务的*输入分布上测量的，而非来自先前任务的保留数据，但它仍然能预测过去任务上的性能下降。在实践中，这为我们提供了一个强大的工具，可以直接从基座策略和训练策略之间的漂移来估计遗忘量——通过测量新专用数据上的 KL 距离。

为了确定导致 RL 策略 KL 漂移更小的原因，作者从两个维度分解了 RL 和 SFT 之间的差异——同策略与离线数据、以及目标是否包含负梯度（在 RL 中，当样本得分低于奖励基线时存在，在 SFT 中则不存在，因为 SFT 只强化正确的演示）——这些负梯度将概率从错误输出中推开。令人惊讶的是，他们发现同策略与离线数据完全解释了泛化性能的差异，而负梯度没有可辨识的影响。

从直觉上看，同策略方法采样的是模型已经赋予非忽略概率的输出，因此每次更新都被约束在靠近当前分布的区域。另一方面，SFT 在固定的外部分布上训练，该分布可能远离模型当前生成的内容，而每一步梯度都会将模型拉向那个遥远的目标，无论模型自身信念如何。
