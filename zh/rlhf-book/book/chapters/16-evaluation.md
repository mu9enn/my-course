<!--
  Copyright (c) 2025-2026 Nathan Lambert.
  Licensed under CC BY-NC-SA 4.0:
  https://creativecommons.org/licenses/by-nc-sa/4.0/
  Full license: https://github.com/natolambert/rlhf-book/blob/main/LICENSE-CHAPTERS
-->
---
prev-chapter: "Regularization"
prev-url: "15-regularization"
page-title: 评估
search-title: "第 16 章：评估"
meta-description: "用于衡量 RLHF、后训练、奖励模型、开放式生成和模型行为的评估方法。"
next-chapter: "Crafting Model Character and Products"
next-url: "17-product"
lectures:
  - video: "https://www.youtube.com/watch?v=dFafQmClYq4&list=PLL1tdVxB1CpVpEtMHxwuR4uI4Lxjw00_y&index=19"
    label: "第 12 讲：前沿模型评估的演进"
---

# 评估

**评估**（evaluation）是一套用于理解本书所述训练过程的质量与影响的技术。评估通常通过**基准测试**（benchmark，即 benchmark）来表达——例如常见的 MMLU、GPQA、SWE-bench、MATH 等——这些基准测试是离散的问答集合或评测环境，旨在测量模型的特定属性。评估方法本身在不断演进，因此我们在本章中梳理 RLHF 领域评估的几个关键发展阶段，并提炼出将延续到语言建模未来的常见主题。理解语言模型评估、尤其是后训练阶段评估的关键在于：当前流行的评估体系实际上是对主流训练最佳实践和目标的映射。虽然具有挑战性的评估能够推动语言模型进入新领域，但绝大多数评估的设计目标是为新模型构建有用的信号。

从某种意义上说，本章旨在呈现 RLHF 早期历史中一些典型评估体系的"速写"，帮助读者理解常见主题、具体细节和故障模式。

在 RLHF 和后训练领域，评估经历了几个显著的发展阶段：

1. **早期对话阶段（Early chat-phase）**：早期使用 RLHF 或偏好调优（preference tuning）训练的模型，其评估主要关注模型的对话性能，尤其是与 GPT-4 等已知强模型的对比。早期代表包括 MT-Bench [@zheng2023judging]、AlpacaEval [@dubois2024length] 和 Arena-Hard [@li2024crowdsourced]。这些基准测试用 LLM-as-a-judge（以大型语言模型担任评判者）替代了人类评估员——使用 GPT-4 等模型对回答打分——以经济的方式扩展人类评估标准（参见第 12 章）。这些模型的评估较为局限，如今这些基准已被归类为"对话"（chat）或"指令遵循"（instruction following）领域。

2. **多技能时代（Multi-skill era）**：随着时间推移，业界逐渐认识到 RLHF 不仅可以提升对话能力，还可以用于提升更多技能。例如，Tülu 评估套件包含了知识（MMLU [@hendrycks2020measuring]、PopQA [@mallen2023llm_memorization]、TruthfulQA [@lin2021truthfulqa]）、推理（BigBenchHard [@suzgun2022challenging]、DROP [@dua2019drop]）、数学（MATH [@hendrycksmath2021]、GSM8K [@cobbe2021gsm8k]）、代码（HumanEval [@chen2021codex]、HumanEval+ [@evalplus]）、指令遵循 [@zhou2023instructionfollowingevaluationlargelanguage] 和安全性（多个评估的综合）等任务。这反映了后训练被接受为一种超越安全和对话的多面解决方案。

3. **推理与工具（Reasoning & tools）**：当前后训练时代的特征是聚焦于具有挑战性的推理和工具使用问题。这包括更加困难的知识密集型任务，如 GPQA Diamond [@rein2023gpqa] 和 Humanity's Last Exam [@phan2025hle]；复杂的软件工程任务，如 SWE-Bench+ [@aleithan2024swebenchplus] 和 LiveCodeBench [@jain2024livecodebench]；以及以近年 AIME 竞赛为代表的挑战性数学问题。

