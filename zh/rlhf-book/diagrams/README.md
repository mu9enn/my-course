# RLHF Book 图示源文件

本目录包含用于生成插图的源文件。这些是**示意草图**，旨在与编码工具协同迭代，后续将交由专业美术人员进行精修。

## 快速入门

```bash
cd diagrams

# Generate everything
make all

# Or specific targets
make tokens    # Token strip diagrams (reward models)
make tikz      # TikZ diagrams (policy gradients, distillation)
make training-recipes  # MOPD + sequential RL recipes, including dark variants
make figures   # Standalone figures (cartpole, tool_use, etc.)
make clean     # Remove generated files
make help      # List all targets
```

## 目录结构

```
diagrams/
├── specs/          # YAML specifications for diagram content
├── scripts/        # Python/matplotlib generator scripts
├── tikz/           # TikZ/LaTeX diagram sources, organized by topic (see below)
├── generated/      # Output directory (png/, svg/, pdf/)
├── feedback/       # Gemini API diagram review feedback
├── Makefile        # Build automation
└── README.md       # This file (diagram catalog)
```

### `tikz/` 主题文件夹

TikZ 源文件按主题分组（命名依据为所支持的书籍章节）。`make tikz` 会递归查找 `*_tikz.tex`，因此新增一图只需将 `<name>_tikz.tex` 放入对应文件夹即可。

```
tikz/
├── _shared/               # styles_rlhf.tex — shared styles, found via TEXINPUTS
├── 02-related-works/      # Ch 2: rlhf_schematic, rlhf_timeline
├── 03-training-overview/  # Ch 3: rl_loop, rlhf_loop, thermostat_equation
├── 06-policy-gradients/   # Ch 6: reinforce, ppo, grpo, rloo
├── 07-reasoning/          # Ch 7: rlvr_loop
├── 12-synthetic-data/     # Ch 12: knowledge_distillation, synthetic_data_distillation
├── 13-tools/              # Ch 13: tooluse_rl
├── 16-evaluation/         # Ch 16: eval_components
├── 17-product/            # Ch 17: persona_vectors_pipeline
└── pretraining/           # talks/intro: pretraining_next_token
```

任意子文件夹中的源文件都可以直接 `\input{styles_rlhf.tex}` —— Makefile 会自动将 `tikz/_shared` 加入 `TEXINPUTS`。输出的文件名保持扁平化，因此图示生成的 PNG / SVG / PDF 名称不会因其所在文件夹而改变。

### 样式约定

以下约定用于保持插图的一致性与清晰度。RL 回路族（`rl_loop`、`rlhf_loop`、`rlvr_loop`、`tooluse_rl`）共享 `_shared/styles_rl_loop.tex`，其中编码了如下规范：

- **箭头动态效果：起点紧贴，终点略留间隙。** 箭头从所属方块边缘出发，在目标方块前约 5pt 处停止，不与其接触。这比首尾相连的箭头更具动态感。在 TikZ 中体现为箭头样式的 `shorten >=5pt`（头部后缩，尾部保持紧贴）—— 参见 `loop` 样式。
- **不要浪费纵向空间。** 方块之间保持紧凑；避免行与行之间出现过大空白。`-trim` 仅裁剪画布外边距，节点间布局间距由你控制 —— 保持紧凑，使整张图呈现为一个紧凑的整体，而非漂浮在留白中。
- **以 `TIKZ_DENSITY` dpi（默认 800）栅格化。** 线稿图即便在高 DPI 下文件体积依然很小；PDF / SVG 保持矢量格式。如需单次构建提高精度，可用 `make tikz TIKZ_DENSITY=1200`。
- **文本字体为 Latin Modern Sans**（`\usepackage{lmodern}` + `\sfdefault`）—— 基础 TeX Live 不含 Helvetica 度量。

## 工具要求

- **Python + matplotlib**：`uv sync`
- **TikZ / LaTeX**：`brew install --cask basictex`（用于 `make tikz`）
- **SVG 导出**：`brew install pdf2svg`（可选，用于 TikZ 转 SVG）

