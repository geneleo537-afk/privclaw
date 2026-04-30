'use client'

import Link from 'next/link'
import { Header } from '@/components/layout/header'
import { Footer } from '@/components/layout/footer'
import {
  BrainCircuit, Target, Rocket, Headphones, ArrowRight,
  Mail, Calendar,
  FileText, Terminal, GitBranch,
  ShoppingCart, GraduationCap, Landmark, Factory,
} from 'lucide-react'
import { Button } from '@/components/ui/button'

/* ── PrivClaw 核心能力 ────────────────────────────────── */
const CORE_CAPABILITIES = [
  {
    icon: <BrainCircuit className="h-6 w-6" />,
    title: '需求深度理解',
    desc: '1 对 1 专属顾问深入了解您的业务场景、痛点和目标，确保 AI 员工方案精准匹配实际需求。',
  },
  {
    icon: <Target className="h-6 w-6" />,
    title: '定制化交付',
    desc: '基于 OpenClaw 能力模块生态，为您组装专属 AI 员工工作流，而非千篇一律的通用方案。',
  },
  {
    icon: <Rocket className="h-6 w-6" />,
    title: '持续进化',
    desc: 'AI 员工上线后每月迭代升级，根据业务变化和使用反馈不断优化，越用越聪明。',
  },
  {
    icon: <Headphones className="h-6 w-6" />,
    title: '快速响应',
    desc: '专属技术团队对接，问题最快 2 小时响应，确保 AI 员工稳定高效运行。',
  },
]

/* ── 技术能力示例（ClawHub 真实热门数据）──────── */
const TECH_DEMOS = [
  {
    name: 'gog',
    slug: 'gog',
    icon: <Mail className="h-7 w-7" />,
    category: 'Google 全能',
    desc: 'Google Workspace 全能工具，覆盖 Gmail、日历、云端硬盘，一句话管理你的整个 Google 生态。',
    command: '帮我查看 Gmail 里今天的重要邮件，未读标记红色星标',
    output: '已扫描收件箱，找到 12 封未读邮件，已标记 5 封重要邮件为红色星标。',
    color: '#4285F4',
    tag: '办公协同',
  },
  {
    name: 'summarize',
    slug: 'summarize',
    icon: <FileText className="h-7 w-7" />,
    category: '内容摘要',
    desc: '多格式内容摘要引擎，支持网页、PDF、YouTube 视频，快速提炼核心观点。',
    command: '总结这个 YouTube 视频的核心观点 https://youtu.be/xxx',
    output: '已获取字幕，主要观点：1. AI Agent 架构趋势 2. 多模态融合 3. 工具调用标准化',
    color: '#10B981',
    tag: '内容处理',
  },
  {
    name: 'notion',
    slug: 'notion',
    icon: <GitBranch className="h-7 w-7" />,
    category: '知识管理',
    desc: 'Notion 笔记与数据库管理，自然语言增删查改页面、数据库条目，知识库随时在线。',
    command: '在"项目看板"数据库新增一条：Q2 发布计划，优先级高',
    output: '已在「项目看板」新增条目，标题：Q2 发布计划，优先级：🔴 高，状态：待开始。',
    color: '#000000',
    tag: '项目管理',
  },
  {
    name: 'nano-pdf',
    slug: 'nano-pdf',
    icon: <FileText className="h-7 w-7" />,
    category: '文档处理',
    desc: 'PDF 编辑与处理，支持提取文本、合并拆分、添加水印，告别繁琐的 PDF 操作。',
    command: '把合同 A.pdf 和附件 B.pdf 合并，加上公司水印',
    output: '已合并为 合同_完整版.pdf（共 48 页），公司水印已添加到每页右下角。',
    color: '#EF4444',
    tag: '数据处理',
  },
  {
    name: 'ffmpeg-video-editor',
    slug: 'ffmpeg-video-editor',
    icon: <Calendar className="h-7 w-7" />,
    category: '视频剪辑',
    desc: '自然语言生成 FFmpeg 命令，轻松完成视频裁剪、转码、拼接，无需记住复杂参数。',
    command: '把 input.mp4 的前 30 秒剪出来，输出 1080p 的 clip.mp4',
    output: '正在执行 ffmpeg 命令……已生成 clip.mp4（1920×1080，30s，12.3 MB）。',
    color: '#EC4899',
    tag: '多媒体',
  },
  {
    name: 'docker-essentials',
    slug: 'docker-essentials',
    icon: <Terminal className="h-7 w-7" />,
    category: 'DevOps',
    desc: 'Docker 容器管理核心命令，通过对话式交互构建镜像、管理容器、清理资源。',
    command: '列出所有运行中的容器，停掉占用内存最多的那个',
    output: '发现 6 个运行中容器，已停止 redis-cache（占用 1.2 GB），释放内存成功。',
    color: '#2496ED',
    tag: '运维管理',
  },
]

