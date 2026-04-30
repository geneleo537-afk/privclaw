import type { Metadata } from 'next'
import './globals.css'
import { Providers } from './providers'

export const metadata: Metadata = {
  title: 'PrivClaw 智慧龙虾定制 | AI 定制服务',
  description:
    'PrivClaw 基于 OpenClaw 技术，为企业和个人提供 AI 员工定制服务。全天候工作，成本低 90%，持续进化。',
  keywords: ['PrivClaw', '智慧龙虾定制', 'AI 定制服务', 'AI 员工', 'OpenClaw', '能力模块'],
  openGraph: {
    title: 'PrivClaw 智慧龙虾定制 | AI 定制服务',
    description: '为企业和个人提供专属 AI 员工方案，全天候工作，成本低 90%',
    type: 'website',
    locale: 'zh_CN',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN" suppressHydrationWarning>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
