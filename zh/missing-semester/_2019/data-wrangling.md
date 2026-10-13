---
layout: lecture
title: "数据整理"
presenter: Jon
date: 2019-01-17
order: 2
video:
  aspect: 56.25
  id: VW2jn9Okjhw
---

你有没有遇到过一堆文本、想对它做点什么的情况？
很好。这就是**数据整理**（Data Wrangling）的核心所在！
具体来说，就是把数据从一种格式适配成另一种格式，直到最终得到
你真正想要的东西。

我们其实已经见过基本的数据整理：`journalctl | grep -i intel`。
 - 找出所有提到 Intel 的系统日志条目（不区分大小写）
 - 实际上，大多数数据整理工作就是在了解你有哪些工具，
   以及如何把它们组合使用。

让我们从头开始：我们需要一个数据源，以及一个对它的操作目标。
日志通常是很好的用例，因为你经常需要调查其中的一些内容，
而通读整份日志又不切实际。让我们通过查看服务器的日志来
看看谁在尝试登录我的服务器：

```bash
ssh myserver journalctl
```

这个结果太多了。我们把它缩小到 ssh 相关的内容：

```bash
ssh myserver journalctl | grep sshd
```

注意到我们正在用**管道**（pipe）把一个**远程**文件通过本地计算机上的
`grep` 来过滤！`ssh` 很神奇。不过这仍然比我们想要的多得多，
而且很难阅读。让我们改进一下：

```bash
ssh myserver journalctl | grep sshd | grep "Disconnected from"
```

这里仍然有很多噪音。有很多方法可以去掉这些噪音，
但让我们来看看你工具箱里最强大的工具之一：`sed`。

`sed` 是一个"流编辑器"，构建在旧的 `ed` 编辑器之上。
在 `sed` 中，你基本上是通过给出一组简短的命令来描述如何修改文件，
而不是直接操作其内容（虽然你也可以这样做）。它有很多命令，
但其中一个最常用的就是 `s`：替换（substitution）。比如，我们可以这样写：

```bash
ssh myserver journalctl
 | grep sshd
 | grep "Disconnected from"
 | sed 's/.*Disconnected from //'
```

我们刚才写的是一条简单的**正则表达式**（regular expression）——
一种强大的构造，让你可以用模式来匹配文本。`s` 命令的格式是：
`s/REGEX/SUBSTITUTION/`，其中 `REGEX` 是你要搜索的正则表达式，
`SUBSTITUTION` 是用来替换匹配文本的字符串。

## 正则表达式

正则表达式既常见又实用，因此值得花点时间理解它们是如何工作的。
让我们从上面使用过的那条正则表达式开始看：`/.*Disconnected from /`。
正则表达式通常（虽然并非总是）被 `/` 包围。大部分 ASCII 字符
只是保持它们的字面含义，但有些字符具有"特殊"的匹配行为。
不同字符具体对应什么功能，在不同的正则表达式实现中略有差异，
这确实让人感到头疼。非常常见的模式包括：

 - `.` 表示"除换行符外的任意单个字符"
 - `*` 前一项零次或多次
 - `+` 前一项一次或多次
 - `[abc]` `a`、`b`、`c` 中的任意一个字符
 - `(RX1|RX2)` 匹配 `RX1` 或 `RX2` 之一
 - `^` 行的开头
 - `$` 行的结尾

