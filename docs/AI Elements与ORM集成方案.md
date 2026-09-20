# AI Elements Vue 与 ORM/双数据库集成方案

## 1. 定位

AI Elements Vue 是建立在 shadcn-vue 之上的 Vue AI 组件源码注册表，不是独立 UI Framework。组件安装后进入本项目源码，可继续维护和审查。它只解决 AI 交互呈现；模型调用、权限、会话、持久化和任务执行仍由本项目自己的模块与 API 负责。

官方入口：<https://www.ai-elements-vue.com/>。官方支持：

```bash
npx ai-elements-vue@latest add conversation message prompt-input
# 或
npx shadcn-vue@latest add https://registry.ai-elements-vue.com/conversation.json
```

## 2. 前端落点

```text
admin/src/components/ui/                  # shadcn-vue primitives
admin/src/components/ai-elements/          # AI Elements Vue 复制进来的组件源码
admin/src/core/ai/                         # 纯类型、状态、Adapter 接口
admin/src/modules/ai/
├── index.ts
├── module.ts
├── pages/ChatPage.vue
├── components/AiConversation.vue
├── components/AiPromptInput.vue
├── composables/useAiChat.ts
├── services/ai-service.ts                  # 只调用 generated SDK/AI Adapter
└── locales/{zh-CN,en}.json
```

禁止 `components/ai-elements` 直接 import 数据库、Pinia 业务 Store 或写 `/api/...` 字符串。所有 API 通过 OpenAPI 生成的 SDK，所有流式传输通过 `core/ai` 的统一 Adapter。

## 3. 首批组件与职责

| 组件 | 用途 | 首版状态 |
| --- | --- | --- |
| Conversation | 消息滚动容器和底部定位 | 必须 |
| Message | 用户/助手消息、错误和重试 | 必须 |
| PromptInput | 输入、附件、提交、取消 | 必须 |
| Loader/Shimmer | 等待/流式反馈 | 必须 |
| Sources/Inline Citation | 引用来源 | 必须 |
| Model Selector | 选择后端允许的模型 | 必须，选项来自 API |
| Tool/Confirmation | 工具调用和用户确认 | 第二个小版本 |
| Task/Plan | 长任务进度 | 与 Task Engine 一起 |
| Artifact/Code Block | 代码/文档结果 | 与 AI 工具场景一起 |

不要一次安装全部注册表组件；按页面需求加入，保留 lockfile 和生成文件变更记录。

## 4. AI 后端契约

后端模块建议：

```text
server/app/modules/ai/
├── module.py
├── model.py          # conversation/message/attachment 元数据
├── schema.py
├── repository.py     # 只用 SQLAlchemy ORM
├── service.py        # 权限、配额、会话、Provider Adapter
├── router.py
├── resource.py
└── permissions.py
```

最小 API：

```text
GET    /api/v1/ai/models
POST   /api/v1/ai/conversations
GET    /api/v1/ai/conversations/{id}
POST   /api/v1/ai/conversations/{id}/messages
POST   /api/v1/ai/conversations/{id}/cancel
```

`POST messages` 的响应契约必须明确是普通 JSON 还是 SSE/WebSocket；推荐首版使用 SSE，并定义 `message.delta`、`message.completed`、`message.error`、`tool.requested`、`citation.added`、`done` 事件。事件数据只能是可序列化 DTO，不把 Provider SDK 对象传给前端。

## 5. ORM 数据模型原则

首版使用 SQLAlchemy 2.x async ORM：

```text
ai_conversations
  id, owner_user_id, title, provider_key, model_key,
  status, created_at, updated_at

ai_messages
  id, conversation_id, role, content, status,
  model_key, token_input, token_output, error_code,
  created_at

ai_citations
  id, message_id, title, url, excerpt, position, created_at
```

- Repository 只能使用 `select()`、关系加载、分页和条件更新；不写 SQL 字符串。
- `content` 使用 `Text`，短字段使用有长度的 `String`；Token 数量使用整数；时间为 UTC timezone-aware。
- 不把完整 Provider 原始响应无界写入数据库；需要调试时写脱敏、限长的 JSON 摘要。
- API Key、Authorization、prompt 中识别出的 Secret 不能进入 `content`、日志、审计或任务 args。
- 归属和权限由 Service 校验；前端隐藏会话不算授权。

## 6. Provider Adapter

```python
class AiProvider(Protocol):
    key: str

    async def stream(
        self,
        *,
        model: str,
        messages: Sequence[ProviderMessage],
        tools: Sequence[ToolDefinition],
        cancel: CancellationToken,
    ) -> AsyncIterator[ProviderEvent]: ...
```

`AiService` 只依赖这个接口；OpenAI、Anthropic、本地模型或测试 Fake 都通过 Adapter 注册。Provider 失败统一映射为 `AI_PROVIDER_UNAVAILABLE`、`AI_QUOTA_EXCEEDED`、`AI_REQUEST_FAILED` 等机器可读错误。没有任何 Provider 配置时，`/health` 仍为可用，AI 页面显示配置状态而不是让整个应用启动失败。

## 7. ORM 双数据库切换

业务代码不读取数据库类型。只替换：

```env
DATABASE_URL=postgresql+asyncpg://...
# 或
DATABASE_URL=mysql+aiomysql://...
```

同时安装两个 async driver，Engine 工厂按 URL 创建 Engine。Model、Repository、Service、AI API 不改变。迁移不得使用 `JSONB`、`ILIKE`、`citext`、`SKIP LOCKED` 或任一数据库专有 DDL；确有需求必须进入批准的 Adapter 例外，并为另一数据库定义行为。

## 8. 测试与验收

- Component tests：Conversation、Message、PromptInput 覆盖 empty/loading/streaming/error/cancel/retry/citation/tool confirmation。
- API tests：未登录、越权、会话归属、Provider 错误、重复提交、取消。
- ORM integration：PostgreSQL 和 MySQL 使用同一测试矩阵；迁移 `upgrade → downgrade → upgrade`。
- Contract test：OpenAPI 生成 SDK 成功，SSE 事件类型与前端解析器一致。
- Offline test：删除 AI Provider/Redis 配置，基础 Admin Shell、登录、标准 CRUD、OpenAPI 仍能运行。
- Secret test：输入或异常含 token/password/api_key 时，响应日志、审计和数据库均不得保存原值。

## 9. 实施顺序

1. P1 先完成 shadcn-vue/Tailwind CSS Variables 基线。
2. P6 只安装首批 AI Elements 源码组件，完成静态演示，不接真实 Provider。
3. 完成 `core/ai` Adapter、OpenAPI DTO 和 Fake Provider 测试。
4. 完成 AI 模块 ORM/迁移/API，并在 PostgreSQL/MySQL 各跑一遍。
5. 最后接真实 Provider、SSE、取消和工具确认；真实密钥只在本地环境注入。

这样即使 AI 服务暂时不可用，项目的 Admin Framework、ORM、数据库切换和标准 Resource 仍然是独立可交付的。
