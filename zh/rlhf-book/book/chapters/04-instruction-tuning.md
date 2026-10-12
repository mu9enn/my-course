<!--
  Copyright (c) 2025-2026 Nathan Lambert.
  Licensed under CC BY-NC-SA 4.0:
  https://creativecommons.org/licenses/by-nc-sa/4.0/
  Full license: https://github.com/natolambert/rlhf-book/blob/main/LICENSE-CHAPTERS
-->
---
prev-chapter: "训练概览"
prev-url: "03-training-overview"
page-title: 指令微调
search-title: "第 4 章：指令微调"
meta-description: "指令微调如何将基础语言模型转化为可用的助手，并为后续的 RLHF 和后训练阶段做好准备。"
next-chapter: "奖励建模"
next-url: "05-reward-models"
lectures:
  - video: "https://www.youtube.com/watch?v=4gIwiSPmQkU&list=PLL1tdVxB1CpVpEtMHxwuR4uI4Lxjw00_y&index=3"
    label: "讲座 2：指令微调、奖励建模、拒绝采样（第 4、5、9 章）"
---

# 指令微调

早期的大规模预训练语言模型以后续词元预测（next-token prediction）为目标进行训练，默认情况下并不带有用于遵循指令的显式接口。
GPT-3 发布前后 [@brown2020language]，提示（prompting）和上下文学习（in-context learning）成为一种被广泛采用的方式，通过给出示例并在上下文中让模型完成类似任务，将单个模型适配到多个任务上（尽管针对特定任务进行微调仍然很常见）。
一个合乎逻辑的下一步是指令微调（instruction fine-tuning），它教会模型以"指令-回答"的格式进行响应，而不仅仅是续写文本。
例如，给定提示"What is the capital of France?"，基础模型可能会继续输出"What is the capital of Germany? What is the capital of Italy?…"——仅仅是延续了问题的模式——而经过指令微调的模型则会回答"The capital of France is Paris."。

指令微调的兴起源于两条研究路线的交汇。
首先，自然语言处理（NLP）从为每个任务量身定制的微调设置转向了统一的"文本到文本"或指令框架，这使得标准化多样化数据集并训练跨越多个任务的单一模型变得直接可行。
统一任务框架的代表性工作包括：*Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer*（T5 模型）[@raffel2020exploring]、*Finetuned Language Models Are Zero-Shot Learners*（FLAN 数据集）[@wei2021finetuned]、*Multitask Prompted Training Enables Zero-Shot Task Generalization*（T0 模型）[@sanh2021multitask]，以及 *Cross-Task Generalization via Natural Language Crowdsourcing Instructions*（Natural Instructions 数据集）[@mishra2021cross]。
其次，预训练语言模型的规模放大以及提示/上下文学习的兴起表明，单个模型可以跨任务泛化，但当模型显式地用"指令-回答"示例进行训练时，这种泛化能力会变得更加可靠。
这些趋势共同开启了在大规模指令集合上对预训练语言模型进行微调的时代——也就是如今通常所称的指令微调（instruction fine-tuning, IFT）或监督微调（supervised fine-tuning, SFT），使得训练通用模型的能力走向了更广泛的社区。

自被发现以来，指令微调（也称口语化简称为 *instruction tuning*）已日趋成熟，成为许多语言建模流水线中的标准实践。
其核心而言，IFT 是将语言模型适配到目标任务分布的最简单方法。
它为 RLHF 打下了基础：通过让模型熟悉"问答"这一类指令格式来做好准备，同时也是尝试将现代技术应用于新领域时的第一个工具。
如果没有基本的指令遵循能力，本书中讨论的大多数流水线——从偏好数据收集到在线 RLHF 优化——都无法进行。

指令微调在其他地方已有大量论述，本质上属于监督学习，因此本章重点介绍对 RLHF 从业者最有意义的实践细节：训练数据如何格式化和组织。
数据和格式上的决策将在后续的训练阶段中直接使用，以便为模型吸收后训练数据建立统一的语言。

## 聊天模板与指令的结构

后训练过程的第一步是定义一种模式，用于格式化用户查询，使其能够被通过 tokenizer 处理信息的语言模型轻松读取。
在使用预训练语言模型时，提示的方式非常简单。模型只认识少数几种 token：起始序列 token（例如 `<bos_token>`）、结束序列 token（例如 `<eos_token>`），以及填充 token（用于处理包含空元素的批量训练）。
因此，要提示基础模型，用户需要输入一段 token 序列让模型进行续写，例如：

```text
<bos_token> The capital of the United States is
```

接下来，模型会持续生成 token，直到其上下文窗口耗尽，或者生成了结束序列 token。

从指令调调到 RLHF 和其他方法，所有后训练阶段都依赖这种格式化方式。
负责处理与用户交互结构的工具被称为**聊天模板（chat template）**。

下面是一个我们将逐步拆解的示例：

