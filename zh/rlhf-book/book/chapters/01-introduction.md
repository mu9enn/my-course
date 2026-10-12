<!--
  Copyright (c) 2025-2026 Nathan Lambert.
  Licensed under CC BY-NC-SA 4.0:
  https://creativecommons.org/licenses/by-nc-sa/4.0/
  Full license: https://github.com/natolambert/rlhf-book/blob/main/LICENSE-CHAPTERS
-->
---
prev-chapter: "首页"
prev-url: "https://rlhfbook.com/"
page-title: 简介
search-title: "第一章：简介"
meta-description: "从第一性原理介绍 RLHF，它在语言模型中改变了什么，以及它是如何成为现代后训练的一部分的。"
next-chapter: "RLHF 简史"
next-url: "02-related-works"
lectures:
  - video: "https://www.youtube.com/watch?v=MMDNaeIFVy8&list=PLL1tdVxB1CpVpEtMHxwuR4uI4Lxjw00_y&index=2"
    label: "第 0 讲：先修知识"
  - video: "https://www.youtube.com/watch?v=o6l6tJQgUg4&list=PLL1tdVxB1CpVpEtMHxwuR4uI4Lxjw00_y&index=2"
    label: "第 1 讲：概述（第一至第三章）"
---

# 简介

基于人类反馈的强化学习（Reinforcement Learning from Human Feedback，简称 RLHF）是一种将人类信息融入人工智能系统的技术。

RLHF 最初作为一种方法来求解那些难以精确指定的问题而诞生。对于直接面向人类使用的系统，这类问题无处不在——因为个人的偏好往往是难以用语言表达的。这一问题覆盖所有内容领域，以及人与数字系统交互的方方面面。

RLHF 早期的应用往往集中在控制问题和其他强化学习（Reinforcement Learning，简称 RL）的传统领域，其目标是通过优化特定行为来完成任务。

整个 RLHF 领域起步时的核心问题是："我们能否仅凭最基础的偏好信号来引导优化过程，从而解决困难的问题？"

RLHF 因 ChatGPT 的发布以及随后大语言模型（Large Language Models，简称 LLMs）和其他基础模型的快速发展而广为人知。

## RLHF 三步走

RLHF 的基本流水线包含三个步骤。

**第一步**：训练一个能够响应用户提问的语言模型（参见第四章）。

**第二步**：收集人类偏好数据，用于训练一个反映人类偏好的奖励模型（参见第五章）。

**第三步**：使用选定的 RL 优化器，通过采样模型生成结果并根据奖励模型进行评分，来优化语言模型（参见第三和第六章）。

本书将对上述每个步骤中的关键决策和基本实现示例进行详细说明。

RLHF 已成功应用于许多领域，随着技术日渐成熟，其复杂度也在不断提升。RLHF 的早期突破性实验被应用于深度强化学习 [@christiano2017deep]、文本摘要 [@stiennon2020learning]、指令跟随 [@ouyang2022training]、从网页信息中解析内容以回答问题 [@nakano2021webgpt]，以及"对齐"（alignment）[@bai2022training]。

早期 RLHF 的菜谱式方法总结如下（见 @fig:rlhf-basic）。

