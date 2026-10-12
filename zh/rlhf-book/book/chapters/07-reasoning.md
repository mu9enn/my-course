<!--
  Copyright (c) 2025-2026 Nathan Lambert.
  Licensed under CC BY-NC-SA 4.0:
  https://creativecommons.org/licenses/by-nc-sa/4.0/
  Full license: https://github.com/natolambert/rlhf-book/blob/main/LICENSE-CHAPTERS
-->
---
prev-chapter: "Reinforcement Learning"
prev-url: "06-policy-gradients"
page-title: 推理与推理时扩展
search-title: "第7章：推理与推理时扩展"
meta-description: "后训练中的推理训练与推理时扩展，包括 RLVR 和思考模型。"
next-chapter: "Direct-Alignment Algorithms"
next-url: "08-direct-alignment"
lectures:
  - video: "https://www.youtube.com/watch?v=o4AB5xHIDdM&list=PLL1tdVxB1CpVpEtMHxwuR4uI4Lxjw00_y&index=7"
    label: "讲义5：推理模型的崛起"
---

# 推理与推理时扩展

推理模型（reasoning models）和推理时扩展（inference-time scaling）在 2024 年底到 2025 年，乃至更远的未来，为语言模型性能带来了巨大的飞跃。推理时扩展是指通过在实际生成阶段使用更多计算资源（例如生成更长的推理链或对同一问题采样多个回答）来提升模型性能的能力。经过大量推理训练的语言模型能够非常充分地利用这一特性。这些模型在训练过程中使用了大量的带可验证奖励的强化学习（RLVR, Reinforcement Learning with Verifiable Rewards）[@lambert2024t]，同时也仍然使用了大量的 RLHF。在本章中，我们将回顾 AI 社区如何重新认识强化学习在语言模型中潜力的发展历程，介绍 RLVR 的基本原理，重点讨论几项关键工作，并展望将定义该领域未来几年走向的一些争议话题。

## RLVR 的角色

首先，让我们从 Yann LeCun 在 2016 年 Neural Information Processing Systems（NeurIPS）会议上首次提出的一个如今广为流传的"蛋糕隐喻"说起。这个隐喻描述了现代机器学习中不同学习阶段的相对地位：

> 如果智力是一块蛋糕，蛋糕的主体是**无监督学习**，蛋糕上的糖霜是**监督学习**，而蛋糕顶端的樱桃则是**强化学习（RL）**。

借助现代语言模型和后训练流程的近期变化，这个比喻已经基本完整。RLHF 是这一路径的先导，而为推理模型（主要涉及数学、代码和科学领域）使用的强化学习则是对这一比喻的进一步印证。在这个比喻中：

- 在海量的互联网数据上进行的自监督学习构成了蛋糕的主体（如果从计算的 FLOPs 消耗角度来看，尤其如此）。
- 后训练阶段的起点——对指令的监督微调（SFT）——将模型的分布调整到一个更狭窄的范围内。
- 最后是"纯粹"的强化学习（RL）作为蛋糕顶端的樱桃。用于构建新"推理"或"思考"模型的大规模强化学习正是这一画龙点睛之笔（当然还有 RLHF 的辅助，正如我们后面将要解释的，RLHF 并不属于经典意义上的 RL）。

这种推理训练的微小结晶体现在**思考模型（thinking models）**中——它们结合了本书讨论的后训练技术进行偏好对齐，并在可验证领域进行强化学习训练，从而大幅提升推理、编码和数学解题等能力。

这些模型的训练方法称为**带可验证奖励的强化学习**（RLVR, Reinforcement Learning with Verifiable Rewards）[@lambert2024t]。RLVR 与 RLHF 的工作流程非常相似，但它用评分函数替代了奖励模型：答案正确时返回正奖励，不正确时返回 0。

以 RLHF 和 RLVR 在评分方式上的差异为例。在 RLHF 中，奖励模型必须评估主观性的质量：

> **提示**：请解释经济学中的"机会成本"概念。
>
> **回复**：机会成本是你在做决策时所放弃的次优替代方案的价值。举个例子，如果你花一小时学习而不是工作，机会成本就是你可以赚到的工资……

