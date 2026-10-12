# 训练流程图表

这两张示意图扩展了第 3 章图 5 和图 6 的视觉语言（`book/images/rlhf-basic.png` 与 `rlhf-complex.png`）：带轮廓的矩形模型框、灰色开放式箭头、圆角连接线，以及斜体的训练操作标签。矩形代表模型检查点（checkpoint），箭头描述它们如何被训练。所有连接线均绘制在背景层上，位于填充色矩形及其轮廓的后方。在多教师同策略蒸馏（MOPD）示意图中，步骤标签位于其箭头的下方。两条一行的 "Domain / SFT" 和 "Domain / RL" 标签居中对齐于下方两条水平箭头之间；加宽间距可避免标签与矩形重叠。

共享样式文件位于 `../_shared/styles_training_recipes.tex`。定义 `\figdark=1` 即可使用站点默认的板岩色（slate）配色方案。深色 PNG 具有透明画布、板岩色填充矩形、浅色文字、轮廓和箭头。

## 专业教师与 MOPD

![专业教师与多教师同策略蒸馏（MOPD）](../../../book/images/rlhf-mopd.png)

`rlhf_mopd_tikz.tex` 展示了一个初始的共享 SFT 检查点，随后为每个领域教师（domain teacher）分别进行 SFT 与 RL，最后通过多教师同策略蒸馏（MOPD）将知识蒸馏到一个通用学生模型中。行号 `1`、`2`、…、`N` 代表任意领域，而非某个模型实际拥有的教师数量。每行教师标签仅标注一个代表性领域：写作（Writing）、编码（Coding）或数学（Math）。MOPD 利用教师在学生模型生成序列（rollout）上的输出分布来传递知识，而不是对权重进行平均。学生模型的初始化和生成序列 / 损失机制不在本概述的覆盖范围。

