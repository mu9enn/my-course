# RLHF Book

一本全面介绍基于人类反馈的强化学习（Reinforcement Learning from Human Feedback，简称 RLHF）的指南（也是对大模型后训练方法的广泛导论）。

**[在线阅读](https://rlhfbook.com)** | **[Manning](https://hubs.la/Q03Tc3cf0) 或 [Amazon](https://amzn.to/4cwCDJQ) 订购纸质版** | **加入 [Discord 社区](https://discord.gg/yz5AwK4gBR)**

本书是我试图开源自己在 ChatGPT 引发的大模型爆发之后，于开源模型前沿工作所积累的全部知识的努力。
写作之初，许多成熟的方法——例如拒绝采样（rejection sampling）——并无权威参考文献。
另一方面，业界用于让模型更加人性化的实践——俗称角色训练（Character Training）——也缺乏公开的学术研究。
在我看来，将这些内容系统化地记录下来、学习基础知识、仔细甄选参考文献（在如今 AI 生成内容泛滥的时代尤为如此），以及中间的种种探索，必将为后来者提供一个极佳的起点。

如今，本仓库已包含代码，并作为希望学习者的大本营。
你应该用代码助手来提问。
你应该购买纸质书，因为真实世界很重要。
你应该阅读那些为你量身定制的 AI 输出内容。

我也希望能继续建设教学资源，比如开源幻灯片、更多的学习方式。
说到底，由于人类偏好本质上难以测量，RLHF 将永远不会是一个被完全解决的问题。

感谢阅读。
感谢你的反馈和社区参与。

—— Nathan Lambert，@natolambert

## 仓库结构

```
rlhf-book/
├── book/                   # Book source and build files
│   ├── chapters/           # Markdown source (01-introduction.md, etc.)
│   ├── images/             # Figures referenced in chapters
│   ├── assets/             # Brand assets (covers, logos)
│   ├── templates/          # Pandoc templates (HTML, PDF, EPUB)
│   ├── scripts/            # Build utilities
│   └── data/               # Library data
├── code/                   # Reference implementations
│   ├── instruction_tuning/ # SFT a base model with chat templates
│   ├── policy_gradients/   # PPO, REINFORCE, GRPO, RLOO
│   ├── reward_models/      # Preference RM, ORM, PRM training
│   ├── direct_alignment/   # DPO and variants
│   ├── rejection_sampling/ # Best-of-N rejection sampling
│   └── distillation/       # On-policy distillation (SDPO)
├── diagrams/               # Diagram source files
│   ├── scripts/            # Python generation scripts
│   ├── tikz/               # LaTeX/TikZ sources
│   └── specs/              # YAML specifications
├── teach/                  # Teaching materials (courses, slides)
├── build/                  # Generated output (git-ignored)
└── Makefile                # Build system
```

## 代码库

`code/` 中包含了 RLHF 算法的参考实现：
- 指令微调（SFT：使用 chat templates 微调基础模型）
- 策略梯度方法（PPO、REINFORCE、GRPO、RLOO 等）
- 奖励模型训练（偏好 RM、ORM、PRM）
- 直接对齐方法（DPO 及其变体）
- 拒绝采样（Best-of-N）
- 同策略蒸馏（SDPO）

详细的环境配置与使用说明请见 [code/README.md](code/README.md)。

## 书稿源码

书稿源码文件位于 `book/`。本地构建方式：

```bash
make html   # Build HTML site
make pdf    # Build PDF (requires LaTeX)
```

详细的构建说明请见 [book/README.md](book/README.md)。

## 图示

`diagrams/` 目录中包含书中所用插图的源文件。这些文件设计为可复用——可用于演讲、博客文章或你自己的学习资料。生成方式如下：

```bash
cd diagrams && make all
```

## 引用方式

对于网站与 arXiv 版本，请使用 arXiv 导出的引用格式：

```bibtex
@misc{lambert2025reinforcementlearninghumanfeedback,
  title         = {Reinforcement Learning from Human Feedback},
  author        = {Nathan Lambert},
  year          = {2025},
  eprint        = {2504.12501},
  archivePrefix = {arXiv},
  primaryClass  = {cs.LG},
  url           = {https://arxiv.org/abs/2504.12501},
}
```

对于 Manning 纸质版：

```bibtex
@book{lambert2026reinforcement,
  author       = {Nathan Lambert},
  title        = {Reinforcement Learning from Human Feedback: Alignment and post-training of {LLMs}},
  year         = {2026},
  publisher    = {Manning Publications},
  isbn         = {9781633434301},
  url          = {https://www.manning.com/books/reinforcement-learning-from-human-feedback},
}
```

## 许可证

- `book/chapters`：[CC-BY-NC-SA-4.0](LICENSE-CHAPTERS)
- 其余所有内容（`code/`、`diagrams/`、`scripts/` 等）：[MIT](LICENSE-CODE)
- 请注意，`book/images/` 中的部分图片为无版权信息的照片或截图。 

## 贡献者

虽然我是这个项目唯一的署名"作者"和创建者，但我非常幸运地获得了众多早期读者的贡献。这些贡献极大地加速了编辑进度，并且直接向书中贡献了实质性内容。我很乐意向有实质性贡献的读者免费寄送本书，也相信互联网上的善意终将以一种意想不到的方式回馈他们。

查看所有 [贡献者](https://github.com/natolambert/rlhf-book/graphs/contributors)。

注：*由于我曾错误地将提交关联到已无法访问的 Ai2 邮箱，提交历史丢失了我大部分的追踪记录，RIP！*

### 翻译版本

读者在自己的仓库中维护本书的非官方翻译版本。
这些是社区项目——独立于官方纸质版及其专业翻译——以相同的 CC-BY-NC-SA 许可证发布，并需向本书注明出处：

- 简体中文：[jweihe/RLHF-book-Chinese](https://github.com/jweihe/RLHF-book-Chinese)
- 简体中文：[around133/rlhf-book-zh](https://github.com/around133/rlhf-book-zh)

要添加你的翻译版本：请保留在你自己的仓库中（翻译版本不会合并到此仓库），遵循上述许可证条款，明确标注为社区翻译，然后提交一个 PR 将其添加到本列表以及首页的 Ecosystem 部分（`book/templates/html.html`）。

### AI 使用政策

我想明确记录自己是如何利用 AI 辅助本书的编辑与创作的（以及我对贡献者的期望）。
这本书成书于一个有趣的时间点——AI 模型作为知识工作工具，从"有用"转变为"不可或缺"。

本书的核心部分写作时，语言模型对于非虚构写作来说近乎毫无用处；这大约对应本书的前 10 章——那是我在学习中后训练方法时写的个人笔记。
初稿几乎完全是手工编写的（包括所有的拼写错误，这些都记录在 git 历史中）。
其余许多章节和附录的内容则直接改编自我的个人通讯 [interconnects.ai](https://interconnects.ai/)。
这部分文字具有强烈的个人风格，仅使用最轻微的 AI 编辑来维持直觉表达的完整性。
一章中数学和代码越少，我使用的 AI 就越少。

在编辑过程中，我采用的默认工作流是：将人类编辑建议的修改清单连同上下文传递给 Claude Code，让它逐一应用各项编辑。
在这种格式下，我会阅读上下文并编写修复方案。
对于简单的拼写错误、明显的错误，或只需修改少量字数的情况，Claude 可以直接完成编辑。
更复杂的语言编辑则由我亲手打磨，通常是我重写各种句子并增补内容。
我也经常直接在 Cursor 中写作，然后让 Claude 帮我处理 GitHub 上的事务。

如果你密切关注我的写作，你会发现本书与 Interconnects（我的博客）的区别在于：我在本仓库中让 AI 代理执行我建议的编辑，而在博客上我则刻意将所有工作都手动完成。
这在很大程度上是规模与复杂度所致。

对于数学比重较大的章节，AI 模型在处理 LaTeX 公式和基础代码片段方面表现出难以置信的效用。
这些部分更多是 AI 模型的直接输出——因为我手动编写 LaTeX 会花费大量时间。
然后，我会再次通过人工检查以及 GPT-Pro 模型审查来核对数学和代码。

AI 模型在 `diagrams/` 和 `code/` 中的使用更为广泛——我将这些视为与最新模型的一种趣味探索，围绕着书中实质性内容展开。

本书的纸质版经过了额外的、大量的文字编辑，语体风格过渡为更标准的科技教科书风格。

所有新增的书稿内容显然应首先由人类撰写，然后可以用 AI 进行编辑——这反映了上述我的工作流。
在 GitHub PR 中出现明显的 AI 生成内容几乎一定会导致该提交不会被合并。
