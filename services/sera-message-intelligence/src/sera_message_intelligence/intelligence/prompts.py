CHUNK_SYSTEM = """You summarize chat messages into factual structured JSON.
Never invent facts. Every claim must include exact message_ids copied from the supplied [m:ID] messages.
Return JSON only."""

MERGE_SYSTEM = """You create one Personal Intelligence Brief from validated chat claims.
Do not produce per-group diaries. Prioritize what the owner needs to notice or act on.
Every output item MUST include real message_ids copied from the supplied validated claims.
Never invent message IDs or unsupported facts. Return JSON only."""

def chunk_prompt(chunk_text:str)->str:
    return f'''Summarize this conversation chunk.
Return:
{{"summary":"short factual overview","claims":[{{"kind":"key_point|action|decision|risk|opportunity|resource","text":"...","message_ids":[1,2]}}]}}
Each claim must cite the specific messages that support it.
Messages:
{chunk_text}'''

def merge_prompt(summary_json:str)->str:
    return f'''Create candidate items for a single cross-group intelligence brief.
Use ONLY the validated claims below.
Return:
{{"executive_summary":"...","items":[{{"category":"must_handle|important|actions|decisions|opportunities|risks|people_to_reply|resources|knowledge|topics","title":"...","summary":"...","message_ids":[1,2],"confidence":0.0,"importance":{{"personal_relevance":0.0,"actionability":0.0,"urgency":0.0,"novelty":0.0,"source_weight":0.0}}}}]}}
Validated chunk claims:
{summary_json}'''
