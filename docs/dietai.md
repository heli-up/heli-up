# AIGC Dietai 后端工程

在 AI 饮食健康管理平台中担任后端核心开发，负责分层架构、业务接口、数据迁移和前后端联调。工作覆盖饮食记录、AI 对话与宠物健康管理。

## 架构与交付

```text
客户端 / AI Agent
       │
       ▼
路由层：认证、参数校验、接口协议
       │
       ▼
服务层：饮食记录、会话、宠物健康等业务
       │
       ▼
模型层：关系数据与领域模型
       │
       ▼
基础设施：数据库、对象存储、定时任务、外部模型 API
```

按项目经历统计，三个里程碑累计完成 **113 个 API 端点、49 张数据表与 8 个定时任务**。这些数字描述当时的交付范围，未由个人主页更新脚本重新统计，可能与公开分支后续版本存在差异。

## 我的工作

- 设计并实现路由、服务、模型、基础设施分层，编写 Alembic 迁移，为高频查询增加复合索引。
- 实现 JWT 双令牌与 bcrypt 认证体系，完成饮食记录、AI 对话会话等模块。
- 搭建真实宠物健康管理子系统，接入通义万相与 rembg 图像处理管线，配合智能硬件饮食记录。
- 实现滑动窗口限流，修复越权访问并脱敏异常信息，通过 Swagger 支持接口联调。

项目经历记录的压力测试为 50 并发下 CRUD 响应小于 500 ms。由于主页未附测试环境、延迟分位数与完整报告，该数值仅作为当时测试记录，不作为所有接口的性能承诺。

## 公开实现入口

- [DietAI 仓库](https://github.com/helililili/DietAI)：本人账号下的 fork，包含项目整体实现。
- [API 路由](https://github.com/helililili/DietAI/tree/main/routers)
- [数据模型](https://github.com/helililili/DietAI/tree/main/shared/models)
- [限流中间件](https://github.com/helililili/DietAI/blob/main/shared/middleware/rate_limiter.py)
- [复合索引迁移](https://github.com/helililili/DietAI/blob/main/alembic/versions/b4c3_add_performance_indexes.py)
- [定时任务](https://github.com/helililili/DietAI/blob/main/shared/tasks/scheduler.py)
- [宠物形象生成](https://github.com/helililili/DietAI/blob/main/agent/diet_deep_agent/tools/pet_avatar_generator.py)

[返回主页](../README.md)
