# 金融科技 UI 设计模式

## 核心原则

金融科技（Fintech）UI 设计必须在"信任感"和"功能性"之间找到平衡。用户将真实的资金数据托付给产品，因此每一个像素都应当传递安全、可靠和专业。同时，高净值用户对效率和信息密度有较高要求，设计不能为了美观而牺牲信息获取速度。

---

## 为什么有效

### 1. 信任是金融科技的第一货币
金融产品的用户决策中，信任占据了 80% 的权重。一个看起来"不专业"的界面会让用户立即怀疑数据的安全性。视觉设计中的"信任信号"——整洁的布局、专业的字体、安全徽章、合规信息——是用户决定是否使用产品的关键因素。

### 2. 信息密度与可读性的平衡
金融数据天然具有高信息密度（数字、图表、表格、状态）。用户需要快速扫描大量信息并做出决策。设计的关键是建立清晰的视觉层级，让用户在 3 秒内找到需要的关键数据。

### 3. 降低焦虑感
金融操作（交易、转账、投资）天然带有焦虑感。设计应该通过色彩、动效和反馈机制来降低用户的焦虑——确认状态、进度指示、成功动画都是有效的焦虑缓解手段。

---

## 核心设计模式

### 1. 投资组合仪表盘（Portfolio Dashboard）

```css
/* 组合仪表盘关键样式 */
.portfolio-overview {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.portfolio-card {
  background: #fff;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.portfolio-value {
  font-size: 2.5rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.portfolio-change {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-weight: 600;
  font-size: 0.875rem;
}

.portfolio-change.positive { color: #16a34a; }
.portfolio-change.negative { color: #dc2626; }
```

**仪表盘设计要点**：
- **总资产净值**：放置在页面顶部最显眼位置
- **关键指标网格**：日收益、总收益、风险评级、持仓分布
- **趋势图**：使用 Sparkline 或微缩折线图展示近期趋势
- **资产分布**：使用饼图或环形图展示资产配置比例
- **最近交易**：列表形式展示最近 5-10 笔交易，可快速扫描

### 2. 交易历史记录（Transaction History）

| 元素 | 设计原则 | 实现建议 |
|------|---------|---------|
| 日期分组 | 按日期分组，今天 > 昨天 > 本周 > 本月 | 使用粘性日期标题 |
| 交易类型 | 图标 + 颜色区分 | 转入=绿色、转出=红色、兑换=蓝色 |
| 金额展示 | 右对齐，大号字体 | 正数绿色，负数红色，带货币符号 |
| 状态标签 | 轻量徽章 | 已完成、处理中、失败 |
| 筛选器 | 顶部导航式筛选 | 全部、转入、转出、兑换、失败 |
| 搜索 | 支持关键词和金额搜索 | 实时搜索，结合键盘快捷键 |

```css
/* 交易记录行样式 */
.transaction-item {
  display: grid;
  grid-template-columns: 40px 1fr auto;
  align-items: center;
  padding: 1rem 0;
  border-bottom: 1px solid #f0f0f0;
}

.transaction-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.transaction-icon.deposit { background: #dcfce7; }
.transaction-icon.withdrawal { background: #fee2e2; }
```

### 3. KYC 流程设计（Know Your Customer）

KYC 流程是用户注册和验证身份的关键环节，设计不当会导致大量用户流失。

**KYC 流程设计原则**：
1. **分步展示**：显示总步骤数（如"步骤 2/5"），让用户知道进度
2. **即时验证**：上传身份证后立即显示验证结果，不延迟
3. **示例引导**：展示"正确示例"和"错误示例"，减少上传失败
4. **容错设计**：上传失败时提供具体原因和重试选项
5. **隐私保护**：在页面上展示"数据加密"和"隐私保护"的信任信号
6. **保存草稿**：允许用户保存进度，稍后继续

```html
<!-- KYC 上传组件 -->
<div class="kyc-upload-zone">
  <div class="upload-icon">
    <svg><!-- 上传图标 --></svg>
  </div>
  <p class="upload-title">上传身份证正面</p>
  <p class="upload-hint">支持 JPG、PNG，文件大小不超过 10MB</p>
  <div class="upload-example">
    <img src="example-correct.jpg" alt="正确示例">
    <span class="example-label correct">正确示例</span>
    <img src="example-wrong.jpg" alt="错误示例">
    <span class="example-label wrong">错误示例</span>
  </div>
  <button class="upload-btn">选择文件</button>
</div>
```