```jinja
{% if messages[0]['role'] == 'system' %}
    {# If the conversation begins with a system message, treat it as a special first turn.
       We set an offset so the user/assistant alternation check lines up correctly. #}
    {% set offset = 1 %}
{% else %}
    {# No system message: user should be the first non-empty turn. #}
    {% set offset = 0 %}
{% endif %}

{# Emit the beginning-of-sequence token (model-specific). #}
{{ bos_token }}

{# Serialize each message into the model's chat-markup tokens. #}
{% for message in messages %}
    {# Enforce role alternation: (system), user, assistant, user, assistant, ...
       The boolean expression compares "is this a user message?" against whether the
       current index (plus offset) is expected to be user or assistant. #}
    {% if (message['role'] == 'user') != (loop.index0 % 2 == offset) %}
        {{ raise_exception('Conversation roles must alternate user/assistant/user/assistant/...') }}
    {% endif %}

    {# Wrap each message with special tokens:
       - <|im_start|><role>\n
       - message content (trimmed)
       - <|im_end|>\n
       This produces a single flat token sequence the LM can train on. #}
    {{ '<|im_start|>' + message['role'] + '\n' + message['content'] | trim + '<|im_end|>\n' }}
{% endfor %}

{# Optionally append an "assistant" start tag with no content.
   This cues generation to continue from the assistant role. #}
{% if add_generation_prompt %}
    {{ '<|im_start|>assistant\n' }}
{% endif %}
```
这是将包含消息和角色信息的 Python 字典列表转换为语言模型可以预测的 token 的原始代码。

所有传递给模型的输入都会被分配一个角色。
传统的三个角色是 `system`、`user` 和 `assistant`。

`system` 标签仅用于对话的第一条消息；它保存对智能体（agent）的指令，这些指令不会从用户处接收，也不会向用户展示。
这些**系统提示（system prompts）**用于为模型提供额外的上下文信息，例如当前日期和时间，或者用于补充行为规则。
举个有趣的例子，可以告诉模型"You are a friendly chatbot who always responds in the style of a pirate."。

接下来，另外两个角色就很直观了：**user** 保存使用 AI 的人发送的消息，**assistant** 保存来自模型的响应（即扮演 AI 助手的回答）。

为了将所有这些信息转换为 token，我们使用上面开始的代码。模型有一系列 *特殊 token*，用于分隔不同的消息。
如果我们用示例查询"How many helicopters can a human eat in one sitting?"运行上述代码，输入模型的 token 序列将如下所示：

```text
<|im_start|>system
You are a friendly chatbot who always responds in the style of a pirate<|im_end|>
<|im_start|>user
How many helicopters can a human eat in one sitting?<|im_end|>
<|im_start|>assistant
```

注意序列末尾的 token 是 `<|im_start|>assistant`. This is how the model knows to continue generating tokens until it finally generates its end-of-sequence token, which in this case is `<|im_end|>`.

By packing all question-answer pair data (and downstream preference tuning data) into this format, modern language models follow it with perfect consistency. This is the language that instruction-tuned models use to exchange information with users and the models running on GPUs or other computing devices.

The behavior can be extended naively to multiple turns, as shown below:

```text
<|im_start|>system
You are a friendly chatbot who always responds in the style of a pirate<|im_end|>
<|im_start|>user
How many helicopters can a human eat in one sitting?<|im_end|>
<|im_start|>assistant
Oh just 6.<|im_end|>
<|im_start|>user
Are you sure about that?<|im_end|>
<|im_start|>assistant
```

In the open ecosystem, the standard method for applying the chat template to a list of messages uses a Jinja snippet stored in the tokenizer configuration, as `apply_chat_template`.

The above chat template is a derivative of OpenAI's Chat Markup Language (ChatML), which was an early attempt to standardize message formatting.
Now, OpenAI and other model providers use a hierarchical system where the user can configure a system message, yet there are higher-level instructions that may or may not be revealed to the user [@wallace2024instruction].

Many other chat templates exist. Some other examples include Zephyr's [@tunstall2023zephyr]:

```text
<|system|>
You are a friendly chatbot who always responds in the style of a pirate</s>
<|user|>
How many helicopters can a human eat in one sitting?</s>
<|assistant|>
```

Or Tülu's:

```text
<|user|>
How are you doing?
<|assistant|>
I'm just a computer program, so I don't have feelings, but I'm functioning as expected. How can I assist you today?<|endoftext|>
```

Beyond this, many chat templates include formatting and other tokens for tasks such as tool-use.


## Best Practices for Instruction Tuning

Instruction tuning as the foundation of post-training and creating helpful language models is well-established.
There are many ways to achieve successful instruction tuning.
For example, efficient fine-tuning with quantization of some model parameters makes training very accessible [@dettmers2023qlora].
Also, in narrow domains such as chat alignment, i.e., without harder skills such as math or code, small, focused datasets can achieve strong performance [@zhou2023lima].

Soon after the release of ChatGPT, human datasets with as few as 10K samples such as No Robots were state-of-the-art [@no_robots].
Years later, large-scale synthetic datasets work best [@lambert2024t] on most tasks.

A few principles remain:

