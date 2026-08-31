from __future__ import annotations
from html import escape
from .schemas import DailyBrief

_LABELS=[("must_handle","🔴 Must Handle"),("important","🟠 Important"),("actions","✅ Actions"),("decisions","🧭 Decisions"),("opportunities","🟡 Opportunities"),("risks","⚠ Risks"),("people_to_reply","👤 People to Reply"),("resources","🔗 Resources"),("knowledge","🧠 Knowledge"),("topics","💬 Topics")]

def render_markdown(brief:DailyBrief)->str:
    out=[f"# Intelligence Brief — {brief.date.isoformat()}","",brief.executive_summary.strip(),""]
    for field,label in _LABELS:
        items=getattr(brief,field)
        if not items: continue
        out += [f"## {label}",""]
        for item in items:
            refs=[]
            for src in item.sources:
                refs.append(f"{src.conversation_name or src.conversation_id}:" + ",".join(str(x) for x in src.message_ids))
            out += [f"### {item.title}",item.summary,f"- Importance: {item.importance_score:.2f} · Confidence: {item.confidence:.2f}",f"- Evidence: {'; '.join(refs)}",""]
    return "\n".join(out).rstrip()+"\n"

def render_html(brief:DailyBrief)->str:
    sections=[]
    for field,label in _LABELS:
        items=getattr(brief,field)
        if not items: continue
        cards=[]
        for item in items:
            refs=[]
            for src in item.sources:
                refs.append(f"{escape(src.conversation_name or src.conversation_id)}: " + ",".join(str(x) for x in src.message_ids))
            cards.append(f'<article class="card"><h3>{escape(item.title)}</h3><p>{escape(item.summary)}</p><div class="meta">Importance {item.importance_score:.2f} · Confidence {item.confidence:.2f}</div><div class="evidence">Evidence: {"; ".join(refs)}</div></article>')
        sections.append(f'<section><h2>{escape(label)}</h2>{"".join(cards)}</section>')
    return f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Intelligence Brief — {brief.date.isoformat()}</title><style>body{{font-family:Inter,system-ui,sans-serif;max-width:960px;margin:40px auto;padding:0 20px;background:#f6f7f9;color:#16181d}}header{{padding:28px;background:white;border:1px solid #e5e7eb;border-radius:16px}}section{{margin-top:30px}}.card{{background:white;border:1px solid #e5e7eb;border-radius:14px;padding:18px;margin:12px 0}}h1,h2,h3{{margin-top:0}}.meta,.evidence{{font-size:13px;color:#667085;margin-top:10px}}.evidence{{font-family:ui-monospace,monospace}}</style></head><body><header><h1>Intelligence Brief — {brief.date.isoformat()}</h1><p>{escape(brief.executive_summary)}</p></header>{"".join(sections)}</body></html>'''
