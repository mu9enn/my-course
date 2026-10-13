---
title: "LLM 后训练的机器学习基础"
author: "Nathan Lambert"
fonts:
  heading: "Rubik"
  body: "Poppins"
bibliography: refs.bib
figure_captions: true
footer:
  left: "rlhfbook.com/course"
  center: "LLM 后训练的机器学习基础"
  right: "Lambert {n}/{N}"
custom_css: |
  .slide--section-break { background: #84A98C; }
  :root {
    --colloquium-progress-fill: #84A98C;
  }
  .slide--title-sidebar h1 {
    font-size: 2.5em;
    letter-spacing: 0;
  }
---

<!-- layout: title-sidebar -->
<!-- valign: bottom -->

# 课程先修知识：LLM 后训练的机器学习基础

<div class="colloquium-title-eyebrow">rlhfbook.com</div>

<div class="colloquium-title-meta">
<p class="colloquium-title-name">Nathan Lambert</p>
</div>

<p class="colloquium-title-note">从交叉熵到偏好和强化学习——在 Lecture 1 之前的一篇简短、可选的复习。</p>

<p class="colloquium-title-note" style="font-size: 0.6em; opacity: 0.7;">本幻灯片在 GLM 5.2 的协助下撰写。</p>

---

## 这篇复习涵盖什么

**不要求有强化学习的先修知识。** 我们假设你具备入门级机器学习的素养——熟悉损失函数、梯度和概率论，并能熟练使用 PyTorch 的张量操作。本幻灯片是对自回归语言模型以及本课程使用的一小部分核心思想的复习：

- **语言模型**——对数概率的自回归分解、语言模型头（LM head）、softmax、交叉熵、以及张量形状解剖
- **优化**——梯度下降、训练循环、预训练 → 监督微调（SFT）
- **概率论**——KL 散度（及熵）、sigmoid 和成对似然
- **强化学习的建模方式**——马尔可夫决策过程（MDP）设置及 RL 的目标

---

<!-- layout: section-break -->

## 语言模型

---

<!-- columns: 45/55 -->
## 语言模型是什么

语言模型以**自回归**的方式学习一组**词元**（tokens，即词/子词）的联合概率——每次预测都依赖于它之前的词元。

给定 $x = (x_1, \ldots, x_T)$，模型将序列概率分解为：

$$P_\theta(x) = \prod_{t=1}^{T} P_\theta(x_t \mid x_1, \ldots, x_{t-1}).$$

现代大语言模型（ChatGPT、Claude、Gemini）都是基于**自注意力**的**仅解码器 Transformer**——每个位置只能关注自身以及它之前的位置。

|||

![下一个词元预测：一个仅解码器语言模型从它之前的前缀中一次预测一个词元。](assets/pretraining_next_token_tikz.png)
<!-- cite-right: Vaswani2017AttentionIA -->

---

## 语言模型头（LM head）

Transformer 主干网络为每个词元输出一个**隐藏状态**（hidden state）向量。**LM head** 是一个最后的线性投影层，从隐藏维度投影回**词表**（tokenizer 空间）。

- 隐藏状态 $\xrightarrow{\text{LM head}}$ **logits**（每个词表词元一个分数）
- logits 经过 **softmax** → 下一个词元的概率分布
- 从该分布中采样 / 取 argmax → 生成的词元

同一个主干网络可以携带**不同的 head** 来应对不同的任务。在本课程中，第一个例子是一个**奖励模型头**（第 5 章）——相同的 Transformer，新的 head，新的目标函数。

---

## Softmax 与对数概率

**Softmax** 将时刻 $t$ 的 logits $z^{(t)}$ 转换为下一个词元的分布——产生每个词元的概率：

$$P_\theta(x_t \mid x_{<t}) = \mathrm{softmax}(z^{(t)})_{x_t} = \frac{e^{z^{(t)}_{x_t}}}{\sum_j e^{z^{(t)}_j}}.$$

整个序列的概率是这些项的**乘积**（链式法则），而在**对数空间**中乘积变成了求和：

$$\log P_\theta(x) = \log \prod_{t=1}^{T} P_\theta(x_t \mid x_{<t}) = \sum_{t=1}^{T} \log P_\theta(x_t \mid x_{<t}).$$

因此，求和中的每一项都是在真实词元处读取的 logits 的 `log_softmax`——这恰好就是该位置处的（负的）交叉熵损失。

为什么要用对数概率？**数值稳定性**（许多小概率的连乘会下溢），以及求和比连乘更容易求导。

---

## 一个 LM 训练样本的张量解剖

课程中会讨论 logits 的移位、目标对数概率的抓取（gather）和 mask 掩码。下面以张量形状层面完整走一遍整个流程：

```text
input_ids  ∈ ℕ^{B × L}          # INPUT TO MODEL -- token IDs, batch B, length L
   → model(input_ids).logits ∈ ℝ^{B × L × V}     # one vector per position, V = vocab
   → log_softmax + gather    ∈ ℝ^{B × (L-1)}     # log-prob of each observed token
   → (× completion_mask).sum ∈ ℝ^{B}             # one completion log-prob per sequence
```

接下来：用 PyTorch 逐步展示相同的路径。

---

## 一个 LM 训练样本的张量解剖

```python
logits = model(input_ids).logits            # (B, L, V): a score for every vocab token, at every position
```

---

## 一个 LM 训练样本的张量解剖

```python
logits = model(input_ids).logits            # (B, L, V): a score for every vocab token, at every position
logits = logits[:, :-1, :]                  # drop the last position — its prediction has no next token to score
```

---

## 一个 LM 训练样本的张量解剖

```python
logits = model(input_ids).logits            # (B, L, V): a score for every vocab token, at every position
logits = logits[:, :-1, :]                  # drop the last position — its prediction has no next token to score
labels = input_ids[:, 1:]                   # the target at each position is just the actual next token (the shift)
```

---

## 一个 LM 训练样本的张量解剖

```python
logits = model(input_ids).logits            # (B, L, V): a score for every vocab token, at every position
logits = logits[:, :-1, :]                  # drop the last position — its prediction has no next token to score
labels = input_ids[:, 1:]                   # the target at each position is just the actual next token (the shift)
completion_mask = completion_mask[:, 1:]    # shift the mask the same way so it lines up with labels (1 = completion)
```

---

## 一个 LM 训练样本的张量解剖

```python
logits = model(input_ids).logits            # (B, L, V): a score for every vocab token, at every position
logits = logits[:, :-1, :]                  # drop the last position — its prediction has no next token to score
labels = input_ids[:, 1:]                   # the target at each position is just the actual next token (the shift)
completion_mask = completion_mask[:, 1:]    # shift the mask the same way so it lines up with labels (1 = completion)
log_probs = logits.log_softmax(dim=-1)      # normalize logits into log-probabilities over the vocab -> (B, L-1, V)
```

---

## 一个 LM 训练样本的张量解剖

```python
logits = model(input_ids).logits            # (B, L, V): a score for every vocab token, at every position
logits = logits[:, :-1, :]                  # drop the last position — its prediction has no next token to score
labels = input_ids[:, 1:]                   # the target at each position is just the actual next token (the shift)
completion_mask = completion_mask[:, 1:]    # shift the mask the same way so it lines up with labels (1 = completion)
log_probs = logits.log_softmax(dim=-1)      # normalize logits into log-probabilities over the vocab -> (B, L-1, V)
token_log_probs = log_probs.gather(-1, labels.unsqueeze(-1)).squeeze(-1)  # read off the log-prob of each TRUE next token -> (B, L-1)
```

---

## 一个 LM 训练样本的张量解剖

```python
logits = model(input_ids).logits            # (B, L, V): a score for every vocab token, at every position
logits = logits[:, :-1, :]                  # drop the last position — its prediction has no next token to score
labels = input_ids[:, 1:]                   # the target at each position is just the actual next token (the shift)
completion_mask = completion_mask[:, 1:]    # shift the mask the same way so it lines up with labels (1 = completion)
log_probs = logits.log_softmax(dim=-1)      # normalize logits into log-probabilities over the vocab -> (B, L-1, V)
token_log_probs = log_probs.gather(-1, labels.unsqueeze(-1)).squeeze(-1)  # read off the log-prob of each TRUE next token -> (B, L-1)
seq_log_probs = (token_log_probs * completion_mask).sum(dim=-1)           # zero out prompt/pad, then sum per sequence -> (B,)
```

**一个词元的移位** 是自回归步骤的字面实现：位置 $t$ 的 logits 预测词元 $t+1$。对词元级对数概率求和然后 `loss.backward()`——自动微分将这个求和转化为对应词元级梯度的求和。

---

## 后训练代码中常见的三种 mask

Mask 是 LLM 代码中沉默的 bug 藏身之处。三种不同的 mask 完成三种不同的工作：

- **因果 mask**（内置于解码器注意力中）——位置 $t$ 不能关注位置 $> t$ 的内容。这就是让模型自回归的原因；在训练代码中你永远不会去触碰它。
- **注意力 / 填充 mask**——告诉注意力机制忽略填充词元（将变长序列 batch 在一起时用到）。形状为 `(B, L)`。
- **完成 / 损失 mask**——仅在完成部分的词元处为 `1`；损失在它上面做乘法后再求和。**提示（prompt）词元用于条件化预测但不贡献损失。**

> 完成 mask 写错会导致两种灾难：要么在 prompt 上训练（把梯度浪费在你不能改变的词元上），要么在填充上训练（在噪声上训练）。

---

## 解码小复习

生成过程**在 $\pi_\theta$ 的分布中采样/搜索**——权重相同，但每次词元有多种选取方式：

- **贪婪解码**——每一步取 $\arg\max_v P_\theta(v \mid x_{<t})$。确定性强但短视：局部最优的词元可能导致整条序列失败。
- **束搜索（Beam search）**——按累积对数概率保留前 $b$ 条部分序列，展开并修剪到 $b$ 条。对低熵任务（翻译）效果很好，但对开放式文本则显得平庸。
- **温度采样**——$y_t \sim \mathrm{softmax}(z_t / T)$。较高的 $T$ → 更多样化，较低的 $T$ → 更趋近贪婪。
- **截断采样**——仅从 top-$k$ 词元中采样，或从累积质量 $\ge p$ 的最小词元集合中采样（top-$p$ / 核采样）。
- **前瞻搜索（MCTS 及类似方法）**——在做出决策之前用值/奖励模型对未来的模拟延续进行打分——与推理时推理（inference-time reasoning）同属解码阶段的技术。

关键区分：**分布** $\pi_\theta$ vs **采样它的过程**。

---

## 训练语言模型：交叉熵

在每个位置上，交叉熵将模型预测的分布与**真实**的下一个词元标签 $q_t$ 进行比较。该标签在真实词元 $x_t$ 处是一个*独热编码*（one-hot），因此对词表的求和坍缩为单个项：

$$H(q_t,\, P_\theta) = -\sum_{v \in \mathcal{V}} q_t(v)\,\log P_\theta(v \mid x_{<t}) = -\log P_\theta(x_t \mid x_{<t}).$$

因此，"与真实词元比较"仅仅是独热编码选出了一个对数概率。对位置求和、对数据平均就得到 LM 损失——等价于**负对数似然（NLL）**：

$$\mathcal{L}_{\text{LM}}(\theta) = -\,\mathbb{E}_{x \sim \mathcal{D}}\left[\sum_{t=1}^{T} \log P_\theta(x_t \mid x_{<t})\right].$$

"预测下一个词元"**就是**监督学习——标签只是序列中的下一个词元。

---

<!-- layout: section-break -->

## 优化与微调

---

## 梯度下降与训练循环

训练不断重复一个步骤：

$$\theta \leftarrow \theta - \eta \,\nabla_\theta \mathcal{L}(\theta).$$

- $\theta$ —— 模型参数，$\eta$ —— 学习率，$\nabla_\theta \mathcal{L}$ —— 损失的梯度
- **AdamW** 及相关自适应优化器是 LM 训练中的标准选择（自适应、带动量），而非纯粹的 SGD
- 训练以优化器**步骤 / token 数**来衡量；**epochs（轮次）**对于有限规模的微调数据集是一个有用的度量单位。学习率调度曲线的重要性不亚于学习率本身

基本的反向传播循环在预训练、中训练和微调之间是共享的——不同的是**mask 掩码、采样、批处理、数据构建和系统实现**，而不是优化器。

---

## 预训练 → 中训练 → SFT

预训练*末尾*的边界是模糊的，但对后训练极其重要：

- **预训练**——在大规模原始网页 / 代码数据上做下一个词元的交叉熵；**每一个**词元都对损失有贡献。
- **中训练（Mid-training）**——预训练末尾的退火 / 高质量数据阶段，在任何指令数据之前。此阶段数据质量逐步提升。它可被视为后训练的一部分，但通常不被讨论。
- **SFT（监督微调）**——仍然是交叉熵，但现在是在**指令–响应**对上，并带有**完成 mask**：只有响应词元对损失有贡献，prompt 仅用于条件化。模型学会的是*回应*，而不只是续写文本。

现代后训练流水线从一个**中训练**的检查点开始，因此本课程的故事实际上就是从那里开始的。

---

<!-- layout: section-break -->

## 概率论基础

---

## KL 散度（及熵）

**Kullback–Leibler 散度**衡量一个分布与另一个分布的差异：

$$\mathcal{D}_{\text{KL}}(p \,\|\, q) = \sum_i p_i \log \frac{p_i}{q_i}.$$

记住三点：

- **不对称**——$\mathcal{D}_{\text{KL}}(p\|q) \neq \mathcal{D}_{\text{KL}}(q\|p)$；方向很重要
- **非负**，且当且仅当 $p = q$ 时为 $0$
- **对齐的核心对象**：RLHF 中的 KL 惩罚项（Lectures 3–4）确保策略靠近其 SFT 起点，而 DPO 损失（Lecture 6）则是从一个 **KL-正则化的奖励最大化** 目标推导出来的

相关概念：**熵** $H(p) = -\sum_i p_i \log p_i$ 是分布的不确定性（均匀分布 = 高，尖峰分布 = 低）。它出现在这些系统的定义、推导和理解中，计算方法非常相似。

你将在几乎每一节对齐课程中看到 KL 散度。

---

## KL 散度（及熵）

三个量，一张信息论图景（以 *nats* 度量时使用 $\ln$，以 *bits* 度量时使用 $\log_2$）：

- **熵（Entropy）** $H(p) = -\sum_i p_i \log p_i$ —— 从 $p$ 中采样样本的平均惊讶程度；编码它们的不可约简成本。均匀分布 = 高，尖峰分布 = 低。
- **交叉熵（Cross-entropy）** $H(p, q) = -\sum_i p_i \log q_i$ —— 用为*错误*分布 $q$ 设计的码来编码来自 $p$ 的样本的成本。
- **KL 散度** $\mathcal{D}_{\text{KL}}(p \,\|\, q) = \sum_i p_i \log \frac{p_i}{q_i}$ —— 使用 $q$ 代替 $p$ 所带来的*额外*成本。

它们服从一个恒等式：

$$H(p, q) = H(p) + \mathcal{D}_{\text{KL}}(p \,\|\, q).$$

因此，最小化交叉熵**等价于**最小化与真相的 KL 散度——$H(p)$ 由数据固定。在 LM 训练中标签 $p$ 是独热编码，因此 $H(p)=0$，**交叉熵 = KL = NLL**。而在 RLHF 中，KL 项是作为*主动引入*的惩罚项加上的，用来保持策略靠近其参考分布。

> 译者补充：在信息论中，$H(p)$ 表示分布 $p$ 自身的不确定性（熵）。当 $p$ 是独热编码时，意味着某个事件以概率 1 发生，不确定性为零，所以 $H(p)=0$。因此最小化交叉熵 $H(p,q)$ 等价于最小化 KL 散度，而 KL 散度衡量的是两个分布之间的距离。

---

## KL 散度（及熵）

对序列而言，KL 背后的求和是不可计算的——但 KL 是一个**期望**，因此可以通过**蒙特卡洛**估计：从策略中抽取样本，对 log-ratio 取平均。

$$\mathcal{D}_{\text{KL}}(\pi_\theta \,\|\, \pi_{\text{ref}}) = \mathbb{E}_{x \sim \pi_\theta}\!\left[\log \frac{\pi_\theta(x)}{\pi_{\text{ref}}(x)}\right] \approx \frac{1}{N}\sum_{i=1}^{N} \log \frac{\pi_\theta(x_i)}{\pi_{\text{ref}}(x_i)}.$$

- 被积项就是你已经生成的每条 rollout 上的**对数概率比**。
- 朴素平均（$\hat k_1 = \log\frac{\pi_\theta}{\pi_{\text{ref}}}$）无偏但方差大，且在有限样本中可能为负。
- RLHF 使用的是方差低、始终 $\ge 0$ 的 **$k_3$ 估计量** $\hat k_3 = r - 1 - \log r$，其中 $r = \tfrac{\pi_{\text{ref}}}{\pi_\theta}$ [@schulman2020klapprox]。

这是信息论的实践面貌：**从样本中近似目标分布**，以方差换取不可计算的求和。

---

## Sigmoid 与成对似然

偏好（"响应 $y_w$ 优于 $y_l$"）是一个**二元**结果，因此分数差通过一个 **sigmoid** 挤压为概率：

$$\sigma(z) = \frac{1}{1+e^{-z}}, \qquad P(y_w \succ y_l \mid x) = \sigma\!\left(r(x,y_w) - r(x,y_l)\right).$$

识别三点：

- sigmoid 将**分数差**转换为二元概率
- 只有**相对**的奖励差才有意义——同时将两个奖励加上一个常数不会改变任何结果
- $-\log \sigma(\cdot)$ 就是**二元负对数似然**

**Lecture 2 完整推导了这个 Bradley–Terry 模型** 来训练奖励模型；**Lecture 6 在 DPO 内部复用了完全相同的 $\sigma(\Delta r)$ 形状**。

---

<!-- layout: section-break -->

## 强化学习建模

---

## 语言模型作为一个 MDP

强化学习研究一个智能体在**马尔可夫决策过程**（Markov decision process, MDP）$(\mathcal{S}, \mathcal{A}, P, r, \gamma)$ 中行动：

| MDP 概念 | 语言模型 |
|-------------|---------------|
| 状态 $s_t$ | prompt + 已有词元：$(x, y_{<t})$ |
| 动作 $a_t$ | 下一个词元 $y_t$ |
| 转移 $P$ | 确定性：追加该词元 |
| 策略 $\pi_\theta(a_t \mid s_t)$ | LM 的下一个词元分布 |
| 奖励 $r$ | 通常为**终端**：RM 分数或验证器输出 |
| 折扣因子 $\gamma$ | 通常为 $1.0$（不折扣） |

策略就是 LM，按词元分解：

$$\pi_\theta(y \mid x) = \prod_t \pi_\theta(y_t \mid x, y_{<t}).$$

---

## RL 的目标，以及为什么用于语言模型

RL 的目标是选择策略参数 $\theta$，以在策略自身的期望下最大化**期望奖励**：

$$J(\theta) = \mathbb{E}_{y \sim \pi_\theta}[R(x, y)].$$

一个人类偏好（或一个验证器）是整条响应*末尾*的一个标量：

- **稀疏**——整条响应只有一个标签，而非每个词元一个
- **延迟**——一个词元的质量取决于整个完成
- **没有词元级标签**——且普通梯度无法通过离散采样的词元回传

因此，对于"偏好"不存在交叉熵标签。策略梯度本身就是在优化期望的评估器分数——先是通过*学习*该信号作为奖励模型，然后通过*优化*它。这就是 RLHF 的整个动机。

---

## 这些工具变成了后训练

本幻灯片中的一切都是基础工具——**概率、损失、梯度和采样**。后训练就是你把这些工具指向一个预训练模型、并获得比原始下一个词元预测更丰富的反馈时所产生的东西：

- **示范**（"生成这个响应"）→ 监督微调
- **偏好**（"让这个响应比那个响应更可能出现"）→ 奖励建模或偏好优化（DPO）
- **奖励**（"采样那些得分高的响应"）→ 强化学习（PPO、GRPO、RLVR）
- **约束**（"不要偏离起始位置太远"）→ 正则化，尤其是 KL 惩罚

不同的数据和不同的目标函数；但它们共享同一个底层目标：

> **将模型的响应分布朝我们希望的行为方向改变。**

这正是本课程剩余部分的主题。

---

## 如果哪些觉得生疏了：

- **RL**——Sutton & Barto, *Reinforcement Learning: An Introduction*；David Silver 的 UCL 课程；UC Berkeley CS285
- **从零构建语言模型**——Sebastian Raschka, *Build a Large Language Model (From Scratch)*
- **本书自己的参考**——附录 A（术语表）涵盖了贯穿全书的语言建模概述、KL 和 RL 词汇

可以深入 rabbit holes，跳过章节阅读，追逐让你感兴趣的东西——本课程的设计就是为此而建的。
