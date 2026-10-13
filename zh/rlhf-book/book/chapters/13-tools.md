<!--
  Copyright (c) 2025-2026 Nathan Lambert.
  Licensed under CC BY-NC-SA 4.0:
  https://creativecommons.org/licenses/by-nc-sa/4.0/
  Full license: https://github.com/natolambert/rlhf-book/blob/main/LICENSE-CHAPTERS
-->
---
prev-chapter: "合成数据与蒸馏"
prev-url: "12-synthetic-data"
page-title: 工具调用与函数调用
search-title: "第 13 章：工具调用与函数调用"
meta-description: "工具调用和函数调用作为训练更强大的语言模型产品和智能体的后训练目标。"
next-chapter: "过度优化"
next-url: "14-over-optimization"
lectures:
  - video: "https://www.youtube.com/watch?v=GMry2DzC304&list=PLL1tdVxB1CpVpEtMHxwuR4uI4Lxjw00_y&index=17"
    label: "第 11 讲：工具调用、函数调用与通往智能体之路"
---

# 工具调用与函数调用

让语言模型使用外部工具是扩展其能力的一种自然方式，尤其适用于对精度要求高的任务——外部工具中包含所需的信息，或智能体需要与复杂的 Web 系统交互的场景。工具调用是一项语言模型需要接受训练才能获得的能力，RLHF 以及本书介绍的其他方法都可以进一步优化它。

考虑一个来自用户的提问：

> **用户**：今天的总统是谁？

一个没有工具的语言模型会因为预训练数据的知识截止期而难以回答这个问题，但通过一次搜索查询就能轻松获得该信息。

再看另一个例子：

> **用户**：把我下载文件夹里所有的 arXiv 论文移动到 ~/research/ 目录，文件名需要标明论文的日期。

这是仅靠模型权重根本无法完成的任务——工具的使用让语言模型得以处理更广泛范围的任务。

在深入之前，区分那些常被混用的相关术语很有必要：

- **工具调用（Tool use）**：模型发出一个结构化请求（工具名称和参数）；由调度器执行该工具；结果被追加到上下文中；模型继续生成。
- **函数调用（Function calling）**：参数必须符合一组声明的函数模式（通常为 JSON Schema）的工具调用，可实现可靠解析和校验。
- **代码执行（Code execution）**：工具调用的一个特例，其中"工具"是一个代码解释器（如 Python）；结果以工具输出的形式返回。

## 工具调用概览

AI 模型通过输出特殊 token 来触发特定端点，从而使用任何外部工具。这些工具可以是高度专门化的函数（如查询某地天气），也可以是作为复杂行为基础构建模块的代码解释器或搜索引擎。我们之前的例子展示了语言模型需要比其基于过往数据训练的固定权重更最新的信息，但还有一些工具（如代码执行），能让语言模型规避其概率性、生成式的本质，返回精确答案。

考虑将 π 打印为 50 位近似值这一任务（如果不从记忆中背诵，就存在幻觉风险）。一个拥有工具的语言模型可以这样做：

```text
<code>
from decimal import Decimal, getcontext
getcontext().prec = 60

def compute_pi():
    # Chudnovsky algorithm for computing pi
    C = 426880 * Decimal(10005).sqrt()
    K, M, X, L, S = 0, 1, 1, 13591409, Decimal(13591409)
    for i in range(1, 100):
        M = M * (K**3 - 16*K) // ((i)**3)
        K += 12
        L += 545140134
        X *= -262537412640768000
        S += Decimal(M * L) / X
    return C / S

print(str(compute_pi())[:52])
</code>

<output>
3.14159265358979323846264338327950288419716939937510
</output>
```

本章将介绍现代语言模型中工具调用的起源、基本知识与格式规范，以及顶级模型在使用工具方面的当前权衡。

"工具调用"（tool use）这一术语的确切起源已不可考，但这一思想的渊源远远早于 RLHF 广泛传播的后 ChatGPT 时代。2015 年前后的早期尝试试图构建在现代语言模型之前就存在的系统，例如神经程序员解释器（Neural Programmer-Interpreters, NPI）[@reed2015neural]——"一种循环且可组合的神经网络，学习表示和执行程序。"

随着语言模型日益流行，许多子领域都在使用外部能力的集成来增强性能。为了获取模型权重之外的信息，许多人使用了检索增强生成（Retrieval Augmented Generation）[@lewis2020retrieval] 或网页浏览 [@nakano2021webgpt]。不久之后，其他人开始探索将语言模型与程序 [@gao2023pal] 或工具 [@parisi2022talm] 集成的方案。

随着这一领域的成熟，这些模型在底层语言建模能力大幅提升的同时，也获得了更复杂的能力。例如，Toolformer 可以使用"计算器、问答系统、两种不同的搜索引擎、翻译系统和日历" [@schick2023toolformerlanguagemodelsteach]。

