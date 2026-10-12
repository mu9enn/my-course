<!--
  Copyright (c) 2025-2026 Nathan Lambert.
  Licensed under CC BY-NC-SA 4.0:
  https://creativecommons.org/licenses/by-nc-sa/4.0/
  Full license: https://github.com/natolambert/rlhf-book/blob/main/LICENSE-CHAPTERS
-->
---
prev-chapter: "Rejection Sampling"
prev-url: "09-rejection-sampling"
page-title: 偏好的本质
search-title: "第10章：偏好的本质"
meta-description: "从概念层面探讨人类偏好、偏好学习，以及为什么RLHF可以优化难以具体指定的行为。"
next-chapter: "Preference Data"
next-url: "11-preference-data"
lectures:
  - video: "https://www.youtube.com/watch?v=Y2tv5vuaxFs&list=PLL1tdVxB1CpVpEtMHxwuR4uI4Lxjw00_y&index=13"
    label: '第8讲：论"偏好"与偏好数据'
---

# 偏好的本质

基于人类反馈的强化学习（Reinforcement Learning from Human Feedback, RLHF）在早期文献中也被称为"基于人类偏好（Human Preferences）的强化学习"，其出现是为了在那些难以专门设计奖励函数（Reward Function）的领域优化机器学习模型。

"偏好"（Preference）一词出现在早期文献中，也是 RLHF 流程的核心所在——人类偏好正是我们试图建模的对象，也是训练数据的来源。要理解建模和度量人类偏好的挑战范围，需要在更广泛的语境中理解：什么是偏好、我们对偏好的理解如何形成、以及经济学、心理学、哲学等多个学科又是如何为现代 RLHF 提供理论支撑的。

## 当偏好取代正确性

考虑一个例子：你怎么判断下面这两首诗哪首更好？2025年2月26日，我向 Claude 3.7 Sonnet 和搭载 GPT-4o 的 ChatGPT 分别提出了以下请求：

> **用户**：为我写一首关于一只乐观的金鱼的短诗。

**示例 1：**

> **回复**：《乐观的金鱼》
> 
> 一条小金鱼，明亮又大胆，
> 游着圆圈，梦想说不完。
> 尽管碗小而且圆，
> 无尽的奇迹依旧存在。
> 
> "世界广阔，"她总是这样说，
> "我会每一天发现新的快乐！"
> 每一次涟漪，每一次闪光，
> 她追逐阳光，追逐梦想。
> 
> 没有墙壁能削弱她希望的视野，
> 因为在她心中，海洋在生长。
> 尽管她只在同一个地方游动，
> 她以爱与优雅迎接每一天。

**示例 2：**

> **回复**：《乐观的金鱼》
> 
> 在一个弯曲的玻璃碗中，
> 游着一条明亮又大胆的金鱼。
> 人们说它只有三秒钟的记忆，
> 但每一次循环都感觉全新而灿烂。
> 
> "今天也许会带来新鲜的鱼片，
> 或者也许有一座高高的城堡。
> 水看起来格外清澈——
> 这堵墙之外有什么冒险在等待？"
> 
> 鳞片闪亮，转了又转，
> 永远一次次发现快乐。
> 每一刻都新鲜，每一次转动都明亮，
> 金色色调中的乐观主义者。

哪一首更好？它们分别来自哪个模型？你又如何分辨？尤其可以把这个问题与"美国总统是谁？"这样的提问对比——后一类问题有明确的对错。

使用人类作为奖励信号（Reward Signal）的动机，是为了获得目标奖励的间接指标，并将下游模型与人类偏好（Human Preferences）*对齐*（Align）。但在实践中，实现这一目标充满挑战，对最佳实践的解读也存在大量灰色地带。

人类标注（Human-Labeled）的反馈数据的使用融合了多个学科的历史。单独使用人类数据是一个被深入研究的问题，但在 RLHF 的语境中，这些数据被用在多个长期存在的研究领域的交汇处 [@lambert2023entangled]。

作为粗略近似，现代 RLHF 是以下三个领域发展的交汇：