---

## 完整图示目录

### 词元序列条可视化

水平排列的 token 序列，展示不同奖励模型类型在何处施加监督信号。基于 GSM8K 数学示例。

| 输出文件名 | 脚本 | 说明 | 所在章节 |
|---|---|---|---|
| `pref_rm_training` | `generate_token_strips.py` | 偏好奖励模型：在 EOS 处进行成对比较（chosen vs rejected） | 第 5 章（奖励模型） |
| `prm_training_inference` | `generate_token_strips.py` | 过程奖励模型：在步骤边界处标注 3 类标签（训练 vs 推理） | 第 5 章（奖励模型） |
| `orm_inference` | `generate_token_strips.py` | 结果奖励模型：逐 token 的正确性概率 | 第 5 章（奖励模型） |
| `value_fn_inference` | `generate_token_strips.py` | 价值函数：逐 token 的状态价值 V(s) | 第 5 章（奖励模型） |
| `orm_training` | `generate_multilane_strips.py` | ORM 多车道：token、标签、目标、模型输出 | 第 5 章（奖励模型） |
| `value_fn_training` | `generate_multilane_strips.py` | 价值函数多车道：训练数据流 | 第 5 章（奖励模型） |

**Make 目标：** `make tokens`

### TikZ / LaTeX 架构图

框线箭头流程图，覆盖 RLHF 架构及相关训练概念。许多图示使用了 `tikz/_shared/styles_rlhf.tex` 中的共享样式。

| 输出文件名 | 源文件 | 说明 | 所在章节 |
|---|---|---|---|
| `rl_loop_tikz` | `tikz/03-training-overview/rl_loop_tikz.tex` | 标准 RL 反馈回路：智能体 ↔ 环境，含 s/a/r | 第 3 章（训练概览） |
| `rlhf_loop_tikz` | `tikz/03-training-overview/rlhf_loop_tikz.tex` | RLHF 回路：训练数据 → 智能体 → 生成结果 → 奖励模型 → 标量奖励 | 第 3 章（训练概览） |
| `rlhf_schematic_tikz` | `tikz/02-related-works/rlhf_schematic_tikz.tex` | RLHF 回路：RL 算法、环境、奖励预测器、人类反馈（Christiano 等 2017） | 第 2 章（相关工作） |
| `rlhf_timeline_tikz` | `tikz/02-related-works/rlhf_timeline_tikz.tex` | 三个时代中关键 RLHF 发展时间线 | 第 2 章（相关工作） |
| `thermostat_equation_tikz` | `tikz/03-training-overview/thermostat_equation_tikz.tex` | 用恒温器类比 RL 目标函数 | 第 3 章（训练概览） |
| `rlhf_mopd_tikz` | `tikz/03-training-overview/rlhf_mopd_tikz.tex` | 共享 SFT → 领域 SFT 教师 → 领域 RL 教师 → MOPD → 单一学生 | 第 3 章（训练概览） |
| `rlhf_sequential_rl_tikz` | `tikz/03-training-overview/rlhf_sequential_rl_tikz.tex` | 整体流程：SFT → 推理 RL → 智能体 RL → 通用 RL | 第 3 章（训练概览） |
| `reinforce_tikz` | `tikz/06-policy-gradients/reinforce_tikz.tex` | REINFORCE：基础策略梯度算法 | 第 6 章（策略梯度） |
| `ppo_tikz` | `tikz/06-policy-gradients/ppo_tikz.tex` | PPO：单一输出、价值网络、GAE、奖励中的 KL 项 | 第 6 章（策略梯度） |
| `grpo_tikz` | `tikz/06-policy-gradients/grpo_tikz.tex` | GRPO：一组 G 个输出、组归一化、损失中的 KL | 第 6 章（策略梯度） |
| `rloo_tikz` | `tikz/06-policy-gradients/rloo_tikz.tex` | RLOO：K 个输出、留一法基线、奖励中的 KL | 第 6 章（策略梯度） |
| `rlvr_loop_tikz` | `tikz/07-reasoning/rlvr_loop_tikz.tex` | RLVR 回路：带可验证奖励的 RLHF 回路（正确时 r = γ，否则 r = 0） | 第 7 章（推理） |
| `knowledge_distillation_tikz` | `tikz/12-synthetic-data/knowledge_distillation_tikz.tex` | 知识蒸馏流水线 | 第 12 章（合成数据） |
| `synthetic_data_distillation_tikz` | `tikz/12-synthetic-data/synthetic_data_distillation_tikz.tex` | 合成数据蒸馏流程 | 第 12 章（合成数据） |
| `sdpo_tikz` | `tikz/12-synthetic-data/sdpo_tikz.tex` | SDPO 自蒸馏：基于示例的条件自教师与仅输入问题的学生之间，在采样生成结果上的逐 token 反向 KL 散度 | 第 12 章（合成数据） |
| `tooluse_rl_tikz` | `tikz/13-tools/tooluse_rl_tikz.tex` | 工具使用 RL：智能体 ↔ 环境/工具 沿轨迹交互，轨迹结束时给予评分奖励 | 第 13 章（工具） |
| `eval_components_tikz` | `tikz/16-evaluation/eval_components_tikz.tex` | 运行评估的各组件：工具框架 / 沙盒 / 硬件、提示 → LLM → 评分器（基于 Florian Brand 的方法）；通过 `\def\evalstage{1..3}` 分阶段展示 | 第 16 章（评估） |
| `persona_vectors_pipeline_tikz` | `tikz/17-product/persona_vectors_pipeline_tikz.tex` | 人格向量提取与引导流水线 | 第 17 章（产品） |
| `pretraining_next_token_tikz` | `tikz/pretraining/pretraining_next_token_tikz.tex` | 入门级下一个词元预测示例，含目标词元与损失直觉 | 演讲/演示 |

