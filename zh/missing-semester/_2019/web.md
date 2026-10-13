---
layout: lecture
title: "Web 与浏览器"
presenter: Jose
date: 2019-01-31
order: 1
video:
  aspect: 62.5
  id: XpZO3S8odec
special: true
---

除了终端（Terminal）之外，Web 浏览器是另一个你可能投入大量时间的工具。因此，学会高效、有产出地使用它是非常值得的。

## 快捷键

在浏览器中四处点击往往不是最快的方式。熟悉常用快捷键，从长远来看会大大提高效率。

- 在链接上 `Middle Button Click`（鼠标中键点击）可在新标签页中打开它
- `Ctrl+T` 打开新标签页
- `Ctrl+Shift+T` 重新打开最近关闭的标签页
- `Ctrl+L` 选中地址栏（search bar）的内容
- `Ctrl+F` 在当前网页中搜索。如果你经常使用搜索功能，可以安装支持在搜索中使用**正则表达式**（regular expression）的扩展插件

## 搜索运算符（Search operators）

Google 或 DuckDuckGo 等 Web 搜索引擎提供了多种搜索运算符，可以执行更精确的检索：

- `"bar foo"` 强制精确匹配 "bar foo"（含空格和顺序）
- `foo site:bar.com` 在 bar.com 域名内搜索 foo
- `foo -bar` 从搜索结果中排除包含 bar 的词条
- `foobar filetype:pdf` 搜索指定扩展名的文件
- `(foo|bar)` 搜索包含 foo 或 bar 的匹配项