这是按要求整理出的通用训练流程，灵感来源于 [MiMo-V2-Flash 报告 §4.1](https://arxiv.org/html/2601.02780v1#S4.SS1) 与 [Nemotron 3 Ultra 报告 §3](https://research.nvidia.com/labs/nemotron/files/NVIDIA-Nemotron-3-Ultra-Technical-Report.pdf)，正如 [课程幻灯片](https://rlhfbook.com/teach/course/conversation-01/#14) 中讨论的那样。本示意图并非对其中任一完整配方的精确复现。MiMo 描述的是专用 RL/SFT，并不要求每位教师都必须遵循相同的两个阶段。Nemotron 额外加入了学生 RL、多样化的教师路径、多轮蒸馏以及其他收尾步骤，这些都被有意省略了。

## 顺序强化学习

![顺序强化学习](../../../book/images/rlhf-sequential-rl.png)

`rlhf_sequential_rl_tikz.tex` 展示了总体 SFT 之后，按顺序对同一个模型的连续检查点分别执行推理 RL、智能体 RL 和通用 RL。此处的阶段顺序来自附带的 **GLM-5** 幻灯片以及 [GLM-5 技术报告 §3](https://arxiv.org/html/2602.15763v1#S3)。由于参考来源是 GLM-5，本示意图并不声称这是 GLM-5.2 的特定配方。它仅孤立地展示了顺序 RL 各阶段：完整的 GLM-5 配方还包含最终的同策略跨阶段蒸馏（§3.5），此处未予呈现。

## 构建与章节素材

从仓库根目录执行：

```bash
# Both figures; final PNGs at the book's 400 dpi convention.
make -C diagrams training-recipes TIKZ_DENSITY=400

cp diagrams/generated/png/rlhf_mopd_tikz.png book/images/rlhf-mopd.png
cp diagrams/generated/png/rlhf_mopd_tikz-dark.png book/images/rlhf-mopd-dark.png
cp diagrams/generated/svg/rlhf_mopd_tikz.svg book/images/rlhf-mopd.svg
cp diagrams/generated/png/rlhf_sequential_rl_tikz.png book/images/rlhf-sequential-rl.png
cp diagrams/generated/png/rlhf_sequential_rl_tikz-dark.png book/images/rlhf-sequential-rl-dark.png
cp diagrams/generated/svg/rlhf_sequential_rl_tikz.svg book/images/rlhf-sequential-rl.svg
```

构建目标需要 LaTeX、ImageMagick，以及 `pdf2svg` 或 Poppler 的 `pdftocairo`。默认 PNG 分辨率为 800 dpi；使用 300 即可快速预览。PDF / SVG 导出保持矢量格式。所有中间文件和生成输出均保留在 `diagrams/generated/` 下；经审核的网络与印刷素材通过 `book/images/` 进行版本管理。深色 PNG 需在深色背景上预览。

MOPD 示意图位于第 3 章 "Transition to MOPD and Agents" 小节中 DeepSeek R1 内容之后，附带深色模式素材。顺序 RL 示意图仍可作为独立素材使用；章节现在使用原始 GLM-5 Figure 5 来展示完整的混合配方，包括跨阶段蒸馏（提取细节见下文）。两张示意图的示例标记如下：

```markdown
![A schematic of specialist post-training: shared SFT, domain-specific SFT and RL, then multi-teacher on-policy distillation into one student.](images/rlhf-mopd.png){#fig:rlhf-mopd data-dark-src="images/rlhf-mopd-dark.png"}

![A schematic of sequential post-training: overall SFT followed by reasoning, agentic, and general reinforcement learning.](images/rlhf-sequential-rl.png){#fig:rlhf-sequential-rl data-dark-src="images/rlhf-sequential-rl-dark.png"}
```

## GLM-5 Figure 5 复现

`book/images/glm5-pipeline.png` 与 `.svg` 复现了 GLM-5 团队论文 *GLM-5: from Vibe Coding to Agentic Engineering* 中的 Figure 5，来源 [arXiv:2602.15763v2](https://arxiv.org/abs/2602.15763v2)，遵循 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可。原图的构图和配色均被保留，包括两套站点主题下的白色背景。该图替代了第 3 章中仅展示顺序 RL 的示意图；其已有的图片锚点（anchor）已保留。

裁剪时排除了论文说明文字及 PDF 第 4 页周边的正文。使用的坐标为 PDF 点单位（以页面左下角为原点）：`(107, 496.331, 505.19508, 721.00016)`，已为嵌入的图预留了一点的边距。PNG 以 400 dpi 渲染（2213 × 1249 像素），PDF 与 SVG 保持矢量格式。源 PDF 的 SHA-256 校验值：

`e20742ff36e08dc361de6973f7f72ad38e107edf8fd92d2a777a8428fc9b8f0e`。

从仓库根目录复现（需已安装 `pypdf` 和 Poppler）：

```bash
curl -L --fail https://arxiv.org/pdf/2602.15763v2 \
  -o diagrams/generated/pdf/glm5-source.pdf
uv run python diagrams/scripts/extract_glm5_pipeline.py
cp diagrams/generated/png/glm5-pipeline.png book/images/
cp diagrams/generated/svg/glm5-pipeline.svg book/images/
```

## Nature Figure 2 复现

`book/images/deepseek-r1-pipeline.png` 与 `.svg` 复现了 Guo 等（DeepSeek-AI 团队）发表于 *Nature* **645**，633–638（2025）中的 Figure 2，doi：[10.1038/s41586-025-09422-z](https://doi.org/10.1038/s41586-025-09422-z)。[已发表 PDF](https://www.nature.com/articles/s41586-025-09422-z.pdf) 第 637 页（PDF 第 5 页）规定，除非另有版权声明，文章及其图表均遵循 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可。[Figure 2](https://www.nature.com/articles/s41586-025-09422-z/figures/2) 无单独限制。复现后的图片仍为 © The Author(s) 2025，CC BY 4.0。章节说明文字链接了论文和许可信息；提取细节记录如下。

图像内容未作修改：PDF 按印刷页码 635（PDF 第 3 页）上的 Figure 2 进行裁剪，边距设为两点，排除了出版商的说明文字和页面正文。裁剪矩形为 `(81.736, 69.398, 514.636, 276.769)`（PDF 点单位，从页面左下角测量）。PNG 输出为 2405 × 1153 像素（400 dpi）；SVG 保留矢量路径。裁剪后的 PDF 保留在 `diagrams/generated/pdf/` 中；章节用 PNG 保留了原始白色背景。

从仓库根目录复现（需已安装 `pypdf` 和 Poppler）：

```bash
mkdir -p diagrams/generated/{pdf,png,svg}
curl -L --fail 'https://www.nature.com/articles/s41586-025-09422-z.pdf' \
  -o diagrams/generated/pdf/deepseek-r1-nature-source.pdf
uv run python - <<'PYTHON'
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject

reader = PdfReader('diagrams/generated/pdf/deepseek-r1-nature-source.pdf')
page = reader.pages[2]
box = RectangleObject((81.736, 69.398, 514.636, 276.769))
for name in ('mediabox', 'cropbox', 'trimbox', 'bleedbox', 'artbox'):
    setattr(page, name, box)
writer = PdfWriter()
writer.add_page(page)
writer.add_metadata({
    '/Title': 'DeepSeek-R1 multistage pipeline (Nature Figure 2)',
    '/Author': 'Daya Guo et al. (DeepSeek-AI Team)',
    '/Subject': 'Figure 2 from Nature 645, 633–638 (2025), doi:10.1038/s41586-025-09422-z. CC BY 4.0. Cropped to the original figure; artwork unchanged.',
})
with Path('diagrams/generated/pdf/deepseek-r1-pipeline.pdf').open('wb') as output:
    writer.write(output)
PYTHON
pdftocairo -svg diagrams/generated/pdf/deepseek-r1-pipeline.pdf \
  diagrams/generated/svg/deepseek-r1-pipeline.svg
pdftoppm -cropbox -r 400 -png -singlefile \
  diagrams/generated/pdf/deepseek-r1-pipeline.pdf \
  diagrams/generated/png/deepseek-r1-pipeline
cp diagrams/generated/png/deepseek-r1-pipeline.png book/images/
cp diagrams/generated/svg/deepseek-r1-pipeline.svg book/images/
```

源 PDF 在提取时的 SHA-256 校验值为

`916fdaafc3b44143a9744481d079744f773d73d06372f82b1dba1076525927f2`。

Nature 还提供了一份 [官方 1787 × 847 PNG](https://media.springernature.com/full/springer-static/image/art%3A10.1038%2Fs41586-025-09422-z/MediaObjects/41586_2025_9422_Fig2_HTML.png)，用于验证矢量裁剪是否完整保留了原图内容。