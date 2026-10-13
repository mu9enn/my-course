# 指令微调（SFT）

面向 [RLHF Book](https://rlhfbook.com) 的基座语言模型教学型监督微调（SFT）示例。
关于 chat-template 结构、prompt masking，以及 SFT 在整个后训练流水线中的
角色，详见 **第四章：指令微调（Instruction Fine-Tuning）**。

## 合理性检查：从"续写"到"回答"

本模块旨在直观呈现一个效果：基座模型会无休止地续写文本；
而经过指令微调的模型则能够回答问题并在适当时机停止生成。

用提示词 *"What is the capital of France?"* 调用 `allenai/OLMo-2-0425-1B`（基座模型）时，
生成的内容会发散到更多问题或无关文本上。在小型指令数据集上完成 SFT 之后，
同样的提示词会生成 *"The capital of France is Paris."*，
并在助手结束发言标记（end-of-turn token）处停止生成。

训练循环会在 step 0（基座模型）以及之后每 `sample_every` 个优化器步时，
将该提示词对应的生成样本打印到控制台，因此随着训练的进行，
模型从"续写"到"回答"的转变过程一目了然。

训练初期，基座模型尚未内化 chat-template 的规则，也不清楚"回答完一次就停"
的约定，因此在助手轮次结束后继续续写，甚至凭空编造出更多用户问题：

```
──────────────────────────────────── Samples @ step 100 ─────────────────────────────────────
╭─ Prompt 1 ────────────────────────────────────────────────────────────────────────────────╮
│ <|endoftext|><|user|>                                                                     │
│ What is the capital of France?                                                            │
│ <|assistant|>                                                                             │
│ Paris                                                                                     │
│ What is the capital of Germany?                                                           │
│ <|assistant|>>                                                                            │
│ Berlin                                                                                    │
│ What is the capital of Italy?                                                             │
│ <|assistant|>>                                                                            │
│ Rome                                                                                      │
│ ...                                                                                       │
╰───────────────────────────────────────────────────────────────────────────────────────────╯
```

几百步之后，模型已经学会了给出一段连贯的助手回答，并输出 `<|endoftext|>` 来结束本轮对话：

```
──────────────────────────────────── Samples @ step 650 ─────────────────────────────────────
╭─ Prompt 1 ────────────────────────────────────────────────────────────────────────────────╮
│ <|endoftext|><|user|>                                                                     │
│ What is the capital of France?                                                            │
│ <|assistant|>                                                                             │
│ The capital of France is Paris.<|endoftext|>                                              │
╰───────────────────────────────────────────────────────────────────────────────────────────╯
```

## 训练结果

![指令微调训练结果](../images/wandb_instruction_tuning.png)

参考运行记录：[wandb](https://wandb.ai/rlhf-book/core/runs/nybj8sdx)
（模型 `allenai/OLMo-2-0425-1B`，数据集 `HuggingFaceH4/no_robots`，
3 个 epoch，默认配置）。损失在前 ~150 步急剧下降——模型在此期间
"学会"了 chat-template 的格式——之后持续缓慢下降，逐步改进
回复风格。`grad_norm` 也在同样的早期阶段趋于平稳；其余的波动
对应于 batch 中更长或更难的样本行。

## 快速开始

```bash
cd code/
uv sync

# 默认运行（约 9.5K 行，3 个 epoch，bf16 精度下可跑在 24 GB GPU 上）
uv run python -m instruction_tuning.train \
    --config instruction_tuning/configs/sft_olmo2_1b.yaml

# 开启 W&B 日志记录
WANDB_PROJECT=rlhf-book uv run python -m instruction_tuning.train \
    --config instruction_tuning/configs/sft_olmo2_1b.yaml
```

## 运行流程

1. 加载 `allenai/OLMo-2-0425-1B`（基座模型）及其 tokenizer。基座
   tokenizer 没有 `chat_template`，因此我们从
   `allenai/OLMo-2-0425-1B-SFT` 中"提取"出标准模板，让生成的模型
   使用相同的 `<|user|>` / `<|assistant|>` 对话格式。
2. 加载 `HuggingFaceH4/no_robots`，用 chat-template 渲染每一行数据，
   并在 prompt token 上标注 `-100`（`IGNORE_INDEX`）——只有
   助手（assistant）的 token 对损失函数有贡献。
3. 使用 AdamW + 线性预热/衰减策略进行训练，精度为 bf16，并启用
   梯度检查点（gradient checkpointing）和梯度累积（gradient
   accumulation）。未使用分片（sharding）或数据并行。
4. 定期针对一组固定的提示词池（包括"法国首都是什么"的提示词）生成
   补全结果，并以彩色面板的形式打印到控制台。损失和学习率会记录
   到 W&B；样本文本仅输出到控制台。

## OLMo-2 对话格式的"彩蛋"

OLMo-2 的 tokenizer 对 `<|endoftext|>` （id 为 `100257`）作为 BOS（start of conversation）、EOS
*以及* UNK 三种用途——唯一的另一个特殊 token 是 `<|pad|>`。
因此，任何渲染后的对话都长这样：

```
<|endoftext|><|user|>\nhi\n<|assistant|>\nhello<|endoftext|>
^^^^^^^^^^^^                                   ^^^^^^^^^^^^
   BOS (start of conversation)                 EOS (end of assistant turn)
```

模型通过上下文来消除歧义：在对话开头、紧跟 `<|user|>` 时，
它表示"开始"；而在助手消息之后出现时，则表示"停止"。其他
模型家族避免了这种设计——Llama-3 使用不同的 `<|begin_of_text|>` /
`<|end_of_text|>`，Qwen 使用 `
<|im_start|>` / `<|im_end|>`. The
`<|user|>` / `<|assistant|>` / `<|system|>` role markers are *not* special
词表中 *并非* 特殊 token；它们被拆解为普通的 BPE 子词片段（`<`、
`|`, `user`, `|`, `>`), which is why the base model (pre-SFT) treats them
as ordinary text and produces nonsense like `<|admin|>` continuations.

## Dataset

`HuggingFaceH4/no_robots` (CC BY-NC 4.0). 9.5K human-written
instruction-response rows in the standard `messages` format, mostly
single-turn. Strong signal-to-noise per row for a sanity-check SFT run.

License caveat: No Robots is non-commercial. It is fine for educational
fine-tuning and the resulting checkpoint is for learning, not redistribution.

## Memory Expectations

With bf16 and gradient checkpointing on `OLMo-2-0425-1B`:

| Setting | Approximate VRAM |
|---------|------------------|
| `batch_size=4`, `max_length=2048` | ~14–18 GB |
| `batch_size=8`, `max_length=2048` | ~22–24 GB |
| `batch_size=4`, `max_length=4096` | ~22–24 GB |

These fit a 24 GB consumer/workstation GPU. The default config sticks to
`batch_size=4 × gradient_accumulation_steps=8` (effective batch 32) for headroom.

## File Structure

```
instruction_tuning/
├── __init__.py
├── README.md      # this file
├── config.py      # pydantic Config + YAML loader
├── train.py       # SFT loop with in-loop sample logging
├── utils.py       # model loading, chat-template lifting, dataset, generation
└── configs/
    └── sft_olmo2_1b.yaml
```