更多详细的运算符列表可在 [Google](https://ahrefs.com/blog/google-advanced-search-operators/) 和 [DuckDuckGo](https://duck.co/help/results/syntax) 等主流引擎的帮助页面找到。

## 搜索栏（Search bar）

搜索栏本身也是一个强大的工具。大多数浏览器能够自动推断网站所使用的搜索引擎并将其保存下来。通过编辑**关键词参数**（keyword argument），可以实现类似 `y 一些搜索词` 这样直接在搜索引擎中输入关键词的操作。

- 在 Google Chrome 中，它们位于 [chrome://settings/searchEngines](chrome://settings/searchEngines)
- 在 Firefox 中，它们位于 [about:preferences#search](about:preferences#search)

例如，你可以设置让 `y 一些搜索词` 直接在 YouTube 中搜索。

此外，如果你拥有一个域名，可以通过域名注册商（registrar）设置子域名转发。比如我已将 `https://ht.josejg.com` 指向本课程网站。这样我只需输入 `ht.`，搜索栏就会自动补全。这种设置另一个好处是：与书签不同，它可以在任何浏览器中使用。

## 隐私扩展插件

如今，上网冲浪往往会因广告而感到厌烦，并因追踪器（trackers）的存在而侵犯隐私。另外，一个优秀的广告拦截插件不仅会拦截大多数广告内容，还会拦截可疑和恶意网站——因为这些网站的域名通常已被列入公共黑名单。它还可以通过减少页面请求的数量，在一定程度上缩短页面加载时间。推荐以下扩展：

- **uBlock Origin**（[Chrome](https://chrome.google.com/webstore/detail/ublock-origin/cjpalhdlnbpafiamejdnhcphjbkeiagm)、[Firefox](https://addons.mozilla.org/en-US/firefox/addon/ublock-origin/)）：基于预设规则拦截广告和追踪器。你还应该查看设置中启用的黑名单，因为你可以根据自己的地区或浏览习惯启用更多规则。甚至可以安装来自[世界各地](https://github.com/gorhill/uBlock/wiki/Filter-lists-from-around-the-web)的过滤规则。

- **[Privacy Badger](https://privacybadger.org/)**：自动检测并阻止追踪器。例如，当你从一个网站跳转到另一个网站时，广告公司会跟踪你访问过的站点并为你建立用户画像。

- **[HTTPS Everywhere](https://www.eff.org/https-everywhere)**：一个非常优秀的扩展，如果目标网站支持，它会自动将 HTTP 请求重定向到 HTTPS 版本。

你可以在[这里](https://www.privacytools.io/privacy-browser-addons/)找到更多同类扩展。

## 样式自定义（Style customization）

Web 浏览器只是运行在**你的机器**上的另一套软件，因此你通常有权决定它应该显示什么、以何种方式运行。自定义样式（custom styles）就是很好的例子。浏览器使用 **Cascading Style Sheets**（层叠样式表，通常缩写为 **CSS**）来决定网页的渲染样式。

你可以通过检查（inspect）网页源码并临时修改其内容和样式来查看效果（这也是为什么你不应该轻信网页截图的原因之一）。

如果你希望让浏览器**永久地**覆盖某个网页的样式设置，就需要使用扩展插件。我们推荐 **[Stylus](https://github.com/openstyles/stylus)**（[Firefox](https://addons.mozilla.org/en-US/firefox/addon/styl-us/)、[Chrome](https://chrome.google.com/webstore/detail/stylus/clngdbkpkpeebahjckkjfobafhncgmne?hl=en)）。

例如，我们可以为课程网站编写如下样式：

```css

body {
    background-color: #2d2d2d;
    color: #eee;
    font-family: Fira Code;
    font-size: 16pt;
}

a:link {
    text-decoration: none;
    color: #0a0;
}
```

此外，Stylus 还能发现其他用户编写并发布在 [userstyles.org](https://userstyles.org/) 上的样式。例如，大多数常见网站都有一套或多套深色主题（dark theme）样式表。顺便一提，你不应该使用 Stylish，因为它已被证实会泄露用户数据，详见[此处](https://arstechnica.com/information-technology/2018/07/stylish-extension-with-2m-downloads-banished-for-tracking-every-site-visit/)。

## 功能自定义（Functionality Customization）

与修改样式类似，你也可以通过编写自定义 JavaScript 代码，然后借助 [Tampermonkey](https://tampermonkey.net/) 等浏览器扩展来加载这些脚本，从而修改网站的行为。

例如，下面的脚本可以让你使用 J 和 K 键实现类似 Vim 的导航效果。

```js
// ==UserScript==
// @name         VIM HT
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  Vim JK for our website
// @author       You
// @match        https://hacker-tools.github.io/*
// @grant        none
// ==/UserScript==


(function() {
    'use strict';

    window.onkeyup = function(e) {
        var key = e.keyCode ? e.keyCode : e.which;

        if (key == 74) { // J is key 74
            window.scrollBy(0,500);;
        }else if (key == 75) { // K is key 75
            window.scrollBy(0,-500);;
        }
    }
})();
```

还有一些脚本仓库，例如 [OpenUserJS](https://openuserjs.org/) 和 [Greasy Fork](https://greasyfork.org/en)。但请注意，安装他人提供的用户脚本可能非常危险，因为它们几乎可以做任何事情——包括窃取你的信用卡信息。除非你自己通读了整个脚本、理解了它做了什么，并且百分之百确定它没有在搞什么可疑操作，否则千万不要安装。千万不要安装包含你无法阅读的**压缩（minified）**或**混淆（obfuscated）**代码的脚本！

> 译者注：用户脚本（User Script）是浏览器扩展的一种轻量形式，允许用户在特定网页上注入自定义 JavaScript。正因为权限较高，其安全性高度依赖于脚本本身的质量。

## Web API

越来越多的网络服务开始提供**应用程序接口**（Application Programming Interface，简称 **API**，此处特指 **Web API**），让你可以通过发送 Web 请求与服务进行交互。

关于该主题的更深入介绍可以参考[这里](https://developer.mozilla.org/en-US/docs/Learn/JavaScript/Client-side_web_APIs/Introduction)。[许多公共 API](https://github.com/toddmello/public-apis) 可供使用。Web API 在很多场景下都很有用：

- **数据获取（Retrieval）**。Web API 可以很方便地为你提供信息，例如地图、天气或你的公网 IP 地址。例如，`curl ipinfo.io` 会返回一个 JSON 对象，其中包含你公网 IP、地区、位置等详细信息。经过适当的解析后，这些工具甚至可以与命令行工具集成。下面的 Bash 函数会调用 Google 自动补全 API，并返回前 10 个匹配结果。

```bash
function c() {
    url='https://www.google.com/complete/search?client=hp&hl=en&xhr=t'
    # NB: user-agent must be specified to get back UTF-8 data!
    curl -H 'user-agent: Mozilla/5.0' -sSG --data-urlencode "q=$*" "$url" |
        jq -r ".[1][][0]" |
        sed 's,</\?b>,,g'
}
```

- **交互（Interaction）**：Web API 的端点（endpoints）还可以用于触发特定操作。这些请求通常需要某种形式的**认证令牌**（authentication token），你可以从服务提供方获取。例如，执行以下命令可以在某个 Slack 频道中发送一条 `Hello, World!` 消息：

```
curl -X POST -H 'Content-type: application/json' --data '{"text":"Hello, World!"}' "https://hooks.slack.com/services/$SLACK_TOKEN"
```

- **管道连接（Piping）**：由于一些带有 Web API 的服务非常流行，一些常见的 Web API "胶水"（gluing，即把不同 API 串联起来的操作）已经实现完毕并随服务器一起提供。例如 [If This Then That](https://ifttt.com/) 和 [Zapier](https://zapier.com/) 就属于这类服务。

> 译者补充：Web API 的"Piping"能力本质上是将不同服务的接口拼接在一起，实现跨平台自动化。例如，当你在 GitHub 上创建一个 issue 时，Zapier 可以自动往你的 Slack 频道发一条通知——不需要你自己写代码，只需要在 Zapier 界面选择触发器和动作即可。

## Web 自动化（Web Automation）

有时 Web API 还不够。如果只需要读取页面内容，你可以使用 `pup` 这样的 HTML 解析器，或者使用库（例如 Python 的 BeautifulSoup）。但如果需要**交互操作**或**执行 JavaScript**，这些方案就力不从心了。

- **WebDriver**。例如，以下脚本会使用 Wayback Machine（互联网档案馆）保存指定 URL 的快照，模拟手动输入网址的操作：

```python
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys


def snapshot_wayback(driver, url):

    driver.get("https://web.archive.org/")
    elem = driver.find_element_by_class_name('web-save-url-input')
    elem.clear()
    elem.send_keys(url)
    elem.send_keys(Keys.RETURN)
    driver.close()


driver = Firefox()
url = 'https://hacker-tools.github.io'
snapshot_wayback(driver, url)
```


## 练习（Exercises）

1. 编辑你浏览器中一个你经常使用的关键词搜索引擎（keyword search engine）
1. 安装上述提到的扩展插件。了解如何针对某个网站禁用 uBlock Origin / Privacy Badger。你看到了什么区别？试着在广告很多的网站（如 YouTube）上操作一下。
1. 安装 Stylus，使用所提供的 CSS 为课程网站编写一个自定义样式。这里有一些常见的编程字符 `=   ==   ===   >=   =>   ++   /=   ~=`。当把字体改为 Fira Code 时它们会发生什么变化？如果想了解更多，可以搜索"编程字体连字"（programming font ligatures）。
1. 找到一个可以获取你所在城市的天气的 Web API。
1. 使用 [Selenium](https://www.selenium.dev/documentation/) 等 WebDriver 软件，自动化一个你经常用浏览器执行的重复性手动任务。
