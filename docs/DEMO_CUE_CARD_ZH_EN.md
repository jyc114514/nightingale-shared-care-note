# Nightingale 双语录制 Cue Card

目标：4:30 · 操作提示中文 · 网页标签 English · 口播/字幕 English。把这张卡放在第二块
屏幕或手机上，不要录进视频。精确旁白以 [`DEMO_SCRIPT_SPOKEN_EN.md`](DEMO_SCRIPT_SPOKEN_EN.md)
为准；下表只用于快速找动作。

| 时间 | 中文操作提示 | 画面确认 | 下一步 |
| --- | --- | --- | --- |
| 00:00–00:24 | 镜头外登录 Staff，选 `Sarah Tan` 和 `English`；等待 `Up to date`；关闭 `Guide` 和 drawer。 | `Shared Care Note`、`Staff view`、共享工作区 | `Glance View` |
| 00:24–01:06 | 在 `Glance View` 选择当前实际可用的 AI-assisted card；指出 action/status/item kind/risk/priority；展开 `Why is this here?`；点击 `Open source`。 | `Original source`、版本、高亮原文；`Technical details` 默认折叠 | 保持来源可见 |
| 01:06–01:44 | 找到 `Voice note`；如无 result，播放音频后只点一次 `Create care-note suggestion`；等待 `Ready for review`；点 transcript segment 和 `View source`。 | 音频、时间戳文字记录、建议和来源链路 | 进入协作 |
| 01:44–02:08 | `Staff note` → `Edit` → `Save revision`；`Comments` → `Comment body` → `@Clinician A` → `Add comment`。 | 新版本、团队讨论、mention | 状态切换 |
| 02:08–02:30 | 按实际状态完成 `Resolve`/`Unresolve`、`Pin`/`Unpin`；关 drawer；停录后镜头外 `Sign out` 并登录 Clinician。 | 讨论状态和优先级反馈完成切换 | `Clinician view` |
| 02:30–03:05 | `Clinician section` → `Edit` → `Save revision`；`History` → earlier version → `Compare`；看 `Before`/`After`；如可用 `Revert` 一次。 | 新版本和保留的历史 | `Historical context` |
| 03:05–03:37 | 展开 `How historical context is organised`；指出 `Recent context`、`Earlier context`、`Historical summary`；点击 `View original record`。 | 摘要明确不是原始记录，页面滚到相关时间线 | 念 UX-01 evidence |
| 03:37–04:10 | 停录切换 Sarah Patient；确认 `Patient view`、`Your care summary`；展示患者时间线和 `Voice note`。 | 仅患者可见内容，无内部协作控件 | 收尾 |
| 04:10–04:30 | 关闭 drawer，指向 synthetic-only disclosure 和 source/review boundary，鼠标移开，念最后一段。 | HTTPS 应用页面稳定 | 停录并做 QA |

## 备用标记

- 当前卡片已是 `Reviewed`：换另一张仍显示 `Needs review` 的卡片；不要写死名称或版本。
- 已有 Voice result：直接展示，不再次点击 `Create care-note suggestion`。
- `Compare`/`Revert` 不可用：停在当前 `History`，按实际画面说明。
- 页面状态不稳定：停录、镜头外刷新或重新准备，不把错误状态剪成成功。

## 安全标记

- 密码输入、账号切换、浏览器自动填充和地址栏敏感信息全部离镜头。
- 不展示 API key、数据库 URL、环境变量、Cookie、browser storage、DevTools、Render
  Environment 或 provider console。
- 录制前后不修改 clinical note 原文，不把来源技术细节当作主旁白。
- 视频通过 [`DEMO_VIDEO_QA.md`](DEMO_VIDEO_QA.md) 前，不生成最终 PDF/ZIP/MANIFEST，不 push，
  不发邮件。
