---
layout: page
title: "2026 课程"
description: >
  Missing Semester，MIT 2026 一月期课程讲义与视频。
permalink: /2026/
phony: true
---

<ul class="double-spaced">
  {% assign lectures = site['2026'] | sort: 'date' %}
  {% for lecture in lectures %}
    {% if lecture.phony != true %}
      <li>
        <strong>{{ lecture.date | date: '%-m/%-d' }}</strong>:
        {% if lecture.ready %}
          <a href="{{ lecture.url }}">{{ lecture.title }}</a>
        {% elsif lecture.noclass %}
          {{ lecture.title }} [无课堂]
        {% else %}
          {{ lecture.title }} [即将发布]
        {% endif %}
        {% if lecture.details %}
          <br>
          ({{ lecture.details }})
        {% endif %}
      </li>
    {% endif %}
  {% endfor %}
</ul>

课程的视频录制已上传至 [YouTube 播放列表](https://www.youtube.com/playlist?list=PLyzOVJj3bHQunmnnTXrNbZnBaCA-ieK4L)。

# 走出 MIT

我们也在这门课程发布到了 MIT 之外，希望其他人能从这些资源中受益。你可以在以下平台找到相关帖子和讨论：

- [Hacker News](https://news.ycombinator.com/item?id=47124171)
- [Lobsters](https://lobste.rs/s/q4ykw7/missing_semester_your_cs_education_2026)
- [r/learnprogramming](https://www.reddit.com/r/learnprogramming/comments/1r93yk6/the_missing_semester_of_your_cs_education_2026/)
- [X](https://x.com/anishathalye/status/2024521145777848588)
- [Bluesky](https://bsky.app/profile/jonhoo.eu/post/3mfa2bhyuj22i)
- [Mastodon](https://fosstodon.org/@jonhoo/116098318361854057)
- [LinkedIn](https://www.linkedin.com/posts/anishathalye_i-returned-to-mit-during-iap-january-term-activity-7430285026933522433-Ehr9)
- [YouTube](https://www.youtube.com/playlist?list=PLyzOVJj3bHQunmnnTXrNbZnBaCA-ieK4L)

# 致谢

感谢 Elaine Mello 和 [MIT Open Learning](https://openlearning.mit.edu/)，使得我们得以录制课程视频。感谢 Luis Turino 与 [SIPB](https://sipb.mit.edu/) 作为 [SIPB IAP 2026](https://sipb.mit.edu/iap/) 的一部分支持了本课程。

<!--
译者注：本文档为独立中文改编版本，非官方中文译本。原文版权归 Missing Semester 原作者所有，此处翻译仅供学习参考。
-->