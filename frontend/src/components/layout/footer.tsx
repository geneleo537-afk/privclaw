import Link from 'next/link'

export function Footer() {
  const currentYear = new Date().getFullYear()

  return (
    <footer className="border-t border-[hsl(var(--border))] bg-[hsl(var(--muted)/0.3)]">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* 品牌介绍 */}
          <div className="md:col-span-1">
            <Link href="/" className="flex items-center gap-2 mb-3">
              <span className="text-2xl">🦞</span>
              <span className="font-bold text-lg text-[hsl(var(--primary))]">PrivClaw 智慧龙虾定制</span>
            </Link>
            <p className="text-sm text-[hsl(var(--muted-foreground))] leading-relaxed">
              基于 OpenClaw 技术的 AI 定制服务平台，为企业和个人提供专属 AI 员工方案。
            </p>
          </div>

          {/* 服务与方案 */}
          <div>
            <h4 className="font-semibold text-sm mb-4">服务与方案</h4>
            <ul className="space-y-2">
              {[
                { label: '服务方案', href: '/#solutions' },
                { label: '能力库', href: '/plugins' },
                { label: '合作流程', href: '/#process' },
                { label: '关于我们', href: '/about' },
              ].map((item) => (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    className="text-sm text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--primary))] transition-colors"
                  >
                    {item.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* 开发者生态 */}
          <div>
            <h4 className="font-semibold text-sm mb-4">开发者生态</h4>
            <ul className="space-y-2">
              {[
                { label: '发布能力模块', href: '/dashboard/plugins/new' },
                { label: '开发者文档', href: '/docs' },
                { label: 'OpenClaw 协议', href: '/openclaw' },
                { label: '收益结算', href: '/dashboard/wallet' },
              ].map((item) => (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    className="text-sm text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--primary))] transition-colors"
                  >
                    {item.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* 联系我们 */}
          <div>
            <h4 className="font-semibold text-sm mb-4">联系我们</h4>
            <ul className="space-y-2">
              {[
                { label: '商务合作', href: 'mailto:business@lobstermart.com' },
                { label: '举报问题', href: 'mailto:report@lobstermart.com' },
                { label: '技术支持', href: 'mailto:support@lobstermart.com' },
                { label: '加入我们', href: '/careers' },
              ].map((item) => (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    className="text-sm text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--primary))] transition-colors"
                  >
                    {item.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* 版权 */}
        <div className="mt-10 pt-6 border-t border-[hsl(var(--border))] flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-[hsl(var(--muted-foreground))]">
          <p>&copy; {currentYear} PrivClaw 智慧龙虾定制. 保留所有权利。</p>
          <p>Powered by OpenClaw &middot; AI 定制服务</p>
        </div>
      </div>
    </footer>
  )
}
