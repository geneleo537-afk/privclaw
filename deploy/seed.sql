-- PrivClaw 种子数据：管理员 + 分类 + 标签 + 6 个官方自营插件

-- 用户 profile
INSERT INTO user_profiles (id, user_id, bio, created_at, updated_at)
VALUES (
  'b0000000-0000-0000-0000-000000000001',
  'a0000000-0000-0000-0000-000000000001',
  'PrivClaw 平台官方管理员',
  NOW(),
  NOW()
);

-- 分类
INSERT INTO plugin_categories (id, name, slug, description, sort_order) VALUES
  ('c0000000-0000-0000-0000-000000000001', '生产力',   'productivity', '提升工作效率的能力模块', 1),
  ('c0000000-0000-0000-0000-000000000002', '开发工具', 'devtools',     '面向开发者的效率工具',   2),
  ('c0000000-0000-0000-0000-000000000003', 'AI 增强',  'ai',           'AI 驱动的智能能力',     3),
  ('c0000000-0000-0000-0000-000000000004', '内容创作', 'content',      '内容生产与处理工具',    4),
  ('c0000000-0000-0000-0000-000000000005', '自动化',   'automation',   '流程自动化能力模块',    5),
  ('c0000000-0000-0000-0000-000000000006', '数据分析', 'data',         '数据处理与分析工具',    6);

-- 标签（plugin_tags 表无 updated_at 列）
INSERT INTO plugin_tags (id, name, slug) VALUES
  ('d0000000-0000-0000-0000-000000000001', '办公协同',   'office'),
  ('d0000000-0000-0000-0000-000000000002', '内容处理',   'content-proc'),
  ('d0000000-0000-0000-0000-000000000003', '项目管理',   'project-mgmt'),
  ('d0000000-0000-0000-0000-000000000004', '文档处理',   'docs'),
  ('d0000000-0000-0000-0000-000000000005', '多媒体',     'media'),
  ('d0000000-0000-0000-0000-000000000006', 'DevOps',     'devops'),
  ('d0000000-0000-0000-0000-000000000007', '运维管理',   'ops'),
  ('d0000000-0000-0000-0000-000000000008', '知识管理',   'knowledge'),
  ('d0000000-0000-0000-0000-000000000009', '数据处理',   'data-proc'),
  ('d0000000-0000-0000-0000-00000000000a', '视频剪辑',   'video-edit'),
  ('d0000000-0000-0000-0000-00000000000b', '官方自营',   'official');

-- 插件 1: Google 全能
INSERT INTO plugins (id, developer_id, category_id, name, slug, summary, description, icon_url, price, is_free, status, review_status, current_version, avg_rating, rating_count, download_count, purchase_count, published_at, created_at, updated_at)
VALUES (
  'e0000000-0000-0000-0000-000000000001',
  'a0000000-0000-0000-0000-000000000001',
  'c0000000-0000-0000-0000-000000000001',
  'Google 全能',
  'clawstore-google-workspace',
  'Google Workspace 全能工具，覆盖 Gmail、日历、云端硬盘，一句话管理你的整个 Google 生态。',
  '## Google 全能

Google Workspace 全能工具，覆盖 Gmail、日历、云端硬盘等核心服务。

### 核心能力
- **Gmail 管理**：扫描收件箱、标记重要邮件、批量归档
- **日历管理**：查看日程、创建事件、智能提醒
- **云端硬盘**：搜索文件、共享链接、空间管理

### 使用示例
```
$ 帮我查看 Gmail 里今天的重要邮件，未读标记红色星标
→ 已扫描收件箱，找到 12 封未读邮件，已标记 5 封重要邮件为红色星标。
```',
  '', 0, true, 'published', 'approved', '1.2.0',
  4.8, 156, 2340, 890, NOW(), NOW(), NOW()
);

