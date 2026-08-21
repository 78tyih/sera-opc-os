# Factories

> 生产工厂 — Sera OPC OS 的生产系统。

## 工厂列表

| 工厂 | 输入 | 输出 | 状态 |
|------|------|------|------|
| research-factory | 商业问题 | 研究报告 | ❌ 待创建 |
| product-factory | 市场机会 | 商业产品 | ❌ 待创建 |
| design-factory | 产品需求 | 设计资产 | ❌ 待创建 |
| engineering-factory | 设计规范 | 软件产品 | ❌ 待创建 |
| marketing-factory | 产品 | 流量 | ❌ 待创建 |
| content-factory | 主题 | 内容资产 | ❌ 待创建 |
| sales-factory | 产品 | 客户 | ❌ 待创建 |
| growth-factory | 产品 | 增长 | ❌ 待创建 |

## 工厂标准结构

```
factory-name/
├── agents/          # 工厂内部 Agent
├── workflows/       # 生产流水线
├── templates/       # 输出模板
├── quality/         # 质量标准
└── examples/        # 案例
```

## 详细定义

完整定义见 `docs/blueprints/Sera-OPC-OS-V2.0-Factory-Blueprint.md`