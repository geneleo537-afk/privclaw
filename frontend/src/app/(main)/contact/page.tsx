import { Mail, Phone, ArrowLeft } from 'lucide-react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'

export const metadata = {
  title: '免费咨询 - PrivClaw AI 定制服务',
  description: '联系我们，了解 AI 员工如何帮助您的业务降本增效。',
}

export default function ContactPage() {
  return (
    <div className="min-h-[calc(100vh-64px)] flex flex-col justify-center px-4 py-16">
      <div className="container mx-auto max-w-2xl">
        {/* 返回首页 */}
        <Link
          href="/"
          className="inline-flex items-center gap-1.5 text-sm text-gray-400 hover:text-gray-600 transition-colors mb-8"
        >
          <ArrowLeft className="h-4 w-4" />
          返回首页
        </Link>

        {/* 标题区 */}
        <div className="mb-12">
          <p
            className="text-lg font-bold uppercase tracking-widest mb-3"
            style={{ color: '#EB4C4C' }}
          >
            免费咨询
          </p>
          <h1 className="text-4xl sm:text-5xl font-black text-gray-900 mb-4">
            让我们聊聊您的需求
          </h1>
          <p className="text-lg text-gray-500 leading-relaxed">
            无论您想了解 AI 员工方案，还是寻求定制化解决方案，都欢迎随时联系我们。
          </p>
        </div>

        {/* 联系方式卡片 */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 mb-12">
          <div className="flex items-start gap-4 p-6 rounded-2xl border border-gray-100 bg-gray-50 hover:shadow-md transition-shadow">
            <div
              className="w-12 h-12 rounded-full flex items-center justify-center shrink-0"
              style={{ backgroundColor: 'rgba(235,76,76,0.1)', color: '#EB4C4C' }}
            >
              <Phone className="h-5 w-5" />
            </div>
            <div>
              <p className="font-bold text-gray-900 mb-1">电话咨询</p>
              <p className="text-gray-500 text-sm mb-2">工作日 9:00 - 18:00</p>
              <a
                href="tel:+8613800138000"
                className="text-lg font-black hover:underline"
                style={{ color: '#EB4C4C' }}
              >
                138-0013-8000
              </a>
            </div>
          </div>

          <div className="flex items-start gap-4 p-6 rounded-2xl border border-gray-100 bg-gray-50 hover:shadow-md transition-shadow">
            <div
              className="w-12 h-12 rounded-full flex items-center justify-center shrink-0"
              style={{ backgroundColor: 'rgba(235,76,76,0.1)', color: '#EB4C4C' }}
            >
              <Mail className="h-5 w-5" />
            </div>
            <div>
              <p className="font-bold text-gray-900 mb-1">邮件咨询</p>
              <p className="text-gray-500 text-sm mb-2">24 小时内回复</p>
              <a
                href="mailto:hello@clawsourcing.com"
                className="text-lg font-black hover:underline"
                style={{ color: '#EB4C4C' }}
              >
                hello@clawsourcing.com
              </a>
            </div>
          </div>
        </div>

        {/* 附加说明 */}
        <div className="rounded-2xl p-6 text-center" style={{ backgroundColor: '#FFF5F5' }}>
          <p className="text-gray-600 text-sm leading-relaxed">
            咨询完全免费，无任何隐性费用。我们会根据您的业务场景，提供定制化的 AI 员工方案建议。
          </p>
        </div>

        {/* 底部 CTA */}
        <div className="text-center mt-10">
          <Button
            asChild
            variant="outline"
            className="rounded-full h-11 px-7 text-sm font-semibold border-2 hover:opacity-80 transition-opacity"
            style={{ borderColor: '#EB4C4C', color: '#EB4C4C', backgroundColor: 'transparent' }}
          >
            <Link href="/#solutions">了解服务方案</Link>
          </Button>
        </div>
      </div>
    </div>
  )
}
