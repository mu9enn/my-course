---
layout: lecture
title: "编辑器（Vim）"
description: >
  学习使用 Vim——一款专为高效代码编辑而设计的功能强大的文本编辑器。
thumbnail: /static/assets/thumbnails/2020/lec3.png
date: 2020-01-15
ready: true
video:
  aspect: 56.25
  id: a6Q8Na575qc
---

撰写英语单词和编写代码是两种截然不同的活动。在编程时，你花在切换文件、阅读、导航和编辑代码上的时间，远比写一大段长文字多。因此，写英语单词（比如 Microsoft Word）和写代码（比如 Visual Studio Code）需要不同类型的程序。

作为程序员，我们大部分时间都在编辑代码，所以花时间来掌握一款适合自己的编辑器是值得的。学习新编辑器的方法如下：

- 从一个教程开始（即本讲，加上我们会提到的资源）
- 在所有文字编辑场景中坚持使用该编辑器（即便一开始会让你变慢）
- 遇到问题当场查：如果觉得某件事应该有更好的做法，那通常确实有更好的做法

如果你按上述方法，全身心地将新程序用于所有文字编辑目的，那么掌握一个复杂文本编辑器的时间线大致如下。花一到两个小时，你就能学会编辑器的基本操作，比如打开和编辑文件、保存和退出、在缓冲区之间导航。坚持 20 小时后，你的速度应该能赶上你用过的旧编辑器。之后再往后，你就能体会到好处了：你积累了足够的知识和肌肉记忆，使用新编辑器会真正帮你省时间。现代文本编辑器是功能强大、花样繁多的工具，所以学习永无止境——你了解得越多，操作就越快。

# 学哪个编辑器？

