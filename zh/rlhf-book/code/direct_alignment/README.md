# 直接对齐算法

本目录提供 [RLHF Book](https://rlhfbook.com) 中直接对齐方法的的教学实现。数学推导与直观理解请参见 **第八章：直接对齐**。

> **状态**：DPO / IPO / KTO / APO 已验证通过。SimPO 与 ORPO 已实现，目前正在调参打磨中。

截至 2026-02-08，ORPO / SimPO 仍属在研状态。日期化的运行日志与相关链接见 `direct_alignment/experiments/2026-02-08-orpo-simpo.md`。

## 参考运行

| 算法 | wandb | 状态 |
|-----------|-------|--------|
| **DPO** | [dpo-olmo-1b](https://wandb.ai/rlhf-book/core/runs/fzy8k8go) | ✅ 已验证 |
| **DPO-Norm** | [dpo-norm-olmo-1b](https://wandb.ai/rlhf-book/core/runs/giyhitjw) | ✅ 已验证 |
| **IPO** | [ipo-olmo-1b](https://wandb.ai/rlhf-book/core/runs/5s29syo6) | ✅ 已验证 |
| **SimPO** | [simpo-olmo-1b](https://wandb.ai/rlhf-book/core/runs/ftv5rs3x) | ⚠️ 噪声较大 — 待调试 |
| **ORPO** | [orpo-olmo-1b](https://wandb.ai/rlhf-book/core/runs/o38ffli5) | ⚠️ 噪声较大 — 待调试 |
| **KTO** | [kto-olmo-1b](https://wandb.ai/rlhf-book/core/runs/hgqrkfi6) | ✅ 已验证 |
| **APO Zero** | [apo-zero-olmo-1b](https://wandb.ai/rlhf-book/core/runs/3m2uiyw3) | ✅ 已验证 |
| **APO Down** | [apo-down-olmo-1b](https://wandb.ai/rlhf-book/core/runs/tqzkmyi6) | ✅ 已验证 |

![DPO、IPO 和 KTO 的直接对齐准确率曲线](../images/wandb_direct_alignment.png)

## 算法速览

| 算法 | 论文 | 核心思想 |
|-----------|-------|----------|
| **DPO** | [Rafailov et al., 2023](https://arxiv.org/abs/2305.18290) | 基础直接对齐方法 — 通过 log-ratio 隐式建模奖励 |
| **DPO-Norm** | [Meng et al., 2024](https://arxiv.org/abs/2405.14734) | 在 DPO 基础上对响应 token 的 log-prob 取均值，并使用参考模型 |
| **cDPO** | 与 DPO 相同 | 对噪声偏好数据使用 label smoothing 的 DPO |
| **IPO** | [Azar et al., 2023](https://arxiv.org/abs/2310.12036) | 使用回归目标替代分类目标 — 更稳健 |
| **SimPO** | [Meng et al., 2024](https://arxiv.org/abs/2405.14734) | 长度归一化，无需参考模型 |
| **ORPO** | [Hong et al., 2024](https://arxiv.org/abs/2403.07691) | 结合 SFT 与偏好训练，无需参考模型 |
| **KTO** | [Ethayarajh et al., 2024](https://arxiv.org/abs/2402.01306) | 灵感来源于前景理论，可直接使用二元好/坏标签 |
| **APO-Zero** | [D'Oosterlinck et al., 2024](https://arxiv.org/abs/2408.06266) | 锚定偏好优化 — 提升 chosen 似然、降低 rejected 似然（适用于偏好数据优于模型时） |
| **APO-Down** | [D'Oosterlinck et al., 2024](https://arxiv.org/abs/2408.06266) | 锚定偏好优化 — 同时降低两者的似然，rejected 降得更多（适用于偏好数据劣于模型时） |

## 快速开始

```bash
cd code/
uv sync

# Train DPO on 1k samples (quick test)
uv run python -m direct_alignment.train --loss dpo --max_samples 1000

# Train with config file
uv run python -m direct_alignment.train --config direct_alignment/configs/dpo.yaml

# Train with wandb logging
WANDB_PROJECT=rlhf-book uv run python -m direct_alignment.train --loss dpo
```

## 损失函数

### DPO Loss

核心 DPO loss 通过最大化 chosen 与 rejected 之间的 margin 来优化：

```python
# From Chapter 8
pi_logratios = policy_chosen_logps - policy_rejected_logps
ref_logratios = reference_chosen_logps - reference_rejected_logps
logits = pi_logratios - ref_logratios
loss = -F.logsigmoid(beta * logits)
```

### DPO-Norm Loss

DPO-Norm 保留了 DPO 的参考模型，但对每个序列的 log-prob 使用响应 token 的平均值来计算：

```python
policy_chosen = sum(policy_chosen_token_logps) / chosen_tokens
policy_rejected = sum(policy_rejected_token_logps) / rejected_tokens
ref_chosen = sum(ref_chosen_token_logps) / chosen_tokens
ref_rejected = sum(ref_rejected_token_logps) / rejected_tokens

pi_logratios = policy_chosen - policy_rejected
ref_logratios = ref_chosen - ref_rejected
logits = pi_logratios - ref_logratios
loss = -F.logsigmoid(beta * logits)
```

这一方法借鉴了 SimPO 的长度归一化思路，但不移除 DPO 的参考修正项，也不添加 SimPO 的 margin 项 `gamma`。

使用 DPO-Norm 时，推荐 `direct_alignment/configs/dpo_norm.yaml`。如果直接使用 CLI 参数覆盖，请传入 `--beta 2.0` 或另一个调优后的值，因为 CLI 的默认值沿用 DPO 的 `0.1`。
后续可以考虑为仅 CLI 运行的各算法完善默认初始化。

### SimPO Loss

SimPO 移除了参考模型，使用长度归一化：

```python
# Average log probs instead of sum
avg_logp_chosen = sum(log_probs) / num_tokens
logits = avg_logp_chosen - avg_logp_rejected
loss = -F.logsigmoid(beta * logits - gamma)
```

### IPO Loss

IPO 对目标 margin 使用平方误差：

```python
target_margin = 1.0 / (2.0 * beta)
loss = (logits - target_margin) ** 2
```

### KTO Loss

KTO 使用前景理论，采用统一的参考点：

```python
# KL reference point (from separate samples in full implementation)
KL = mean(all_logratios).clamp(min=0)
# Desirable: want chosen better than reference
loss_chosen = 1 - sigmoid(beta * (chosen_logratio - KL))
# Undesirable: want rejected worse than reference
loss_rejected = 1 - sigmoid(beta * (KL - rejected_logratio))
```

## 数据集

默认数据集为 `argilla/ultrafeedback-binarized-preferences-cleaned`，是 UltraFeedback 的清洗版本，约含 60k 对偏好样本。

其他兼容的数据集：

- `Anthropic/hh-rlhf` — Anthropic 的 helpfulness/harmlessness 数据
- 任何包含 `prompt`、`chosen`、`rejected` 列的数据集

## 关键超参数

| 参数 | DPO | DPO-Norm | IPO | SimPO | ORPO | APO |
|-----------|-----|----------|-----|-------|------|-----|
| `beta` | 0.1-0.5 | 2.0-5.0 | 0.1 | 2.0-2.5 | 0.1 | 0.1 |
| `learning_rate` | 5e-6 | 5e-6 到 1e-6 | 5e-6 | 8e-7 到 1e-6 | 1e-6 | 5e-6 |
| 参考模型 | 需要 | 需要 | 需要 | 不需要 | 不需要 | 需要 |

**重要**：DPO 需要使用非常低的 learning rate（1e-7 到 5e-6）。较高的 learning rate 会导致训练发散。

**关于 IPO loss 的数值量级**：IPO 对目标 margin `1/(2*beta)` 使用平方误差。当 beta=0.1 时，目标为 5.0，因此早期的 loss 值（约 10-25）会远高于 DPO（约 0.5-0.7）。这是预期之内的结果 — IPO 的 loss 和梯度范数不能与 DPO 直接比较。

**关于 SimPO 的 learning rate**：SimPO 需要比 DPO 更低的 learning rate（3e-7 到 1e-6）。根据 [SimPO 官方仓库](https://github.com/princeton-nlp/SimPO)："较大的 learning rate（例如 1e-5）会显著降低性能，导致模型生成不连贯的句子或完全重复的响应。"

**关于 DPO-Norm 的数值量级**：DPO-Norm 使用 per-token 平均 log-ratio，因此其 logits 远小于求和形式的 DPO logits。`beta` 约 `2.0` 是一个合理的起始值（与 SimPO 的范围匹配）。这一做法已得到 SimPO 作者的直接支持（[GitHub #20](https://github.com/princeton-nlp/SimPO/issues/20)）以及 Ai2 open-instruct 维护者（[GitHub #237](https://github.com/allenai/open-instruct/pull/237)）的认可。

### 训练中生成日志

训练可以定期生成样本输出以进行定性检查。当前实现支持：

- 可配置的生成参数（`sample_do_sample`、`sample_temperature`、`sample_top_p`、`sample_max_tokens`）
- 多轮采样策略（`fixed`、`round_robin`、`random`）
- 默认使用较大的轮转 prompt 池（16 个 prompt），也支持通过 `sample_prompts_file` 传入自定义 prompt 文件
- W&B table 日志，附带 per-sample 元数据（prompt id、解码设置、token 上限）

### ORPO / SimPO / DPO-Norm 实现注意事项

这些 loss 的实现比较容易出错，因为它们对 log-prob 的缩放量级非常敏感。

- **ORPO 在此实现中使用平均 log-probabilities**（与 TRL ORPO 行为一致），而非序列的求和 log-probabilities。
- **这对 ORPO 为何重要**：长响应的求和 log-probs 会变成量级很大的负数，这使得 ORPO 的 log-odds 项在数值上极端化，可能主导 SFT 项。
- **修复前观察到的失效模式**：出现极大的 `log_odds_ratio` / `or_loss` 值，优化不稳定。
- **当前 ORPO 的安全保护**：在执行 `log1mexp` 前将策略 log-probs 截断至 `< 0`，以规避边界情况的数值问题。
- **SimPO 保持基于平均 log-prob**（如设计所述），且对 learning rate 敏感；默认值调得比 DPO 更低。
- **DPO-Norm 对策略和参考模型均使用平均 log-probabilities**，然后对由此产生的 per-token log-ratio 应用标准 DPO loss。
- **配置含义**：SimPO / ORPO 的 learning rate 有意设得更低，运行时间更长以降低噪声。

### 序列长度控制

遵循 TRL 风格的 prompt / completion 长度控制选项：

| 参数 | 默认值 | 描述 |
|-----------|---------|-------------|
| `max_length` | 512 | 最大总序列长度（prompt + completion） |
| `max_prompt_length` | None | 最大 prompt token 数（超出时从左截断） |
| `max_completion_length` | None | 最大 completion token 数（从右截断） |
| `truncation_mode` | `keep_end` | `keep_end` 保留响应，`keep_start` 保留 prompt |

当总长度超过 `max_length` 时，默认从**左侧**（prompt 端）截断，以尽可能多地保留响应 — 因为我们的 loss 只在响应 token 上计算。

## 内存需求

在 DGX Spark（119.7 GB 统一内存）上对 OLMo-2-0425-1B-SFT 进行的内存分析结果：

| Batch Size | max_length=512 | max_length=1024 | max_length=2048 | max_length=4096 |
|------------|----------------|-----------------|-----------------|-----------------|
| 1 | 20% | 21% | 21% | 24% |
| 2 | 21% | 21% | 24% | 28% |
| 4 | 21% | 24% | 28% | 35% |
| 8 | 24% | 28% | 35% | 53% |
| 16 | 28% | 35% | 53% | ~85%+ |

**推荐配置**：batch_size=8、max_length=2048（占用 35% 内存），配合 gradient_accumulation_steps=8，等效 batch size 为 64。

对于带有 gradient checkpointing 的小显卡：

- 1B 模型：约 8-10 GB
- 3B 模型：约 15-20 GB

## 参考实现

链接已固定至特定 commit 以保证可复现性（2026 年 1 月）。

### DPO

**论文：** [Direct Preference Optimization: Your Language Model is Secretly a Reward Model](https://arxiv.org/abs/2305.18290)

| 来源 | 链接 |
|--------|------|
| 原始实现 (Eric Mitchell) | [trainers.py @ f8b8c0f](https://github.com/eric-mitchell/direct-preference-optimization/blob/f8b8c0f49dc92a430bae41585f9d467d3618fe2f/trainers.py) |
| TRL | [dpo_trainer.py @ 035c3ff](https://github.com/huggingface/trl/blob/035c3ffa70065339a18e98def65d90ca45e64a5c/trl/trainer/dpo_trainer.py) |
| Open-Instruct | [dpo_tune_cache.py @ d64832d](https://github.com/allenai/open-instruct/blob/d64832d0b3bca46f4c3e5d1af24f62c23cfa7e63/open_instruct/dpo_tune_cache.py) |
| Open-Instruct | [dpo_utils.py @ d64832d](https://github.com/allenai/open-instruct/blob/d64832d0b3bca46f4c3e5d1af24f62c23cfa7e63/open_instruct/dpo_utils.py) |

### KTO

**论文：** [KTO: Model Alignment as Prospect Theoretic Optimization](https://arxiv.org/abs/2402.01306)

| 来源 | 链接 |
|--------|------|
| 官方实现 (HALOs) | [trainers.py @ 4831988](https://github.com/ContextualAI/HALOs/blob/48319882d57af6ebf19e0d39c41fa9aa3cf9dc1e/train/trainers.py) |
| TRL | [kto_trainer.py @ 035c3ff](https://github.com/huggingface/trl/blob/035c3ffa70065339a18e98def65d90ca45e64a5c/trl/experimental/kto/kto_trainer.py) |

**注**：完整的 KTO 需要单独采样来进行 KL 估计。我们的简化版本从 batch 中估计 KL。

### IPO

**论文：** [A General Theoretical Paradigm to Understand Learning from Human Preferences](https://arxiv.org/abs/2310.12036)

| 来源 | 链接 |
|--------|------|
| TRL | [dpo_trainer.py @ 035c3ff](https://github.com/huggingface/trl/blob/035c3ffa70065339a18e98def65d90ca45e64a5c/trl/trainer/dpo_trainer.py)（`loss_type="ipo"`） |
| OpenRLHF | [dpo_trainer.py](https://github.com/OpenRLHF/OpenRLHF)（将 DPO / IPO / cDPO 归为同组） |

### SimPO

**论文：** [SimPO: Simple Preference Optimization with a Reference-Free Reward](https://arxiv.org/abs/2405.14734)

| 来源 | 链接 |
|--------|------|
| 官方实现 | [simpo_trainer.py @ 1b3e8f3](https://github.com/princeton-nlp/SimPO/blob/1b3e8f31a33cd70b3ce52c6065782ab0fae9bf7c/scripts/simpo_trainer.py) |
| Open-Instruct | [dpo_utils.py @ d64832d](https://github.com/allenai/open-instruct/blob/d64832d0b3bca46f4c3e5d1af24f62c23cfa7e63/open_instruct/dpo_utils.py)（`simpo_loss`） |

### ORPO

**论文：** [ORPO: Monolithic Preference Optimization without Reference Model](https://arxiv.org/abs/2403.07691)

| 来源 | 链接 |
|--------|------|
| TRL | [orpo_trainer.py @ 035c3ff](https://github.com/huggingface/trl/blob/035c3ffa70065339a18e98def65d90ca45e64a5c/trl/trainer/orpo_trainer.py) |

### APO

**论文：** [Anchored Preference Optimization and Contrastive Revisions: Addressing Underspecification in Alignment](https://arxiv.org/abs/2408.06266)

两种锚定变体用于消除 DPO 中未指定的似然方向：

- **APO-Zero**：提升 chosen 似然、降低 rejected 似然（适用于偏好数据优于模型时）
- **APO-Down**：同时降低两者的似然，rejected 降得更多（适用于偏好数据劣于模型时）

Hugging Face 的 [SmolLM3 后训练配方](https://huggingface.co/blog/smollm3) 中已使用 APO 替代 DPO。

| 来源 | 链接 |
|--------|------|
| TRL | [dpo_trainer.py @ 035c3ff](https://github.com/huggingface/trl/blob/035c3ffa70065339a18e98def65d90ca45e64a5c/trl/trainer/dpo_trainer.py)（`loss_type="apo_zero"` / `"apo_down"`） |

### 尚未实现

#### ODPO（带偏移的 DPO）

**论文：** [Provably Robust DPO: Aligning Language Models with Noisy Feedback](https://arxiv.org/abs/2403.00409)

| 来源 | 链接 |
|--------|------|
| 官方实现 | [trainers.py @ 6152f67](https://github.com/rycolab/odpo/blob/6152f6723ebca6c2e74ab360dd3e7c0d8047a5f0/trainers.py) |

#### BCO

**论文：** [BCO: A Unified Binary Classifier for Alignment](https://arxiv.org/abs/2404.04656)

| 来源 | 链接 |
|--------|------|
| TRL | [bco_trainer.py @ 035c3ff](https://github.com/huggingface/trl/blob/035c3ffa70065339a18e98def65d90ca45e64a5c/trl/trainer/bco_trainer.py) |

#### Online DPO

**论文：** [Direct Language Model Alignment from Online AI Feedback](https://arxiv.org/abs/2402.04792)

| 来源 | 链接 |
|--------|------|
| TRL | [online_dpo_trainer.py @ 035c3ff](https://github.com/huggingface/trl/blob/035c3ffa70065339a18e98def65d90ca45e64a5c/trl/trainer/online_dpo_trainer.py) |

## 文件结构

```
direct_alignment/
├── README.md          # This file
├── experiments/       # Experiment logs and sweep notes
├── config.py          # Configuration dataclass
├── data.py            # Preference data loading with response masking
├── loss.py            # Loss function implementations
├── train.py           # Training loop with sample generation
└── configs/           # YAML config files
    ├── dpo.yaml
    ├── dpo_norm.yaml
    ├── ipo.yaml
    ├── simpo.yaml
    ├── orpo.yaml
    ├── kto.yaml
    ├── apo_zero.yaml
    └── apo_down.yaml
```

## 实现注意事项

### KTO 数据格式

KTO loss 函数支持论文中的原始设定（需要来自不相关输出的独立 KL 样本），但**当前数据加载器仅支持成对的偏好数据**（prompt / chosen / rejected 格式）。KTO 通过将 `chosen` 视为 desirable、`rejected` 视为 undesirable 来进行训练。

如需支持真正的非配对 KTO 数据（prompt / response / label 格式），请参见下方的 TODO。

### 截断策略

长序列从**左侧**（prompt token）截断，以尽可能多地保留响应。这一点很重要 — 因为我们的 loss 只在响应 token 上计算。

### Chat Template 要求

模型必须配置 chat template。目前尚不支持不带 chat template 的基础模型（参见 TODO）。

## 期待社区贡献的 TODO

以下内容是理想的社区贡献方向，能让实现更加完整：

- [ ] **非配对 KTO 数据加载器**：支持 `prompt/response/label` 格式的数据集（单个响应附带二元好/坏标签），不再要求成对数据
- [ ] **参考 logprob 缓存**：缓存参考模型的 log-probs，避免每个 batch 重复计算（可参考 Open-Instruct 的 `dpo_tune_cache.py`）
- [ ] **基础模型支持**：为没有 chat template 的模型提供兜底格式化
- [ ] **评估集成**：接入 `log_every` 和 `eval_every` 配置项

## 项目来源

我使用 GPT 5.2 Pro 基于规范实现写了一份计划，由 Claude Code with Opus 4.5 编写代码，期间定期获取 Codex 5.2 xhigh 的反馈，并通过手动调参使配置文件具有代表性的学习曲线。

正因如此，**非常鼓励社区贡献**。我愿意在我的 Spark 上测试高质量的 PR，继续将本项目打造为对 RLHF 和后训练感兴趣的动手爱好者的家园。