随后，Gorilla 被训练使用 1645 个 API（来自 PyTorch Hub、TensorFlow Hub v2 和 Hugging Face），其评估基准 APIBench 成为热门的伯克利函数调用排行榜（Berkeley Function Calling Leaderboard）的基础 [@patil2023gorilla]。自这些早期模型以来，被调用的动作多样性大幅增长。

如今，工具调用模型已与常规的语言模型交互深度交织在一起。模型上下文协议（Model Context Protocol, MCP）作为一种通用的格式化方案出现，用于将语言模型与外部数据源（或工具）连接 [@anthropic_mcp_2024]。凭借更强大的模型和更好的格式，工具调用的语言模型已应用于诸多场景，包括 Microsoft Office 或 Google Workspace 等流行应用中的生产力辅助工具、科学领域 [@bran2023chemcrow]、医疗领域 [@li2024mmedagent]、Claude Code 或 Cursor 等编程智能体 [@zhang2024codeagent]、数据库集成，以及许多其他自主工作流。

评估工具调用模型涉及多个维度：工具名称和参数正确性的精确匹配指标、模式（schema）有效性，以及在模拟环境中的端到端任务完成度。跨试验的可靠性同样重要——$\tau$-bench 引入了 pass^k 指标（区别于 pass@k），用于衡量智能体是否持续成功而非偶尔成功 [@yao2024taubench]。ToolLLM 及其 ToolBench 数据集为在 16,000 多个真实 API 上训练和评估工具使用提供了一个大规模框架 [@qin2023toollm]，而伯克利函数调用排行榜（Berkeley Function Calling Leaderboard, BFCL）仍是比较模型函数调用准确度的热门基准 [@patil2023gorilla]。

## Interweaving Tool Calls in Generation

Training data for function calling looks much like other post-training data, with one addition: a system prompt that instructs the model what tools it has available.
An example formatted data point with the system prompt and tools available in JSON format is shown below:
```xml
<system>
You are a function-calling AI model. You are provided with function signatures within <functions></functions> XML tags. You may call one or more functions to assist with the user query. Don't make assumptions about what values to plug into functions.
</system>

<functions>
[
  {
    "name": "search_movies",
    "description": "Search for movies by title and return matching results with IDs.",
    "parameters": {
      "type": "object",
      "properties": {
        "query": {
          "type": "string",
          "description": "The search string for the movie title."
        }
      },
      "required": ["query"]
    }
  },
  {
    "name": "get_movie_details",
    "description": "Fetch detailed information about a movie including cast, runtime, and synopsis.",
    "parameters": {
      "type": "object",
      "properties": {
        "movie_id": {
          "type": "string",
          "description": "The unique identifier for the movie."
        }
      },
      "required": ["movie_id"]
    }
  },
  {
    "name": "get_showtimes",
    "description": "Get movie showtimes for a given location and date.",
    "parameters": {
      "type": "object",
      "properties": {
        "movie_id": {
          "type": "string",
          "description": "The unique identifier for the movie."
        },
        "zip_code": {
          "type": "string",
          "description": "ZIP code for theater location."
        },
        "date": {
          "type": "string",
          "description": "Date for showtimes in YYYY-MM-DD format."
        }
      },
      "required": ["movie_id", "zip_code"]
    }
  }
]
</functions>

<user>
...
</user>
``` 
虽然语言模型在生成补全内容，但如果它遵循这个示例，它会生成 token `search_movies("Star Wars")` 来搜索《星球大战》。这些通常被编码在特殊的格式标记内，接下来插入序列的 token 将包含工具输出。有了这种机制，模型可以学习完成比许多简单独立模型更复杂的任务。

一种流行的工具调用形式是代码执行，它让模型能够对复杂的逻辑或数学问题给出精确答案。例如，在推理模型（reasoning model）的 thinking token 期间，语言模型的执行过程中就可以进行代码执行。与函数调用类似，首先有标签包裹要执行的代码（由模型生成），然后有单独的标签包裹输出。
```text
<|user|>
What is the 50th Fibonacci number? (Use the standard F_0=0, F_1=1 indexing.)</s>
<|assistant|>
<think>
Okay, I will compute the 50th Fibonacci number with a simple loop, then return the result.

<code>
def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

fib(50)
</code>

<output>
12586269025
</output>
</think>
<answer>
The 50th Fibonacci number is 12 586 269 025.
</answer>
```

幕后发生的事情是，语言模型将工具输入和输出与标准的自回归生成 token 交织在一起。实现这一点的调度循环大致如下：

```python
messages = [...]
while True:
    response = model(messages, tools=tools)
    if not response.tool_calls:
        return response.text

    for call in response.tool_calls:
        result = execute_tool(call.name, call.args)
        messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
```