程序员对文本编辑器的 [意见往往很强烈](https://en.wikipedia.org/wiki/Editor_war)。

那么现在哪些编辑器流行呢？可以参考这份 [Stack Overflow 调查](https://insights.stackoverflow.com/survey/2019/#development-environments-and-tools)（注意 Stack Overflow 用户可能并不能代表全体程序员）。[Visual Studio Code](https://code.visualstudio.com/) 是最受欢迎的编辑器。[Vim](https://www.vim.org/) 则是最受欢迎的全命令行编辑器。

## Vim

本课程的各位讲师都使用 Vim 作为编辑器。Vim 历史悠久；它源自 Vi 编辑器（1976 年），至今仍在持续开发。Vim 背后有若干非常巧妙的思想，正因如此，许多工具都提供了 Vim 模拟模式（例如，已有 140 万人安装了 [VS Code 中的 Vim 模拟插件](https://github.com/VSCodeVim/Vim)）。即便你最终转用了其他编辑器，Vim 依然值得学习。

在 50 分钟内我们无法教完 Vim 的所有功能，所以我们重点放在：讲解 Vim 的哲学思想、教你基础操作、展示一些更高级的功能，并提供让你掌握该工具的资源。

# Vim 的设计哲学

编程时，你大部分时间都在阅读/编辑代码，而非从零开始编写。正因如此，Vim 是一款**模态编辑器（modal editor）**：它对插入文本和操纵文本使用不同的模式。Vim 是可编程的（使用 Vimscript 以及 Python 等其他语言），而且 Vim 的**接口本身就是一种编程语言**：按键（具有助记名称）就是命令，而且这些命令可以**组合**。Vim 避免使用鼠标，因为鼠标太慢；甚至避免使用方向键，因为它们需要的移动太多。

最终的效果是，编辑器的操作速度可以跟得上你的思维速度。

# 模态编辑

Vim 的设计理念基于这样一个事实：程序员大部分时间花在阅读、导航和做小幅修改上，而不是写一大段文字。正因如此，Vim 具有多种操作模式。

- **普通模式（Normal）**：用于在文件中移动和进行编辑
- **插入模式（Insert）**：用于插入文字
- **替换模式（Replace）**：用于替换文字
- **可视模式（Visual，含行可视和块可视）**：用于选中文本块
- **命令行模式（Command-line）**：用于执行命令

按键在不同操作模式下的含义不同。例如，字母 `x` 在插入模式下会直接插入字符 'x'，在普通模式下会删除光标所在的字符，在可视模式下则会删除所选内容。

在默认配置下，Vim 会在左下角显示当前模式。初始/默认模式为普通模式。你通常大部分时间会在普通模式和插入模式之间切换。

你可以通过按下 `<ESC>`（Escape 键）从任意模式切换回普通模式。从普通模式出发，可以用 `i` 进入插入模式，`R` 进入替换模式，`v` 进入可视模式，`V` 进入可视行模式，`<C-v>`（Ctrl-V，有时也写作 `^V`）进入可视块模式，以及 `:` 进入命令行模式。

使用 Vim 时你会频繁使用 `<ESC>` 键：建议将 Caps Lock 重新映射为 Escape（[macOS 操作指南](https://vim.fandom.com/wiki/Map_caps_lock_to_escape_in_macOS)），或者为 `<ESC>` 创建一个[替代映射](https://vim.fandom.com/wiki/Avoid_the_escape_key#Mappings)，比如绑定到简单的按键组合。

# 基础操作

## 插入文字

在普通模式下，按 `i` 进入插入模式。此后 Vim 的行为就和普通的文本编辑器一样，直到你按 `<ESC>` 回到普通模式。配合上面讲过的基础操作，你已经可以开始编辑文件了（只不过如果你所有编辑都从插入模式来做，效率可能并不高）。

## 缓冲区、标签页和窗口

Vim 维护着一个打开文件的集合，称为**缓冲区（buffers）**。一个 Vim 会话中包含若干标签页（tabs），每个标签页下有若干窗口（拆分后的窗格）。每个窗口显示一个缓冲区。与你熟悉的其它程序（比如网页浏览器）不同，缓冲区与窗口之间**不是**一一对应的——窗口仅仅是视图。一个缓冲区可以在**多个**窗口中打开，甚至可以在同一个标签页下同时打开。这非常实用，比如可以同时查看同一个文件的不同部分。

默认情况下，Vim 启动时只有一个标签页，该标签页下包含一个窗口。

## 命令行

在普通模式下输入 `:` 即可进入命令行模式。按下 `:` 后，光标会跳到屏幕底部的命令行处。这个模式提供了大量功能，包括打开、保存和关闭文件，以及[退出 Vim](https://twitter.com/iamdevloper/status/435555976687923200)。

- `:q` 退出（关闭窗口）
- `:w` 保存（"write"，写入）
- `:wq` 保存并退出
- `:e {文件名}` 打开文件进行编辑
- `:ls` 显示当前打开的缓冲区
- `:help {主题}` 打开帮助文档
    - `:help :w` 打开 `:w` 命令的帮助
    - `:help w` 打开 `w` 移动命令的帮助

# Vim 的接口是一种编程语言

Vim 最重要的理念是：**Vim 的接口本身就是一种编程语言**。按键（具有助记名称）是命令，而且这些命令可以**组合**。这使得移动和编辑操作非常高效，尤其在命令变成肌肉记忆之后。

## 移动操作

你应该把大部分时间花在普通模式上，使用移动命令在缓冲区中导航。Vim 中的移动操作也被称为"**名词（nouns）**"，因为它们指向文本的某一部分。

- 基本移动：`hjkl`（左、下、上、右）
- 单词：`w`（下一个词）、`b`（词首）、`e`（词尾）
- 行：`0`（行首）、`^`（第一个非空白字符）、`$`（行尾）
- 屏幕：`H`（屏幕顶部）、`M`（屏幕中部）、`L`（屏幕底部）
- 滚动：`Ctrl-u`（上滚）、`Ctrl-d`（下滚）
- 文件：`gg`（文件开头）、`G`（文件末尾）
- 行号：`:{行号}<CR>` 或 `{行号}G`（跳转到指定行号）
- 其他：`%`（匹配的成对项，比如括号对）
- 查找：`f{字符}`、`t{字符}`、`F{字符}`、`T{字符}`
    - 在当前行向前/向后查找/查找到 {字符} 之前
    - `,` / `;` 用于在匹配结果之间导航
- 搜索：`/{正则表达式}`、`n` / `N` 用于在搜索结果之间导航

## 选择

可视模式：

- 可视模式（字符选择）：`v`
- 可视行模式：`V`
- 可视块模式：`Ctrl-v`

可视模式下配合使用移动键即可选中文本。

## 编辑操作

你过去用鼠标完成的一切操作，现在都可以用键盘通过编辑命令来完成，这些命令可以和移动命令组合——Vim 的接口此时开始看起来像一门编程语言。Vim 的编辑命令也被称为"**动词（verbs）**"，因为动词作用于名词。

- `i` 进入插入模式
    - 但如果是操纵/删除文本，光用退格键还不够
- `o` / `O` 在当前行下方/上方插入新行
- `d{运动}` 删除 {运动} 指定的文本
    - 例如 `dw` 删除一个词，`d$` 删除到行尾，`d0` 删除到行首
- `c{运动}` 更改 {运动} 指定的文本
    - 例如 `cw` 更改一个词
    - 等同于 `d{运动}` 后接 `i`
- `x` 删除字符（等价于 `dl`）
- `s` 替换字符（等价于 `cl`）
- 可视模式 + 操作
    - 选中文本，`d` 删除或 `c` 更改
- `u` 撤销，`<C-r>` 重做
- `y` 复制 / "拉取（yank）"（部分其他命令如 `d` 也会复制到剪贴板）
- `p` 粘贴
- 还有很多可以学习：例如 `~` 可以翻转字符的大小写

## 计数

你可以将名词和动词与**计数**结合，指定某个操作执行的次数。

- `3w` 向前移动 3 个词
- `5j` 向下移动 5 行
- `7dw` 删除 7 个词

## 修饰符

你可以使用**修饰符**来改变名词的含义。常见的修饰符有 `i`（表示"内部"）和 `a`（表示"外部/整个"）。

- `ci(` 更改当前括号内的内容
- `ci[` 更改当前方括号内的内容
- `da'` 删除一个单引号字符串（包括两边的引号）

> 译者补充：在 Vim 命令语法中，修饰符与名词搭配使用来限定操作范围。`i`（inner）限定到成对标记的**内部**（不含标记本身），`a`（around）则包含成对标记**本身**。例如 `di(` 只删除括号内部的内容，而 `da(` 会连同括号一起删除。

# 演示

下面是一个有缺陷的 [fizz buzz](https://en.wikipedia.org/wiki/Fizz_buzz) 实现：

```python
def fizz_buzz(limit):
    for i in range(limit):
        if i % 3 == 0:
            print('fizz')
        if i % 5 == 0:
            print('fizz')
        if i % 3 and i % 5:
            print(i)

def main():
    fizz_buzz(10)
```

我们将修复以下问题：

- main 从未被调用
- 从 0 开始而非从 1 开始
- 15 的倍数会分行输出 "fizz" 和 "buzz"
- 5 的倍数打印的是 "fizz" 而非 "buzz"
- 使用了硬编码的 10 作为参数，而不是接受命令行参数

{% comment %}
- main is never called
  - `G` end of file
  - `o` open new line below
  - type in "if __name__ ..." thing
- starts at 0 instead of 1
  - search for `/range`
  - `ww` to move forward 2 words
  - `i` to insert text, "1, "
  - `ea` to insert after limit, "+1"
- newline for "fizzbuzz"
  - `jj$i` to insert text at end of line
  - add ", end=''"
  - `jj.` to repeat for second print
  - `jjo` to open line below if
  - add "else: print()"
- fizz fizz
  - `ci'` to change fizz
- command-line argument
  - `ggO` to open above
  - "import sys"
  - `/10`
  - `ci(` to "int(sys.argv[1])"
{% endcomment %}

演示操作请参见视频。对比用 Vim 和用其他程序进行上述修改的区别。注意在 Vim 中所需的按键数量非常少，让你能够以思维的速度进行编辑。

# 自定义 Vim

Vim 通过一个纯文本配置文件 `~/.vimrc`（包含 Vimscript 命令）来定制。你可能需要开启许多基础设置。

我们提供了一个文档完善的基础配置，你可以直接拿来使用。推荐使用这个配置，因为它修复了 Vim 一些古怪的默认行为。**从这里下载我们的配置文件 [vimrc](/2020/files/vimrc) 并保存到 `~/.vimrc`。**

Vim 的可定制性极强，花些时间探索定制选项是值得的。你可以到 GitHub 上查看其他人的 dotfiles 来寻找灵感，比如各位讲师的 Vim 配置（[Anish](https://github.com/anishathalye/dotfiles/blob/master/vimrc)、[Jon](https://github.com/jonhoo/configs/blob/master/editor/.config/nvim/init.lua)（使用 [neovim](https://neovim.io/)）、[Jose](https://github.com/JJGO/dotfiles/blob/master/vim/.vimrc)）。关于这个话题也有很多好的博客文章。不建议直接复制粘贴别人的完整配置，而是应该阅读、理解，并取所需。

# 扩展 Vim

Vim 有大量的插件可以扩展其功能。与网上那些过时的建议相反，你**不需要**为 Vim 使用独立的插件管理器（Vim 8.0 起即可）。你可以使用 Vim 内置的包管理系统。只需创建目录 `~/.vim/pack/vendor/start/`，将插件放到那里即可（例如通过 `git clone` 拉取）。

以下是我们推荐的一些插件：

- [ctrlp.vim](https://github.com/ctrlpvim/ctrlp.vim)：模糊文件搜索
- [ack.vim](https://github.com/mileszs/ack.vim)：代码搜索
- [nerdtree](https://github.com/scrooloose/nerdtree)：文件浏览器
- [vim-easymotion](https://github.com/easymotion/vim-easymotion)：快捷跳转

我们尽量不在这里给出过长的一大串插件列表。你可以查看讲师们的 dotfiles（[Anish](https://github.com/anishathalye/dotfiles)、[Jon](https://github.com/jonhoo/configs)、[Jose](https://github.com/JJGO/dotfiles)）来了解我们还用了哪些其他插件。[Vim Awesome](https://vimawesome.com/) 也是一个很好的插件发现站。关于这个话题也有很多博客文章——只需搜索"best Vim plugins"即可。

# 其他程序中的 Vim 模式

许多工具都支持 Vim 模拟。质量从好到优秀不等，具体取决于工具，可能不支持 Vim 的某些高级功能，但大多数都能很好地覆盖基础操作。

## Shell

如果你使用 Bash，执行 `set -o vi`。如果使用 Zsh，执行 `bindkey -v`。对于 Fish，执行 `fish_vi_key_bindings`。此外，无论你使用哪种 shell，都可以设置 `export EDITOR=vim`。这个环境变量用于决定当某个程序想要启动编辑器时，应该调用哪个编辑器。例如 `git` 会使用这个编辑器来编写提交信息。

## Readline

许多程序在其命令行界面中使用 [GNU Readline](https://tiswww.case.edu/php/chet/readline/rltop.html) 库。Readline 同样支持（基础）Vim 模拟，可以在 `~/.inputrc` 文件中添加以下行来启用：

```
set editing-mode vi
```

有了这个设置，例如 Python REPL 就会支持 Vim 快捷键绑定。

## 其他

甚至 web [浏览器](https://vim.fandom.com/wiki/Vim_key_bindings_for_web_browsers) 也有 Vim 快捷键扩展——Chrome 上比较流行的是 [Vimium](https://chrome.google.com/webstore/detail/vimium/dbepggeogbaibhgnhhndojpepiihcmeb?hl=en)，Firefox 上则是 [Tridactyl](https://github.com/tridactyl/tridactyl)。你甚至可以在 [Jupyter notebook](https://github.com/jupyterlab-contrib/jupyterlab-vim) 中获得 Vim 快捷键绑定。这里有一份[非常长的列表](https://reversed.top/2016-08-13/big-list-of-vim-like-software)，汇总了支持类似 Vim 快捷键的软件。

# Vim 高级功能

下面通过一些示例来展示编辑器的强大之处。我们无法教你所有这类技巧，但你会在日常使用中逐步学到。一个很好的思路是：当你在编辑器中觉得"这件事肯定有更好的做法"时，通常确实有——去网上搜一下。

## 搜索和替换

`:s`（substitute，替换）命令（[文档](https://vim.fandom.com/wiki/Search_and_replace)）。

- `%s/foo/bar/g`
    - 在文件中全局替换 foo 为 bar
- `%s/\[.*\](\(.*\))/\1/g`
    - 将命名式的 Markdown 链接替换为纯 URL

## 多窗口

- `:sp` / `:vsp` 拆分窗口
- 可以在多个窗口中查看同一个缓冲区。

## 宏

- `q{字符}` 开始录制寄存器 `{字符}` 中的宏
- `q` 停止录制
- `@{字符}` 重放宏
- 宏执行遇到错误时停止
- `{数量}@{字符}` 将宏执行 {数量} 次
- 宏可以递归
    - 先通过 `q{字符}q` 清空该宏
    - 录制宏时，用 `@{字符}` 来递归调用该宏（录制完成前调用相当于无操作）
- 示例：将 XML 转换为 JSON（[文件](/2020/files/example-data.xml)）
    - 包含 "name" / "email" 键的对象数组
    - 用 Python 程序？
    - 用 sed / 正则表达式？
        - `g/people/d`
        - `%s/<person>/{/g`
        - `%s/<name>\(.*\)<\/name>/"name": "\1",/g`
        - ……
    - 使用 Vim 命令/宏
        - `Gdd`、`ggdd` 删除首行和末行
        - 格式化单个元素的宏（寄存器 `e`）
            - 跳转到包含 `<name>` 的行
            - `qe^r"f>s": "<ESC>f<C"<ESC>q`
        - 格式化一个人的宏
            - 跳转到包含 `<person>` 的行
            - `qpS{<ESC>j@eA,<ESC>j@ejS},<ESC>q`
        - 格式化一个人并跳转到下一个人的宏
            - 跳转到包含 `<person>` 的行
            - `qq@pjq`
        - 执行宏直到文件末尾
            - `999@q`
        - 手动移除最后一个 `,` 并添加 `[` 和 `]` 分隔符

# 资源

- `vimtutor` 是随 Vim 一起安装的教程——只要 Vim 已安装，你就可以在 shell 中运行 `vimtutor`
- [Vim Adventures](https://vim-adventures.com/) 是一款用来学习 Vim 的游戏
- [Vim Tips Wiki](https://vim.fandom.com/wiki/Vim_Tips_Wiki)
- [Vim Advent Calendar](https://vimways.org/2019/) 包含各种 Vim 技巧
- [Vim Golf](https://www.vimgolf.com/) 是一种[代码高尔夫](https://en.wikipedia.org/wiki/Code_golf)，只不过编程语言是 Vim 的界面
- [Vi/Vim Stack Exchange](https://vi.stackexchange.com/)
- [Vim Screencasts](http://vimcasts.org/)
- [Practical Vim](https://pragprog.com/titles/dnvim2/)（书籍）

# 练习

1. 完成 `vimtutor` 教程。提示：它最适合在 [80x24](https://en.wikipedia.org/wiki/VT100)（80 列 × 24 行）的终端窗口中运行。
1. 下载我们的 [基础 vimrc 配置文件](/2020/files/vimrc) 并保存到 `~/.vimrc`。使用 Vim（！）阅读整个文件，观察新配置下 Vim 的外观和行为有哪些细微的不同。
1. 安装并配置一个插件：[ctrlp.vim](https://github.com/ctrlpvim/ctrlp.vim)。
    1. 使用 `mkdir -p ~/.vim/pack/vendor/start` 创建插件目录
    1. 下载插件：`cd ~/.vim/pack/vendor/start; git clone https://github.com/ctrlpvim/ctrlp.vim`
    1. 阅读插件的[文档](https://github.com/ctrlpvim/ctrlp.vim/blob/master/readme.md)。尝试通过导航到一个项目目录、打开 Vim 并使用 Vim 命令行执行 `:CtrlP` 来练习使用 CtrlP 搜索文件。
    1. 根据你的 `~/.vimrc` 添加[配置](https://github.com/ctrlpvim/ctrlp.vim/blob/master/readme.md#basic-options)，将 Ctrl-P 设置为启动 CtrlP，完成自定义。
1. 在本地重新做一遍课堂上的 [演示](#demo)，来练习 Vim 操作。
1. 在接下来的一个月中，用 Vim 做**所有**的文字编辑工作。当任何操作看起来效率不高，或当你觉得"应该有更好的做法"时，试着去搜一搜，通常确实有。如果遇到卡住的地方，来参加办公时间或给我们发邮件。
1. 将你其他的工具也配置为使用 Vim 快捷键绑定（见上方说明）。
1. 进一步自定义你的 `~/.vimrc` 并安装更多插件。
1. （进阶）使用 Vim 宏将 XML 转换为 JSON（[示例文件](/2020/files/example-data.xml)）。尝试独立完成，如果遇到卡住的地方可以参考上方[宏](#macros)一节的内容。

> 译者补充（自测）：以下三道选择题可帮助你检验对本节核心概念的理解。答案不在此提供，建议先自行练习后再对照答案。
> 1. 在 Vim 中，`di(` 和 `da(` 有什么区别？
> 2. 如果你想在普通模式下直接删除光标所在整行，最简短的命令组合是什么？
> 3. 录制一个宏后，你希望它自动执行 100 次，应该输入什么？