`sed` 的正则表达式有些古怪，在大多数这些符号前面都需要加上 `\`
才能让它们发挥特殊含义。或者你也可以用 `-E` 参数。

所以，再看 `/.*Disconnected from /`，我们看到它匹配的是
任意以若干字符开头、后跟字面字符串 "Disconnected from " 的文本。
这正是我们想要的。但要小心，正则表达式是有陷阱的。
如果有人尝试用用户名 "Disconnected from" 登录呢？我们会看到：

```
Jan 17 03:13:00 thesquareplanet.com sshd[2631]: Disconnected from invalid user Disconnected from 46.97.239.16 port 55920 [preauth]
```

那我们会得到什么结果呢？好吧，`*` 和 `+` 默认情况下是"贪婪"的。
它们会尽可能多地匹配文本。所以上面那行我们最终只会得到：

```
46.97.239.16 port 55920 [preauth]
```

这可能不是你想要的。在一些正则表达式实现中，你可以在 `*` 或 `+`
后面加上 `?` 让它们变成非贪婪的，但遗憾的是 `sed` 不支持这个。
不过我们可以切换到 Perl 的命令行模式，它 _确实_ 支持这个构造：

```bash
perl -pe 's/.*?Disconnected from //'
```

接下来的部分我们还是用 `sed`，因为在这种类型的任务中
`sed` 远比 Perl 更常用。`sed` 还可以做其他一些方便的事情，
比如打印指定匹配之后的行、单次执行多次替换、搜索特定内容等等。
不过我们不会在这里覆盖太多内容。`sed` 本身几乎就是一个独立的话题，
而且通常还有更好的工具可用。

好了，我们还想去掉一个后缀。我们该怎么做呢？
要只匹配用户名之后的文本有些棘手，尤其是用户名可能包含空格之类的东西！
我们需要匹配的是**整行**：

```bash
 | sed -E 's/.*Disconnected from (invalid |authenticating )?user .* [^ ]+ port [0-9]+( \[preauth\])?$//'
```

让我们用一个 [正则表达式调试工具](https://regex101.com/r/qqbZqh/2)
来看看这里发生了什么。好，开头和之前一样。然后，我们匹配的是
"user"各种变体（日志中有两个前缀）。接着，我们匹配的是用户名所在的位置，
即任意字符序列。然后是匹配任意单个单词（`[^ ]+`，即任意非空非空格序列）。
然后是单词 "port" 后跟数字序列。再后面是可选的后缀
` [preauth]`，以及行尾。

请注意，使用这种技术，用户名是 "Disconnected from"
不会再让我们困惑了。你能看出为什么吗？

不过这里有一个问题，整个日志会变成空行。
毕竟我们是想要**保留**用户名的。为此，我们可以使用"捕获组"（capture groups）。
任何被括号包围的正则表达式匹配到的文本都会被存储在一个编号的捕获组中。
这些捕获组可以在替换中（在某些引擎中甚至可以在模式本身中！）使用
`\1`、`\2`、`\3` 等来引用。所以：

```bash
 | sed -E 's/.*Disconnected from (invalid |authenticating )?user (.*) [^ ]+ port [0-9]+( \[preauth\])?$/\2/'
```

你可能已经想到，你可以构造出**非常**复杂的正则表达式。
比如，这是一篇关于如何匹配[电子邮件地址](https://www.regular-expressions.info/email.html)的文章。
[并不简单](https://web.archive.org/web/20221223174323/http://emailregex.com/)。
而且[有大量讨论](https://stackoverflow.com/questions/201323/how-to-validate-an-email-address-using-a-regular-expression/1917982)。
还有人写了[测试](https://fightingforalostcause.net/content/misc/2006/compare-email-regex.php)。
还有[测试矩阵](https://mathiasbynens.be/demo/url-regex)。
你甚至可以用正则表达式来判断一个给定数字[是否为素数](https://www.noulakaz.net/2007/03/18/a-regular-expression-to-check-for-prime-numbers/)。

正则表达式出了名的难以正确使用，但它们在工具箱里也非常好用！

## 回到数据整理

好了，现在我们有：

```bash
ssh myserver journalctl
 | grep sshd
 | grep "Disconnected from"
 | sed -E 's/.*Disconnected from (invalid |authenticating )?user (.*) [^ ]+ port [0-9]+( \[preauth\])?$/\2/'
```

我们其实也可以只用 `sed` 来完成，但为什么要那么做呢？
为了乐趣。

```bash
ssh myserver journalctl
 | sed -E
   -e '/Disconnected from/!d'
   -e 's/.*Disconnected from (invalid |authenticating )?user (.*) [^ ]+ port [0-9]+( \[preauth\])?$/\2/'
```

这里展示了 `sed` 的一些能力。`sed` 还可以注入文本（使用 `i` 命令）、
显式打印行（使用 `p` 命令）、按索引选择行，以及很多其他东西。
查阅 `man sed`！

总之，我们现在得到的是所有尝试过登录的用户名列表。
但这基本没什么帮助。让我们找找最常见的几个：

```bash
ssh myserver journalctl
 | grep sshd
 | grep "Disconnected from"
 | sed -E 's/.*Disconnected from (invalid |authenticating )?user (.*) [^ ]+ port [0-9]+( \[preauth\])?$/\2/'
 | sort | uniq -c
