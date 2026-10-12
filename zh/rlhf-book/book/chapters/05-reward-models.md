<!--
  Copyright (c) 2025-2026 Nathan Lambert.
  Licensed under CC BY-NC-SA 4.0:
  https://creativecommons.org/licenses/by-nc-sa/4.0/
  Full license: https://github.com/natolambert/rlhf-book/blob/main/LICENSE-CHAPTERS
-->
---
prev-chapter: "Instruction Fine-Tuning"
prev-url: "04-instruction-tuning"
page-title: 奖励模型
search-title: "第五章：奖励模型"
meta-description: "如何从偏好数据中训练奖励模型，并将其作为学习到的目标用于 RLHF 后训练流水线。"
next-chapter: "Reinforcement Learning"
next-url: "06-policy-gradients"
lectures:
  - video: "https://www.youtube.com/watch?v=4gIwiSPmQkU&list=PLL1tdVxB1CpVpEtMHxwuR4uI4Lxjw00_y&index=3"
    label: "讲座 2：IFT、奖励模型、拒绝采样（第 4、5、9 章）"
---

# 奖励模型

奖励模型是现代化 RLHF（基于人类反馈的强化学习）方法的核心——它们负责学习复杂的人类偏好。
它们使我们的模型能够从不便于精确指定的信号中进行学习。
它们将数据中复杂的特征压缩为一种可在下游训练中使用的表示——这再次展现了现代深度学习那令人惊叹的表达能力。
在后续章节研究的优化过程中，这些模型充当了核心优化的代理目标（proxy objectives）。
如图 @fig:rm-role-in-rlhf 所示，奖励模型在 RLHF 中所扮演的角色，类似于标准强化学习中返回奖励的环境组件；但与固定的环境不同，我们可以从人类偏好中学习并控制这个奖励函数。

在历史上，奖励模型曾被广泛用于强化学习研究中，作为环境奖励的代理 [@sutton2018reinforcement]。
奖励模型最初以现代形式被提出，是用来研究价值对齐（value alignment）问题的工具 [@leike2018scalable]。
这类模型通常接收某种形式的输入，并输出一个单一的标量奖励值。
奖励可以表现为多种形式——在传统 RL 问题中，它尝试逼近环境中该问题的精确奖励；但在 RLHF 中，我们会看到奖励模型实际上输出的是一种概率——即某个输入属于"高质量"的概率（即在成对偏好关系中"被选择"的答案）。

RLHF 中的奖励建模做法与逆强化学习（inverse reinforcement learning）密切相关——在该领域中，问题是从行为轨迹中逼近智能体的奖励函数 [@ng2000algorithms]，以及深度强化学习的其他分支。
它们的高层问题陈述是相同的，但实现方式和研究重点完全不同，因此它们通常被视为完全不同的研究领域。

最常见的奖励模型通常被称为 Bradley-Terry 奖励模型，也是本章的主要关注点，它预测一段文本在训练比较中接近"偏好文本"的概率。
在本节后续，我们还将它与结果奖励模型（Outcome Reward Models, ORM）、过程奖励模型（Process Reward Models, PRM）以及其他类型的奖励模型进行比较。

*在整章中，我们使用 $x$ 表示 prompt（提示），$y$ 表示 completion（补全）。这种记法在语言模型文献中很常见，其中方法作用于完整的 prompt-completion 对，而非逐个 token 操作。*

