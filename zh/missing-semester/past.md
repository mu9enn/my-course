---
layout: page
title: 往期课程
description: >
  查找 Missing Semester 所有往期课程。
---

{% comment %} pop to remove default "posts" collection {% endcomment %}
{% assign sorted_collections = site.collections | sort: 'label' | pop | reverse %}
<ul>
{% for collection in sorted_collections %}
    <li><a href="/{{ collection.label }}/">{{ collection.label }}</a></li>
{% endfor %}
</ul>

每年开设的课程都是完全自包含（self-contained）的，不依赖之前的内容。我们建议从最新的版本开始学习。每年的课程主题可能有所不同，因此我们继续保留并托管早期版本的课程笔记和录像。