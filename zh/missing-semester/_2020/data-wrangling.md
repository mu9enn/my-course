---
layout: lecture
title: "数据搬运"
description: >
  学习如何使用 sed、awk 和正则表达式等命令行工具来操作和转换数据。
thumbnail: /static/assets/thumbnails/2020/lec4.png
date: 2020-01-16
ready: true
video:
  aspect: 56.25
  id: sz_dsktIjt4
special: true
---

你有没有过这样的经历：想把一份数据从一种格式转换成另一种格式？当然有过！这篇讲座的核心内容就是讲这件事。具体来说，就是如何反复"揉捏"（massage）数据——无论它是文本格式还是二进制格式——直到它变成你想要的样子。

我们在之前的讲座中已经接触过一些基本的数据搬运操作。基本上每次你使用 `|`（管道）操作符的时候，你就在进行某种形式的数据搬运。考虑这样一个命令：`journalctl | grep -i intel`。它会找出所有系统日志中提到 Intel 的行（忽略大小写）。你可能不觉得这是在搬运数据，但它确确实实把一种格式（你整个系统日志）转换成了对你更有用的格式（仅包含 Intel 的行日志）。大部分数据搬运工作就是：你知道自己有哪些工具可用，以及如何把它们组合起来。

我们从最基本的开始。要进行数据搬运，你需要两样东西：要搬运的数据，以及用来处理它的工具。日志文件通常是一个很好的用例，因为你经常想要调查其中的某些内容，而且通读整个日志并不现实。我们来查看一下谁在尝试登录我的服务器——通过查看我的服务器日志：

```bash
ssh myserver journalctl
```

这输出太多了。让我们把它缩小到仅包含 ssh 相关的内容：

```bash
ssh myserver journalctl | grep sshd
```

注意我们在这里用管道把_远程_文件传送到本机的 `grep` 上！`ssh` 非常神奇，我们将在关于 shell 环境的下一节讲座中进一步讨论它。但这仍然远远多于我们需要的内容，而且很难阅读。让我们做得更好一些：

```bash
ssh myserver 'journalctl | grep sshd | grep "Disconnected from"' | less
```

为什么需要额外的引号？好吧，我们的日志可能非常大，把所有数据都传送到我们电脑上再做过滤是一种浪费。相反，我们可以先在远程服务器上完成过滤，然后再在本地对数据进行搬运。`less` 提供了一个"分页器"（pager），让我们可以在冗长的输出内容中上下滚动。为了在我们调试命令行时节省一些网络流量，我们甚至可以把当前过滤好的日志存到一个文件中，这样在开发阶段就不需要联网了：

```console
$ ssh myserver 'journalctl | grep sshd | grep "Disconnected from"' > ssh.log
$ less ssh.log
```

这里仍然有很多噪音。有很多方法可以消除它们，但让我们来看看你的工具箱中最强大的工具之一：`sed`。

`sed` 是一个"流编辑器"（stream editor），它构建在古老的 `ed` 编辑器之上。在 `sed` 中，你基本上给出简短的指令来描述如何修改文件，而不是直接操纵文件内容（虽然你也可以这样做）。它有很多命令，但其中最常用的一个是 `s`：替换（substitution）。例如，我们可以这样写：

```bash
ssh myserver journalctl
 | grep sshd
 | grep "Disconnected from"
 | sed 's/.*Disconnected from //'
```

我们刚刚写的是一个简单的_正则表达式_（regular expression）——一种强大的构造，允许你根据模式来匹配文本。`s` 命令的写法是 `s/正则表达式/替换内容/`，其中`正则表达式`是你要搜索的模式，`替换内容`是你希望用哪些文本来替换匹配到的内容。

