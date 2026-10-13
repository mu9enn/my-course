---
layout: lecture
title: "版本控制与 Git"
description: >
  了解 Git 的数据模型，以及如何使用 Git 进行版本控制和协作。
thumbnail: /static/assets/thumbnails/2026/lec5.png
date: 2026-01-16
ready: true
video:
  aspect: 56.25
  id: 9K8lB61dl3Y
---

版本控制系统（Version Control Systems, VCS）是用于追踪源代码（或其他文件和文件夹集合）变更的工具。顾名思义，这类工具帮助维护一个变更历史记录；不仅如此，它们还促进了团队协作。从逻辑上讲，VCS 通过一系列_快照（snapshots）_来追踪一个文件夹及其内容的变更，其中每个快照封装了顶层目录中所有文件/文件夹的完整状态。VCS 还会保存元数据，例如谁创建了每个快照、每个快照关联的提交说明（commit message），等等。

版本控制为何有用？即使你独自工作，它也能让你查看旧的项目快照、保留某些变更的原因日志、在平行的开发分支上工作，以及做更多事情。与他人协作时，它是查看他人做了哪些变更以及解决并发开发冲突的不可或缺的工具。

现代 VCS 还能轻松（且经常自动）回答如下问题：

- 这个模块是谁写的？
- 这个特定文件的这一行是什么时候被编辑的？由谁编辑的？为什么要改？
- 在最近 1000 次修订中，某个单元测试是在何时/为何开始失效的？

