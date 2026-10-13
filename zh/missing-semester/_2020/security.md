---
layout: lecture
title: "安全与密码学"
description: >
  了解哈希函数和密码学原语（如哈希函数和密钥派生函数），理解 Git 和 SSH 等工具如何使用它们。
thumbnail: /static/assets/thumbnails/2020/lec9.png
date: 2020-01-28
ready: true
video:
  aspect: 56.25
  id: tjwobAmnKTo
special: true
---

去年的[安全与隐私讲义](/2019/security/)聚焦于你作为计算机*用户*如何更安全地使用计算机。今年，我们将关注与安全相关的密码学概念，这些概念与我们在课程前面讨论过的工具相关，比如 Git 中哈希函数的使用，或者 SSH 中的密钥派生函数以及对称/非对称密码系统。

本讲义不能替代关于计算机系统安全（[6.858](https://css.csail.mit.edu/6.858/)）或密码学（[6.857](https://courses.csail.mit.edu/6.857/) 和 6.875）等更为严格和完整的课程。没有接受过系统安全方面的正式训练，请不要去做安全相关工作。除非你是专家，否则不要[自己搞加密](https://www.schneier.com/blog/archives/2015/05/amateurs_produc.html)。同样的原则也适用于系统安全。

本讲义对基础密码学概念进行了非常随意的（但我们认为实用的）讲解。本讲义不足以教会你*设计*安全系统或密码学协议，但希望它能让你对自己已经使用的程序和协议有一个通用的理解。

# 熵

[熵](https://en.wikipedia.org/wiki/Entropy_(information_theory))是衡量随机性的指标。这在确定密码强度时很有用。

![XKCD 936: Password Strength](https://imgs.xkcd.com/comics/password_strength.png)

如上 [XKCD 漫画](https://xkcd.com/936/) 所示，密码 "correcthorsebatterystaple" 比 "Tr0ub4dor&3" 更安全。但我们如何对这类东西进行量化呢？

熵的单位是*比特*（bit），当从一组可能结果中均匀随机地选取时，熵等于 `log_2(可能结果的数量)`。抛一枚公平硬币给出 1 bit 熵。掷一个六面骰子（2.58 bits）约有 \~2.58 bits 熵。

你应当考虑这样一个事实：攻击者可能知道密码的*模型*，但不知道用于选择特定密码的随机性（例如来自[掷骰子](https://en.wikipedia.org/wiki/Diceware)的随机性）。

到底需要多少比特的熵才够？这取决于你的威胁模型（threat model）。对于在线猜测，XKCD 漫画指出的那样，\~40 bits 熵就相当不错了。要对离线猜测具有抵抗力，则需要更强的密码（例如 80 bits 或更多）。

# 哈希函数

[密码学哈希函数](https://en.wikipedia.org/wiki/Cryptographic_hash_function)将任意大小的数据映射到固定大小，并具有某些特殊性质。哈希函数的大致规范如下：

```
hash(value: array<byte>) -> vector<byte, N>  (for some fixed N)
```

一个哈希函数的例子是 [SHA1](https://en.wikipedia.org/wiki/SHA-1)，它被 Git 所使用。它将任意大小的输入映射到 160 位的输出（可以表示为 40 个十六进制字符）。我们可以使用 `sha1sum` 命令尝试对一个输入求 SHA1 哈希：

```console
$ printf 'hello' | sha1sum
aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d
$ printf 'hello' | sha1sum
aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d
$ printf 'Hello' | sha1sum
f7ff9e8b7bb2e09b70935a5d785e0cc5d9d0abf0
```

从高层次来看，哈希函数可以视为一个难以逆向的、看起来随机的（但确定性的）函数（这就是[哈希函数的理想模型](https://en.wikipedia.org/wiki/Random_oracle)，也称为随机预言机）。哈希函数具有以下性质：

- **确定性**（Deterministic）：相同的输入总是产生相同的输出。
- **不可逆**（Non-invertible）：对于某个期望的输出 `h`，很难找到一个输入 `m` 使得 `hash(m) = h`。
- **目标抗碰撞**（Target collision resistant）：给定一个输入 `m_1`，很难找到另一个不同的输入 `m_2` 使得 `hash(m_1) = hash(m_2)`。
- **抗碰撞**（Collision resistant）：很难找到两个输入 `m_1` 和 `m_2` 使得 `hash(m_1) = hash(m_2)`（注意，这是一个比目标抗碰撞更强的性质）。

译者注：这里前三个性质中，"不可逆"意味着你不能从一个哈希值反推出原始数据；"目标抗碰撞"意味着如果你已经有一个具体的输入，很难找到另一个不同的输入产生相同的哈希值；而"抗碰撞"意味着你根本不需要先有一个输入，就能找到任意两个产生相同哈希值的输入。第三个性质蕴含第二个性质，但反过来不成立。

注意：虽然对于某些目的来说 SHA-1 可能还够用，但它已[不再](https://web.archive.org/web/20260207211148/https://shattered.io/)被认为是一个强健的密码学哈希函数。你可能会对这份[密码学哈希函数生命周期表](https://valerieaurora.org/hash.html)感兴趣。不过请注意，推荐具体的哈希函数已经超出本讲义的范围。如果你在做与此相关的工作，你需要接受安全/密码学方面的正式训练。

## 应用

- **Git 的内容寻址存储**（content-addressed storage）。[哈希函数](https://en.wikipedia.org/wiki/Hash_function)的概念更广泛（还有非密码学哈希函数）。为什么 Git 要使用密码学哈希函数？
- **文件内容的简要摘要**。软件通常可以从（可能不太可信的）镜像站点下载，例如 Linux ISO 镜像，而我们不希望完全信任这些镜像站点。官方网站通常会在下载链接旁边（这些链接指向第三方镜像站）发布哈希值，以便在文件下载完成后进行验证。
- **[承诺方案](https://en.wikipedia.org/wiki/Commitment_scheme)**。假设你想对某个值做出承诺，但之后再揭示这个值本身。例如，我想在没有可信的共享硬币（双方都能看到的硬币）的情况下，"在心里"做一次公平的抛硬币。我可以选择一个值 `r = random()`，然后分享 `h = sha256(r)`。之后，你可以喊正面或反面（我们约定偶数 `r` 表示正面，奇数 `r` 表示反面）。你喊完以后，我可以揭示我的值 `r`，你可以检查 `sha256(r)` 是否与我之前分享的哈希值匹配，以确认我没有作弊。

# 密钥派生函数

与密码学哈希相关的概念是[密钥派生函数](https://en.wikipedia.org/wiki/Key_derivation_function)（KDF），它被用于多种应用，包括产生用于其他密码算法的密钥的固定长度输出。通常，KDF 是刻意缓慢的，以减缓离线的暴力破解攻击。

## 应用

- 从密码口令中产生密钥，供其他密码算法使用（例如对称密码，见下文）。
- **存储登录凭据**。存储明文密码是不好的；正确的方法是为每个用户生成并存储一个随机[盐值](https://en.wikipedia.org/wiki/Salt_(cryptography)) `salt = random()`，存储 `KDF(password + salt)`，并通过用输入的密码和存储的盐值重新计算 KDF 来验证登录尝试。

# 对称密码

当你想到密码学时，最先想到的概念可能就是隐藏消息内容。对称密码通过以下一组功能来实现这一目标：

```
keygen() -> key  (this function is randomized)

encrypt(plaintext: array<byte>, key) -> array<byte>  (the ciphertext)
decrypt(ciphertext: array<byte>, key) -> array<byte>  (the plaintext)
```

加密函数的性质是：给定输出（密文），如果没有密钥，很难确定输入（明文）。解密函数具有显而易见的正确性性质，即 `decrypt(encrypt(m, k), k) = m`。

今天广泛使用的一个对称密码系统例子是 [AES](https://en.wikipedia.org/wiki/Advanced_Encryption_Standard)。

## 应用

- 在不可信的云服务上加密存储文件。这可以与 KDF 结合使用，这样你就可以用密码口令加密一个文件。生成 `key = KDF(passphrase)`，然后存储 `encrypt(file, key)`。

# 非对称密码

"非对称"这个词指的是存在两个密钥，各有不同的角色。私钥，顾名思义，应被保密，而公钥可以公开分享，不会影响安全性（与对称密码系统中共享密钥不同）。非对称密码系统提供以下一组功能，用于加密/解密和签名/验证：

```
keygen() -> (public key, private key)  (this function is randomized)

encrypt(plaintext: array<byte>, public key) -> array<byte>  (the ciphertext)
decrypt(ciphertext: array<byte>, private key) -> array<byte>  (the plaintext)

sign(message: array<byte>, private key) -> array<byte>  (the signature)
verify(message: array<byte>, signature: array<byte>, public key) -> bool  (whether or not the signature is valid)
```

加密/解密函数具有与对称密码系统中的对应函数类似的性质。消息可以使用*公钥*进行加密。给定输出（密文），在*没有私钥*的情况下，很难确定输入（明文）。解密函数具有显而易见的正确性性质，即 `decrypt(encrypt(m, public key), private key) = m`。

对称加密和非对称加密可以类比为物理上的锁。对称密码系统就像是一个门锁：任何有钥匙的人都可以开锁和关门。非对称加密就像一把带钥匙的挂锁。你可以把未上锁的锁（公钥）给别人，他们可以放一封消息到一个盒子里，然后锁上锁，此后只有你能打开这把锁，因为你保留了钥匙（私钥）。

签名/验证函数具有你在物理签名中期望的相同性质，即签名很难伪造。不管是什么消息，*没有私钥*的情况下，很难产生一个签名，使得 `verify(message, signature, public key)` 返回 true。当然，验证函数也具有显而易见的正确性性质，即 `verify(message, sign(message, private key), public key) = true`。

## 应用

- **[PGP 邮件加密](https://en.wikipedia.org/wiki/Pretty_Good_Privacy)**。人们可以将其公钥发布在网络上（例如 PGP 密钥服务器，或 [Keybase](https://keybase.io/)）。任何人都可以向他们发送加密邮件。
- **私人消息**。像 [Signal](https://signal.org/) 和 [Keybase](https://keybase.io/) 这样的应用使用非对称密钥来建立私密通信通道。
- **软件签名**。Git 支持 GPG 签名的提交和标签。有了公开的公钥，任何人都可以验证下载软件的真实性。

## 密钥分发

非对称密钥密码学非常美妙，但它面临一个大的挑战：公钥的分配 / 将公钥映射到现实世界的身份。对此问题有许多解决方案。Signal 有一个简单的方案：首次使用时信任，并支持带外（out-of-band）公钥交换（你在面对面时验证你朋友的"安全号码"）。PGP 有不同的方案，即[信任网](https://en.wikipedia.org/wiki/Web_of_trust)。Keybase 又有另一种方案，即[社会证明](https://keybase.io/blog/chat-apps-softer-than-tofu)（以及其它有趣的想法）。每种模型都有其优点；我们（讲师）比较喜欢 Keybase 的模型。

# 案例分析

## 密码管理器

这是一个每个人都应该尝试使用的必备工具（例如 [KeePassXC](https://keepassxc.org/)、[pass](https://git.zx2c4.com/password-store/about/) 和 [1Password](https://1password.com)）。密码管理器让你能够方便地为所有登录使用唯一的、随机生成的高熵密码，并将所有密码保存在一个地方，用对称密码加密，密钥通过 KDF 从密码口令中生成。

使用密码管理器可以让你避免密码复用（这样当网站被攻破时你受到的影响更小），使用高熵密码（这样你被攻破的可能性更低），并且只需要记住一个高熵密码。

## 双因素认证

[双因素认证](https://en.wikipedia.org/wiki/Multi-factor_authentication)（2FA）要求你使用密码口令（"你已知晓的东西"）配合 2FA 认证器（如 [YubiKey](https://www.yubico.com/)，"你拥有的东西"）来防护被盗密码和[钓鱼](https://en.wikipedia.org/wiki/Phishing)攻击。

## 全盘加密

保持笔记本电脑的整个磁盘加密是在笔记本电脑被盗的情况下保护数据的简单方法。你可以在 Linux 上使用 [cryptsetup + LUKS](https://wiki.archlinux.org/index.php/Dm-crypt/Encrypting_a_non-root_file_system)，Windows 上使用 [BitLocker](https://fossbytes.com/enable-full-disk-encryption-windows-10/)，或 macOS 上使用 [FileVault](https://support.apple.com/en-us/HT204837)。这会对整个磁盘使用对称密码加密，密钥受到密码口令的保护。

## 私人消息

使用 [Signal](https://signal.org/) 或 [Keybase](https://keybase.io/)。端到端安全性由非对称密钥加密引导建立（bootstrapped）。获取你联系人的公钥是关键步骤。如果你想要良好的安全性，你需要通过带外方式（使用 Signal 或 Keybase）验证公钥，或者信任社会证明（使用 Keybase）。

## SSH

我们在[之前的讲义](/2020/command-line/#remote-machines)中讨论了 SSH 和 SSH 密钥的使用。让我们来看看这方面的密码学方面。

当你运行 `ssh-keygen` 时，它会生成一个非对称密钥对 `public_key, private_key`。这是随机生成的，使用操作系统提供的熵（从硬件事件等收集）。公钥原样存储（它是公开的，所以保密并不重要），但在存储时，私钥应在磁盘上加密。`ssh-keygen` 程序会提示用户输入一个密码口令，这个密码口令通过密钥派生函数产生一个密钥，然后用于用对称密码加密私钥。

在实际使用中，一旦服务器知道了客户端的公钥（存储在 `.ssh/authorized_keys` 文件中），连接的客户端就可以使用非对称签名来证明其身份。这是通过[挑战-响应认证](https://en.wikipedia.org/wiki/Challenge%E2%80%93response_authentication)完成的。从高层次来说，服务器选择一个随机数并发送给客户端。然后客户端用私钥对这个消息签名，并将签名发回给服务器，服务器根据记录的公钥验证签名。这有效地证明了客户端持有与服务器 `.ssh/authorized_keys` 文件中公钥对应的私钥，因此服务器可以允许客户端登录。

{% comment %}
extra topics, if there's time

security concepts, tips
- biometrics
- HTTPS
{% endcomment %}

# 资源

- [去年的讲义](/2019/security/)：当该讲义更侧重于作为计算机用户的安全和隐私
- [Cryptographic Right Answers](https://latacora.micro.blog/2018/04/03/cryptographic-right-answers.html)：回答了"对于 X 我应该用什么密码学"的许多常见 X 的问题。

# 练习

1. **熵。**
    1. 假设一个密码是由四个小写字典词连接而成，每个词从大小为 100,000 的字典中均匀随机选取。这样的密码示例是 `correcthorsebatterystaple`。它有多少比特的熵？
    1. 考虑一种替代方案：一个密码由 8 个随机字母数字字符（包括小写和大写字母）组成。一个示例是 `rg8Ql34g`。它有多少比特的熵？
    1. 哪个是更强的密码？
    1. 假设攻击者每秒可以尝试 10,000 个猜测。平均来说，破解每个密码需要多长时间？
1. **密码学哈希函数。** 从[镜像站点](https://www.debian.org/CD/http-ftp/)（例如这个[阿根廷镜像站点](http://debian.xfree.com.ar/debian-cd/current/amd64/iso-cd/)）下载一个 Debian 镜像。用从 Debian 官方网站获取的哈希值交叉校验哈希值（例如使用 `sha256sum` 命令，如在这个托管于 `debian.org` 的[文件](https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/SHA256SUMS)中，如果你已从阿根廷镜像站点下载了上述链接文件的话）。
1. **对称密码。** 使用 [OpenSSL](https://www.openssl.org/) 用 AES 加密一个文件：`openssl aes-256-cbc -salt -in {输入文件名} -out {输出文件名}`。使用 `cat` 或 `hexdump` 查看内容。使用 `openssl aes-256-cbc -d -in {输入文件名} -out {输出文件名}` 解密，并使用 `cmp` 确认内容与原文匹配。
1. **非对称密码。**
    1. 在一台你能访问的计算机上（不是 Athena，因为 Kerberos 与 SSH 密钥的交互方式很奇怪）[设置 SSH 密钥](https://www.digitalocean.com/community/tutorials/how-to-set-up-ssh-keys--2)。确保你的私钥使用密码口令加密，以便在存储时得到保护。
    1. [设置 GPG](https://www.digitalocean.com/community/tutorials/how-to-use-gpg-to-encrypt-and-sign-messages)
    1. 给 Anish 发送一封加密邮件（[公钥](https://keybase.io/anish)）。
    1. 使用 `git commit -S` 签名一个 Git 提交，或使用 `git tag -s` 创建一个签名的 Git 标签。使用 `git show --show-signature` 验证提交上的签名，或使用 `git tag -v` 验证标签上的签名。