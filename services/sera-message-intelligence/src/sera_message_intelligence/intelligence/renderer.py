from __future__ import annotations

from html import escape

from .schemas import DailyBrief


_LABELS = [
    ("must_handle", "🔴 必须处理"),
    ("important", "🟠 重要信息"),
    ("actions", "✅ 待办行动"),
    ("decisions", "🧭 决策"),
    ("opportunities", "🟡 机会"),
    ("risks", "⚠ 风险"),
    ("people_to_reply", "👤 待回复的人"),
    ("resources", "🔗 资源"),
    ("knowledge", "🧠 知识沉淀"),
    ("topics", "💬 主题"),
]


def render_markdown(brief: DailyBrief) -> str:
    out = [f"# 个人情报简报 — {brief.date.isoformat()}", "", brief.executive_summary.strip(), ""]
    for field, label in _LABELS:
        items = getattr(brief, field)
        out += [f"## {label}", ""]
        if not items:
            out += ["本次没有识别到可验证条目。", ""]
            continue
        for item in items:
            refs = []
            for source in item.sources:
                refs.append(
                    f"{source.conversation_name or source.conversation_id}："
                    + ",".join(str(message_id) for message_id in source.message_ids)
                )
            out += [
                f"### {item.title}",
                item.summary,
                f"- 重要程度：{item.importance_score:.2f} · 可信度：{item.confidence:.2f}",
                f"- 证据：{'; '.join(refs)}",
                "",
            ]
    return "\n".join(out).rstrip() + "\n"


def render_html(brief: DailyBrief) -> str:
    sections = []
    for field, label in _LABELS:
        items = getattr(brief, field)
        cards = []
        if not items:
            cards.append('<p class="empty">本次没有识别到可验证条目。</p>')
        for item in items:
            refs = []
            for source in item.sources:
                refs.append(
                    f"{escape(source.conversation_name or source.conversation_id)}："
                    + ",".join(str(message_id) for message_id in source.message_ids)
                )
            cards.append(
                f'<article class="card"><h3>{escape(item.title)}</h3>'
                f'<p>{escape(item.summary)}</p>'
                f'<div class="meta">重要程度 {item.importance_score:.2f} · '
                f'可信度 {item.confidence:.2f}</div>'
                f'<div class="evidence">证据：{"; ".join(refs)}</div></article>'
            )
        sections.append(f'<section><h2>{escape(label)}</h2>{"".join(cards)}</section>')
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>个人情报简报 — {brief.date.isoformat()}</title><style>body{{font-family:Inter,system-ui,"Microsoft YaHei",sans-serif;max-width:960px;margin:40px auto;padding:0 20px;background:#f6f7f9;color:#16181d}}header{{padding:28px;background:white;border:1px solid #e5e7eb;border-radius:16px}}section{{margin-top:30px}}.card{{background:white;border:1px solid #e5e7eb;border-radius:14px;padding:18px;margin:12px 0}}h1,h2,h3{{margin-top:0}}.meta,.evidence,.empty{{font-size:13px;color:#667085;margin-top:10px}}.evidence{{font-family:ui-monospace,monospace}}</style></head><body><header><h1>个人情报简报 — {brief.date.isoformat()}</h1><p>{escape(brief.executive_summary)}</p></header>{"".join(sections)}</body></html>'''
