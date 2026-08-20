# AI SaaS 产品设计模式

## 核心原则

AI SaaS 产品与传统 SaaS 产品在设计上有本质区别：AI 的输出是不可预测的，这为 UI 设计带来了独特的挑战。AI SaaS 设计的核心原则是"管理期望"——用户需要明确知道 AI 能做什么、不能做什么、以及为什么做出这样的输出。同时，AI 产品的"魔法时刻"需要被精心设计，让用户感受到 AI 的强大，而非被 AI 的不确定性困扰。

---

## 为什么有效

### 1. 不确定性管理
传统 UI 的输入-输出是确定性的（点击按钮 -> 执行操作 -> 显示结果）。AI 的输出是概率性的，可能延迟、可能不准确、可能需要多次尝试。好的 AI UX 设计通过状态提示、进度反馈和预期管理，让用户对 AI 的不确定性有心理准备。

### 2. 信任建立的特殊性
AI 产品的信任建立与传统产品不同。用户需要同时信任"技术能力"（AI 能否准确完成任务）和"数据安全"（我的数据会不会被滥用）。因此，AI 产品需要同时展示"能力证明"和"安全承诺"。

### 3. 控制感与自动化的平衡
AI 的强大之处在于自动化，但过度自动化会让用户感到失控。好的 AI 设计在 AI 的自主性和用户的控制权之间找到平衡——AI 提供建议，用户做最终决定；AI 执行操作，用户随时可以干预。

---

## 核心设计模式

### 1. AI 聊天界面设计

```css
/* AI 聊天界面布局 */
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  max-width: 800px;
  margin: 0 auto;
}

.message-row {
  display: flex;
  gap: 0.75rem;
  padding: 1rem;
  animation: messageIn 0.3s ease;
}

.message-row.user {
  justify-content: flex-end;
}

.message-row.assistant {
  justify-content: flex-start;
}

.message-bubble {
  max-width: 75%;
  padding: 0.75rem 1rem;
  border-radius: 16px;
  line-height: 1.6;
}

.message-bubble.user {
  background: #1a1a1a;
  color: #fff;
  border-bottom-right-radius: 4px;
}

.message-bubble.assistant {
  background: #f5f5f5;
  color: #1a1a1a;
  border-bottom-left-radius: 4px;
}

/* AI 输入状态指示器 */
.typing-indicator {
  display: flex;
  gap: 0.25rem;
  padding: 0.5rem;
}

.typing-dot {
  width: 8px;
  height: 8px;
  background: #999;
  border-radius: 50%;
  animation: typingBounce 1.4s infinite;
}

@keyframes typingBounce {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-4px); }
}
```

**AI 聊天界面设计要点**：
- **消息流清晰**：用户消息和 AI 消息在视觉上有明显区分
- **流式响应**：AI 生成内容时逐字显示，减少等待焦虑
- **输入状态提示**：AI 正在"思考"时，显示过渡动画
- **上下文保持**：聊天历史保持在可视区域内，新消息自动滚到底部
- **操作按钮**：AI 回答后，提供"复制"、"重新生成"、"分享"等操作
- **来源引用**：AI 引用外部信息时，标注来源和置信度

### 2. 结果展示模式

| 结果类型 | 展示模式 | 设计要点 |
|---------|---------|---------|
| 文本生成 | 富文本预览 | 支持 Markdown 渲染、代码高亮、列表 |
| 图像生成 | 画廊模式 | 网格展示，支持缩放、下载、重新生成 |
| 数据分析 | 图表 + 文字 | 先展示关键洞察，再展示详细数据 |
| 代码生成 | 代码编辑器 | 语法高亮，行号，一键复制，运行预览 |
| 结构化数据 | 表格模式 | 列排序、搜索、导出 CSV |

### 3. 模型选择界面

```html
<!-- 模型选择器 -->
<div class="model-selector">
  <label class="model-select-label">选择模型</label>
  <div class="model-options">
    <div class="model-option active">
      <div class="model-name">GPT-4o</div>
      <div class="model-desc">最强大、最智能的模型</div>
      <div class="model-badge">推荐</div>
    </div>
    <div class="model-option">
      <div class="model-name">GPT-4o Mini</div>
      <div class="model-desc">快速、经济，适合简单任务</div>
    </div>
    <div class="model-option">
      <div class="model-name">Claude 3.5 Sonnet</div>
      <div class="model-desc">擅长长文本和推理</div>
    </div>
  </div>
</div>
```

