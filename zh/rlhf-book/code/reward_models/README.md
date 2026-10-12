# 奖励模型训练

![RLHF 训练循环概览。](../../book/images/rlhf-overview.png)

本节为 [RLHF Book](https://rlhfbook.com) 提供奖励模型训练的示例实现。
详细的数学推导和直觉解释参见 **第五章：奖励模型**。

> **⚠️ 开发中**：本实现为实验性质。目前三种奖励模型均支持通过配置文件驱动训练并附带验证日志，但数据集和评估环节仍需进一步完善。欢迎贡献！

## 算法

| 算法 | 脚本 | 核心思想 |
|------|------|----------|
| **ORM**（结果奖励模型） | `train_orm.py` | 对完整回答打分 |
| **偏好奖励模型（Preference RM）** | `train_preference_rm.py` | 基于 Bradley-Terry 模型的成对偏好建模 |
| **PRM**（过程奖励模型） | `train_prm.py` | 对中间推理步骤打分 |

## 参考运行

| 算法 | wandb 日志 | 状态 |
|------|-----------|------|
| **ORM** | [run](https://wandb.ai/rlhf-book/core/runs/3gkoqb7f) | 实验性 |
| **偏好奖励模型** | [run](https://wandb.ai/rlhf-book/core/runs/1g3y9bcc) | 实验性 |
| **PRM** | [run](https://wandb.ai/rlhf-book/core/runs/iv4d966d) | 实验性 |

## 快速开始

```bash
cd code/
uv sync

# Train ORM
WANDB_PROJECT=rlhf-book uv run python -m reward_models.train_orm \
    --config reward_models/configs/orm.yaml

# Train Preference RM (Bradley-Terry)
WANDB_PROJECT=rlhf-book uv run python -m reward_models.train_preference_rm \
    --config reward_models/configs/preference_rm.yaml

# Train PRM
WANDB_PROJECT=rlhf-book uv run python -m reward_models.train_prm \
    --config reward_models/configs/prm.yaml
```

## 奖励模型配置

ORM、PRM 和偏好奖励模型脚本分别使用 `reward_models/configs/orm.yaml`、
`reward_models/configs/prm.yaml` 和 `reward_models/configs/preference_rm.yaml` 作为配置文件。
如果你只想运行小规模实验，可以复制相应的 YAML 文件并修改副本。

默认配置在 5,000 对 UltraFeedback 偏好数据上训练 Qwen3-0.6B，关键超参数如下：

- 有效批次大小（effective batch size）：16
- 学习率：5e-5
- 训练轮数（epochs）：2
- 验证集划分比例：10%
- 学习率调度：线性预热 + 线性衰减
- 每 25 次优化器步记录一次验证日志

这些超参数来自一次小型搜索实验，旨在提供一个更清晰的**教育基准**，而非普遍最优的选择。

奖励模型训练通常以约一轮（one epoch）来降低过拟合风险。本示例使用两轮的缘故是：在本地 5,000 对数据的小规模搜索中，两轮训练产出的验证曲线更加清晰。但读者在实际使用时应密切观察第二轮中的 `val/loss`（验证损失）和 `val/accuracy`（验证准确率）指标；如果验证指标出现退化，应当减少 `epochs` 的值。

## 已知问题

- 训练曲线可能较为波动——超参数尚待优化
- 数据集的选择与预处理可能需要进一步打磨
- 模型架构为教育目的作了简化

## 面向社区贡献的 TODO

- [ ] 在标准基准（RewardBench）上开展评估
- [ ] 加入数据增强和课程学习（curriculum learning）