-- 插件 2: 内容摘要
INSERT INTO plugins (id, developer_id, category_id, name, slug, summary, description, icon_url, price, is_free, status, review_status, current_version, avg_rating, rating_count, download_count, purchase_count, published_at, created_at, updated_at)
VALUES (
  'e0000000-0000-0000-0000-000000000002',
  'a0000000-0000-0000-0000-000000000001',
  'c0000000-0000-0000-0000-000000000004',
  '内容摘要',
  'clawstore-summarize',
  '多格式内容摘要引擎，支持网页、PDF、YouTube 视频，快速提炼核心观点。',
  '## 内容摘要

多格式内容摘要引擎，支持网页、PDF、YouTube 视频。

### 核心能力
- **网页摘要**：输入 URL 即可获取核心观点
- **PDF 解析**：上传 PDF 自动提取关键内容
- **视频总结**：YouTube 视频字幕提取 + 观点归纳

### 使用示例
```
$ 总结这个 YouTube 视频的核心观点 https://youtu.be/xxx
→ 已获取字幕，主要观点：1. AI Agent 架构趋势 2. 多模态融合 3. 工具调用标准化
```',
  '', 0, true, 'published', 'approved', '2.0.1',
  4.6, 203, 3120, 1450, NOW(), NOW(), NOW()
);

-- 插件 3: Notion 知识管理
INSERT INTO plugins (id, developer_id, category_id, name, slug, summary, description, icon_url, price, is_free, status, review_status, current_version, avg_rating, rating_count, download_count, purchase_count, published_at, created_at, updated_at)
VALUES (
  'e0000000-0000-0000-0000-000000000003',
  'a0000000-0000-0000-0000-000000000001',
  'c0000000-0000-0000-0000-000000000001',
  'Notion 知识管理',
  'clawstore-notion',
  'Notion 笔记与数据库管理，自然语言增删查改页面、数据库条目，知识库随时在线。',
  '## Notion 知识管理

Notion 笔记与数据库管理，自然语言增删查改。

### 核心能力
- **页面管理**：创建、编辑、搜索页面
- **数据库操作**：新增/修改/查询数据库条目
- **知识检索**：全文搜索 + 语义匹配

### 使用示例
```
$ 在"项目看板"数据库新增一条：Q2 发布计划，优先级高
→ 已在「项目看板」新增条目，标题：Q2 发布计划，优先级：🔴 高，状态：待开始。
```',
  '', 0, true, 'published', 'approved', '1.5.0',
  4.7, 178, 2870, 1120, NOW(), NOW(), NOW()
);

-- 插件 4: nano-pdf
INSERT INTO plugins (id, developer_id, category_id, name, slug, summary, description, icon_url, price, is_free, status, review_status, current_version, avg_rating, rating_count, download_count, purchase_count, published_at, created_at, updated_at)
VALUES (
  'e0000000-0000-0000-0000-000000000004',
  'a0000000-0000-0000-0000-000000000001',
  'c0000000-0000-0000-0000-000000000006',
  'nano-pdf',
  'clawstore-nano-pdf',
  'PDF 编辑与处理，支持提取文本、合并拆分、添加水印，告别繁琐的 PDF 操作。',
  '## nano-pdf

PDF 编辑与处理工具，支持多种操作。

### 核心能力
- **文本提取**：从 PDF 中提取纯文本或结构化内容
- **合并拆分**：多个 PDF 合并为一，或按页拆分
- **水印处理**：添加文字/图片水印，支持位置和透明度配置

### 使用示例
```
$ 把合同 A.pdf 和附件 B.pdf 合并，加上公司水印
→ 已合并为 合同_完整版.pdf（共 48 页），公司水印已添加到每页右下角。
```',
  '', 0, true, 'published', 'approved', '1.0.3',
  4.5, 92, 1560, 680, NOW(), NOW(), NOW()
);

-- 插件 5: FFmpeg 视频编辑器
INSERT INTO plugins (id, developer_id, category_id, name, slug, summary, description, icon_url, price, is_free, status, review_status, current_version, avg_rating, rating_count, download_count, purchase_count, published_at, created_at, updated_at)
VALUES (
  'e0000000-0000-0000-0000-000000000005',
  'a0000000-0000-0000-0000-000000000001',
  'c0000000-0000-0000-0000-000000000005',
  'FFmpeg 视频编辑器',
  'clawstore-ffmpeg-video-editor',
  '自然语言生成 FFmpeg 命令，轻松完成视频裁剪、转码、拼接，无需记住复杂参数。',
  '## FFmpeg 视频编辑器

自然语言驱动 FFmpeg，无需记住复杂命令。

### 核心能力
- **视频裁剪**：按时间点或时长剪切片段
- **格式转码**：MP4/AVI/MOV/WebM 互转
- **视频拼接**：多段视频无缝合并
- **分辨率调整**：自由调整输出分辨率

### 使用示例
```
$ 把 input.mp4 的前 30 秒剪出来，输出 1080p 的 clip.mp4
→ 正在执行 ffmpeg 命令……已生成 clip.mp4（1920x1080，30s，12.3 MB）。
```',
  '', 0, true, 'published', 'approved', '1.1.0',
  4.4, 67, 980, 420, NOW(), NOW(), NOW()
);