尽管存在其他 VCS，**Git** 已是版本控制的事实标准。[XKCD 1597 号漫画](https://xkcd.com/1597/)捕捉到了 Git 的名声：

![xkcd 1597](https://imgs.xkcd.com/comics/git.png)

由于 Git 的接口是一种"有漏洞的抽象"（leaky abstraction），自上而下地学习 Git（从它的接口 / 命令行界面开始）会造成大量困惑。人们可以死记硬背几条命令，把它们当作魔法咒语，并在出问题时按照上面漫画中的方式操作。

Git 的接口确实不够优雅，但它的底层设计和理念却非常精妙。丑陋的接口只能被_死记硬背_，而精妙的设计可以被_理解_。正因如此，我们采用自底向上的方式来讲解 Git：先从它的数据模型（data model）讲起，随后再覆盖命令行接口。一旦理解了数据模型，你就能明白各个命令如何操作底层的数据结构。

# Git 的数据模型

Git 的巧妙之处在于其设计周到的数据模型，该模型支撑了版本控制的所有出色特性，如维护历史、支持分支和启用协作。

## 快照（Snapshots）

Git 将某个顶层目录中文件及文件夹集合的历史建模为一连串快照。在 Git 术语中，一个文件被称为"blob"（二进制大对象），它只是一串字节。一个目录被称为"tree"（树），它将名称映射到 blob 或 tree（因此目录可以包含其他目录）。一个快照就是正在被追踪的顶层 tree。例如，我们可能有如下 tree 结构：

```
<root> (tree)
|
+- foo (tree)
|  |
|  + bar.txt (blob, contents = "hello world")
|
+- baz.txt (blob, contents = "git is wonderful")
```

顶层 tree 包含两个元素：一个 tree "foo"（其本身包含一个元素——blob "bar.txt"），以及一个 blob "baz.txt"。

## 历史建模：快照之间的关系

版本控制系统应该如何关联快照？一种简单的模型是拥有线性历史（linear history），即一个按时间顺序排列的快照列表。出于各种原因，Git 并没有使用类似这样的简单模型。

在 Git 中，历史是一个快照组成的有向无环图（Directed Acyclic Graph, DAG）。听起来可能像个高深的名词，但不用害怕。它的含义仅仅是：Git 中的每个快照都会引用一组"父节点（parents）"——即它之前的快照。而是一组而非单个父节点（在线性历史中会是单个）的原因是：一个快照可能源自多个父节点，例如在合并（merging）两条平行的开发分支时。

Git 将这些快照称为"提交（commit）"。可视化一段提交历史可能如下所示：

```
o <-- o <-- o <-- o
            ^
             \
              --- o <-- o
```

在上方的 ASCII 示意图中，`o` 对应各个提交（快照）。箭头指向每个提交的父节点（这是"先于"关系，而不是"后于"）。在第三次提交之后，历史分叉成了两条独立的分支。这可能对应，例如，两个独立的特性被独立且并行地开发。未来，这些分支可能会被合并，生成一个同时整合了两个特性的新快照，产生如下所示的新历史，其中新生成的合并提交以粗体标出：

<pre class="highlight">
<code>
o <-- o <-- o <-- o <---- <strong>o</strong>
            ^            /
             \          v
              --- o <-- o
</code>
</pre>

Git 中的提交是不可变的（immutable）。但这并不意味着不能纠正错误——只是对提交历史的"编辑"实际上是在创建全新的提交，然后引用（references，见下文）会更新指向新的提交。

## 数据模型的伪代码

用伪代码写出 Git 的数据模型或许能帮助理解：

```
// 文件是一串字节
type blob = array<byte>

// 目录包含命名的文件和目录
type tree = map<string, tree | blob>

// 提交拥有父节点、元数据和顶层 tree
type commit = struct {
    parents: array<commit>
    author: string
    message: string
    snapshot: tree
}
```

这是一套干净、简洁的历史模型。

## 对象与内容寻址（Content-addressing）

"对象（object）"是一个 blob、tree 或 commit：

```
type object = blob | tree | commit
```

在 Git 的数据存储中，所有对象都通过其 [SHA-1 哈希](https://en.wikipedia.org/wiki/SHA-1)进行内容寻址。

```
objects = map<string, object>

def store(object):
    id = sha1(object)
    objects[id] = object

def load(id):
    return objects[id]
```

Blob、tree 和 commit 统一于此：它们都是对象。当它们引用其他对象时，并不在其磁盘表示中真正_包含_它们，而是通过哈希来引用。

例如，上文 [快照](#snapshots) 中的目录结构对应的 tree（通过 `git cat-file -p 698281bc680d1995c5f4caaf3359721a5a58d48d` 可视化），如下所示：

```
100644 blob 4448adbf7ecd394f42ae135bbeed9676e894af85    baz.txt
040000 tree c68d233a33c5c06e0340e4c224f0afca87c8ce87    foo
```

tree 本身包含了对其内容的指针：`baz.txt`（一个 blob）和 `foo`（一个 tree）。如果我们查看由对应 baz.txt 的哈希所指向的内容，使用 `git cat-file -p 4448adbf7ecd394f42ae135bbeed9676e894af85`，得到如下结果：

```
git is wonderful
```

## 引用（References）

现在，所有快照都可以通过其 SHA-1 哈希来标识。这很不方便，因为人类不擅长记忆一串 40 位的十六进制字符。

Git 对此的解决方案是：给 SHA-1 哈希配上人类可读的名称，称为"引用（references）"。引用是指向提交的指针。与不可变的对象不同，引用是可变的（可以更新为指向一个新提交）。例如，`master` 引用通常指向主开发分支的最新提交。

```
references = map<string, string>

def update_reference(name, id):
    references[name] = id

def read_reference(name):
    return references[name]

def load_reference(name_or_id):
    if name_or_id in references:
        return load(references[name_or_id])
    else:
        return load(name_or_id)
```

有了这个机制，Git 就可以使用"master"这样的人类可读名称来引用历史中的特定快照，而不是一长串十六进制字符。

有一点需要注意：我们经常需要一种"我们当前在历史的什么位置"的概念，这样当我们创建新快照时，就知道它是相对于什么建立的（即如何设置提交的 `parents` 字段）。在 Git 中，"我们当前在哪里"由一个特殊的引用——"HEAD"——来表示。

## 仓库（Repositories）

最后，我们可以定义什么是（大致上）一个 Git _仓库（repository）_：它是数据 `objects`（对象）和 `references`（引用）。

在磁盘上，所有 Git 存储都是对象和引用——这就是 Git 数据模型的全部。所有 `git` 命令都映射为通过添加对象和添加/更新引用来操作提交 DAG 的某种方式。

每当你在输入任何命令时，想一想这个命令在对底层图数据结构做怎样的操作。反过来，如果你试图对提交 DAG 做某种特定的变更，例如"丢弃未提交的更改，让 'master' 引用指向提交 `5d83f9e`"，很可能有一个命令可以做到（例如在这种情况下，`git checkout master; git reset --hard 5d83f9e`）。

# 暂存区（Staging Area）

这是另一个与数据模型正交（orthogonal）的概念，但它是在创建提交时的接口的一部分。

你可能会想象以如下方式实现上述的快照功能：有一个"创建快照"命令，该命令基于工作目录的_当前状态_创建新快照。有些版本控制工具就是这样工作的，但 Git 不是。我们希望提交干净的快照，而从当前状态创建快照并不总是理想的。例如，假设你实现了两个独立的功能，希望创建两个独立的提交，其中第一个引入第一个功能，第二个引入第二个功能。或者假设你在代码中到处添加了调试用 print 语句，同时还修复了一个 bug；你希望提交 bug 修复的同时丢弃所有 print 语句。

Git 通过一个称为"暂存区（staging area）"的机制来解决这类场景，允许你指定哪些修改应该包含在下一个快照中。

# Git 命令行接口

为了避免重复信息，我们不会在讲义中详细解释下面的命令。详见强烈推荐参考的 [Pro Git](https://git-scm.com/book/en/v2)，或观看授课视频。

## 基本操作

- `git help <command>`：获取 Git 命令的帮助
- `git init`：创建一个新的 Git 仓库，数据存储在 `.git` 目录中
- `git status`：告诉你当前状况
- `git add <filename>`：将文件添加到暂存区
- `git commit`：创建新提交
    - 编写[好的提交说明](https://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html)！
    - 更多编写[好的提交说明](https://chris.beams.io/posts/git-commit/)的理由！
- `git log`：展示扁平的历史日志
- `git log --all --graph --decorate`：以图形式可视化历史
- `git diff <filename>`：展示相对于暂存区的变更
- `git diff <revision> <filename>`：展示两个快照之间某个文件的差异
- `git checkout <revision>`：更新 HEAD（如果检出一个分支，还会更新当前分支）

## 分支与合并

- `git branch`：显示分支
- `git branch <name>`：创建分支
- `git switch <name>`：切换到分支
- `git checkout -b <name>`：创建分支并切换到它
    - 等价于 `git branch <name>; git switch <name>`
- `git merge <revision>`：合并到当前分支
- `git mergetool`：使用高级工具来帮助解决合并冲突
- `git rebase`：将一组补丁重新变基（rebase）到一个新的基线上

## 远程仓库（Remotes）

- `git remote`：列出远程仓库
- `git remote add <name> <url>`：添加一个远程仓库
- `git push <remote> <local branch>:<remote branch>`：将对象发送到远程仓库，并更新远程引用
- `git branch --set-upstream-to=<remote>/<remote branch>`：设置本地与远程分支之间的对应关系
- `git fetch`：从远程仓库获取对象和引用
- `git pull`：等价于 `git fetch; git merge`
- `git clone`：从远程仓库下载仓库

## 撤销

- `git commit --amend`：编辑提交的 contents/说明
- `git reset <file>`：从暂存区取消文件
- `git restore`：丢弃变更

# 进阶 Git

- `git config`：Git [高度可定制](https://git-scm.com/docs/git-config)
- `git clone --depth=1`：浅克隆（shallow clone），不带完整的版本历史
- `git add -p`：交互式暂存
- `git rebase -i`：交互式变基
- `git blame`：显示每一行最后由谁编辑
- `git stash`：临时移除对当前工作目录的修改
- `git bisect`：在历史中二分查找（例如用于定位回归问题）
- `git revert`：创建一个新的提交，其效果是反转某个先前提交
- `git worktree`：同时检出多个分支
- `.gitignore`：[指定](https://git-scm.com/docs/gitignore)应被忽略的有意未跟踪的文件

# 杂项

- **图形界面（GUIs）**：Git 有许多[图形界面客户端](https://git-scm.com/downloads/guis)。我们自己不使用图形界面，而是使用命令行接口。
- **Shell 集成**：在你的 shell 提示符中包含 Git 状态信息非常实用（[zsh](https://github.com/olivierverdier/zsh-git-prompt)、[bash](https://github.com/magicmonty/bash-git-prompt)）。通常包含在如 [Oh My Zsh](https://github.com/ohmyzsh/ohmyzsh) 之类的框架中。
- **编辑器集成**：与上面类似，有很多实用的集成方案。[fugitive.vim](https://github.com/tpope/vim-fugitive) 是 Vim 中的标准集成方案。
- **工作流（Workflows）**：我们教了你数据模型和一些基本命令，但没有告诉你在使用大型项目时应该遵循哪些实践（并且[有许多](https://nvie.com/posts/a-successful-git-branching-model/)[不同的](https://www.endoflineblog.com/gitflow-considered-harmful)[方法](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow)）。
- **GitHub**：Git 不等于 GitHub。GitHub 有一种特有的向其他项目贡献代码的方式，称为[拉取请求（Pull Requests）](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/about-pull-requests)。
- **其他 Git 托管平台**：GitHub 并不特殊：有许多 Git 仓库托管服务，如 [GitLab](https://about.gitlab.com/) 和 [BitBucket](https://bitbucket.org/)。

# 资源

- [Pro Git](https://git-scm.com/book/en/v2) 是**强烈推荐的读物**。在阅读了第 1 到第 5 章后，你应该已经能熟练使用 Git。因为你现在理解了数据模型，后面的章节包含一些有趣的进阶内容。
- [Oh Shit, Git!?!](https://ohshitgit.com/) 是一份简短指南，教你如何从常见的 Git 错误中恢复。
- [Git for Computer Scientists](https://eagain.net/articles/git-for-computer-scientists/) 是对 Git 数据模型的简短解释，比这些讲义更少的伪代码、更多的精美图解。
- [Git from the Bottom Up](https://jwiegley.github.io/git-from-the-bottom-up/) 对超出数据模型本身的 Git 实现细节做了详细说明，适合好奇的读者。
- [How to explain git in simple words](https://smusamashah.github.io/blog/2017/10/14/explain-git-in-simple-words)
- [Learn Git Branching](https://learngitbranching.js.org/) 是一款基于浏览器的 Git 教学游戏。

# 练习

1. 如果你没有 Git 的使用经验，可以尝试阅读 [Pro Git](https://git-scm.com/book/en/v2) 的前几章，或使用类似 [Learn Git Branching](https://learngitbranching.js.org/) 的教程。在学习过程中，将 Git 命令与数据模型联系起来。
1. 克隆 [课程网站的仓库](https://github.com/missing-semester/missing-semester)。
    1. 通过将其可视化为图来探索版本历史。
    1. 最后一个修改 `README.md` 的人是谁？（提示：使用带参数的 `git log`）。
    1. `collections:` 这一行的最后一次修改关联的提交说明是什么？（提示：使用 `git blame` 和 `git show`）。
1. 学习 Git 时的一个常见错误是提交不应该由 Git 管理的大型文件或添加敏感信息。尝试将文件添加到仓库中，进行若干次提交，然后从_历史记录中_删除该文件（而不仅仅是从最新提交中删除）。你可能需要查看[这篇指南](https://help.github.com/articles/removing-sensitive-data-from-a-repository/)。
1. 从 GitHub 克隆某个仓库，并修改其现有文件之一。当你执行 `git stash` 时会发生什么？运行 `git log --all --oneline` 时你看到了什么？运行 `git stash pop` 撤销你用 `git stash` 所做的操作。在什么场景下这可能有用？
1. 与许多命令行工具一样，Git 提供了一个配置文件（或 dotfile）叫 `~/.gitconfig`。在 `~/.gitconfig` 中创建一个别名，这样当你运行 `git graph` 时，你可以获得 `git log --all --graph --decorate --oneline` 的输出。你可以直接[编辑](https://git-scm.com/docs/git-config#Documentation/git-config.txt-alias) `~/.gitconfig` 文件，也可以使用 `git config` 命令来添加别名。关于 Git 别名的信息可以在[这里](https://git-scm.com/book/en/v2/Git-Basics-Git-Aliases)找到。
1. 在运行 `git config --global core.excludesfile ~/.gitignore_global` 之后，你可以在 `~/.gitignore_global` 中定义全局忽略模式。这会设置 Git 使用的全局忽略文件的位置，但你仍然需要手动在该路径创建文件。设置你的全局 gitignore 文件来忽略特定操作系统或编辑器的临时文件，例如 `.DS_Store`。
1. 分叉 [课程网站的仓库](https://github.com/missing-semester/missing-semester)，找到一个你可以修复的拼写错误或其他改进之处，然后在 GitHub 上提交一个拉取请求（你可能需要查看[这个指南](https://github.com/firstcontributions/first-contributions)）。请只提交有用的 PR（请不要 spam 我们！）。如果你找不到可以改进的地方，可以跳过此练习。
1. 通过模拟协作场景来练习解决合并冲突：
    1. 使用 `git init` 创建新仓库，并创建一个名为 `recipe.txt` 的文件，写入几行内容（例如一个简单菜谱）。
    1. 提交它，然后创建两个分支：`git branch salty` 和 `git branch sweet`。
    1. 在 `salty` 分支中修改一行（例如将 "1 cup sugar" 改为 "1 cup salt"）并提交。
    1. 在 `sweet` 分支中不同地修改同一行（例如将 "1 cup sugar" 改为 "2 cups sugar"）并提交。
    1. 现在切换到 `master` 并尝试 `git merge salty`，然后 `git merge sweet`。会发生什么？查看 `recipe.txt` 的内容 —— `<<<<<<<`、`=======` 和 `>>>>>>>` 标记分别是什么意思？
    1. 通过编辑文件保留你想保留的内容、移除冲突标记，然后使用 `git add` 和 `git commit`（或 `git merge --continue`）完成合并来解决冲突。或者，尝试使用 `git mergetool` 通过图形或终端合并工具来解决冲突。
    1. 使用 `git log --graph --oneline` 可视刚刚创建的合并历史。