**模型选择设计原则**：
- 每个模型有清晰的"能力标签"（速度、价格、能力范围）
- 默认推荐最佳模型，降低用户选择负担
- 高级用户可以通过"设置"选择更精细的参数
- 模型切换后，对话历史应当保留
- 显示当前模型的使用额度或成本估算

### 4. API Playground 设计

```css
/* API Playground 布局 */
.api-playground {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  height: 600px;
}

.api-request-panel {
  display: flex;
  flex-direction: column;
}

.api-request-editor {
  flex: 1;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.875rem;
  padding: 1rem;
  resize: none;
}

.api-response-panel {
  display: flex;
  flex-direction: column;
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1rem;
}
```

**Playground 设计要点**：
- 左右分栏：左侧请求编辑，右侧响应展示
- 参数面板：可折叠的参数配置区域
- 实时预览：修改参数后自动更新响应
- 请求历史：保存最近 10 次请求，支持回顾
- 代码生成：自动生成 curl、Python、JavaScript 等调用代码
- 错误处理：清晰展示错误信息，提供修复建议

### 5. 按使用量定价展示

| 定价模式 | 展示方式 | 设计要点 |
|---------|---------|---------|
| 按 Token 计费 | 实时计数 + 估算器 | 显示已用 Token 和预估费用 |
| 按请求计费 | 月度配额仪表盘 | 进度条展示剩余额度 |
| 按时间计费 | 订阅制 + 用量封顶 | "标准版 ¥199/月，含 100 万 Token" |
| 免费额度 | 使用进度条 | "免费额度剩余 70%" |

### 6. 等待清单模式（Waitlist）

```css
/* 等待清单表单 */
.waitlist-container {
  max-width: 480px;
  margin: 0 auto;
  text-align: center;
  padding: 4rem 2rem;
}

.waitlist-position {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 0.5rem;
}

.waitlist-progress {
  width: 100%;
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
  margin: 1rem 0;
}

.waitlist-progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #1a1a1a, #444);
  border-radius: 4px;
  transition: width 1s ease;
}
```

**等待清单设计要点**：
- 展示排队位置，让用户知道"进度"
- 估计等待时间，管理用户预期
- 邀请好友可以插队，利用社交裂变
- 提供"提前体验"的付费选项
- 到达时发送通知，减少用户流失

### 7. 演示模式（Demo Mode）

```css
/* 演示模式覆盖层 */
.demo-overlay {
  position: relative;
}

.demo-overlay::after {
  content: "演示模式";
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: rgba(0,0,0,0.7);
  color: #fff;
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-size: 0.75rem;
  z-index: 10;
}

.demo-input-hint {
  border: 2px dashed #e0e0e0;
  border-radius: 8px;
  padding: 1rem;
  text-align: center;
  color: #999;
}
```

**演示模式原则**：
- 清晰标识"这是演示数据"，避免用户误解
- 演示操作不应触发真实 API 调用
- 演示数据应该看起来真实但容易识别
- 提供"立即开始"的 CTA 引导用户注册
- 演示模式中的功能限制要明确标注

---

## 示例

### ChatGPT 界面设计
- 极简的聊天界面，输入框固定在底部
- 模型选择使用下拉菜单，不干扰主界面
- 流式输出实时显示，减少等待感
- 对话历史在侧边栏，支持搜索
- 代码块自带复制按钮和语言标签

### DALL-E 图像生成界面
- 提示词输入框 + 参数设置面板
- 生成的图像以网格展示，支持缩放
- 每次生成 4 个变体，让用户选择
- 显示"生成中"的进度动画
- 生成结果支持编辑、重新生成、下载

---

## 何时使用

- 设计任何 AI 驱动的 SaaS 产品
- 用户与 AI 模型有交互操作时
- 需要展示 AI 生成结果的界面
- 按使用量计费的 AI 服务
- 需要管理用户对 AI 能力期望的产品

## 何时不宜使用

- 非 AI 驱动的传统 SaaS 产品——不需要展示模型选择、Token 计数等
- AI 能力完全在后台运行（如推荐系统、垃圾过滤）——不需要用户可见的 AI 交互界面
- 用户不需要知道"这是 AI 在运行"的产品——后端 AI 功能不需要前端 AI 设计模式
- 极简的 AI 工具（如 AI 翻译按钮）——不需要复杂的界面，一个按钮即可
- 面向非技术用户的产品——避免使用"模型"、"Token"、"参数"等技术术语