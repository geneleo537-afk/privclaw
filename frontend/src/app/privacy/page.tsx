export default function PrivacyPage() {
  return (
    <div className="container mx-auto max-w-3xl px-4 py-16">
      <h1 className="text-3xl font-bold mb-6">隐私政策</h1>
      <div className="space-y-4 text-sm leading-7 text-[hsl(var(--muted-foreground))]">
        <p>当前页面为本地开发占位版，用于避免注册与支付相关页面出现空链接。</p>
        <p>
          正式上线前，这里需要明确说明用户资料、订单数据、支付信息和日志信息的收集、
          使用、存储与删除策略。
        </p>
      </div>
    </div>
  )
}
