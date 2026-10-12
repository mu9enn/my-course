<!--
  Copyright (c) 2025-2026 Nathan Lambert.
  Licensed under CC BY-NC-SA 4.0:
  https://creativecommons.org/licenses/by-nc-sa/4.0/
  Full license: https://github.com/natolambert/rlhf-book/blob/main/LICENSE-CHAPTERS
-->
---
prev-chapter: "Direct-Alignment Algorithms"
prev-url: "08-direct-alignment"
page-title: 拒绝采样
search-title: "第 9 章：拒绝采样"
meta-description: "使用奖励模型或偏好信号改善后训练语言模型的拒绝采样与 best-of-n 方法。"
next-chapter: "The Nature of Preferences"
next-url: "10-preferences"
lectures:
  - video: "https://www.youtube.com/watch?v=4gIwiSPmQkU&list=PLL1tdVxB1CpVpEtMHxwuR4uI4Lxjw00_y&index=3"
    label: "Lecture 2: IFT, Reward Modeling, Rejection Sampling (Chap. 4, 5, & 9)"
---

# 拒绝采样

拒绝采样（Rejection Sampling, RS）是偏好微调中应用最广泛也最缺乏系统记录的方法之一。
许多著名的 RLHF 论文将其作为训练流水线中的核心组件，但却缺少一份关于其最佳实现方式以及它为何效果如此出色的标准说明。
拒绝采样可以应用于训练流水线的多个阶段——指令微调之后、基于强化学习的优化之后，甚至 RLVR（基于强化学习的验证推理）之后，因此它是一种用途广泛但难以归类的工具。
再加上它缺乏系统文档的支持，这也是为什么它出现在核心优化方法章节的末尾。

拒绝采样的基本思路是：从模型生成一批新的候选输出，用训练好的奖励模型对其进行筛选，最后只在得分最高的输出上对原始模型进行微调（使用的损失函数与指令微调相同）。

这个名称源自计算统计学 [@gilks1992adaptive]，在那种场景中，研究者希望从一个复杂的分布中采样，却缺乏直接的方法。
为了解决这个问题，人们先从一种更容易建模的分布中采样，再用启发式规则检查采样是否"被允许"（即是否满足目标分布的要求）。
在语言模型的语境下，目标分布是高质量的对 prompt 的输出，过滤器是一个奖励模型，而采样分布则是当前模型本身。

WebGPT [@nakano2021webgpt]、Anthropic 的 Helpful and Harmless 智能体 [@bai2022training]、OpenAI 关于过程奖励模型的热门论文 [@lightman2023let]、Llama 2 Chat 模型 [@touvron2023llama] 以及其他开创性工作都使用了这一基线方法；近期的研究则对其进行了更形式化的总结，例如 RAFT [@dong2023raft] 将其扩展到多模态对齐，以及统计拒绝采样优化（Statistical Rejection Sampling Optimization, RSO）[@liu2023statistical] 从原则上梳理了拒绝采样与其他偏好学习目标之间的关系。

*在本章中，我们用 $x$ 表示 prompt，用 $y$ 表示输出。这种符号表示在语言模型文献中很常见，因为相关方法操作的是完整的 prompt-输出对，而非单个 token。*

## 训练过程：分步讲解

拒绝采样整体上分为以下几个阶段。

0. **选择 prompt 和奖励模型：** 首先，你需要决定选择哪些 prompt 来训练，这是相对于训练的其他阶段而言的。最简单的方法是复用第一阶段 SFT/IFT 中使用过的所有 prompt，但这可能会导致一定程度的过拟合。在执行拒绝采样之前，你还必须已经训练好了一个奖励模型（参见第 5 章获取更多信息）。
1. **从起始检查点生成输出：** 接下来，你需要用你想要优化的模型，针对选定的 prompt 生成输出。这一步可能涉及调整多项设置，如采样温度、top-p、最大序列长度、每个 prompt 生成的输出数量等。
2. **用奖励模型选出得分最高的输出：** 所有输出都由奖励模型进行排名。此阶段还可以包含去重处理，即每个 prompt 只保留一个输出。当然，这类设计选择往往需要通过经验性的消融实验来确定。
3. **在最优输出上进行 SFT：** 拒绝采样的最后一步，是在选定的输出上对起始检查点执行标准的指令微调。

@fig:rs-overview 展示了拒绝采样流程的可视化概览。

