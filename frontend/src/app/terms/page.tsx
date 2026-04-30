export default function TermsPage() {
  return (
    <div className="container mx-auto max-w-3xl px-4 py-16">
      <h1 className="text-3xl font-bold mb-6">使用条款</h1>
      <div className="space-y-4 text-sm leading-7 text-[hsl(var(--muted-foreground))]">
        <p>当前页面为本地开发占位版，用于避免注册、支付等页面出现死链。</p>
        <p>
          在正式上线前，这里应补充真实的服务条款，包括账号责任、插件版权、
          退款规则、违规处理和平台免责边界。
        </p>
      </div>
    </div>
  )
}
