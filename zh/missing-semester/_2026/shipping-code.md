---
layout: lecture
title: "代码打包与发布"
description: >
  学习项目打包、虚拟环境、版本管理和部署库/应用/服务的方法。
thumbnail: /static/assets/thumbnails/2026/lec6.png
date: 2026-01-20
ready: true
video:
  aspect: 56.25
  id: KBMiB-8P4Ns
---

让代码按预期工作已经很难；让同一份代码在你的机器之外的另一台机器上运行，往往更难。

"发布代码"（shipping code）指的是：把你写的代码转换成一种可用的形式，让其他人无需依赖你的计算机的精确配置就能运行它。发布代码有多种形式，具体取决于编程语言的选择、系统库、操作系统等许多因素。它也取决于你在构建什么：一个软件库、一个命令行工具和一个 Web 服务各自有不同的需求和部署步骤。但不管哪种情况，都有一个共同的模式：我们需要定义交付物是什么——也就是所谓的**工件**（artifact）——以及它对运行环境做出哪些假设。

在本讲中，我们将覆盖以下内容：

- [依赖与环境](#dependencies--environments)
- [工件与打包](#artifacts--packaging)
- [发布与版本控制](#releases--versioning)
- [可复现性](#reproducibility)
- [虚拟机与容器](#vms--containers)
- [配置](#configuration)
- [服务与编排](#services--orchestration)
- [发布](#publishing)

我们将借助 Python 生态中的具体示例来解释这些概念——具体示例对于理解很有帮助。虽然其他编程语言的生态所使用的工具不同，但这些概念在很大程度上是共通的。

# 依赖与环境

在现代软件开发中，抽象的层次无处不在。程序自然会将逻辑委托给其他库或服务。然而，这也会在你的程序和其所需的库之间引入**依赖**（dependency）关系。例如，在 Python 中，如果要获取某个网页的内容，我们经常这样写：

```python
import requests

response = requests.get("https://missing.csail.mit.edu")
```

但 `requests` 库并不随 Python 运行时一起打包。如果我们在没有安装 `requests` 的情况下尝试运行这段代码，Python 会抛出一个错误：

```console
$ python fetch.py
Traceback (most recent call last):
  File "fetch.py", line 1, in <module>
    import requests
ModuleNotFoundError: No module named 'requests'
```

为了让这个库可用，我们需要先运行 `pip install requests` 来安装它。`pip` 是 Python 语言提供的用于安装包的命令行工具。执行 `pip install requests` 会产生以下一系列动作：

1. 在 Python 包索引（[PyPI](https://pypi.org/)）中搜索 requests
1. 查找与我们当前运行平台匹配的合适的工件
1. 解析依赖关系 —— `requests` 库本身也依赖其他包，因此安装器必须先找到所有传递依赖（transitive dependencies）的兼容版本并先行安装
1. 下载工件，然后解压并将文件复制到文件系统中的正确位置

```console
$ pip install requests
Collecting requests
  Downloading requests-2.32.3-py3-none-any.whl (64 kB)
Collecting charset-normalizer<4,>=2
  Downloading charset_normalizer-3.4.0-cp311-cp311-manylinux_x86_64.whl (142 kB)
Collecting idna<4,>=2.5
  Downloading idna-3.10-py3-none-any.whl (70 kB)
Collecting urllib3<3,>=1.21.1
  Downloading urllib3-2.2.3-py3-none-any.whl (126 kB)
Collecting certifi>=2017.4.17
  Downloading certifi-2024.8.30-py3-none-any.whl (167 kB)
Installing collected packages: urllib3, idna, charset-normalizer, certifi, requests
Successfully installed certifi-2024.8.30 charset-normalizer-3.4.0 idna-3.10 requests-2.32.3 urllib3-2.2.3
```

在这里我们可以看到 `requests` 拥有自己的依赖，如 `certifi` 和 `charset-normalizer`，这些依赖必须在 `requests` 安装之前安装。一旦安装完成，Python 运行时在导入该库时就能找到它。

```console
$ python -c 'import requests; print(requests.__path__)'
['/usr/local/lib/python3.11/dist-packages/requests']

$ pip list | grep requests
requests        2.32.3
```

不同编程语言有各自用于安装和发布库的工具、约定与实践。在 Rust 等语言中，工具链是统一的——`cargo` 负责构建、测试、依赖管理和发布。而在另一些语言如 Python 中，统一发生在规范层面——不是单一工具，而是有一套标准化的规范定义打包的工作方式，允许每个任务有相互竞争的工具（`pip` 与 [`uv`](https://docs.astral.sh/uv/)、`setuptools` 与 [`hatch`](https://hatch.pypa.io/) 与 [`poetry`](https://python-poetry.org/)）。在某些生态如 LaTeX 中，TeX Live 或 MacTeX 等发行版则捆绑了数千个预装包。

引入依赖也必然引入依赖冲突。当程序需要同一个依赖的不兼容版本时，就会发生冲突。例如，如果 `tensorflow==2.3.0` 要求 `numpy>=1.16.0,<1.19.0`，而 `pandas==1.2.0` 要求 `numpy>=1.16.5`，那么任何满足 `numpy>=1.16.5,<1.19.0` 的版本都有效。但如果你的项目中另一个包要求 `numpy>=1.19`，你就遇到了一个所有约束都无法满足的冲突。

这种多个包需要同一个共享依赖的互不兼容版本的情况，通常被称为**依赖地狱**（dependency hell）。一种应对冲突的方式是把每个程序的依赖隔离到各自的**虚拟环境**（environment）中。在 Python 中，我们运行以下命令来创建一个虚拟环境：

```console
$ which python
/usr/bin/python
$ pwd
/home/missingsemester
$ python -m venv venv
$ source venv/bin/activate
$ which python
/home/missingsemester/venv/bin/python
$ which pip
/home/missingsemester/venv/bin/pip
$ python -c 'import requests; print(requests.__path__)'
['/home/missingsemester/venv/lib/python3.11/site-packages/requests']

$ pip list
Package Version
------- -------
pip     24.0
```

你可以把虚拟环境看作是整个独立的语言运行时副本，它拥有自己的一组已安装包。这个虚拟环境将已安装的依赖从全局 Python 安装中隔离开来。为每个项目分别维护一个包含其所需依赖的虚拟环境，是一个好的做法。

> 虽然许多现代操作系统自带 Python 等编程语言的运行时安装，但修改这些安装是不明智的，因为操作系统本身可能依赖它们来提供功能。更推荐使用独立的虚拟环境。

在有些语言中，安装流程不是由工具定义，而是作为规范定义的。在 Python 中，[PEP 517](https://peps.python.org/pep-0517/) 定义了构建系统接口，[PEP 621](https://peps.python.org/pep-0621/) 规定了项目元数据存储在 `pyproject.toml` 中的方式。这让开发者得以改进 `pip`，产出更加优化的工具如 `uv`。安装 `uv` 只需执行 `pip install uv` 即可。

使用 `uv` 替代 `pip` 遵循相同的接口，但速度快得多：

```console
$ uv pip install requests
Resolved 5 packages in 12ms
Prepared 5 packages in 0.45ms
Installed 5 packages in 8ms
 + certifi==2024.8.30
 + charset-normalizer==3.4.0
 + idna==3.10
 + requests==2.32.3
 + urllib3==2.2.3
```

> 我们强烈建议尽可能使用 `uv pip` 替代 `pip`，它能大幅缩短安装时间。

除了隔离依赖，虚拟环境还允许你拥有不同版本的编程语言运行时。

```console
$ uv venv --python 3.12 venv312
Using CPython 3.12.7
Creating virtual environment at: venv312

$ source venv312/bin/activate && python --version
Python 3.12.7

$ uv venv --python 3.11 venv311
Using CPython 3.11.10
Creating virtual environment at: venv311

$ source venv311/bin/activate && python --version
Python 3.11.10
```

当你需要跨多个 Python 版本测试代码，或者某个项目需要特定版本时，这就非常有用。

> 在一些编程语言中，每个项目会自动获得自己的依赖环境，无需手动创建，但原理是相同的。如今大多数语言也都有在同一系统上管理多个语言版本的机制，并能指定每个项目使用哪个版本。

# 工件与打包

在软件开发中，我们区分**源代码**和**工件**（artifacts）。开发者编写和阅读源代码，而工件是从源代码打包而成的、可分发的输出——即准备好被安装或部署的东西。一个工件可以简单到仅是一个我们直接运行的代码文件，也可以复杂到包含应用程序所有必要组件的完整虚拟机。

考虑下面这个例子，我们当前目录下有一个 Python 文件 `greet.py`：

```console
$ cat greet.py
def greet(name):
    print(f"Hello, {name}!")

$ python -c "from greet import greet; greet('World')"
Hello, World!

$ cd /tmp
$ python -c "from greet import greet; greet('World')"
ModuleNotFoundError: No module named 'greet'
```

一旦我们切换到另一个目录，导入就会失败，因为 Python 只在特定位置搜索模块（当前目录、已安装的包，以及 `PYTHONPATH` 中的路径）。打包通过在已知位置安装代码解决了这个问题。

在 Python 中，为一个库打包就是产生一个包安装器（如 `pip` 或 `uv`）可以用来安装相关文件工件。Python 的工件被称为**轮子**（wheel），包含安装一个包所需的所有信息：代码文件、关于包的元数据（名称、版本、依赖），以及在环境中放置文件的说明。构建工件要求我们编写一个项目文件（也常称为清单），详细说明项目的具体信息、所需的依赖、包的版本以及其他信息。在 Python 中，我们为此使用 `pyproject.toml`。

> `pyproject.toml` 是现代且推荐的方式。虽然 `requirements.txt` 或 `setup.py` 等早期打包方法仍然支持，但你应该优先使用 `pyproject.toml`。

以下是一个同时提供命令行工具的库的最小 `pyproject.toml`：

```toml
[project]
name = "greeting"
version = "0.1.0"
description = "A simple greeting library"
dependencies = ["typer>=0.9"]

[project.scripts]
greet = "greeting:cli"

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
```

`typer` 库是一个流行的 Python 包，用于以最小的样板代码创建命令行界面。

对应的 `greeting.py` 如下：

```python
import typer


def greet(name: str) -> None:
    print(f"Hello, {name}!")


def cli() -> None:
    typer.run(greet)


if __name__ == "__main__":
    cli()
```

有了这个文件，我们现在就可以构建轮子了：

```console
$ uv build
Building source distribution...
Building wheel from source distribution...
Successfully built dist/greeting-0.1.0.tar.gz
Successfully built dist/greeting-0.1.0-py3-none-any.whl

$ ls dist/
greeting-0.1.0-py3-none-any.whl
greeting-0.1.0.tar.gz
```

`.whl` 文件是轮子（一种具有特定结构的 zip 归档），`.tar.gz` 则是面向需要从源码构建的系统提供的源码分发。

你可以检查轮子的内容来看看打包了哪些东西：

```console
$ unzip -l dist/greeting-0.1.0-py3-none-any.whl
Archive:  dist/greeting-0.1.0-py3-none-any.whl
  Length      Date    Time    Name
---------  ---------- -----   ----
      150  2024-01-15 10:30   greeting.py
      312  2024-01-15 10:30   greeting-0.1.0.dist-info/METADATA
       92  2024-01-15 10:30   greeting-0.1.0.dist-info/WHEEL
        9  2024-01-15 10:30   greeting-0.1.0.dist-info/top_level.txt
      435  2024-01-15 10:30   greeting-0.1.0.dist-info/RECORD
---------                     -------
      998                     5 files
```

现在，如果我们把这个轮子给另一个人，他们可以运行以下命令来安装它：

```console
$ uv pip install ./greeting-0.1.0-py3-none-any.whl
$ greet Alice
Hello, Alice!
```

这会将我们之前构建的库安装到他们的环境中，包括 `greet` 命令行工具。

这种方法也有局限性。特别是，如果我们的库依赖平台特定的库，例如用于 GPU 加速的 CUDA，那么我们的工件只能在安装了这些特定库的系统中运行，我们可能需要为不同的平台（Linux、macOS、Windows）和架构（x86、ARM）分别构建轮子。

安装软件时，有一个重要的区分：从源码安装与安装预编译二进制。从源码安装意味着下载原始代码并在你的机器上编译它——这需要已安装编译器和构建工具，对大型项目来说可能花费大量时间。

安装预编译二进制意味着下载别人已经编译好的工件——更快更简单，但二进制必须匹配你的平台和架构。例如，[ripgrep 的发布页面](https://github.com/BurntSushi/ripgrep/releases) 显示了面向 Linux（x86_64、ARM）、macOS（Intel、Apple Silicon）和 Windows 的预编译二进制。

# 发布与版本控制

代码的构建是一个连续的过程，但发布是离散的。在软件开发中，开发环境与生产环境之间有一条清晰的界限。代码需要在开发环境中被证明可用之后，才能被**发布**（shipping）到生产环境。发布过程涉及许多步骤，包括测试、依赖管理、版本控制、配置、部署和发布。

软件库不是静态的，而是随着修复和新功能的引入不断演进。我们通过离散的**版本标识符**来追踪这种演进，这些标识符对应库在某个时间点的状态。库行为的变化可能范围从修复非核心功能的补丁、扩展功能的新特性，到破坏向后兼容性的变更。**变更日志**（changelog）记录了某个版本引入了哪些变更——这些是软件开发者用来沟通新版本相关变更的文档。

然而，追踪每个依赖的持续变更是不切实际的，尤其是还要考虑传递依赖——即我们的依赖的依赖。

> 你可以使用 `uv tree` 可视化整个项目依赖树，它以树的形式展示所有包及其传递依赖。

为简化这个问题，存在关于如何对软件进行版本控制的约定，其中最普遍的之一是 [语义化版本](https://semver.org/)（Semantic Versioning，简称 SemVer）。在语义化版本中，版本采用 MAJOR.MINOR.PATCH 形式的标识符，每个值取一个整数。简言之：

- PATCH（例如，1.2.3 → 1.2.4）应当仅包含 Bug 修复，且完全向后兼容
- MINOR（例如，1.2.3 → 1.3.0）以向后兼容的方式添加新功能
- MAJOR（例如，1.2.3 → 2.0.0）表示可能需要代码修改的破坏性变更

> 这是一种简化，我们鼓励阅读完整的 SemVer 规范来理解，例如为什么从 0.1.3 到 0.2.0 可能导致破坏性变更，或者 1.0.0-rc.1 的含义是什么。

Python 打包支持由 [PEP 440](https://peps.python.org/pep-0440/) 定义的标准版本指定符。因此，当指定依赖的版本时，我们可以使用各种约束：

在 `pyproject.toml` 中，我们有不同的方式来约束依赖兼容版本的范围：

```toml
[project]
dependencies = [
    "requests==2.32.3",  # 精确版本 - 仅此特定版本
    "click>=8.0",        # 最低版本 - 8.0 或更高
    "numpy>=1.24,<2.0",  # 范围 - 至少 1.24 但低于 2.0
    "pandas~=2.1.0",     # 兼容发布 - >=2.1.0 且 <2.2.0
]
```

版本指定符存在于许多包管理器中（npm、cargo 等），具体语义各不相同。`~=` 操作符是 Python 的"兼容发布"操作符——`~=2.1.0` 意为"与 2.1.0 兼容的任何版本"，即 `>=2.1.0` 和 `<2.2.0`。这大致等价于 npm 和 cargo 中的脱字符（`^`）操作符，其遵循 SemVer 的兼容性概念。

并非所有软件都使用语义化版本。另一种常见的替代方案是日历版本（Calendar Versioning，CalVer），其中版本基于发布日期而非语义含义。例如，Ubuntu 使用 `24.04`（2024 年 4 月）和 `24.10`（2024 年 10 月）这样的版本。CalVer 让你很容易看出一个版本有多旧，但它无法传达任何关于兼容性的信息。最后，语义化版本并非完美无缺，有时维护者可能无意中在次要或补丁版本中引入了破坏性变更。

# 可复现性

在现代软件开发中，你编写的代码建立在大量的抽象层之上。这包括如编程语言运行时、第三方库、操作系统，甚至是硬件本身等因素。这任何一层之间的差异都可能改变你代码的行为，甚至使其无法按预期工作。此外，即使是底层硬件的差异也会影响你发布软件的能力。

**固定**（pinning）一个库指的是指定精确版本而非范围，例如 `requests==2.32.3` 而非 `requests>=2.0`。

包管理器的一项工作就是考虑依赖（及传递依赖）提供的所有约束，然后生成一个满足所有约束的有效版本列表。这个具体的版本列表可以保存到文件中以用于可复现性目的；这些文件被称为**锁文件**（lock files）。

```console
$ uv lock
Resolved 12 packages in 45ms

$ cat uv.lock | head -20
version = 1
requires-python = ">=3.11"

[[package]]
name = "certifi"
version = "2024.8.30"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/...", hash = "sha256:..." }
wheels = [
    { url = "https://files.pythonhosted.org/...", hash = "sha256:..." },
]
...
```

在处理依赖版本控制和可复现性时，一个关键区分是库与应用程序/服务之间的区别。库的目的是被其他代码导入和使用，而这些代码可能拥有自己的依赖，因此指定过于严格的版本约束可能会与用户的其他依赖产生冲突。相比之下，应用程序或服务是软件的最终消费者，通常通过用户界面或 API 暴露其功能，而非通过编程接口。对于库，指定版本范围以最大化与更广泛包生态的兼容性是一个好的做法。对于应用程序，固定精确版本确保可复现性——每个人运行应用程序时都使用完全相同的依赖。

> 译者补充：锁文件（lock file）的作用是记录在某一时刻所有依赖及其传递依赖的确切版本。当其他人（或 CI 系统）使用同一个锁文件安装时，会得到一模一样的依赖树，从而保证"在我机器上能跑"也等于"在你机器上能跑"。

对于需要最大可复现性的项目，像 [Nix](https://nixos.org/) 和 [Bazel](https://bazel.build/) 这样的工具提供**确定性构建**（hermetic builds）——其中每一个输入，包括编译器、系统库，甚至构建环境本身都被固定并通过内容寻址。这保证了无论构建何时何地进行，输出都逐位相同。

> 你甚至可以使用 NixOS 管理你的整个计算机系统，使得你可以轻松拉起计算机配置的多个副本，并通过版本控制的配置文件管理其完整配置。

软件开发中有一个永无止境的张力：新软件版本要么有意、要么无意地引入破坏；另一方面，旧软件版本会随着时间的推移而出现安全漏洞。我们可以通过持续集成流水线（我们稍后在 [代码质量与 CI](/2026/code-quality/) 讲座中会看到更多）来解决这个问题——用它来测试应用程序对新软件版本的兼容性，同时建立自动化来检测我们的依赖是否有新版本发布，例如 [Dependabot](https://github.com/dependabot)。

即使有了 CI 测试，在升级软件版本时仍然会发生问题，常常是因为开发环境与生产环境之间不可避免的不匹配。在这些情况下，最好的做法是有一个**回滚**（rollback）计划，即回退版本升级并重部署一个已知良好的版本。

# 虚拟机与容器

随着你越来越依赖复杂的依赖，你的代码的依赖很可能超出包管理器所能处理的范围。一个常见的原因是必须与特定的系统库或硬件驱动程序进行交互。例如，在科学计算和 AI 中，程序经常需要专门的库和驱动来利用 GPU 硬件。许多系统级依赖（GPU 驱动、特定编译器版本、共享库如 OpenSSL）仍然需要系统级安装。

传统上，这个更广泛的依赖问题通过虚拟机（VMs）来解决。虚拟机抽象整个计算机，并提供一个完全隔离的环境，拥有自己专用的操作系统。一种更现代的方法是使用容器，它将应用程序连同其依赖、库和文件系统一起打包，但共享宿主机的操作系统内核，而不是虚拟化整个计算机。容器比虚拟机更轻量，因为它们共享内核，启动更快且运行更高效。

最流行的容器平台是 [Docker](https://www.docker.com/)。Docker 引入了一种标准化方式来构建、分发和运行容器。在底层，Docker 使用 containerd 作为其容器运行时——这也是 Kubernetes 等其他工具使用的行业标准。

运行容器很简单。例如，要在容器中运行 Python 解释器，我们使用 `docker run`（`-it` 标志使容器以交互式终端运行。退出后，容器停止。）：

```console
$ docker run -it python:3.12 python
Python 3.12.7 (main, Nov  5 2024, 02:53:25) [GCC 12.2.0] on linux
>>> print("Hello from inside a container!")
Hello from inside a container!
```

在实际使用中，你的程序可能依赖于整个文件系统。为解决这个问题，我们可以使用包含应用程序完整文件系统的容器镜像作为工件。容器镜像通过编程方式创建。使用 Docker，我们通过 Dockerfile 语法精确指定镜像的依赖、系统库和配置：

```dockerfile
FROM python:3.12
RUN apt-get update
RUN apt-get install -y gcc
RUN apt-get install -y libpq-dev
RUN pip install numpy
RUN pip install pandas
COPY . /app
WORKDIR /app
RUN pip install .
```

一个重要区分：Docker **镜像**（image）是打包好的工件（类似模板），而**容器**（container）是该镜像的一个运行实例。你可以从同一个镜像运行多个容器。镜像以层（layer）方式构建，Dockerfile 中的每条指令（`FROM`、`RUN`、`COPY` 等）创建一个新的层。Docker 会缓存这些层，因此如果你更改 Dockerfile 中的某一行，只需要重建该行及其后续层。

上面的 Dockerfile 有几个问题：它使用了完整的 Python 镜像而非精简变体，分别运行单独的 `RUN` 命令创建不必要的层，版本未固定，且没有清理包管理器缓存、携带不必要的文件。其他常见错误包括以 root 不安全地运行容器，以及无意中在层中嵌入密钥。

下面是一个改进版本：

```dockerfile
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project
COPY . .
RUN uv sync --locked --no-dev
```

在前面的示例中我们看到，我们没有从源码安装 `uv`，而是从 `ghcr.io/astral-sh/uv:latest` 镜像复制预编译二进制。这被称为**构建器模式**（builder pattern）。使用这种模式，我们不需要携带编译代码所需的所有工具，只需携带运行应用程序所需的最终二进制文件（在本例中为 `uv`）。

Docker 有重要的局限性需要注意。首先，容器镜像通常是平台特定的——为 `linux/amd64` 构建的镜像在没有模拟的情况下无法在 `linux/arm64`（Apple Silicon Mac）上原生运行，而模拟速度很慢。其次，Docker 容器需要 Linux 内核，因此在 macOS 和 Windows 上，Docker 实际上在底层运行一个轻量级 Linux VM，增加了开销。第三，Docker 的隔离性弱于 VM——容器共享宿主内核，在多方环境中存在安全问题。

> 如今，越来越多的项目也开始利用 [nix flakes](https://serokell.io/blog/practical-nix-flakes) 来为每个项目管理系统级库和应用。

# 配置

软件本质上都是可配置的。在 [命令行环境](/2026/command-line-environment/) 讲座中，我们看到了程序通过标志、环境变量或甚至配置文件（又名 dotfiles）接收选项。这种情况对于更复杂的应用程序同样适用，并且有成熟的模式用于大规模管理配置。软件配置不应嵌入代码中，而应在运行时提供。常见的两种方式是环境变量和配置文件。

以下是一个通过环境变量配置的应用程序的示例：

```python
import os

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///local.db")
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
API_KEY = os.environ["API_KEY"]  # 必需 —— 如果未设置则抛出异常
```

应用程序也可以通过配置文件来配置（例如，一个通过 `yaml.load` 加载配置的 Python 程序），`config.yaml`：

```yaml
database:
  url: "postgresql://localhost/myapp"
  pool_size: 5
server:
  host: "0.0.0.0"
  port: 8080
  debug: false
```

思考配置的一个好用的右倾原则是：同一代码库应仅通过配置变更（而非代码变更）就能部署到不同的环境（开发、预发布、生产）。

在众多配置选项中，往往包含敏感数据，如 API 密钥。密钥需要小心处理以避免意外泄露，且不应纳入版本控制。

# 服务与编排

现代应用程序很少孤立存在。一个典型的 Web 应用可能需要一个数据库用于持久存储、一个缓存用于性能、一个消息队列用于后台任务，以及多种其他辅助服务。现代架构通常不会将一切打包成一个单体应用，而是将功能分解为可以独立开发、部署和扩展的独立服务。

举例来说，如果我们确定应用程序从使用缓存中受益，我们可以利用已有的经实战检验的方案（如 [Redis](https://redis.io/) 或 [Memcached](https://memcached.org/)），而不是自己从零构建。我们可以在构建容器时将 Redis 嵌入我们的应用程序依赖中，但这意味着需要协调 Redis 和我们的应用程序之间的所有依赖，这可能颇具挑战甚至不可行。相反，我们可以做的是将每个应用程序独立部署到自己的容器中。这通常被称为**微服务架构**（microservice architecture），其中每个组件作为独立服务运行，并通过网络通信，通常通过 HTTP API。

[Docker Compose](https://docs.docker.com/compose/) 是一个用于定义和运行多容器应用程序的工具。你不必单独管理容器，而是在单个 YAML 文件中声明所有服务，然后一起编排它们。现在我们的完整应用程序包含不止一个容器：

```yaml
# docker-compose.yml
services:
  web:
    build: .
    ports:
      - "8080:8080"
    environment:
      - REDIS_URL=redis://cache:6379
    depends_on:
      - cache

  cache:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

通过 `docker compose up`，两个服务一起启动，Web 应用可以通过主机名 `cache` 连接 Redis（Docker 的内部 DNS 会自动解析服务名）。Docker Compose 让我们声明如何部署一个或多个服务，并处理启动编排、在它们之间设置网络，以及为数据持久性管理共享卷。

对于生产部署，你通常希望 Docker Compose 服务在系统启动时自动启动，并在失败时重启。一种常见的方法是使用 systemd 来管理 Docker Compose 的部署：

```ini
# /etc/systemd/system/myapp.service
[Unit]
Description=My Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/myapp
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down

[Install]
WantedBy=multi-user.target
```

这个 systemd 单元文件确保你的应用在系统启动时（Docker 就绪之后）启动，并提供 `systemctl start myapp`、`systemctl stop myapp` 和 `systemctl status myapp` 等标准控制命令。

随着部署要求变得越来越复杂——需要在多台机器上扩展、服务崩溃时的容错以及高可用性保证——组织会转向更复杂的容器编排平台，如 Kubernetes（k8s），它可以在机器集群上管理数千个容器。不过，Kubernetes 学习曲线陡峭且运维开销巨大，因此对于较小的项目来说往往是大材小用。

这种多容器设置之所以部分可行，是因为现代服务通过标准化的 API（尤其是 HTTP REST API）相互通信。例如，每当一个程序与 OpenAI 或 Anthropic 等 LLM 提供商交互时，底层它发送的是一个 HTTP 请求到他们的服务器并解析响应：

```console
$ curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "content-type: application/json" \
    -H "anthropic-version: 2023-06-01" \
    -d '{"model": "claude-sonnet-4-20250514", "max_tokens": 256,
         "messages": [{"role": "user", "content": "Explain containers vs VMs in one sentence."}]}'
```

# 发布

当你的代码已经能工作时，你可能有兴趣将其分发，供他人下载和安装。分发有多种形式，并且与你所操作的编程语言和环境密切相关。

最简单的分发形式是上传工件，供他人下载和安装到本地。这仍然很常见，你可以在 [Ubuntu 的软件包归档](http://archive.ubuntu.com/ubuntu/pool/main/) 中找到它，它本质上是一个 `.deb` 文件的 HTTP 目录列表。

如今，GitHub 已成为发布源代码和工件的事实上的平台。虽然源代码通常公开可用，GitHub Releases 允许维护者为标记的版本附加预编译的二进制和其他工件。

一些包管理器还支持直接从 GitHub 安装，可以从源码或预编译的轮子安装：

```console
# 从源码安装（将克隆并构建）
$ pip install git+https://github.com/psf/requests.git

# 从特定标签/分支安装
$ pip install git+https://github.com/psf/requests.git@v2.32.3

# 直接从 GitHub release 安装轮子
$ pip install https://github.com/user/repo/releases/download/v1.0/package-1.0-py3-none-any.whl
```

实际上，有些语言如 Go 使用去中心化的分发模式——没有中央包仓库，Go 模块直接从它们的源代码仓库分发。模块路径如 `github.com/gorilla/mux` 指示代码所在位置，`go get` 直接从那里获取。但是，大多数包管理器如 `pip`、`cargo` 或 `brew` 都有预打包项目的中央索引，以便于分发和安装。如果我们运行

```console
$ uv pip install requests --verbose --no-cache 2>&1 | grep -F '.whl'
DEBUG Selecting: requests==2.32.5 [compatible] (requests-2.32.5-py3-none-any.whl)
DEBUG No cache entry for: https://files.pythonhosted.org/packages/1e/db/4254e3eabe8020b458f1a747140d32277ec7a271daf1d235b70dc0b4e6e3/requests-2.32.5-py3-none-any.whl.metadata
DEBUG No cache entry for: https://files.pythonhosted.org/packages/1e/db/4254e3eabe8020b458f1a747140d32277ec7a271daf1d235b70dc0b4e6e3/requests-2.32.5-py3-none-any.whl
```

我们可以看到 `requests` 的轮子是从哪里获取的。注意文件名中的 `py3-none-any`——这意味着该轮子在任何操作系统、任何架构的任意 Python 3 版本上都能工作。对于有编译代码的包，轮子是平台特定的：

```console
$ uv pip install numpy --verbose --no-cache 2>&1 | grep -F '.whl'
DEBUG Selecting: numpy==2.2.1 [compatible] (numpy-2.2.1-cp312-cp312-macosx_14_0_arm64.whl)
```

这里的 `cp312-cp312-macosx_14_0_arm64` 表示该轮子专门用于 ARM64（Apple Silicon）上 macOS 14+ 的 CPython 3.12。如果你在不同的平台上，`pip` 将下载不同的轮子或从源码构建。

相反，为了让别人能够找到我们创建的包，我们需要将其发布到这些注册表之一。在 Python 中，主要的注册表是 [Python 包索引（PyPI）](https://pypi.org)。与安装类似，发布包有多种方式。`uv publish` 命令为上传包到 PyPI 提供了现代界面：

```console
$ uv publish --publish-url https://test.pypi.org/legacy/
Publishing greeting-0.1.0.tar.gz
Publishing greeting-0.1.0-py3-none-any.whl
```

这里我们使用的是 [TestPyPI](https://test.pypi.org)——一个独立的包注册表，用于测试你的发布流程，而不会污染正式的 PyPI。上传后，你可以从 TestPyPI 安装：

```console
$ uv pip install --index-url https://test.pypi.org/simple/ greeting
```

发布软件时的一个关键考虑是信任。用户如何验证他们下载的包确实来自你且未被篡改？包注册表使用校验和来验证完整性，一些生态还支持包的签名以提供作者身份的密码学证明。

不同语言有自己的包注册表：[crates.io](https://crates.io) 用于 Rust，[npm](https://www.npmjs.com) 用于 JavaScript，[RubyGems](https://rubygems.org) 用于 Ruby，[Docker Hub](https://hub.docker.com) 用于容器镜像。同时，对于私有或内部包，组织通常部署自己的包存储库（如私有 PyPI 服务器或私有 Docker 注册表），或使用云提供商提供托管解决方案。

将 Web 服务部署到互联网涉及额外的基础设施：域名注册、将域名指向服务器的 DNS 配置，以及通常使用 nginx 等反向代理来处理 HTTPS 和路由流量。对于更简单的用例（如文档或静态站点），[GitHub Pages](https://pages.github.com/) 直接从仓库提供免费托管。

<!--
## 文档

到目前为止，我们一直强调交付物**工件**作为打包和发布代码的主要输出。除工件外，我们还需要为用户记录代码的功能、安装说明和使用示例。

[Sphinx](https://www.sphinx-doc.org/)（Python）和 [MkDocs](https://www.mkdocs.org/) 等工具可以自动从 docstrings 和 markdown 文件生成交互式文档，通常托管在 [Read the Docs](https://readthedocs.org/) 等服务上。对于基于 HTTP 的 API，[OpenAPI 规范](https://www.openapis.org/)（前身为 Swagger）提供了描述 API 端点的标准格式，工具可以利用它自动生成交互式文档和客户端库。 -->


# 练习

1. 将你的环境通过 `printenv` 保存到文件，创建一个虚拟环境并激活它，再将 `printenv` 输出到另一个文件中，然后 `diff before.txt after.txt`。环境中哪些内容发生了变化？为什么 shell 优先选择虚拟环境？（提示：查看激活前后的 `$PATH`。）运行 `which deactivate` 并推理 `deactivate` 这个 bash 函数在做什么。
1. 创建一个带有 `pyproject.toml` 的 Python 包，并在虚拟环境中安装它。创建一个锁文件并检查它的内容。
1. 安装 Docker，并使用 docker compose 在本地构建 Missing Semester 课程网站。
1. 为一个简单的 Python 应用编写一个 Dockerfile。然后编写一个 `docker-compose.yml`，将你的应用与一个 Redis 缓存一起运行。
1. 将一个 Python 包发布到 TestPyPI（除非值得分享，否则不要发布到正式的 PyPI）。然后构建一个包含该包的 Docker 镜像，并将其推送到 `ghcr.io`。
1. 使用 [GitHub Pages](https://docs.github.com/en/pages/quickstart) 创建一个网站。额外（不加分）挑战：配置自定义域名。