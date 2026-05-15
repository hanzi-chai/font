# 项目说明（供 Claude 参考）

## 项目概述

本仓库是一个 OpenType 字体工程，字体名称为 **Chai Sans**，基于 Noto Sans 风格设计，提供简体中文汉字拆分所需的部件字形。字形均使用私用区（PUA，E000–F8FF）编码。

## 目录结构

```
sources/
  masters/
    Chai Sans-Regular.ufo/   # 唯一字重的 UFO 源文件
      fontinfo.plist                 # 字体元信息（名称、度量值等）
      features.fea                   # OpenType 特性代码
      glyphs/                        # 各字形的 .glif 文件
dist/                                # 构建输出（不提交到版本库）
build.py                             # 构建脚本
requirements.txt                     # Python 依赖
```

## 构建流程

构建脚本 `build.py` 做三件事：

1. 用 `defcon` 加载 UFO，在内存中将汉字字形名（如 `畫字头`）改为 `uniXXXX` 格式——CFF 格式只允许 latin-1 字形名，必须在编译前完成转换。
2. 用 `ufo2ft.compileOTF` 编译为 OTF（CFF 轮廓）。编译时传入 `useProductionNames=False`（避免内部 save/reload 触发编码错误）和 `optimizeCFF=0`（跳过 cffsubr subroutinization，同样会触发 save）。
3. 用 `fontTools` 将 OTF 转换为 WOFF 和 WOFF2。

## 注意事项

- 字形名含汉字是本项目特有的约束，不要在构建脚本里对字形名做其他假设。
- `dist/` 目录为构建产物，不纳入版本控制。
- 修改 `.glif` 文件后重新运行 `build.py` 即可更新输出。
- 依赖通过 `requirements.txt` 管理，不要在 `build.py` 里自动安装依赖。
