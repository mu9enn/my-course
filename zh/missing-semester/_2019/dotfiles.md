---
layout: lecture
title: "点配置文件"
presenter: Anish
date: 2019-01-24
order: 1
video:
  aspect: 62.5
  id: YSZBWWJw3mI
---

许多程序使用纯文本文件来配置，这些文件被称为「点配置文件」（dotfile，因为文件名以 `.` 开头，例如 `~/.gitconfig`），在 `ls` 默认列目录时被隐藏。

你使用的许多工具可能都拥有大量可以精细调节的设置。通常，这些工具使用专门的配置语言来进行定制，例如 Vim 使用 Vimscript，shell 则使用自身的脚本语言。

将工具按照你的习惯进行定制和适配，可以显著提升你的效率。我们建议你亲自花时间配置自己的工具，而不只是从 GitHub 上 clone 别人的点配置文件。

你可能已经有一些点配置文件了。以下是一些常见的位置：

- `~/.bashrc`
- `~/.emacs`
- `~/.vim`
- `~/.gitconfig`

有些程序不会把配置文件直接放在主目录下，而是放在 `~/.config` 下的某个子文件夹中。

点配置文件并非命令行程序所独有——例如 [MPV](https://mpv.io/) 视频播放器也可以通过编辑 `~/.config/mpv` 下的文件来配置。

# 学会定制工具

你可以通过阅读在线文档或[手册页（man pages）](https://en.wikipedia.org/wiki/Man_page)来了解工具的各类配置。另一个不错的方法是搜索关于特定程序的博客文章，作者们通常会在文中分享自己的定制方案。还有一种方式是浏览其他人的点配置文件——你可以在 GitHub 上找到大量的[点配置文件仓库](https://github.com/search?o=desc&q=dotfiles&s=stars&type=Repositories)——例如人气最高的[这一个](https://github.com/mathiasbynens/dotfiles)（但我们不建议你照搬别人的配置）。

# 组织结构

你该如何组织自己的点配置文件？它们应该放在一个独立文件夹中，置于[版本控制](/2019/version-control/)下，并通过脚本使用**符号链接**（symlink）将其链接到正确的位置。这样做的好处包括：

- **安装便捷**：如果你在一台新机器上登录，只需几分钟就能完成自定义配置的安装
- **可移植**：你的工具在不同机器上的行为保持一致
- **同步更新**：你可以在任何一处更新点配置文件，并将所有机器的配置保持同步
- **变更追踪**：你可能会在整个编程生涯中一直维护这些点配置文件，版本历史对于长周期项目来说非常有用

```shell
cd ~/src
mkdir dotfiles
cd dotfiles
git init
touch bashrc
# create a bashrc with some settings, e.g.:
#     PS1='\w > '
touch install
chmod +x install
# insert the following into the install script:
#     #!/usr/bin/env bash
#     BASEDIR=$(dirname $0)
#     cd $BASEDIR
#
#     ln -s ${PWD}/bashrc ~/.bashrc
git add bashrc install
git commit -m 'Initial commit'
```

# 进阶话题

## 针对特定机器的配置

大多数时候，你在不同机器上的配置是相同的，但有时你希望在某台特定机器上做一些微调。以下是几种处理方式：

### 每台机器一个分支

使用版本控制为每台机器维护一个独立分支。这种方法在逻辑上直观明了，但可能显得比较笨重。

### 条件判断

如果配置文件本身支持，可以使用类似条件判断的结构来应用特定于某台机器的配置。例如，你的 shell 可以写成这样：

```shell
if [[ "$(uname)" == "Linux" ]]; then {do_something else}; fi

# Darwin 是 macOS 系统的架构名称
if [[ "$(uname)" == "Darwin" ]]; then {do_something}; fi

# 也可以针对特定主机名
if [[ "$(hostname)" == "myServer" ]]; then {do_something}; fi
```

### 包含文件（Includes）

如果配置文件支持包含机制，可以利用它来引入额外的配置。例如，`~/.gitconfig` 可以包含如下设置：

```
[include]
    path = ~/.gitconfig_local
```

然后在每台机器上，`~/.gitconfig_local` 可以包含该机器特有的设置。你甚至可以将这些设置放在一个独立的仓库中进行管理。

这种包含方式也同样适用于让不同的程序共享一部分配置。例如，如果你希望 `bash` 和 `zsh` 共享同一组别名（aliases），可以把它们统一写在 `.aliases` 文件中，然后在两个配置文件中都加入以下代码块：

```bash
# Test if ~/.aliases exists and source it
if [ -f ~/.aliases ]; then
    source ~/.aliases
fi
```

# 参考资料

- 讲师们的点配置文件：
  [Anish](https://github.com/anishathalye/dotfiles)、
  [Jon](https://github.com/jonhoo/configs)、
  [Jose](https://github.com/jjgo/dotfiles)
- [GitHub does dotfiles](https://dotfiles.github.io/)：点配置文件框架、工具、示例和教程
- [Shell 启动脚本](https://web.archive.org/web/20260329133158/https://blog.flowblok.id.au/2013-02/shell-startup-scripts.html)：详解 shell 所使用的各类配置文件

# 练习

1. 为你的点配置文件创建一个文件夹，并设置[版本控制](/2019/version-control/)。

2. 为至少一个程序添加配置，例如你的 shell，并加入一些自定义设置（起步阶段可以简单到只是通过设置 `$PS1` 来定制你的 shell 提示符）。

3. 搭建一种快速、免手动操作的方式在新机器上安装你的点配置文件。这可以只是一个调用了 `ln -s` 为每个文件创建符号链接的 shell 脚本，你也可以使用[专门的工具](https://dotfiles.github.io/utilities/)。

4. 在一台全新的虚拟机上测试你的安装脚本。

5. 将当前所有的工具配置迁移到你的点配置文件仓库中。

6. 将你的点配置文件发布到 GitHub。