# 小鹤反查 · Xiaohe Lookup

小鹤双拼·音形的反向查询工具：**键码查汉字、汉字查全码、全拼换双拼键序**。单文件、零依赖、离线可用。

官网 react.xhup.club 的编码查询只支持「输入汉字 → 查编码」，不支持反方向；本工具把两个方向都做全了，而且不联网。

## 功能

- **双拼反查**：输入两码（`xn`）→ 列出同码全部汉字，按使用频率排序，附全码与带调拼音
- **全码精确查**：输入四码（`xnld`）或 `xn~ld` → 直接命中（小）
- **汉字查码**：粘贴汉字（`小`）→ 显示它的全部编码与读音
- **全拼换算**：输入全拼（`xiao`）或词组（`nihao`）→ 给出双拼键序（ni hc），附高频候选
- **首键浏览**：输入单字母（`x`）→ 该键下所有双拼码与音节
- 点击任意结果复制全码；↑↓ 选择，Enter 复制，Esc 清空

共收录 418 个双拼码、52,054 条音形编码、40,491 个汉字（含扩展区生僻字，权重 0 者灰显）。

## 使用

三种方式，任选：

1. **单文件离线**（推荐）：下载 [index.html](index.html)，本地双击打开即用。保存一份，永远可用，不需要网络。
2. **在线版**：GitHub Pages <https://cyriusweng.github.io/xhup-lookup/>（发布后生效）
3. **安装为应用**：在线版在手机浏览器里「添加到主屏幕」，即成为离线可用的独立应用（PWA）。

## 重建

修改词典或模板后：

```sh
python3 build.py
```

脚本从 `data/` 的 Rime 词典编译出 `index.html` 与全部图标，无第三方依赖。

## 数据来源与许可

- 词典取自 [boomker/rime-fast-xhup](https://github.com/boomker/rime-fast-xhup)（LGPL-3.0，commit `83aed1c`，2026-01 版码表），详见 [data/README.md](data/README.md)
- 小鹤音形、小鹤双拼方案由鹤大（[flypy.com](https://flypy.com)）设计，感谢原作者的持续维护
- 本工具代码以 [GPL-3.0](LICENSE) 发布

## 致谢

- [flypy.com](https://flypy.com) — 小鹤音形输入方案
- [boomker/rime-fast-xhup](https://github.com/boomker/rime-fast-xhup) — Rime 词典
- [react.xhup.club](http://react.xhup.club) — 原版编码查询，本项目的出发点

---

Offline reverse lookup for Xiaohe Shuangpin/Yinxing: type a two-letter code to list every character under it with full codes and tone-marked pinyin, paste a character to see its codes, or type full pinyin (`nihao`) to get the shuangpin keystroke sequence (`ni hc`). One self-contained HTML file, no dependencies, works fully offline; installable as a PWA when hosted. Data from rime-fast-xhup (LGPL-3.0), scheme by flypy.com. Code under GPL-3.0.
