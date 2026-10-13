---
layout: page
title: 你的计算机教育所缺的一节课
description: >
  掌握强大工具，让你成为更高效的研究人员和程序员。
# subtitle: IAP 2026
subtitle: "2026"
nositetitle: true
---

课程会教你计算机高级主题——从操作系统到机器学习——但有一门关键的课程却很少被涵盖，通常只能让学生自己去摸索：如何熟练使用各种工具。我们将教你如何掌握命令行、使用功能强大的文本编辑器、利用版本控制系统的高级功能，等等！

学生在整个学习生涯中会花费数百小时使用这些工具（在职业生涯中更是长达数千小时），因此让这段体验尽可能流畅、毫无阻碍是非常有意义的。掌握这些工具不仅能让你少花时间琢磨如何让自己的工具听命于你，还能让你解决那些过去看起来不可思议的复杂问题。

如今，随着 AI 驱动和 AI 增强型工具与工作流的引入，软件工程的许多方面也在发生变化。如果在适当时机使用，并对它们各自的不足之处保持清醒认识，这些工具通常能为研究人员和从业者带来显著收益，因此值得花时间建立实际可用的知识储备。由于 AI 是一种跨领域的使能技术，我们没有设置单独的 AI 讲座，而是将最新适用的 AI 工具和技术直接融入每一节课程中。

了解更多关于[开设这门课的初衷](/about/)。

{% comment %}
# 注册

