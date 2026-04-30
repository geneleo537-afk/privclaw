/**
 * PrivClaw 智慧龙虾定制 — 统一网页风格规范
 *
 * 所有页面和组件必须遵循此文件定义的设计令牌。
 * AI 开发新页面时直接引用此文件，确保视觉一致性。
 *
 * ⚠️ 本文件仅作为规范参考和常量导出，不上传云端。
 */

/* ================================================================
 * 1. 品牌色彩体系
 * ================================================================ */
export const BRAND_COLORS = {
  /** 主品牌色 — 龙虾红，用于 CTA 按钮、高亮文字、重点标注 */
  primary: '#EB4C4C',
  /** 品牌浅色 — hover 状态、次级装饰 */
  primaryLight: '#FF7070',
  /** 品牌淡色 — 背景装饰、分割线、弱强调 */
  primaryPale: '#FFA6A6',
  /** 品牌暖色 — 标签背景、Hero 渐变点缀 */
  primaryCream: '#FFEDC7',
} as const

/** 语义色（非品牌色场景使用） */
export const SEMANTIC_COLORS = {
  success: '#10B981',
  warning: '#F59E0B',
  error: '#EF4444',
  info: '#3B82F6',
} as const

/** 中性色阶 */
export const NEUTRAL = {
  white: '#FFFFFF',
  bg: '#FAFAFA',          // section 交替背景
  border: '#E5E5E5',      // 卡片/输入框边框
  textPrimary: '#111827',  // 标题、正文强调
  textSecondary: '#6B7280', // 正文
  textMuted: '#9CA3AF',    // 辅助说明
  textDisabled: '#D1D5DB',
} as const

/* ================================================================
 * 2. 字号体系（映射 Tailwind class）
 * ================================================================ */
export const TYPOGRAPHY = {
  /** 页面主标题 — Hero h1 */
  heroTitle: 'text-5xl sm:text-6xl lg:text-[5.5rem] font-black leading-[1.05] tracking-tight',
  /** section 主标题 — h2 */
  sectionTitle: 'text-5xl sm:text-6xl font-black',
  /** section 红色标签 */
  sectionLabel: 'text-2xl font-bold uppercase tracking-widest',
  /** section 描述文字 */
  sectionDesc: 'text-xl text-gray-500',
  /** 卡片标题 */
  cardTitle: 'text-base font-black text-gray-900',
  /** 卡片描述 */
  cardDesc: 'text-sm text-gray-500 leading-relaxed',
  /** 统计数字 */
  statNumber: 'text-4xl font-black',
  /** 统计标签 */
  statLabel: 'text-sm text-gray-400',
} as const

/* ================================================================
 * 3. 间距与布局
 * ================================================================ */
export const LAYOUT = {
  /** 最大内容宽度 */
  maxWidth: 'max-w-7xl',
  /** section 内边距 */
  sectionPadding: 'px-4 py-12',
  /** section 最小高度（全屏 snap） */
  sectionMinHeight: 'min-h-screen',
  /** 容器通用 class */
  container: 'container mx-auto max-w-7xl',
  /** 标题到内容的间距 */
  titleGap: 'mb-12',
  /** 卡片网格间距 */
  gridGap: 'gap-6',
} as const

/* ================================================================
 * 4. 圆角规范
 * ================================================================ */
export const RADIUS = {
  /** 按钮 — 圆角胶囊 */
  button: 'rounded-full',
  /** 卡片 — 大圆角 */
  card: 'rounded-2xl',
  /** 卡片加大 — 流程步骤等 */
  cardLg: 'rounded-3xl',
  /** 输入框 */
  input: 'rounded-2xl',
  /** 标签/badge */
  badge: 'rounded-full',
  /** 图标容器 */
  iconBox: 'rounded-xl',
} as const

/* ================================================================
 * 5. 按钮规范
 * ================================================================ */