```

`sort` 会对其输入进行**排序**。`uniq -c` 会将连续的相同行折叠为一行，
前面带有出现次数的计数。我们可能还想对这个结果排序，只保留
最常见的登录：

```bash
ssh myserver journalctl
 | grep sshd
 | grep "Disconnected from"
 | sed -E 's/.*Disconnected from (invalid |authenticating )?user (.*) [^ ]+ port [0-9]+( \[preauth\])?$/\2/'
 | sort | uniq -c
 | sort -nk1,1 | tail -n10
```

`sort -n` 将以**数值**（而非字典）顺序排序。`-k1,1` 表示
"只按第一个以空白分隔的列排序"。`,n` 部分表示"排序到第 `n` 个字段为止"，
默认是到行尾。在_这个特定示例_中，按整行排序不会有问题，
但我们是来学习的！

如果我们想要_最不_常见的，我们可以用 `head` 代替 `tail`。
还有 `sort -r`，它以相反的顺序排序。

好了，这已经很不错了，但我们只想得到用户名，
也许不一定每行一个？

```bash
ssh myserver journalctl
 | grep sshd
 | grep "Disconnected from"
 | sed -E 's/.*Disconnected from (invalid |authenticating )?user (.*) [^ ]+ port [0-9]+( \[preauth\])?$/\2/'
 | sort | uniq -c
 | sort -nk1,1 | tail -n10
 | awk '{print $2}' | paste -sd,
```

我们先从 `paste` 开始看：它让你用给定的单字符分隔符（`-d`）
按行合并（`-s`）。但 `awk` 又是什么？

## awk —— 另一种编辑器

`awk` 是一种编程语言，只不过它碰巧非常擅长处理文本流。
如果你要认真学习 `awk`，那就**有太多**东西可以说了，
但就像这里提到的其他许多东西一样，我们只过一下基础知识。

首先，`{print $2}` 做了什么？`awk` 程序的格式是由一个可选的
模式（pattern）加一个"当模式匹配某行时该如何处理"的块组成。
默认模式（我们在上面使用的那个）匹配所有行。在块内部，
`$0` 被设为整行的内容，`$1` 到 `$n` 被设为该行按 `awk`
字段分隔符（默认是空白，可通过 `-F` 修改）分隔的第 `n` 个
**字段**。在这种情况下，我们是说：对每一行，打印第二个字段的内容，
正好就是用户名！

让我们看看能不能做一些更花哨的事。让我们计算一下只出现一次、
以 `c` 开头、以 `e` 结尾的用户名数量：

```bash
 | awk '$1 == 1 && $2 ~ /^c[^ ]*e$/ { print $2 }' | wc -l
```

这里有很多内容值得展开。首先，注意我们现在有了一个
模式（即 `{...}` 之前的那部分）。模式表示这一行的第一个字段
应该等于 1（即 `uniq -c` 的输出计数），而且第二个字段
应该匹配给定的正则表达式。块仅仅是打印用户名。
然后我们用 `wc -l` 统计输出的行数。

不过，`awk` 是一种编程语言，记住了吗？

```awk
BEGIN { rows = 0 }
$1 == 1 && $2 ~ /^c[^ ]*e$/ { rows += $1 }
END { print rows }
```

`BEGIN` 是一个匹配输入开头的模式（`END` 匹配结尾）。
现在，逐行处理的块只是把第一个字段的计数加到变量里
（虽然在这个例子中它总是 1），然后我们在最后把它打印出来。
事实上，我们_完全可以_完全去掉 `grep` 和 `sed`，因为
`awk` [能搞定一切](https://web.archive.org/web/20251210045942/https://backreference.org/2010/02/10/idiomatic-awk/)，
不过我们就留作读者练习了。

## 数据分析

你可以做数学运算！

```bash
 | paste -sd+ | bc -l
```

```bash
echo "2*($(data | paste -sd+))" | bc -l
```

你可以通过多种方式获取统计信息。
[`st`](https://github.com/nferraz/st) 相当不错，但如果你已经有 R：

```bash
ssh myserver journalctl
 | grep sshd
 | grep "Disconnected from"
 | sed -E 's/.*Disconnected from (invalid |authenticating )?user (.*) [^ ]+ port [0-9]+( \[preauth\])?$/\2/'
 | sort | uniq -c
 | awk '{print $1}' | R --slave -e 'x <- scan(file="stdin", quiet=TRUE); summary(x)'
