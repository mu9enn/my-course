---
layout: lecture
title: "版本控制"
presenter: Jon
date: 2019-01-22
order: 2
video:
  aspect: 56.25
  id: 3fig2Vz8QXs
---

当你在一件事上工作，而这件事随时间不断变化时，能够_追踪_这些变化就会非常有用。这可能有多种原因：它为你保留了一份"谁改了什么、怎么改的、为什么改"的记录，也方便你随时回退。版本控制系统（VCS, Version Control System）就是干这个的。它允许你_提交_（commit）一组文件的变更，并附上一条描述变更信息的说明，同时也支持查看和回退你过去所做的任何更改。

大多数 VCS 都支持在多个用户之间共享提交历史。这使得协作变得非常方便：你能看到别人做了什么更改，别人也能看到你的更改。而且由于 VCS 追踪的是_变更_本身（而非文件快照），只要各人的改动触及的是相对不重叠的部分，它通常能够（尽管不是每次都一定能）自动将不同人的更改合并到一起。

市面上有[很多](https://en.wikipedia.org/wiki/Comparison_of_version-control-software)种 VCS，它们在支持的用途、运作方式和交互方式上差异巨大。这里我们将聚焦于最常用的一款——[git](https://git-scm.com/)，但同时也建议你去了解一下 [Mercurial](https://www.mercurial-scm.org/)。

好了，废话不多说，直接上干货。

## 难道 git 是什么黑暗魔法？

并不完全是。你需要理解它的_数据模型_。我们会略过一些细节，但粗略地说，git 里最_核心_的概念是_提交_（commit）。

 - 每个提交都有一个唯一的名称，叫作"修订哈希"（revision hash）——一个类似 `998622294a6c520db718867354bf98348ae3c7e2` 的长哈希值，通常简写为一段（近似唯一的）前缀：`9986222`
 - 提交里包含作者信息和提交消息
 - 还包含其所有_祖先提交_的哈希——通常就是前一个提交的哈希
 - 提交同时也代表了从一个_差异_（diff）：即从提交的祖先状态到达当前状态的变更记录（例如"在这个文件的这一行删除、在这一行添加、将该文件重命名"等）
   - 实际上，git 存储的是完整的_前后状态_
   - 所以不建议在 git 里管理那些经常变更的大文件

一开始，_仓库_（repository）（大致来说就是 git 所管理的文件夹）里面没有任何内容，也没有任何提交。我们来做一下初始化：

```console
$ git init hackers
$ cd hackers
$ git status
```

这里的输出实际上给了我们一个很好的起点。我们逐行来分析，确保理解每一处含义。

首先，"On branch master"（当前在 master 分支上）。

 - 我们当然不想每次都手动输入一长串哈希值。
 - _分支_（branches）就是指向某个哈希值的_名字_。
 - 传统上，`master` 这个名称用来指向"最新"的提交。每当有一个新的提交，`master` 这个名字就会被更新为指向那个新提交的哈希。
 - 特殊名称 `HEAD` 指代"当前"分支
 - 你也可以通过 `git branch`（或 `git tag`）创建自己的名字，后面会讲到

我们直接跳过"No commits yet"（还没有提交）——这句话的字面意思已经说得很清楚了。

然后是"nothing to commit"（没有要提交的变更）。

 - 每个提交都包含一组变更的差异（diff）。那这些差异最初是怎么构造出来的呢？
 - _可以_直接把你自上次提交以来所做的_全部_变更一次性提交
   - 但有时候你只想提交其中的一部分（例如不想把 `TODO` 也提交）
   - 有时候你希望把一个大改动拆成多个提交，给每个提交分别写一条消息
 - git 让你通过_暂存区_（staging area）来构造提交
   - 用 `git add` 将某个文件（或文件集合）中的变更加入到暂存区
     - 用 `git add -p` 只暂存文件中的部分变更
     - 不传参数时，`git add` 作用于所有已知的文件
   - 用 `git rm` 删除某个文件并将删除操作加入暂存区
   - 用 `git reset` 清空暂存区的变更集合
     - 注意：这_不会_修改你任何文件中的内容
     - 它只是意味着后续不会有变更被纳入提交
     - 要移除某些特定的暂存变更：`git reset FILE` 或 `git reset -p`
   - 用 `git diff --staged` 查看暂存区的变更
   - 用 `git diff` 查看尚未暂存的剩余变更
   - 当你对暂存的内容满意之后，用 `git commit` 创建提交
     - 如果你想提交_所有_变更：`git commit -a`
     - 更多信息请参阅 `git help add`

当你尝试以上这些操作时，不妨多跑跑 `git status` 看看 git 认为你当前在做什么——它的提示往往非常有用！

## 提交，说的是什么？

好的，我们有了一个提交，接下来呢？

 - 我们可以查看最近的变更：`git log`（或 `git log --oneline`）
 - 查看完整的变更内容：`git log -p`
 - 显示某个特定的提交：`git show master`
   - 加上 `-p` 可以显示完整差异/补丁
 - 使用 `git checkout NAME` 回到某个提交时的状态
   - 如果 `NAME` 是一个提交的哈希，git 会告诉你处于"detached"（分离）状态。这仅仅意味着没有一个_名字_指向这个提交，所以如果你在此状态下创建新提交，没有人（没有其他名字）能"看到"它们。
 - 使用 `git revert NAME` 撤销某个变更
   - 把 `NAME` 所指提交中的差异_反向_应用一遍
 - 使用 `git diff NAME..` 将旧版本与当前版本进行比较
   - `a..b` 是一个提交_范围_。如果省略任一边，则默认为 `HEAD`
 - 使用 `git log NAME..` 显示两个提交之间的所有提交记录
   - 同样支持 `-p`
 - 可以使用 `git reset NAME` 将 `master` 指向一个特定的提交（效果上等同于回退到那个提交）
   - 咦，`reset` 不是用来修改暂存区的吗？
     它其实有两种用法（详见 `git help reset`），其中一种就是：将 `HEAD` 设置为给定名字所指向的提交
   - 注意：这不会修改任何文件——`git diff` 现在的效果等同于 `git diff NAME..`

## 名字的学问

显然，_名字_在 git 里很重要，而且它们正是理解 git_大量_行为的关键。到目前为止，我们已经聊过提交哈希、`master` 和 `HEAD`。但还有更多！

 - 你可以用 `git branch b` 创建自己的分支（就像 `master` 一样）
   - 这会创建一个新名字 `b`，指向 `HEAD` 当前所在的提交
   - 但你仍然"在" master 上，所以如果你此时创建新提交，只有 `master` 会指向它，`b` 不会
   - 用 `git checkout b` 切换到那个分支
     - 之后你创建的所有提交都会更新 `b` 这个名字
     - 用 `git checkout master` 切回 master
       - 你在 `b` 中做的所有更改都"隐藏"起来了
     - 这是一个非常方便的功能，可以轻松地测试不同改动
 - _标签_（tags）是另一种类型的名字，它们_永远不会_改变，并且有自己独立的提交消息。通常用来标记发布版本和更新日志
 - `NAME^` 表示"`NAME` 之前的那个提交"
   - 可以递归使用：`NAME^^^`
   - 你_很可能_在用到 `~` 时实际想要的是 `~` 所代表的含义
     - `~` 表示_时间上_的上一代，而 `^` 沿祖先链回溯
     - `~~` 等价于 `^^`
     - 用 `~` 你还可以写 `X~3` 表示"`X` 之上第 3 代提交"
     - 你不应该使用 `^3`
   - `git diff HEAD^`
 - `-` 表示"上一个名字"
 - 大多数命令默认操作的是 `HEAD`，除非你传入其他参数

## 收拾烂摊子

你的提交历史_非常_容易变成下面这样：

 - `add feature x` —— 可能还会附带一段关于 `x` 的提交说明！
 - `forgot to add file`
 - `fix bug`
 - `typo`
 - `typo2`
 - `actually fix`
 - `actually actually fix`
 - `tests pass`
 - `fix example code`
 - `typo`
 - `x`
 - `x`
 - `x`
 - `x`

git 对此_完全不在乎_，但对你未来的自己，或那些好奇"到底改了哪些东西"的其他人来说，这就很不友好了。git 允许你清理这些混乱：

 - `git commit --amend`：把暂存区的变更合入上一次提交
   - 注意：这会_修改_上一个提交，给它一个新的哈希！
 - `git rebase -i HEAD~13` 是_魔法_操作。
   对过去 13 次提交中的每一次，选择要做的事情：
   - 默认是 `pick`：不做任何更改
   - `r`：修改提交消息
   - `e`：修改提交内容（添加或删除文件）
   - `s`：将当前提交_变基_（squash）到上一个提交，并编辑提交消息
   - `f`："fixup"——将当前提交合入上一个提交；丢弃当前提交的消息
   - 最后，`HEAD` 会被重新指向新的最后一个提交
   - 这个过程通常被称作_压缩_（squashing）提交
   - 它真正做的事情是：把 `HEAD` 回退到 rebase 起点，然后按指示依次重新应用各提交
 - `git reset --hard NAME`：将所有文件的状态重置为 `NAME` 所指的状态（如果没有给出名字则默认为 `HEAD`）。这是撤销变更的利器。

## 与他人协作

版本控制的一个常见用例是让多个人能够同时修改同一组文件，而不互相踩踏对方的工作。或者更准确地说：确保_如果_他们踩到了一起，变更也不会无声无息地互相覆盖。

git 是一个_分布式_（distributed）的 VCS：每个人都拥有整个仓库的一份本地拷贝（更准确地说，是所有别人选择公开的变更）。有些 VCS 是_集中式_（centralized）的（例如 Subversion）：服务器保管所有提交，客户端只拥有它们"检出"（checked out）的文件。基本上，它们只拥有_当前_的文件，需要什么东西时得向服务器请求。

git 仓库的每一个副本都可以列为一个"远程"（remote）。你可以使用 `git clone ADDRESS`（而不是 `git init`）来复制一个已有的 git 仓库。这会在本地创建一个名为 _origin_ 的远程，指向 `ADDRESS`。你可以通过 `git fetch REMOTE` 从一个远程获取名称及其指向的提交。远程上的所有名称都以 `REMOTE/NAME` 的形式对你可用，你可以像使用本地名字一样使用它们。

如果你对某个远程有写入权限，你可以使用 `git push` 来修改远程上的名字，让它们指向你创建的提交。例如，让远程 `origin` 上的 `master` 名称（分支）指向我们当前 master 分支所指向的提交：

   - `git push origin master:master`
   - 为方便起见，你可以用 `-u` 设置当从当前分支执行 `git push` 时默认的推送目标
   - 考虑一下：这条命令会有什么效果？`git push origin master:HEAD^`

你通常会使用 GitHub、GitLab、BitBucket 或其他服务作为你的远程。在 git 看来，这些服务并没有任何"特殊"之处。它们不过是一堆名字和提交而已。如果有人在 master 上做了更改，并将 `github/master` 更新为指向他们的提交（我们稍后会回到这一点），那么当你执行 `git fetch github` 时，你就可以通过 `git log github/master` 看到他们的更改。

## 与他人的工作合流

到目前为止，分支看起来似乎没什么用：你可以创建它们、在上面工作，然后呢？最终你不还是需要把 `master` 指向它们吗？

 - 如果你正在做一个大功能的同时需要修复一个 bug 怎么办？
 - 如果在此期间其他人对 master 做了更改怎么办？

不可避免地，你都需要把一条分支上的变更与另一条分支上的变更_合并_（merge）到一起，不管这些变更是你自己做的还是别人做的。git 通过 `git merge NAME` 来做到这一点，`merge` 会：

 - 找到 `HEAD` 和 `NAME` 上一次共享的祖先提交（即它们分歧的地方）
 - （尝试）将所有那些变更应用到当前 `HEAD`
 - 产生一个新的提交，其中包含所有变更，并将 `HEAD` 和 `NAME` 都列为其祖先
 - 将 `HEAD` 设置为该提交的哈希

当你的大功能完成后，你可以将该分支合并到 master，git 会确保你不会丢失任何一个分支上的变更！

如果你以前使用过 git，你可能会用另一个名字认出 `merge`：`pull`。当你执行 `git pull REMOTE BRANCH` 时，实际上是：

 - `git fetch REMOTE`
 - `git merge REMOTE/BRANCH`
 - 和 `push` 一样，`REMOTE` 和 `BRANCH` 经常被省略，此时会使用该分支的"跟踪"远程分支（还记得 `-u` 的作用吗？）

在大多数情况下这工作得_非常好_——只要被合并的分支之间的变更是不重叠的。如果不是，你就会遇到_合并冲突_（merge conflict）。听起来吓人……

 - 合并冲突只是 git 在告诉你它不知道最终的差异（diff）应该长什么样
 - git 暂停执行，请你来完成"合并提交"的暂存
 - 在你的编辑器中打开冲突的文件，你会看到一大堆尖括号（`<<<<<<<`）。`=======` 之上的部分是自共享祖先提交以来在 `HEAD` 中所做的更改；`=======` 之下是 `NAME` 中所做的更改
 - `git mergetool` 非常好用——它会打开一个差异编辑器
 - 当你_解决_（resolve）了冲突、确定了文件最终的样貌之后，用 `git add` 将这些更改暂存
 - 所有冲突解决完毕后，用 `git commit` 完成提交
   - 如果不想继续了，可以用 `git merge --abort` 放弃

恭喜你解决了人生中第一次 git 合并冲突！\o/ 现在你可以通过 `git push` 发布你的完成更改了。

## 当两个世界碰撞

当你执行 `push` 时，git 会检查如果你更新了要推送到的远程名字，是否会有其他人的工作丢失。它是这样做的：检查远程名字当前指向的提交是否是你正在推送的提交的_祖先_。如果是的话，git 可以安全地直接更新这个名字；这被称为_快进_（fast-forward）。如果不是，git 会拒绝更新远程名字，并告诉你有冲突的更改。

如果你的 push 被拒绝了，该怎么办？

 - 用 `git pull`（即 `fetch` + `merge`）合并远程变更
 - 用 `--force` 强制推送：这会丢失其他人的更改！
   - 还有 `--force-with-lease`，它只会在远程名字自上次从此远程 fetch 以来_没有变化_时才强制推送。安全得多！
   - 如果你 rebase 了那些之前已经推送过的本地提交（"历史改写"；大概率不要这么做），你就必须强制推送。想想为什么！
 - 尝试将你的更改_重新应用_到远程变更的_上方_
   - 这就是一个 `rebase`（变基）操作！
     - 从共享祖先开始回退所有本地提交
     - 将 `HEAD` 快进到远程名字处的提交
     - 按顺序重新应用本地提交
       - 可能会有你需要手动解决的冲突
       - 使用 `git rebase --continue` 或 `--abort`
     - [更多内容](https://git-scm.com/book/en/v2/Git-Branching-Rebasing)
   - `git pull --rebase` 可以帮你启动这个过程
   - 到底该 merge 还是 rebase 是个热门话题！以下是一些有用的阅读：
     - [这篇](https://www.atlassian.com/git/tutorials/merging-vs-rebasing)
     - [这篇](https://web.archive.org/web/20210106220723/https://derekgourlay.com/blog/git-when-to-merge-vs-when-to-rebase/)
     - [这篇](https://stackoverflow.com/questions/804115/when-do-you-use-git-rebase-instead-of-git-merge)

# 延伸阅读

[![XKCD 上的 git 漫画](https://imgs.xkcd.com/comics/git.png)](https://xkcd.com/1597/)

 - [Learn git branching](https://learngitbranching.js.org/)
 - [How to explain git in simple words](https://smusamashah.github.io/blog/2017/10/14/explain-git-in-simple-words)
 - [Git from the bottom up](https://jwiegley.github.io/git-from-the-bottom-up/)
 - [Git for computer scientists](https://eagain.net/articles/git-for-computer-scientists/)
 - [Oh shit, git!](https://ohshitgit.com/)
 - [The Pro Git book](https://git-scm.com/book/en/v2)

# 练习

1. 在一个仓库里尝试修改一个已有的文件。执行 `git stash` 后会发生什么？运行 `git log --all --oneline` 会看到什么？执行 `git stash pop` 撤销 `git stash` 所做的更改。在什么场景下这可能有用？

1. 学习 git 时的一个常见错误是把不应该由 git 管理的大文件或包含敏感信息的文件提交上去。尝试把一个文件添加到一个仓库中，做一些提交，然后把该文件从历史记录中删除（你可以查看[这个页面](https://help.github.com/articles/removing-sensitive-data-from-a-repository/)了解方法）。另外，如果你确实希望 git 帮助你管理大文件，可以了解一下 [Git-LFS](https://git-lfs.github.com/)。

1. git 在撤销变更方面非常方便，但人们还需要熟悉各种不太常见的操作方法：
   1. 如果某个文件在某个提交中被错误地修改了，可以用 `git revert` 来恢复。但如果一个提交涉及多项变更，`revert` 可能并不是最佳选择。我们该如何使用 `git checkout` 来恢复某个特定提交中的文件版本？
   1. 创建一个分支，在该分支上做一个提交，然后删除它。你是否还能恢复那个提交？试试看看 `git reflog`。（提示：尽快恢复悬空（dangling）对象，git 会定期自动清理那些没有任何名字指向的提交。）
   1. 如果对 `git reset --hard` 的使用太过激进而误用了它而非 `git reset`，变更就可能会丢失。但既然那些变更曾经已经被暂存过，我们仍然可以恢复它们。（查看 `git fsck --lost-found` 和 `.git/lost-found`）

1. 在任何 git 仓库中查看 `.git/hooks` 文件夹，你会找到一堆以 `.sample` 结尾的脚本。如果你把它们重命名去掉 `.sample` 后缀，它们就会根据名称被触发执行。例如 `pre-commit` 会在执行提交之前运行。自己来试验一下。

1. 与许多命令行工具一样，`git` 提供了一个配置文件（也叫 dotfile）叫 `~/.gitconfig`。在 `~/.gitconfig` 中创建一个别名，使得当你运行 `git graph` 时得到 `git log --oneline --decorate --all --graph` 的输出（这是一个快速可视化提交图的优秀命令）。

1. git 还允许你在 `~/.gitignore_global` 下定义全局忽略模式，这可以用来防止常见错误，比如不小心添加 RSA 密钥。创建一个 `~/.gitignore_global` 文件，添加模式 `*rsa`，然后在某个仓库中测试它是否生效。

1. 当你开始对 `git` 更加熟悉之后，你会发现一些常见任务（比如编辑 `.gitignore`）很常用。[git extras](https://github.com/tj/git-extras/blob/master/Commands.md) 提供了一系列与 git 集成的实用小工具。例如 `git ignore PATTERN` 会把指定的模式添加到你的仓库中的 `.gitignore` 文件里，而 `git ignore-io LANGUAGE` 则能从 [gitignore.io](https://www.gitignore.io) 获取该语言常见的忽略模式。安装 `git extras` 并试着使用一些工具，比如 `git alias` 或 `git ignore`。

1. Git 的 GUI 程序有时是个很好的资源。尝试在一个 git 仓库中运行 [gitk](https://git-scm.com/docs/gitk)，探索其界面的不同部分。然后执行 `gitk --all`，看看有什么不一样？

1. 当你已经习惯了命令行应用之后，GUI 工具可能会显得笨重/臃肿。命令行工具与 GUI 之间的一个不错的折中方案是基于 ncurses 的工具——它们可以在命令行中导航，同时仍然提供交互式界面。git 有 [tig](https://github.com/jonas/tig)，试着安装并在某个仓库中运行它。你可以在[这里](https://www.atlassian.com/blog/git/git-tig)找到一些使用示例。

{% comment %}

 - forced push + `--force-with-lease`
 - git merge/rebase --abort
 - git blame
 - exercise about why rebasing public commits is bad

{% endcomment %}