export const BUTTON = {
  /** 主要 CTA */
  primary: {
    className: 'rounded-full font-bold text-white border-0 hover:opacity-90 transition-opacity',
    style: { backgroundColor: '#EB4C4C' },
    sizes: {
      sm: 'h-10 px-6 text-sm',
      md: 'h-11 px-7 text-sm',
      lg: 'h-12 px-10 text-base',
      xl: 'h-14 px-10 text-base',
    },
  },
  /** 描边按钮 */
  outline: {
    className: 'rounded-full font-semibold border-2 hover:opacity-80 transition-opacity bg-transparent',
    style: { borderColor: '#EB4C4C', color: '#EB4C4C' },
  },
  /** 反色按钮（用于深色背景） */
  inverted: {
    className: 'rounded-full font-bold border-0 hover:opacity-90 transition-opacity',
    style: { backgroundColor: 'white', color: '#EB4C4C' },
  },
} as const

/* ================================================================
 * 6. 卡片规范
 * ================================================================ */
export const CARD = {
  /** 标准卡片 */
  base: 'rounded-2xl border border-gray-100 bg-white',
  /** 悬停效果 */
  hover: 'hover:shadow-xl transition-all duration-300 hover:-translate-y-1',
  /** 图标容器尺寸 */
  iconSize: {
    sm: 'w-11 h-11',
    md: 'w-12 h-12',
    lg: 'w-14 h-14',
  },
  /** 图标容器样式 */
  iconStyle: {
    className: 'rounded-xl flex items-center justify-center',
    style: { backgroundColor: 'rgba(235,76,76,0.08)', color: '#EB4C4C' },
  },
} as const

/* ================================================================
 * 7. 动效系统
 * ================================================================ */
export const ANIMATION = {
  /** 可用的 data-animate 值 */
  types: ['fade-up', 'fade-in', 'scale-in', 'slide-left', 'slide-right', 'zoom-in'] as const,
  /** 统一时长 */
  duration: '0.72s',
  /** 统一缓动 */
  easing: 'cubic-bezier(0.22, 1, 0.36, 1)',
  /** 推荐延迟间隔（同组元素依次出现） */
  staggerDelay: 70,
} as const

/* ================================================================
 * 8. 模拟终端组件规范（Skill 展示卡片）
 * ================================================================ */
export const TERMINAL = {
  /** 终端背景色 */
  bg: '#1a1a2e',
  /** 标题栏红绿灯 */
  dots: {
    close: 'bg-red-400/80',
    minimize: 'bg-yellow-400/80',
    maximize: 'bg-green-400/80',
  },
  /** 文字颜色 */
  text: {
    command: 'text-green-400',
    output: 'text-gray-300',
    prompt: 'text-gray-500',
    highlight: 'text-yellow-400',
  },
} as const

/* ================================================================
 * 9. 响应式断点约定
 * ================================================================ */
export const BREAKPOINTS = {
  /** Tailwind 默认断点，此处仅作参考 */
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
  /** 网格列数约定 */
  gridCols: {
    categories: 'grid-cols-2 sm:grid-cols-3 lg:grid-cols-6',
    plugins: 'grid-cols-2 sm:grid-cols-4',
    skillCards: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    features: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4',
  },
} as const

/* ================================================================
 * 10. Header 规范
 * ================================================================ */
export const HEADER = {
  height: 'h-16',
  logo: {
    emoji: 'text-4xl',
    title: 'font-black text-2xl',
    subtitle: 'text-xs',
    titleColor: '#EB4C4C',
  },
} as const

/* ================================================================
 * 11. Section 背景约定
 * ================================================================ */
export const SECTION_BG = {
  /** 默认白底 */
  white: 'bg-white',
  /** 浅灰交替 */
  gray: { backgroundColor: '#fafafa' },
  /** 暖色交替 */
  warm: { backgroundColor: 'rgba(255,237,199,0.38)' },
  /** 品牌色全屏（CTA） */
  brand: { backgroundColor: '#EB4C4C' },
  /** Hero 渐变 */
  heroGradient: { background: 'linear-gradient(160deg, #FFF5F5 0%, #FFEDC7 40%, #FFF 100%)' },
} as const