填写此[注册表单](https://forms.gle/j2wMzi7qeiZmzEWy9)加入 IAP 2026 班级。
{% endcomment %}

# 教学大纲

{% comment %}
**讲座**：[35-225](https://whereis.mit.edu/?go=35)，13:30–14:30（_例外_：1月16日周五 15:00–16:00）<br>
**讨论**：[OSSU Discord](https://ossu.dev/#community)（将 `#missing-semester-forum` 当作 Piazza 使用，用 `#missing-semester` 和同学、讲师聊天）
{% endcomment %}

<ul>
{% assign lectures = site['2026'] | sort: 'date' %}
{% for lecture in lectures %}
    {% if lecture.phony != true %}
        <li>
        <strong>{{ lecture.date | date: '%-m/%-d/%y' }}</strong>:
        {% if lecture.ready %}
            <a href="{{ lecture.url }}">{{ lecture.title }}</a>
        {% else %}
            {{ lecture.title }} {% if lecture.noclass %}[无课]{% endif %}
        {% endif %}
        </li>
    {% endif %}
{% endfor %}
</ul>

## 往年特别专题

每届的课程内容会有所不同。对于那些希望了解历届涵盖的所有专题、且对 2026 年未讲到的一些往年内容感兴趣的同学，我们列出过去几年中曾讲过但 2026 年未覆盖的专题。

{% comment %} pop to remove default "posts" collection {% endcomment %}
{% assign sorted_collections = site.collections | sort: 'label' | pop | reverse %}
<ul>
{% for collection in sorted_collections %}
    {% assign grouped_lectures = site[collection.label] | group_by: 'date' | sort: 'name' %}
    {% for group in grouped_lectures %}
        {% assign sorted_lectures = group.items | sort: 'order' %}
        {% for lecture in sorted_lectures %}
            {% if lecture.special == true %}
                <li>
                    <strong>{{ lecture.date | date: '%-m/%-d/%y' }}</strong>:
                    <a href="{{ lecture.url }}">{{ lecture.title }}</a>
                </li>
            {% endif %}
        {% endfor %}
    {% endfor %}
{% endfor %}
</ul>

{% comment %}
讲座视频会在课后立即通过 Panopto 向 MIT 学生开放。该系统的限制在于只有拥有 MIT Kerberos 凭据的用户才能访问原始讲座视频。我们正对讲座视频进行剪辑并上传到 YouTube。部分视频已经上传完成，其余的预计在二月中旬之前上传。

如果你等不到 2026 年 1 月，也可以看看[之前版本的课程](/2020/)，它们涵盖了大量相同的主题。
{% endcomment %}

# 通用信息

**授课教师**：本课程由 [Anish](https://anish.io/)、[Jon](https://thesquareplanet.com/) 和 [Jose](https://josejg.com/) 共同讲授。<br>
**问题反馈**：请发送邮件至 [missing-semester@mit.edu](mailto:missing-semester@mit.edu)。<br>
**讨论区**：[OSSU Discord](https://ossu.dev/#community)（将 `#missing-semester-forum` 当作 Piazza 使用，用 `#missing-semester` 和同学、讲师聊天）。

# Beyond MIT（MIT 之外）

我们也希望将这门课分享出去，让更多人从中受益。你可以在以下平台找到相关的帖子和讨论：

 - Hacker News（[2026](https://news.ycombinator.com/item?id=47124171)、[2020](https://news.ycombinator.com/item?id=22226380)、[2019](https://news.ycombinator.com/item?id=19078281)）
 - Lobsters（[2026](https://lobste.rs/s/q4ykw7/missing_semester_your_cs_education_2026)、[2020](https://lobste.rs/s/ti1k98/missing_semester_your_cs_education_mit)、[2019](https://lobste.rs/s/h6157x/mit_hacker_tools_lecture_series_on)）
 - r/learnprogramming（[2026](https://www.reddit.com/r/learnprogramming/comments/1r93yk6/the_missing_semester_of_your_cs_education_2026/)、[2020](https://www.reddit.com/r/learnprogramming/comments/eyagda/the_missing_semester_of_your_cs_education_mit/)、[2019](https://www.reddit.com/r/learnprogramming/comments/an42uu/mit_hacker_tools_a_lecture_series_on_programmer/)）
 - r/programming（[2020](https://www.reddit.com/r/programming/comments/eyagcd/the_missing_semester_of_your_cs_education_mit/)、[2019](https://www.reddit.com/r/programming/comments/an3xki/mit_hacker_tools_a_lecture_series_on_programmer/)）
 - X（[2026](https://x.com/anishathalye/status/2024521145777848588)、[2020](https://twitter.com/jonhoo/status/1224383452591509507)、[2019](https://x.com/jonhoo/status/1090323977766137858)）
 - Bluesky（[2026](https://bsky.app/profile/jonhoo.eu/post/3mfa2bhyuj22i)）
 - Mastodon（[2026](https://fosstodon.org/@jonhoo/116098318361854057)）
 - LinkedIn（[2026](https://www.linkedin.com/posts/anishathalye_i-returned-to-mit-during-iap-january-term-activity-7430285026933522433-Ehr9)）
 - YouTube（[2026](https://www.youtube.com/playlist?list=PLyzOVJj3bHQunmnnTXrNbZnBaCA-ieK4L)、[2020](https://www.youtube.com/playlist?list=PLyzOVJj3bHQuloKGG59rS43e29ro7I57J)、[2019](https://www.youtube.com/playlist?list=PLyzOVJj3bHQuiujH1lpn8cA9dsyulbYRv)）

# 翻译版本

{% comment %} keep these in alphabetical order {% endcomment %}

- [阿拉伯语](https://missing-semester-ar.github.io/)
- [孟加拉语](https://missing-semester-bn.github.io/)
- [缅甸语](https://missing-semester-my.github.io/)
- [简体中文](https://missing-semester-cn.github.io/)
- [繁体中文（台湾）](https://missing-semester-tw.github.io/)
- [德语](https://missing-semester-de.github.io/)
- [意大利语](https://missing-semester-it.github.io/)
- [日语](https://missing-semester-jp.github.io/)
- [卡纳达语](https://missing-semester-kn.github.io/)
- [韩语](https://missing-semester-kr.github.io/)
- [蒙古语](https://missing-semester-mn.io)
- [波斯语](https://missing-semester-fa.github.io/)
- [葡萄牙语](https://missing-semester-pt.github.io/)
- [俄语](https://missing-semester-rus.github.io/)
- [塞尔维亚语](https://netboxify.com/missing-semester/)
- [西班牙语](https://missing-semester-esp.github.io/)
- [瑞典语](https://den-saknade-terminen.l10n.se/)
- [泰语](https://missing-semester-th.github.io/)
- [土耳其语](https://missing-semester-tr.github.io/)
- [越南语](https://missing-semester-vn.github.io/)

注意：以上均为外部社区翻译链接，我们并未对这些翻译版本进行审核。

如果你为本课程笔记制作了翻译版本，请提交一个 [pull request](https://github.com/missing-semester/missing-semester/pulls)，我们将把它添加到列表中！

## 致谢

{% comment %}
2026 acks; previous years' acks are on their respective pages
{% endcomment %}

感谢 Elaine Mello 和 [MIT Open Learning](https://openlearning.mit.edu/) 使得我们得以录制讲座视频。感谢 Luis Turino / [SIPB](https://sipb.mit.edu/) 作为 [SIPB IAP 2026](https://sipb.mit.edu/iap/) 的一部分对本课程的支持。

---

<div class="small center">
<p><a href="https://github.com/missing-semester/missing-semester">源代码</a>。</p>
<p>本作品采用 CC BY-NC-SA 许可证发布。</p>
<p>参见<a href="/license/">此处</a>了解贡献和翻译指南。</p>
</div>