除此之外，新领域还会不断涌现。随着 AI 逐渐成为一个工业化领域，评估的激励正在转变，并涉及多方利益相关者。自 ChatGPT 发布以来，出现了众多私人评估（如 Scale Leaderboard [@scale2024seal]）、社区驱动的评估（如 Chatbot Arena [@chiang2024chatbot]）以及第三方评估公司（如 Artificial Analysis 和 Epoch AI）。在本章的讨论中，我们将穿插说明这些评估是如何被实施和理解的。

## 提示格式

**提示**（prompting）语言模型本身是一个简单的操作，也是一种相当自然的行为，但它同时也是一门可以不断练习和打磨的手艺/艺术 [@schulhoff2024prompt]。**提示**（prompt）是向语言模型组织信息和上下文的方式。对于常见交互，提示相对简单；而对于高级场景，精心设计的提示往往决定了一个特定用例的成功或失败。

在评估场景下，提示技术会对模型表现产生重大影响。有些提示技巧——如下面讨论的格式设计——可以让模型表现从 60% 骤降至接近 0。同样，提示的改变也能帮助模型在训练中学得更好。通俗地说，巧妙地提示模型可以获得"未来模型"般的主观体验，解锁超出正常使用范围的性能。

不过，通过提示获得的性能提升通常小于改进数据或训练算法等核心领域，但在最终产品中仍可能产生实质性影响。更大的启示是：当训练一个强大、领先水平的模型时，更容易通过不当提示破坏其性能、导致表现断崖式下跌，而不是找到那一点点额外的性能提升。

用现代语言模型进行高质量提示，可能需要为模型准备一份完整的报告供其回答（通常包含数千个 token 的生成文本）。这种行为是许多关于语言模型表现如何被衡量和理解的变化所催生的。

### 少样本提示与对数概率评分

早期的语言模型仅作为智能补全（autocomplete）使用。为了让这些模型以更开放的方式运行，人们会向模型展示多个示例，然后给出一个不完整的短语作为提示。这被称为**少样本**（few-shot）或**上下文学习**（in-context learning）[@brown2020language]，当时尚未涉及指令微调（instruction tuning）或 RLHF。

在常见的评估场景中，少样本提示看起来像这样：

```text
# Few-Shot Prompt for a Question-Answering Task
You are a helpful assistant. Below are example interactions to guide your style:

### Example 1
User: "What is the capital of France?"
Assistant: "The capital of France is Paris."

### Example 2
User: "Who wrote the novel '1984'?"
Assistant: "George Orwell wrote '1984.'"

# Now continue the conversation using the same style.
User: "Can you explain what a neural network is?"
Assistant:
```

这里有多种评估回答的方式。如果我们考虑 MMLU 风格的题目——模型需要从多个选项中选择一个：

```text
# Few-Shot Prompt

Below are examples of MMLU-style questions and answers:

### Example 1
Q: A right triangle has legs of lengths 3 and 4. What is the length of its hypotenuse?
Choices:
(A) 5
(B) 6
(C) 7
(D) 8

Correct Answer: (A)

### Example 2
Q: Which of the following is the chemical symbol for Sodium?
Choices:
(A) Na
(B) S
(C) N
(D) Ca

Correct Answer: (A)

### Now answer the new question in the same style:

Q: Which theorem states that if a function f is continuous on a closed interval [a,b], then f must attain both a maximum and a minimum on that interval?
Choices:
(A) The Mean Value Theorem
(B) The Intermediate Value Theorem
(C) The Extreme Value Theorem
(D) Rolle's Theorem

Correct Answer:
```

让语言模型给出答案，可以采取两种路径：一种是基于某些采样参数生成 token，然后判断答案是否正确（A、B、C 或 D）——这种格式建议参见 [@robinson2023leveraging]；另一种是查看每个 token 的**对数概率**（log-probabilities），如果正确答案出现的概率更高，就将任务标记为正确。

让我们深入这些评估细节。前者在单次尝试中通常称为**精确匹配**（exact match），在聚合多个样本时则称为**多数投票**（majority voting）——对于测试功能正确性的代码评估，类似的指标是 pass@k；后一种方法称为**（条件）对数概率评分**（(conditional) log-likelihood scoring），其中条件就是提示本身。核心区别在于：从基础概率分布中采样会自然地引入随机性，而模型输出的对数概率则是静态的（忽略细微的数值差异）。

