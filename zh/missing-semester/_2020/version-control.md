---
layout: lecture
title: "版本控制（Git）"
description: >
  学习 Git 的数据模型，以及如何利用 Git 进行版本控制和团队协作。
thumbnail: /static/assets/thumbnails/2020/lec6.png
date: 2020-01-22
ready: true
video:
  aspect: 56.25
  id: 2sjqTHE0zok
---

版本控制系统（Version Control Systems，简称 VCS）是用来追踪源代码（或其他文件与文件夹集合）变更的工具。顾名思义，这类工具帮助维护变更历史记录；此外，它们也促进了多人协作。VCS 通过一系列快照（snapshot）来追踪文件夹及其内容的变更，其中每个快照封装了顶层目录下所有文件/文件夹的完整状态。VCS 还会维护一些元数据（metadata），比如谁创建了每个快照、每个快照关联的提交信息等。

版本控制为什么有用？即使你独自工作，它也能让你查看项目的旧快照、记录某些变更的原因、在并行的开发分支上工作，以及更多功能。当与他人合作时，版本控制是了解别人做了什么、以及解决并行开发中的冲突的宝贵工具。

现代 VCS 还能让你轻松地（且通常是自动地）回答以下问题：

- 这个模块是谁写的？
- 某个特定文件的这一行是什么时候被编辑的？谁编辑的？为什么编辑？
- 在过去 1000 次修订中，某个单元测试是什么时候/为什么坏掉的？