- High-quality data is key to performance. The completions are what the model actually learns from (in many cases the prompts are not predicted over so the model does not learn to predict prompts).
- Around 1M prompts can be used to create a model capable of excellent RLHF and post-training. Further scaling can still help, but returns diminish quickly.
- The best prompts are those in a similar distribution to downstream tasks of interest.
- If multiple stages of training are done after instruction tuning, the models can recover from some noise in the instruction-tuning data. Crafting the overall optimization is more important than fixating on each individual stage.

## Implementation Details

While the loss function is the same as that used in pretraining, there are a few key implementation details that differ from the setting used for pretraining.
Many practices, such as deciding on the types of parallelism used to shard models across many GPUs, are the same as pretraining, but the total number of machines used is often lower (for the first technical change listed below):

- **Smaller batch sizes**: Compared to pretraining, instruction tuning (and other post-training techniques such as preference fine-tuning) use substantially smaller batch sizes to optimize well on a narrower data distribution while preserving the model's generalization from pretraining. For example, OLMo 2 uses a batch size of 1024 packed-rows for the 7B and 2048 for the 13B pretraining, where these models have a total context length of 4096 tokens, and each row in the batch is a combination of documents that fills the sequence length. For post-training, both these models only use a batch size of 256 *prompts* [@olmo20242], without filling to the full sequence length (for far fewer non-masked tokens per batch). The smaller batch sizes mean that these training jobs cannot be sharded across as many devices as during pretraining -- in practice, distributed training setups have minimum per-device batch sizes, so if you're trying to retain a smaller global batch size for SFT you can use cumulatively fewer GPUs. In practice the batch size forcing a smaller concurrent GPU allotment per training job is not a limiting factor because the training token counts for SFT are much smaller than in pretraining, and training for multiple seeds is needed in post-training to obtain the best final performance.
- **Prompt masking**: When pretraining, every token in the batch is predicted autoregressively and the loss is then applied to them. For instruction tuning, the prompt tokens are masked out so the model isn't learning to accurately predict user queries -- just responses. The same applies to other post-training algorithms.
- **Multi-turn masking**: For multi-turn conversations, there are two common masking choices. (1) *Final-turn only*: only the tokens in the final assistant turn are included in the loss, while all earlier context (including earlier assistant turns) is masked. Long conversations can still be "unrolled" into multiple training samples: for a conversation of $N$ turns, each example predicts one assistant response while masking all prior context and excluding any future turns. (2) *Mask user turns only*: all user turns are masked, but *every* assistant turn is included in the loss. You can still unroll in this setting if you want more (shorter) training examples, but the key difference is that intermediate assistant replies are trained on directly.
- **Same loss function as pretraining:** Instruction tuning uses the same autoregressive loss function used in pretraining language models, but with substantially different data and masking (training only on full sequences, whereas pretraining documents can be split across batches), etc.
- **Learning rate:** SFT typically uses a learning rate one to two orders of magnitude smaller than pretraining to best manage the different optimization dynamics (smaller datasets, smaller batches, and a strong pretrained initialization all favor more conservative updates). For example, OLMo 2 uses a peak learning rate of $3 \times 10^{-4}$ for pretraining but $1 \times 10^{-5}$ for SFT [@olmo20242]. Olmo 3 uses a higher SFT learning rate of $5\text{-}8 \times 10^{-5}$ [@teamolmo2025olmo3], in part because its training infrastructure uses sequence packing, which fits multiple examples into each training sequence and increases the effective batch size measured in useful tokens. Larger batches produce lower-variance gradient estimates, which in turn supports a higher learning rate without destabilizing training -- a relationship known as the linear scaling rule. The learning rate is commonly warmed up over a small fraction of training steps before decaying linearly. In practice, teams often sweep over multiple learning rates and select the best checkpoint on a held-out evaluation suite [@teamolmo2025olmo3].

## Suggested Experiments

The companion code repository includes a small SFT training script in `code/instruction_tuning/`.
It is intended as a learning exercise to make the base-model-to-assistant transition concrete.

1. **Run the canonical SFT example and watch the base→assistant transition.**
   Run:

   ```bash
   cd code/
   uv run python -m instruction_tuning.train --config instruction_tuning/configs/sft_olmo2_1b.yaml
   ```

   This trains `allenai/OLMo-2-0425-1B` (base) on `HuggingFaceH4/no_robots` and prints generations for a fixed prompt pool every 50 optimizer steps.
   At step 0 the base model rambles, repeats the prompt, and emits malformed role markers; after a few hundred steps the same prompts produce concise answers that terminate at `<|endoftext|>`.
   This is the sanity check for instruction tuning — the same loss function as pretraining, but applied to a chat template with prompt tokens masked.

2. **Sweep the learning rate.**
   Copy `sft_olmo2_1b.yaml` and try `lr` values of `1e-6`, `5e-6`, and `5e-5` while holding everything else fixed.
   Inspect at which learning rate the model first answers and stops cleanly versus when it overfits and starts producing template-shaped slop.
   This is the practical version of the "one to two orders of magnitude below pretraining" guidance above.