对数概率评分有两种潜在的实现方式：一是只看字母（A）的概率，二是看完整答案 "The Mean Value Theorem" 的概率。两种都是可接受的指标，但预测答案字母远比预测完整的多 token 答案概率简单得多。对数概率评分在后训练之前的预训练评估中更常见，因为那时的模型缺乏精确匹配所需的人机问答格式；而在后训练阶段，精确匹配是标准做法 [@teamolmo2025olmo3]。

精确匹配面临不同的问题——例如需要严格的格式后缀（如 `The answer is:`），或者使用正则表达式在生成的全文中检测答案（如查找 `(C)` 或答案字符串本身）。如果评估格式与模型的生成方式不匹配，分数会急剧下降。用语言模型做评估时，最好的情况是格式不是瓶颈，从而能够测试出模型的真实能力。实现格式无关的（format-agnostic）评估需要大量的努力和调优，在实践中相当罕见。

回到评估的历史。无论使用上面哪种设置，少样本提示面临的一个共同挑战是：模型不遵循格式时，回答会被计为错误。在设计评估域时，上下文中使用的示例数量通常作为一个设计参数，范围从 3 到 8 个或更多。

### 思维链提示（Chain-of-Thought Prompting）

在少样本提示的演进过程中，出现了为模型提供思维链（chain-of-thought）示例的想法。具体做法是在上下文示例中给出逐步推理过程，如下所示（后来被显式要求生成推理步骤的提示所取代）[@wei2022chain]：

```text
# standard prompting
Q: Roger has 5 tennis balls. He buys 2 more cans of tennis balls. Each can has 3 tennis balls. How many tennis balls does he have now?

A: The answer is 11.

Q: The cafeteria had 23 apples. If they used 20 to make lunch and bought 6 more, how many apples do they have?

A: The answer is ...

# chain-of-thought prompting
Q: Roger has 5 tennis balls. He buys 2 more cans of tennis balls. Each can has 3 tennis balls. How many tennis balls does he have now?

A: Roger started with 5 balls. 2 cans of 3 tennis balls each is 6 tennis balls. 5 + 6 = 11. The answer is 11.

Q: The cafeteria had 23 apples. If they used 20 to make lunch and bought 6 more, how many apples do they have?

A: The cafeteria had 23 apples originally. They...
```

### 零样本指令跟随（Zero-Shot Instruction Following）

随着时间推移，语言模型变得越来越强大，评估方式逐渐演进为**零样本**（zero-shot）评估，即所谓的"零样本学习"（zero-shot learners）[@wei2021finetuned]。FLAN 表明，在特定任务上微调的语言模型——作为现代指令微调的前置——能够泛化到它们没有接受过训练的零样本问题 [@wei2021finetuned]（T0 也给出了类似结果 [@sanh2021multitask]）。这是**指令微调**（instruction fine-tuning, IFT）的兴起——它是 RLHF 和后训练的重要前驱。

一个零样本问题看起来像这样：

```text
User: "What is the capital of France?"
Assistant:
```

从这里开始，2022 年的时间线开始纳入早期 RLHF 的关键工作，如 InstructGPT。伴随这些模型的核心能力和用例进一步转向更加开放的使用场景。随着使用方式变得更加开放，从模型中采样生成的评估变得越来越流行，因为它更贴近实际使用——从技术上说，这可以称为**基于生成的**（generation-based，精确匹配）评估，但它没有同样清晰的专有术语。在这一时期（ChatGPT 发布后的近年），RLHF 研究中仍在使用一些选择题评估，因为从一种评估方式过渡到通用做法需要相当长的时间（通常以年为单位）——例如，这类评估通过将温度设置为 0，然后采样字符 A、B、C 或 D 来完成。

### 推理时代的评估提示（Reasoning-Era Evaluation Prompts）

随着 2024 年底至 2025 年初推理模型（reasoning models）的崛起，模型行为的一个重要变化是在每次回答之前都会加上一个长篇幅的**思维链**（Chain-of-Thought, CoT）推理过程。这些模型不再需要被提示以 [@kojima2022large] 提出的经典短语 "think step by step"。

