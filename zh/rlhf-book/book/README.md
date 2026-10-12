# RLHF Book - 构建系统

本构建系统基于 [**Pandoc book template**](https://github.com/wikiti/pandoc-book-template)。

本目录包含将 RLHF Book 构建为多种格式（HTML、PDF、EPUB、DOCX）所需的源文件。

## 使用方法

在仓库根目录下执行：

```bash
make          # Build all formats
make html     # Build HTML site
make pdf      # Build PDF (requires LaTeX)
make epub     # Build EPUB
make files    # Copy assets to build output
```

### 已知的转换问题

由于网站采用了嵌套目录结构，PDF 中各章节之间的节链接会失效。我们为更好的网页阅读体验选择接受这一问题，但建议不要在 Markdown 文件中放置任何指向 `rlhfbook.com` 的链接。非 HTML 版本并不适合这类链接。

### 使用编码智能体编辑时的常见失败原因

本构建系统支持合法的 UTF-8 Unicode 标点符号（包括弯引号和破折号）。类似 `Cannot decode byte '\xe2': Data.Text.Encoding: Invalid UTF-8 stream` 的错误表示输入内容格式有误或编码不正确，而不是因为包含了合法的 Unicode 标点。

可以用 `file -I book/chapters/filename.md` 查看文件编码，或用 `iconv -f UTF-8 -t UTF-8 book/chapters/filename.md >/dev/null` 进行验证。保持源文件为 UTF-8 编码即可；PDF 构建过程会在需要时对 TeX 输出做标准化处理。

## 安装依赖

详细信息请查阅 [Pandoc 安装页面](http://pandoc.org/installing.html)。

### Linux

*注意：这些步骤尚未经过全面测试。*

原始构建指令：
```sh
sudo apt-get install pandoc
```

本模板使用 [make](https://www.gnu.org/software/make/) 来构建输出文件，所以也别忘了安装它：

```sh
sudo apt-get install make
```

如需导出为 PDF，请确保安装以下软件包：

```sh
sudo apt-get install texlive-fonts-recommended texlive-xetex
```

经用户实际测试过的构建指令（参见 [issue #117](https://github.com/natolambert/rlhf-book/issues/117)）：
> 我在 PopOS 22.04 Linux 系统上分享下自己让本书成功构建的过程：
>
> 安装 Pandoc 3.6.4 以避免关于 pandoc-crossref 的警告信息。
>
> 需要执行 `brew install pandoc-crossref` 才能让构建正常运行。
>
> 执行 `sudo apt install fonts-dejavu`，因为我系统的软件仓库中没有提供 ttf-dejavu 包。
>
> 执行 `make clean` 清除已有构建产物。
>
> 在项目目录中执行 `git pull`，将本地副本与 GitHub 仓库同步。

### macOS
```
brew install pandoc
brew install make
brew install pandoc-crossref
```

对于 arXiv 源文件 bundle，还需确保 PDF 模板所使用的 Python 运行环境和 LaTeX 包均已安装：

```sh
brew install uv
```

小型 TeX 安装：

```sh
brew install --cask basictex
sudo tlmgr update --self
sudo tlmgr install fvextra tcolorbox pdfcol
```

更完整的 TeX 安装方式：

```sh
brew install --cask mactex-no-gui
```

在仓库根目录下构建面向 arXiv 的 bundle：

```sh
make -B latex
```

生成的源文件 bundle 会写入 `build/arxiv.zip`。

arXiv 目标只复制 `book.tex` 中引用的图片。如果 arXiv 报告图片过大，请将 `book/images` 中对应的源文件尺寸缩小到 arXiv 的像素数量限制以下，然后重新执行 `make -B latex`。

或者，直接使用 [GitHub Actions 工作流](https://github.com/natolambert/rlhf-book/blob/main/.github/workflows/static.yml) —— 该工作流会在 macOS 上自动为新版本执行构建。

## 目录结构

```
book/
├── chapters/     # Markdown source files (one per chapter)
├── images/       # Image assets referenced in chapters
├── assets/       # Brand assets (covers, logos)
├── templates/    # Pandoc templates for each output format
├── scripts/      # Build utilities
├── data/         # Library data (JSON)
└── preorder/     # Order redirect page
```

## 配置

编辑 *book/metadata.yml* 文件来设置构建配置：

```yml
---
title: My book title
author: Daniel Herzog
rights: MIT License
lang: en-US
tags: [pandoc, book, my-book, etc]
abstract: |
  Your summary.
mainfont: DejaVu Sans

# Filter preferences:
# - pandoc-crossref
linkReferences: true
---
```

所有可用字段的完整列表见 [此页面](http://pandoc.org/MANUAL.html#extension-yaml_metadata_block)。

## 创建章节

在 *chapters/* 文件夹中创建一个新的 Markdown 文件即可新增章节；最终会得到类似这样的结构：

```
chapters/01-introduction.md
chapters/02-installation.md
chapters/03-usage.md
chapters/04-references.md
```

Pandoc 和 Make 会按照文件名自动排序并拼接它们；这也是我们使用数字前缀的原因。

每个章节至少需要指定一个标题：

```md
# Introduction

This is the first paragraph of the introduction chapter.

## First

This is the first subsection.

## Second

This is the second subsection.
```

每个一级标题（`#`）对应一本书的一章，每个二级标题（`##`）对应一章中的一节。你可以使用 Markdown 所支持的任何层级的子标题。

### 手动控制页面顺序

如果你不想使用数字前缀来自动排序，也可以手动控制页面顺序。

此时需在 Makefile 中将 `CHAPTERS` 变量替换为你指定的顺序。例如：

```
CHAPTERS += $(addprefix ./book/chapters/,\
 01-introduction.md\
 02-installation.md\
 03-usage.md\
 04-references.md\
)
```

### 章节之间的链接

可以使用锚点链接在书中各章节之间相互链接：

```md
// chapters/01-introduction.md
# Introduction

For more information, check the [Usage] chapter.

// chapters/02-installation.md
# Usage

...
```

如果需要为引用自定义显示名称，可以使用如下语法：

```md
For more information, check [this](#usage) chapter.
```

锚点名应全部小写，空格、冒号、分号等字符应替换为连字符。例如 `Chapter title: A new era` 应写为 `#chapter-title-a-new-era`。

### 节之间的链接

节之间的链接方式与锚点链接相同：

```md
# Introduction

## First

For more information, check the [Second] section.

## Second

...
```

或带自定义名称的写法：

```md
For more information, check [this](#second) section.
```

## 插入各类元素

### 插入图片

使用 Markdown 语法插入图片并附带说明文字：

```md
![A cool seagull.](images/seagull.png)
```

Pandoc 会自动将图片转换为图形（figure），将方括号中的文字（即图片说明文字）作为标题。

如果需要调整图片尺寸（自 Pandoc 1.16 起支持），可使用如下语法：

```md
![A cool seagull.](images/seagull.png){ width=50% height=50% }
```

### 插入表格

使用 Markdown 表格，并通过 `Table: <Your table description>` 语法添加标题：

```md
| Index | Name |
| ----- | ---- |
| 0     | AAA  |
| 1     | BBB  |
| ...   | ...  |

Table: This is an example table.
```

### 插入公式

用单 `$` 包裹 LaTeX 数学公式作为行内（行内小字）公式：

```md
This, $\mu = \sum_{i=0}^{N} \frac{x_i}{N}$, the mean equation, ...
```

Pandoc 在 HTML 中把公式渲染为 MathJax，在 EPUB 中渲染为 MathML，在 PDF 中渲染为原生 LaTeX。

如果希望将公式居中显示（而非行内），使用双 `$$` 包裹：

```md
$$\mu = \sum_{i=0}^{N} \frac{x_i}{N}$$
```

[这里](https://www.codecogs.com/latex/eqneditor.php) 有一个在线公式编辑器。

### 交叉引用

最初，此模板使用 LaTeX 标签来为图片、表格、公式或章节自动编号，类似如下写法：

```md
Please, admire the gloriousness of Figure \ref{seagull_image}.

![A cool seagull.\label{seagull_image}](images/seagull.png)
```

**但这类引用仅在导出为 LaTeX 格式（即 PDF、LaTeX）时才生效。**

如果你需要在其他格式中也支持交叉引用，此模板现在通过 [Pandoc 过滤器](https://pandoc.org/filters.html) 实现了交叉引用功能。如果需要使用，请选用一个合法的插件及其对应语法。

强烈推荐使用 [pandoc-crossref](https://github.com/lierdakil/pandoc-crossref)，也有其他采用类似语法的替代方案，例如
[pandoc-xnos](https://github.com/tomduck/pandoc-xnos)。

首先，在 *Makefile* 中通过更新 `FILTER_ARGS` 变量来启用该过滤器：

```make
FILTER_ARGS = --filter pandoc-crossref
```

然后即可使用过滤器提供的交叉引用语法。例如 *pandoc-crossref* 使用 `{#<type>:<id>}` 作为定义锚点、`@<type>:id` 作为引用标记。一些示例：

```md
List of references:

- Check @fig:seagull.
- Check @tbl:table.
- Check @eq:equation.

List of elements to reference:

![A cool seagull](images/seagull.png){#fig:seagull}

$$ y = mx + b $$ {#eq:equation}

| Index | Name |
| ----- | ---- |
| 0     | AAA  |
| 1     | BBB  |
| ...   | ...  |

Table: This is an example table. {#tbl:table}
```

更详细的使用说明请查阅所选过滤器的文档（[pandoc-crossref 使用说明](http://lierdakil.github.io/pandoc-crossref/)）。

### 内容过滤器

如果需要在内容交给 Pandoc 之前对其进行预处理，可以使用 `CONTENT_FILTERS`。设置此 Makefile 变量后，它会在将 Markdown 内容传给 Pandoc 之前被依次执行。例如，用 `sed` 将 `@pagebreak` 全部替换为 `<div style="page-break-before: always;"></div>`：

```
CONTENT_FILTERS = sed 's/@pagebreak/"<div style=\"page-break-before: always;\"><\/div>"/g'
```

如需使用多个过滤器，可以在 `CONTENT_FILTERS` 变量中包含多个管道符：

```
CONTENT_FILTERS = \
  sed 's/@pagebreak/"<div style=\"page-break-before: always;\"><\/div>"/g' | \
  sed 's/@image/[Cool image](\/images\/image.png)/g'
```

## 输出格式

本模板使用 *Makefile* 来自动化构建流程。我们不再直接调用 *Pandoc CLI 工具*，而是通过一些 *make* 命令来完成构建。

### 导出为 PDF

请注意，生成 PDF 文件需要额外安装依赖（约 800 MB）：

```sh
sudo apt-get install texlive-xetex ttf-dejavu
```

安装完依赖后执行：

```sh
make pdf
```

生成的文件会放在 *build/pdf* 目录下。

### 导出为 EPUB

执行：

```sh
make epub
```

生成的文件会放在 *build/epub* 目录下。

### 导出为 HTML

执行：

```sh
make html
```

生成的文件会放在 *build/html* 目录下。

### 导出为 DOCX

执行：

```sh
make docx
```

生成的文件会放在 *build/docx* 目录下。

### 额外配置

如需自定义输出行为，你可能需要查阅 [Pandoc 手册](http://pandoc.org/MANUAL.html)，了解有关 PDF（LaTeX）生成、自定义样式等的更多信息，并据此修改 Makefile。

### 模板

输出文件通过 [Pandoc 模板](https://pandoc.org/MANUAL.html#templates) 生成。所有模板位于 `templates/` 目录下，可根据需要自行修改。本仓库中已包含一些基础格式模板，方便你快速起步。

## 参考链接

- [Pandoc](http://pandoc.org/)
- [Pandoc Manual](http://pandoc.org/MANUAL.html)
- [Wikipedia: Markdown](http://wikipedia.org/wiki/Markdown)