（你可能在 Vim [讲义文档](/2020/editors/#advanced-vim)的"查找并替换"部分认出这种语法了！事实上，Vim 使用的一种搜索替换语法与 `sed` 的替换命令类似。学会一种工具，往往会让你对其他工具变得更加熟练。）

## 正则表达式

正则表达式非常常见且实用，值得花一些时间来理解它们是如何工作的。让我们从回顾上面用过的表达式 `/.*Disconnected from /` 开始。正则表达式通常（虽然不总是）被 `/` 包围。大多数 ASCII 字符都携带它们的字面含义，但有些字符具有"特殊"的匹配行为。不同字符具体做什么，在正则表达式的不同实现之间略有差异，而这正是令人非常抓狂的地方。下面是最常见的模式：

 - `.` 表示"除了换行符之外的任意单个字符"
 - `*` 匹配前面的表达式零次或多次
 - `+` 匹配前面的表达式一次或多次
 - `[abc]` 匹配 `a`、`b` 或 `c` 中的任意一个字符
 - `(RX1|RX2)` 匹配能匹配 `RX1` 或 `RX2` 的内容
 - `^` 行首
 - `$` 行尾

`sed` 的正则表达式有点特别，你通常需要在大多数这些符号前加上 `\` 才能让它们获得特殊含义。或者你也可以传入 `-E` 选项来启用扩展正则表达式。

所以，再看一下 `/.*Disconnected from /`，我们能看到它匹配的是：以任意数量的字符开头、后面跟着字面量字符串 "Disconnected from " 的文本。这正是我们想要的。但小心了，正则表达式是会有陷阱的。如果有人在用户名中尝试使用 "Disconnected from" 来登录呢？我们会看到类似这样的日志：

```
Jan 17 03:13:00 thesquareplanet.com sshd[2631]: Disconnected from invalid user Disconnected from 46.97.239.16 port 55920 [preauth]
```

最终我们会得到什么？`*` 和 `+` 默认情况下是"贪婪的"（greedy），它们会尽可能多地匹配文本。因此，在上面这个例子中，我们最终只得到

```
46.97.239.16 port 55920 [preauth]
```

这可能不是你想要的结果。在某些正则表达式实现中，你可以在 `*` 或 `+` 后面加一个 `?` 来让它们变成非贪婪的（non-greedy），但不幸的是 `sed` 不支持这个特性。不过我们_可以_切换到 perl 的命令行模式，它_支持_这个构造：

```bash
perl -pe 's/.*?Disconnected from //'
```

在这篇讲座的其余部分我们将继续使用 `sed`，因为它在同类工作中无疑是最常见的工具。`sed` 还能做其他一些方便的事情，比如打印匹配行之后的内容、每次调用执行多次替换、搜索内容等。但我们在这里不会覆盖太多这些内容。`sed` 基本上自成一大主题，但通常往往有更好的工具。

好的，我们还有一个后缀也想去掉。我们要怎么做呢？要只匹配用户名_后面_的文本会有一点棘手，尤其是用户名中可以包含空格之类的字符！我们需要做的是匹配_整行_：

```bash
 | sed -E 's/.*Disconnected from (invalid |authenticating )?user .* [^ ]+ port [0-9]+( \[preauth\])?$//'
```

让我们在 [正则表达式调试器](https://regex101.com/r/qqbZqh/2) 中看看发生了什么。好的，开头部分与之前相同。然后，我们匹配"user"的各种变体（日志中有两种前缀）。接下来匹配代表用户名字符串的任意字符序列。然后是匹配任意单个单词（`[^ ]+`；即任意非空的非空格字符序列）。接着是单词 "port"，后面跟着一串数字。然后可能是后缀 `[preauth]`，以及行尾。

注意，使用这种技巧之后，即使用户名是 "Disconnected from" 也不会再让我们困惑了。你能看出为什么吗？

但这里有一个问题：整个日志都会变成空行。因为我们毕竟是想_保留_用户名的。为此，我们可以使用"捕获组"（capture groups）。正则表达式中被括号 `()` 包裹的部分会被存储在一个编号的捕获组中。这些捕获组在替换表达式中（在某些引擎中，甚至在模式本身内部！）都可以作为 `\1`、`\2`、`\3` 等来引用。所以：

```bash
 | sed -E 's/.*Disconnected from (invalid |authenticating )?user (.*) [^ ]+ port [0-9]+( \[preauth\])?$/\2/'
```

正如你大概能想象的那样，你可以构造出_极其_复杂的正则表达式。例如，这里有一篇文章讲解如何匹配一个[电子邮件地址](https://www.regular-expressions.info/email.html)。这[并不容易](https://web.archive.org/web/20221223174323/http://emailregex.com/)。而且[有大量讨论](https://stackoverflow.com/questions/201323/how-to-validate-an-email-address-using-a-regular-expression/1917982)。人们还[编写了测试](https://fightingforalostcause.net/content/misc/2006/compare-email-regex.php)和[测试矩阵](https://mathiasbynens.be/demo/url-regex)。你甚至能用正则表达式来判断一个给定的数字[是否是素数](https://www.noulakaz.net/2007/03/18/a-regular-expression-to-check-for-prime-numbers/)。

正则表达式以"很难写对"而著称，但它们在你的工具箱中确实非常实用！

## 回到数据搬运

好的，现在我们得到了

```bash
ssh myserver journalctl
 | grep sshd
 | grep "Disconnected from"
 | sed -E 's/.*Disconnected from (invalid |authenticating )?user (.*) [^ ]+ port [0-9]+( \[preauth\])?$/\2/'
```

`sed` 还能做各种其他有趣的事情，比如注入文本（使用 `i` 命令）、显式打印行（使用 `p` 命令）、按索引选择行等。去查一下 `man sed` 吧！

不管怎样。我们现在得到的是一份所有尝试过登录的用户名列表。但这还不太有帮助。让我们找找哪些用户名最常见：

```bash
ssh myserver journalctl
 | grep sshd
 | grep "Disconnected from"
 | sed -E 's/.*Disconnected from (invalid |authenticating )?user (.*) [^ ]+ port [0-9]+( \[preauth\])?$/\2/'
 | sort | uniq -c
```

`sort` 会对输入进行_排序_。`uniq -c` 会把连续相同的行合并为一行，并在前面加上出现次数作为前缀。我们可能也想对结果进行排序，只保留出现次数最多的用户名：

```bash
ssh myserver journalctl
 | grep sshd
 | grep "Disconnected from"
 | sed -E 's/.*Disconnected from (invalid |authenticating )?user (.*) [^ ]+ port [0-9]+( \[preauth\])?$/\2/'
 | sort | uniq -c
 | sort -nk1,1 | tail -n10
```

`sort -n` 会以数字顺序（而不是字典序）进行排序。`-k1,1` 表示"仅按第一个空白分隔的列排序"。`,n` 部分表示"排序到第 `n` 个字段为止"，默认是到行尾。在这个_特别_的例子中，按整行排序没什么区别，但我们这里是为了学习！

如果我们想要_最少_见的那些，可以用 `head` 代替 `tail`。另外也有 `sort -r`，可以反向排序。

好的，这已经相当酷了，但如果我们想把用户名提取成一个逗号分隔的列表（而不是一行一个），或许是为了配置文件，该怎么做呢？

```bash
ssh myserver journalctl
 | grep sshd
 | grep "Disconnected from"
 | sed -E 's/.*Disconnected from (invalid |authenticating )?user (.*) [^ ]+ port [0-9]+( \[preauth\])?$/\2/'
 | sort | uniq -c
 | sort -nk1,1 | tail -n10
 | awk '{print $2}' | paste -sd,
```

如果你在使用 macOS：注意，如上面所示的命令无法与 macOS 自带的 BSD 版 `paste` 配合使用。请参阅[shell 工具讲座的练习题 4](/2020/shell-tools/#exercises)，了解更多关于 BSD 和 GNU coreutils 之间差异的内容，以及如何在 macOS 上安装 GNU coreutils 的说明。

让我们从 `paste` 开始：它允许你用给定的单字符分隔符（此处是 `,`）把多行合并为一行（使用 `-s` 选项）。但那是什么 `awk` 的东西？

## awk —— 另一种编辑器

`awk` 是一种_碰巧_非常擅长处理文本流的编程语言。如果你认真学习 `awk`，可以说的东西_多得很_，但就像这里提到的其他很多工具一样，我们只涵盖最基础的部分。

首先，`{print $2}` 是做什么的？`awk` 程序的格式是：一个可选的模式（pattern）加上一个代码块，表示当该模式匹配到某一行时该做什么。默认模式（我们上面使用的就是这种）匹配所有行。在代码块内部，`$0` 被设置为整行的内容，而 `$1` 到 `$n` 则被设置为该行被 `awk` 字段分隔符分隔后的第 `n` 个_字段_（默认以空白分隔，可通过 `-F` 修改）。在这里，我们说的是：对于每一行，打印第二个字段的内容，恰好就是用户名！

让我们看看能否做点更花哨的事情。我们来统计一下出现次数为 1、以 `c` 开头并以 `e` 结尾的用户名有多少个：

```bash
 | awk '$1 == 1 && $2 ~ /^c[^ ]*e$/ { print $2 }' | wc -l
```

这里面有不少值得拆解的东西。首先注意，我们现在有一个模式（即 `{...}` 之前的部分）。模式表示：行的第一个字段应等于 1（即 `uniq -c` 给出的计数），而且第二个字段应匹配给定的正则表达式。而代码块仅仅是打印那个用户名。然后我们用 `wc -l` 统计输出的行数。

不过，`awk` 是一门编程语言，记住？

```awk
BEGIN { rows = 0 }
$1 == 1 && $2 ~ /^c[^ ]*e$/ { rows += $1 }
END { print rows }
```

`BEGIN` 是一个匹配输入开头的模式（`END` 匹配结尾）。现在，每行处理的代码块会把第一个字段的计数累加起来（虽然在这种情况下它总是 1），然后在最后打印出总数。事实上，我们_可以_完全去掉 `grep` 和 `sed`，因为 `awk` [什么都能做](https://web.archive.org/web/20251210045942/https://backreference.org/2010/02/10/idiomatic-awk/)，但这就留给读者作为练习了。

## 数据分析

你可以直接在 shell 中用 `bc` 做数学计算——`bc` 是一个能从标准输入读取内容的_计算器_！例如，把每行的数字连在一起，用 `+` 分隔，然后相加：

```bash
 | paste -sd+ | bc -l
```

或者生成更复杂的表达式：

```bash
echo "2*($(data | paste -sd+))" | bc -l
```

你可以通过多种方式获取统计数据。[`st`](https://github.com/nferraz/st) 是个相当不错的工具，但如果你已经有了 [R](https://www.r-project.org/)：

```bash
ssh myserver journalctl
 | grep sshd
 | grep "Disconnected from"
 | sed -E 's/.*Disconnected from (invalid |authenticating )?user (.*) [^ ]+ port [0-9]+( \[preauth\])?$/\2/'
 | sort | uniq -c
 | awk '{print $1}' | R --no-echo -e 'x <- scan(file="stdin", quiet=TRUE); summary(x)'
```

R 是另一种（有点_古怪_）编程语言，非常适合数据分析和[绘图](https://ggplot2.tidyverse.org/)。我们不会深入细节，但简单来说，`summary` 会打印一个向量的汇总统计信息，而我们创建了一个包含输入数字流的向量，所以 R 给我们提供了我们想要的统计数据！

如果你只想做一些简单的绘图，`gnuplot` 是你的好帮手：

```bash
ssh myserver journalctl
 | grep sshd
 | grep "Disconnected from"
 | sed -E 's/.*Disconnected from (invalid |authenticating )?user (.*) [^ ]+ port [0-9]+( \[preauth\])?$/\2/'
 | sort | uniq -c
 | sort -nk1,1 | tail -n10
 | gnuplot -p -e 'set boxwidth 0.5; plot "-" using 1:xtic(2) with boxes'
```

## 用数据搬运来构造命令行参数

有时候你希望进行数据搬运，以便从较长的列表中找出要安装或移除的东西。前面讨论过的数据搬运方法加上 `xargs` 可以形成非常强大的组合。

例如，如在讲座中看到的，我可以使用以下命令，通过数据搬运工具提取出旧版的 nightly 构建名称，然后通过 `xargs` 将它们传递给卸载工具，从而从系统中卸载旧的 Rust nightly 构建：

```bash
rustup toolchain list | grep nightly | grep -vE "nightly-x86" | sed 's/-x86.*//' | xargs rustup toolchain uninstall
```

## 处理二进制数据

到目前为止，我们主要讨论的是搬运文本型数据，但管道在处理二进制数据时同样有用。例如，我们可以使用 ffmpeg 从摄像头捕获一张图片，将其转换为灰度，压缩，通过 SSH 传送到远程机器上，在那里解压、做一份拷贝，然后显示出来。

```bash
ffmpeg -loglevel panic -i /dev/video0 -frames 1 -f image2 -
 | convert - -colorspace gray -
 | gzip
 | ssh mymachine 'gzip -d | tee copy.jpg | env DISPLAY=:0 feh -'
```

# 练习题

1. 完成这个[简短的正则表达式交互式教程](https://regexone.com/)。
2. 找出 `/usr/share/dict/words` 中至少包含三个 `a` 且不以 `'s` 结尾的单词数量。这些单词中，最常见的最后两个字母是什么？`sed` 的 `y` 命令，或者 `tr` 程序，可以帮助你忽略大小写。这样的双字母组合有多少种？作为一个挑战：哪些组合_没有_出现过？
3. 想做原地替换（in-place substitution）时，很容易想到类似 `sed s/REGEX/SUBSTITUTION/ input.txt > input.txt` 的做法。但这是一个_坏主意_，为什么？这仅是 `sed` 特有的问题吗？使用 `man sed` 查找如何完成这个操作。
4. 找出过去十次开机中你的系统平均、中位数和最长开机时间。在 Linux 上使用 `journalctl`，在 macOS 上使用 `log show`，查找每次开机开始和结束时附近的日志时间戳。在 Linux 上，它们可能看起来像这样：
   ```
   Logs begin at ...
   ```
   以及
   ```
   systemd[577]: Startup finished in ...
   ```
   在 macOS 上，[查找](https://eclecticlight.co/2018/03/21/macos-unified-log-3-finding-your-way/)：
   ```
   === system boot:
   ```
   以及
   ```
   Previous shutdown cause: 5
   ```
5. 找出那些在_你过去三次_重启中_没有_共同出现的启动消息（参见 `journalctl` 的 `-b` 标志）。把这个任务拆分为多个步骤。首先，找到一个方法来仅获取过去三次开机的日志。你要使用的提取日志的工具可能有一个适用的标志，或者你可以使用 `sed '0,/STRING/d'` 来删除所有在匹配 `STRING` 的行_之前_的行。接下来，去掉行中_始终_变化的部分（比如时间戳）。然后，对输入去重并统计每个行的出现次数（`uniq` 是你的好帮手）。最后，消除任何出现次数为 3 的行（因为它_在_所有三次开机中_都_出现过）。
6. 找一个在线数据集，比如[这个](https://commons.wikimedia.org/wiki/Data:Wikipedia_statistics/data.tab)、[这个](https://ucr.fbi.gov/crime-in-the-u.s/2016/crime-in-the-u.s.-2016/topic-pages/tables/table-1)，或者也许是[这里](https://www.springboard.com/blog/data-science/free-public-data-sets-data-science-project/)的一个。使用 `curl` 获取它，并从中仅提取两列数值数据。如果你获取的是 HTML 数据，[`pup`](https://github.com/EricChiang/pup) 可能会有帮助。对于 JSON 数据，尝试使用 [`jq`](https://stedolan.github.io/jq/)。在一个命令中找出某一列的最小值和最大值，在另一个命令中计算两列求和之后的差值。