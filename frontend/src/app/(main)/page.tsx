'use client'

import { useEffect } from 'react'
import Link from 'next/link'
import {
  ArrowRight, Shield, Zap, Wallet,
  ChevronRight, GitBranch, Mail,
  FileText, Users, Clock, TrendingUp, HeartPulse,
  BrainCircuit, Headphones, Scale, Layers,
  CheckCircle2, XCircle,
  Headset, PenTool, BarChart3, Cog,
  MessageSquare, CalendarCheck, FileCheck, Rocket,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { PluginGrid } from '@/components/plugin/plugin-grid'
import { usePlugins } from '@/hooks/use-plugins'
import type { PluginCardProps } from '@/components/plugin/plugin-card'

/* ── 分类数据 ─────────────────────────────────────────── */
const CATEGORIES = [
  { name: '生产力',   slug: 'productivity', icon: '⚡', desc: '任务管理 · 流程提效' },
  { name: '开发工具', slug: 'devtools',      icon: '🛠️', desc: '代码审查 · 调试辅助' },
  { name: 'AI 增强',  slug: 'ai',            icon: '🤖', desc: '提示词 · 上下文增强' },
  { name: '数据分析', slug: 'data',          icon: '📊', desc: '报表 · 可视化' },
  { name: '内容创作', slug: 'content',       icon: '✍️', desc: '写作 · 生成 · 编辑' },
  { name: '自动化',   slug: 'automation',    icon: '🔄', desc: '工作流 · 定时任务' },
]

/* ── 服务方案 ─────────────────────────────────────────── */
const SOLUTIONS = [
  {
    icon: <Headset className="h-7 w-7" />,
    title: '智能客服方案',
    emoji: '🎧',
    points: ['7x24 自动应答', '工单智能分流', '满意度自动提升', '多渠道接入'],
  },
  {
    icon: <PenTool className="h-7 w-7" />,
    title: '内容运营方案',
    emoji: '📝',
    points: ['营销文案生成', '社媒排期发布', '数据分析报告', '多平台同步'],
  },
  {
    icon: <BarChart3 className="h-7 w-7" />,
    title: '数据处理方案',
    emoji: '📊',
    points: ['报表自动生成', '数据清洗转换', '跨系统同步', '异常预警监控'],
  },
  {
    icon: <Cog className="h-7 w-7" />,
    title: '办公自动化方案',
    emoji: '⚡',
    points: ['邮件智能管理', '日程协调安排', '文档批量处理', '审批流程自动化'],
  },
]

/* ── 合作流程 ─────────────────────────────────────────── */
const PROCESS_STEPS = [
  {
    step: '01',
    title: '需求沟通',
    desc: '免费咨询，深入了解您的业务场景和痛点，明确 AI 员工能为您解决的具体问题。',
    detail: '1 对 1 专属顾问，免费无套路',
    icon: <MessageSquare className="h-6 w-6" />,
  },
  {
    step: '02',
    title: '方案设计',
    desc: '定制 AI 员工方案，明确功能模块、工作流程和预期效果，给出详细报价。',
    detail: '量化目标，效果可预期',
    icon: <CalendarCheck className="h-6 w-6" />,
  },
  {
    step: '03',
    title: '开发部署',
    desc: '技术团队搭建专属工作流，配置能力模块，进行全面测试后交付上线。',
    detail: '快速交付，最快 3 天上线',
    icon: <FileCheck className="h-6 w-6" />,
  },
  {
    step: '04',
    title: '持续优化',
    desc: '上线后持续监控 AI 员工表现，根据业务变化每月迭代升级，确保效果持续提升。',
    detail: '专属运维，按月迭代',
    icon: <Rocket className="h-6 w-6" />,
  },
]

/* ── 插件实例展示（技术能力演示）──────── */
const PLUGIN_DEMOS = [
  {
    name: 'gog',
    icon: <Mail className="h-7 w-7" />,
    category: 'Google 全能',
    tag: '办公协同',
    desc: 'Google Workspace 全能工具，覆盖 Gmail、日历、云端硬盘，一句话管理你的整个 Google 生态。',
    command: '帮我查看 Gmail 里今天的重要邮件，未读标记红色星标',
    output: '已扫描收件箱，找到 12 封未读邮件，已标记 5 封重要邮件为红色星标。',
    color: '#4285F4',
  },
  {
    name: 'summarize',
    icon: <FileText className="h-7 w-7" />,
    category: '内容摘要',
    tag: '内容处理',
    desc: '多格式内容摘要引擎，支持网页、PDF、YouTube 视频，快速提炼核心观点。',
    command: '总结这个 YouTube 视频的核心观点 https://youtu.be/xxx',
    output: '已获取字幕，主要观点：1. AI Agent 架构趋势 2. 多模态融合 3. 工具调用标准化',
    color: '#10B981',
  },
  {
    name: 'notion',
    icon: <GitBranch className="h-7 w-7" />,
    category: '知识管理',
    tag: '项目管理',
    desc: 'Notion 笔记与数据库管理，自然语言增删查改页面、数据库条目，知识库随时在线。',
    command: '在"项目看板"数据库新增一条：Q2 发布计划，优先级高',
    output: '已在「项目看板」新增条目，标题：Q2 发布计划，优先级：🔴 高，状态：待开始。',
    color: '#000000',
  },
  {
    name: 'nano-pdf',
    icon: <FileText className="h-7 w-7" />,
    category: '文档处理',
    tag: '数据处理',
    desc: 'PDF 编辑与处理，支持提取文本、合并拆分、添加水印，告别繁琐的 PDF 操作。',
    command: '把合同 A.pdf 和附件 B.pdf 合并，加上公司水印',
    output: '已合并为 合同_完整版.pdf（共 48 页），公司水印已添加到每页右下角。',
    color: '#EF4444',
  },
]

/* ── 成功案例（模拟数据） ─────────────────────────────── */
const CASE_STUDIES = [
  {
    company: '某电商公司',
    industry: '电子商务',
    metric: '30 分钟 → 30 秒',
    label: '客服响应时间',
    desc: '部署智能客服 AI 员工后，客服响应时间从平均 30 分钟缩短至 30 秒，客户满意度提升 40%。',
    color: '#4285F4',
  },
  {
    company: '某教育机构',
    industry: '在线教育',
    metric: '节省 8 万/月',
    label: '人力成本降低',
    desc: 'AI 员工承担了 80% 的重复性内容运营工作，每月节省 8 万元人力成本，团队可专注核心教研。',
    color: '#10B981',
  },
  {
    company: '某制造企业',
    industry: '智能制造',
    metric: '3 天 → 10 分钟',
    label: '报表生成效率',
    desc: '原本需要 3 天的月度报表生成流程，AI 员工 10 分钟即可完成，数据准确率从 95% 提升至 99.8%。',
    color: '#EB4C4C',
  },
]

/* ── 培训计划价格表 ─────────────────────────────────────── */
const PRICING_PLANS = [
  {
    name: '入门教学',
    emoji: '🌱',
    price: 999,
    unit: '一次性',
    desc: '从零开始掌握 OpenClaw 部署与安全配置',
    features: [
      { text: 'OpenClaw 系统安装部署教学', included: true },
      { text: '安全防护配置指导', included: true },
      { text: '基础使用培训', included: true },
      { text: '配套教程文档', included: true },
      { text: '学员交流群（30 天）', included: true },
      { text: '个人赚钱指导', included: false },
      { text: '配置问题持续支持', included: false },
    ],
    cta: '立即报名',
    highlighted: false,
  },
  {
    name: '年度社群',
    emoji: '🔥',
    price: 4999,
    unit: '/年',
    desc: '个人赚钱社群 + 全年技术支持与资源对接',
    badge: '最受欢迎',
    features: [
      { text: '入门教学全部内容', included: true },
      { text: '个人变现赚钱指导', included: true },
      { text: '一年内配置问题协助', included: true },
      { text: '安全问题持续支持', included: true },
      { text: '1v1 专属技术顾问', included: true },
      { text: '赚钱社群资源对接', included: true },
      { text: '优先响应服务', included: true },
      { text: '企业工作流定制', included: false },
    ],
    cta: '立即加入',
    highlighted: true,
  },
  {
    name: '终身会员',
    emoji: '👑',
    price: 20000,
    unit: '一次性',
    desc: '终身全部权益 + 赠送一次企业工作流定制规划',
    features: [
      { text: '年度社群全部权益', included: true },
      { text: '终身社群与技术支持', included: true },
      { text: '终身配置与安全支持', included: true },
      { text: '终身系统升级指导', included: true },
      { text: '终身优先技术响应', included: true },
      { text: '1v1 深度咨询不限次', included: true },
      { text: '赠送企业工作流定制规划', included: true },
    ],
    cta: '咨询详情',
    highlighted: false,
  },
]

/* ── 工具函数 ─────────────────────────────────────────── */
function toCardProps(plugin: {
  id: string; name: string; summary: string; iconUrl?: string
  price: number; avgRating: number; downloadCount: number
  developerName: string; slug: string
}): PluginCardProps {
  return {
    id: plugin.id, name: plugin.name, description: plugin.summary,
    coverUrl: plugin.iconUrl, price: plugin.price, avgRating: plugin.avgRating,
    downloadCount: plugin.downloadCount, developerName: plugin.developerName, slug: plugin.slug,
  }
}

/* 导航栏高度（px），用于计算 section 可见区域 */
const HEADER_H = 64

function useScrollAnimation() {
  useEffect(() => {
    const container = document.getElementById('page-snap-container')
    const elements = document.querySelectorAll('[data-animate]')
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const el = entry.target as HTMLElement
            const delay = Number(el.dataset.delay ?? 0)
            setTimeout(() => el.classList.add('in-view'), delay)
            observer.unobserve(el)
          }
        })
      },
      { threshold: 0.08, rootMargin: '-30px', root: container }
    )
    elements.forEach((el) => observer.observe(el))
    return () => observer.disconnect()
  }, [])
}

