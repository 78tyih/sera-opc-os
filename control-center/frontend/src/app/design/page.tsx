"use client"

import { useRef, useState, type CSSProperties } from "react"
import { motion } from "framer-motion"
import {
  Grip,
  Sparkles,
  Droplets,
  Layers,
  Sun,
  Pause,
  Play,
  MousePointer2,
} from "lucide-react"

// Design Lab —— C · 玻璃金融 · 玻璃拟态实验室
// 目标：让"玻璃"真的可见。backdrop-blur 只有在玻璃后面有东西时才会显形，
// 所以用一个会动的彩色光斑背景 + 可拖动的玻璃卡片 + 实时参数滑块来演示。

interface Orb {
  size: number
  color: string
  top: string
  left: string
  duration: number
  x: number
  y: number
}

const ORBS: Orb[] = [
  { size: 560, color: "radial-gradient(circle at 50% 50%, rgba(0,102,255,0.60), transparent 70%)", top: "-120px", left: "8%", duration: 11, x: 70, y: 40 },
  { size: 460, color: "radial-gradient(circle at 50% 50%, rgba(38,146,255,0.45), transparent 70%)", top: "30%", left: "72%", duration: 14, x: -60, y: 50 },
  { size: 380, color: "radial-gradient(circle at 50% 50%, rgba(94,234,212,0.30), transparent 70%)", top: "62%", left: "20%", duration: 16, x: 50, y: -60 },
  { size: 300, color: "radial-gradient(circle at 50% 50%, rgba(168,85,247,0.28), transparent 70%)", top: "8%", left: "48%", duration: 18, x: -40, y: 70 },
]

function Slider({
  label,
  value,
  min,
  max,
  step,
  onChange,
  unit,
  hint,
}: {
  label: string
  value: number
  min: number
  max: number
  step: number
  onChange: (v: number) => void
  unit: string
  hint: string
}) {
  return (
    <div>
      <div className="flex items-center justify-between mb-1.5">
        <span className="text-xs" style={{ color: "var(--text-primary)" }}>{label}</span>
        <span className="text-xs font-semibold" style={{ color: "var(--brand)" }}>
          {value}{unit}
        </span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={e => onChange(Number(e.target.value))}
        className="w-full"
        style={{ accentColor: "var(--brand)" }}
      />
      <div className="text-[10px] mt-1" style={{ color: "var(--text-muted)" }}>{hint}</div>
    </div>
  )
}