![早期三步 RLHF 流程示意图：监督微调（SFT）→ 奖励模型 → 优化](images/rlhf-basic.png){#fig:rlhf-basic}

在现代语言模型训练中，RLHF 只是**后训练**（Post-Training）的一个组成部分。

后训练是一整套更完整的技术和最佳实践，旨在让语言模型对下游任务更加有用 [@lambert2024t]。后训练可以总结为一个多阶段训练过程，使用三种优化方法：

1. **指令 / 监督微调**（Instruction Fine-Tuning / Supervised Fine-Tuning，IFT/SFT）：教会模型输出格式，并形成指令跟随能力的基础。这主要是学习语言中的*特征*。
2. **偏好微调**（Preference Fine-Tuning，PreFT）：通过 RLHF 及相关方法对齐人类偏好（同时也能获得一小段能力上的提升）。这主要是关于语言的*风格*以及难以量化的微妙人类偏好。
3. **可验证奖励强化学习**（Reinforcement Learning with Verifiable Rewards，RLVR）：最新类型的后训练，通过更多的 RL 训练来提升可验证领域上的性能。

RLHF 存在于并主导了第二个领域——**偏好微调**。这一领域比指令微调更为复杂，因为它通常涉及真实目标的代理奖励模型以及更嘈杂的数据。与此同时，RLHF 也远比语言模型中另一种热门的 RL 方法——可验证奖励强化学习（RLVR）——更为成熟。正因如此，本书聚焦于偏好学习；但要全面理解 RLHF 的角色，也必须使用这些其他训练阶段，因此它们在本书中也有详细的解释。

在审视我们用于打造广泛使用模型的各类方法和注意力分布时，RLHF 通俗地说 *正是* 导致现代后训练出现的原因。

RLHF 正是让 ChatGPT 获得巨大成功的关键技术——因此 2023 年初，RLHF 几乎囊括了整个后训练领域的大部分兴趣。

如今，RLHF 只是后训练的一部分。因此，本书将追溯为何 RLHF 在早期获得如此多的关注，以及哪些其他方法随之兴起并与其互补。

训练语言模型是一个极其复杂的过程，往往需要数十到上百人的大型技术团队，以及数百万美元的数据和算力成本。本书服务于三个目的，帮助读者理解 RLHF 及相关方法如何被用来打造领先的模型：

首先，本书将大型科技公司内部往往不公开的尖端研究提炼为清晰的专题和权衡取舍，让读者能够理解模型是如何被造出来的。

其次，本书将让读者能搭建基本的代码示例，亲自动手对这些模型进行微调。

最后，除了教授 RLHF 的技术，本书还旨在提炼出 *为什么* RLHF 对现代 AI 模型至关重要的直觉。

由于 RLHF 的复杂性以及最前沿的方法往往复杂到无法独自完成，本书侧重于让读者拥有从事相关工作和启动研究项目所需的工具。其他人则可以单纯地、精确地理解这种在全球范围内引发无数讨论的技术的内在机制。

为特定需求提供一份精确的 RLHF 操作手册是不可能的——否则也不会有大量公司提供价值数百万美元的 RLHF 训练和相关方法服务。然而，AI 系统的快速进步意味着，掌握了这些知识的读者将能够越来越多地独立完成自己的训练任务。

## RLHF 做了什么？

围绕 RLHF 最大的问题——同时也是至今仍然难以回答的问题——是"RLHF 训练为模型带来了什么？"

近年来，语言模型已经从基准测试范围内的学术研究实验转变为一种通用技术。RLHF 正是这一转变的核心。

首先，让我们来看看一个经过自回归预训练的语言模型会如何回答一个查询。

一个强大的基座模型 Llama 3.1 405B Base，在看到提示 "The president of the united states in 2006 was" 后会续写如下：

> **Response**: George W. Bush, the governor of Florida in 2006 was Jeb Bush, and John McCain was an Arizona senator in 2006 - who later lost to obama.
> September 1 -- U.S. President Bush signs an executive order to provide more options for faith-based organizations when delivering social services that are paid for with federal funds.
> January 1 -- The current deadline set by United States Congress in the Unlawful Internet Gambling Enforcement Act, aka UIGEA.
> search: Amendments to the 1961 International Convention for the Protection of New Varieties of Plants require plant breeders’ rights include farmer’s privilege.
> 2009 was a common year starting on Thursday of the Gregorian calendar, the 2009th year of the Common Era (ce) and Anno Domini (ad) designations, the 9th year of the 3rd millennium, the 9th year of the 21st century, and the 10th and last year of the 2000s decade.

很明显，这个模型只是在补全句子并加上其他常见的互联网元数据。

相比之下，经过 RLHF（及其他后训练手段）训练的模型会用截然不同的方式回答这个问题。用同样的提示 "The president of the united states in 2006 was" 来询问 Tülu 3 405B，它的回答简明扼要：

> **Response**: George W. Bush was the president of the United States in 2006. He served two terms in office, from January 20, 2001, to January 20, 2009.

这种风格的转变源于本书所描述的后训练方法。

理解 RLHF 运作方式最有力的视角，是去思考*风格*（style）如何作用于你与语言模型的交互。

信息呈现的风格（与语气或格式密切相关）对其被学习的方式至关重要。"风格"一词通常用来描述模型的表现方式。为了理解差异，请看以下两个对同一问题的示例回答：

> **User**: Help, I have to give a presentation tomorrow and I’m panicking.

一种生硬、缺乏共情的风格：

> **Response**: You’ll be fine. Practice your slides a few times, get some sleep, and stop overthinking it. Just present what you know and move on.

一种更温暖、更具支持性的风格：

> **Response**: That sounds really stressful, and it’s a normal reaction. If you can, do one quick practice run now, pick the one or two points you most want people to remember, and then give yourself permission to rest—being clear and calm tomorrow will matter more than cramming tonight.

另一方面，**格式**（format）指的是答案的结构方式。

现代语言模型以大量使用 Markdown 格式而闻名——包括列表、换行和表情符号。来看两个对以下问题的截然不同的回答：

> **User**: How can I improve my sleep quality?

来自早期语言模型的简洁回答：

> **Response**: Try to go to bed at the same time each night, avoid caffeine late in the day, and keep your bedroom quiet and dark.

或者说更丰富、更结构化的回答：

> **Response**: Better sleep, in practice
> 
> **Goal**: make your schedule predictable and your environment boring enough that your brain gives up.
> 
> **Tonight (quick wins)**:
>
> 1. Dim lights for the last hour before bed.
> 2. No caffeine after lunch; keep alcohol minimal.
> 3. If you’re stuck awake, get up and do something quiet until sleepy again.
> 
> **Daily basics (most impact)**:
>
> - Same wake time (even weekends) --> anchors your body clock.
> - Morning light for 5-10 minutes --> helps set circadian rhythm.
> - Cool, dark room (fan/eye mask) --> easier to stay asleep.
> 
> **If you want a simple rule**:
> `wake time fixed + caffeine cutoff + wind-down routine`
> 
> If sleep problems are persistent or severe, it can be worth talking with a clinician—many issues are very treatable.

指令微调可以让模型以问答格式可靠地给出回答，而 RLHF 则将这些回答打磨成我们现在对语言模型所期望的那种可靠、温暖、引人入胜的回答。

现代研究已确立 RLHF 为一种通用方法，可以将微妙的风格和相关行为特征整合到模型中。RLHF 实用性的早期经典例子之一是在安全领域的应用 [@dai2023safe] [@bai2022training]，RLHF 使模型在各种数据集上都能同时做到有用且无害。

与其他后训练技术（如指令微调）相比，RLHF 在跨领域泛化方面表现好得多 [@kirk2023understanding] [@chu2025sft]——这有助于创建有效的通用模型。

从直觉上看，这一点体现在优化技术的使用方式上。

指令微调训练模型在上下文文本接近其见过的示例时预测下一个 token。它优化模型使其更频繁地在文本中输出特定特征。这是一种**逐 token** 的更新。

而 RLHF 则在**回答级别**上调整整体完成结果，而非仅仅关注下一个 token。此外，它告诉模型什么样的回答 *更好*，而不是给它一个具体应该学习的回答。RLHF 还向模型展示了它应该避免的回答类型，即负反馈。

实现这一目标的训练通常被称为 *对比损失*（contrastive loss）函数——即损失值通过两个或多个示例之间的比较来计算，而非从每个示例独立计算。这一术语在本书中反复出现。

这种灵活性虽是 RLHF 的一大优势，但也带来了实现上的挑战。这些挑战主要集中在 *如何控制优化过程*。正如本书后续将介绍的，实现 RLHF 通常需要训练一个奖励模型，但最佳实践尚未完全确立，且高度依赖具体应用领域。因此，优化过程本身容易出现 *过度优化*（over-optimization），因为我们的奖励信号充其量只是一个代理目标，需要正则化来约束。

在以上限制条件下，有效的 RLHF 需要一个良好的起点——因此 RLHF 不能单独解决所有问题，需要透过更广阔的后训练视角来对待。

鉴于这种复杂性，实现 RLHF 的成本远高于简单的指令微调，还可能带来一些意想不到的挑战，例如长度偏见（length bias）[@singhal2023long] [@park2024disentangling]。对于追求绝对性能的模型训练工作，RLHF 已被公认为实现强大微调模型的关键环节——尽管它在算力、数据成本和时间上都需要更高的投入。

在 ChatGPT 发布后的 RLHF 早期历史中，有许多研究论文展示了通过有限指令微调来近似解决 RLHF 问题的方案。但随着文献的日益成熟，人们一次又一次地反复证明：RLHF 及相关方法是模型性能的核心阶段，无法轻易舍弃。

## RLHF 菜谱的走读

为了给全书奠定基础，有必要在不使用那些在尚未建立基本直觉之前难以理解的技术术语的情况下，了解"做 RLHF"具体是什么样子的——以最小的示例来看。

本节跟随 OpenAI 在 2022 年通过 InstructGPT 模型所确立的、被描述为经典三步走的 RLHF 菜谱 [@ouyang2022training]。

这个流程的第一步是将模型从一个完成文本的基座模型转变为一个能够在问答格式下运行的指令跟随模型。

这一转变通过在精心制作的一组数据点上使用与预训练相同的下一个 token 预测损失函数来完成——但在这组数据中，模型*仅*看到问答格式的数据。在展示这些高质量的回答后，当模型被特定的 token 序列提示时，它就会知道自己应当以更为明确的助手身份来回答任何查询。

有了*模型应该如何回答的形态*这一基础，接下来的两个步骤协作起来提升回答的整体质量。这两个步骤共同构建了一个问题框架，让我们可以使用强化学习来更新模型，使其变得更有用。

这两个步骤中的第一步是训练一个捕获人类偏好的奖励模型。

要将强化学习应用于一个问题，你需要一个能指示质量的奖励函数。奖励模型的目标是创建一个标量信号，随后可以用 RL 对其进行优化。在实践中，这涉及在一个包含文本片段之间偏好关系的微调数据集上微调一个语言模型（通常是上一步中相同的指令微调模型）。

这个数据集通过多种提示（prompts）、模型完成结果和标注者来收集，力求捕捉一个关于"语言模型什么样的回答更好"的稳健信号。奖励模型学会了文本中哪些特征优于其他特征——因此当它在推理时（以及在 RL 过程中作为奖励信号）使用时，可以对任意输入文本打分以判断其好坏。

有了这两个组件——一个问答模型和一个奖励模型——我们便集齐了所有零件，可以真正地开始基于人类反馈的强化学习（RLHF）。

实际的 RLHF 阶段按如下方式进行：选取一些代表模型应当擅长的任务的提示，生成大量的完成结果，让奖励模型对它们进行排名，然后使用 RL 来弄清楚如何修改模型以使其变得更好。

基本的原语是：强化学习接收到关于哪些动作是好的信号——以语言模型生成的 token 形式——并推导出将不同动作归因于模型中不同参数的更新规则。

最终的 RLHF 阶段调整参数，使好的 token 更可能出现，并且以迭代的方式进行，同时保持初始模型的一般能力。

RL 完成且性能趋于饱和之后，这通常就是最终交付给用户的模型。

全书将涵盖多种如何实施 RLHF 的菜谱，以及构成更广泛后训练工具箱的其他相关优化方法。所有这些方法都是为了应对语言模型面临的更具挑战性的问题而出现的，并且为了使原始 RLHF 方法的优势更加强大。

## 后训练直觉

我们已经确认：RLHF 具体以及后训练一般地来说，对最新模型的性能及其如何改变模型的输出至关重要，但我们尚不清楚 *为什么* RLHF 有效。

这里有一个简单的类比，来解释为什么在任何基座模型之上都能通过后训练在基准测试上获得如此多的提升。

我一直在用**提取解释理论**（Elicitation Interpretation of Post-Training）来描述后训练的潜力——我们所做的全部事情，就是通过放大基座模型中有价值的行为来提取潜力。

为了让这个类比成立，我们做一个类比：将基座模型——即从大规模、下一个 token 预测的预训练中出来的语言模型——与构建复杂系统中的其他基础组件进行类比。我们以汽车底盘作为例子，底盘定义了可以在其上构建一个汽车的空间。

考虑一级方程式赛车（Formula 1，简称 F1）：大多数车队每年都会以全新的底盘和引擎起步。然后他们花一整年的时间进行空气动力学和系统改进（当然，这是一个轻微的简化），从而显著改善车辆的性能。最好的 F1 车队在赛季内的改进幅度远大于底盘与底盘之间的差异。

后训练也是如此：当人们越来越了解一个静态基座模型的癖性和倾向时，可以从中提取大量的性能。最好的后训练团队能在极短的时间内提取大量的性能。这组技术包括了接近和预训练结束之后的一切：如"中期训练"（annealing 退火 / 高质量预训练末尾网页数据）、指令微调、RLVR、偏好微调等。一个很好的例子是 Allen Institute for AI 的完全开源的小规模混合专家（Mixture-of-Experts，MoE）模型 OLMoE Instruct 从第一版到第二版的变更。第一版模型于 2024 年秋季发布 [@muennighoff2024olmoe]，而第二版仅更新了后训练部分，在大部分预训练未变动的情况下，流行基准测试上的平均评估分数从 35 提升到了 48 [@ai2_olmoe_ios_2025]。

其核心思想是：基座模型内部已经蕴含了大量的智能和能力，但由于它们只能以下一个 token 预测的方式回答，而不能以问答格式回答，因此需要围绕它们进行大量工作——通过后训练——才能制作出优秀的最终模型。

那么，当你看看 2025 年 2 月发布的 OpenAI 的 GPT-4.5 模型时——它由于基座模型过大而无法向数百万用户提供服务，因此在消费级产品上基本失败——你可以将其视为一个更为动态和令人兴奋的基础，供 OpenAI 在此基础上构建。

有了这种直觉，基座模型决定了最终模型绝大部分的潜力，而后训练的工作就是将这些潜力全部培育出来。

我将这种直觉描述为后训练的提取理论（Elicitation Theory of Post-Training）。

这一理论与以下现实相契合：用户看到的绝大多数增益来自后训练——因为它暗示，在互联网上预训练的模型中包含的潜在能力比我们可以单纯通过教导模型（比如在早期后训练阶段反复注入某些狭窄样本，即仅做指令微调）所达到的更多。

后训练的挑战在于：在从预训练中提取所有知识和智能的同时，将模型从下一个 token 预测重新塑造为对话式问答。

与这一理论相关的想法是"浅层对齐假说"（Superficial Alignment Hypothesis），该假说在 LIMA: Less is More for Alignment 一文中被提出 [@zhou2023lima]。这篇文章在重要直觉上有一些正确的认识，但在全局层面上理由有误。其作者写道：

> 模型的知识与能力几乎全部在预训练期间习得，而对齐则教会它在与用户交互时应使用哪些子分布的格式。如果这个假说成立，且对齐主要关乎学习风格，那么浅层对齐假说的一个推论是：人们可以用相当少量样本来充分微调一个预训练语言模型。

深度学习的所有成功本应教会你：扩大数据规模对性能至关重要。这里的主要区别在于，作者讨论的是对齐和风格——这是当时学术界后训练的关注点。用几千条样本来进行指令微调，你可以大幅度改变一个模型并提升一组狭义评估上的表现，例如 AlpacaEval、MT-Bench、Arena（前身为 Chatbot Arena，一个用户面对面比较匿名模型回答的平台）等。但这些并不总能转化为更棘手的能力——这就是为什么 Meta 不会仅凭这些数据来训练其 Llama Chat 模型。学术成果有其可借鉴之处，但若你想理解技术发展的宏观图景，则需要谨慎解读。

这篇文章想表明的是：你可以通过少量样本来大幅改变模型。这是我们所知的，并且对新型模型的短期适配非常重要——但它们在性能方面的论证给一般读者留下了错误的启示。

如果我们改变数据，对模型性能和行为的提升幅度可能更大，但这远非"浅层"。如今的基座语言模型（无后训练）可以在一些数学问题上使用强化学习进行训练，学会输出完整的链式思维（chain-of-thought）推理，然后在整套推理评估（如 BigBenchHard、Zebra Logic、AIME 等）上获得更高的分数。

浅层对齐假说是错误的——那些认为 RLHF 和后训练"只是为了 vibes"（感觉而已）的人同样也是错误的。这是 2023 年整个领域必须克服的一课（尽管许多 AI 观察家至今仍根深蒂固于此）。

后训练早已超越了这一阶段，我们正在认识到：模型的风格是在行为之上运作的——例如现在流行的长链式思维。

随着 AI 社区将后训练进一步推向智能体（agentic）和推理（reasoning）模型时代，浅层对齐假说的破败程度进一步加剧。

RL 方法正逐渐成为训练前沿语言模型所需算力的越来越大的份额。自 2024 年秋季我们在 Tülu 3 工作中提出可验证奖励强化学习（RLVR）以来，仅过了很短的时间 [@lambert2024t]，后训练所使用的算力规模就已急剧增长。以推广 RLVR 而闻名的 DeepSeek R1 在后训练中的整体算力使用仅约占 5%——R1 的 RL 训练使用了 147K H800 GPU 小时 [@guo2025deepseek]，而底层 DeepSeek V3 基座模型的预训练使用了 2.8M GPU 小时 [@deepseekai2025deepseekv3technicalreport]。

截至 2026 年，研究扩展 RL 核心方法的相关研究表明，单个消融实验可能需要 10-100K GPU 小时 [@khatri2025art]，相当于 Olmo 3.1 Think 32B（2025 年 11 月发布）在 RL 阶段使用的算力——该模型在 200 块 GPU 上训练了 4 周 [@teamolmo2025olmo3]。

截至 2026 年，扩展后训练的科学仍处于非常早期的阶段，正在从语言模型预训练中采纳思想和方法，并将它们应用到这一新领域中。因此确切使用的 GPU 小时数会发生变化，但后训练算力增加的趋势将持续下去。

总而言之，后训练的提取理论很可能只有在相对于计算密集的前沿模型而言应用更轻量级后训练菜谱（即用于专业化一个模型）时，才会成为正确的理解方式。

## 我们如何走到这里

为什么这本书现在有意义？未来会发生多大的变化？

后训练——即从原始预训练语言模型中提取强大行为的技艺——自 ChatGPT 发布、重新唤起人们对 RLHF 的兴趣以来，经历了多个阶段和情绪起伏。

在 Alpaca [@alpaca]、Vicuna [@vicuna2023]、Koala [@koala_blogpost_2023] 和 Dolly [@DatabricksBlog2023DollyV1] 的时代，使用有限的人类数据点加上 Self-Instruct 风格的扩展合成数据来微调原始 LLaMA，以获得与 ChatGPT 类似的行为。这些早期模型的基准测试完全依赖于 vibes（以及人类评估），因为我们都被这些小型模型能够在跨领域表现出如此令人印象深刻的行为这一事实深深吸引。

那是有充分理由的兴奋。

开源后训练比闭源方案走得更远、发布更多的模型、引发更大的声浪。

各大公司都在紧急行动——例如 DeepMind 与 Google Brain 合并或新建实验室——并需要时间来跟进。开源菜谱经历了几个爆发然后又落后的阶段。

Alpaca 等论文之后的时代——开源菜谱的第一次滞后——是由对基于人类反馈的强化学习（RLHF）的怀疑和质疑所定义的，而 RLHF 正是 OpenAI 所强调的对首个 ChatGPT 成功至关重要的技术。

许多公司怀疑自己是否真的需要去做 RLHF。

一句常见的话——"指令微调就足以完成对齐"——当时如此流行，以至于即便面对明显的反证，它今天仍然有一定分量。

这种对 RLHF 的怀疑持续了很长时间，尤其在开源领域，因为团队负担不起 10 万美元到 100 万美元级别的数据预算。

那些早期拥抱 RLHF 的公司最终赢得了局面。

Anthropic 在 2022 年全年发表了大量关于 RLHF 的研究，如今可以说拥有最好的后训练 [@askell2021general] [@bai2022training] [@bai2022constitutional]。

开源团队难以复现甚至不知道基本闭源技术与领先闭源模型之间的差距，是一个常见的主题。

开源对齐方法和后训练的第一个转变是直接偏好优化（Direct Preference Optimization，DPO）的故事 [@rafailov2024direct]——它表明，通过直接在成对偏好数据上取梯度步，可以用比 RLHF 更少的组件来解决相同的优化问题。

DPO 论文于 2023 年 5 月发布，但在 2023 年秋季之前，并没有任何清晰重要的模型使用它来训练。

随着少数突破性的 DPO 模型的发布——这一切都取决于找到更好的、更低的学习率——情况发生了变化。Zephyr-Beta [@tunstall2023zephyr]、Tülu 2 [@ivison2023camels] 以及许多其他模型表明，后训练的 DPO 时代已经到来。Chris Manning 甚至亲口向我表达了"拯救了 DPO"的谢意。

自 2023 年末以来，偏好微调已成为发布一个好模型必须满足的最低门槛。

DPO 时代在 2024 年继续，以算法的不断变体形式出现，但我们又陷入了开源菜谱的又一次停滞。开源后训练菜谱已经在知识和资源的可用程度上达到了饱和。

在 Zephyr 和 Tülu 2 发布一年后，那个突破性的数据集——UltraFeedback——可以说在开源菜谱的偏好微调中仍然是最先进的 [@cui2023ultrafeedback]。

与此同时，Llama 3.1 [@dubey2024llama] 和 Nemotron 4 340B [@adler2024nemotron] 的报告给了我们实质性的暗示：大规模后训练远比学术文献所触及的更为复杂且影响深远。

闭源实验室在做全栈后训练——一个包含指令微调、RLHF、提示设计等的大型多阶段过程——而学术论文只是在表面徘徊。Tülu 3 代表了一项全面、开源的努力，旨在构建未来学术后训练研究的基础 [@lambert2024t]。

后训练是一个复杂的过程，涉及上述训练目标以不同顺序应用以针对特定能力。

本书旨在提供一个理解所有这些技术的平台，随着领域成熟，关于如何交错使用它们的最佳实践也将涌现。

后训练目前的主要创新领域是可验证奖励强化学习（RLVR）、推理训练一般地以及相关想法。

这些更新的方法大量构建在 RLHF 的基础设施和思想之上，但进化速度远快于 RLHF。

本书旨在记录 RLHF 在快速变化的初期之后的第一批稳定文献。

## 本书范围

本书力求涵盖执行经典 RLHF 实现的每个核心步骤。

本书不会涵盖所有组件的历史或最新研究方法，而只关注那些被反复证明会出现的技术、问题和权衡。

### 章节概览

本书包含以下章节：

#### 入门

贯穿全书有用的参考材料和背景。

1. **简介**：RLHF 概览以及本书所提供的内容。
2. **RLHF 简史**：RLHF 技术历史中的关键模型和论文。
3. **训练概览**：RLHF 的训练目标如何设计以及如何理解其基本原理。

#### 核心训练流水线

用于优化语言模型以使其对齐人类偏好的技术集。

4. **指令微调**：将语言模型适配为问答格式。
5. **奖励建模**：从偏好数据中训练奖励模型，作为 RL 训练的优化目标（或用于数据筛选）。
6. **强化学习**：贯穿整个 RLHF 用于优化奖励模型（及其他信号）的核心 RL 技术。
7. **推理与推理时扩展**：新 RL 训练方法在推理时扩展中的作用，相对于后训练和 RLHF 的关系。
8. **直接对齐算法**：直接从成对偏好数据优化 RLHF 目标、而非先学习奖励模型的算法。
9. **拒绝采样**：一种使用奖励模型配合指令微调来对齐模型的基本技术。

#### 数据与偏好

为 RLHF 提供燃料的数据的背景，以及该数据试图解决的全局性问题。

10. **偏好的本质**：为什么需要人类偏好数据来支撑和理解 RLHF。
11. **偏好数据**：如何为 RLHF 收集偏好数据。
12. **合成数据**：从人类数据转向合成数据的历程，AI 反馈如何工作，以及如何从其他模型中进行蒸馏。
13. **工具使用和函数调用**：训练模型在输出中调用函数或工具的基础。

#### 实践考虑

实施和评估 RLHF 的基本问题和讨论。

14. **过度优化**：定性地观察为什么 RLHF 会出错，以及为什么在奖励模型中使用软优化目标时过度优化是不可避免的。
15. **正则化**：将这些优化工具约束到参数空间的有效区域的工具。
16. **评估**：评估（和提示）在语言模型中不断演进的角色。
17. **塑造模型人格与产品**：随着主要 AI 实验室用 RLHF 微妙地将模型与它们的产品相匹配，RLHF 的适用性正在发生怎样的转变。

#### 附录

定义和扩展讨论的参考资料。

- **附录 A — 定义**：RL、语言建模以及本书利用的其他 ML 技术的数学定义。
- **附录 B — 不止于"风格"**：由于风格在信息传递中扮演的关键角色，RLHF 在改善模型用户体验方面的作用经常被低估。

### 目标读者

本书面向具有语言建模、强化学习和一般机器学习入门经验的读者。

本书不会对所有技术提供详尽文档，而只提供那些对理解 RLHF 至关重要的内容。

### 如何使用本书

本书很大程度上是因为 RLHF 工作流中的重要主题缺乏权威参考资料而被创建的。

鉴于 LLM 整体发展的速度，加上收集和使用人类数据的复杂性质，RLHF 是一个格外学术化的领域——公开发表的结果往往噪声很大，且难以在多种设置下复现。

为了培养扎实的直觉，鼓励读者阅读每个主题的多个论文，而不是将任何一个结果视为定论。

为此，本书包含大量学术风格的引用，指向每个声明的权威参考资料。

本书的贡献在于为你提供尝试玩具实现或深入研究文献所需的最小知识。

这是一本 *不是* 综合性教科书的书——而是一本用于回顾和快速入门的小书。

本书的纸质版于 2026 年 7 月由 Manning 出版，网页版本则持续收集小幅改进和勘误修正。如果你发现任何错别字或重要遗漏，请在 [GitHub](https://github.com/natolambert/rlhf-book) 上贡献修复或建议。

### 关于作者

Nathan Lambert 博士是一位研究者和作家，专注于构建语言模型的开放科学。他通过机器人学博士论文，并在 ChatGPT 发布后不久组建 RLHF 团队，从而进入这一领域。

他在 Allen Institute for AI（Ai2）和 Hugging Face 工作期间，发布了许多使用 RLHF 训练的模型、后续数据集和训练代码库。

其中包括 [Zephyr-Beta](https://huggingface.co/HuggingFaceH4/zephyr-7b-beta)、[Tülu 2](https://huggingface.co/allenai/tulu-2-dpo-70b)、[OLMo](https://huggingface.co/allenai/OLMo-7B-Instruct)、[TRL](https://github.com/huggingface/trl)、[Open Instruct](https://github.com/allenai/open-instruct) 等等。

他撰写了大量关于 RLHF 的内容，包括[多篇博客文章](https://www.interconnects.ai/t/rlhf)和[学术论文](https://scholar.google.com/citations?hl=en&user=O4jW7BsAAAAJ&view_op=list_works&sortby=pubdate)。

## RLHF 的未来

随着对语言建模的投入，传统 RLHF 方法出现了许多变体。

通俗地说，RLHF 已与多种重叠的方法变得同义。

RLHF 是偏好微调（Preference Fine-Tuning，PreFT）技术的一个子集，其中包括直接对齐算法（参见第八章）——这些是 DPO 之后的方法类别，它们直接在偏好数据上取梯度步来解决偏好学习问题，而非学习一个中间奖励模型。

RLHF 是与语言模型"后训练"的快速进展最紧密相关的工具——后训练涵盖了在主要基于网页数据的大规模自回归训练之后的所有训练。

这本教材对 RLHF 及其直接相邻的方法（如指令微调和设置 RLHF 训练所需的其他实现细节）进行了广泛概述。

随着越来越多使用 RL 微调语言模型的成功案例出现——例如 OpenAI 的 o1 推理模型——RLHF 将被视为一座桥梁，它使进一步在大规模基座模型微调上投资 RL 方法成为可能。

与此同时，虽然短期内的关注点可能更集中在 RLHF 中的 RL 部分——作为最大化有价值任务性能的一种方式——但 RLHF 的核心在于它是研究现代 AI 所面临的宏大问题的一副透镜。

我们如何将人类价值观和目标的复杂性映射到日常生活中所使用的系统中？

本书希望成为对这些问题的数十年研究和经验的坚实基础。
