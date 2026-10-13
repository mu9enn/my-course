---
layout: lecture
title: "编辑器"
presenter: Anish
date: 2019-01-22
order: 1
video:
  aspect: 62.5
  id: 1vLcusYSrI4
---

# 编辑器的重要性

作为程序员，我们花费大量时间编辑纯文本文件。因此，花时间投资找到一个适合自己的编辑器是非常值得的。

你该如何学习一种新编辑器？强迫自己使用它一段时间，哪怕它会暂时降低你的工作效率。这种投入很快就能收回成本（两周足以学会基础操作）。

我们将以 Vim 为例进行教学，但同时也鼓励你尝试其他编辑器。这是一个非常个人化的选择，人们往往对编辑器有[强烈的偏好](https://en.wikipedia.org/wiki/Editor_war)。

我们不可能在 50 分钟内教会你如何熟练使用一款强大的编辑器，所以我们的重点是：教你基础操作，展示一些进阶功能，并提供你进一步掌握该工具的资源。我们会以 Vim 作为讲解的载体，但大部分思路都可以平移到你使用的任何一款强大编辑器上（如果某些思路无法平移，那你可能不该用那款编辑器）。

![编辑器学习曲线](/2019/files/editor-learning-curves.jpg)

<!-- source: https://blogs.msdn.microsoft.com/steverowe/2004/11/17/code-editor-learning-curves/ -->

这张编辑器学习曲线图是伪命题——学会一款强大编辑器的基础操作其实相当容易（尽管精通可能需要多年时间）。

如今的编辑器都有哪些比较流行？可以参考这份 [Stack Overflow 调查](https://insights.stackoverflow.com/survey/2018/#development-environments-and-tools)（注意：Stack Overflow 的用户可能并不完全代表全体程序员）。

## 命令行编辑器

即使你最终决定使用图形界面（GUI）编辑器，掌握一款命令行编辑器也是有价值的——因为你可以在远程机器上轻松编辑文件。

# Nano

Nano 是一款简单的命令行编辑器。

- 用方向键移动光标
- 所有其他快捷键（保存、退出）显示在底部

# Vim

Vi/Vim 是一款强大的文本编辑器。它是一个命令行程序，通常预装在几乎所有系统上，因此在远程机器上编辑文件时非常方便。

Vim 也有图形界面版本，例如 GVim 和 [MacVim](https://macvim-dev.github.io/macvim/)。这些版本提供了更多特性，比如 24 位真彩色、菜单和弹出窗口。

## Vim 的设计哲学

- 编写代码时，你大部分时间其实在阅读和编辑，而不是从头书写
    - Vim 是一款**模态（modal）**编辑器：在不同的模式下分别执行插入文本和操作文本
- Vim 是可编程的（可以使用 Vimscript，也可以使用 Python 等其他语言）
- Vim 的界面本身就像一门编程语言
    - 按键（带有助记名称）就是命令
    - 命令可以组合
- 尽量不使用鼠标：鼠标太慢了
- 编辑器应该跟得上你的思考速度

## Vim 入门

### 模式

Vim 会在左下角显示当前模式。

- **普通模式（Normal mode）**：在文件中移动、进行编辑操作
    - 你大部分时间都会待在这个模式
- **插入模式（Insert mode）**：用于插入文本
- **可视模式（Visual mode，包含可视、行、块三种子模式）**：用于选中文本块

按 `<ESC>` 可以从任何模式切回普通模式。在普通模式下，用 `i` 进入插入模式，用 `v` 进入可视模式，用 `V` 进入可视行模式，用 `<C-v>` 进入可视块模式。

使用 Vim 时你会频繁按下 `<ESC>` 键：建议把 Caps Lock 键映射为 Escape 键。

### 基础操作

Vim 的 Ex 命令通过普通模式下的 `:{命令}` 来执行。

- `:q` 退出（关闭窗口）
- `:w` 保存
- `:wq` 保存并退出
- `:e {文件名}` 打开文件进行编辑
- `:ls` 显示当前打开的缓冲区
- `:help {主题}` 打开帮助
    - `:help :w` 打开 `:w` 这个 Ex 命令的帮助
    - `:help w` 打开 `w` 这个移动命令的帮助

### 移动

Vim 的核心在于高效移动。在普通模式下导航文件。

- 禁用方向键以避免养成坏习惯
```vim
nnoremap <Left> :echoe "Use h"<CR>
nnoremap <Right> :echoe "Use l"<CR>
nnoremap <Up> :echoe "Use k"<CR>
nnoremap <Down> :echoe "Use j"<CR>
```
- 基础移动：`hjkl`（左、下、上、右）
- 单词操作：`w`（下一个词）、`b`（词的开头）、`e`（词的结尾）
- 行操作：`0`（行首）、`^`（第一个非空白字符）、`$`（行尾）
- 屏幕操作：`H`（屏幕顶部）、`M`（屏幕中间）、`L`（屏幕底部）
- 文件操作：`gg`（文件开头）、`G`（文件结尾）
- 行号：`:{数字}<CR>` 或 `{数字}G`（跳转到第 {数字} 行）
- 杂项：`%`（跳转到配对的括号/标签等）
- 查找：`f{字符}`、`t{字符}`、`F{字符}`、`T{字符}`
    - 在当前行的向前/向后查找/跳至 {字符}
- 重复 N 次：`{数字}{移动}`，例如 `10j` 向下移动 10 行
- 搜索：`/{正则}`，`n` / `N` 跳转到下一个/上一个匹配项

### 选择

可视模式有三种：

- 可视模式（Visual，字符级）
- 可视行模式（Visual Line）
- 可视块模式（Visual Block）

在可视模式下依然可以使用移动键来扩展选区。

### 文本操作

过去你用鼠标做的事情，现在都可以用键盘来完成（配合强大的、可组合的命令）。

- `i` 进入插入模式
    - 但对于操作/删除文本，只靠退格键是不够的
- `o` / `O` 在当前行下方/上方插入新行
- `d{运动}` 删除 {运动} 所定义的范围
    - 例如 `dw` 删除一个词，`d$` 删除到行尾，`d0` 删除到行首
- `c{运动}` 更改 {运动} 所定义的范围
    - 例如 `cw` 更改一个词
    - 效果相当于 `d{运动}` 后紧跟 `i`
- `x` 删除字符（等价于 `dl`）
- `s` 替换字符（等价于 `xi`，先删除再进入插入模式）
- 可视模式 + 操作
    - 选中文本后，按 `d` 删除，按 `c` 更改
- `u` 撤销，`<C-r>` 重做
- 还有更多操作值得学习：例如 `~` 可以翻转字符的大小写

### 学习资源

- `vimtutor` 命令行程序，教你 Vim 基础
- [Vim Adventures](https://vim-adventures.com/) 游戏，帮助你学习 Vim

## 自定义 Vim

Vim 通过一个纯文本配置文件 `~/.vimrc`（包含 Vimscript 命令）进行自定义。你很可能需要开启一些基础设置。

可以参考 GitHub 上别人的 dotfiles 获取灵感，但尽量不要直接复制粘贴别人的完整配置。阅读、理解，然后取你所需。

以下是一些值得考虑的配置项：

- 语法高亮：`syntax on`
- 配色方案
- 行号：`set nu` / `set rnu`（相对行号）
- 允许退格键删除所有字符：`set backspace=indent,eol,start`

## 进阶 Vim

下面是一些示例，展示编辑器的强大能力。我们不可能在这里讲授所有这些功能，但你在使用中会逐渐学会。一个好的经验法则：当你在编辑器中使用某个功能时心想"一定有更好的方法来做这件事"——那很可能确实有，去网上查一下就好。

### 搜索与替换

`:s`（substitute，替换）命令（[文档](https://vim.fandom.com/wiki/Search_and_replace)）。

- `%s/foo/bar/g`
    - 在整个文件中全局替换 foo 为 bar
- `%s/\[.*\](\(.*\))/\1/g`
    - 将 Markdown 格式的名称链接替换为纯 URL

### 多窗口

- `sp` / `vsp` 分割窗口（水平分割 / 垂直分割）
- 可以对同一个缓冲区拥有多个视图。

### 鼠标支持

- `set mouse+=a`
    - 可以鼠标点击、滚动选择

### 宏

- `q{字符}` 开始录制寄存器 {字符} 中的宏
- `q` 停止录制
- `@{字符}` 回放宏
- 宏在执行出错时会停止
- `{数字}@{字符}` 将宏执行 {数字} 次
- 宏可以是递归的
    - 先用 `q{字符}q` 清空宏
    - 录制宏，在录制过程中使用 `@{字符}` 调用自身（在录制完成之前它将是空操作）
- 示例：将 XML 转换为 JSON（[源文件](/2019/files/example-data.xml)）
    - 目标是包含 "name" 和 "email" 两个键的对象数组
    - 用 Python 写一个程序？
    - 用 sed / 正则表达式？
        - `g/people/d`
        - `%s/<person>/{/g`
        - `%s/<name>\(.*\)<\/name>/"name": "\1",/g`
        - ……
    - 用 Vim 命令 / 宏
        - `Gdd`, `ggdd` 删除首尾行
        - 宏：格式化单个元素（寄存器 `e`）
            - 跳转到 `<name>` 所在行
            - `qe^r"f>s": "<ESC>f<C"<ESC>q`
        - 宏：格式化一个人
            - 跳转到 `<person>` 所在行
            - `qpS{<ESC>j@eA,<ESC>j@ejS},<ESC>q`
        - 宏：格式化一个人并跳转到下一个人
            - 跳转到 `<person>` 所在行
            - `qq@pjq`
        - 执行宏直到文件末尾
            - `999@q`
        - 手动删除末尾的 `,` 并添加 `[` 和 `]` 包裹

## 扩展 Vim

有很多插件可以扩展 Vim 的功能。

首先，用插件管理器配置好你的环境，比如
[vim-plug](https://github.com/junegunn/vim-plug)、
[Vundle](https://github.com/VundleVim/Vundle.vim) 或
[pathogen.vim](https://github.com/tpope/vim-pathogen)。

以下是一些值得考虑的插件：

- [ctrlp.vim](https://github.com/kien/ctrlp.vim)：模糊文件搜索
- [vim-fugitive](https://github.com/tpope/vim-fugitive)：Git 集成
- [vim-surround](https://github.com/tpope/vim-surround)：操作"周围字符"（引号、括号等）
- [gundo.vim](https://github.com/sjl/gundo.vim)：浏览撤销树
- [nerdtree](https://github.com/scrooloose/nerdtree)：文件浏览器
- [syntastic](https://github.com/vim-syntastic/syntastic)：语法检查
- [vim-easymotion](https://github.com/easymotion/vim-easymotion)：快捷跳转
- [vim-over](https://github.com/osyo-manga/vim-over)：替换预览

插件列表：

- [Vim Awesome](https://vimawesome.com/)

## 其他程序中的 Vim 模式

对于许多流行的编辑器（如 vim 和 emacs），很多其他工具都支持编辑器模拟。

- Shell
    - bash：`set -o vi`
    - zsh：`bindkey -v`
    - `export EDITOR=vim`（被 `git` 等程序使用的环境变量）
- `~/.inputrc`
    - `set editing-mode vi`

甚至在 Web [浏览器](https://vim.fandom.com/wiki/Vim_key_bindings_for_web_browsers) 中也有 Vim 快捷键扩展，一些流行的包括 Google Chrome 上的 [Vimium](https://chrome.google.com/webstore/detail/vimium/dbepggeogbaibhgnhhndojpepiihcmeb?hl=en) 和 Firefox 上的 [Tridactyl](https://github.com/tridactyl/tridactyl)。

## 学习资源

- [Vim Tips Wiki](https://vim.fandom.com/wiki/Vim_Tips_Wiki)
- [Vim Advent Calendar](https://vimways.org/2018/)：各类 Vim 小技巧
- [Neovim](https://neovim.io/)：一款现代化的 Vim 重新实现，拥有更活跃的开发。
- [Vim Golf](https://www.vimgolf.com/)：各类 Vim 代码高尔夫挑战

{% comment %}
# Resources

TODO resources for other editors?
{% endcomment %}

# 练习

1. 尝试几种不同的编辑器。至少体验一款命令行编辑器（如 Vim）和至少一款图形界面编辑器（如 Atom）。通过 `vimtutor`（或其他编辑器的等效教程）等教程进行学习。要真正感受一款新编辑器，请强迫自己在几天内完全使用它来完成日常工作。

1. 自定义你的编辑器。在网上查找技巧和建议，并参考其他人的配置（通常都有很好的文档说明）。

1. 尝试为你使用的编辑器安装插件。

1. 坚持使用一款强大的编辑器至少两周：到那时你应该已经能看到它带来的收益。在某个时刻，你的编辑器应该能跟得上你的思维速度。

1. 安装一个 linter（例如 Python 的 pyflakes），将它与你的编辑器关联，并测试它是否正常工作。