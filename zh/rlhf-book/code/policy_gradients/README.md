# 策略梯度方法（Policy Gradient Methods）

![RLHF 训练循环概述。](../../book/images/rlhf-overview.png)

面向 [RLHF Book](https://rlhfbook.com) 的教学用策略梯度算法实现。
数学推导与直觉分析见 **第六章：策略梯度方法**。
安装、配置与内存需求见父目录 [`code/README.md`](../README.md)。

## 算法一览

| 算法 | 配置文件 | 核心思想 |
|------|----------|----------|
| **REINFORCE** | `reinforce.yaml` | [Williams (1992)](https://link.springer.com/article/10.1007/BF00992696) —— 基础策略梯度 |
| **RLOO** | `rloo.yaml` | REINFORCE Leave-One-Out（逐样本剔除）（[Ahmadian et al., 2024](https://arxiv.org/abs/2402.14740)） |
| **PPO** | `ppo.yaml` | 近端策略优化（Proximal Policy Optimization）（[Schulman et al., 2017](https://arxiv.org/abs/1707.06347)） |
| **GRPO** | `grpo.yaml` | 组相对策略优化（Group Relative Policy Optimization）（[Shao et al., 2024](https://arxiv.org/abs/2402.03300)） |
| **Dr. GRPO** | `drgrpo.yaml` | Dr. GRPO —— 消除长度与难度偏差（[Liu et al., 2025](https://arxiv.org/abs/2503.20783)） |
| **GSPO** | `gspo.yaml` | 组序列策略优化（Group-Sequence Policy Optimization）（[Zheng et al., 2025](https://arxiv.org/abs/2505.13818)） |
| **CISPO** | `cispo.yaml` | 截断重要性采样策略优化（Clipped Importance Sampling PO）（[MiniMax, 2025](https://arxiv.org/abs/2506.13585)） |
| **SAPO** | `sapo.yaml` | 软自适应策略优化（Soft Adaptive Policy Optimization）（[Gao et al., 2025](https://arxiv.org/abs/2511.20347)） |
| **DAPO** | `dapo.yaml` | 解耦截断与动态采样策略优化（Decoupled Clip and Dynamic sAmpling Policy Optimization）（[Yu et al., 2025](https://arxiv.org/abs/2503.14476)） |
| **MaxRL** | `maxrl.yaml` | 最大似然强化学习（Maximum Likelihood Reinforcement Learning）（[Tajwar et al., 2026](https://arxiv.org/abs/2602.02710)） |

> **译者注**：以上算法均属于策略梯度家族或与其等价的直接对齐方法。对于 RLHF 后训练而言，它们的不同之处在于：如何估算策略梯度、如何在更新中约束策略偏离初始模型、以及如何利用奖励信号来引导生成质量。第六章会逐一推导。

## 参考运行结果

| 算法 | wandb 链接 | 状态 |
|------|------------|------|
| **REINFORCE** | [run](https://wandb.ai/rlhf-book/core/runs/0uqbq4oz) | ✅ 已验证 |
| **RLOO** | [run](https://wandb.ai/rlhf-book/core/runs/07xeasn8) | ✅ 已验证 |
| **PPO** | [run](https://wandb.ai/rlhf-book/core/runs/ku3r3g9j) | ✅ 已验证 |
| **GRPO** | [run](https://wandb.ai/rlhf-book/core/runs/vjp7lgdi) | ✅ 已验证 |
| **Dr. GRPO** | [run](https://wandb.ai/rlhf-book/core/runs/a1swuynq) | ✅ 已验证 |
| **GSPO** | [run](https://wandb.ai/rlhf-book/core/runs/10sxytli) | ✅ 已验证 |
| **CISPO** | [run](https://wandb.ai/rlhf-book/core/runs/6dg0m06n) | ✅ 已验证 |
| **SAPO** | [run](https://wandb.ai/rlhf-book/core/runs/79608nwk) | ✅ 已验证 |
| **DAPO** | [run](https://wandb.ai/rlhf-book/core/runs/db1pipip) | ✅ 已验证 |
| **MaxRL** | [run](https://wandb.ai/rlhf-book/core/runs/fdowf1se) | ✅ 已验证 |

## 快速开始

```bash
cd /path/to/rlhf-book/code
uv sync

# GRPO (recommended starting point)
uv run python -m policy_gradients.train --config policy_gradients/configs/grpo.yaml

# REINFORCE baseline
uv run python -m policy_gradients.train --config policy_gradients/configs/reinforce.yaml

# PPO with value function
uv run python -m policy_gradients.train --config policy_gradients/configs/ppo.yaml
```

## 社区贡献 TODO

- [ ] 在保留的推理基准测试（held-out reasoning benchmarks）上补充评估结果