function useScrollSnap() {
  useEffect(() => {
    /* 隐藏滚动容器的滚动条 */
    const style = document.createElement('style')
    style.textContent = `
      #page-snap-container::-webkit-scrollbar { display: none }
      #page-snap-container { scrollbar-width: none; -ms-overflow-style: none }
    `
    document.head.appendChild(style)
    return () => { document.head.removeChild(style) }
  }, [])
}

/* ── 首页组件 ─────────────────────────────────────────── */
export default function HomePage() {
  useScrollAnimation()
  useScrollSnap()

  const hotQuery   = usePlugins({ page_size: 8, sort_by: 'download_count' })
  const hotPlugins = (hotQuery.data?.items ?? []).map(toCardProps)
  const totalPlugins = hotQuery.data?.total ?? 0

  const sectionSnap: React.CSSProperties = {
    height: `calc(100dvh - ${HEADER_H}px)`,
    scrollSnapAlign: 'start',
    scrollSnapStop: 'always',
    overflow: 'hidden',
  }

  return (
    <div
      id="page-snap-container"
      className="bg-white"
      style={{
        height: `calc(100dvh - ${HEADER_H}px)`,
        overflowY: 'auto',
        scrollSnapType: 'y mandatory',
      }}
    >

      {/* ══ 1. AI 员工 Hero ══════════════════════════════════════ */}
      <section
        style={sectionSnap}
        className="relative flex flex-col justify-center overflow-hidden px-4"
      >
        {/* 品牌色渐变背景 */}
        <div className="pointer-events-none absolute inset-0"
          style={{ background: 'linear-gradient(135deg, #1a0a0a 0%, #4a1010 30%, #EB4C4C 70%, #ff7b5c 100%)' }} />
        <div className="pointer-events-none absolute inset-0">
          <div className="absolute left-1/4 top-1/3 w-[600px] h-[600px] rounded-full opacity-20"
            style={{ background: 'radial-gradient(circle, #ff6b6b 0%, transparent 70%)' }} />
          <div className="absolute right-1/4 bottom-1/4 w-[400px] h-[400px] rounded-full opacity-15"
            style={{ background: 'radial-gradient(circle, #FFEDC7 0%, transparent 70%)' }} />
        </div>

        <div className="container mx-auto max-w-4xl text-center relative z-10">
          <div data-animate="fade-in" data-delay="0"
            className="inline-flex items-center gap-2 text-base font-semibold px-4 py-1.5 rounded-full mb-8"
            style={{ backgroundColor: 'rgba(255,255,255,0.15)', color: '#FFEDC7' }}>
            <BrainCircuit className="h-4 w-4" />
            <span>PrivClaw · AI 定制服务</span>
          </div>

          <h1 data-animate="fade-up" data-delay="120"
            className="text-5xl sm:text-6xl lg:text-[5.5rem] font-black leading-[1.05] tracking-tight mb-6 text-white text-balance"
            style={{ fontFamily: 'var(--font-display), serif' }}>
            你下一个招聘的员工，
            <br />
            <span style={{ color: '#FFEDC7' }}>不需要领薪水。</span>
          </h1>

          <p data-animate="fade-up" data-delay="240"
            className="text-lg sm:text-xl max-w-2xl mx-auto mb-4 leading-relaxed"
            style={{ color: 'rgba(255,255,255,0.85)' }}>
            我们为您打造专属的 AI 员工。全天候工作，成本比人类员工低 90%，每月持续进化。
          </p>

          <p data-animate="fade-up" data-delay="320"
            className="text-base max-w-xl mx-auto mb-10 leading-relaxed"
            style={{ color: 'rgba(255,255,255,0.6)' }}>
            不是聊天机器人，不是模板。是一个定制的数字员工——了解您的业务，使用您的工具，完成实际工作。
          </p>

          <div data-animate="fade-up" data-delay="420" className="flex flex-wrap justify-center gap-4">
            <Button asChild
              className="rounded-full h-14 px-10 text-base font-bold border-0 hover:opacity-90 transition-opacity"
              style={{ backgroundColor: 'white', color: '#EB4C4C' }}>
              <Link href="/contact">免费咨询 <ArrowRight className="h-4 w-4 ml-1.5" /></Link>
            </Button>
            <Button asChild variant="outline"
              className="rounded-full h-14 px-10 text-base font-bold bg-transparent transition-colors"
              style={{ borderColor: 'rgba(255,255,255,0.4)', color: 'white' }}>
              <a href="#solutions">了解服务方案 <ChevronRight className="h-4 w-4 ml-1" /></a>
            </Button>
          </div>
        </div>

        <div className="absolute bottom-10 left-1/2 -translate-x-1/2 animate-bounce opacity-40">
          <div className="w-6 h-10 rounded-full border-2 border-white/40 flex items-start justify-center pt-2">
            <div className="w-1 h-3 rounded-full bg-white/40" />
          </div>
        </div>
      </section>

      {/* ══ 2. 成本对比 ══════════════════════════════════════════ */}
      <section
        style={{ ...sectionSnap, backgroundColor: '#fafafa' }}
        className="flex flex-col justify-center px-4 py-6"
      >
        <div className="container mx-auto max-w-5xl">
          <div className="text-center mb-6">
            <p data-animate="fade-in" data-delay="0"
              className="text-lg font-bold uppercase tracking-widest mb-2" style={{ color: '#EB4C4C' }}>
              成本对比
            </p>
            <h2 data-animate="fade-up" data-delay="80"
              className="text-4xl sm:text-5xl font-black text-gray-900">
              为什么选择 AI 员工？
            </h2>
            <p data-animate="fade-up" data-delay="160"
              className="text-gray-500 mt-2 text-lg max-w-xl mx-auto">
              直观对比，让数据说话
            </p>
          </div>

          <div data-animate="fade-up" data-delay="280"
            className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-4xl mx-auto">
            {/* 人类员工卡片 */}
            <div className="rounded-3xl border-2 border-gray-200 bg-white p-5">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center">
                  <Users className="h-6 w-6 text-gray-500" />
                </div>
                <div>
                  <h3 className="text-xl font-black text-gray-900">人类员工</h3>
                  <p className="text-sm text-gray-400">传统雇佣模式</p>
                </div>
              </div>
              <div className="space-y-1.5">
                {[
                  { icon: <Wallet className="h-4 w-4" />,       label: '年薪成本',   value: '¥15-50 万' },
                  { icon: <Clock className="h-4 w-4" />,        label: '工作时间',   value: '8 小时/天' },
                  { icon: <TrendingUp className="h-4 w-4" />,   label: '上手周期',   value: '1-3 个月' },
                  { icon: <Headphones className="h-4 w-4" />,   label: '凌晨值班',   value: '需加班费' },
                  { icon: <Scale className="h-4 w-4" />,        label: '稳定性',     value: '离职风险' },
                  { icon: <HeartPulse className="h-4 w-4" />,   label: '病假/休假',  value: '带薪假期' },
                  { icon: <Layers className="h-4 w-4" />,       label: '管理成本',   value: '需要主管' },
                  { icon: <Users className="h-4 w-4" />,        label: '扩容速度',   value: '招聘 1-2 月' },
                ].map((item) => (
                  <div key={item.label} className="flex items-center justify-between py-1.5 border-b border-gray-100 last:border-0">
                    <div className="flex items-center gap-2 text-gray-500">
                      {item.icon}
                      <span className="text-sm">{item.label}</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <XCircle className="h-4 w-4 text-gray-300" />
                      <span className="text-sm font-semibold text-gray-600">{item.value}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* AI 员工卡片 */}
            <div className="rounded-3xl border-2 p-5 relative overflow-hidden"
              style={{ borderColor: '#EB4C4C', backgroundColor: '#FFF5F5' }}>
              <div className="absolute top-4 right-4 px-3 py-1 rounded-full text-xs font-bold text-white"
                style={{ backgroundColor: '#EB4C4C' }}>
                推荐
              </div>
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 rounded-full flex items-center justify-center"
                  style={{ backgroundColor: 'rgba(235,76,76,0.15)' }}>
                  <BrainCircuit className="h-6 w-6" style={{ color: '#EB4C4C' }} />
                </div>
                <div>
                  <h3 className="text-xl font-black text-gray-900">AI 员工</h3>
                  <p className="text-sm" style={{ color: '#EB4C4C' }}>PrivClaw 方案</p>
                </div>
              </div>
              <div className="space-y-1.5">
                {[
                  { icon: <Wallet className="h-4 w-4" />,       label: '年薪成本',   value: '低至 ¥1-5 万' },
                  { icon: <Clock className="h-4 w-4" />,        label: '工作时间',   value: '24/7 全天候' },
                  { icon: <TrendingUp className="h-4 w-4" />,   label: '上手周期',   value: '即刻部署' },
                  { icon: <Headphones className="h-4 w-4" />,   label: '凌晨值班',   value: '无需额外费用' },
                  { icon: <Scale className="h-4 w-4" />,        label: '稳定性',     value: '永不离职' },
                  { icon: <HeartPulse className="h-4 w-4" />,   label: '病假/休假',  value: '全年无休' },
                  { icon: <Layers className="h-4 w-4" />,       label: '管理成本',   value: '自助面板' },
                  { icon: <Users className="h-4 w-4" />,        label: '扩容速度',   value: '分钟级扩展' },
                ].map((item) => (
                  <div key={item.label} className="flex items-center justify-between py-1.5 border-b border-red-100 last:border-0">
                    <div className="flex items-center gap-2" style={{ color: '#EB4C4C' }}>
                      {item.icon}
                      <span className="text-sm">{item.label}</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <CheckCircle2 className="h-4 w-4" style={{ color: '#EB4C4C' }} />
                      <span className="text-sm font-semibold text-gray-900">{item.value}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div data-animate="fade-up" data-delay="500" className="text-center mt-5">
            <Button asChild style={{ backgroundColor: '#EB4C4C' }}
              className="rounded-full h-12 px-10 text-base font-bold text-white border-0 hover:opacity-90 transition-opacity">
              <Link href="/contact">免费咨询 <ArrowRight className="h-4 w-4 ml-1.5" /></Link>
            </Button>
          </div>
        </div>
      </section>

      {/* ══ 3. 服务方案概览 ════════════════════════════════════════ */}
      <section id="solutions" style={sectionSnap}
        className="flex flex-col justify-center px-4 py-6 bg-white">
        <div className="container mx-auto max-w-7xl">
          <div className="text-center mb-6">
            <p data-animate="fade-in" data-delay="0"
              className="text-lg font-bold uppercase tracking-widest mb-2" style={{ color: '#EB4C4C' }}>
              服务方案
            </p>
            <h2 data-animate="fade-up" data-delay="80"
              className="text-4xl sm:text-5xl font-black text-gray-900">
              为不同业务场景，定制 AI 解决方案
            </h2>
            <p data-animate="fade-up" data-delay="160"
              className="text-gray-500 mt-2 text-lg max-w-2xl mx-auto">
              无论您是需要智能客服、内容运营还是数据处理，我们都有成熟方案
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 max-w-6xl mx-auto mb-6">
            {SOLUTIONS.map((sol, i) => (
              <div key={sol.title}
                data-animate="fade-up" data-delay={String(200 + i * 100)}
                className="group relative flex flex-col p-5 rounded-3xl border border-gray-100 bg-gray-50 hover:shadow-xl transition-all duration-300 hover:-translate-y-1"
                onMouseEnter={e => (e.currentTarget.style.borderColor = '#FFA6A6')}
                onMouseLeave={e => (e.currentTarget.style.borderColor = '')}>
                <span className="text-3xl mb-3">{sol.emoji}</span>
                <h3 className="text-lg font-black text-gray-900 mb-3">{sol.title}</h3>
                <ul className="space-y-2 flex-1">
                  {sol.points.map((point) => (
                    <li key={point} className="flex items-center gap-2 text-sm text-gray-500">
                      <CheckCircle2 className="h-4 w-4 shrink-0" style={{ color: '#EB4C4C' }} />
                      {point}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          <div data-animate="fade-up" data-delay="680" className="text-center">
            <Button asChild style={{ backgroundColor: '#EB4C4C' }}
              className="rounded-full h-12 px-10 text-base font-bold text-white border-0 hover:opacity-90 transition-opacity">
              <Link href="/contact">预约方案演示 <ArrowRight className="h-4 w-4 ml-1.5" /></Link>
            </Button>
          </div>
        </div>
      </section>

      {/* ══ 4. 合作流程 ════════════════════════════════════════════ */}
      <section id="process" style={{ ...sectionSnap, backgroundColor: '#fafafa' }}
        className="flex flex-col justify-center px-4 py-6">
        <div className="container mx-auto max-w-7xl">
          <div className="text-center mb-6">
            <p data-animate="fade-in" data-delay="0"
              className="text-lg font-bold uppercase tracking-widest mb-2" style={{ color: '#EB4C4C' }}>
              合作流程
            </p>
            <h2 data-animate="fade-up" data-delay="100"
              className="text-4xl sm:text-5xl font-black text-gray-900">
              从咨询到上线，全程透明
            </h2>
            <p data-animate="fade-up" data-delay="180" className="text-gray-500 mt-2 text-lg max-w-lg mx-auto">
              四步开启 AI 员工之旅，全程有专人对接
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 max-w-6xl mx-auto mb-5">
            {PROCESS_STEPS.map((item, i) => (
              <div key={item.step}
                data-animate="fade-up" data-delay={String(250 + i * 130)}
                className="relative flex flex-col p-5 rounded-3xl border border-gray-100 bg-white hover:shadow-lg transition-all duration-300"
                onMouseEnter={e => (e.currentTarget.style.borderColor = '#FFA6A6')}
                onMouseLeave={e => (e.currentTarget.style.borderColor = '')}>
                <span className="font-black leading-none mb-2 select-none"
                  style={{ fontSize: '3rem', color: '#FFA6A6', lineHeight: 1 }}>
                  {item.step}
                </span>
                <h3 className="text-lg font-black text-gray-900 mb-1">{item.title}</h3>
                <p className="text-sm text-gray-500 leading-relaxed mb-3">{item.desc}</p>
                <p className="text-sm font-medium px-4 py-2 rounded-full inline-self-start"
                  style={{ backgroundColor: 'rgba(255,166,166,0.2)', color: '#EB4C4C' }}>
                  {item.detail}
                </p>
                {i < 3 && (
                  <div className="hidden md:flex absolute -right-3 top-1/2 -translate-y-1/2 z-10">
                    <ArrowRight className="h-6 w-6" style={{ color: '#FFA6A6' }} />
                  </div>
                )}
              </div>
            ))}
          </div>

          <div data-animate="fade-up" data-delay="780" className="text-center">
            <Button asChild style={{ backgroundColor: '#EB4C4C' }}
              className="rounded-full h-12 px-10 text-base font-bold text-white border-0 hover:opacity-90 transition-opacity">
              <Link href="/contact">免费咨询 <ArrowRight className="h-4 w-4 ml-1.5" /></Link>
            </Button>
          </div>
        </div>
      </section>

      {/* ══ 5. 技术能力展示 ═════════════════════════════════════ */}
      <section style={{ ...sectionSnap, backgroundColor: 'white' }}
        className="flex flex-col justify-center px-4 py-6">
        <div className="container mx-auto max-w-7xl">
          <div className="text-center mb-5">
            <p data-animate="fade-in" data-delay="0"
              className="text-lg font-bold uppercase tracking-widest mb-2" style={{ color: '#EB4C4C' }}>
              技术能力
            </p>
            <h2 data-animate="fade-up" data-delay="80"
              className="text-4xl sm:text-5xl font-black text-gray-900">
              看看 AI 员工都能做什么
            </h2>
            <p data-animate="fade-up" data-delay="160"
              className="text-gray-500 mt-2 text-lg max-w-2xl mx-auto">
              基于 OpenClaw 能力模块生态，为 AI 员工装配各种专业技能
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-5xl mx-auto" data-animate="fade-up" data-delay="280">
            {PLUGIN_DEMOS.map((p) => (
              <div key={p.name}
                className="group flex flex-col rounded-2xl border border-gray-100 bg-white overflow-hidden hover:shadow-lg transition-all duration-300 hover:-translate-y-1">
                {/* 头部 + 描述 */}
                <div className="flex items-start gap-3 p-4 pb-2">
                  <div className="w-11 h-11 rounded-xl flex items-center justify-center shrink-0 mt-0.5"
                    style={{ backgroundColor: `${p.color}12`, color: p.color }}>
                    {p.icon}
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="text-base font-black text-gray-900">{p.name}</h3>
                      <span className="text-xs font-semibold px-2 py-0.5 rounded-full shrink-0"
                        style={{ backgroundColor: `${p.color}12`, color: p.color }}>
                        {p.category}
                      </span>
                      <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-500 shrink-0">
                        {p.tag}
                      </span>
                    </div>
                    <p className="text-sm text-gray-500 leading-snug">{p.desc}</p>
                  </div>
                </div>

                {/* 模拟终端 */}
                <div className="mx-4 mb-4 rounded-lg overflow-hidden"
                  style={{ backgroundColor: '#1a1a2e' }}>
                  <div className="flex items-center gap-1.5 px-3 py-1.5 border-b border-white/5">
                    <div className="w-2 h-2 rounded-full bg-red-400/80" />
                    <div className="w-2 h-2 rounded-full bg-yellow-400/80" />
                    <div className="w-2 h-2 rounded-full bg-green-400/80" />
                    <span className="text-[10px] text-gray-500 ml-1.5 font-mono">privclaw</span>
                  </div>
                  <div className="px-3 py-2.5 font-mono text-xs leading-snug">
                    <p className="text-green-400"><span className="text-gray-500">$</span> {p.command}</p>
                    <p className="text-gray-300 mt-1"><span className="text-yellow-400">→</span> {p.output}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div data-animate="fade-up" data-delay="500" className="text-center mt-5">
            <Button asChild style={{ backgroundColor: '#EB4C4C' }}
              className="rounded-full h-12 px-10 text-base font-bold text-white border-0 hover:opacity-90 transition-opacity">
              <Link href="/plugins">
                查看全部能力 <ArrowRight className="h-4 w-4 ml-1.5" />
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* ══ 6. 成功案例 ═══════════════════════════════════════════ */}
      <section style={{ ...sectionSnap, backgroundColor: '#fafafa' }}
        className="flex flex-col justify-center px-4 py-6">
        <div className="container mx-auto max-w-7xl">
          <div className="text-center mb-6">
            <p data-animate="fade-in" data-delay="0"
              className="text-lg font-bold uppercase tracking-widest mb-2" style={{ color: '#EB4C4C' }}>
              客户案例
            </p>
            <h2 data-animate="fade-up" data-delay="80"
              className="text-4xl sm:text-5xl font-black text-gray-900">
              已有客户从中受益
            </h2>
            <p data-animate="fade-up" data-delay="160"
              className="text-gray-500 mt-2 text-lg max-w-xl mx-auto">
              真实数据，看得见的降本增效
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-5xl mx-auto mb-6"
            data-animate="fade-up" data-delay="280">
            {CASE_STUDIES.map((cs) => (
              <div key={cs.company}
                className="flex flex-col p-5 rounded-3xl bg-white border border-gray-100 hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
                <div className="flex items-center gap-2 mb-4">
                  <span className="text-xs font-semibold px-3 py-1 rounded-full"
                    style={{ backgroundColor: `${cs.color}12`, color: cs.color }}>
                    {cs.industry}
                  </span>
                </div>
                <p className="text-sm text-gray-400 mb-2">{cs.company}</p>
                <p className="text-3xl font-black text-gray-900 mb-1">{cs.metric}</p>
                <p className="text-sm font-semibold mb-4" style={{ color: cs.color }}>{cs.label}</p>
                <p className="text-sm text-gray-500 leading-relaxed">{cs.desc}</p>
              </div>
            ))}
          </div>

          {/* 统计条 */}
          <div data-animate="fade-up" data-delay="500"
            className="flex flex-wrap justify-center items-center gap-8 pt-4 border-t border-gray-200 max-w-3xl mx-auto">
            {[
              { num: '50+', label: '服务客户' },
              { num: '100 万+', label: '任务处理' },
              { num: '98%', label: '客户满意度' },
            ].map((stat, i) => (
              <div key={stat.label} className="flex items-center gap-8">
                <div className="text-center">
                  <p className="text-4xl font-black" style={{ color: '#EB4C4C' }}>{stat.num}</p>
                  <p className="text-sm text-gray-400 mt-1">{stat.label}</p>
                </div>
                {i < 2 && <div className="hidden sm:block w-px h-12 bg-gray-200" />}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ══ 7. 培训计划 ═══════════════════════════════════════════ */}
      <section id="pricing" style={sectionSnap}
        className="flex flex-col justify-center px-4 py-6 bg-white">
        <div className="container mx-auto max-w-5xl">
          <div className="text-center mb-6">
            <p data-animate="fade-in" data-delay="0"
              className="text-lg font-bold uppercase tracking-widest mb-2" style={{ color: '#EB4C4C' }}>
              培训计划
            </p>
            <h2 data-animate="fade-up" data-delay="80"
              className="text-4xl sm:text-5xl font-black text-gray-900">
              选择适合您的服务方案
            </h2>
            <p data-animate="fade-up" data-delay="160"
              className="text-gray-500 mt-2 text-lg max-w-xl mx-auto">
              从入门到终身，灵活匹配您的业务阶段
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-5xl mx-auto">
            {PRICING_PLANS.map((plan, i) => (
              <div key={plan.name}
                data-animate="fade-up" data-delay={String(200 + i * 120)}
                className={`relative flex flex-col rounded-2xl p-5 transition-all duration-300 ${
                  plan.highlighted
                    ? 'border-2 md:-translate-y-2 shadow-lg'
                    : 'border border-gray-100 bg-gray-50 hover:shadow-xl hover:-translate-y-1'
                }`}
                style={plan.highlighted
                  ? { borderColor: '#EB4C4C', backgroundColor: '#FFF5F5' }
                  : undefined
                }
                onMouseEnter={e => { if (!plan.highlighted) e.currentTarget.style.borderColor = '#FFA6A6' }}
                onMouseLeave={e => { if (!plan.highlighted) e.currentTarget.style.borderColor = '' }}>

                {/* 角标 */}
                {'badge' in plan && plan.badge && (
                  <div className="absolute -top-3 right-6 px-4 py-1 rounded-full text-xs font-bold text-white"
                    style={{ backgroundColor: '#EB4C4C' }}>
                    {plan.badge}
                  </div>
                )}

                {/* 头部 */}
                <div className="flex items-center gap-3 mb-2">
                  <span className="text-2xl">{plan.emoji}</span>
                  <h3 className="text-lg font-black text-gray-900">{plan.name}</h3>
                </div>
                <p className="text-sm text-gray-500 mb-3">{plan.desc}</p>

                {/* 价格 */}
                <div className="flex items-end gap-1 mb-4">
                  <span className="text-base font-bold text-gray-400">¥</span>
                  <span className="text-4xl font-black leading-none" style={{ color: plan.highlighted ? '#EB4C4C' : '#1a1a1a' }}>
                    {plan.price.toLocaleString()}
                  </span>
                  <span className="text-sm text-gray-400 mb-0.5 ml-1">{plan.unit}</span>
                </div>

                {/* Features 列表 */}
                <ul className="space-y-1.5 flex-1 mb-4">
                  {plan.features.map((f) => (
                    <li key={f.text} className="flex items-center gap-2 text-sm">
                      {f.included
                        ? <CheckCircle2 className="h-3.5 w-3.5 shrink-0" style={{ color: '#EB4C4C' }} />
                        : <XCircle className="h-3.5 w-3.5 shrink-0 text-gray-300" />
                      }
                      <span className={f.included ? 'text-gray-700' : 'text-gray-400 line-through'}>{f.text}</span>
                    </li>
                  ))}
                </ul>

                {/* CTA 按钮 */}
                <Button asChild
                  className={`rounded-full h-10 text-sm font-bold transition-opacity hover:opacity-90 ${
                    plan.highlighted ? 'border-0 text-white' : 'bg-transparent'
                  }`}
                  style={plan.highlighted
                    ? { backgroundColor: '#EB4C4C' }
                    : { borderColor: '#EB4C4C', color: '#EB4C4C', borderWidth: '2px' }
                  }
                  variant={plan.highlighted ? 'default' : 'outline'}>
                  <Link href="/contact">{plan.cta} <ArrowRight className="h-4 w-4 ml-1.5" /></Link>
                </Button>
              </div>
            ))}
          </div>

          {/* 底部信任提示 */}
          <div data-animate="fade-up" data-delay="600"
            className="flex flex-wrap justify-center gap-6 mt-5 text-sm text-gray-400">
            {['支持开具发票', '企业对公转账', '7 天无理由退款'].map((tip) => (
              <div key={tip} className="flex items-center gap-1.5">
                <CheckCircle2 className="h-4 w-4" style={{ color: '#EB4C4C' }} />
                <span>{tip}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ══ 8. 能力生态（紧凑版） ════════════════════════════════ */}
      <section style={{ ...sectionSnap, backgroundColor: 'rgba(255,237,199,0.38)' }}
        className="flex flex-col justify-center px-4 py-6">
        <div className="container mx-auto max-w-7xl">
          <div className="text-center mb-5">
            <p data-animate="fade-in" data-delay="0"
              className="text-lg font-bold uppercase tracking-widest mb-2" style={{ color: '#EB4C4C' }}>
              能力生态
            </p>
            <h2 data-animate="fade-up" data-delay="80"
              className="text-4xl sm:text-5xl font-black text-gray-900">
              数百个经过验证的能力模块
            </h2>
            <p data-animate="fade-up" data-delay="160"
              className="text-gray-500 mt-2 text-lg max-w-2xl mx-auto">
              基于 OpenClaw 开源协议，覆盖六大业务场景
            </p>
          </div>

          {/* 分类网格 — 紧凑卡片 */}
          <div className="grid grid-cols-3 sm:grid-cols-6 gap-3 mb-5">
            {CATEGORIES.map((cat, i) => (
              <div key={cat.slug} data-animate="scale-in" data-delay={String(i * 50)}>
                <Link href={`/plugins?category=${cat.slug}`}
                  className="group flex flex-col items-center gap-2 p-4 rounded-2xl bg-white border-2 border-transparent transition-all duration-300 hover:shadow-lg cursor-pointer"
                  onMouseEnter={e => {
                    e.currentTarget.style.borderColor = '#EB4C4C'
                    e.currentTarget.style.transform = 'translateY(-4px)'
                  }}
                  onMouseLeave={e => {
                    e.currentTarget.style.borderColor = 'transparent'
                    e.currentTarget.style.transform = ''
                  }}>
                  <span className="text-4xl transition-transform duration-300 group-hover:scale-110">{cat.icon}</span>
                  <p className="text-sm font-black text-gray-800 group-hover:text-[#EB4C4C] transition-colors">{cat.name}</p>
                </Link>
              </div>
            ))}
          </div>

          {/* 热门能力模块 */}
          <div data-animate="scale-in" data-delay="400">
            {hotQuery.isLoading ? (
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                {Array.from({ length: 4 }).map((_, i) => (
                  <div key={i} className="h-56 rounded-2xl bg-gray-100 animate-pulse" />
                ))}
              </div>
            ) : hotPlugins.length > 0 ? (
              <PluginGrid plugins={hotPlugins.slice(0, 4)} cols={4} />
            ) : (
              <div className="flex flex-col items-center justify-center py-6 gap-3">
                <span className="text-5xl">🦞</span>
                <p className="text-gray-400 text-lg font-medium">能力模块即将上线，敬请期待</p>
              </div>
            )}
          </div>

          {/* 统计 + CTA 行 */}
          <div data-animate="fade-up" data-delay="550"
            className="flex flex-wrap items-center justify-center gap-8 mt-5 pt-4 border-t border-[#FFA6A6]/30">
            {[
              { num: `${totalPlugins || '0'}+`, label: '可用能力模块' },
              { num: '6', label: '覆盖场景' },
              { num: '50+', label: '服务客户' },
            ].map((stat, i) => (
              <div key={stat.label} className="flex items-center gap-8">
                <div className="text-center">
                  <p className="text-3xl font-black text-gray-900">{stat.num}</p>
                  <p className="text-xs text-gray-400 mt-0.5">{stat.label}</p>
                </div>
                {i < 2 && <div className="hidden sm:block w-px h-10 bg-[#FFA6A6]/30" />}
              </div>
            ))}
            <Button asChild style={{ backgroundColor: '#EB4C4C' }}
              className="rounded-full h-10 px-8 text-sm font-bold text-white border-0 hover:opacity-90 transition-opacity">
              <Link href="/plugins?sort=download_count">
                浏览能力库 <ArrowRight className="h-3.5 w-3.5 ml-1" />
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* ══ 9. 生态合作 + 咨询 CTA（合并） ═══════════════════════ */}
      <section style={{ ...sectionSnap, backgroundColor: '#EB4C4C' }}
        className="flex flex-col justify-center px-4 py-6 relative overflow-hidden">
        <div className="pointer-events-none absolute inset-0">
          <div className="absolute -top-40 -right-40 w-[500px] h-[500px] rounded-full opacity-20"
            style={{ backgroundColor: '#FF7070' }} />
          <div className="absolute -bottom-48 -left-24 w-[600px] h-[600px] rounded-full opacity-15"
            style={{ backgroundColor: '#FFA6A6' }} />
          <div className="absolute top-1/4 left-1/4 w-32 h-32 rounded-full opacity-10 bg-white" />
        </div>

        <div className="container mx-auto text-center relative z-10 max-w-3xl">
          <p data-animate="fade-in" data-delay="0"
            className="text-2xl font-bold uppercase tracking-widest mb-4" style={{ color: '#FFA6A6' }}>
            生态合作
          </p>
          <h2 data-animate="zoom-in" data-delay="100"
            className="text-4xl sm:text-6xl font-black text-white mb-6 text-balance"
            style={{ fontFamily: 'var(--font-display), serif' }}>
            成为 PrivClaw 生态合作伙伴
          </h2>
          <p data-animate="fade-up" data-delay="200"
            className="text-lg mb-8 max-w-lg mx-auto leading-relaxed" style={{ color: '#FFA6A6' }}>
            发布你的能力模块，与我们共建 AI 服务生态，共享商业价值
          </p>

          {/* 三个优势 */}
          <div data-animate="fade-up" data-delay="300"
            className="grid grid-cols-1 sm:grid-cols-3 gap-4 max-w-3xl mx-auto mb-8">
            {[
              { icon: <Wallet className="h-6 w-6" />,  title: '70% 收益分成', desc: '平台仅收取 30%，公平透明' },
              { icon: <Shield className="h-6 w-6" />,  title: '安全审核机制', desc: '严格审查，保护开发者权益' },
              { icon: <Zap className="h-6 w-6" />,     title: '企业级支持',   desc: '专属技术对接，快速响应需求' },
            ].map((b) => (
              <div key={b.title} className="flex flex-col items-center gap-3 rounded-2xl px-5 py-6"
                style={{ backgroundColor: 'rgba(255,255,255,0.12)' }}>
                <div style={{ color: '#FFA6A6' }}>{b.icon}</div>
                <p className="text-white font-black text-base">{b.title}</p>
                <p className="text-sm" style={{ color: '#FFA6A6' }}>{b.desc}</p>
              </div>
            ))}
          </div>

          <div data-animate="fade-up" data-delay="420"
            className="flex flex-wrap justify-center gap-4">
            <Button asChild className="rounded-full h-14 px-10 text-base font-bold border-0 hover:opacity-90 transition-opacity"
              style={{ backgroundColor: 'white', color: '#EB4C4C' }}>
              <Link href="/dashboard/plugins/new">
                发布能力模块 <ArrowRight className="h-4 w-4 ml-1.5" />
              </Link>
            </Button>
            <Button asChild variant="outline"
              className="rounded-full h-14 px-10 text-base font-bold bg-transparent transition-colors"
              style={{ borderColor: 'rgba(255,255,255,0.4)', color: 'white' }}>
              <Link href="/contact">商务合作</Link>
            </Button>
          </div>
        </div>
      </section>

    </div>
  )
}