![奖励模型在 RLHF 中扮演标准 RL 中返回奖励的环境组件角色。关键区别在于，在 RLHF 中，我们可以从人类偏好中学习和控制这个奖励函数，而不是由环境固定。](images/rlhf-overview.png){#fig:rm-role-in-rlhf}

## 训练 Bradley-Terry 奖励模型

奖励模型的标准实现源于偏好关系的 Bradley-Terry 模型 [@BradleyTerry]。
有**两种**流行的表达方式用于训练标准 RLHF 奖励模型——它们在数学上是等价的。

首先，Bradley-Terry 偏好模型定义了在一对物品 $i$ 和 $j$ 的比较中，评估者偏好 $i$ 超过 $j$ 的概率：

$$P(i > j) = \frac{p_i}{p_i + p_j}.$$ {#eq:bradterry}

Bradley-Terry 模型假设每个物品有一个潜在的强度 $p_i > 0$，而观察到的偏好只是这些潜在强度的有噪反映。
常用的做法是使用无界分数对 Bradley-Terry 模型进行参数化，其中 $p_i = e^{r_i}$，由此得到以下形式：

$$P(i > j) = \frac{e^{r_i}}{e^{r_i} + e^{r_j}} = \sigma(r_i-r_j).$$ {#eq:bradterry_unbounded}

其中 $\sigma(z) = \frac{1}{1 + e^{-z}}$ 是逻辑函数（sigmoid 函数），因此偏好概率仅依赖于分数差 $r_i - r_j$。
只有分数的差值有意义：给每个 $r_k$ 加上相同的常数 $c$ 不会改变 $P(i > j)$。
这些形式对人类偏好提供了一种实用的近似，在 RLHF 中通常效果很好。

要训练奖励模型，我们必须构造一个满足上述关系的损失函数。
在实践中，这通过将语言模型转换为输出标量分数的模型来实现——通常是通过在语言模型最后一个隐藏状态上附加一个小型线性层（head），从中产生一个单一的奖励值。
给定 prompt $x$ 和两个采样补全 $y_1$ 和 $y_2$，我们用奖励模型 $r_\theta$ 对两者打分，并将条件分数记为 $r_\theta(y_i \mid x)$。

奖励模型分配给 $y_1$ 优于 $y_2$ 的概率变为：

$$P(y_1 > y_2 \mid x) = \frac{\exp\left(r_\theta(y_1 \mid x)\right)}{\exp\left(r_\theta(y_1 \mid x)\right) + \exp\left(r_\theta(y_2 \mid x)\right)}.$$ {#eq:bradterryrm}

我们将"被选择"的偏好补全记为 $y_c$（chosen），将被拒绝的补全记为 $y_r$（rejected）。

接下来的损失函数会鼓励奖励模型对人类偏好的补全给出更高的分数，用 sigmoid 将分数差转换为概率。
@eq:bradterryrm 中的偏好似然（likelihood）是起点。我们首先通过将分子和分母同时除以 $\exp\left(r_\theta(y_c \mid x)\right)$ 将该似然改写为 sigmoid 形式：

$$
\begin{aligned}
P(y_c > y_r \mid x)
&= \frac{\exp\left(r_\theta(y_c \mid x)\right)}{\exp\left(r_\theta(y_c \mid x)\right) + \exp\left(r_\theta(y_r \mid x)\right)} \\
&= \frac{\exp\left(r_\theta(y_c \mid x)\right)}{\exp\left(r_\theta(y_c \mid x)\right)\left(1 + \frac{\exp\left(r_\theta(y_r \mid x)\right)}{\exp\left(r_\theta(y_c \mid x)\right)}\right)} \\
&= \frac{1}{1 + \frac{\exp\left(r_\theta(y_r \mid x)\right)}{\exp\left(r_\theta(y_c \mid x)\right)}} \\
&= \frac{1}{1 + \exp\left(-(r_\theta(y_c \mid x) - r_\theta(y_r \mid x))\right)} \\
&= \sigma \left( r_\theta(y_c \mid x) - r_\theta(y_r \mid x) \right).
\end{aligned}
$$ {#eq:bradterryrm_sigmoid}

然后，通过对偏好数据集 $D$ 做极大似然拟合（maximum likelihood）来训练奖励模型——最大化观察到偏好的对数似然的期望。
由于对数函数是单调递增的，这等价于最小化期望负对数似然（negative log-likelihood）：

$$
\begin{aligned}
\theta^* &= \arg\max_\theta \mathbb{E}_{(x, y_c, y_r) \sim D}\left[ \log P(y_c > y_r \mid x) \right] \\
&= \arg\min_\theta \mathbb{E}_{(x, y_c, y_r) \sim D}\left[ -\log \sigma \left( r_\theta(y_c \mid x) - r_\theta(y_r \mid x) \right) \right].
\end{aligned}
$$ {#eq:bradterryrm_deriv}

在数据集上求期望**之前**先取对数，这才使得负对数似然损失成为正确的目标：最大化期望概率 $\mathbb{E}[P]$ 并不等于最大化期望对数概率 $\mathbb{E}[\log P]$。

逐样本损失（per-example loss）是上述期望内的 log-sigmoid 表达式，如 [@ouyang2022training] 以及其他工作所示：
$$\mathcal{L}(\theta) = - \log \left( \sigma \left( r_{\theta}(y_c \mid x) - r_{\theta}(y_r \mid x) \right) \right)$$ {#eq:rewardmodeling1}

另一种在数学上等价的表达式使用 softplus 函数 $\log(1+e^x)$，如 [@askell2021general] 及其他工作所示：
$$\mathcal{L}(\theta) = \log \left( 1 + e^{r_{\theta}(y_r \mid x) - r_{\theta}(y_c \mid x)} \right)$$ {#eq:rewardmodeling2}

二者等价的原因在于：令 $\Delta = r_{\theta}(y_c \mid x) - r_{\theta}(y_r \mid x)$，利用 $\sigma(\Delta) = \frac{1}{1 + e^{-\Delta}}$ 可得 $-\log\sigma(\Delta) = \log(1 + e^{-\Delta}) = \log\left(1 + e^{r_{\theta}(y_r \mid x) - r_{\theta}(y_c \mid x)}\right)$。
这两种形式都出现在 RLHF 文献中。

![训练偏好奖励模型需要成对的被选择与被拒绝的补全。模型基于序列级表示（通常是 end-of-sequence (EOS) token 的隐藏状态）为每个补全计算标量分数，对比损失仅依赖于两个分数之差。](images/pref_rm_training.png){#fig:pref_rm_training data-dark-src="images/pref_rm_training-dark.png"}

### 默认奖励模型架构

实现奖励模型最常用的方式是使用类似 Transformers 库中 `AutoModelForSequenceClassification` 的抽象——在语言模型上附加一个小型线性层，对每个 prompt-completion 对在训练或推理时产生一个标量奖励分数。
在推理时，模型从该线性层输出一个单一 logit，表示这段文本"被选择"的*相对概率*。

也存在其他实现方式——例如直接从最终嵌入（embeddings）上取一个线性层——但这些在开源工具中较少使用。

### 实现示例

实现奖励建模的损失函数非常简单。
更复杂的实现挑战在于搭建一个独立的数据加载器和推理流水线。
在有了正确的 dataloader（包含带 tokenized prompt 以及对应的 chosen 和 rejected 补全）的情况下，损失函数实现如下：
```python
import torch.nn as nn
# inputs_chosen / inputs_rejected include the prompt tokens x and the respective
# completion tokens (y_c or y_r) that the reward model scores jointly.
rewards_chosen = model(**inputs_chosen)
rewards_rejected = model(**inputs_rejected)

loss = -nn.functional.logsigmoid(rewards_chosen - rewards_rejected).mean()
```

从更大的图景来看，这通常是在一个因果语言模型（causal language model，即逐 token 从左到右生成、在预测每个 token 时以所有先前 token 为条件的模型）的基础上，额外添加一个 head（并使用上述损失进行训练），将最终的隐藏状态映射为输入分数。
该代码接收标准的 transformer 输入——`input_ids`（tokenized 文本）和 `attention_mask`（标记真实 token 与 padding）——并从最后一个真实 token 处提取隐藏状态（模型对输入的内在表示），然后将其通过一个线性层产生标量奖励。
该模型的结构如下：

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class BradleyTerryRewardModel(nn.Module):
    """
    Standard scalar reward model for Bradley-Terry preference learning.

    Usage (pairwise BT loss):
        rewards_chosen = model(**inputs_chosen)    # (batch,)
        rewards_rejected = model(**inputs_rejected)  # (batch,)
        loss = -F.logsigmoid(rewards_chosen - rewards_rejected).mean()
    """
    def __init__(self, base_lm):
        super().__init__()
        self.lm = base_lm  # e.g., AutoModelForCausalLM
        self.head = nn.Linear(self.lm.config.hidden_size, 1)

    def _sequence_rep(self, hidden, attention_mask):
        """
        Get a single vector per sequence to score.
        Default: last non-padding token (EOS token); if no mask, last token.
        hidden: (batch, seq_len, hidden_size)
        attention_mask: (batch, seq_len)
        """

        # Index of last non-pad token in each sequence
        # attention_mask is 1 for real tokens, 0 for padding
        lengths = attention_mask.sum(dim=1) - 1  # (batch,)
        batch_idx = torch.arange(hidden.size(0), device=hidden.device)
        return hidden[batch_idx, lengths]  # (batch, hidden_size)

    def forward(self, input_ids, attention_mask):
        """
        A forward pass designed to show inference structure of a standard reward model.
        To train one, this function will need to be modified to compute rewards from both
         chosen and rejected inputs, applying the loss above.
        """
        outputs = self.lm(
            input_ids=input_ids,
            attention_mask=attention_mask,
            output_hidden_states=True,
            return_dict=True,
        )
        # Final hidden states: (batch, seq_len, hidden_size)
        hidden = outputs.hidden_states[-1]

        # One scalar reward per sequence: (batch,)
        seq_repr = self._sequence_rep(hidden, attention_mask)
        rewards = self.head(seq_repr).squeeze(-1)

        return rewards
```

在本节及后续内容中，奖励模型（以及大部分后训练任务）的实现复杂度主要集中在正确构建数据加载器和分布式学习系统上。
注意，训练奖励模型时最常见的做法是仅训练 1 个 epoch，以避免过拟合。

## 结果奖励模型（Outcome Reward Models）

<!-- Huge thanks to Hangliang Ren, graduate student at Northeastern University for helping with this section (and PRMs), see https://github.com/myhott163com/RLHF_ORM_PRM -->

大多数针对语言模型和其他 AI 系统的*偏好微调*（preference tuning）都使用上文讨论的 Bradley-Terry 模型。
对于推理密集型任务，可以使用结果奖励模型（Outcome Reward Model, ORM）。
ORM 的训练数据构造方式与标准偏好微调类似。
此处我们有一个问题陈述或 prompt，$x$，以及两个补全 $y_1$ 和 $y_2$。
这里使用的归纳偏置（inductive bias）是：一个补全应该是问题的正确答案，另一个是不正确的，从而得到 $(y_c, y_{ic})$。

在继续之前，需要特别说明的是：结果奖励模型在后训练文献中是一个相对小众的领域，我们引用的关键论文在实现细节上存在微妙差异。
核心思想是学习一个逐 token 的信号，用来评估补全最终得出正确答案的可能性，但不同时期出现了不同的训练方法和架构。

所用模型架构与标准奖励模型非常相似——都是在一个可以输出单一 logit 的模型（对于 RM 而言）上附加一个线性层——但 ORM 的训练目标稍有不同。
首先，让我们拆解原始 GSM8K 论文（一项研究小学算术的流行基准测试）[@cobbe2021gsm8k] 中的内容——这篇论文提出了后来成为 ORM 的核心思想，但当时尚未命名。我们从架构入手，参见第 4.3 节：

> 我们可以训练验证器基于整个生成解做单一的标量预测，也可以在解中每个 token 之后做标量预测。
> 默认情况下，我们选择后者，训练验证器在每生成一个 token 后做出预测。

这正是结果奖励模型的默认实现与 Bradley-Terry 模型分道扬镳的地方——它们在每一个 token 上做出预测。
作者评论说，逐 token 信息可以是"一种有用的辅助信号，鼓励模型在整段推理过程中进行判断"，而不仅仅是预测最终结果（这与其名称"结果奖励模型"多少有些反直觉）。继续引用附录 E：

> 我们以联合目标训练验证器：模型除了学习原始的语言建模目标外，还要学习将模型补全标注为正确或不正确。
> 从架构上看，我们的验证器是语言模型，附加了一个小型标量 head，能够逐 token 输出预测。
> 我们将该标量 head 实现为一个单独的偏置（bias）参数和一个增益（gain）参数，作用于语言模型最终 unembedding 层输出的 logits。

翻译过来，这实现为一个小型 head，在每个 token 上输出一个标量 logit，而不是传统 RM 中为整个序列输出一个 logit 的分类 head。
另外，在原始的 GSM8K 论文中，作者联合训练了 ORM 与下一个 token 的语言建模损失——这种做法后来并未成为默认方式。

"outcome-reward model"（结果奖励模型）一词出现在 2022 年，在一篇比较"outcome-supervised RM（ORM）"与过程奖励模型（预测推理质量的模型）的论文中 [@uesato2022solving]——这是一个重要的补充：这是实现 ORM 的另一种方式，即把二元 `correct` 或 `incorrect` 标记映射到 LLM 的分词器词表中，作为步级（step-level）信号，而非学习一个单独的标量 head 来逐 token 预测正确性。

本书所采用的标准实现来自论文 *Let's Verify Step by Step* [@lightman2023let]，其中结果奖励模型训练的是一个逐 token 的预测器，使用交叉熵损失来判断答案是否正确。

形式上，逐 token 损失在每个补全 token 上施加二元交叉熵，每个 token 关联的结果概率被训练为逼近该序列的结果标签：

$$\mathcal{L}_{\text{token}}(\theta) = -\mathbb{E}_{(s,r)\sim \mathcal{D}}\left[\frac{1}{T}\sum_{t=1}^{T} \left( r\log p_\theta(s_t) + (1-r)\log\left(1-p_\theta(s_t)\right) \right)\right]$$ {#eq:orm_token_loss}

其中 $s$ 是 $T$ 个 token 组成的补全，$r \in \{0,1\}$ 是二元标签，1 表示对给定 prompt 的正确答案，0 表示错误答案，而 $p_\theta(s_t) = \sigma(w_\theta(s_t))$ 是从模型标量 logit $w_\theta(s_t)$ 在 token $t$ 预测的正确性概率。

一种更简化的 ORM 形式，参见 [@lyu2025exploring]，采用序列级交叉熵损失，模型在推理时仍然用于逐 token 输出：

$$\mathcal{L}_{\text{CE}}(\theta) = -\mathbb{E}_{(s,r)\sim \mathcal{D}}\left[r\log \bar{p}_\theta(s) + (1-r)\log(1-\bar{p}_\theta(s))\right]$$ {#eq:orm_loss}

其中 $r \in \{0,1\}$ 是二元标签，1 表示正确答案，0 表示错误答案，而 $\bar{p}_\theta(s) = \sigma\left(\frac{1}{T}\sum_{t=1}^{T} w_\theta(s_t)\right)$ 将逐 token logits 的均值压缩为一个表示整个补全正确的概率——注意，这里不是逐 token 概率的平均，因为 sigmoid 函数是在池化（pooling）之后应用的。
在代码中，这个结果标签会被复制到每个补全 token 上，而 prompt token 会被 mask 掉（用 `-100`），因此不参与损失计算。

实现一个结果奖励模型（以及我们将在后面看到的过程奖励模型等其他类型）涉及在补全是否为正确样本的基础上逐 token 施加交叉熵损失。
这与语言建模损失非常接近——它不需要标准 Bradley-Terry 奖励模型所要求的"chosen-rejected"成对结构。
在下面的简化 ORM 训练设置中，我们没有采样新 token，也没有在下一个 token 预测上训练 LLM；我们只需将固定的 prompt-completion 序列通过 backbone，然后训练 ORM head 去预测正确性标签。

模型结构可以如下所示：

```python
import torch.nn as nn
import torch.nn.functional as F

class OutcomeRewardModel(nn.Module):
    def __init__(self, base_lm):
        super().__init__()
        self.lm = base_lm  # e.g., AutoModelForCausalLM
        self.head = nn.Linear(self.lm.config.hidden_size, 1)

    def forward(self, input_ids, attention_mask=None, labels=None):
        """
        input_ids contains a full prompt+completion sequence.
        labels is token-aligned: prompt tokens are -100, and each completion
         token repeats the sequence outcome label (1=correct, 0=incorrect).
        If labels=None, this is an inference-only forward pass and the loss is
         returned as None.
        """
        outputs = self.lm(
            input_ids=input_ids,
            attention_mask=attention_mask,
            output_hidden_states=True,
            return_dict=True,
        )
        # Final hidden states: (batch, seq_len, hidden_size)
        hidden = outputs.hidden_states[-1]
        # One scalar logit per token: (batch, seq_len)
        logits = self.head(hidden).squeeze(-1)

        # Inference-only forward pass: no loss is computed.
        if labels is None:
            return None, logits
        # Only compute loss on completion tokens (labels 0 or 1)
        # Prompt tokens have labels = -100
        mask = labels != -100
        loss = None
        if mask.any():
            loss = F.binary_cross_entropy_with_logits(
                logits[mask], labels[mask].float()
            )
        else:
            loss = logits.sum() * 0
        return loss, logits
```

一个简化的损失实现如下：

```python
# Feed the full prompt+completion sequence once; no token sampling happens here.
# Assume model already has: model.lm (backbone) + model.head
hidden = model.lm(**inputs, output_hidden_states=True).hidden_states[-1]
logits_per_token = model.head(hidden).squeeze(-1)  # (batch, seq_len)
# This will sometimes be compressed as model.forward() in other implementations

# Binary labels: 1=correct, 0=incorrect (prompt tokens masked as -100)
mask = labels != -100
loss = F.binary_cross_entropy_with_logits(
    logits_per_token[mask], labels[mask].float()
)
```

这里的关键直觉是：ORM 会在序列中的每个 token 输出一个正确性概率（判断仅基于最终答案——推理过程中的错误不会被 ORM 训练捕捉到）。
这个过程可能会有噪声，因为更新和损失的传播取决于 token 级别的结果和注意力映射。

![在推理时，结果奖励模型在补全 token 上输出逐 token 的正确性概率。prompt token 在评分时被忽略，补全概率可以聚合为响应级分数，用于验证、过滤或重排。](images/orm_inference.png){#fig:orm_inference data-dark-src="images/orm_inference-dark.png"}

![训练结果奖励模型使用来自验证器或数据集的离线标签（例如，正确补全全部为 1）。每个补全 token 使用二元交叉熵与结果标签进行训练，逐 token 概率聚合为最终分数，用于验证、过滤或重排。](images/orm_training.png){#fig:orm_training data-dark-src="images/orm_training-dark.png"}

这些模型一直沿用至今，但在开源 RLHF 工具中的支持较少。
例如，开创性工作 *Let's Verify Step by Step* [@lightman2023let] 也使用了同类型的 ORM，但去掉了 Cobbe et al. 2021 中损失函数的语言建模预测部分。
最终的损失是每个 token 上的交叉熵损失，用于预测最终答案是否正确。

由于支持不足，"结果奖励模型"（ORM）这一术语已经被用于多种方式。
一些文献，如 [@lyu2025exploring]，仍然受到 Cobbe et al. 2021 原始定义的影响；另一些则更广泛地将其用于任何被训练用来预测补全是否正确的验证器。

## 过程奖励模型（Process Reward Models）

过程奖励模型（Process Reward Models, PRMs），最初被称为过程监督奖励模型，是在链式推理（chain-of-thought）过程中的每一个*步骤*输出分数的奖励模型。
它们与标准 RM（仅在 EOS token 处输出一个分数）和 ORM（在每个 token 处输出一个分数）不同。
过程奖励模型需要在每个推理步骤结束时获得监督信号，然后以类似的方式训练：步骤中的 token 被训练为对应的目标——PRM 的目标是步骤级别的，而 ORM 的目标是整个响应。

遵循 [@lightman2023let]，二元标注的 PRM 通常以逐步骤交叉熵损失进行优化：

$$\mathcal{L}_{\text{PRM}}(\theta) = - \mathbb{E}_{(x, s) \sim \mathcal{D}} \left[ \sum_{i=1}^{K} y_{s_i} \log r_\theta(s_i \mid x, s_{< i}) + (1 - y_{s_i}) \log \left(1 - r_\theta(s_i \mid x, s_{< i})\right) \right] $$ {#eq:prm_loss}

其中 $s$ 是有 $K$ 个标注步骤的采样链式推理，$y_{s_i} \in \{0,1\}$ 表示第 $i$ 步是否正确，而 $r_\theta(s_i \mid x, s_{< i})$ 是 PRM 在给定原始 prompt $x$ 和之前所有步骤 $s_{< i}$ 条件下，预测第 $i$ 步有效的概率。

以下是 Hugging Face 的 TRL（Transformer Reinforcement Learning）[@vonwerra2022trl] 中如何将这种逐步骤标签封装到 trainer 中的示例：

```python
# Get the ID of the separator token and add it to the completions
separator_ids = tokenizer.encode(step_separator, add_special_tokens=False)
completions_ids = [completion + separator_ids for completion in completions_ids]

# Create the label 
labels = [[-100] * (len(completion) - 1) + [label] for completion, label in zip(completions_ids, labels)]
```

传统上，PRM 使用语言建模 head 进行训练，仅在推理步骤结束时输出一个 token——例如在双换行或另一个特殊 token 处。
这些预测通常为：-1 表示错误、0 表示中立、1 表示正确。
这些标签不一定表示模型是否走在正确的路径上，而是表示该步骤本身是否正确。

![过程奖励模型仅在步骤边界（如换行 token）处提供监督。每个步骤获得一个 3 类标签：正确（+1）、中立（0）或错误（-1）。所有其他 token 在训练时被 mask。](images/prm_training_inference.png){#fig:prm_training_inference data-dark-src="images/prm_training_inference-dark.png"}

下面展示一个 PRM 的构造示例。

```python
import torch.nn as nn
import torch.nn.functional as F

class ProcessRewardModel(nn.Module):
    def __init__(self, base_lm, num_classes=3):
        super().__init__()
        self.lm = base_lm  # e.g., AutoModelForCausalLM
        self.head = nn.Linear(self.lm.config.hidden_size, num_classes)

    def forward(self, input_ids, attention_mask=None, labels=None):
        """
        The inputs are tokenized prompts and completions, where the end of a
         "reasoning step" is denoted by a designated separator token such as a
         newline or other special marker rather than batch padding.
        labels will be a list of labels, True, False, and Neutral (3 labels) which
         will be predicted by the model.
        If labels=None, this is an inference-only forward pass and the loss is
         returned as None.
        """
        outputs = self.lm(
            input_ids=input_ids,
            attention_mask=attention_mask,
            output_hidden_states=True,
            return_dict=True,
        )
        # Final hidden states: (batch, seq_len, hidden_size)
        hidden = outputs.hidden_states[-1]
        # One logit vector per token: (batch, seq_len, num_classes)
        logits = self.head(hidden)

        # Inference-only forward pass: no loss is computed.
        if labels is None:
            return None, logits
        # Only compute loss at step boundaries (where labels != -100)
        # Labels map: -1 -> 0, 0 -> 1, 1 -> 2 (class indices)
        mask = labels != -100
        loss = None
        if mask.any():
            loss = F.cross_entropy(
                logits[mask], labels[mask]
            )
        else:
            loss = logits.sum() * 0
        return loss, logits
```

核心损失函数看起来与结果奖励模型非常相似，差别仅在于标签应用的时间间隔不同。

```python
# Assume model outputs 3-class logits per token
hidden = model.lm(**inputs, output_hidden_states=True).hidden_states[-1]
logits = model.head(hidden)  # (batch, seq_len, 3)

# 3-class labels at step boundaries only: 0=-1, 1=0, 2=1 (others masked as -100)
mask = labels != -100
loss = F.cross_entropy(logits[mask], labels[mask])
```

## 比较不同类型的奖励模型（及价值函数）

上述各类奖励模型展示了在 RLHF 及其他后训练方法中衡量"质量"的多种方式。
以下是一个关于各类模型预测内容和训练方式的小结。

::: {.table-wrap}
| 模型类别 | 预测内容 | 训练方式 | 语言模型结构 |
|------------|------------------|---------------------|--------------|
| **奖励模型（RM）** | 序列级质量分数 $r_\theta(x, y)$ | 对比损失：对同一 prompt 的各个补全进行成对（或 N 向）比较 | 在 EOS/最后一个 token 的隐藏状态上附加线性层 |
| **结果奖励模型（ORM）** | 每个 token 上答案为正确的概率 | 标注好的结果标签（如可验证领域中的成功/失败）；每个样本独立标注，无需成对比较 | 逐 token 二元交叉熵 head；标签重复结果标签 |
| **过程奖励模型（PRM）** | 推理步骤结束时的奖励或分数 | 使用中阶反馈或逐步标注训练（在推理步骤的每个 token 上训练） | 逐 token head，预测步骤正确性（-1、0、1） |
| **价值函数（Value Functions）** | 给定当前状态下的期望回报 | 通过回归到序列中的每个点来训练 | 带有逐 token 输出的标量回归 head |

表：奖励模型类型比较。 {#tbl:rm_compare}
:::

关于上表中各类型的区别，有几点需要注意——模型类型之间的边界并不总是泾渭分明：

- 在偏好微调和推理训练中，价值函数的折扣因子往往为 1，这使得价值函数甚至更接近结果奖励模型，但训练损失不同。
- PRM 可以通过从中间状态执行 rollout 并收集结果数据来进行监督。这混合了多种思想，但如果*损失函数*使用的是逐推理步骤的标签，则它更应被称为 PRM。

**如果你对 Bradley-Terry 成对模型使用"正确/错误"对进行训练，会发生什么？**
许多关于 ORM 的混淆来自一小部分文献——它们使用从答案正确性派生的成对数据训练奖励模型。
在这种情况下，你将正确答案设置为选定响应（chosen），将同一问题的错误答案设置为被拒绝响应（rejected）。
从技术上讲，这并非 ORM，仍然直接使用对比式序列级损失进行训练。
这仍然是 Bradley-Terry 模型，归入我们讨论的第一类模型。

**ORM 与价值函数的区别。**
ORM 和价值函数可能看起来很相似，因为两者都使用相同的 head 架构产生逐 token 输出，但它们在*预测内容*和*目标来源*上有所不同：

- **ORM** 在每个 token 上预测补全是否最终以正确答案结束。目标来自*离线标签*（一个验证器或数据集将序列标注为正确或不正确），并被广播到每个中间 token 用于训练。
- **价值函数** 预测期望的*剩余*回报：$V(s_t) = \mathbb{E}\left[\sum_{k \geq t} \gamma^{k-t} r_k \mid s_t\right]$。目标通常*从当前策略 $\pi_\theta$ 下的同策略 rollout 中计算*，并会随着策略的变化而变化（从技术上讲，价值函数也可以离策略训练，但在语言建模领域这尚未确立）。

如果你定义一个密集 token 奖励 $r_t = \mathbb{1}[\text{token 正确}]$ 并使用 $\gamma = 1$，那么 ORM 在学习 $r_t$（或 $p(r_t = 1)$），而价值 head 在学习剩余求和 $\sum_{k \geq t} r_k$。
它们可以共享相同的基座模型和 head 维度，但*语义和监督流水线*不同：ORM 从固定标签进行离线训练，而价值函数是同策略训练，并用于计算策略梯度的优势 $A_t = \hat{R}_t - V_t$。

### 各类型奖励模型的推理方式

这些模型在推理时（训练完成后）以不同方式处理数据，以应对 RM 用于的多种任务。

**Bradley-Terry RM（偏好模型）：**

- *输入：* prompt $x$ + 候选补全 $y$
- *输出：* 单一标量 $r_\theta(x, y)$，来自 EOS/最后一个 token 的隐藏状态的线性层
- *用途：* 对 $k$ 个补全重排序，选取 top-1（best-of-N 采样）；或为 RLHF 提供终端奖励
- *聚合：* 标量输出不需要聚合

**Outcome RM：**

- *输入：* prompt $x$ + 补全 $y$
- *输出：* 补全 token 上的逐 token 概率 $p_t \approx P(\text{最终答案正确} \mid y_{\leq t})$
- *用途：* 对已完成候选者打分；通过均值、最小值（尾部风险）或乘积 $\prod_t p_t$（等价于 log-probability 求和 $\sum_t \log p_t$）聚合
- *聚合选择：* 平均正确性、最小 $p_t$、最后 $m$ 个 token 的平均值，或对任何 $p_t < \tau$ 进行阈值标记

**Process RM：**

- *输入：* prompt $x$ + 带步骤边界的推理轨迹
- *输出：* 步骤边界的分数（如正确/中立/错误的类别 logit）
- *用途：* 对完整链式推理打分；或通过修剪低分分支来引导搜索/解码
- *聚合：* 跨步骤聚合（而非 token）——平均步骤分数、最小值（fail-fast）或加权求和偏向后期步骤

**Value Function：**

- *输入：* prompt $x$ + 当前前缀 $y_{\leq t}$（一个状态）
- 输出：完成中每个 token 位置的 $V_t$（从状态 $t$ 开始的期望剩余回报）
- 用途：在 RL 训练中计算逐 token 优势 $A_t = \hat{R}_t - V_t$；各步骤的分数作为基线
- *聚合：* 通常取最后一个生成 token 处的 $V$；解释不同于"正确性概率"

简而言之，理解不同模型的方式如下：

- **RM：** "这个完整答案有多好？" → 标量值
- **ORM：** "这个答案最终正确吗？" → 逐 token 预测结果（作为中间质量的代理）
- **PRM：** "推理步骤是否合理？" → 逐步骤分数
- **Value：** "从这里还有多少剩余奖励？" → RL 优势中的基线

## 其他奖励模型变体

奖励建模在 RLHF 中仍然是一个相对未充分探索的领域。
传统的 Bradley-Terry 奖励建模损失在许多流行工作中被修改过，但这些修改尚未收敛为单一的"最佳实践"。

### 偏好边距损失（Preference Margin Loss）

当标注者提供等级评分或排名时（例如使用 1–5 的李克特量表 Likert Scale，其中有序类别表示偏好强度的大小），关系的量级可以被用于训练。
最常见的做法是沿偏好方向将数据二值化，将相对评分或排名的混合信息缩减为"被选择"和"被拒绝"两类补全。
额外的信息（如偏好强度）已被用于改进模型训练，但尚未成为标准做法。
Llama 2 提出使用两个数据点之间的边距 $m(y_c, y_r)$ 来区分偏好的量级：

$$\mathcal{L}(\theta) = - \log \left( \sigma \left( r_{\theta}(y_c \mid x) - r_{\theta}(y_r \mid x) - m(y_c, y_r) \right) \right)$$ {#eq:rewardmodelingmargin}

例如，每个补全通常根据质量给予 1 到 5 的排名。
在选中样本被分配 5 分、被拒绝样本被分配 2 分的情况下，边距 $m(y_c, y_r)= 5 - 2 = 3$。
也可以探索其他计算边距的函数。

注意，在 Llama 3 中，由于团队观察到规模扩大后边际收益递减，边距项被移除了。

### 平衡每个 Prompt 的多个比较

InstructGPT 研究了在每个 prompt 上使用 $K = 4$ 到 9 个补全进行排名的影响，从每个 prompt 产生 $\binom{K}{2}$ 个成对比较 [@ouyang2022training]。
由于这些比较高度相关（它们共享同一个 prompt），简单地将它们打乱并放入数据集会导致奖励模型过拟合。
为解决此问题，他们对每个 prompt 的每个比较进行了损失更新加权——如果不重新加权，包含更多补全的 prompt 会因为产生更多比较对而对总损失的贡献更大。
在实践中，来自单个 prompt 的所有 $\binom{K}{2}$ 个比较通常被包含在同一个训练批次中并一起平均，因此每个 prompt 只贡献一个分组更新，而不是出现在多个单独的批次中。
这减少了对单个 prompt 的过拟合，也防止了带有更多采样补全的 prompt 主导损失。
损失函数变为：

$$\mathcal{L}(\theta) = - \frac{1}{\binom{K}{2}} \mathbb{E}_{(x, y_c, y_r)\sim D} \log \left( \sigma \left( r_{\theta}(y_c \mid x) - r_{\theta}(y_r \mid x) \right) \right)$$ {#eq:rewardmodelinginstructgpt}

### K 向损失函数（K-Wise Loss Function）

存在许多其他形式的公式化方法，可以为 RLHF 创建合适的人类偏好模型。
其中一个例子是流行早期 RLHF 模型 Starling 7B 和 34B 中使用的基于 Plackett-Luce 模型的 K 向损失函数（K-wise loss）[@liu2019learning] [@zhu2024starling]。

Zhu et al. 2023 [@zhu2023principled] 将设定形式化如下：
给定 prompt（或状态）$s^i$，从 $P(a_0,\cdots,a_{K-1}|s^i)$ 中采样 $K$ 个动作 $(a_0^i, a_1^i, \cdots, a_{K-1}^i)$。
然后，标注者按偏好对 $K$ 个动作进行排名，产生一个排列 $\sigma^i: [K] \mapsto [K]$，其中 $\sigma^i(0)$ 是最受偏好的动作。
这产生了所有 $K$ 个物品完整排名的 Plackett-Luce 概率：

$$P(\sigma^i|s^i,a_0^i,a_1^i,\ldots,a_{K-1}^i) = \prod_{k=0}^{K-1} \frac{\exp(r_{\theta\star}(s^i,a_{\sigma^i(k)}^i))}{\sum_{j=k}^{K-1}\exp(r_{\theta\star}(s^i,a_{\sigma^i(j)}^i))}$$ {#eq:kwise_rm}

当 $K = 2$ 时，这退化为 Bradley-Terry（BT）成对比较模型。
无论如何，训练完成后，这些模型在 RLHF 训练中的使用方式与其他奖励模型类似。

## 生成式奖励建模（即 LLM-as-a-Judge）

由于偏好数据的成本高昂，一个重要的研究领域应运而生：使用现有的语言模型作为人类偏好的评判者，或用于其他评估场景 [@zheng2023judging]。
核心思路是用指令提示语言模型如何进行评判，再加上一个 prompt 和两个补全（类似于人工标注者的操作方式）。
一个来自该领域开创性工作、用于聊天评估 MT-Bench [@zheng2023judging] 的 prompt 示例如下：

```text
[System]
Please act as an impartial judge and evaluate the quality of the responses provided by two AI assistants to the user question displayed below.
You should choose the assistant that follows the user's instructions and answers the user's question better.
Your evaluation should consider factors such as the helpfulness, relevance, accuracy, depth, creativity, and level of detail of their responses.
Begin your evaluation by comparing the two responses and provide a short explanation.
Avoid any position biases and ensure that the order in which the responses were presented does not influence your decision.
Do not allow the length of the responses to influence your evaluation.
Do not favor certain names of the assistants.
Be as objective as possible.
After providing your explanation, output your final verdict by strictly following this format: "[[A]]" if assistant A is better, "[[B]]" if assistant B is better, and "[[C]]" for a tie.
[User Question]
{question}
[The Start of Assistant A's Answer]
{answer_a}
[The End of Assistant A's Answer]
[The Start of Assistant B's Answer]
{answer_b}
[The End of Assistant B's Answer]
```

由于 LLM-as-a-judge 在评估中的有效性，它催生了许多其他评估方法，如 AlpacaEval [@dubois2024length]、Arena-Hard [@li2024crowdsourced] 和 WildBench [@lin2024wildbench]，许多人开始使用 LLM-as-a-judge 代替奖励模型来创建和使用偏好数据。

围绕所谓"生成式奖励模型"（Generative Reward Models）[@mahan2024generative] [@zhang2024generative] [@ankner2024critique]（包括*专门*训练为高效评判者的模型 [@kim2023prometheus]）已形成一整片研究领域。
但在 RM 评估上，它们往往落后于现有奖励模型，这表明奖励建模对于当前 RLHF 仍然是一项重要的技术。

改善 LLM-as-a-judge 工作流程鲁棒性的一个常见技巧是将采样温度（sampling temperature）设为 0，以降低评分的方差。

## 进一步阅读

奖励建模的学术文献在 2024 年确立了自己的地位。
早期进展的很大一部分聚焦于建立基准测试和识别行为模式。
第一个 RM 基准测试 RewardBench 提供了测试奖励模型的通用基础设施 [@lambert2024rewardbench]。
此后，RM 评估已扩展到类似于通用后训练模型的评估类型——一些评估测试已知正确答案领域的预测准确率 [@lambert2024rewardbench]，另一些则更接近 LLM-as-a-judge 所执行的"感觉类"（vibes）评估或与其他基准的相关性 [@wen2024rethinking]。

新的基准测试示例包括：

- **纯文本（通用聊天/偏好）：** RMB [@zhou2024rmb]、RewardBench2 [@malik2025rewardbench]、Preference Proxy Evaluations [@frick2024evaluate] 或 RM-Bench [@liu2024rm]。
- **专用纯文本（数学等）：** multilingual reward bench (M-RewardBench) [@gureja2024m]、用于检索增强生成（RAG）的 RAG-RewardBench [@jin2024rag]、针对拼写错误的 ReWordBench [@wu2025rewordbench]、RewardMATH [@kim2024evaluating] 或 AceMath-RewardBench [@liu2024acemath]。
- **过程奖励模型：** PRM Bench [@song2025prmbench] 或 ProcessBench [@zheng2024processbench]，以及视觉基准 VisualProcessBench [@wang2025visualprm] 或 ViLBench [@tu2025vilbench]。
- **智能体奖励模型：** Agent-RewardBench [@men2025agentrewardbench] 或 CUARewardBench [@lin2025cuarewardbench]。
- **多模态：** MJ-Bench [@chen2024mj]、Multimodal RewardBench [@yasunaga2025multimodal]、VL RewardBench [@li2024vlrewardbench] 或 VLRMBench [@ruan2025vlrmbench]。

要了解*训练*奖励模型的进展，可以参考新的奖励模型训练方法，包括方面条件模型（aspect-conditioned models）[@wang2024interpretable]、高质量人工数据集 [@wang2024helpsteer2] [@wang2024helpsteer2p]、扩展实验 [@adler2024nemotron]、广泛实验 [@touvron2023llama] 或数据去偏 [@park2024offsetbias]。

## 建议的实验

配套代码仓库在 `code/reward_models/` 中包含了小型奖励模型训练脚本。
这些设计为学习练习，而非调优后的参考配方。
从干净的 `code/` 环境开始，运行 `uv sync`，然后一次运行一个实验。

1. **在 UltraFeedback 上训练一个 Bradley-Terry 偏好奖励模型。**
   运行：

   ```bash
   cd code/
   uv run python -m reward_models.train_preference_rm --config reward_models/configs/preference_rm.yaml
   ```

   观察演示和 W&B 日志中被选择与被拒绝响应之间的奖励边距是否增长。
   然后在 yaml 配置中改变 `samples`、`lr` 和 `model_id`，观察信号何时变得嘈杂或不稳定。

2. **比较结果监督和过程监督。**
   运行 GSM8K 结果奖励模型和 PRM800K 过程奖励模型：

   ```bash
   cd code/
   uv run python -m reward_models.train_orm --config reward_models/configs/orm.yaml
   uv run python -m reward_models.train_prm --samples 500 --epochs 2
   ```

   比较各模型训练完成后的打分能力：ORM 应能区分正确和错误的答案，而 PRM 应能为中间推理步骤分配分数。
   这是序列级、结果级和过程级监督之间区别的实践版本。

3. **添加小型保留奖励模型评估。**
   一个有用的贡献是为 `reward_models/` 添加一个 50 至 200 例的评估，报告准确率或偏好对排序，而无需完整的训练运行。
   保持评估规模足够小，以便在调参时使用。