**Make 目标：** `make tikz`

对于两张训练食谱图，使用 `make training-recipes` 仅构建其浅色 PDF / SVG / PNG 及透明暗色 PNG 版本。它们共享 `tikz/_shared/styles_training_recipes.tex`，与第 3 章 `rlhf-basic` 和 `rlhf-complex` 图中的空心方框和灰色开放箭头一致。参见[食谱说明](tikz/03-training-overview/README.md)获取源文件、有意简化说明、预览图及可直接嵌入章节的标记。

### 独立插图

针对特定概念的独立图示。

| 输出文件名 | 脚本 | 说明 | 所在章节 |
|---|---|---|---|
| `cartpole` | `generate_cartpole.py` | CartPole 环境：推车、摆杆、状态变量、动作 | 第 6 章（策略梯度） |
| `tool_use_generation` | `generate_tool_use.py` | 工具使用：生成与外部执行交替进行 | 第 13 章（工具） |
| `interleaved_thinking` | `generate_interleaved_thinking.py` | 推理模型的思考 / 回答块交替呈现 | 演讲/演示 |

**Make 目标：** `make figures`

### 数据规格

| 文件 | 说明 |
|---|---|
| `specs/reward_models.yaml` | 所有奖励模型类型的 token 示例、高亮位置、标注信息 |

---

## 工作流程

1. **编辑规格**：在 `specs/` 中编辑或直接修改脚本
2. **生成图示**：运行 `make all`（或指定目标）
3. **审查输出**：查看 `generated/{png,svg,pdf}/` 中的结果
4. **获取 AI 反馈**：通过 `/gemini-feedback diagrams/generated/png/<name>.png` 提交评审
5. **复制评审通过版本**：放入消费方资源目录（章节用 `book/images/`，幻灯片用对应的 `teach/**/assets/`）
6. **提交**：将图示源文件与评审通过的资源一并提交至消费方资源目录；`diagrams/generated/` 作为构建输出，保留在 `.gitignore` 中

## 移交给美术人员

需要专业精修时：

1. 将所有图示导出为 SVG
2. 提供 YAML 规格作为语义化文档
3. 附上样式指南（字体、颜色、描边宽度）
4. 使用一致的命名规范：`fig_rm_{type}_{variant}.svg`