虽然还存在其他 VCS，但 **Git** 是版本控制的实际标准。这个 [XKCD 漫画](https://xkcd.com/1597/) 很好地反映了 Git 的名声：

![xkcd 1597](https://imgs.xkcd.com/comics/git.png)

由于 Git 的接口是一种**有漏洞的抽象**（leaky abstraction）——即接口没有完全隐藏底层复杂性，而是暴露了一些实现细节——自顶向下地学习 Git（从它的命令行接口开始）往往会导致大量困惑。你完全可以死记硬背几条命令，把它们当作咒语来念，然后在出现问题时遵循上述漫画中的方式。

诚然，Git 的接口不够优雅，但它的底层设计和思想非常优美。丑陋的接口只能 _死记_，而优美的设计则可以 _理解_。正因如此，我们从底向上讲解 Git：先介绍数据模型，然后再讲解命令行接口。一旦理解了数据模型，你就能更好地明白各个命令是如何操作底层数据结构的。

# Git 的数据模型

你可以用很多非正式的方式来处理版本控制，但 Git 拥有一个深思熟虑的模型，它使得版本控制的所有优秀特性成为可能——比如维护历史、支持分支、以及促进协作。

## 快照

Git 将某个顶层目录下的文件和文件夹集合的历史建模为一系列快照。在 Git 的术语中，一个文件被称为 **blob**，它仅仅是一堆字节；一个目录被称为 **树**（tree），它将名称映射到 blob 或树（所以目录可以包含其他目录）。所谓快照，就是当前正在被追踪的顶层树。例如，我们可能有一棵树如下所示：

```
<root> (tree)
|
+- foo (tree)
|  |
|  + bar.txt (blob, contents = "hello world")
|
+- baz.txt (blob, contents = "git is wonderful")
```

顶层树包含两个元素：一棵名为 "foo" 的树（其本身又包含一个元素——一个名为 "bar.txt" 的 blob），以及一个名为 "baz.txt" 的 blob。

## 建模历史：关联快照

版本控制系统应该如何关联快照？一种简单的方式是采用线性历史——即按时间顺序排列的快照列表。然而出于许多原因，Git 并没有使用这种简单模型。

在 Git 中，历史是快照组成的**有向无环图**（Directed Acyclic Graph，简称 DAG）。这听起来可能像一个花哨的数学术语，但别害怕。它的意思仅仅是：Git 中的每个快照都引用了一组**父快照**（parents），即它之前的快照。父快照是一组而非单个（在线性历史中则只有一个父快照），因为某个快照可能来源于多个父快照，例如，由于合并（merging）了两条并行开发分支。

Git 将这些快照称为 **commit**（提交）。一个提交历史的可视化可能看起来像这样：

```
o <-- o <-- o <-- o
            ^
             \
              --- o <-- o
```

在上方的 ASCII 图中，`o` 对应各个单独的提交（快照）。箭头指向每个提交的父提交（表示"在前"关系，而不是"在后"关系）。在第三次提交之后，历史分叉为两条独立的分支。这可能对应例如两条独立功能分支的并行开发。在未来，这些分支可能会被合并，创建一个融合了两个功能的新快照，产生看起来像这样的新历史，其中新创建的合并提交以粗体显示：

<pre class="highlight">
<code>
o <-- o <-- o <-- o <---- <strong>o</strong>
            ^            /
             \          v
              --- o <-- o
</code>
</pre>

Git 中的提交是不可变的（immutable）。这并不意味着错误无法纠正——它只是说，对提交历史的"编辑"实际上是在创建全新的提交，而引用（见下文）会被更新为指向新的提交。

## 伪代码形式的数据模型

用伪代码来呈现 Git 的数据模型可能会更有启发性：

```
// a file is a bunch of bytes
type blob = array<byte>

// a directory contains named files and directories
type tree = map<string, tree | blob>

// a commit has parents, metadata, and the top-level tree
type commit = struct {
    parents: array<commit>
    author: string
    message: string
    snapshot: tree
}
```

这是一个清晰、简洁的历史模型。

## 对象与内容寻址

**"对象"**（object）是一个 blob、树或提交：

```
type object = blob | tree | commit
```

在 Git 的数据存储中，所有对象都通过它们的 [SHA-1 哈希](https://en.wikipedia.org/wiki/SHA-1)进行**内容寻址**（content-addressed）。

```
objects = map<string, object>

def store(object):
    id = sha1(object)
    objects[id] = object

def load(id):
    return objects[id]
```

<!-- 译者注：SHA-1 是一种哈希算法。在 Git 中它仅用于生成对象的唯一标识符，不用于安全目的。尽管 SHA-1 已被证明存在碰撞漏洞，但对于"生成不可变对象的 ID"这一用途而言仍然足够好。Git 中一个对象的 ID 通常称为其"哈希"（hash）或"OID"（对象 ID）。 -->

Blob、树和提交以此方式统一起来——它们都是对象。当它们引用其他对象时，它们在磁盘上的表示中并不实际 _包含_ 这些对象，而是通过哈希值引用它们。

例如，上面[快照](#snapshots)章节中的示例目录结构的树（通过 `git cat-file -p 698281bc680d1995c5f4caaf3359721a5a58d48d` 可视化），如下所示：

```
100644 blob 4448adbf7ecd394f42ae135bbeed9676e894af85    baz.txt
040000 tree c68d233a33c5c06e0340e4c224f0afca87c8ce87    foo
```

这棵树本身包含对其内容的指针——`baz.txt`（一个 blob）和 `foo`（一棵树）。如果我们用 `git cat-file -p 4448adbf7ecd394f42ae135bbeed9676e894af85` 查看 `baz.txt` 对应哈希的内容，得到以下结果：

```
git is wonderful
```

## 引用

现在，所有快照都可以通过它们的 SHA-1 哈希来识别。但这不太方便，因为人类不擅长记忆由 40 个十六进制字符组成的字符串。

Git 解决这个问题的方式是给 SHA-1 哈希起人类可读的名字，称为 **引用**（references）。引用是指向提交的指针。与不可变的对象不同，引用是可变的——可以被更新为指向新的提交。例如，`master` 引用通常指向主开发分支的最新提交。

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

有了这个机制，Git 就可以用 "master" 这样人类可读的名字来引用历史中的某个特定快照，而不需要一长串十六进制字符串。

还有一个细节：我们通常需要一个表示"当前在历史中的什么位置"的概念，这样当我们创建新快照时，就知道它是相对于什么（即如何设置提交的 `parents` 字段）。在 Git 中，这个"当前位置"是一个称为 **HEAD** 的特殊引用。

## 仓库（Repositories）

最后，我们可以定义（大致上）什么是 Git **仓库**（repository）：它由数据 `objects` 和 `references` 组成。

在磁盘上，Git 的所有存储就是对象和引用——这就是 Git 数据模型的全部内容。所有 `git` 命令都映射为通过添加对象和添加/更新引用来操作提交 DAG 的某种行为。

每当你在输入任何命令时，想想这个命令在底层图数据结构上做了什么操作。反过来，如果你想要对提交 DAG 做出某种特定的变更，比如"丢弃未提交的更改，让 'master' 引用指向提交 `5d83f9e`"，那么大概率有一条命令可以做到（比如在这个例子中是 `git checkout master; git reset --hard 5d83f9e`）。

# 暂存区（Staging Area）

这是另一个独立于数据模型的概念，但它是创建提交接口的一部分。

你可能会想象这样实现上面描述的快照功能：提供一个"创建快照"命令，基于工作目录的 _当前状态_ 创建新快照。有些版本控制工具就是这样工作的，但 Git 不是。我们希望有干净的快照，而且从当前状态创建快照并不总是最理想的。例如，设想这样一个场景：你实现了两个独立的功能，你想创建两个独立的提交——第一个提交引入第一个功能，第二个提交引入第二个功能。或者设想这样一个场景：你的代码中到处添加了调试用的打印语句，同时还有一个 bug 修复；你希望只提交 bug 修复而丢弃所有打印语句。

Git 通过一个称为 **暂存区**（staging area）的机制来容纳这样的场景——它允许你指定哪些修改应该被包含在下一次快照中。

# Git 命令行接口

为了避免重复信息，我们不再对下面的命令做详细解释。详细信息请参考非常推荐的 [Pro Git](https://git-scm.com/book/en/v2)，或者观看课程视频。

## 基本操作

{% comment %}

The `git init` command initializes a new Git repository, with repository
metadata being stored in the `.git` directory:

```console
$ mkdir myproject
$ cd myproject
$ git init
Initialized empty Git repository in /home/missing-semester/myproject/.git/
$ git status
On branch master

No commits yet

nothing to commit (create/copy files and use "git add" to track)
```

How do we interpret this output? "No commits yet" basically means our version
history is empty. Let's fix that.

```console
$ echo "hello, git" > hello.txt
$ git add hello.txt
$ git status
On branch master

No commits yet

Changes to be committed:
  (use "git rm --cached <file>..." to unstage)

        new file:   hello.txt

$ git commit -m 'Initial commit'
[master (root-commit) 4515d17] Initial commit
 1 file changed, 1 insertion(+)
 create mode 100644 hello.txt
```

With this, we've `git add`ed a file to the staging area, and then `git
commit`ed that change, adding a simple commit message "Initial commit". If we
didn't specify a `-m` option, Git would open our text editor to allow us type a
commit message.

Now that we have a non-empty version history, we can visualize the history.
Visualizing the history as a DAG can be especially helpful in understanding the
current status of the repo and connecting it with your understanding of the Git
data model.

The `git log` command visualizes history. By default, it shows a flattened
version, which hides the graph structure. If you use a command like `git log
--all --graph --decorate`, it will show you the full version history of the
repository, visualized in graph form.

```console
$ git log --all --graph --decorate
* commit 4515d17a167bdef0a91ee7d50d75b12c9c2652aa (HEAD -> master)
  Author: Missing Semester <missing-semester@mit.edu>
  Date:   Tue Jan 21 22:18:36 2020 -0500

      Initial commit
```

This doesn't look all that graph-like, because it only contains a single node.
Let's make some more changes, author a new commit, and visualize the history
once more.

```console
$ echo "another line" >> hello.txt
$ git status
On branch master
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git checkout -- <file>..." to discard changes in working directory)

        modified:   hello.txt

no changes added to commit (use "git add" and/or "git commit -a")
$ git add hello.txt
$ git status
On branch master
Changes to be committed:
  (use "git reset HEAD <file>..." to unstage)

        modified:   hello.txt

$ git commit -m 'Add a line'
[master 35f60a8] Add a line
 1 file changed, 1 insertion(+)
```

Now, if we visualize the history again, we'll see some of the graph structure:

```
* commit 35f60a825be0106036dd2fbc7657598eb7b04c67 (HEAD -> master)
| Author: Missing Semester <missing-semester@mit.edu>
| Date:   Tue Jan 21 22:26:20 2020 -0500
|
|     Add a line
|
* commit 4515d17a167bdef0a91ee7d50d75b12c9c2652aa
  Author: Anish Athalye <me@anishathalye.com>
  Date:   Tue Jan 21 22:18:36 2020 -0500

      Initial commit
```

Also, note that it shows the current HEAD, along with the current branch
(master).

We can look at old versions using the `git checkout` command.

```console
$ git checkout 4515d17  # previous commit hash; yours will be different
Note: checking out '4515d17'.

You are in 'detached HEAD' state. You can look around, make experimental
changes and commit them, and you can discard any commits you make in this
state without impacting any branches by performing another checkout.

If you want to create a new branch to retain commits you create, you may
do so (now or later) by using -b with the checkout command again. Example:

  git checkout -b <new-branch-name>

HEAD is now at 4515d17 Initial commit
$ cat hello.txt
hello, git
$ git checkout master
Previous HEAD position was 4515d17 Initial commit
Switched to branch 'master'
$ cat hello.txt
hello, git
another line
```

Git can show you how files have evolved (differences, or diffs) using the `git
diff` command:

```console
$ git diff 4515d17 hello.txt
diff --git c/hello.txt w/hello.txt
index 94bab17..f0013b2 100644
--- c/hello.txt
+++ w/hello.txt
@@ -1 +1,2 @@
 hello, git
 +another line
```

{% endcomment %}

- `git help <command>`：获取 Git 命令的帮助
- `git init`：创建一个新的 Git 仓库，数据存储于 `.git` 目录中
- `git status`：告诉你当前发生了什么
- `git add <filename>`：将文件添加到暂存区
- `git commit`：创建一个新的提交
    - 请撰写[好的提交信息](https://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html)！
    - 撰写[好的提交信息](https://chris.beams.io/posts/git-commit/)的更多理由！
- `git log`：显示扁平化的历史记录
- `git log --all --graph --decorate`：将历史可视化为 DAG
- `git diff <filename>`：展示你相对于暂存区所做的更改
- `git diff <revision> <filename>`：展示文件在两个快照之间的差异
- `git checkout <revision>`：更新 HEAD（如果检出的是分支，则同时更新当前分支）

## 分支与合并

{% comment %}

Branching allows you to "fork" version history. It can be helpful for working
on independent features or bug fixes in parallel. The `git branch` command can
be used to create new branches; `git checkout -b <branch name>` creates and
checks out a new branch.

Merging is the opposite of branching: it allows you to combine forked version
histories, e.g. merging a feature branch back into master. The `git merge`
command is used for merging.

{% endcomment %}

- `git branch`：显示分支
- `git branch <name>`：创建一个分支
- `git checkout -b <name>`：创建一个分支并切换到它
    - 等同于 `git branch <name>; git checkout <name>`
- `git merge <revision>`：合并到当前分支
- `git mergetool`：使用更强大的工具来帮助解决合并冲突
- `git rebase`：将一组补丁重新变基（rebase）到新的基础上

## 远程仓库（Remotes）

- `git remote`：列出远程仓库
- `git remote add <name> <url>`：添加一个远程仓库
- `git push <remote> <local branch>:<remote branch>`：将对象发送到远程仓库，并更新远程引用
- `git branch --set-upstream-to=<remote>/<remote branch>`：建立本地分支与远程分支之间的对应关系
- `git fetch`：从远程仓库检索对象/引用
- `git pull`：等同于 `git fetch; git merge`
- `git clone`：从远程仓库下载仓库

## 撤销（Undo）

- `git commit --amend`：编辑某个提交的内容/信息
- `git reset HEAD <file>`：从暂存区撤销一个文件
- `git checkout -- <file>`：丢弃更改

# 高级 Git

- `git config`：Git 是[高度可定制的](https://git-scm.com/docs/git-config)
- `git clone --depth=1`：浅克隆，不包含完整的版本历史
- `git add -p`：交互式暂存
- `git rebase -i`：交互式变基
- `git blame`：显示每一行最后是由谁编辑的
- `git stash`：临时移除工作目录的修改
- `git bisect`：二分搜索历史（例如用于定位回归问题）
- `.gitignore`：[指定](https://git-scm.com/docs/gitignore)有意不追踪的文件以忽略

# 杂项

- **图形界面（GUIs）**：Git 有很多[图形界面客户端](https://git-scm.com/downloads/guis)。我们个人不使用它们，而是使用命令行接口。
- **Shell 集成**：在 Shell 提示符中显示 Git 状态非常方便（[zsh](https://github.com/olivierverdier/zsh-git-prompt)、[bash](https://github.com/magicmonty/bash-git-prompt)）。通常会包含在 [Oh My Zsh](https://github.com/ohmyzsh/ohmyzsh) 等框架中。
- **编辑器集成**：与上述类似，许多编辑器都有便捷集成。对于 Vim 而言，标准选择是 [fugitive.vim](https://github.com/tpope/vim-fugitive)。
- **工作流**：我们教了你数据模型和一些基本命令；但没有告诉你在大项目上应该遵循什么实践（并且存在[许多](https://nvie.com/posts/a-successful-git-branching-model/)[不同的](https://www.endoflineblog.com/gitflow-considered-harmful)[方法](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow)）。
- **GitHub**：Git 不等于 GitHub。GitHub 有一种向其他项目贡献代码的特定方式，称为 [Pull Request](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/about-pull-requests)。
- **其他 Git 托管平台**：GitHub 并非不可替代：还有许多 Git 仓库托管平台，如 [GitLab](https://about.gitlab.com/) 和 [BitBucket](https://bitbucket.org/)。

# 资源

- [Pro Git](https://git-scm.com/book/en/v2) 是**强烈推荐阅读的书籍**。在理解了数据模型之后，阅读第 1 至第 5 章应该就能教会你高效使用 Git 所需的大部分知识。后面的章节还有一些有趣的进阶内容。
- [Oh Shit, Git!?!](https://ohshitgit.com/) 是一份简短指南，教你如何从一些常见的 Git 错误中恢复。
- [Git for Computer Scientists](https://eagain.net/articles/git-for-computer-scientists/) 是对 Git 数据模型的简短解释，比这些讲义的伪代码更少、图表更丰富。
- [Git from the Bottom Up](https://jwiegley.github.io/git-from-the-bottom-up/) 是对 Git 在数据模型之外实现细节的详细解释，适合好奇的读者。
- [How to explain git in simple words](https://smusamashah.github.io/blog/2017/10/14/explain-git-in-simple-words)
- [Learn Git Branching](https://learngitbranching.js.org/) 是一款浏览器端的游戏，教你学习 Git。

# 练习

1. 如果你没有使用 Git 的经验，可以尝试阅读 [Pro Git](https://git-scm.com/book/en/v2) 的前几章，或者使用 [Learn Git Branching](https://learngitbranching.js.org/) 之类的教程。在练习过程中，将 Git 命令与数据模型联系起来。
1. 克隆[课程网站的仓库](https://github.com/missing-semester/missing-semester)。
    1. 以图形方式可视化版本历史，探索它的结构。
    1. 最后一个修改 `README.md` 的人是谁？（提示：使用带有参数的 `git log`）。
    1. 最后一次修改 `_config.yml` 的 `collections:` 行时，关联的提交信息是什么？（提示：使用 `git blame` 和 `git show`）。
1. 学习 Git 时的一个常见错误是提交不应该由 Git 管理的大文件，或者提交敏感信息。试着向仓库中添加一个文件，进行一些提交，然后从历史中删除这个文件（你可能想看看[这篇指南](https://help.github.com/articles/removing-sensitive-data-from-a-repository/)）。
1. 从 GitHub 克隆某个仓库，并修改它的一个已有文件。执行 `git stash` 会发生什么？运行 `git log --all --oneline` 你会看到什么？运行 `git stash pop` 来撤销 `git stash` 所做的操作。在什么场景下这可能有用？
1. 和许多命令行工具一样，Git 提供了一个称为 `~/.gitconfig` 的配置文件（dotfile）。在 `~/.gitconfig` 中创建一个别名，使得当你运行 `git graph` 时，得到的输出等同于 `git log --all --graph --decorate --oneline`。你可以直接[编辑](https://git-scm.com/docs/git-config#Documentation/git-config.txt-alias) `~/.gitconfig` 文件，也可以使用 `git config` 命令来添加别名。关于 Git 别名的更多信息可以在[这里](https://git-scm.com/book/en/v2/Git-Basics-Git-Aliases)找到。
1. 在运行 `git config --global core.excludesfile ~/.gitignore_global` 之后，你可以在 `~/.gitignore_global` 中定义全局忽略模式。这设置了 Git 将使用的全局忽略文件的位置，但你仍然需要手动在该路径创建文件。配置你的全局 gitignore 文件以忽略操作系统或编辑器特定的临时文件，比如 `.DS_Store`。
1. Fork [课程网站的仓库](https://github.com/missing-semester/missing-semester)，找到一个你可以修正的拼写错误或其他改进之处，然后在 GitHub 上提交一个 Pull Request（你可能想看看[这里](https://github.com/firstcontributions/first-contributions)）。请只提交有用的 PR（请不要刷屏！）。如果你找不到可以改进的地方，可以跳过这个练习。