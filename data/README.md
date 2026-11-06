# 数据来源与已知问题

## 文件

| 文件 | 内容 | 原始路径 |
|---|---|---|
| `flypy_chars.dict.yaml` | 单字全码 `字<TAB>双拼~形码<TAB>权重`（version 2026.01.21） | `cn_dicts/flypy_chars.dict.yaml` |
| `flypy_chars_ext.dict.yaml` | 扩展区生僻字，权重 0 | `cn_dicts/flypy_chars_ext.dict.yaml` |
| `flyhe_chars.dict.yaml` | 单字读音 `字<TAB>带调拼音<TAB>权重`（version 2026.01.11） | `cn_dicts/flyhe_chars.dict.yaml` |
| `LICENSE-rime-fast-xhup.txt` | 上游 LGPL-3.0 全文 | `LICENSE` |

均取自 [boomker/rime-fast-xhup](https://github.com/boomker/rime-fast-xhup)，commit `83aed1cd8cc7530ac93ad4395bf3d4a6a59c02a2`（2026-11-05）。上游再往前是小鹤音形官方码表与 Rime 社区的整理，感谢鹤大（flypy.com）与 boomker。

## 编译规则（build.py）

1. 合并两份码表，按 `(字, 双拼, 形码)` 去重，权重取最大值
2. 每个双拼码的音节标签由成员字的读音投票产生；音节与双拼码全局一一对应，得票最多的组先认领（所以 `uw`＝shei、`uv`＝shui，而不是两组都标 shui）
3. 每条记录的拼音 = 该字读音中与组音节匹配的那个（保留声调）；没有匹配时显示组音节（无调）
4. 权重 0 视为生僻字，界面灰显

## 已知问题

- 5 个小组（`eh`、`yd`、`fs`、`ny`、`px`）无法认领到独占音节，沿用了多数票标签；这些组的字仍可用键码查到，拼音检索会优先命中更大的组
- 音形简码（一简到三简）不在词典内，本工具只显示四码全码
- 汉字读音来自 `flyhe_chars`，个别生僻字读音与组音节不一致时显示组音节
