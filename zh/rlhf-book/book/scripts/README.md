# 脚本

用于管理参考文献库及其他图书维护任务的实用工具。

## 参考文献工具

- **check_bib_integrity.py** — 检查 `bib.bib` 中是否存在重复的引用键（bib key）以及未使用的条目。还会报告那些引用了不存在的 bib key 的 Markdown 引用。
  ```bash
  uv run python book/scripts/check_bib_integrity.py
  ```

- **check_arxiv_publications.py** — 扫描 arXiv 预印本，查找已被同行评审会议/期刊正式发表的文章（使用 DBLP API）。将结果保存为 JSON 文件以便审查。
  ```bash
  uv run python book/scripts/check_arxiv_publications.py --delay 1.0
  uv run python book/scripts/check_arxiv_publications.py --resume  # if interrupted
  ```

- **update_bib_from_arxiv_check.py** — 将 `check_arxiv_publications.py` 的检查结果应用到 `.bib` 文件中，包括更改条目类型（entry type）、补充出版地/会议名（venue/booktitle）以及更新年份。
  ```bash
  uv run python book/scripts/update_bib_from_arxiv_check.py --dry-run  # preview changes
  uv run python book/scripts/update_bib_from_arxiv_check.py            # apply changes
  ```

## 其他脚本

- **epub-citations.lua** — 将 citeproc 格式的文献引用转换为 EPUB 3 的弹出式脚注：把每个被引用的书目条目复制到章节本地的 `<aside>` 中。
- **validate_ebooks.py** — 验证电子书制品（ebook artifacts）中的弹出脚注结构、XML 良构性（well-formedness）、ID 唯一性以及内部链接完整性（执行 `make validate-ebooks`）。在可用时还会调用 `epubcheck` 进行交叉验证。
- **ensure_pdfoutput.py** — 确保 LaTeX 中的 PDF 输出设置正确。
- **generate_library.py** — 生成库文件。
- **normalize_tex_unicode.py** — 规范化 TeX 文件中的 Unicode 字符。
- **report_non_ascii.py** — 报告文件中存在的非 ASCII 字符。
- **strip_unicode_from_markdown.py** — 移除 Markdown 文件中的 Unicode 字符。
- **strip_xetex_branch.py** — 剥离 XeTeX 相关的分支代码。