```

R 是另一种（有些古怪的）编程语言，非常适合数据分析和
[绘图](https://ggplot2.tidyverse.org/)。我们不会深入太多细节，
简而言之，`summary` 会打印一个矩阵的摘要统计信息，
而我们从输入流构建了一个数字矩阵，所以 R 给了我们想要的统计信息！

如果你只是想要一些简单的绘图，`gnuplot` 是你的好帮手：

```bash
ssh myserver journalctl
 | grep sshd
 | grep "Disconnected from"
 | sed -E 's/.*Disconnected from (invalid |authenticating )?user (.*) [^ ]+ port [0-9]+( \[preauth\])?$/\2/'
 | sort | uniq -c
 | sort -nk1,1 | tail -n10
 | gnuplot -p -e 'set boxwidth 0.5; plot "-" using 1:xtic(2) with boxes'
```

## 用数据整理来生成参数

有时你想要通过数据整理来从较长列表中找出要安装或卸载的东西。
我们前面讨论过的数据整理方法加上 `xargs` 可以成为一个强大的组合：

```bash
rustup toolchain list | grep nightly | grep -vE "nightly-x86|01-17" | sed 's/-x86.*//' | xargs rustup toolchain uninstall
```

# 练习

1. 如果你不熟悉正则表达式，
   [这里](https://regexone.com/) 有一个简短的交互式教程，
   涵盖了大部分基础知识。

1. `sed s/REGEX/SUBSTITUTION/g` 和普通 `sed` 有什么不同？
   `/I` 或 `/m` 又分别有什么作用？

1. 进行原地替换时，很自然会想执行类似
   `sed s/REGEX/SUBSTITUTION/ input.txt > input.txt` 的操作。
   但这是一个糟糕的做法——为什么？这和 `sed` 本身有关吗？

1. 用你熟悉的语言（使用正则表达式）实现一个简易的 `grep`。
   如果希望输出像 `grep` 那样有高亮颜色，请搜索 ANSI 颜色
   转义序列。

1. 有时，使用原始 `mv` 命令来重命名文件可能会很棘手。
   `rename` 是一个巧妙的工具，可以达到这个目的，而且
   具有类似 `sed` 的语法。试着创建一堆文件名中包含空格的文件，
   然后用 `rename` 把它们替换为下划线。

1. 找出你过去三次重启中_没有_共享的启动消息
   （参见 `journalctl` 的 `-b` 参数）。你可能想把所有
   启动日志合并到一个文件中，这样可能会更容易处理。

1. 使用日志时间戳，统计过去十次启动中系统启动时间的若干
   统计数据。可以关注以下消息：
   ```
   Logs begin at ...
   ```
   以及
   ```
   systemd[577]: Startup finished in ...
   ```

1. 在 `/usr/share/dict/words` 中找出包含至少三个 `a`
   且不以 `'s` 结尾的单词数量。这些单词最常见的最后两个
   字母是什么？`sed` 的 `y` 命令，或者 `tr` 程序，
   可以帮助你处理大小写不敏感的问题。这样的双字母组合有多少？
   还有一个进阶问题：哪些组合_从未_出现过？

1. 找一个在线数据集合，比如
   [这个](https://commons.wikimedia.org/wiki/Data:Wikipedia_statistics/data.tab)
   或 [这个](https://ucr.fbi.gov/crime-in-the-u.s/2016/crime-in-the-u.s.-2016/topic-pages/tables/table-1)。
   也可以从 [这个站点](https://www.springboard.com/blog/data-science/free-public-data-sets-data-science-project/) 找。
   使用 `curl` 获取它，并提取出两个数值列。
   如果是 HTML 数据，[`pup`](https://github.com/EricChiang/pup) 可能很有用。
   如果是 JSON 数据，试试 [`jq`](https://stedolan.github.io/jq/)。
   在一个命令中找到某一列的最小值和最大值，
   在另一个命令中计算两列之间差异的总和。

---

> 译者注：本文件基于 [The Missing Semester](https://missing.csail.mit.edu/) 的英文原版
> 进行独立中文改编，未经原作者授权或审阅。原文版权归其作者所有。
> 如有翻译错误或不准确之处，以英文原文为准。