![工具调用将模型生成与外部执行交织在一起：模型生成 token，直到发出工具调用（橙色），外部系统执行该工具并将输出（紫色）注入序列，然后模型继续生成。模型可以在单次生成中发出多个工具调用。训练期间，工具调用和输出的 token 通常被遮蔽以排除在损失函数之外。](images/tool_use_generation.png){#fig:tool-use-generation data-dark-src="images/tool_use_generation-dark.png"}

工具调用的训练目标是让模型在这套不同的 token 流中表现出可预测的行为——知道何时发出工具调用、如何正确格式化参数，以及如何将结果融入回复中。开源模型必须经过训练，才能与用户可能即插即用的各种工具协同工作。

## 多步工具推理

OpenAI 的 o3 模型在如何将多步工具调用与语言模型集成方面实现了显著的跨越。这种行为与社区中更早的研究趋势有关。例如，ReAct [@yao2023react] 展示了如何将行动与推理交织为同一次模型生成：

> 在本文中，我们探索使用大语言模型以交织方式同时生成推理轨迹和特定于任务的操作，从而使两者产生更大协同效应：推理轨迹帮助模型推导、跟踪和更新操作计划以及处理异常情况，而操作则允许它与知识库或环境等外部源进行交互并收集额外信息。

（译者注：ReAct 的核心思想是让模型在一次生成中交替输出推理步骤和工具调用，使推理指导工具选择，工具结果又反过来影响后续推理。）

随着工具调用能力的成熟和推理模型的兴起，多轮工具调用已成为一个引人注目的研究领域 [@wang2025ragenunderstandingselfevolutionllm]。使用强化学习训练这些多步行为，与传统强化学习（而非逐样本 RLHF 循环）更为相似：智能体在分配任何奖励之前，会先与环境及其工具在整个轨迹上进行交互，如 @fig:tool-use-rl 所示。

![多步工具调用的强化学习。从训练数据中采样一个 prompt，智能体（策略 $\pi_\theta$）在轨迹上与环境及其工具交互，动作 $a_t$ 与观测 $o_t$ 交替出现。完成的轨迹被评估或验证后，在末尾产生单一奖励 $r_T$，驱动策略更新。与逐样本 RLHF 循环不同，奖励只在多步 rollout 之后才到达——更接近经典 RL。](images/tool_use_rl_loop.png){#fig:tool-use-rl data-dark-src="images/tool_use_rl_loop-dark.png"}

## 模型上下文协议（Model Context Protocol）

模型上下文协议（Model Context Protocol, MCP）是一个用于将语言模型连接到外部数据源和信息系统的开放标准 [@anthropic_mcp_2024]。在数据层，MCP 使用 JSON-RPC 2.0，并为其基本原语提供发现和执行方法。MCP 不要求每个外部系统使用特定的工具调用格式，而是让模型能够通过标准化协议访问丰富的上下文信息。

MCP 是在本章工具调用内容之上的一个简单增强——它是应用程序以可预测的 JSON 模式向语言模型传递上下文（数据 + 操作）的方式。模型与之交互的 MCP 服务器拥有核心原语：资源（只读数据块）、提示（模板化消息/工作流）和工具（模型可调用的函数）。

由此，MCP 架构可以总结为：

- MCP 服务器封装特定的数据源或能力。
- MCP 客户端（如 Claude Desktop、IDE 插件）聚合一个或多个服务器。
- 宿主（如 Claude 或 ChatGPT 应用）提供用户/语言模型接口；更换模型供应商或后端工具只需替换中间的客户端。

MCP 让工具调用模型的开发者可以使用相同的基础设施将他们的服务器或客户端连接到不同的模型，同时模型也有一个可预测的格式，可以用来集成外部组件。这些特性共同使得工具调用模型在现实领域中的开发环境更加可预测。

MCP 服务器通过标准化的 JSON 模式向客户端暴露工具：
```json
{
  "name": "get_weather",
  "description": "Get current weather for a location",
  "inputSchema": {
    "type": "object",
    "properties": {
      "location": {
        "type": "string",
        "description": "City name or coordinates"
      }
    },
    "required": ["location"]
  }
}
```

实现该工具的极简 Python MCP 服务器：
```python
from mcp.server import Server
from mcp.types import Tool, TextContent

server = Server("weather-server")

@server.list_tools()
async def list_tools():
    return [Tool(
        name="get_weather",
        description="Get current weather",
        inputSchema={
            "type": "object",
            "properties": {"location": {"type": "string"}},
            "required": ["location"]
        }
    )]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "get_weather":
        weather = fetch_weather(arguments["location"])
        return [TextContent(type="text", text=weather)]
```

## 实现细节

在实现工具调用模型时，有多个格式化和掩码（masking）决策需要考虑：

- **Python 格式 vs JSON 格式**：本章中我们包含了将工具调用格式化为 JSON 数据结构和 Python 代码的例子。模型往往会选择其中一种结构，而行业内不同提供商使用不同的格式。
- **掩码工具输出**：训练工具调用模型时一个重要细节是，工具输出中的 token 需要从模型的训练损失中掩码掉。这确保模型不会学习到预测处理工具调用的系统的输出（因为这些结果并非由模型生成的 token）。
- **多轮工具调用的格式**：在实现工具调用模型时，常见做法是为数据加载格式增加更多结构。后训练数据集的标准做法是 user 和 assistant 交替的消息列表（通常还包含 system 消息）。整体结构对工具调用也是一样的，但模型的轮次被拆分为由每次工具调用分隔的内容子段落。如下所示。

```python
messages = [
{
"content": "You are a function calling AI model. You are provided with function signatures within <functions></functions> XML tags. You may call one or more functions to assist with the user query. Don't make assumptions about what values to plug into functions.",
"function_calls": null,
"functions": "[{\"name\": \"live_giveaways_by_type\", \"description\": \"Retrieve live giveaways from the GamerPower API based on the specified type.\", \"parameters\": {\"type\": {\"description\": \"The type of giveaways to retrieve (e.g., game, loot, beta).\", \"type\": \"str\", \"default\": \"game\"}}}]",
"role": "system"
},
{
"content": "Where can I find live giveaways for beta access and games?",
"function_calls": null,
"functions": null,
"role": "user"
},
{
"content": null,
"function_calls": "live_giveaways_by_type(type='beta')\nlive_giveaways_by_type(type='game')",
"functions": null,
"role": "assistant"
}
]
```

- **分词和消息格式细节**：OpenAI 消息格式中的工具调用通常需要经过聊天模板（控制发送模型的消息格式的代码）进行分词，将结构化的 JSON 表示转换为原始 token 流。这个过程在不同模型架构之间有所不同——一些模型使用特殊 token 来标记工具调用，另一些则在 token 流内部维持结构化格式。[聊天模板实验室](https://huggingface.co/spaces/huggingfacejs/chat-template-playground?modelId=Qwen/Qwen3-8B) 提供了一个交互式环境，用于探索不同模型如何将消息格式转换为 token 流。
- **推理 token 的连续性**：随着推理模型的出现（它们在答案前有独立的"推理"token 流），对于如何在工具调用循环中处理这些 token 存在不同的实现方式。一些模型在单个轮次内的工具调用步骤之间保留推理 token，在多次工具调用之间维持上下文。然而，这些 token 通常在轮次之间被清除以最小化服务成本（不过并非总是如此——这是一项设计决策）。
- **跨提供商的 API 格式**（截至 2026 年 5 月）：不同提供商使用概念上相似但技术上不同的格式。OpenAI 的 Chat Completions API 使用带有唯一 ID 的 `tool_calls` 数组，而更新的 Responses API 将调用表示为 `function_call` 项，以 `call_id` 为键返回 `function_call_output` 项。Anthropic 使用 `input_schema` 定义工具，将调用和结果表示为 `tool_use` 和 `tool_result` 内容块。Gemini 暴露了 `AUTO`、`ANY`、`NONE` 等函数调用模式，在支持的 Gemini 和 Vertex AI 配置中还有 `VALIDATED` 模式。
- **模式合规与约束解码**：生产系统经常使用约束解码（constrained decoding）或"严格模式"（strict mode）选项来确保有效的 JSON 和正确的参数类型，从而减少因格式错误输出导致的重试。一些闭源模型提供商额外进行后训练以使结构化 JSON 输出更加可靠，而对于开源模型，这通常在 vLLM 等系统中作为推理参数来处理。
- **工具输出的上下文消耗**：工具输出可能迅速消耗模型的上下文窗口，特别是返回大量结果的搜索或检索工具。系统必须决定如何截断、总结或分页工具输出，在保持上下文可管理的同时保留模型继续操作所需的信息。

回到后训练：工具调用的训练数据从哪里来，又使用什么目标函数？

人工编写工具调用轨迹的成本很高，因此大多数现代工具调用语料库是合成数据或自举数据——类似于 Toolformer 风格的自我标注 [@schick2023toolformerlanguagemodelsteach] 或 ToolBench [@qin2023toollm] 的大规模生成。

就训练目标而言，在工具轨迹上的监督微调（SFT）教授基本的格式和工具选择。这为行为提供了基础，通常足以建立这项技能的基础。对轨迹进行偏好优化（如 DPO）可以改善关于何时调用工具而非直接回答的决策。对于具有多步工具调用的智能体任务，使用环境反馈（任务成功、约束满足）的强化学习成为自然的目标——模型从其增强工具的行动是否真正解决了问题中学习。