这一评估实践的下一个演进版本是基于生成的（精确匹配）评估，辅以思维链推理（因此几乎总是温度设置大于 0 以获得最佳表现）。

例如，在某些设置中，针对每个问题或类别，都有专门设计的提示，以帮助从模型中提取行为。Tülu 3 是一项早期的开创性论文，详细记录了在多项选择题上用于 CoT 回答的一些提示 [@lambert2024t]。以下是一个用于 MMLU 的提示示例——MMLU 是从单 token 答案采样过渡到长格式 CoT 加精确匹配答案检查的评估之一。

```text
Answer the following multiple-choice question by giving the correct answer letter in parentheses.
Provide CONCISE reasoning for the answer, and make sure to finish the response with "Therefore, the answer is (ANSWER_LETTER)" where (ANSWER_LETTER) is one of (A), (B), (C), (D), (E), etc.

Question: {question}
(A) {choice_A}
(B) {choice_B}
(C) ...

Answer the above question and REMEMBER to finish your response with the exact phrase "Therefore, the answer is (ANSWER_LETTER)" where (ANSWER_LETTER) is one of (A), (B), (C), (D), (E), etc.
```

尤其是当模型使用特殊格式来分隔思考 token 和答案 token 时，这对评估体系提出了最新的重大更新需求。评估正在转向：模型需要通过思维链提示以生成式方式做出回应。

### 智能体评估的复杂性

随着模型走向智能体（agent），评估范式正变得越来越复杂。系统提示（system prompt）和推理软件现在作为额外的一层进入评估——主要通过评估框架（harness）的中介软件，以及运行这些软件的底层基础设施。评估框架（harness）是一个循环，包含了管理上下文的提示和技能，如上下文压缩、工具调用、凭证管理等。在智能体评估中，模型通常需要在沙盒（sandbox）中运行——即具有明确定义的环境，包含特定信息（例如解决任务所需的文件）和规则，以使评估可复现（如特定的工具定义）。沙盒增加了运行模型的复杂度，因为你通常除了用于推理的 GPU 之外，还需要更多的 CPU。