1. 哲学、心理学、经济学、决策理论（Decision Theory）以及人类偏好的本质；
2. 最优控制（Optimal Control）、强化学习（Reinforcement Learning）以及效用最大化（Maximizing Utility）；
3. 现代深度学习系统。

每个领域都带来了关于"偏好是什么"以及"如何优化它"的具体假设，这些假设决定了 RLHF 问题的动机和设计。在实践中，RLHF 方法的动机和研究通常从经验对齐（Empirical Alignment）的视角出发——即在特定技能上最大化模型表现，而非测量其对特定价值观的校准程度（Calibration to Specific Values）。然而，RLHF 方法中价值观对齐（Value Alignment）的起源仍在通过研究"多元化对齐"（Pluralistic Alignment）的跨人群方法来继续探索，例如立场论文 [@conitzer2024social]、[@mishra2023ai]、新数据集 [@kirk2024prism] 以及个性化方法 [@poddar2024personalizing]。

本章的目标是说明：复杂的动机如何导致人们对 RLHF 所用工具的本质做出一些在实践中常常不成立的预设。获取 RLHF 数据的细节将在第 11 章进一步讨论，而将其用于奖励建模（Reward Modeling）的内容见第 5 章。

## RLHF 与偏好的起源

要拆解启发现代 RLHF 使用的复杂历史，需要追溯以下三方面的智力基础：对人类价值观量化的基础、强化学习与最优性的基础，以及与偏好度量相关的行为经济学。将强化学习用于优化偏好奖励模型这一构想，把曾经相隔甚远的多个学科的历史汇聚到一起，形成了一种紧密的优化机制，但这种机制建立在关于人性的多种不同假设之上。第 @fig:tree 图展示了这一基础内容历史的高层次时间线。

我们的目标是梳理出设计者在不同历史阶段引入到系统架构中的各类不确定性（Uncertainty）。现代问题规范一次又一次地退出了那些存在最优解可行的领域，转而部署规格不完善的模型作为近似解。

首先，以下内容都基于一个假设，即人类偏好以某种形式存在——这一假设出现在早期哲学讨论中，例如亚里士多德《工具论》（Topics）第三卷。

