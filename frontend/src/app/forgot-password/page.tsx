import Link from 'next/link'

export default function ForgotPasswordPage() {
  return (
    <div className="container mx-auto max-w-xl px-4 py-16">
      <h1 className="text-3xl font-bold mb-4">忘记密码</h1>
      <p className="text-sm leading-7 text-[hsl(var(--muted-foreground))]">
        当前版本还没有开放完整的找回密码流程。开发联调阶段建议直接在本地数据库中
        重置测试账号密码，或重新注册一个新账号继续验证主流程。
      </p>
      <Link href="/login" className="inline-block mt-6 text-sm text-[hsl(var(--primary))] hover:underline">
        返回登录
      </Link>
    </div>
  )
}