对这些回复进行评分需要评判清晰度、准确性、完整性和有用性——所有这些都需要学习的偏好，且没有绝对正确的答案。

相比之下，RLVR 使用能返回确定分数的验证函数。以数学题为例：

> **提示**：小于 20 的所有素数之和是多少？
>
> **回复**：小于 20 的素数有 2, 3, 5, 7, 11, 13, 17, 和 19。
> 将它们相加：2 + 3 = 5，然后 5 + 5 = 10，10 + 7 = 17，17 + 11 = 28，28 + 13 = 41，41 + 17 = 58，最终 58 + 19 = 77。
> 答案是 $\boxed{77}$。
>
> **验证**：`extracted_answer == 77` → 奖励 = 1

`\boxed{}` 是数学排版中采用的一种惯例，使得提取答案变得直接明了——无论模型是如何得出结果的，一个简单的正则表达式就可以从回复中提取最终答案。注意还存在其他提取答案的方法，比如直接使用短语 "The answer is: "（如上例所示）、特殊 token 如 `<answer>`，或定界符如 `####`。

对于代码生成，验证通常以单元测试的形式出现：

> **提示**：写一个 Python 函数 `fib(n)`，返回第 n 个斐波那契数，其中 fib(0) = 0，fib(1) = 1。
>
> **回复**：
> def fib(n):
>     if n < 2:
>         return n
>     return fib(n - 1) + fib(n - 2)
>
> **验证（单元测试）**：
>
> assert fib(0) == 0   # base case
> assert fib(1) == 1   # base case
> assert fib(10) == 55 # larger value
> (全部通过 → 奖励 = 1)

单元测试是代码的自然验证函数：它们使用已知的输入-输出对来执行模型的解决方案。一种常见的评分方式是做简单的门控：如果所有断言都通过，奖励为 1；如果任何一个失败，奖励为 0。其他方案则根据通过的测试数量按比例给予部分分数。

在上述两个例子中，都不需要学习的奖励模型，大多数方案也无需它（因为这些领域的模型对过优化具有鲁棒性），但也可以使用多个奖励的线性组合。

RLVR 背后的思想在强化学习文献中并不陌生——根据答案是否正确来进行梯度更新的核心理念几乎就是强化学习的教科书定义。将其应用到语言模型时的创新，主要在于如何在保持微调模型强大泛化能力的同时使用它。在此之中，语言建模文献中存在许多相关的思路，模型可以从关于答案正确性的反馈中学习。

最初，在我参与 coined（首创）"带可验证奖励的强化学习（RLVR）"这一术语的工作 [@lambert2024t] 中，该方法本应被命名为"带真实奖励的强化学习（RLGT）"。然而 RLVR 与单纯从真实答案中学习有细微的差别。在数学这类领域中，正如我们上面看到的，存在单一的真实答案来验证解决方案。但在其他领域，如代码生成或精确的指令遵循中，答案可以用检查函数（例如单元测试）来验证，即使存在多个正确答案而并非单一真实答案。RLVR 进展的核心在于拥有多样化和深度的可验证问题集，即使精确解并非先验可知。

