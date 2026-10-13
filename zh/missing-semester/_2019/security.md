---
layout: lecture
title: "安全与隐私"
presenter: Jon
date: 2019-01-31
order: 2
video:
  aspect: 56.25
  id: OBx_c-i-M8s
special: true
---

世界是个可怕的地方，人人都想搞你。

好吧，也许未必，但这并不意味着你要把自己所有的秘密都晾在太阳底下。安全（以及隐私）基本上就是**提高攻击者的门槛**。先搞清楚你的威胁模型（threat model，即你究竟在防备谁、防备什么），然后围绕它来设计你的安全机制！如果你的威胁模型是 NSA（美国国家安全局）或摩萨德（以色列情报特务局），那你 _很可能_ 要倒霉了。

让技术身份更安全有 _很多_ 种方法。我们会在这里提到许多高层次的建议，但这始终是一个持续的过程，而自学安全知识是你能做的最好的事之一。所以：

## 关注对的人

提升安全意识最好的方法之一就是关注那些在安全领域积极发声的人。以下是一些建议：

 - [@TroyHunt](https://twitter.com/TroyHunt)
 - [@SwiftOnSecurity](https://twitter.com/SwiftOnSecurity)
 - [@taviso](https://twitter.com/taviso)
 - [@thegrugq](https://twitter.com/thegrugq)
 - [@tqbf](https://twitter.com/tqbf)
 - [@mattblaze](https://twitter.com/mattblaze)
 - [@moxie](https://twitter.com/moxie)

另见[这个列表](https://heimdalsecurity.com/blog/best-twitter-cybersec-accounts/)获取更多推荐。

## 通用安全建议

Tech Solidarity 有一份[给记者的安全守则清单](https://web.archive.org/web/20221123204419/https://techsolidarity.org/resources/basic_security.htm)，给出了许多中肯的建议，而且相对时效。[@thegrugq](https://medium.com/@thegrugq) 也写了一篇关于[旅行安全建议](https://medium.com/@thegrugq/stop-fabricating-travel-security-advice-35259bf0e869)的博客文章，同样值得一读。我们会在这里复述这些来源中的大部分建议，再加上一些额外内容。另外，买一个 [USB 数据线阻断器](https://www.amazon.com/dp/B00QRRZ2QM/)，因为 [USB 很可怕](https://www.bleepingcomputer.com/news/security/heres-a-list-of-29-different-types-of-usb-attacks/)。

## 认证

如果你还没做过，首先要做的事就是下载一个密码管理器。一些不错的选择包括：

 - [1Password](https://1password.com/)
 - [KeePass](https://keepass.info/)
 - [BitWarden](https://bitwarden.com/)
 - [`pass`](https://git.zx2c4.com/password-store/about/)

如果你特别 paranoid（多疑），那就选一个在**本地**加密密码的，而不是把密码以明文形式存在服务器上的。用这个管理器为你所有在乎的网站生成密码。然后，开启**双因素认证**（two-factor authentication，简称 2FA），最好搭配一个 [FIDO/U2F](https://fidoalliance.org/) 加密狗（比如 [YubiKey](https://www.yubico.com/quiz/)，学生可以享受 [8 折优惠](https://www.yubico.com/why-yubico/for-education/)）。TOTP（比如 Google Authenticator 或 Duo）应急也行，但 [不能防范钓鱼攻击](https://twitter.com/taviso/status/1082015009348104192)。短信验证码基本上没什么用——除非你的威胁模型只包括路过的随机路人截获你传输中的密码。

另外，关于纸质密钥（paper key）的说明：很多服务会给你一把"备用密钥"，以防你丢失了真正的第二认证因子（顺便说一句，一定要在某个安全的地方放一把备用加密狗！）。你 _可以_ 把这些密钥存进密码管理器，但这意味着一旦有人访问了你的密码管理器，你就彻底完蛋了（当然，也许你的威胁模型本来就是这么设计的）。如果你是真的 paranoid，就把这些纸质密钥打印出来，**永远不要**数字化存储，然后把它们放在现实世界中的保险柜里。

## 私密通信

使用 [Signal](https://www.signal.org/)（[设置指南](https://medium.com/@mshelton/signal-for-beginners-c6b44f76a1f0)。[Wire](https://wire.com/en/) 也 [没问题](https://www.securemessagingapps.com/)；WhatsApp 也行；[不要用 Telegram](https://twitter.com/bascule/status/897187286554628096)）。桌面端的即时通讯软件问题多多（部分原因是它们通常依赖 Electron，这意味着你需要信任一大套技术栈）。

电子邮件尤其棘手，即使有 PGP 签名也是如此。它通常**不是前向安全的**（forward-secure，即即使密钥事后泄露，过去的消息也不会被解密），而且密钥分发的问题相当严重。[keybase.io](https://keybase.io/) 能缓解一部分，也还有别的一些用途。另外，PGP 密钥通常是在桌面电脑上管理的，而桌面恰恰是**安全性最低**的计算环境之一。与此相关，考虑一下买一台 Chromebook，或者只用带键盘的平板电脑来工作。

## 文件安全

文件安全很难，涉及多个层面。你究竟要防备什么？

[![$5 wrench](https://imgs.xkcd.com/comics/security.png)](https://xkcd.com/538/)

 - **离线攻击**（有人在你关机时偷走了你的笔记本）：开启**全盘加密**（full disk encryption）（Linux 上 [cryptsetup + LUKS](https://wiki.archlinux.org/index.php/Dm-crypt/Encrypting_a_non-root_file_system)，Windows 上 [BitLocker](https://fossbytes.com/enable-full-disk-encryption-windows-10/)，macOS 上 [FileVault](https://support.apple.com/en-us/HT204837)）。注意，如果攻击者 _同时_ 控制了你也确实想要你的秘密，这招不管用。
 - **在线攻击**（有人拿到了你的笔记本且它正处于开机状态）：使用**文件加密**。主要有两种方式：
   - **加密文件系统**：分层文件系统加密软件单独加密每个文件，而不是加密整个块设备。提供解密密钥后可以"挂载"这些文件系统，在里面自由浏览文件；卸载后这些文件就全部不可访问了。现代方案包括 [gocryptfs](https://github.com/rfjakob/gocryptfs) 和 [eCryptFS](https://www.ecryptfs.org/)。更详细的对比可以参见[这里](https://nuetzlich.net/gocryptfs/comparison/)和[这里](https://wiki.archlinux.org/index.php/disk_encryption#Comparison_table)。
   - **加密文件**：使用对称加密（参见 `gpg -c`）和一个密钥来加密单个文件。或者，像 `pass` 那样，**再用你的公钥加密这个密钥**，这样只有你用对应的私钥才能把密钥读回来。加密设置（算法、密钥长度等）非常关键！
 - **合理的否认性**（[plausible deniability](https://en.wikipedia.org/wiki/Plausible_deniability)，"警官，请问有什么可以帮您的？"）：通常性能较低，数据更容易丢失。实际上证明其提供了[可否认加密](https://en.wikipedia.org/wiki/Deniable_encryption)是非常困难的！参见[这个讨论](https://security.stackexchange.com/questions/135846/is-plausible-deniability-actually-feasible-for-encrypted-volumes-disks)，然后再考虑是否想要试试 [VeraCrypt](https://www.veracrypt.fr/en/Home.html)（那个被维护的、来自经典的 TrueCrypt 的衍生版本）。
 - **加密备份**：使用 [Tarsnap](https://www.tarsnap.com/) 或 [Borgbase](https://www.borgbase.com/)。
   - 想一下：如果攻击者拿到了你的笔记本，他们能否删除你的备份？

## 网络安全与隐私

互联网是个 _非常_ 可怕的地方。公开 WiFi 网络 [很](https://www.troyhunt.com/the-beginners-guide-to-breaking-website/) [可怕](https://www.troyhunt.com/talking-with-scott-hanselman-on/)。确保你**用完之后删除**这些网络——否则你的手机之后会很乐意自动通知并重新连接到同名网络！

如果你在一个不信任的网络上，使用 VPN _可能_ 值得，但要记住：你正在**非常信任**这个 VPN 提供商。你真的比你的 ISP（互联网服务提供商）更信任他们吗？如果你真的需要 VPN，选择一个你确信可以信任的提供商，而且你应该**付费**使用。或者干脆自己搭建 [WireGuard](https://www.wireguard.com/)——它 [非常出色](https://web.archive.org/web/20210526211307/https://latacora.micro.blog/there-will-be/)！

[cipherlist.eu](https://cipherlist.eu/) 上还提供了许多联网应用的安全配置选项。如果你特别在意隐私，[privacytools.io](https://privacytools.io) 也是一个不错的资源。

其中一些人可能会对 [Tor](https://www.torproject.org/) 感兴趣。请记住：Tor _并非_ 特别能抵抗能力强大的全球攻击者，对**流量分析攻击**也相对脆弱。它在小规模隐藏流量方面可能有用，但在隐私方面实际上买不到太多东西。更好的做法是**从一开始就使用更安全的**服务（Signal、TLS + 证书固定等）。

## 网页安全

所以，你还想上网？
天哪，你还真是给自己找罪受。

安装 [HTTPS Everywhere](https://www.eff.org/https-everywhere)。SSL/TLS [至关重要](https://www.troyhunt.com/ssl-is-not-about-encryption/)，而且它 _不只是_ 关于加密——还包括**验证你一开始就在和正确的服务通信**！如果你运行自己的 Web 服务器，[测试一下](https://www.ssllabs.com/ssltest/index.html)。TLS 配置[可能非常复杂](https://wiki.mozilla.org/Security/Server_Side_TLS)。HTTPS Everywhere 会尽最大努力，在有 HTTPS 替代方案时绝不把你导航到 HTTP 站点。这并不能一劳永逸，但能帮上忙。如果你真的是重度 paranoid，可以把你绝对不需要的 SSL/TLS 证书颁发机构（CA）加入黑名单。

安装 [uBlock Origin](https://github.com/gorhill/uBlock)。它是一个[广谱拦截器](https://github.com/gorhill/uBlock/wiki/Blocking-mode)，不仅可以阻止广告，还可以拦截页面上各种第三方通信，以及内联脚本等。如果你愿意花时间来配置以确保功能正常，可以切换到[中等模式](https://github.com/gorhill/uBlock/wiki/Blocking-mode:-medium-mode)甚至[强力模式](https://github.com/gorhill/uBlock/wiki/Blocking-mode:-hard-mode)。你_会_发现有些网站在你充分调整设置之前无法正常运行，但这也会显著提升你的在线安全性。

如果你在使用 Firefox，请启用[多账户容器](https://support.mozilla.org/en-US/kb/containers)。为社交网络、银行、购物等分别创建独立的容器。Firefox 会为每个容器完全独立地保存 Cookie 和其他状态数据，所以你在一个容器中访问的网站无法窥探其他容器中的敏感数据。在 Google Chrome 中，你可以使用 [Chrome 个人资料](https://support.google.com/chrome/answer/2364824) 实现类似效果。

## 练习

1. 使用 PGP 加密一个文件
1. 使用 VeraCrypt 创建一个简单的加密卷
1. 为你数据最敏感的账户启用双因素认证（2FA），例如 GMail、Dropbox、GitHub 等