-- 插件 6: Docker Essentials
INSERT INTO plugins (id, developer_id, category_id, name, slug, summary, description, icon_url, price, is_free, status, review_status, current_version, avg_rating, rating_count, download_count, purchase_count, published_at, created_at, updated_at)
VALUES (
  'e0000000-0000-0000-0000-000000000006',
  'a0000000-0000-0000-0000-000000000001',
  'c0000000-0000-0000-0000-000000000002',
  'Docker Essentials',
  'clawstore-docker-essentials',
  'Docker 容器管理核心命令，通过对话式交互构建镜像、管理容器、清理资源。',
  '## Docker Essentials

Docker 容器管理工具，对话式交互。

### 核心能力
- **镜像管理**：构建、拉取、推送、清理镜像
- **容器操作**：启动、停止、重启、日志查看
- **资源清理**：一键清理悬挂镜像、停止容器、未使用网络
- **Compose 编排**：通过自然语言生成 docker-compose.yml

### 使用示例
```
$ 清理所有停止的容器和悬挂镜像
→ 已清理 5 个停止容器，释放 2.3 GB 磁盘空间。
```',
  '', 0, true, 'published', 'approved', '1.3.2',
  4.3, 54, 870, 350, NOW(), NOW(), NOW()
);

-- 标签关联（每个插件都有"官方自营"标签）
-- Google 全能: 办公协同 + 官方自营
INSERT INTO plugin_tag_relations (plugin_id, tag_id) VALUES
  ('e0000000-0000-0000-0000-000000000001', 'd0000000-0000-0000-0000-000000000001'),
  ('e0000000-0000-0000-0000-000000000001', 'd0000000-0000-0000-0000-00000000000b');

-- 内容摘要: 内容处理 + 官方自营
INSERT INTO plugin_tag_relations (plugin_id, tag_id) VALUES
  ('e0000000-0000-0000-0000-000000000002', 'd0000000-0000-0000-0000-000000000002'),
  ('e0000000-0000-0000-0000-000000000002', 'd0000000-0000-0000-0000-00000000000b');

-- Notion: 知识管理 + 项目管理 + 官方自营
INSERT INTO plugin_tag_relations (plugin_id, tag_id) VALUES
  ('e0000000-0000-0000-0000-000000000003', 'd0000000-0000-0000-0000-000000000008'),
  ('e0000000-0000-0000-0000-000000000003', 'd0000000-0000-0000-0000-000000000003'),
  ('e0000000-0000-0000-0000-000000000003', 'd0000000-0000-0000-0000-00000000000b');

-- nano-pdf: 文档处理 + 数据处理 + 官方自营
INSERT INTO plugin_tag_relations (plugin_id, tag_id) VALUES
  ('e0000000-0000-0000-0000-000000000004', 'd0000000-0000-0000-0000-000000000004'),
  ('e0000000-0000-0000-0000-000000000004', 'd0000000-0000-0000-0000-000000000009'),
  ('e0000000-0000-0000-0000-000000000004', 'd0000000-0000-0000-0000-00000000000b');

-- FFmpeg: 多媒体 + 视频剪辑 + 官方自营
INSERT INTO plugin_tag_relations (plugin_id, tag_id) VALUES
  ('e0000000-0000-0000-0000-000000000005', 'd0000000-0000-0000-0000-000000000005'),
  ('e0000000-0000-0000-0000-000000000005', 'd0000000-0000-0000-0000-00000000000a'),
  ('e0000000-0000-0000-0000-000000000005', 'd0000000-0000-0000-0000-00000000000b');

-- Docker: DevOps + 运维管理 + 官方自营
INSERT INTO plugin_tag_relations (plugin_id, tag_id) VALUES
  ('e0000000-0000-0000-0000-000000000006', 'd0000000-0000-0000-0000-000000000006'),
  ('e0000000-0000-0000-0000-000000000006', 'd0000000-0000-0000-0000-000000000007'),
  ('e0000000-0000-0000-0000-000000000006', 'd0000000-0000-0000-0000-00000000000b');

-- 更新分类插件计数
UPDATE plugin_categories SET plugin_count = (
  SELECT COUNT(*) FROM plugins WHERE category_id = plugin_categories.id AND status = 'published' AND deleted_at IS NULL
);
