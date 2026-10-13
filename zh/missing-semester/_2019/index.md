---
layout: page
title: "2019 课程讲座"
description: >
  Missing Semester 课程讲义和录像，MIT IAP 2019。
permalink: /2019/
phony: true
---

{% assign lecture_date = site['2019'] | group_by: 'date' | sort: 'name' %}
{% for date in lecture_date %}
  {% if date.name == "" %}{% continue %}{% endif %}
  <h2>{{ date.name | date: '%A, %-m/%-d' }}</h2>
  {% assign lectures = date.items | sort: 'order' %}
  <ul>
  {% for lecture in lectures %}
    {% if lecture.phony != true %}
      <li>
        <a href="{{ lecture.url }}">{{ lecture.title }}</a>
      </li>
    {% endif %}
  {% endfor %}
  </ul>
{% endfor %}

# 其他平台的分享

我们也在 MIT 之外分享了这门课程，希望更多人能够从中受益。你可以在以下平台找到相关的帖子和讨论：

- [Hacker News](https://news.ycombinator.com/item?id=19078281)
- [Lobsters](https://lobste.rs/s/h6157x/mit_hacker_tools_lecture_series_on)
- [r/learnprogramming](https://www.reddit.com/r/learnprogramming/comments/an42uu/mit_hacker_tools_a_lecture_series_on_programmer/)
- [r/programming](https://www.reddit.com/r/programming/comments/an3xki/mit_hacker_tools_a_lecture_series_on_programmer/)
- [Twitter](https://twitter.com/Jonhoo/status/1091896192332693504)
- [YouTube](https://www.youtube.com/playlist?list=PLyzOVJj3bHQuiujH1lpn8cA9dsyulbYRv)

# 致谢

本课程作为 [SIPB IAP 2019](https://sipb.mit.edu/iap/2019/) 的一部分讲授，并得到了 [SIPB](https://sipb.mit.edu/) 和 [MIT EECS](https://www.eecs.mit.edu/) 的共同赞助。