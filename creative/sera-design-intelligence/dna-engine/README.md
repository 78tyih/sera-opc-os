# Sera Design DNA Engine

设计 DNA 提取引擎 — 从任意网站 URL 自动提取品牌设计系统。

## 目标

将任意优秀网站的设计系统转化为结构化的 STYLE_DNA.json，使 AI 设计系统能够理解和复现其设计语言。

## 提取工作流

### Step 1: Capture（捕获）
- 截图全页面（Desktop + Mobile）
- 录制关键交互动效
- 收集 CSS 变量和设计 Token
- 提取字体加载信息

### Step 2: Visual Analysis（视觉分析）
- 色彩系统提取：主色、辅色、背景色、语义色
- 字体系统识别：标题体、正文字体、字重、字号阶梯
- 间距系统推算：网格基准、间距单位

### Step 3: Component Extraction（组件提取）
- 识别页面中的可复用组件（按钮、卡片、表单、导航等）
- 提取组件状态样式（hover/active/disabled）
- 记录组件的尺寸和间距规范

### Step 4: Design Token Extraction（设计 Token 提取）
- CSS 自定义属性提取 (`--color-*`, `--spacing-*`, `--font-*`)
- 颜色格式标准化（HEX/RGB/HSL）
- 断点系统识别（Breakpoints）

### Step 5: Brand DNA Analysis（品牌 DNA 分析）
- 品牌个性评估（Professional / Friendly / Luxurious / Minimal…）
- 情感关键词提取
- 行业定位识别
- 品牌语调分析

### Step 6: Style DNA Generation（Style DNA 生成）
- 根据上述分析生成标准化的 STYLE_DNA.json
- 验证 JSON Schema 符合性
- 输出至 `dna-engine/examples/` 目录

## 输出格式

每个提取结果是一个 STYLE_DNA.json 文件，遵循 `extraction-schema.json` 定义的 Schema。

## 使用方式

```bash
# 提取指定 URL 的设计 DNA
dna-engine extract --url https://example.com --output ./examples/example-dna.json

# 验证已有 DNA 文件
dna-engine validate ./examples/example-dna.json

# 比较两个 DNA 的相似度
dna-engine compare ./examples/a-dna.json ./examples/b-dna.json
```

## 相关文件

- `extraction-schema.json` — STYLE_DNA.json 的 JSON Schema 定义
- `dna-template.json` — 标准 DNA 模板
- `examples/` — 已提取的 DNA 案例