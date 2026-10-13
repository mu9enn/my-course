---
layout: lecture
title: "操作系统定制"
presenter: Anish
date: 2019-01-29
order: 3
video:
  aspect: 62.5
  id: epSRVqQzeDo
special: true
---

除了图形化设置菜单提供的选项之外，你还可以通过多种方式对操作系统进行深度定制。

# 键盘重映射

你的键盘上很可能有一些按键你并不常用。与其让它们闲置，不如把它们重新映射为更有用的功能。

## 映射到其他按键

最简单的情形是把一个键重新映射为另一个键。比如，如果你很少使用 **大写锁定键（Caps Lock）**，就可以把它重新映射为一个更常用的功能。以 Vim 用户为例，你可能想把 Caps Lock 映射为 **退出键（Escape）**。

在 macOS 上，你可以通过「系统偏好设置」→「键盘」做一部分重映射；如果要实现更复杂的映射关系，则需要借助专门的软件工具。

## 映射到任意命令

你并不局限于把键映射到其他键——有些工具允许你将按键（或按键组合）映射为任意命令。例如，你可以把 `Command`+`Shift`+`T` 设置为打开一个新终端窗口。

# 自定义隐藏的操作系统设置

## macOS

macOS 通过 `defaults` 命令暴露了大量有用的系统设置。例如，你可以让隐藏应用的 **Dock** 图标显示为半透明：

```shell
defaults write com.apple.dock showhidden -bool true
```

并不存在一份能涵盖所有可能设置的完整清单，但你可以在线找到各类具体定制列表，比如 Mathias Bynens 的
[.macos](https://github.com/mathiasbynens/dotfiles/blob/master/.macos)。

# 窗口管理

## 平铺式窗口管理

[平铺式窗口管理（Tiling window management）](https://en.wikipedia.org/wiki/Tiling_window_manager) 是一种窗口管理方式——它把窗口组织为互不重叠的矩形区域。如果你使用的是基于 Linux 的操作系统，可以直接安装一个 **平铺式窗口管理器（tiling window manager）**；如果你用的是 Windows 或 macOS，则可以安装一些辅助应用来近似实现这种效果。

## 屏幕管理

你可以设置键盘快捷键来跨屏幕操作窗口，比如把窗口快速移动到另一块显示器上。

## 布局脚本

如果你有固定的窗口排列习惯（比如左侧终端、右侧编辑器），与其每次都手动拖拽摆放，不如把这些布局写成脚本。这样，调用一次脚本即可瞬间恢复整套布局。

# 资源

- [Hammerspoon](https://www.hammerspoon.org/) — macOS 桌面自动化工具
- [Rectangle](https://rectangleapp.com/) — macOS 窗口管理器
- [Karabiner](https://karabiner-elements.pqrs.org/) — 功能丰富的 macOS 键盘重映射工具
- [r/unixporn](https://www.reddit.com/r/unixporn/) — 社区用户分享的精美桌面配置截图与文档

# 练习

1. 找出如何将 Caps Lock 键重新映射为你更常用的按键（例如 Escape、Ctrl 或 Backspace）。

2. 设置一个全局键盘快捷键，用于打开一个新的终端窗口或一个新的浏览器窗口。

{% comment %}

TODO

- Bitbar / Polybar
- Clipboard Manager (stack/searchable history)

{% endcomment %}