![拒绝采样概览。](images/rejection-sampling.png){#fig:rs-overview}

关于应该使用哪些 prompt、如何选择奖励模型、如何安排拒绝采样的顺序等具体问题，文献中并未给出充分的记录。
本章对这些方法进行了概述，更多的实验工作留待读者自行探索。

### 生成输出

为了针对每个 prompt 生成一组多个候选输出，我们先定义 $M$ 个 prompt 构成的向量：

$$X = [x_1, x_2, ..., x_M]$$ {#eq:rs_prompt_vector}

这些 prompt 可以来自多种来源，但最常见的是来自指令训练集。

对于每个 prompt $x_i$，我们生成 $N$ 个输出。我们可以用矩阵来表示：

$$Y = \begin{bmatrix}
y_{1,1} & y_{1,2} & \cdots & y_{1,N} \\
y_{2,1} & y_{2,2} & \cdots & y_{2,N} \\
\vdots & \vdots & \ddots & \vdots \\
y_{M,1} & y_{M,2} & \cdots & y_{M,N}
\end{bmatrix}$$ {#eq:rs_completion_matrix}

其中 $y_{i,j}$ 表示第 $i$ 个 prompt 的第 $j$ 个输出。
每一行 $i$ 对应一个 prompt $x_i$，包含其 $N$ 个候选输出；每一列 $j$ 则对应所有 prompt 中第 $j$ 个采样输出。

### 为输出打分

现在，我们把这些 prompt-输出对全部送入奖励模型，得到一个奖励矩阵。
我们将奖励表示为矩阵 $R$：

$$R = \begin{bmatrix}
r_{1,1} & r_{1,2} & \cdots & r_{1,N} \\
r_{2,1} & r_{2,2} & \cdots & r_{2,N} \\
\vdots & \vdots & \ddots & \vdots \\
r_{M,1} & r_{M,2} & \cdots & r_{M,N}
\end{bmatrix}$$ {#eq:rs_reward_matrix}

每个奖励 $r_{i,j}$ 通过将输出 $y_{i,j}$ 及其对应的 prompt $x_i$ 输入奖励模型 $\mathcal{R}$ 来计算：

$$r_{i,j} = \mathcal{R}(y_{i,j} \mid x_i)$$ {#eq:rs_reward_computation}

有多种方法可以选出得分最高的输出来进行训练。

为了形式化描述基于奖励矩阵选择最优输出的过程，我们可以定义一个作用于奖励矩阵 $R$ 的选择函数 $S$。

#### 每 prompt 选最优

第一种可能的选择函数是为每个 prompt 选取最高奖励对应的输出。

$$S(R) = \left[\arg\max_{j} r_{1,j}, \arg\max_{j} r_{2,j}, ..., \arg\max_{j} r_{M,j}\right]$$ {#eq:rs_selection_per_prompt}

函数 $S$ 返回一个索引向量，其中每个索引对应于 $R$ 中每一行具有最高奖励的那一列。
然后我们可以用这些索引来选出我们的输出：

$$Y_{chosen} = [y_{1,S(R)_1}, y_{2,S(R)_2}, ..., y_{M,S(R)_M}]$$ {#eq:rs_chosen_completions}

#### 全局选 Top-K

或者，我们也可以从全部候选中选出前 $K$ 个 prompt-输出对。
首先，我们将奖励矩阵 $R$ 展平为单个向量：

$$R_{flat} = [r_{1,1}, r_{1,2}, ..., r_{1,N}, r_{2,1}, r_{2,2}, ..., r_{2,N}, ..., r_{M,1}, r_{M,2}, ..., r_{M,N}]$$ {#eq:rs_flattened_rewards}

这个 $R_{flat}$ 向量的长度为 $M \times N$，其中 $M$ 是 prompt 数量，$N$ 是每个 prompt 的输出数量。

现在，我们可以定义一个选择函数 $S_K$，用于选出 $R_{flat}$ 中 $K$ 个最高值对应的索引：

$$S_K(R_{flat}) = \text{argsort}(R_{flat})[-K:]$$ {#eq:rs_topk_selection}

其中 $\text{argsort}$ 返回将数组按升序排列的索引，我们取最后 $K$ 个索引即可得到 $K$ 个最高值。

为了得到我们选定的输出，我们需要将这些展平索引映射回原始的输出矩阵 $Y$。
要将从零开始的展平索引 $k$ 映射回 $(i,j)$，可以通过公式 $i = \lfloor k / N \rfloor + 1$ 和 $j = (k \bmod N) + 1$ 来完成。

译者注：这里的索引映射使用的是 1-based 编号（即 $i$ 从 1 开始），而 $k$ 是 0-based。例如，$N=4$ 时，展平索引 $k=5$ 对应第 $\lfloor 5/4 \rfloor + 1 = 2$ 个 prompt 和第 $(5 \bmod 4) + 1 = 2$ 个输出，即 $(2,2)$。

#### 选择示例

考虑以下场景：我们有 5 个 prompt 和 4 个输出。我们将展示两种基于奖励选择输出的方式。

$$R = \begin{bmatrix}
0.7 & 0.3 & 0.5 & 0.2 \\
0.4 & 0.8 & 0.6 & 0.5 \\
0.9 & 0.3 & 0.4 & 0.7 \\
0.2 & 0.5 & 0.8 & 0.6 \\
0.5 & 0.4 & 0.3 & 0.6
\end{bmatrix}$$ {#eq:rs_example_matrix}

首先是**每 prompt 选最优**。直观上，我们可以将奖励矩阵中标出最高分：

$$R = \begin{bmatrix}
\textbf{0.7} & 0.3 & 0.5 & 0.2 \\
0.4 & \textbf{0.8} & 0.6 & 0.5 \\
\textbf{0.9} & 0.3 & 0.4 & 0.7 \\
0.2 & 0.5 & \textbf{0.8} & 0.6 \\
0.5 & 0.4 & 0.3 & \textbf{0.6}
\end{bmatrix}$$ {#eq:rs_example_per_prompt}

使用 argmax 方法，我们为每个 prompt 选出最佳输出：

$$S(R) = \left[\arg\max_{j} r_{i,j} \text{ for } i \in [1,5]\right]$$ {#eq:rs_example_selection_formula}

$$S(R) = [1, 2, 1, 3, 4]$$ {#eq:rs_example_selection_result}

这意味着我们会选择：

- 对于 prompt 1：输出 1（奖励 0.7）
- 对于 prompt 2：输出 2（奖励 0.8）
- 对于 prompt 3：输出 1（奖励 0.9）
- 对于 prompt 4：输出 3（奖励 0.8）
- 对于 prompt 5：输出 4（奖励 0.6）

现在来看**全局最优**。
让我们标出总体得分最高的前五个输出对。

$$R = \begin{bmatrix}
\textbf{0.7} & 0.3 & 0.5 & 0.2 \\
0.4 & \textbf{0.8} & 0.6 & 0.5 \\
\textbf{0.9} & 0.3 & 0.4 & \textbf{0.7} \\
0.2 & 0.5 & \textbf{0.8} & 0.6 \\
0.5 & 0.4 & 0.3 & 0.6
\end{bmatrix}$$ {#eq:rs_example_top_overall}

首先，我们将奖励矩阵展平：

$$R_{flat} = [0.7, 0.3, 0.5, 0.2, 0.4, 0.8, 0.6, 0.5, 0.9, 0.3, 0.4, 0.7, 0.2, 0.5, 0.8, 0.6, 0.5, 0.4, 0.3, 0.6]$$ {#eq:rs_example_flattened}

现在，我们选出五个最高值对应的索引：
$$S_5(R_{flat}) = [8, 5, 14, 0, 11]$$ {#eq:rs_example_topk_result}

将这些映射回原始矩阵：

- 索引 8 → prompt 3，输出 1（奖励 0.9）
- 索引 5 → prompt 2，输出 2（奖励 0.8）
- 索引 14 → prompt 4，输出 3（奖励 0.8）
- 索引 0 → prompt 1，输出 1（奖励 0.7）
- 索引 11 → prompt 3，输出 4（奖励 0.7）

#### 实现示例

以下代码片段展示了这些选择方法可以如何具体实现。

```python
import numpy as np

x = np.random.randint(10, size=10)
print(f"{x=}")
sorted_indices = np.argsort(x)
x_sorted = x[sorted_indices]
print(f"{x_sorted=}")

# first way to recover the original array
i_rev = np.zeros(10, dtype=int)
i_rev[sorted_indices] = np.arange(10)
np.allclose(x, x_sorted[i_rev])

# second way to recover the original array
np.allclose(x, x_sorted[np.argsort(sorted_indices)])
```

### 微调

在选定输出后，你在当前版本的模型上执行标准的指令微调。
更多细节可参考[指令微调章节](https://rlhfbook.com/c/04-instruction-tuning)。

## 实现细节

执行此项训练的核心超参数都非常直观：

- **采样参数**：拒绝采样直接依赖于模型输出的结果。拒绝采样的常见设置包括高于零的温度（如 0.7 到 1.0 之间），并可对 top-p 或 top-k 等参数进行其他调整。
- **每个 prompt 的输出数量**：成功的拒绝采样实现通常会为每个 prompt 生成 10 到 30 个或更多输出。使用过少的输出会导致训练结果出现偏差和/或较高的噪声。
- **指令微调细节**：目前尚未公开关于拒绝采样期间指令微调的明确训练细节。很可能它们使用的设置与模型初始指令微调阶段略有不同。
- **异构模型生成**：某些拒绝采样实现包含了来自多个模型的生成结果，而不仅仅是即将接受训练的当前模型。对于如何操作，目前尚未形成明确的最佳实践。
- **奖励模型训练**：所使用的奖励模型将极大影响最终结果。有关奖励模型训练的更多信息，请参阅[相关章节](https://rlhfbook.com/c/05-reward-models)。

在进行批量奖励模型推理时，你可以按长度对 tokenized 后的输出进行排序，使每个 batch 内的序列长度相近。
这样可以减少需要运行推理的填充 token 数量，从而在引入轻微实现复杂度的同时提升吞吐率。

## 相关：Best-of-N 采样

Best-of-N（BoN）是拒绝采样的近亲，两者遵循相同的"先生成、再打分"流程，但不同之处在于你**不会**在选定的输出上对模型进行微调。
相反，BoN 是在推理时为静态 prompt（或一组 prompt）计算出最好的输出，相关技术经常被用于聊天模型的"Pro"层级，通过花费额外的计算资源来为你的查询获取一个答案。

Best-of-N 采样通常作为与 RLHF 训练方法对比的基线方法。
需要牢记的是，BoN **不**修改底层模型本身，而是一种采样技术。
因此，将 BoN 采样与在线训练方法（如 PPO）进行比较在某些场景下仍然有效。
例如，你仍然可以针对任何策略来计算运行 BoN 采样时的 KL 距离。

在这里，我们将展示当对单个 prompt 使用简单的 BoN 采样时，上述两种选择标准是等价的。

设 $R$ 为单个 prompt 的奖励向量，包含 $N$ 个输出：

$$R = [r_1, r_2, ..., r_N]$$ {#eq:rewards_vector}

其中 $r_j$ 表示第 $j$ 个输出的奖励。

使用 argmax 方法，我们为 prompt 选出最佳输出：

$$S(R) = \arg\max_{j \in [1,N]} r_j$$ {#eq:selection_function}

使用 $K=1$ 的 Top-K 方法会退化到相同的结果，这也是常见的做法。

## 建议的实验

配套实现代码位于 `code/rejection_sampling/` 中，它运行了一个完整的 GSM8K 拒绝采样流水线：生成 rollout、用奖励模型打分、选择训练子集、进行微调并评估 exact-match 准确率。
这四个配置以对照配对的形式组织，因此读者可以提问：奖励模型实际上是否起了作用。

1. **只构建一次 rollout 缓存。**

   ```bash
   cd code/
   uv run python -m rejection_sampling.preprocess \
       --config rejection_sampling/configs/top_per_prompt.yaml
   ```

   这会为共享的 GSM8K 子集生成并打分输出。
   只要生成和打分的设置保持不变，后续的训练配置会复用该缓存。

2. **对比奖励选择与随机对照。**

   ```bash
   cd code/
   uv run python -m rejection_sampling.train \
       --config rejection_sampling/configs/top_per_prompt.yaml
   uv run python -m rejection_sampling.train \
       --config rejection_sampling/configs/random_per_prompt.yaml
   uv run python -m rejection_sampling.train \
       --config rejection_sampling/configs/top_k_overall.yaml
   uv run python -m rejection_sampling.train \
       --config rejection_sampling/configs/random_k_overall.yaml
   ```

   对照配对读取结果：`top_per_prompt` 与 `random_per_prompt` 一组，`top_k_overall` 与 `random_k_overall` 一组。
   如果奖励选中的运行结果没有击败其随机基线，那么奖励模型或采样的输出在该子集上未能提供有用的信号。

3. **改变奖励模型可用的选择数量。**
   复制一个配置文件，修改 `num_completions_per_prompt`、`temperature`、`top_p` 和 `selection.top_k`。
   更多的输出可以改进可用的最佳样本，但这只有在奖励模型能够有效区分好坏答案的前提下才成立。

4. **尝试更小的策略模型。**
   将 `model_name` 设为一个更小的兼容 instruct 模型，减少 `max_train_samples`，然后重新运行相同的对照配对。
   这会让实验更便宜，同时也能凸显拒绝采样是在挽救较弱的生成结果，还是仅仅在已有较好的结果中进行筛选。

<!-- 译者新增自测题 -->

## 自测题（译者新增）

1. 为什么拒绝采样中的"采样分布"通常选择当前模型，而不是一个预训练的基础模型？这样做对最终效果有什么影响？
2. 在"每 prompt 选最优"与"全局选 Top-K"两种策略之间，如果 $N$（每个 prompt 的输出数）非常大而 $M$（prompt 数量）很小，哪种策略更可能出现重复选中同一 prompt 的情况？
3. 假设奖励模型对两个输出的评分分别为 0.85 和 0.83，但人类标注者认为 0.83 对应的输出质量更高。这说明了奖励模型的什么局限性？在拒绝采样的上下文中，这种误差可能导致什么后果？