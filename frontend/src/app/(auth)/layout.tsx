import Link from 'next/link'

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex">

      {/* ── 左侧品牌面板（桌面端） ─────────────────────────────── */}
      <div
        className="hidden lg:flex lg:w-5/12 flex-col justify-between p-14 relative overflow-hidden"
        style={{ backgroundColor: '#EB4C4C' }}
      >
        {/* 装饰圆形 */}
        <div className="pointer-events-none absolute inset-0">
          <div className="absolute -top-24 -right-24 w-80 h-80 rounded-full opacity-20"
            style={{ backgroundColor: '#FF7070' }} />
          <div className="absolute bottom-0 -left-20 w-96 h-96 rounded-full opacity-15"
            style={{ backgroundColor: '#FFA6A6' }} />
          {/* 小点阵 */}
          <div className="absolute top-40 right-16 grid grid-cols-4 gap-3 opacity-25">
            {Array.from({ length: 16 }).map((_, i) => (
              <div key={i} className="w-1.5 h-1.5 rounded-full bg-white" />
            ))}
          </div>
        </div>

        {/* Logo */}
        <Link href="/" className="flex items-center gap-3 relative z-10">
          <span className="text-4xl">🦞</span>
          <div>
            <p className="text-white font-black text-2xl leading-none">PrivClaw</p>
            <p className="text-xs mt-0.5" style={{ color: '#FFA6A6' }}>智慧龙虾定制</p>
          </div>
        </Link>

        {/* 主文案 */}
        <div className="relative z-10">
          <h2 className="text-5xl font-black text-white leading-[1.1] mb-8"
            style={{ fontFamily: 'var(--font-display), serif' }}>
            AI 定制服务，<br />为你降本增效
          </h2>
          <div className="space-y-4">
            {[
              { icon: '⚡', text: '专属 AI 员工，24/7 全天候工作' },
              { icon: '💰', text: '成本仅为人类员工的 10%' },
              { icon: '🔒', text: '数据安全，私有化部署可选' },
            ].map((item) => (
              <div key={item.text} className="flex items-center gap-3">
                <span className="text-xl">{item.icon}</span>
                <p className="text-sm" style={{ color: 'rgba(255,255,255,0.8)' }}>{item.text}</p>
              </div>
            ))}
          </div>
        </div>

        {/* 统计 */}
        <div className="relative z-10 grid grid-cols-3 gap-3">
          {[
            { num: '50+', label: '服务客户' },
            { num: '90%',  label: '成本节约' },
            { num: '¥0',   label: '咨询费' },
          ].map((stat) => (
            <div key={stat.label}
              className="rounded-xl p-3 text-center"
              style={{ backgroundColor: 'rgba(255,255,255,0.12)' }}>
              <p className="text-xl font-black text-white">{stat.num}</p>
              <p className="text-xs mt-0.5" style={{ color: '#FFA6A6' }}>{stat.label}</p>
            </div>
          ))}
        </div>
      </div>

      {/* ── 右侧表单区 ────────────────────────────────────────── */}
      <div className="flex-1 flex flex-col items-center justify-center px-6 sm:px-12 py-12 bg-white">
        {/* 移动端 Logo */}
        <Link href="/" className="flex items-center gap-2 mb-10 lg:hidden">
          <span className="text-3xl">🦞</span>
          <span className="font-black text-xl" style={{ color: '#EB4C4C' }}>PrivClaw</span>
        </Link>
        <div className="w-full max-w-sm">
          {children}
        </div>
      </div>
    </div>
  )
}
