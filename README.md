# My Course · 中文技术课程

将优秀的英文开放教材制作成可直接学习的中文教学材料：保留推导、例子、代码与练习，让概念之间的联系更清楚；新增解释明确标注为译者注。

这是 mu9enn 维护的独立、非官方改编。内容由 **Claude Code + Qwen3.6-35B-A3B-FP8** 辅助制作，并进行有限人工抽查。技术结论、命令适用环境及长文完整性仍欢迎读者校对。来源、署名与许可见 [NOTICE.md](NOTICE.md)。

## 从这里开始

| 课程 | 中文入口 | 本轮范围 |
| --- | --- | --- |
| RLHF Book · Nathan Lambert | [书稿说明](zh/rlhf-book/README.md) · [第 1 章](zh/rlhf-book/book/chapters/01-introduction.md) · [代码说明](zh/rlhf-book/code/README.md) · [配套课程](zh/rlhf-book/teach/README.md) | 17 章、4 篇附录，以及代码、讲义与构建说明，共 57 篇 Markdown |
| Missing Semester · MIT | [课程首页](zh/missing-semester/index.md) · [汉化进度](zh/missing-semester/TRANSLATION.md) | 保留上游各年份结构，已生成 44/44 篇；以逐篇状态为准 |

RLHF 本轮已结束，已生成 57/57 篇；逐篇状态见 [汉化进度](zh/rlhf-book/TRANSLATION.md)。图片和图内英文、代码注释、参考文献、网站模板及部分维护说明沿用原文，不属于整站界面汉化。

## RLHF Book 阅读目录

推荐先通读第 1–3 章，理解流水线，再按学习目的进入算法、数据和应用部分。代码示例保留上游实现，阅读代码说明前先确认其依赖和硬件要求。

| 章节 | 主题 |
| --- | --- |
| [01](zh/rlhf-book/book/chapters/01-introduction.md) | 引言 |
| [02](zh/rlhf-book/book/chapters/02-related-works.md) | RLHF 简史 |
| [03](zh/rlhf-book/book/chapters/03-training-overview.md) | 训练总览 |
| [04](zh/rlhf-book/book/chapters/04-instruction-tuning.md) | 指令微调 |
| [05](zh/rlhf-book/book/chapters/05-reward-models.md) | 奖励模型 |
| [06](zh/rlhf-book/book/chapters/06-policy-gradients.md) | 策略梯度方法 |
| [07](zh/rlhf-book/book/chapters/07-reasoning.md) | 推理 |
| [08](zh/rlhf-book/book/chapters/08-direct-alignment.md) | 直接对齐方法 |
| [09](zh/rlhf-book/book/chapters/09-rejection-sampling.md) | 拒绝采样 |
| [10](zh/rlhf-book/book/chapters/10-preferences.md) | 人类偏好 |
| [11](zh/rlhf-book/book/chapters/11-preference-data.md) | 偏好数据 |
| [12](zh/rlhf-book/book/chapters/12-synthetic-data.md) | 合成数据 |
| [13](zh/rlhf-book/book/chapters/13-tools.md) | 工具使用 |
| [14](zh/rlhf-book/book/chapters/14-over-optimization.md) | 过度优化 |
| [15](zh/rlhf-book/book/chapters/15-regularization.md) | 正则化 |
| [16](zh/rlhf-book/book/chapters/16-evaluation.md) | 评估 |
| [17](zh/rlhf-book/book/chapters/17-product.md) | 产品与角色训练 |
| [附录 A](zh/rlhf-book/book/chapters/appendix-a-definitions.md) | 定义与背景 |
| [附录 B](zh/rlhf-book/book/chapters/appendix-b-style.md) | 风格与相关实践 |
| [附录 C](zh/rlhf-book/book/chapters/appendix-c-practical.md) | 实践细节 |
| [参考文献](zh/rlhf-book/book/chapters/appendix-00-references.md) | 参考文献入口 |

章节使用 Pandoc 引用及数学语法，GitHub 可能直接显示 `[@citation]`、图表标签等源标记；完整排版需使用书稿原有构建系统。

## 仓库组织

```text
my-course/
├── agent/                    # prompt、术语、逐文件调度脚本和配置
├── original/                 # 只读英文参考：Git submodule 固定版本链接
│   ├── rlhf-book/
│   └── missing-semester/
├── zh/                       # 中文工作版本，保留各自原生结构及资源
│   ├── rlhf-book/
│   └── missing-semester/
├── README.md
├── NOTICE.md                 # 来源、改编说明与许可范围
└── LICENSE
```

`original/` 不保存一份普通英文文件拷贝，而是记录两个上游仓库的固定提交。它们的原文不会被汉化任务修改。`zh/` 是独立工作副本，图像、代码、书目和构建资源沿用上游，以保持相对路径和内容对应关系。

## 克隆与继续汉化

```bash
git clone --recurse-submodules https://github.com/mu9enn/my-course.git
cd my-course
# 普通 clone 后补齐英文参考：
git submodule update --init --recursive
```

调度方式保持简单：**每篇文档一个独立 Claude Code 会话**，模型直接读原文、写中文、自查；核心是 [教学改写 prompt](agent/PROMPT.md) 和 [术语表](agent/TERMS.md)。不拆分文档、不提取格式、不串联多个审校角色。配置和运行方法见 [agent/README.md](agent/README.md)。

```bash
python3 agent/translate.py run --book rlhf-book --all
python3 agent/translate.py status
```

密钥和接口地址需放在本机 `agent/secrets.local.json`，该文件、运行日志和本机状态均不提交。仓库仅提供无密钥的示例配置。

## 阅读、构建与贡献

直接按上述目录阅读 Markdown 即可。若要完整 HTML 排版，在 `zh/rlhf-book/` 使用上游的 `make html`，需要安装 Pandoc 和 pandoc-crossref；更多说明见[中文构建文档](zh/rlhf-book/book/README.md)。本轮首先交付中文 Markdown，尚未完成独立中文站点的模板、域名和导航部署。

校对请说明中文文件路径、对应原文段落和修改理由；新增例子或解释请标记为译者内容。不要直接修改 `original/`，需要更新参考版本时单独更新 submodule 并说明影响。

章节中文改编采用 **CC BY-NC-SA 4.0**；代码、agent 及第三方资源依各自许可。详见 [NOTICE.md](NOTICE.md)。
