# 主页设计与更新机制

主页以招聘方阅读顺序组织：一句话定位、教育背景、技能标签、三个项目案例、工程笔记与公开动态、联系方式。

## 视觉设计

参考 [yuki4266](https://github.com/yuki4266/yuki4266) 的动态 SVG 方法，以及 [anghunk](https://github.com/anghunk) 的定位、联系和内容入口布局。SVG、项目卡片与生成器均为本主页原创实现，没有复制参考仓库的花园、猫、技能资产或代码。

蓝灰底色、青绿数据线与少量暖色标记组成视觉系统。抽象山线与城市轮廓呼应成都；技术、数据与服务节点对应个人项目。图形是工程意象，不是监控面板或性能曲线。

- Header/Footer 按北京时间的晨间、白昼、傍晚、夜间改变天体位置与环境配色，按月份切换季节色。
- GitHub 浅色/深色主题通过 `<picture>` 选择对应 SVG，环境时段与阅读主题相互独立。
- 底部 14 个信号点映射最近 14 天采样到的公开活动数量。公开 Events API 只取最多 100 条，不代表全部贡献或完整提交历史。
- 数据线与节点使用低频 CSS 动画；`prefers-reduced-motion` 下停止动画，静态场景仍完整。
- 内容层使用 GitHub 支持的 Markdown/HTML，图片有替代文本，移动端可直接阅读图片下面的项目职责与链接。

## 更新与可靠性

Python 生成器只使用标准库，不依赖第三方统计卡片、访问计数器、天气服务或前端脚本。Actions 每 6 小时运行一次，也可以手动触发；运行时间可能受 GitHub 调度延迟影响。SVG 是最近一次运行时生成的快照，时间不是浏览者设备的实时钟表。

数据只来自 `https://api.github.com/users/heli-up/events/public?per_page=100`。API 失败时保留已有公开动态和活动采样，继续更新时间场景；没有历史数据时标记活动暂不可用，不填造事件。生成结果随代码提交托管，不需要向访客暴露令牌。

公开动态只展示本人发起的 Push、PR、Release 和 Create 事件，排除主页仓库自身更新及 watch/fork 收藏活动。项目笔记为本主页整理的案例，不伪装成此前已经发布的博客。

如 GitHub 对低活跃仓库暂停定时工作流，可在 Actions 中重新启用。新 fork 中定时任务也可能需要手动启用。仓库级令牌只授予 `contents: write`；手动本地运行无需令牌也可访问公开 API。

```bash
python scripts/update_profile.py
python scripts/update_profile.py --offline
python -m unittest discover -s tests -v
```

[返回主页](../README.md)