/* ── 行业方向 ─────────────────────────────────────────── */
const INDUSTRIES = [
  {
    title: '电商零售',
    desc: '智能客服、订单处理、营销文案生成，全链路电商运营 AI 化。',
    modules: ['智能客服', '内容生成', '数据报表'],
    icon: <ShoppingCart className="h-6 w-6" />,
  },
  {
    title: '在线教育',
    desc: '课程运营、学员答疑、内容摘要、数据分析，教育机构提效利器。',
    modules: ['智能答疑', '内容摘要', '学情分析'],
    icon: <GraduationCap className="h-6 w-6" />,
  },
  {
    title: '金融服务',
    desc: '合规报告生成、数据清洗、客户服务、风控预警，金融场景全覆盖。',
    modules: ['文档处理', '数据清洗', '合规检查'],
    icon: <Landmark className="h-6 w-6" />,
  },
  {
    title: '智能制造',
    desc: '生产报表自动化、设备数据同步、供应链协调，制造企业数字化转型。',
    modules: ['报表生成', '数据同步', '流程自动化'],
    icon: <Factory className="h-6 w-6" />,
  },
]

export default function AboutPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />

      <main className="flex-1">

        {/* ══ Hero ════════════════════════════════════════════════ */}
        <section className="relative overflow-hidden py-24"
          style={{ background: 'linear-gradient(160deg, #FFF5F5 0%, #FFEDC7 40%, #FFF 100%)' }}>
          <div className="container mx-auto px-4 text-center relative z-10">
            <span className="text-7xl mb-6 block">🦞</span>
            <h1 className="text-4xl sm:text-5xl font-black mb-5 text-gray-900">
              关于 <span style={{ color: '#EB4C4C' }}>PrivClaw</span>
            </h1>
            <p className="text-lg text-gray-500 max-w-3xl mx-auto leading-relaxed">
              PrivClaw（智慧龙虾定制）是一家<strong className="text-gray-800">AI 定制服务平台</strong>，
              基于 <strong className="text-gray-800">OpenClaw 开源技术</strong>开发，
              为企业和个人提供专属 AI 员工方案。我们相信，每个企业都应该拥有自己的 AI 员工——
              全天候工作，成本低 90%，持续进化。
            </p>
            <p className="text-sm text-gray-400 mt-4">
              基于 OpenClaw 开源技术开发 · AI 定制服务
            </p>
          </div>
        </section>

        {/* ══ 核心能力 ════════════════════════════════════════════ */}
        <section className="py-20">
          <div className="container mx-auto px-4">
            <div className="text-center mb-14">
              <p className="text-xl font-bold uppercase tracking-widest mb-2" style={{ color: '#EB4C4C' }}>
                核心能力
              </p>
              <h2 className="text-3xl sm:text-4xl font-black text-gray-900">
                不只是工具，是你的 AI 合作伙伴
              </h2>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 max-w-5xl mx-auto">
              {CORE_CAPABILITIES.map((f) => (
                <div key={f.title}
                  className="group p-7 rounded-2xl border border-gray-100 bg-white hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
                  <div className="w-12 h-12 rounded-xl flex items-center justify-center mb-5 transition-colors"
                    style={{ backgroundColor: 'rgba(235,76,76,0.08)', color: '#EB4C4C' }}>
                    {f.icon}
                  </div>
                  <h3 className="text-lg font-black text-gray-900 mb-2">{f.title}</h3>
                  <p className="text-sm text-gray-500 leading-relaxed">{f.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ══ 技术能力示例 ════════════════════════════════════ */}
        <section className="py-20 bg-white">
          <div className="container mx-auto px-4">
            <div className="text-center mb-14">
              <p className="text-xl font-bold uppercase tracking-widest mb-2" style={{ color: '#EB4C4C' }}>
                技术能力示例
              </p>
              <h2 className="text-3xl sm:text-4xl font-black text-gray-900">
                看看 AI 员工能做什么
              </h2>
              <p className="text-gray-500 mt-3 text-base max-w-lg mx-auto">
                基于 OpenClaw 能力模块，每项技能都是即装即用的专业能力
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
              {TECH_DEMOS.map((p) => (
                <div key={p.slug}
                  className="group flex flex-col rounded-2xl border border-gray-100 bg-white overflow-hidden hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
                  {/* 头部 */}
                  <div className="flex items-center gap-4 p-6 pb-4">
                    <div className="w-14 h-14 rounded-2xl flex items-center justify-center shrink-0"
                      style={{ backgroundColor: `${p.color}12`, color: p.color }}>
                      {p.icon}
                    </div>
                    <div className="min-w-0">
                      <h3 className="text-base font-black text-gray-900 truncate">{p.name}</h3>
                      <div className="flex items-center gap-2 mt-0.5">
                        <span className="text-xs font-semibold px-2 py-0.5 rounded-full"
                          style={{ backgroundColor: `${p.color}12`, color: p.color }}>
                          {p.category}
                        </span>
                        <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-500">
                          {p.tag}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* 描述 */}
                  <div className="px-6 pb-4">
                    <p className="text-sm text-gray-500 leading-relaxed">{p.desc}</p>
                  </div>

                  {/* 模拟终端 */}
                  <div className="mx-6 mb-6 rounded-xl overflow-hidden border border-gray-100"
                    style={{ backgroundColor: '#1a1a2e' }}>
                    <div className="flex items-center gap-1.5 px-4 py-2.5 border-b border-white/5">
                      <div className="w-2.5 h-2.5 rounded-full bg-red-400/80" />
                      <div className="w-2.5 h-2.5 rounded-full bg-yellow-400/80" />
                      <div className="w-2.5 h-2.5 rounded-full bg-green-400/80" />
                      <span className="text-[10px] text-gray-500 ml-2 font-mono">privclaw</span>
                    </div>
                    <div className="p-4 font-mono text-xs leading-relaxed">
                      <p className="text-green-400">
                        <span className="text-gray-500">$</span> {p.command}
                      </p>
                      <p className="text-gray-300 mt-2">
                        <span className="text-yellow-400">→</span> {p.output}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="text-center mt-10">
              <Button asChild style={{ backgroundColor: '#EB4C4C' }}
                className="rounded-full h-12 px-10 text-base font-bold text-white border-0 hover:opacity-90 transition-opacity">
                <Link href="/plugins">
                  查看全部能力 <ArrowRight className="h-4 w-4 ml-1.5" />
                </Link>
              </Button>
            </div>
          </div>
        </section>

        {/* ══ 行业方向 ════════════════════════════════════════════ */}
        <section className="py-20" style={{ backgroundColor: '#fafafa' }}>
          <div className="container mx-auto px-4">
            <div className="text-center mb-14">
              <p className="text-xl font-bold uppercase tracking-widest mb-2" style={{ color: '#EB4C4C' }}>
                行业方向
              </p>
              <h2 className="text-3xl sm:text-4xl font-black text-gray-900">
                覆盖多个行业场景
              </h2>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 max-w-5xl mx-auto">
              {INDUSTRIES.map((ind) => (
                <div key={ind.title}
                  className="p-7 rounded-2xl bg-white border border-gray-100 hover:shadow-lg transition-all duration-300">
                  <div className="w-12 h-12 rounded-xl flex items-center justify-center mb-5"
                    style={{ backgroundColor: 'rgba(235,76,76,0.08)', color: '#EB4C4C' }}>
                    {ind.icon}
                  </div>
                  <h3 className="text-lg font-black text-gray-900 mb-2">{ind.title}</h3>
                  <p className="text-sm text-gray-500 leading-relaxed mb-4">{ind.desc}</p>
                  <div className="flex flex-wrap gap-1.5">
                    {ind.modules.map((m) => (
                      <span key={m} className="text-xs px-2.5 py-1 rounded-full bg-gray-50 text-gray-500 font-medium">
                        {m}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ══ 联系我们 ════════════════════════════════════════════ */}
        <section className="py-16 bg-white">
          <div className="container mx-auto px-4 text-center">
            <h2 className="text-2xl font-bold mb-4">联系我们</h2>
            <p className="text-gray-500 mb-8">
              有任何问题、建议或合作意向，欢迎与我们联系
            </p>
            <div className="flex flex-wrap justify-center gap-6">
              {[
                { label: '商务合作', value: 'business@lobstermart.com', href: 'mailto:business@lobstermart.com' },
                { label: '技术支持', value: 'support@lobstermart.com', href: 'mailto:support@lobstermart.com' },
                { label: '问题举报', value: 'report@lobstermart.com', href: 'mailto:report@lobstermart.com' },
              ].map((contact) => (
                <a key={contact.label} href={contact.href}
                  className="flex flex-col items-center gap-1 p-5 rounded-xl border border-gray-100 bg-white hover:shadow-md hover:border-[#EB4C4C]/30 transition-all">
                  <span className="text-sm font-semibold text-gray-500">{contact.label}</span>
                  <span className="text-sm" style={{ color: '#EB4C4C' }}>{contact.value}</span>
                </a>
              ))}
            </div>
          </div>
        </section>

      </main>

      <Footer />
    </div>
  )
}