![将各个子领域整合到现代 RLHF 中的时间线。直接链接是特定技术的连续发展，箭头表示动机和概念联系。](images/rlhf-tree.png){#fig:tree width=100% .center}

## 目标设定：从效用逻辑到奖励函数

RLHF 的优化明确地只依赖奖励模型（Reward Model）。为了将奖励作为优化目标，RLHF 预设在偏好（Preference）、奖励（Reward）和代价（Cost）三个概念上实现了思想汇合。偏好模型（Model of Preference）、奖励函数（Reward Function）和代价景观（Cost Landscape）都是不同学科用来描述领域内特定动作和/或状态的相对优劣的工具。这三种框架的历史可以追溯到概率论（Probability Theory）和决策论（Decision Theory）的起源。1662 年，《皇家学院逻辑》（*The Port Royal Logic*）引入了关于决策质量的观念 [@arnauld1861port]：

> 要判断为获取善或避免恶必须做什么，就必须不仅要考虑善和恶本身，还要考虑它发生或不发生的概率。

这一理论伴随着现代科学思维的发展而发展，始于边沁（Bentham）的功利主义*快乐计算*（*Hedonic Calculus*），认为生活中的一切都可以被衡量 [@bentham1823hedonic]。这些思想首次定量应用出现在 1931 年拉姆齐（Ramsey）的*真理与概率*（*Truth and Probability*）[@ramsey2016truth] 中。

自这些著作以来，对人类偏好的量化、度量与影响一直是社会科学和行为科学中的一个活跃议题。这些争论很少在理论上得到解决；相反，不同的子领域和社会科学分支在偏好度量的方法和途径上达成了内部共识，即使它们在相互专业化发展的过程中，也经常在这个过程中发展出各自独特的语义。

少数经济学家认为，即使偏好存在，由于人们对自己的偏好有偏好、也对彼此的偏好有偏好，偏好难以进行合理的测量 [@hirschman1984against]。在这种观点中（这一观点并未反映在 RLHF 的流程中），个体偏好始终嵌入在更大的社会关系之中，因此任何偏好模型的准确性都取决于任务的定义和语境。一些行为经济学家甚至认为偏好并不存在——它们与其说是对人们真正价值的本体论陈述（Ontological Statement），不如说是一种方法论工具，用于间接捕捉心理倾向（Psychological Predispositions）、感知到的行为规范和伦理义务、对社会秩序的承诺或法律约束 [@hadfield2014microfoundations]。我们将在本章稍后部分讨论这项工作与冯·诺依曼-摩根斯坦（Von Neumann-Morgenstern, VNM）效用定理之间的联系，以及对量化偏好相关不可能定理的反驳。

另一方面，今日使用的强化学习优化方法围绕在试验中优化"折现未来奖励"（Reward-to-Go）的估计值而构建 [@sutton2018reinforcement]，这结合了奖励的概念与多步优化。术语*奖励*（Reward）源于操作性条件反射（Operant Conditioning）、动物行为学和*效果律*（*Law of Effect*）的研究 [@thorndike1927law; @skinner2019behavior]，在这里，奖励是衡量"一个动作有多好"的尺度（越高越好）。

Reward-to-go 沿用了效用（Utility）的概念，效用是理性（Rationality）的度量 [@briggs2014normative]，后被修改为度量或预测未来时间窗口内的奖励。在用于强化学习的数学工具的语境中，"utility-to-go" 的概念在 1960 年的控制论（Control Theory）中首次被提出，具体是在模拟电路（Analog Circuits）的背景下 [@widrow1960adaptive]。这些方法是围绕具有明确最优性定义、或智能体（Agent）目标数值表示的系统设计的。

强化学习（Reinforcement Learning）系统以使用折扣因子（Discount Factor）而闻名，即一个复合乘性因子 $\gamma \in [0,1]$，用于重新加权未来奖励。这些来自最优控制和早期强化学习的假设，与聚合多模态偏好（Multimodal Preferences）的奖励模型形成了鲜明对比。具体来说，RL 系统期望奖励以特定的方式运行，引自 [@singh2009rewards]：

> RL 系统中的奖励对应原始奖励（Primary Rewards），即因与繁殖成功相关而在动物中通过进化过程硬编码的奖励。
> ……此外，形成价值函数（Value Functions）的 RL 系统……实际上创造了条件性或次级奖励（Conditioned or Secondary Reward）过程，其中原始奖励的预测器本身作为奖励发挥作用……
> 结果是，价值函数的局部景观为系统的偏好行为提供方向：决策被做出以促使向更高价值状态的转移。
> 价值函数的梯度与激励动机（Incentive Motivation）之间存在密切的平行关系 [@mcclure2003computational]。

总而言之，奖励在 RL 系统中被用作一种信号，以将行为调谐到明确定义的目标上。其核心论点是：学习算法的性能与*期望适应性*（Expected Fitness）的概念紧密耦合，这渗透了一种流行观点，即 RL 方法是*智能体*（Agent）在环境中行动。这一观点与强化学习技术的发展密切相关，例如关于奖励公式化通用性的声明 [@silver2021reward] 即是典型代表，但当许多个体欲望被简化为单一函数时，这一观点便产生冲突。

## 优化效用的工具

现代强化学习方法严重依赖贝尔曼方程（Bellman Equation）[@bellman1957markovian; @howard1960dynamic] 来递归地计算奖励到去的估计值，这些方程是在可被建模为马尔可夫决策过程（Markov Decision Process, MDP）的封闭环境中推导出来的 [@sutton2018reinforcement]。RL 的这些起源受到动态规划（Dynamic Programming）方法的启发，并且最初纯粹作为最优控制（Optimal Control）技术而被开发（即当时 RL 尚不存在）。MDP 的公式化通过将环境结构化为具有不变的状态-动作（State-Action）分布的系统，为性能提供了理论保证。

"强化"（Reinforcement）一词来自心理学文献，在 1960 年代与这些现代方法交织在一起，成为*强化学习*（Reinforcement Learning）[@MENDEL1970287; @waltz1965]。早期强化学习研究利用奖励信号的监督学习（Supervised Learning）来完成任务。Harry Klopf 的工作重新引入了试错学习（Trial-and-Error Learning）的概念 [@klopf1972brain]，这对该领域在 1980 年代及之后的成功至关重要。

现代 RL 算法在此公式化的 RL 框架下构建，将其作为通过试错寻找最优行为的工具，但使用的条件更宽松。时序差分（Temporal-Difference, TD）学习的概念被开发出来，以帮助智能体解决信用分配（Credit Assignment）和数据收集问题，通过直接更新策略来完成——随着新数据的收集，策略也随之更新 [@sutton1988learning]，这一概念首先成功应用于双陆棋（Backgammon）[@tesauro1995temporal]（而非从大量累积经验的更新，这些经验可能因错误的过去价值预测而过时）。Q-learning 方法（现代许多 RL 形式的基础）通过贝尔曼方程学习一个模型，使用 TD 更新来决定每个状态-动作对（State-Action Pair）的有用性 [@watkins1992q]。^[The term "Q" is used in Q-learning to refer to a technical concept, the Q-function, which maps from any state-action to a scalar estimate of future reward. A value function maps from states to this same estimate.]

**译者补充**：Q-learning 中的"Q"指代 Q-function（Q 函数），它表示在某个状态下采取某个动作后所能获得的期望累积奖励。这与"价值函数"（Value Function）不同，后者只评估某个状态的价值而不考虑具体采取的动作。

关键的是，这些通过效用可证明的有用性概念仅被证明适用于被表述为 MDP 的领域，或具有单一封闭形式奖励函数（Closed-Form Reward Function）的任务，例如深度学习在博弈中取得的突出成功（DQN）[@mnih2013playing]。深度学习使得这些方法能够摄入更多数据并在高维度（High-Dimensionality）环境中工作。

随着方法变得更加通用和成功，ChatGPT 之前的大多数突出发展仍被局限在自适应控制（Adaptive Control）的语境中，其中的奖励和代价函数具有有限的成功概念 [@golnaraghi2017automatic]，例如物理系统一个 episode 中的最低能耗。著名的例子包括在游戏中的进一步成功 [@silver2017mastering]、控制复杂动态系统（如核聚变反应堆）[@degrave2022magnetic]，以及控制快速机器人系统 [@Kaufmann2023fpv]。大多数奖励或代价函数可以返回明确的最优行为，而人类偏好模型则不能。

鉴于深度强化学习（Deep RL）的成功，值得指出的是，关于这些方法为何成功的机制性理解（Mechanistic Understanding）并未得到充分记录。随着评估方法变得越来越复杂，该领域在统计分析方面容易出现错误 [@agarwal2021deep]。此外，RLHF 文献中很少提及逆强化学习（Inverse Reinforcement Learning, IRL）这一子领域。IRL 是基于智能体行为学习奖励函数的问题 [@ng2000algorithms]，与学习奖励模型高度相关。这主要反映了实现 RLHF 稳定路径的演进历程，并激励了对 IRL 方法的进一步投资和比较，以将其扩展到开放对话的复杂度。

## 优化偏好的复杂性

强化学习被设计的语境意味着奖励和代价被假定为稳定和决定性（Determinative）的。奖励和代价都被期望是函数：给定特定的状态-动作对，智能体接收一个固定的数值回报。当我们进入偏好领域时，情况不再如此——人类的偏好在经历过程中会不断漂移。

术语"value"（价值）的过度重载使 RLHF 文献变得复杂。在 RL 中，*value* 是对未来奖励的数值估计（如贝尔曼方程中所述）；在对齐（Alignment）讨论中，*value* 指的是一种道德或伦理原则。这两种含义截然不同，但它们共存于 RLHF 论文中，并非总是被区分开来。

这种张力出现的一个例子是奖励建模：模型试图将屏幕上的文本映射为一个标量信号（Scalar Signal），但问题规范中未捕捉到的动力学（Dynamics）会影响真正的决策 [@salha2011aesthetics; @gilbert2022choices]，例如连续标注大量示例并假设它们相互独立时的偏好偏移（Preference Shift）。最好情况而言，对偏好的建模是将多维奖励景观压缩为一个单一的标量函数。

理论上，冯·诺依曼-摩根斯坦（Von Neumann-Morgenstern, VNM）效用定理赋予设计者构建此类函数的权限，因为它将不确定性下的决策理论基础、偏好理论和抽象效用函数联系在了一起 [@von1947theory]；这些思想一起使得偏好能够以某个个体智能体的期望价值形式来进行建模。大多数 RL 研究中使用的 MDP 公式在理论上已被证明可以修改以适应 VNM 定理 [@pitis2019rethinking]，但这在实践中很少使用。具体来说，马尔可夫公式化在其表达能力上有限 [@pitis2023consistent]，而且向部分可观测过程（Partially-Observed Processes）的过渡（这对语言是必需的），进一步挑战了问题规范的精度 [@abel2021expressivity]。

然而，VNM 效用定理也调用了一些关于偏好本质以及偏好被测量的环境的假设，这些假设在 RLHF 的语境中受到了挑战。例如，人机交互（Human-Computer Interaction, HCI）研究人员强调，任何数值的偏好模型都可能无法捕捉到场景中的所有相关偏好。例如，选项的视觉呈现方式会影响人们的偏好 [@salha2011aesthetics]。这意味着，偏好表达（Representing Preferences）的重要性可能次于该表达如何被整合到可供人们使用的工具中。发展经济学的相关工作也呼应了这一点，表明显示偏好理论（Revealed Preferences）可能只是在重述*休谟的铡刀*（Hume's Guillotine）——即你无法从"是"中提取出"应当"——尤其是选择和偏好之间的差异（我想要什么？与 X 比 Y 更好吗？）[@sen1973behaviour]。

在数学层面上，社会选择理论中著名的不可能定理（Impossibility Theorems）表明，通过给定的偏好优化技术不能同时满足所有公平性标准（Fairness Criteria）[@arrow1950difficulty; @maskin2014arrow]。对这些定理的理论挑战是存在的，例如假设效用的人际比较（Interpersonal Comparison of Utility）是可行的 [@harsanyi1977rule]。这一假设启发了行为经济学中主代理问题（Principal-Agent Problem）在 AI 安全和价值对齐领域的一条丰富研究线 [@hadfield2016cooperative]，甚至可能包括多个委托人（Multiple Principals）[@fickinger2020multi]。然而，由此产生的效用函数可能与可纠正性（Corrigibility）的期望产生冲突，即 AI 系统与其创建者视为纠正性的干预相合作的能力 [@soares2015corrigibility]。哲学家们也指出偏好会随时间变化，引发了关于个人经验、人类决策本质以及不同语境的基本问题 [@pettigrew2019choosing]。围绕人们、地点和多样化情境中偏好聚合的这些冲突，是现代 RLHF 数据集工程的核心。

**译者注**：VNM 效用定理（Von Neumann-Morgenstern Utility Theorem）是决策论中的经典结果，它证明了在满足一定理性公理（如完备性、传递性、独立性、连续性）的条件下，任何理性的决策者都可以被描述为在最大化某个效用函数的期望值。然而，这一定理假设偏好是稳定、一致且可以数值化的——这在人类实际的偏好行为中常常不成立。因此将其直接应用于 RLHF 时需要格外谨慎。

在实践中，VNM 效用定理忽略了偏好也可能是不确定的——这是由于价值本身本质上具有动态性和不确定性。人类的决策受到生物学、心理学、文化和能动性（Agency）的影响，这些因素以影响其偏好的方式发挥作用，而这些原因并不适用于一个完美理性的智能体。因此，理论假设在实践中通过多种方式发生分歧：

- 当偏好被测量的环境变得更为复杂时，测量的偏好可能不具备传递性（Transitivity）或可相互比较；
- 代理度量（Proxy Measurements）可能从隐性数据（页面浏览时间、关闭标签页、向语言模型重复提问）中衍生而来，而没有探讨这些度量如何通过模型的未来训练和部署与它们所在的领域产生交互；
- 输入源的数量和呈现方式可能导致结果变化，例如允许受访者在两个以上的选项中进行选择，或在多个时间点或多个语境中从同一用户获取输入；
- RLHF 训练数据中受访者之间的准确度相对较低，这可能掩盖了用户之间的语境差异，偏好模型可以在不解决这些差异的情况下进行聚合或优化。