---
layout: lecture
title: "自动化"
presenter: Jose
date: 2019-01-24
order: 3
video:
  aspect: 56.25
  id: BaLlAaHz-1k
special: true
---

有时你写了一个脚本来完成某项任务，但希望它定期运行——例如一个备份任务。当然你也可以自己写一个后台守护进程，周期性地醒过来执行任务。不过，大多数 UNIX 系统自带 cron 守护进程（crond），它可以根据简单的规则以最短到一分钟的间隔来运行任务。

在大多数 UNIX 系统上，cron 守护进程 `crond` 默认就是运行着的，你也可以通过 `ps aux | grep crond` 来确认。

## 定时表（crontab）

可以用 `crontab -l` 查看定时表配置，用 `crontab -e` 编辑它。cron 使用五个以空格分隔的字段，加上用户名和命令，格式如下：

- **minute**（分钟）—— 命令在一小时内第几分钟执行，取值范围是 `0` 到 `59`。
- **hour**（小时）—— 命令在几点钟执行，采用 24 小时制，取值范围是 `0` 到 `23`（`0` 即午夜）。
- **dom**（Day of Month，每月的第几天）—— 指定在每月的哪一天执行。例如要让命令在每月 19 日执行，这里就填 `19`。
- **month**（月份）—— 命令在哪个月份执行，可以填数字（`0`–`12`），也可以填月份名称（例如 `May`）。
- **dow**（Day of Week，每周的第几天）—— 命令在哪天执行，可以填数字（`0`–`7`，`0` 和 `7` 都表示周日），也可以填星期名称（例如 `sun`）。
- **user**（用户）—— 以哪个用户的身份运行命令。
- **command**（命令）—— 要执行的命令。这个字段中可以包含多个单词或用空格分隔的内容。

其中，星号 `*` 表示"所有值"，而星号后跟斜杠和数字表示"每第 n 个值"。例如 `*/5` 就是"每 5 个"。下面是一些常用示例：

```shell
*/5   *    *   *   *       # Every five minutes
  0   *    *   *   *       # Every hour at o'clock
  0   9    *   *   *       # Every day at 9:00 am
  0   9-17 *   *   *       # Every hour between 9:00am and 5:00pm
  0   0    *   *   5       # Every Friday at 12:00 am
  0   0    1   */2 *       # Every other month, the first day, 12:00am
```

你可以在 [crontab.guru](https://crontab.guru/examples.html) 上找到更多常见的定时表配置示例。

## Shell 环境和日志

使用 cron 时一个常见的陷阱是：它不会像普通 shell（如 `.bashrc`、`.zshrc` 等）那样加载环境配置文件，默认也不会把输出写入任何日志。再加上 cron 最短只能设置到一分钟一次，初写 cron 脚本时调试起来会相当痛苦。

**译者注：** 为了帮助理解 `2>&1` 的含义——它表示将标准错误（stderr, 文件描述符 2）重定向到标准输出（stdout, 文件描述符 1）的位置。这样标准输出和标准错误就会被送到同一个地方（通常是日志文件）。如果你希望标准输出和标准错误分开记录，也可以分别重定向到不同的文件。

处理环境问题，建议在你的脚本中一律使用绝对路径，并在脚本中显式修改 `PATH` 等环境变量，确保脚本能顺利运行。为了简化日志记录，一个实用的建议是把 crontab 写成类似这样的格式：

```shell
* * * * *   user  /path/to/cronscripts/every_minute.sh >> /tmp/cron_every_minute.log 2>&1
```

然后把具体的逻辑写在单独的脚本文件里。注意 `>>` 表示追加写入文件（而不是覆盖），`2>&1` 把标准错误重定向到标准输出（不过你可能希望把两者分开记录）。

## Anacron

使用 cron 的一个隐患是：如果电脑在 cron 脚本应该执行的时候处于关机或睡眠状态，该任务就不会被执行。对于频繁执行的任务来说这可能无所谓，但如果某个任务运行频率较低，你可能希望确保它最终被执行。[anacron](https://linux.die.net/man/8/anacron) 的工作方式与 cron 类似，只不过它的时间间隔以**天**为单位。与 cron 不同，anacron 不假设机器一直在运行——因此它可以用于非 24 小时开机的机器，来管理每日、每周、每月等定期任务。

## 练习

1. 写一个脚本，每隔一分钟扫描你的下载文件夹（Downloads），查找其中所有的图片文件（你可以查阅 [MIME 类型](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types) 或者使用正则表达式来匹配常见扩展名），然后把它们移动到"图片"文件夹中。

2. 写一个 cron 定时脚本，每周检查系统中已过时的软件包，提醒你更新，或者直接自动更新它们。

{% comment %}

- [fswatch](https://github.com/emcrisostomo/fswatch)
- GUI automation (pyautogui) [Automating the boring stuff Chapter 18](https://automatetheboringstuff.com/chapter18/)
- Ansible/puppet/chef

- https://xkcd.com/1205/
- https://xkcd.com/1319/

{% endcomment %}