![以强化学习反馈循环形式呈现的 RLVR。与奖励模型不同，此处使用验证函数。](images/rlvr-system.png){#fig:rlvr data-dark-src="images/rlvr-system-dark.png"}

成功部署这种训练方式的首批模型是 OpenAI 的 o1 [@openai2024o1] 和开源权重模型 DeepSeek R1 [@guo2025deepseek]。不久之后，整个 AI 行业都将这种训练过程和模型风格作为重点。这里的根本变化更多是训练阶段的重新分配和不同行为的优先级调整，而非这种 RL 配置本身完全新颖。推理模型开启了一个期望大规模扩展 RL 训练的时代。

关于这些模型所表现出的行为类型，以下面 DeepSeek V3 0325 与其推理模型 DeepSeek R1 在查询"Write me a short poem about a goldfish"（给我写一首关于金鱼的短诗）上的对比为例。DeepSeek V3 的回答非常直接：

> **回复**：Goldfish Dreams
>
> In a bowl of glass so clear and round,
> A tiny goldfish swims without a sound.
> With scales that gleam like sunlight's kiss,
> He drifts along in watery bliss.
> 
> A flick of fin, a flash so bright,
> Chasing bubbles in the light.
> Does he dream of oceans wide?
> Or is his little world enough---his pride?

而 DeepSeek R1 的体验则不同。它在回复用户之前会先生成大量的思考 token 来构思回答。其输出如下：

> **回复**：`<thinking>` Okay, the user wants a short poem about a goldfish. Let me start by brainstorming some goldfish-related imagery. Goldfish are often in bowls, right? So maybe start with the setting. Words like "gilded bowl" or "crystal globe" could work.
> 
> Next, think about the movement of the goldfish. They swim smoothly, so words like "dart", "glide", or "swirl" come to mind. Maybe describe their fins as "silken" to emphasize delicacy.
> 
> Then, consider the environment around the goldfish. Sunlight through water creates shimmering effects. Words like "sunbeams dance" or "ripples spin" might capture that. Including elements like castles or pebbles adds a playful touch.
> 
> Themes? Maybe the contrast between the goldfish's small world and its perception of freedom. The bowl as a universe, tiny but complete. Ending with a sense of mystery or silent observation could give depth. Need to keep it concise, maybe four stanzas with a rhyme scheme. Let me check the rhythm and flow. Avoid clichés but keep it accessible. Alright, let's piece it together. `</thinking>` 
> 
> Gilded Dreams in Liquid Glass
> 
> A gilded bowl, a crystal globe,
> Where tiny tides in silence flow---
> A flash of orange, a whispered robe,
> You dart through sunlit indigo.
> 
> Your world is small, yet boundless too---
> Each pebble, castle, weed unfurled.
> The surface bends the sky to blue,
> And ripples spin your liquid world.
> 
> You glide through myths we'll never know,
> A silent monarch, veiled in mist.
> Do dreams drift where the bubbles go?
> Or memories in amethyst?
> 
> We watch you trace your endless sphere---
> A universe within a tear.

`<thinking>` 标签中的 token 是模型的推理过程。对于更复杂的问题，推理阶段在生成答案之前可能需要数千个 token。因此，长上下文语言模型是高级推理行为的先决条件，但这不是本章的焦点。

对**这种训练如何工作**的核心理解在于：对于一个给定模型，我们重复以下循环：

1. 对多个问题采样多个回答，
2. 朝正确的回答方向进行梯度更新，然后
3. 重复以上步骤，反复使用相同的数据。

值得注意的是，这种极其简单的方法（当配合精心设计的数据分布和稳定的训练基础设施时）通过反复回顾相同的问题来帮助模型学习。更令人惊叹的是，对这些训练问题的改进能够泛化到模型从未见过的题目和（某些）领域！

这种简单的方法使模型能够轻量地搜索行为空间，而强化学习算法则提高了与正确答案相关的行为出现的概率。

## 新一代推理模型的起源

在此，我们详细说明导致 2025 年推理模型爆发式增长的高级趋势。

### 为什么现在 RL 起作用了？

尽管长期以来有"强化学习还不够成熟" [@irpan2018deep] 的说法，也有论文详细描述了 RL 的深度可复现性问题 [@henderson2018deep]，但该领域克服了这些困难，找到了高影响力的应用场景。本章中提到了一些，如 ChatGPT 的 RLHF 和 DeepSeek R1 的 RLVR，但还有许多其他领域，包括改进芯片设计 [@mirhoseini2020chip]、掌握电子游戏 [@schrittwieser2020mastering]、自动驾驶 [@cusumano2025robust] 等等。RL 在语言模型上的训练爆发表明该研究领域在许多根本问题上取得了进展，包括：

- **RL 的稳定性问题可以解决**：在其整个发展历史中，RL 普及的限制因素始终是稳定性。这体现在两个方面：首先，学习本身可能不稳定，不一定总是有效；其次，训练本身已知比标准的语言模型训练更加脆弱，更容易出现损失突增、崩溃等问题。不计其数的新模型发布都在预训练基座模型之上使用了这种带可验证奖励的 RL 训练方式，学术界也大量采用了这种方法。RL 的技术门槛已经降到了历史最低。

- **开源版本已经"存在"**：已经有许多工具可以用来 RLVR 和相关技术训练语言模型。例如 TRL [@vonwerra2022trl]、Open Instruct [@lambert2024t]、veRL [@sheng2024hybridflow] 和 OpenRLHF [@hu2024openrlhf]，其中许多都在 RLHF 和后训练流程前期的优化基础上进行了改进。工具的可用性正在推动大量且加速增长的研究。

多个资源指出，推理 RL 训练只有在 2024 年前后开始出现的最先进模型上才可行，这表明在推理训练之前模型需要具备一定的基础能力。

### RL 训练与推理时扩展

通过强化学习训练来激发推理行为和可验证领域上的性能，与推理时扩展的理念密切相关。推理时扩展（inference-time scaling），也称为测试时扩展（test-time scaling），是指一类在推理阶段使用更多计算能力以提升下游任务表现的方法。DeepSeek R1 和 OpenAI 的 o1 发布之前，推理时扩展的方法就已受到研究，这两者均大规模普及了对 RL 训练的投资。例如价值引导采样（value-guided sampling）[@liu2023don] 或带答案提取的重复随机采样（repeated random sampling with answer extraction）[@brown2024large]。此外，推理时扩展还可用于改进超出链式思考（chain-of-thought）推理的更多 AI 训练方法，例如考虑深层选项的奖励模型（reward models that consider the options deeply）[@ankner2024critique] [@liu2025inference]。

RL 训练是利用推理时扩展定律的一条捷径，但从长远来看，我们将拥有更多方法来激发最佳性能所需的推理时权衡。大量使用 RL 训练模型通常使它们能够在每个回复中生成更多 token，并且这种方式与下游性能的显著提升强烈相关（尽管这种序列长度的增加是默认行为，也有研究专门探讨如何在不依赖推理时扩展的情况下提升性能）。这与早期 RLHF 系统中观察到的长度偏向（length-bias）[@singhal2023long] 有显著不同——早期的偏好训练在偏好排名上只有微小的收益，却产生了增加回复平均长度的副作用。

除了核心 RL 训练模型之外，还有许多方法正在被探索，以继续推进推理和推理时计算的极限。这些方法由于其快速演变的性质很大程度上不在本书范围内，但它们包括通过指令微调将更大的 RL 训练模型的推理行为蒸馏到更小模型中 [@muennighoff2025s1]、组合更多推理调用（composing more inference calls）[@chen2024more] 等。这里重要的是下游性能与生成 token 数量的增加之间的相关性——否则就是纯粹的能源浪费。


### RLVR 的未来（超越推理）

在许多领域中，这些新型 RLVR 更聚焦于性能而非行为，因此与开发者的目标更加一致。标准微调 API 通常使用参数高效微调方法（如 LoRA, Low-Rank Adaptation，一种只训练小型附加矩阵而非全部模型权重的参数高效方法，也称为 PEFT, Parameter-Efficient Fine-Tuning），并在指令上监督微调。开发者传入提示词和补全内容，模型通过更新参数使其与补全内容匹配，从而提高数据中特征在模型生成中的出现频率。

RLVR 则专注于答案匹配。给定查询和正确答案，RLVR 帮助模型学会生成正确答案。标准指令微调通常只用 1 到 2 个 epoch 在数据上进行损失更新，而 RLVR 的名字来源于对同样的少量数据点进行数百乃至数千个 epoch 的训练——给模型充分的时间来学习新的行为。这可以看作是将基座模型中偶尔才有效的正向行为强化为 RLVR 之后的稳健行为。

**RL 在语言模型上的应用范围持续扩大**：o1 和 R1 在基础科学层面的最大启示是，我们有了更多方法将语言模型训练为潜在有价值的行为。研究人员和工程师可用的开放机会越多，我们对 AI 总体发展轨迹就应该越有信心。


## 理解推理训练方法

对推理的投入引发了模型训练方式的重大演进。这些训练流程仍然使用前面章节中讨论的通用组件（第 3 章中关于 DeepSeek R1 训练流程的介绍即是一个例子），包括指令微调、基于人类反馈的强化学习（RLHF）和带可验证奖励的强化学习（RLVR）。核心变化是使用更多的 RLVR，并以不同的顺序应用其他训练技术——传统上对于推理模型，核心训练步骤要么是大规模 RL 运行，要么是在已接受了大量 RLVR 训练的另一个模型的*输出*上进行大规模指令微调运行（称为蒸馏）。

### OpenAI o1 或 DeepSeek R1 之前的推理研究

在推理模型爆发之前，大量的研究工作致力于理解如何训练语言模型在可验证领域表现更好。这些工作与后续模型的主要区别在于：它们的处理方法未能扩展到 DeepSeek R1 及后续模型相同的规模，或者它们通过在整体性能上做出牺牲来换取更高的数学或编码能力。我们列出这些工作的基本思想和动机，是为了勾勒推理模型在整个领域中的诞生图景。

2022 年至 2023 年间，训练语言模型在可验证领域的一些最早工作包括自我推理者（STaR, Self-Taught Reasoner）系列 [@zelikman2022star] [@Zelikman2024QuietSTaRLM] 和 TRICE [@hoffman2023training]，两者都使用了真实奖励信号来鼓励模型进行链式思考推理。STaR 在效果上近似策略梯度算法，但在实践中以不同的方式过滤样本，并使用交叉熵而非对数概率；Quiet-STaR 在此基础上扩展，其思想与近期推理模型非常相关——让模型在尝试回答可验证问题之前先生成 token（这有助于训练性能）。TRICE [@hoffman2023training] 也通过生成轨迹（traces）然后使用受马尔可夫链蒙特卡洛启发的自定义期望最大化（EM）算法进行优化来改进推理。VinePPO [@VinePPO] 跟随这些思路，使用了一个更接近现代推理模型配置的方案。VinePPO 使用基于 PPO 的算法，以数学题的正确答案给出二值奖励，在 GSM8K 和 MATH 上训练。

OpenAI 的 o1 和 DeepSeek R1 之前的其他工作使用代码执行作为训练的反馈信号 [@gehring2024rlefgroundingcodellms], [@xu2024dpo]，或使用定理证明的验证（此处称为 Reinforcement Learning from Verifier Feedback, RLVF）[@amit2024models]。Tülu 3 在这些方法的基础上，使用简单的 PPO 训练器给包含正确答案的补全以奖励——最重要的是在广泛评测中保持模型的整体性能。Tülu 3 和二值奖励的现代推理训练技术与 STaR 的迭代方法或 Quiet-STaR 的对数似然奖励形成对比。

### 早期推理模型

下表 @tbl:reasoning_list 总结了 DeepSeek R1 之后发布的若干基础性推理研究报告，其中一些附带了开源数据和模型权重。

::: {.table-wrap}
| 日期        | 名称                        | 要点                                                                  | 开源权重 | 开源数据 |
|-------------|----------------------------|-----------------------------------------------------------------------|----------|----------|
| 2025-01-22  | DeepSeek R1 [@guo2025deepseek]             | 基于 RL 的 DeepSeek 升级，数学和代码推理大幅提升      |  是      | 否   |
| 2025-01-22  | Kimi 1.5 [@team2025kimi]                  | 在中文/英文数据上扩展 PPO/GRPO；AIME 数学很强            | 否           | 否        |
| 2025-03-31  | Open-Reasoner-Zero [@hu2025openreasonerzero]   | 基座模型 RL 的完全开源复现      |  是      |  是   |
| 2025-04-10  | Seed-Thinking 1.5 [@seed2025seed]         | 字节跳动的 RL 流水线，带动态 CoT 门控                         | 是     | 否   |
| 2025-04-30  | Phi-4 Reasoning [@abdin2025phi4]          | 14B 模型；谨慎的 SFT→RL；在 STEM 推理上表现突出                   | 是      | 否        |
| 2025-05-02  | Llama-Nemotron [@bercovich2025llamanemotron]   | 多尺寸"推理切换"模型                 |  是      |  是   |
| 2025-05-12  | INTELLECT-2 [@primeintellectteam2025intellect2reasoningmodeltrained] | 首个公开文档化的全球去中心化 RL 训练运行                    |  是      |  是   |
| 2025-05-12  | Xiaomi MiMo [@xia2025mimo]                | 从预训练到后训练的端到端推理流水线              | 是          | 否       |
| 2025-05-14  | Qwen 3 [@yang2025qwen3]                   | 将 R1 流程应用于新模型                    |  是      | 否   |
| 2025-05-21  | Hunyuan-TurboS [@liu2025hunyuan]          | Mamba-Transformer MoE，自适应长/短 CoT                        | 否           | 否        |
| 2025-05-28  | Skywork OR-1 [@he2025skyworkor1]          | 避免熵崩溃的 RL 流程；在 AIME 上超越 DeepSeek           |  是      |  是   |
| 2025-06-04  | Xiaomi MiMo VL [@coreteam2025mimovltechnicalreport]                | 端到端扩展推理流水线以包含多模态任务              | 是          | 否       |
| 2025-06-04  | OpenThoughts [@guha2025openthoughts]      | 从 QwQ-32B 蒸馏的公开 120 万条指令数据集                    |  是      |  是   |
| 2025-06-10  | Magistral [@mistral2025magistral]         | 在 Mistral 3 上进行纯 RL；多语言 CoT；小模型开源      |  是  | 否        |
| 2025-06-16 | MiniMax-M1 [@minimax2025minimax_m1] | 开源权重 456B MoE 混合/闪电注意力推理模型；1M 上下文；RL w/CISPO；发布 40K/80K 思考预算检查点 | 是 | 否 |
| 2025-07-10 | Kimi K2 [@kimiteam2025kimik2]                            | 1T MoE（32B 活跃），带 MuonClip（QK-clip）保障稳定性；15.5T token 预训练无损失突增；多阶段后训练含智能体数据合成 + 联合 RL；发布基座 + 后训练检查点。                               | 是          | 否         |
| 2025-07-28 | GLM-4.5 [@zeng2025glm45] | 开源权重 355B-A32B MoE "ARC" 模型，带思考/非思考模式；23T token 多阶段训练 + 后训练含专家迭代和 RL；发布 GLM-4.5 + GLM-4.5-Air (MIT)。 | 是 | 否 |
| 2025-08-20 | Nemotron Nano 2 [@nvidia2025nemotronnano2]               | 混合 Mamba-Transformer，支持长"思考轨迹"；20T token FP8 预训练后压缩/蒸馏；明确发布多个检查点以及"大部分"前后训练数据集。                                       | 是          | 是（大部分） |
| 2025-09-09 | K2-Think [@llm3602025k2think]                            | 参数高效数学推理系统：一个 32B 开源权重模型，带测试时扩展流程；定位为完全开源包括训练数据/代码（根据发布材料）。                                                                       | 是          | 是        |
| 2025-09-23 | LongCat-Flash-Thinking [@mlcteam2025longcat]             | 560B MoE 推理模型；报告明确说明从长 CoT 冷启动到大规模 RL 的阶段性流程；开源发布。                                                                                                             | 是          | 否         |
| 2025-10-21 | Ring-1T [@ringteam2025everystepevolves]                  | 万亿级"思考模型"，聚焦 RL 扩展；报告阐述了在 1T 上扩展 RL 的瓶颈/解决方案并发布开源模型。                                                                                                             | 是          | 否         |
| 2025-11-20 | Olmo 3 Think [@teamolmo2025olmo3]         | 完全开源的"模型流程"发布：报告整个生命周期（阶段、检查点和数据点），将 Olmo 3 Think 32B 定位为旗舰开源思考模型。                                        | 是          | 是        |
| 2025-12-02 | DeepSeek V3.2 [@deepseekai2025v32]                       | 开源 MoE 前沿推进，报告强调注意力效率变更、RL 框架升级和智能体/推理性能的数据合成。                                                                             | 是          | 否         |
| 2025-12-05 | K2-V2 [@liu2025k2] | 70B 稠密"360-open"模型从头训练；带 3 档 SFT 仅后训练以支持可控思考。 | 是 | 是 |
| 2025-12-15 | Nemotron 3 Nano [@nvidia2025nemotron3nano]               | 30B-A3B MoE 混合 Mamba-Transformer；在 25T token 上预训练，包含 SFT + 大规模 RL；明确声明提供权重 + 流程/代码 + 大部分训练数据。                                                                      | 是          | 是（大部分） |
| 2025-12-16 | MiMo-V2-Flash [@mimo2025flash] | 309B MoE（15B 活跃），优化速度：混合 SWA/GA 注意力（5:1，128 token 窗口）+ 轻量 MTP；27T token FP8 预训练；后训练含 MOPD + 大规模智能体 RL 用于推理/编码。 | 是 | 否 |
表：2025 年值得关注的推理模型技术报告汇总，这是大规模推理时扩展与 RLHF 的第一年。{#tbl:reasoning_list}
:::


### 训练推理模型的常见实践

本节详细说明在训练推理模型时用于安排训练阶段顺序和修改数据以最大化性能的常用方法。

需要注意的是，这些论文可能使用了列出的技术但未提及，而其同行可能没有提及却实际使用了，因此这些例子是已知实现的子集，应作为参考而非最优流程的最终定论。

- **离线难度过滤**（Offline difficulty filtering）：RLVR 的核心理直觉是模型只能从存在梯度的例子中学习。如果 RLVR 的起始模型以 100% 或 0% 的正确率解决一个问题，那么同一提示的不同补全之间将没有梯度差异（即所有策略在策略梯度算法看来是一样的）。许多模型在开始大规模 RL 之前使用难度过滤，将训练问题限制在起始模型以 20-80% 的正确率解决的范围内。这些数据通过从训练集的每个提示采样 N 次（如 16 次）补全并验证正确率来收集。Seed-Thinking 1.5、Open Reasoner Zero、Phi-4、INTELLECT-2、MiMo RL、Skywork OR-1 等都使用了这种方法的变种。
- **批次内在线过滤**（Per-batch online filtering，或训练过程中的难度课程）：为了补充离线过滤以找到合适的训练问题，另一个重大问题是：在训练过程中，应该以什么顺序向模型呈现问题？为解决这一问题，许多模型使用批次内问题的在线过滤、预建课程/数据调度器、将更难的问题留到训练后期，或其他提高长期稳定性的想法。Kimi 1.5、Magistral、Llama-Nemotron、INTELLECT-2、MiMo-RL、Hunyuan-TurboS 等使用了相关思路。
- **移除 KL 惩罚**（Remove KL penalty）：相对于 RLHF 训练，推理模型的 RL 运行长度（无论用何种指标衡量：总 GPU 小时数、FLOPS 或 RL 步骤）不断增加，且奖励函数对过优化的敏感性降低，许多模型移除了将 RL 学习到的策略约束为与训练开始时使用的基座模型相似的那项 KL 惩罚。这使得模型在训练期间能够进一步探索。RAGEN [@wang2025ragenunderstandingselfevolutionllm]、Magistral、OpenReasonerZero、Skywork OR-1 等使用了此方法。
- **放宽策略梯度裁剪**（Relaxed policy-gradient clipping）：GRPO 算法的新变体（如 DAPO [@yu2025dapo]）对 GRPO（或 PPO）中使用的双向裁剪目标进行了修改，以实现更好的探索。裁剪也被证明在奖励不完美的情况下可能导致虚假的学习信号 [@shao2025spurious]。RAGEN、Magistral、INTELLECT-2 等使用了针对不同梯度方向不同范围的双向裁剪。
- **离策略数据**（Off-policy data，或完全异步更新）：随着 RL 解决更难任务所需的补全长度急剧增加（尤其是响应长度的*方差*显著增大——经常存在极端长度的异常值），RL 运行中的计算资源可能闲置。为解决这一问题，训练正转向异步更新或改变问题在批次中的排列方式以提高整体吞吐量。Seed-Thinking 1.5、INTELLECT-2 等使用了从部分到完全异步（离策略）的数据。
- **额外的格式奖励**（Additional format rewards）：为了使推理过程可预测，许多模型添加了少量奖励来确保模型在给出答案之前遵循正确的格式（如 `<think>...</think>`）。DeepSeek R1、OpenReasonerZero、Magistral、Skywork OR-1 等使用了此方法。
- **语言一致性奖励**（Language consistency rewards）：与格式奖励类似，一些多语言推理模型使用语言一致性奖励来优先处理在推理过程中不切换语言的模型（以提供更好的、更可预测的用户体验）。这包括 DeepSeek R1、Magistral 等。
- **长度惩罚**（Length penalties）：许多模型在 RL 训练过程中使用不同形式的长度惩罚，以随时间稳定学习过程或缓解对困难问题的过度思考。一些例子包括：Kimi 1.5 逐步扩展目标长度以对抗过度思考（同时在难度课程上保持高训练准确率），或 INTELLECT-2 全程运行较小的长度惩罚。渐进式延长训练序列长度通过首先迫使模型在思维预算更少的领域中有效推理来缓解过度思考，然后过渡到更长的训练，使模型能够在更复杂的问题上高效使用这些行为。其他模型使用过长过滤和其他相关实现来提高吞吐量。
- **损失归一化**（Loss normalization）：关于原始 GRPO 算法的每组归一化项可能引入长度或难度偏差的问题，有一些讨论（参见策略梯度章节或 [@liu2025understanding]）。因此，Magistral 或 MiMo 等模型选择在整个批次层面（而非每组层面）归一化损失或优势。
- **并行测试时计算扩展**（Parallel test-time compute scaling）：将多个并行、独立采样回放的回答结合起来可以带来比使用单个回放的回答显著更好的改进。最常见的并行测试时计算扩展形式（如 DeepSeek-R1、Phi-4 等所做）是将多数回放返回的答案作为最终答案。更高级的技术是使用一个评分模型来从并行回放的回答中选择最佳答案。截至 2026 年，此技术在公开记录的推理模型流程中尚未普及，但 Claude 4 的声明中 [@anthropic2025claude4] 有所提及，且在 DeepSeek-GRM [@liu2025inference] 中被使用。

除了上述通用技术外，还有许多关于推理训练如何在不牺牲辅助能力的前提下产生有用模型的常见发现：

- **纯文本推理提升多模态性能**：Magistral、MiMo-VL 等发现，在多模态训练之后，对多模态模型进行纯文本推理训练可以*提升*最终模型的多模态性能。
- **系统提示实现可切换推理**（Toggleable reasoning with system prompt，或长度控制）：Llama-Nemotron、Nemotron Nano、Qwen 3、SmolLM 3 等使用特定的系统提示（可能与长度控制的 RL 训练 [@aggarwal2025l1] 结合）来为用户提供可切换的思考长度。其他开源模型如 OpenAI 的 gpt-oss 和 LLM360 的 K2-V2 [@liu2025k2] 在系统提示中采用低-中-高推理强度设置，但这种行为的训练方法记录不够充分。

## 展望未来

推理模型的格局正在以近年来 AI 研究领域中最快速度发展，这里列出的一些常见实践不可避免地被新技术取代。

多项工作正在系统地理解推理训练为何有效。Olmo 3 Think [@teamolmo2025olmo3] 代表了推理模型完整训练生命周期最全面的开源文档，为研究社区提供了每个阶段的检查点和数据，并在 220 个 GPU 上完成了近 4 周的训练运行。类似地，关于推理 RL 缩放特性的研究工作 [@khatri2025art] 也开始将从业者仅凭直觉理解的计算、数据和性能之间的关系形式化。

明确的一点是，强化学习已经从蛋糕隐喻中的"顶端的樱桃"进化为前沿模型训练中的承重组件。本章中围绕 RLVR 理念的一些次要技术——难度过滤、格式奖励等——并非最终答案，但它们代表了该领域当前对如何从语言模型中激发推理的最佳理解。下一代的方法可能有所不同，但它们将建立在本文奠定的基础之上。
