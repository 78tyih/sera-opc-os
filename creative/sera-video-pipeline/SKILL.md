---
name: sera-video-pipeline
purpose: HeyGen 口播 → 知识型短视频合成管线。把 HeyGen 生成的数字人口播视频（常是 9:16 竖屏内嵌横屏画面、上下白边）合成为 16:9 1080p 知识型短视频（信息图卡+字幕+BGM），全程本地完成（PIL 图卡/字幕 PNG + numpy BGM + ffmpeg 多步合成）。
inputs: HeyGen 口播视频（mp4，竖屏内嵌横屏）；口播文案脚本；分镜表（3-8s 切 Shot，A/B/C/D 版式）；品牌色/设计参数。
outputs: 16:9 1080p 知识型短视频（信息图卡、字幕、BGM、顶部进度条、结尾金句卡），响度标准化（loudnorm I=-15:TP=-1.5:LRA=11）。
workflow: |
  0. 先出分镜：按 3-8s 切 Shot，A/B/C/D 四种版式动态切换；每 Shot 写明口播/人物/HeyGen Motion Prompt/HyperFrames 动画/B-roll/字幕/转场；Safe Area L8%/R8%/T7%/B10%
  1. 探素材：ffprobe 查时长/分辨率；抽帧确认人物取景与白边
  2. 定裁剪：竖屏内嵌横屏按比例算内容带（如 crop=1080:594:0:644），crop→scale=1920:1080
  3. 对时间轴：ffmpeg silencedetect 拿停顿点，把脚本分句映射到语音段
  4. PIL 生成资产：信息图卡（860x560 透明 PNG）、scrim、字幕 PNG（关键词琥珀色高亮）、结尾卡
  5. BGM：numpy 合成 ambient pad（Cmaj7-Am7-Fmaj7-G6 循环），48kHz 立体声 WAV
  6. ffmpeg 四步合成：Pass A 主画面(图卡/字幕/进度条/结尾淡出) → Pass B 尾卡淡入 → Pass C concat 无损拼接 → Pass D 音频混音(voice+BGM sidechaincompress 闪避) + loudnorm
tools: Bash（ffmpeg / ffprobe）, Python（PIL / numpy，参考工作区 propfirm_video/gen_assets.py、gen_subs.py）
examples: |
  - ffprobe -v error -show_entries format=duration,size -of json input.mp4
  - ffmpeg -i input.mp4 -vf "crop=1080:594:0:644,scale=1920:1080" -c:a copy main.mp4
  - ffmpeg -af silencedetect=noise=-32dB:d=0.3 -f null - -i input.mp4
iron_rules: |
  - 禁用 xfade 一条流：loop 图片+trim+xfade 会在过渡前 2 秒卡死；必须「主片淡出到黑+尾卡淡入+concat demuxer」
  - homebrew ffmpeg 无 libass：字幕用 PIL 预渲染 PNG + overlay enable（顺便做关键词混色）
  - 循环 PNG 输入要 -loop 1 -t <时长>；中文字体用 Hiragino Sans GB.ttc（W6 粗体 index=1）
  - 核心文字 100% 由 HyperFrames 承担，HeyGen 与 B-roll 不出文字；A股惯例红涨绿跌
source: ~/.workbuddy/skills/heygen-knowledge-shortvideo/SKILL.md
---

# heygen-knowledge-shortvideo

## Purpose
HeyGen 口播 → 知识型短视频合成管线：把 HeyGen 生成的数字人口播视频（常是 9:16 竖屏内嵌横屏画面、上下白边）合成为 16:9 1080p 知识型短视频（信息图卡 + 字幕 + BGM）。全程本地完成：PIL 生成图卡/字幕 PNG + numpy 合成 BGM + ffmpeg 多步合成。

## Inputs
- HeyGen 口播视频（mp4，9:16 竖屏内嵌横屏画面）
- 口播文案脚本（分句）
- 分镜表（用户 2026-08-18 确立的导演规范：3–8s 切 Shot，A/B/C/D 版式）
- 品牌色 / 设计参数

## Outputs
- 16:9 1080p 知识型短视频：信息图卡、字幕（关键词高亮）、BGM、顶部进度条、结尾金句卡
- 响度标准化（`loudnorm=I=-15:TP=-1.5:LRA=11`）

## Workflow
```
0. 先出分镜：3-8s 切 Shot，A/B/C/D 四种版式（全人物/人物+图卡/网页录屏+PIP/纯图形）动态切换
1. 探素材：ffprobe 查时长/分辨率；抽帧确认取景与白边位置
2. 定裁剪：竖屏内嵌横屏按比例算内容带，crop → scale=1920:1080 得满屏横屏
3. 对时间轴：ffmpeg silencedetect 拿停顿点，把脚本分句映射到语音段（分句数=语音段数时对齐最准）
4. PIL 生成资产：信息图卡(860x560) / scrim / 字幕 PNG(关键词琥珀色 #F5A623) / 结尾卡
5. BGM：numpy 合成 ambient pad（Cmaj7-Am7-Fmaj7-G6 循环），48kHz 立体声 WAV
6. ffmpeg 四步合成：
   Pass A 主画面：crop/scale → scrim → 图卡(fade+滑入) → 字幕(enable 硬切) → 进度条 → 结尾淡出到黑
   Pass B 尾卡：ending.png -loop 1 → fade in
   Pass C concat demuxer 无损拼接（-c copy）
   Pass D 音频：voice(apad) + bgm(volume 0.3, sidechaincompress 闪避) → amix → afade → loudnorm
```

## Tools
- Bash：`ffmpeg` / `ffprobe`（homebrew 路径 `/opt/homebrew/bin/ffmpeg`）
- Python：PIL（图卡/字幕/结尾卡）、numpy（BGM）。参考实现：工作区 `propfirm_video/gen_assets.py`、`gen_subs.py`

## Examples
```bash
# 探素材
ffprobe -v error -show_entries format=duration,size -of json input.mp4
ffmpeg -ss 5 -i input.mp4 -frames:v 1 /tmp/probe.png

# 裁剪竖屏内嵌横屏（示例 1080x1920 → crop=1080:594:0:644）
ffmpeg -i input.mp4 -vf "crop=1080:594:0:644,scale=1920:1080" -c:a copy main.mp4

# 拿停顿点对时间轴
ffmpeg -i input.mp4 -af silencedetect=noise=-32dB:d=0.3 -f null -
```

## Iron Rules（坑）
- **禁用 xfade 一条流**：`loop 图片 + trim + xfade` 组合会在过渡前约 2 秒处彻底卡死（frame 计数归零）。务必拆成「主片淡出到黑 + 尾卡淡入 + concat demuxer」
- **homebrew ffmpeg 无 libass**：`ass`/`subtitles` 滤镜不可用 → 字幕用 PIL 预渲染 PNG + overlay enable，顺便做关键词混色高亮
- 中文字体：macOS 用 `/System/Library/Fonts/Hiragino Sans GB.ttc`（W6 粗体 index=1）；PingFang 在 PrivateFrameworks 不建议依赖
- 循环 PNG 输入要 `-loop 1 -t <时长>`，避免无限流拖慢/挂住
- 设计规范：深色 #0D1420 底、白 #F5F7FA、蓝灰 #7E8AA0、琥珀 #F5A623；A 股惯例红涨绿跌；图卡随语音分句切换（fade 0.35-0.4s + 左侧 40px 滑入）；片尾 4s 金句卡凑足 35-45s

## Source
`~/.workbuddy/skills/heygen-knowledge-shortvideo/SKILL.md`