export default function DesignLabPage() {
  const stageRef = useRef<HTMLDivElement>(null)
  const [opacity, setOpacity] = useState(0.05)      // 玻璃不透明度（越高越"奶"）
  const [blur, setBlur] = useState(20)              // 模糊强度 px
  const [bevel, setBevel] = useState(true)          // 顶部高光内斜面
  const [animate, setAnimate] = useState(true)      // 背景光斑动效

  // 玻璃核心样式（C · 玻璃金融）
  const glass = (extra?: CSSProperties, strong = false): CSSProperties => ({
    background: strong
      ? `rgba(255,255,255,${Math.min(0.18, opacity + 0.05)})`
      : `rgba(255,255,255,${opacity})`,
    border: "1px solid rgba(255,255,255,0.08)",
    borderRadius: 18,
    boxShadow: bevel ? "inset 0 1px 0 0 rgba(255,255,255,0.14)" : "none",
    backdropFilter: `blur(${blur}px) saturate(140%)`,
    WebkitBackdropFilter: `blur(${blur}px) saturate(140%)`,
    ...extra,
  })

  return (
    <div className="space-y-5">
      {/* 顶部 */}
      <div>
        <h1 className="text-2xl font-bold" style={{ color: "var(--text-primary)" }}>C · 玻璃金融 · 玻璃拟态实验室</h1>
        <p className="text-sm mt-1" style={{ color: "var(--text-muted)" }}>
          拖右边的玻璃卡经过光斑、拉下面三个滑块，亲手把「玻璃」的光透、磨砂、高光调出你要的那个度。
        </p>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-[1fr_300px] gap-4 items-start">
        {/* 舞台 */}
        <div
          ref={stageRef}
          className="relative rounded-2xl overflow-hidden border"
          style={{ minHeight: 560, background: "#05070A", borderColor: "var(--border)" }}
        >
          {/* 会动的彩色光斑（玻璃后面需要"有东西"） */}
          {ORBS.map((o, i) => (
            <motion.div
              key={i}
              className="absolute rounded-full pointer-events-none"
              style={{
                width: o.size,
                height: o.size,
                background: o.color,
                filter: "blur(46px)",
                top: o.top,
                left: o.left,
              }}
              animate={animate ? { x: [0, o.x, 0], y: [0, o.y, 0] } : { x: 0, y: 0 }}
              transition={{ duration: o.duration, repeat: Infinity, ease: "easeInOut" }}
            />
          ))}

          {/* 内容层（相对定位在光斑之上） */}
          <div className="relative p-6" style={{ pointerEvents: "none" }}>
            {/* 固定玻璃 spotlight 卡（跨过两个光斑，展示 blur 显形） */}
            <div className="p-5" style={{ ...glass({ maxWidth: 420 }), pointerEvents: "auto" }}>
              <div className="text-xs font-semibold flex items-center gap-1.5 mb-2" style={{ color: "#F8F9FC" }}>
                <Sparkles className="w-3.5 h-3.5" style={{ color: "#0066FF" }} /> 玻璃显形区
              </div>
              <div className="text-[11px] leading-relaxed" style={{ color: "rgba(248,249,252,0.7)" }}>
                这块玻璃的下面正好压着两个蓝色光斑。注意光斑在玻璃内外被「磨砂」了多少——这就是 backdrop-blur 的意义。
              </div>
            </div>
          </div>

          {/* 可拖动玻璃卡 */}
          <motion.div
            drag
            dragConstraints={stageRef}
            dragElastic={0.15}
            dragMomentum={false}
            whileDrag={{ scale: 1.03 }}
            className="absolute p-4 cursor-grab active:cursor-grabbing"
            style={{ ...glass({ width: 240 }, true), top: "42%", left: "54%", pointerEvents: "auto" }}
          >
            <div className="flex items-center gap-2 mb-3 text-xs font-semibold" style={{ color: "#F8F9FC" }}>
              <Grip className="w-3.5 h-3.5" style={{ color: "rgba(248,249,252,0.5)" }} />
              拖动我穿过光斑
            </div>
            <div className="text-2xl font-bold mb-1" style={{ color: "#F8F9FC" }}>12.4K</div>
            <div className="text-[11px]" style={{ color: "rgba(248,249,252,0.6)" }}>记忆对象 · Memory Objects</div>
          </motion.div>
        </div>

        {/* 控制面板 */}
        <div className="space-y-4">
          <div className="htx-card p-5">
            <div className="text-sm font-semibold mb-4 flex items-center gap-1.5" style={{ color: "var(--text-primary)" }}>
              <Layers className="w-4 h-4" style={{ color: "var(--brand)" }} /> 玻璃参数
            </div>
            <div className="space-y-4">
              <Slider
                label="不透明度" value={opacity} min={0.02} max={0.18} step={0.005}
                onChange={setOpacity} unit="" hint="越高越「奶玻璃」，越低越通透"
              />
              <Slider
                label="模糊强度" value={blur} min={0} max={40} step={1}
                onChange={setBlur} unit="px" hint="0 = 无磨砂，20+ = 强磨砂"
              />
              <div className="flex items-center justify-between">
                <span className="text-xs flex items-center gap-1.5" style={{ color: "var(--text-primary)" }}>
                  <Sun className="w-3.5 h-3.5" style={{ color: "var(--brand)" }} /> 顶部高光内斜面
                </span>
                <button
                  onClick={() => setBevel(v => !v)}
                  className="px-3 py-1 rounded-full text-xs font-medium transition-colors"
                  style={{
                    background: bevel ? "var(--brand)" : "var(--bg-surface-hover)",
                    color: bevel ? "#fff" : "var(--text-muted)",
                    border: `1px solid ${bevel ? "transparent" : "var(--border)"}`,
                  }}
                >
                  {bevel ? "开" : "关"}
                </button>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs flex items-center gap-1.5" style={{ color: "var(--text-primary)" }}>
                  <Droplets className="w-3.5 h-3.5" style={{ color: "var(--brand)" }} /> 背景光斑动效
                </span>
                <button
                  onClick={() => setAnimate(v => !v)}
                  className="px-3 py-1 rounded-full text-xs font-medium transition-colors"
                  style={{
                    background: animate ? "var(--brand)" : "var(--bg-surface-hover)",
                    color: animate ? "#fff" : "var(--text-muted)",
                    border: `1px solid ${animate ? "transparent" : "var(--border)"}`,
                  }}
                >
                  {animate ? <Play className="w-3 h-3" /> : <Pause className="w-3 h-3" />}
                </button>
              </div>
            </div>
          </div>

          <div className="htx-card p-5">
            <div className="text-sm font-semibold mb-3 flex items-center gap-1.5" style={{ color: "var(--text-primary)" }}>
              <MousePointer2 className="w-4 h-4" style={{ color: "var(--brand)" }} /> 玻璃三要素
            </div>
            <ol className="space-y-2 text-xs" style={{ color: "var(--text-secondary)" }}>
              <li>① backdrop-blur + saturate —— 磨砂 + 提饱和</li>
              <li>② inset 顶部 1px 高光 —— 玻璃边缘反光（非投影）</li>
              <li>③ 半透明白底 rgba(255,255,255,α) —— 光的入射感</li>
            </ol>
            <p className="text-[11px] mt-3 leading-relaxed" style={{ color: "var(--text-muted)" }}>
              关键：玻璃效果只在「后面有内容」时成立。所以真实页面的背景要做成有景深或光斑，不能是纯平黑。
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}