有关更多信息，你可以参考 Florian Brand 的[这场演讲](https://www.youtube.com/watch?v=CGjuKIppZSs)、@fig:eval-components 中的系统图，或者阅读该时代最受欢迎的评估——Terminal-Bench 的原始版本 [@tbench2025] 和更难的 Terminal-Bench 2.0 [@tbench2026]。

![运行现代智能体评估的组件——每个方框都影响最终分数。图示改编自 Florian Brand 的演讲"Agent 时代的 LLM 基准测试"。](images/eval_components_tikz.png){#fig:eval-components .center data-dark-src="images/eval_components_tikz-dark.png"}

## 为什么许多外部评估比较不可靠

AI 公司在模型发布时给出的语言模型评估结果，只有在带有较大误差范围的前提下才能与其他新闻稿中的结果进行比较——也就是说，略微好一些或差一些应当被视为等价——因为各自内部用于评估的流程在模型之间没有统一控制，也没有明确公开。例如，在 Olmo 3 项目中，作者发现，在推理模型时代的大多数后训练评估中，当评估设置保持不变时，分数之间存在 0.25 到 1.5 个标准差的变化 [@teamolmo2025olmo3]——使用不同的提示或采样参数，也能导致分数的显著变化。

实验室在训练期间对评估进行"爬山"（hillclimb，即 incremental optimization），以使模型更加有用——传统上，他们会结合使用训练集、开发集（validation set）和保留的评估集（test set）。"爬山"是一个通俗术语，用来描述让模型在一系列目标基准测试上逐步变好的做法。对于社区用来比较领先模型的公共评估，我们无法得知哪些基准被用于训练、哪些被保留用于测试。

随着评估分数成为企业营销方案的核心组成部分，它们在内部的实现方式已经发生了漂移。据传，一些大型 AI 实验室会对 GSM8K 或 MATH 等重要评估使用"自定义提示"（custom prompts）。这类做法正在迅速演进。

语言模型评估堆栈之所以被视作营销工具，是因为评估结果没有一个可靠的"事实真相"来源。前沿实验室内部的情况是：评估套件被调优以适应其内部需求。当结果被公开时，我们得到的是实验室为其模型跑出的数字结果，但并不会公开该函数所有的输入配置。这些输入是非常敏感的超参数配置，它们在 OpenAI、Meta、Anthropic 和 Google 各不相同。即使是完全公开的评估标准也难以保证可复现性。专注于自身模型的评估，才是接近可重复评估技术的唯一途径。

营销背后有着良好的初衷，始自技术团队。

另一个在比较多实验室评估结果时造成困惑的例子是：**推理时扩展**（inference-time scaling）被加入到了评估比较中。推理时扩展表明：模型可以通过在推理阶段使用更多 token 来提升性能。因此，以推理总 token 数为基准来控制评估分数很重要，但这尚未成为普遍做法。

在后训练中，数据格式的不同会导致模型在不同评估格式下出现显著差异。例如，两个流行的开源数学数据集 NuminaMath [@li2024numinamath] 和 MetaMath [@yu2023metamath] 在训练时会相互冲突，原因是答案格式存在细微差异——Numina 将答案放入 `\boxed{XYZ}` 中，而 MetaMath 将答案写在 `The answer is: XYZ` 之后——同时训练两者会导致表现比只训练其中一个还要差。强模型被训练为能够适应多种格式，但它们通常有一个最擅长的格式。

综上所述，关于闭源模型评估的现状，我们可以得出几个关键点：

- 我们不知道、也未必拥有各实验室用来"爬山"的核心测试集，因此某些评估实际上是代理指标。
- 前沿模型的推理正变得越来越复杂（特殊的系统提示、特殊的 token 等），我们不清楚这会对评估产生什么影响。
- 我们并不知晓用于数值报告闭源评估的所有格式和细节。

所有这些动态，加上近几年 AI 模型的飞速发展，造就了类似 @fig:benchmark-saturation 的著名图表——每个时代流行的基准测试都会在短时间内被"解决"。描述这种每基准测试层面动态的常用术语是**饱和**（saturation）。当每个基准测试接近 100% 时，模型的提升开始放缓，因为剩下的数据点变得更加困难（在许多情况下甚至是标注有误的），这使其作为训练进步度量（或两个模型之间的比较）的可靠性下降。

![Epoch AI 发布的报告，展示主要 AI 评估如何在短时间内快速饱和（饱和即基准测试达到满分后，模型不再产生有意义的区分信号）。许可协议 CC-BY。](images/benchmark-performance.jpeg){#fig:benchmark-saturation}

## 实验室实际如何在内部使用评估来提升模型

前沿语言模型的评估在今天既是一门艺术，也是一门科学；详细规定不同团队如何使用评估来理解最前沿的语言模型，本身就足以写一本教科书。

不同团队选择不同的评估来保持其独立性，即将其设为真正的测试集（test set），但没有人会公开自己选择了哪些。例如，流行的推理评估 MATH 和 GSM8K 都包含训练集，其中的提示可以被轻松用于提升性能。利用同一分布中的提示来提升表现，与通过训练通用数学数据来泛化到这些任务，是完全不同的两回事。

事实上，这些**训练集**（training set）中包含着极高质量的资料，模型从中学到益处。如果这些公司**不**将对应评估作为核心指标进行跟踪，那么在这些评估集上进行训练就是一个务实的决策——毕竟，高质量数据是模型开发的主要限制因素之一。

领先的 AI 实验室通过在少数关键评估上聚焦来进行"爬山"，并在最后报告核心公共集上的分数。关键是：它们用于跟踪进度的一些评估（如 GPT-4 报告 [@achiam2023gpt] 中从缩放预测的交叉熵损失数据集）通常是公开的。

后训练评估在很大程度上与人类评估相互依赖。生成式语言模型的人类评估会产生 Elo 排名（在早期 Anthropic 论文如 Constitutional AI 中很流行），而奖励模型的人类评估则展示一致性。这些也可以通过 A/B 测试窗口向用户提供两种不同模型来获得（参见[偏好数据章节](https://rlhfbook.com/c/11-preference-data)）。

它们选择聚焦的有限评估集，在评估和训练之间建立了紧密的联系。在过去，MMLU 曾一度是关注的核心评估。随着社区对科学能力的关注增加，GPQA 在推理模型崛起期间变得极受欢迎。实验室会更改评估，使其更适合自己的需求——例如 OpenAI 发布了 SWE-bench Verified [@openai2024swebench]。每个前沿实验室都构建了或购买了大量公共无法访问的内部评估。

在内部改进评估能力对下游训练带来的关键提升是**提高了比较训练运行时的统计功效**（statistical power）。通过改进评估，这些实验室降低了优先信号的噪声，从而做出更明智的训练决策。

这一问题又因现代语言模型训练栈中后训练日益复杂而加剧。如今评估语言模型涉及适度的 token 生成量（而非仅仅查看答案的对数概率），因此需要消耗计算资源。业界普遍认为，前沿实验室会使用一些小技巧来提升许多任务的表现——最常见的解释是为特定评估设计一次性提示（one-off prompts）。

## 污染问题（Contamination）

当前语言模型实践中的一个主要问题（即不限于 RLHF 和后训练）是：有意或无意地将评估数据集的数据用于训练。这被称为**数据集污染**（dataset contamination，一种**数据泄漏**（data leakage）形式），相应的预防措施称为**去污**（decontamination）。要对数据集进行去污，需要在训练集和测试集上搜索 n-gram 重叠（在词或子词 token 级别）或固定长度字符子串匹配（例如 50 个字符）的匹配项 [@singh2024evaluation]。

数据变污的方式有很多种，但最常见的是从网上抓取训练数据时用于多个阶段。基准测试常常列在可被爬取的公共网络域名上，或者用户将问题输入模型后，这些问题可能最终进入未来模型的候选训练数据。

例如，在 Tülu 3 评估套件的去污过程中，作者发现流行的开源数据集被 RLHF 相关的流行评估所污染 [@lambert2024t]。这些重叠包括：UltraFeedback 与 TruthfulQA 的污染、Evol-CodeAlpaca 与 HumanEval 的污染、NuminaMath 与 MATH 的污染，以及 WildChat 与安全评估的污染。这些污染是通过 8-gram 重叠（从训练提示到评估集中的精确提示）发现的。

在其他情况下，模型被发现训练了与基准测试非常接近的数据——例如保持数学问题的文字不变而仅改变数字——这可能在后训练阶段导致异常行为：当模型用随机奖励进行 RL 训练时，基准测试分数反而提升了。这是一个刻意构造的设置（contrived setup），只有在模型存在某些类型的数据污染时才会出现。这类基础模型污染——即无法确切证明模型为何表现出某些行为——在 Qwen 2.5 和 Qwen 3 基础模型上的许多早期 RLVR 研究中都是一个重要的混淆变量 [@shao2025spurious] [@wu2025reasoning]。

为了理解那些不公开或释放训练数据的模型的污染情况，人们创建了基准测试的新版本，对原始问题进行了轻微扰动（例如针对 MATH 的变体 [@huang2025math]），以观察哪些模型是为匹配原始格式或问题而训练的。在这些扰动基准测试上出现高方差并不能确证存在污染（污染很难被证明）。相反，它可能表明模型是在针对特定格式进行训练——这种格式在现实世界中的泛化能力可能有限。

## 工具

目前有多个开源的评估工具可供选择。一些代表性的工具包括：

- Inspect AI（来自英国安全研究所）[@inspectAI2024]
- Hugging Face 的 LightEval [@fourrier2023lighteval]——它驱动了 Open LLM Leaderboard [@open-llm-leaderboard-v2]
- EleutherAI 的评估框架（evaluation harness）[@gao2023evalharness]——建立在 GPT-Neo-X 模型的底层基础设施之上（其中包含一套不错的 GPT-3 时代评估设置和配置）[@gpt-neox-20b]
- Ai2 基于 OLMES 的库 [@gu2024olmes]
- Stanford 基金会模型研究中心的 HELM [@liang2023helm]
- Mosaic（现 Databricks）的 Eval Gauntlet [@mosaicml2024gauntlet]
- 等等。