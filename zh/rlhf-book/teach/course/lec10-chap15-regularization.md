---
title: "第10讲：强化学习中的正则化、为什么 RL 能泛化、以及为什么 SFT 会遗忘"
author: "Nathan Lambert"
fonts:
  heading: "Rubik"
  body: "Poppins"
bibliography: refs.bib
figure_captions: true
footer:
  left: "rlhfbook.com/course"
  center: "第10讲"
  right: "Lambert {n}/{N}"
custom_css: |
  .slide--section-break { background: #F28482; }
  :root {
    --colloquium-progress-fill: #F28482;
  }
  .slide--title-sidebar h1 {
    font-size: 2.5em;
    letter-spacing: 0;
  }
  /* Bulleted lists should never be centered (markers float, looks bad).
     Target lists only -- leave titles and display-math paragraphs centered. */
  .slide ul, .slide ol, .slide li { text-align: left; }
  /* Per-line math reveals: left-align display math and tighten spacing so
     stacked single-line equations read as one aligned derivation. */
  .slide.math-steps .katex-display { text-align: left; margin: 0.35em 0; }
---

<!-- layout: title-sidebar -->
<!-- valign: bottom -->

# 第10讲：强化学习中的正则化、为什么 RL 能泛化、以及为什么 SFT 会遗忘

<div class="colloquium-title-eyebrow">rlhfbook.com</div>

<div class="colloquium-title-meta">
<p class="colloquium-title-name">Nathan Lambert</p>
</div>

<p class="colloquium-title-note">后训练课程 · 第15章</p>

---

<!-- layout: section-break -->
<!-- align: center -->

## 这些优化器如何改变模型的分布？我们该如何控制？

---

<!-- columns: 45/55 -->
## 回顾：RLHF 流程

RL 步骤的目标是**最大化奖励模型的奖励，同时减去从参考模型漂移的惩罚**。

本讲关注的就是这个惩罚项——以及有它和没有它时分别会发生什么。

|||

![RLHF 训练流水线：RL 步骤根据奖励模型优化策略，并通过 KL 惩罚将其约束在参考模型附近。](assets/rlhf-overview.png)

---

<!-- columns: 50/50 -->
## RLVR 同样需要正则化，但最佳实践有所不同

相同的 RL 循环，不同的奖励来源：用验证函数代替奖励模型。

推理模型（在工具使用出现之前）常常直接去掉 KL 惩罚以增强学习效果。

随着大规模工具使用能力的出现，正则化正在回归主流——但目标已不再是到参考模型的 KL 惩罚，而是到*采样分布*的漂移（详见本讲末尾）。

|||

![RLVR 使用验证函数而非奖励模型，但 RL 循环——以及正则化问题——是一致的。](assets/rlvr-system.png)

---

<!-- columns: 40/60 -->
## 本讲大纲

我们如何显式地控制施加在模型上的优化压力。

所用优化器的数学形式如何改变模型的"形状"。

|||

```box
title: 大纲
tone: accent
content: |
  1. 控制 RL 的 **KL 惩罚**
  2. **KL 散度的两个方向**
  3. **为什么 RL 比 SFT 更好地泛化**
  4. **其他相关工作**
```

---

<!-- columns: 50/50 -->

## 补充：请先观看第9讲

```iframe
src: https://rlhfbook.com/teach/course/lec9-chap14-appb-overoptimization/
title: 第9讲幻灯片
height: 300
style: "border:none;display:block;width:100%;aspect-ratio:16/9;height:auto"
```

[幻灯片](https://rlhfbook.com/teach/course/lec9-chap14-appb-overoptimization/)——没错，这些就是真正的幻灯片，嵌在幻灯片里。

|||

```iframe
src: https://www.youtube.com/embed/y04JhXpiI4s?list=PLL1tdVxB1CpVpEtMHxwuR4uI4Lxjw00_y
title: 第9讲视频
height: 300
style: "border:none;display:block;width:100%;aspect-ratio:16/9;height:auto"
```

[在 YouTube 上观看](https://www.youtube.com/watch?v=y04JhXpiI4s&list=PLL1tdVxB1CpVpEtMHxwuR4uI4Lxjw00_y)

---

<!-- layout: section-break -->
<!-- align: center -->

## 第一部分：显式的 KL 惩罚

---

<!-- animate: bullets -->
## 到参考模型的 KL 惩罚控制着奖励

LLM 的标准奖励函数：

$$ r = r_\theta - \lambda_{\text{KL}} \, D_{\mathrm{KL}}\!\left( \pi_{\text{RL}}(y \mid x) \,\|\, \pi_{\text{ref}}(y \mid x) \right) $$

- KL 控制用于 RL 早于 LLM 时代：对话智能体 [@jaques2017sequence]，然后是微调预训练模型 [@jaques2020human]。
- 此惩罚是**反向 KL**——通过对*策略*采样并对照参考模型打分来估计。它惩罚策略在参考模型不会分配概率的地方放置质量（probability mass）。
- "KL 距离"是*优化距离*的花称（KL 并非真正的度量）。
- 实践中，上述 $\lambda$ 常写为 $\beta$。

---

<!-- columns: 45/55 -->
## 实践中如何测量 KL

从 $P$ 采样将定义转化为期望：

$$ D_{\mathrm{KL}}(P \,\|\, Q) = \mathbb{E}_{x \sim P}\left[ \log P(x) - \log Q(x) \right] $$

- 实践中会在训练过程中观察 KL 曲线——KL 值过大通常意味着存在 bug 或模型崩溃。
- 低方差估计量（$k_1, k_2, k_3$）在[问答第2期](https://www.youtube.com/watch?v=gB-bYUECpzE&list=PLL1tdVxB1CpVpEtMHxwuR4uI4Lxjw00_y&index=11)中被提及 [@schulman2020klapprox]。

|||

```python
# sample from the policy
tokens = model.generate(inputs)

# score sampled tokens under both models
logprobs     = log_softmax(model.forward(tokens).logits)
ref_logprobs = log_softmax(ref_model.forward(tokens).logits)

# log-probs of the tokens actually generated
token_lp     = gather(logprobs, tokens)
ref_token_lp = gather(ref_logprobs, tokens)

# sequence-level difference approximates KL
kl_approx = token_lp.sum(-1) - ref_token_lp.sum(-1)
```

---

## 实际运行中的曲线形态

![](assets/olmo2-grpo-zero-reward-kl.png)

一次 OLMo-2-7B 的 GRPO 运行，RL 直接在*基础模型*上进行（R1-Zero 风格，无 SFT），来自 open-instruct（[公开 W&B 日志](https://wandb.ai/ai2-llm/open_instruct_public/reports/OLMo-2-7B-GRPO-Fast-Zero--VmlldzoxMjA0MjU4MQ)）：在约 1M 个 episode 中，可验证奖励持续攀升，同时记录到与参考模型的 KL 逐步上升然后徘徊。该运行中 **β = 0**。
这是一个健康的形状。

---

<!-- cite-right: ziegler2019fine -->
<!-- animate: bullets -->

## 静态还是动态 KL 惩罚？β 最初是反馈控制器

首篇将 RLHF 应用于 LM 的论文并未固定 β。它选择一个**目标 KL**，让控制器去追逐它：

$$ e_t = \operatorname{clip}\!\left( \frac{\mathrm{KL}(\pi_t, \pi_{\text{ref}}) - \mathrm{KL}_{\text{target}}}{\mathrm{KL}_{\text{target}}},\, -0.2,\, 0.2 \right), \qquad \beta_{t+1} = \beta_t \left(1 + K_\beta\, e_t\right) $$

- 一个"对数空间比例控制器"（原论文用语），其中 $K_\beta = 0.1$：KL 过高 → β 增大，将策略拉回；过低 → β 缩小，放开约束。不同种子运行的实验最终落到*相同的* KL 预算上，使得实验可比较。
- 这个想法早于 RLHF：PPO 原始的**自适应 KL 惩罚**变体在目标附近将 β 翻倍或减半 [@schulman2017proximal]，而约束 RL 后来通过惩罚乘数上的完整**PID 控制器**将控制框架明确化 [@stooke2020responsive]。
- 现代实践又回到了较小的**静态**β——或者在许多 RLVR 推理流程中，完全不用 KL 项。

---

<!-- cite-right: ziegler2019fine -->

## 静态还是动态 KL 惩罚？β 最初是反馈控制器

首篇将 RLHF 应用于 LM 的论文并未固定 β。它选择一个**目标 KL**，让控制器去追逐它：

$$ e_t = \operatorname{clip}\!\left( \frac{\mathrm{KL}(\pi_t, \pi_{\text{ref}}) - \mathrm{KL}_{\text{target}}}{\mathrm{KL}_{\text{target}}},\, -0.2,\, 0.2 \right), \qquad \beta_{t+1} = \beta_t \left(1 + K_\beta\, e_t\right) $$

查看代码实现：[原始控制器](https://github.com/openai/lm-human-preferences/blob/cbfd210bb8b08f6bc5c26878c10984b90f516c66/lm_human_preferences/train_policy.py#L115-L124)（lm-human-preferences, 2019）· [TRL 的 `AdaptiveKLController`](https://github.com/huggingface/trl/blob/v0.11.4/trl/trainer/utils.py#L54-L69)（v0.11.4——在现代化重写中被删除）· [open-instruct 今日版本](https://github.com/allenai/open-instruct/blob/5b2ebfa12381925bb431845d588dbc9ebead20a7/open_instruct/grpo_utils.py#L104-L105)：静态 `beta = 0.05`，[直接应用于损失函数中](https://github.com/allenai/open-instruct/blob/5b2ebfa12381925bb431845d588dbc9ebead20a7/open_instruct/grpo_fast.py#L718)。

---

<!-- layout: section-break -->
<!-- align: center -->

## 第二部分：RL 优化是反向 KL 最小化

---

## 奖励惩罚和优化的"形状"是两回事

我们从一个 RL 设置中的**惩罚**开始：一个添加到奖励中的项，带有可调（或可控）的系数。

接下来要谈的是 **RL 优化的"形状"**，以及它与 KL 的关系。
关键在于"哪个方向的 KL"——这由*采样来自哪里*决定：

<!-- step -->

- **SFT**从*数据（或独立教师模型）*采样 → 最小化其损失等价于最小化**正向** KL。
- **RL**从*自身*采样 → *带上*惩罚时，最大化目标等价于向奖励倾斜的参考模型做**反向 KL 最小化**。这只在优化中包含 KL 惩罚时成立（并不适用于所有 RLVR 结果）……但同策略采样仍然*偏向* KL 最小的解。详见后文。

---

<!-- valign: top -->
<!-- title: center -->
<!-- cite-right: chen2025retainingdoingroleonpolicy -->
## RL 是反向 KL

从 KL 正则化目标出发（这是我们 RL 训练器优化的目标）：

$$
\max_\pi\; \mathcal{J}_{\text{RL}}(\theta) = \mathbb{E}_{x \sim \mathcal{D},\, y \sim \pi(\cdot \mid x)}\left[ r(x, y) \right] - \beta\, D_{\mathrm{KL}}\!\left(\pi(\cdot \mid x) \,\|\, \pi_{\text{ref}}(\cdot \mid x)\right)
$$

<!-- step -->

除以 $-\beta$ 并归一化后，目标转化为单个 KL——当 $\pi$ 等于最优策略 $\pi_\star$ 时恰好被最小化。第6讲走过相同的路径（DPO 的起点）：

$$ \pi_\star(y \mid x) = \frac{1}{Z(x)}\, \pi_{\text{ref}}(y \mid x)\, \exp\!\left(\tfrac{1}{\beta}\, r(x,y)\right) $$

<!-- step -->

将 $\pi_\star$ 读作**奖励倾斜的参考模型**（AI 建议的称呼，我自己没想出更好的名字）：取 $\pi_{\text{ref}}$ 并将每个补全的概率乘以 $\exp(r/\beta)$，然后重新归一化（$Z(x)$ 做的就是这件事）。"倾斜"将概率质量移向高奖励补全，同时保持在参考模型的支撑集内——大的 $\beta$ 倾斜幅度极小，小的 $\beta$ 则集中在最高奖励的补全上。

---

<!-- valign: top -->
<!-- title: center -->
<!-- class: math-steps -->
<!-- cite-right: chen2025retainingdoingroleonpolicy -->
## RL 是反向 KL

现在展开到 $\pi_\star$ 的反向 KL，代入 $\log \pi_\star = \log \pi_{\text{ref}} - \log Z(x) + \tfrac{1}{\beta} r(x,y)$：

$$ D_{\mathrm{KL}}(\pi_\theta \,\|\, \pi_\star) = \mathbb{E}_{x \sim \mathcal{D},\, y \sim \pi_\theta}\left[ \log \pi_\theta(y \mid x) - \log \pi_\star(y \mid x) \right] \qquad \text{定义；来自 } \pi_\theta \text{ 的采样} $$

<!-- step -->

$$ \phantom{D_{\mathrm{KL}}(\pi_\theta \,\|\, \pi_\star)} = \mathbb{E}_{x \sim \mathcal{D},\, y \sim \pi_\theta}\left[ \log \pi_\theta - \log \pi_{\text{ref}} + \log Z(x) - \tfrac{1}{\beta}\, r(x,y) \right] \qquad \text{代入 } \log \pi_\star $$

<!-- step -->

$$ \phantom{D_{\mathrm{KL}}(\pi_\theta \,\|\, \pi_\star)} = -\tfrac{1}{\beta}\,\mathbb{E}\left[r(x,y)\right] + D_{\mathrm{KL}}\!\left(\pi_\theta \,\|\, \pi_{\text{ref}}\right) + \underbrace{\log Z(x)}_{\text{常数}} \qquad \text{重组项} $$

<!-- step -->

$$ \phantom{D_{\mathrm{KL}}(\pi_\theta \,\|\, \pi_\star)} \propto -\tfrac{1}{\beta}\, \mathcal{J}_{\text{RL}}(\theta) \qquad \text{丢弃常数} $$

<!-- step -->

$$ \boxed{\ \max_\theta\, \mathcal{J}_{\text{RL}}(\theta) \iff \min_\theta\, D_{\mathrm{KL}}(\pi_\theta \,\|\, \pi_\star)\ } $$

在包含惩罚的情况下，RL 不仅仅是*使用*反向 KL——整个目标**就是**一个反向 KL，指向奖励倾斜的参考策略。

---

<!-- valign: top -->
<!-- title: center -->
## SFT 是正向 KL

接下来是对比。SFT 在固定数据集上训练——采样来自*数据分布*，记作 $\pi_{\mathcal{D}}$，这就对应了另一个 KL 方向：

$$
\begin{aligned}
D_{\mathrm{KL}}(\pi_{\mathcal{D}} \,\|\, \pi_\theta) &= \mathbb{E}_{(x,y) \sim \mathcal{D}} \left[ \log \pi_{\mathcal{D}}(y \mid x) - \log \pi_\theta(y \mid x) \right] && \text{定义；采样即数据}
\end{aligned}
$$

<!-- step -->

$$
\begin{aligned}
&= \underbrace{\mathbb{E}_{(x,y) \sim \mathcal{D}}\left[ \log \pi_{\mathcal{D}}(y \mid x) \right]}_{-H(\pi_{\mathcal{D}}),\ \theta \text{ 的常数}} \; - \; \mathbb{E}_{(x,y) \sim \mathcal{D}}\left[ \log \pi_\theta(y \mid x) \right] && \text{拆分期望}
\end{aligned}
$$

<!-- step -->

$$
\begin{aligned}
&= -H(\pi_{\mathcal{D}}) + \mathcal{L}_{\text{SFT}}(\theta) \;\propto\; \boxed{\ \mathcal{L}_{\text{SFT}}(\theta)\ } && \text{NLL 项即为 SFT 损失}
\end{aligned}
$$

相同的梯度、相同的最小值：最小化 SFT 损失*就是*最小化到数据分布的正向 KL。

---

<!-- rows: 18/82 -->
## SFT 和 RL 是 KL 的两个方向

这与第7讲（同策略蒸馏）非常相似，两个方向的 KL 都在发挥作用。后训练中的数学形式会重复出现：

===

<!-- row-columns: 50/50 -->
**正向 KL**——监督微调（也称标准 KL）：

$$ D_{\mathrm{KL}}(\pi_{\mathcal{D}} \,\|\, \pi_\theta) = \mathbb{E}_{y \sim \pi_{\mathcal{D}}}\!\left[\log \tfrac{\pi_{\mathcal{D}}(y)}{\pi_\theta(y)}\right] $$

采样来自**目标**（一个固定数据集）。

*质量覆盖（Mass-covering）*：无论目标在何处有质量而 $\pi_\theta \to 0$，损失都会爆炸——模型必须展开来覆盖一切。

|||

<!-- step -->

**反向 KL**——强化学习：

$$ D_{\mathrm{KL}}(\pi_\theta \,\|\, \pi_\star) = \mathbb{E}_{y \sim \pi_\theta}\!\left[\log \tfrac{\pi_\theta(y)}{\pi_\star(y)}\right] $$

采样来自**策略自身**。

*模式搜索（Mode-seeking）*：仅在被放置质量的地方受到惩罚，因此向高奖励模式集中。

---

<!-- rows: 18/82 -->
## 回顾第7讲：蒸馏中的同样两个方向

蒸馏版本，直接来自第7讲——用教师模型 $\pi_T$ 替代目标。从学生端采样补全使得 $\pi_\theta$ 出现在 KL 的**左侧**：

===

<!-- row-columns: 50/50 -->
**离线 KD / SFT**（正向 KL）——期望在*教师*上，$z \sim \pi_T$（**离策略**：固定的教师数据集）：

$$ D_{\mathrm{KL}}(\pi_T \,\|\, \pi_\theta) = \mathbb{E}_{z \sim \pi_T}\!\left[\log\frac{\pi_T(z)}{\pi_\theta(z)}\right] $$

*质量覆盖*——由**教师**的质量加权：无论教师在何处有质量而 $\pi_\theta \to 0$，对数比率都会爆炸，因此学生必须覆盖教师可能说出的*一切*。

|||

<!-- step -->

**同策略蒸馏**（反向 KL）——期望在*学生*上，$z \sim \pi_\theta$（**同策略**：你采样的是你正在训练的模型本身）：

$$ D_{\mathrm{KL}}(\pi_\theta \,\|\, \pi_T) = \mathbb{E}_{z \sim \pi_\theta}\!\left[\log\frac{\pi_\theta(z)}{\pi_T(z)}\right] $$

*模式搜索*——由**学生自身的**质量加权：仅当*它*在教师不喜欢的地方放置概率时受惩罚，因此坍塌到教师的模式上。第7讲将*为什么反向 KL 更好*推迟到本讲讨论。

---

<!-- layout: section-break -->
<!-- align: center -->

## 第三部分：为什么 RL 泛化更多

---

<!-- cite-right: chu2025sft -->
## "SFT 会记忆，RL 能泛化"

受控实验：在一个任务上后训练，然后在规则变化下评估（即对问题进行小修改以测试分布外表现）[@chu2025sft]。

- **GeneralPoints**：用四张牌通过 $+,-,\times,\div$ 组合达到 24；测试时改变牌面规则（训练：J/Q/K = 10；测试：11/12/13）。
- **V-IRL**：视觉导航；测试时从绝对方向（北/东）改为相对方向（左/右）。

在 V-IRL 上，RL 将分布外准确率从 **80.8% 提升到 91.8%**。而 SFT 将其摧毁至 **80.8% → 1.3%**——破坏了基础模型已有的空间推理能力。

基于 RL 的后训练仅凭其同策略结构本身就带有*隐式*正则化。SFT 则更加脆弱。

论文：[arxiv.org/abs/2501.17161](https://arxiv.org/abs/2501.17161)

---

## 哪个方向应该遗忘更少？

朴素的理解：正向 KL 是*质量覆盖*，因此 SFT 应保留所有模式——而模式搜索的 RL 会坍缩到单一模式并遗忘其余部分。

这是正确的吗？

---

<!-- img-fill -->
<!-- cite-right: chen2025retainingdoingroleonpolicy -->
## 哪个方向应该遗忘更少？

这种直觉假设策略是单模态的——但 LLM 是多模态的。论文：[arxiv.org/abs/2510.18874](https://arxiv.org/abs/2510.18874)

![](assets/retaining_by_doing_mode_intuition.png)

---

<!-- rows: 50/50 -->
<!-- cite-right: shenfeld2026rls -->
## RL 的剃刀：同等性能下更低的 KL 漂移

> *"对于一个新任务的众多高奖励解中，同策略方法（如 RL）内在倾向于保持在 KL 散度上更接近原始策略的解。"*

- 遗忘与 KL 漂移相关：$\text{Forgetting} \approx f\!\left(\mathbb{E}_{x \sim \tau}\!\left[D_{\mathrm{KL}}\!\left(\pi_0 \,\|\, \pi\right)\right]\right)$，$R^2 = 0.96$——在**新任务的数据上**测量。一种廉价的遗忘预测器。
- 消融实验：**同策略数据完全解释了差异**——负梯度没有可辨识的影响。论文：[arxiv.org/abs/2509.04259](https://arxiv.org/abs/2509.04259)

===

![在所有解决新任务的策略中，RL 收敛到与基础模型 KL 最近的策略——在匹配的新任务性能下产生更高的旧任务保留率。Shenfeld 等，2026（CC-BY）。](assets/rl_razor_motivation.png)

---

<!-- layout: section-break -->
<!-- align: center -->

## 第四部分：控制优化的其他工具

---

<!-- animate: bullets -->
## 其他正则化手段

大多数属于脚手架：为了稳定某一设置而添加，在下一代模型中被简化掉。

- **预训练下一个 token 预测梯度**（InstructGPT）：在目标中加入 $\gamma\, \mathbb{E}_{x \sim \mathcal{D}_{\text{pretrain}}}\left[\log \pi_{\text{RL}}(x)\right]$，"以修复公共 NLP 数据集上的性能回退" [@ouyang2022training]。
- **DPO 旁侧的 NLL**：$\mathcal{L}_{\text{DPO+NLL}} = \mathcal{L}_{\text{DPO}} + \alpha\, \mathcal{L}_{\text{NLL}}$ 确保所选文本在绝对意义上保持高似然，而非仅仅相对地更好 [@pang2024iterative]。
- **奖励模型的边际损失**（Llama 2）：$-\log \sigma\!\left(r_{\theta}(y_c) - r_{\theta}(y_r) - m(y_c, y_r)\right)$，其中边际 $m$ 来自标注者评分差值——即第8讲中的 Likert 量表 [@touvron2023llama]。

---

<!-- animate: bullets -->
## 2026：信任域 / KL 惩罚正在退场

工具使用正在改变正则化要承担的任务。在智能体配方中，到参考模型的 KL 惩罚正在消失：

- GLM-5 直接移除了它——"以加速 RL 改进" [@glm5team2026glm5]。Kimi 也不使用：K2 → K3 配方在没有 KL 惩罚的情况下发布，且完全没有参考策略 [@moonshot2026kimik3]。
- 在我们的 TMax 终端智能体配方中，我们测量了权衡：较小的 KL 减少了崩溃的严重程度但降低了奖励，因此最终配方为 $\beta = 0$ [@ivison2026tmax]。
- TMax 论文总结了我们要应对的数值问题的变化：20+ 回合的轨迹、异步/部分 rollout 以及训练与推理引擎的不匹配使得*从采样器*的漂移成为主要失败模式，而非从初始状态的漂移。（在 TMax 中，不稳定性在超过 10 个助手回合后增加，低于 5 个回合时则不存在 [@ivison2026tmax]。）

---

<!-- rows: 22/78 -->
<!-- cite-right: qi2026dppo -->
## 对采样分布的信任域

**DPPO**（Divergence Proximal Policy Optimization，散度近端策略优化）通过*直接估计* rollout 和训练策略之间的散度（二元总变差）来掩码 token，而非 PPO 的 per-token 比率裁剪 [@qi2026dppo]。

===

<!-- row-columns: 55/45 -->
per-token 比率是该散度的有噪单样本估计。GLM 的 IcePop [@glm5team2026glm5] 和 Kimi 的对数比率区间 [@moonshot2026kimik3] 做着同样的工作：掩码梯度，而非裁剪。

这就是正则化目前的重心所在——算法更新，而非 KL 惩罚。

|||

![动机，来自 DPPO 论文：对相同的 rollout token，per-token 概率比率（左）在低概率处爆炸，而直接估计的 TV 散度（右）保持稳定。Qi 等，2026。](assets/dppo-ratio-vs-tv.png)

---

## 要点回顾

- KL 惩罚是显式控制：一个**反向 KL**，在策略自身的采样上估计。
- KL 正则化的 RL 目标是反向 KL 最小化——向奖励倾斜的参考模型进行模式搜索——而 SFT 是正向方向，向数据质量覆盖。
- 即使没有惩罚，同策略 RL 也自带隐式正则化——SFT 记忆，RL 泛化。

可验证奖励比奖励模型更不易过优化！因此，正则化正在发生变化，KL 惩罚正扮演越来越小的角色。

---

<!-- columns: 50/50 -->
## 课程进度回顾

0. 先修知识回顾
1. 概述 *(第1-3章)*
2. IFT、奖励模型 & 拒绝采样 *(第4、5、9章)*
3. RL：动机与数学 *(第6章)*
4. RL：实现与实践 *(第6章)*
5. 推理模型的崛起 *(第7章)*
6. 直接偏好优化 *(第8章)*

|||

7. 合成数据与现代后训练 *(第12章)*
8. 偏好与偏好数据 *(第10-11章)*
9. 过优化与 RLHF 的恶名 *(第14章、附录B)*
10. **正则化** *(第15章)*——*今天*
11. **评估** *(第16章)*——*下一次（暂定）*
12. **工具使用基础** *(第13章)*——希望吧？

---

<!-- rows: 85/15 -->
## 感谢

欢迎提问和讨论！

如果你愿意花几秒钟订阅或把我的内容分享给朋友，对传播帮助巨大。

联系：nathan@natolambert.com

Newsletter: [interconnects.ai](https://www.interconnects.ai/)

**rlhfbook.com**

===

```builtwith
repo: natolambert/colloquium
```