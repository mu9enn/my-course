# ORPO/SimPO 调试笔记

> 译者注：这是 RLHF Book 项目中关于 [ORPO](https://arxiv.org/abs/2402.01714)（Odds Ratio Preference Optimization）和 [SimPO](https://arxiv.org/abs/2405.14734)（Simple Preference Optimization）训练过程调试的工作笔记。ORPO 和 SimPO 都是不依赖额外奖励模型的"直接对齐"后训练方法——ORPO 将偏好优化与监督微调（SFT）损失联合训练，SimPO 则通过直接的 margin 损失实现偏好优化。

状态：**待验证** — 参见 [#358](https://github.com/natolambert/rlhf-book/issues/358)

## 背景

- ORPO/SimPO 因极端 ORPO 超参尺度导致的训练不稳定性，已在 [PR #243](https://github.com/natolambert/rlhf-book/pull/243) 中通过切换至**平均对数概率**（average log-probs）解决。
- 剩余的问题是"训练曲线稳定但无进展"（stable but flat），尤其是 ORPO 中偏好项（`or_loss`）对总损失的贡献微乎其微，远不及 SFT 损失。
- SimPO 公式现已改用 gamma/beta 比率的形式：`-logsigmoid(beta * (logit_margin - gamma))`。
- 包含完整运行记录与 Weights & Biases（W&B）链接的实验日志位于：`experiments/2026-02-08-orpo-simpo.md`。

## 调试方法

1. 在跑长周期超参网格搜索之前，先跑低样本量的 sanity check（1 个 epoch，640 条样本）。
2. 确认在 gamma/beta 比率 formulation 下，SimPO 的 margin 和 accuracy 确实有响应。
3. 对 ORPO 的 beta 和学习率做 sweep，以重新平衡 SFT 损失与偏好项的相对权重。
4. 以上小实验验证无误后，再启动 12.8K 条样本的全量实验。

## 小实验脚本

```bash
cd code/

# SimPO sanity run
WANDB_ENTITY=rlhf-book WANDB_PROJECT=core ./direct_alignment/experiments/2026-02-08-orpo-simpo/run_simpo_small.sh

# ORPO sanity run
WANDB_ENTITY=rlhf-book WANDB_PROJECT=core ./direct_alignment/experiments/2026-02-08-orpo-simpo/run_orpo_small.sh
```

### 常用的覆盖参数（overrides）

```bash
# SimPO: stronger margin push
GAMMA=1.0 LEARNING_RATE=1e-6 MAX_SAMPLES=640 NUM_EPOCHS=1 ./direct_alignment/experiments/2026-02-08-orpo-simpo/run_simpo_small.sh

# ORPO: stronger preference term
BETA=1.0 LEARNING_RATE=5e-6 MAX_SAMPLES=640 NUM_EPOCHS=1 ./direct_alignment/experiments/2026-02-08-orpo-simpo/run_orpo_small.sh
```

## 验收标准（Acceptance Criteria）

- SimPO：在前 ~10–20 步优化后，`accuracy` 和 `margins` 趋势应持续上升。
- ORPO：`margins` 应明显离开接近零的区域，且 `or_loss` 相对于 `sft_loss` 的贡献应达到可察觉的水平（non-trivial）。
- 生成的样本保持语义连贯（不出现重复性坍缩，即 repetitive collapse）。

---

译者补充

- **平均对数概率**：原文提及的 "average log-probs" 是指在计算序列级对数概率时对序列中各 token 的对数概率求平均，而非直接求和。这种做法可以缓解序列长度差异带来的尺度问题，在 ORPO 等需要比较被选/拒绝序列 log-prob 差的方法中尤为关键。
- **repetitive collapse（重复性坍缩）**：指模型在训练中出现输出高度重复、丧失多样性的退化现象，常见于偏好优化信号过强或梯度尺度失配时。

### 自测题（译者新增）

1. 为什么在 ORPO 中偏好项 `or_loss` 对总损失的贡献可能远小于 SFT 损失？这会对训练产生什么影响？
2. 使用 gamma/beta 比率而不是单独的 gamma 参数来定义 SimPO 的 margin 损失，这样做的好处是什么？