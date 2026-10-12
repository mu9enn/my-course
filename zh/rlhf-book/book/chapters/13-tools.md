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
Although the language model is generating a completion, if it is following this example, it would generate the tokens `search_movies("Star Wars")` to search for Star Wars.
This is often encoded inside special formatting tokens, and then the next tokens inserted into the sequence will contain the tool outputs.
With this, models can learn to accomplish more challenging tasks than many simple standalone models.

A popular form of tool use is code-execution, allowing the model to get precise answers to complex logic or mathematics problems.
For example, code-execution within a language model execution can occur during the thinking tokens of a reasoning model.
As with function calling, there are tags first for the code to execute (generated by the model) and then a separate tag for output.
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

What is happening under the hood is the language model is interleaving tool inputs and outputs with standard autoregressively generated tokens.
The orchestration loop that makes this possible looks something like:

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

![Tool use interleaves model generation with external execution: the model generates tokens until it emits a tool call (orange), an external system executes the tool and injects the output (purple) into the sequence, then the model continues generating. Models can emit multiple tool calls in a single generation. During training, tool call and output tokens are typically masked from the loss.](images/tool_use_generation.png){#fig:tool-use-generation data-dark-src="images/tool_use_generation-dark.png"}

Training for tool use is about getting the model to behave predictably with this different token flow—knowing when to emit a tool call, how to format arguments correctly, and how to incorporate results into its response.
Open models must be trained to work with a variety of tools that users may connect off the shelf.

## Multistep Tool Reasoning

OpenAI's o3 model represented a substantial step-change in how multi-step tool-use can be integrated with language models.
This behavior is related to much earlier research trends in the community.
For example, ReAct [@yao2023react] showcased how actions and reasoning can be interleaved into one model generation:

> In this paper, we explore the use of LLMs to generate both reasoning traces and task-specific actions in an interleaved manner, allowing for greater synergy between the two: reasoning traces help the model induce, track, and update action plans as well as handle exceptions, while actions allow it to interface with and gather additional information from external sources such as knowledge bases or environments.

With the solidification of tool-use capabilities and the take-off of reasoning models, multi-turn tool-use has grown into an exciting area of research [@wang2025ragenunderstandingselfevolutionllm].
Training these multi-step behaviors with RL resembles classic reinforcement learning more than the per-sample RLHF loop: the agent interacts with an environment and its tools over a full trajectory before any reward is assigned, as shown in @fig:tool-use-rl.

![Reinforcement learning for multi-step tool use. A prompt is sampled from the training data and the agent (policy $\pi_\theta$) interacts with the environment and its tools over a trajectory, alternating actions $a_t$ with observations $o_t$. The completed trajectory is graded or verified to produce a single reward $r_T$ at the end, which drives the policy update. Unlike the per-sample RLHF loop, the reward arrives only after a multi-step rollout -- closer to classic RL.](images/tool_use_rl_loop.png){#fig:tool-use-rl data-dark-src="images/tool_use_rl_loop-dark.png"}

## Model Context Protocol

Model Context Protocol (MCP) is an open standard for connecting language models to external data sources and information systems [@anthropic_mcp_2024].
At the data layer, MCP uses JSON-RPC 2.0 with discovery and execution methods for its primitives.
Rather than requiring specific tool call formatting per external system, MCP enables models to access rich contextual information through a standardized protocol.

MCP is a simple addition on top of the tool-use content in this chapter -- it is how applications pass context (data + actions) to language models in a predictable JSON schema. 
MCP servers that the models interact with have core primitives: resources (read-only data blobs), prompts (templated messages/workflows), and tools (functions the model can call). 
With this, the MCP architecture can be summarized as:

- MCP servers wrap a specific data source or capability.
- MCP clients (e.g., Claude Desktop, IDE plug-ins) aggregate one or more servers.
- Hosts, e.g. Claude or ChatGPT applications, provide the user/LLM interface; switching model vendors or back-end tools only means swapping the client in the middle.

MCP enables developers of tool-use models to use the same infrastructure to attach their servers or clients to different models, and at the same time models have a predictable format they can use to integrate external components.
These together make for a far more predictable development environment for tool-use models in real-world domains.

An MCP server exposes tools to clients through a standardized JSON schema:
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

A minimal Python MCP server implementing this tool:
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

## Implementation Details

There are multiple formatting and masking decisions when implementing a tool-use model:

- **Python vs. JSON formatting**: In this chapter, we include examples that format tool use as both JSON data structures and Python code. Models tend to select one structure, whereas different providers across the industry use different formats.
- **Masking tool outputs**: An important detail when training tool-use models is that the tokens in the tool output are masked from the model's training loss. This ensures the model is not learning to predict the output of the system that processes the tool call (as the results are not tokens generated by the model).
- **Multi-turn formatting for tool invocations**: It is common practice when implementing tool-calling models to add more structure to the data-loading format. Standard practice for post-training datasets is a list of messages alternating between user and assistant (and often a system message). The overall structure is the same for tool-use, but the turns of the model are split into subsections of content delimited by each tool call. An example is below.

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

- **Tokenization and message format details**: Tool calls in OpenAI messages format often undergo tokenization through chat templates (the code for controlling the format of messages sent to the model), converting structured JSON representations into raw token streams. This process varies across model architectures---some use special tokens to demarcate tool calls, while others maintain structured formatting within the token stream itself. [Chat template playgrounds](https://huggingface.co/spaces/huggingfacejs/chat-template-playground?modelId=Qwen/Qwen3-8B) provide an interactive environment to explore how different models convert message formats to token streams.
- **Reasoning token continuity**: As reasoning models have emerged, with their separate token stream of "reasoning" before an answer, different implementations exist for how they're handled with tool-use in the loop. Some models preserve reasoning tokens between tool-calling steps within a single turn, maintaining context across multiple tool invocations. However, these tokens are typically erased between turns to minimize serving cost (but they aren't always -- this is a design decision).
- **API formatting across providers** (as of May 2026): Different providers use conceptually similar but technically distinct formats. OpenAI's Chat Completions API uses `tool_calls` arrays with unique IDs, while the newer Responses API represents calls as `function_call` items and returns results as `function_call_output` items keyed by `call_id`. Anthropic defines tools with `input_schema` and represents calls and results as `tool_use` and `tool_result` content blocks. Gemini exposes function-calling modes such as `AUTO`, `ANY`, `NONE`, and, in supported Gemini and Vertex AI configurations, `VALIDATED`.
- **Schema conformance and constrained decoding**: Production systems often enforce valid JSON and correct argument types using constrained decoding or "strict mode" options, reducing retries from malformed outputs. Some closed model providers do additional post-training specifically to make structured JSON output reliable, whereas for open models this is handled as an inference flag in systems like vLLM.
- **Tool output context consumption**: Tool outputs can quickly consume the model's context window, especially with search or retrieval tools that return many results. Systems must decide how to truncate, summarize, or paginate tool outputs to keep context manageable while preserving the information the model needs to continue.

Tying this back to post-training: where does tool-use training data come from, and what objectives are used?
Human-written tool traces are expensive to collect, so most modern tool-use corpora are synthetic or bootstrapped—Toolformer-style self-labeling [@schick2023toolformerlanguagemodelsteach] or large-scale generation as in ToolBench [@qin2023toollm].
For training objectives, supervised fine-tuning (SFT) on tool trajectories teaches basic formatting and tool selection. 
This bootstraps the behavior and is often enough for establishing the foundation of the skill.
Preference optimization (e.g., DPO) over trajectories can improve decisions about when to call a tool versus answer directly.
For agentic tasks with multi-step tool use, RL with environment feedback (task success, constraint satisfaction) becomes the natural objective -- the model learns from whether its tool-augmented actions actually solved the problem.
