import { PluginCard, type PluginCardProps } from './plugin-card'

interface PluginGridProps {
  plugins: PluginCardProps[]
  /** 每行列数配置，默认 1/2/3/4 */
  cols?: 2 | 3 | 4
}

const colsClass: Record<number, string> = {
  2: 'grid-cols-1 sm:grid-cols-2',
  3: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3',
  4: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4',
}

export function PluginGrid({ plugins, cols = 4 }: PluginGridProps) {
  if (plugins.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-[hsl(var(--muted-foreground))]">
        <span className="text-6xl mb-4">🦞</span>
        <p className="text-lg font-medium">暂无插件</p>
        <p className="text-sm mt-1">快来发布第一个插件吧！</p>
      </div>
    )
  }

  return (
    <div className={`grid gap-5 ${colsClass[cols]}`}>
      {plugins.map((plugin) => (
        <PluginCard key={plugin.id} {...plugin} />
      ))}
    </div>
  )
}