### 4. 交易界面（Trading Interface）

```css
/* 交易面板布局 */
.trading-panel {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 1rem;
  height: 100%;
}

/* 订单簿样式 */
.order-book {
  font-family: 'JetBrains Mono', 'SF Mono', monospace;
  font-size: 0.75rem;
  line-height: 1.6;
}

.order-book .price {
  font-weight: 600;
}

.order-book .price.ask { color: #dc2626; }
.order-book .price.bid { color: #16a34a; }
```

**交易界面设计要点**：
- **实时数据**：价格数据使用等宽字体，小数点对齐
- **买入/卖出按钮**：买入用绿色，卖出用红色，大按钮方便快速操作
- **订单簿**：买盘和卖盘分别展示，中间显示最新成交价
- **K 线图**：支持多时间周期（1m、5m、15m、1h、4h、1d）
- **交易日志**：实时展示用户交易记录，带时间戳
- **风险提示**：高风险操作时展示二次确认弹窗

### 5. 安全徽章与合规信号

| 安全信号 | 放置位置 | 设计要点 |
|---------|---------|---------|
| SSL 加密标识 | 登录页、注册页 | 使用锁图标 + "256 位加密" |
| 合规认证 logo | 页脚 | 金融监管机构 logo（如 FINRA、FCA） |
| 资金托管说明 | 存款页、提现页 | "用户资金由 X 银行托管" |
| 双因素认证 | 安全设置页 | 展示 2FA 已启用作为信任信号 |
| 保险保障 | 产品首页 | "最高 X 万元保险保障" |
| 隐私政策链接 | 所有数据输入页面 | 简短描述 + 链接 |

### 6. 图表模式（Chart Patterns）

```css
/* 图表容器 */
.chart-container {
  background: #fff;
  border-radius: 12px;
  padding: 1rem;
  position: relative;
}

.chart-toolbar {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.chart-timeframe {
  padding: 0.25rem 0.75rem;
  border-radius: 6px;
  font-size: 0.8rem;
  cursor: pointer;
  border: 1px solid #e0e0e0;
  background: #fff;
}

.chart-timeframe.active {
  background: #1a1a1a;
  color: #fff;
  border-color: #1a1a1a;
}
```

**图表设计原则**：
- 支持多时间维度切换（1m、5m、15m、1h、4h、1d、1w）
- 图表类型切换（K 线、折线、面积、柱状图）
- 技术指标叠加（MA、MACD、RSI、布林带）
- 大数据量时使用数据聚合（如超过 1000 个数据点自动聚合）
- 触摸设备支持缩放和平移

---

## 示例

### Robinhood 的金融科技设计
- 极简的卡片式布局，降低金融数据的复杂性
- 使用绿色/红色直观表示涨跌
- 圆形进度条展示投资组合配置
- 交易流程极简化，减少操作步骤
- 使用微动效（如数字跳动）增加数据"活"的感觉

### Revolut 的金融科技设计
- 深色主题为主，传递金融专业感
- 预算以环形图展示，直观易读
- 交易记录使用卡片式分组，按日期和时间排序
- 多币种账户使用不同颜色区分
- 安全功能（如临时锁卡）使用大按钮和明确文案

---

## 何时使用

- 设计金融科技产品（银行、投资、支付、贷款）
- 任何需要展示金融数据的界面
- 需要用户信任和资金安全感的操作流程
- 高信息密度的数据展示页面
- 需要合规和监管信号的设计

## 何时不宜使用

- 非金融类的轻量级产品——过度使用金融设计语言会让用户感到"过度严肃"
- 面向儿童或青少年的产品——应使用更友好、色彩更丰富的设计
- 简单的个人记账工具——不需要复杂的金融图表和仪表盘
- 用户无法理解金融术语的产品——应优先使用通俗语言而非专业术语
- 设计品牌定位为"轻松、有趣"的产品——金融科技的严肃感与轻松品牌相悖