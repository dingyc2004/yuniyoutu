# 编译说明

## 环境要求

- **TeX 发行版**：TeX Live 2024+（含 XeLaTeX）
- **中文字体**：无需额外配置，`ctexart` 文档类自动匹配系统字体

## 编译命令

在项目目录（`main.tex` 所在目录）下执行：

```bash
xelatex -interaction=nonstopmode main.tex
xelatex -interaction=nonstopmode main.tex
```

需编译**两次**以使目录、交叉引用和页码生效。

## 文件结构

```
.
├── main.tex              # 主文件（文档类、宏包、封面、目录、\input 各章节）
├── sections/
│   ├── 01_project_overview.tex
│   ├── 02_requirement_analysis.tex
│   ├── ...
│   └── 19_appendix.tex   # 共 19 个章节文件
├── figures/              # 配图（PNG）
├── BUILD.md              # 本文件
└── main.pdf              # 编译产物
```

## 注意事项

- 不可删除 `figures/` 目录，正文插入了多张截图
- 编译过程中 `fancyhdr` 的 `\headheight` 警告可忽略，不影响排版
