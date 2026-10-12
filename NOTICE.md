# 来源、改编与许可

本仓库由 mu9enn 组织维护，是独立、非官方的中文教学改编项目。中文内容由 Claude Code 调用 PJLab `Qwen3.6-35B-A3B-FP8` 辅助生成，并进行有限人工抽查；尚不意味着原作者认可或逐篇人工审核。

## RLHF Book

- 原作者：Nathan Lambert。
- 原仓库：https://github.com/natolambert/rlhf-book
- 英文网站：https://rlhfbook.com
- 参考版本：`eecc49e1e1daf1be670d7242eb090240b5bb0f04`。
- 原文章节与中文教学改编遵循 [CC BY-NC-SA 4.0](zh/rlhf-book/LICENSE-CHAPTERS)。
- 原代码与上游许可范围内的其他材料遵循 [MIT](zh/rlhf-book/LICENSE-CODE)。
- 修改包括：中文转述、段落衔接与术语解释，明确标识的译者注及少量自测题。原有代码、公式、引用和资源保持原样。
- 照片、截图和第三方图像沿用上游的权利说明；本项目不为这些内容另行授予许可。

## Missing Semester

- 原作者：Anish Athalye、Jon Gjengset、Jose Javier Gonzalez Ortiz，及原仓库所列贡献者。
- 原仓库：https://github.com/missing-semester/missing-semester
- 英文网站：https://missing.csail.mit.edu
- 参考版本：`1d695c94ccafdce3f06d6b9dfe3e6f106097693a`。
- 原课程及其中文改编遵循 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)，参见[原课程许可文件](original/missing-semester/license.md)。
- 本轮主要制作 RLHF Book；Missing Semester 尚未完成整套汉化。

## Agent

本仓库原创的调度脚本、prompt 和 agent 文档采用 [MIT License](agent/LICENSE)。这不改变课程正文、图像及其他上游材料的许可。

`original/` 保存 Git submodule 引用，不把英文仓库历史并入本项目；版本固定于相应 gitlink。`agent/sources.lock.json` 也记录相同版本，便于追溯。
