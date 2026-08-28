# Nightingale 双语录制 Cue Card

录制时以 [`DEMO_RECORDING_MASTER_ZH_EN.md`](DEMO_RECORDING_MASTER_ZH_EN.md) 为唯一操作主文件；本文件保留为快速参考卡。

目标：约 4:55（允许 4:40–4:55）· 操作提示中文 · 网页标签 English · 口播/字幕 English。把这张卡放在第二块
屏幕或手机上，不要录进视频。精确旁白、逐 cue 时间码和动作顺序以 Master Runbook 为准；下表
只用于快速找动作。

| 时间 | 中文操作提示 | 画面确认 | 下一步 |
| --- | --- | --- | --- |
| 00:00–00:26 | 镜头外登录 Staff，选 `Sarah Tan` 和 `English`；等待 `Up to date`；关闭 `Guide` 和 drawer。 | `Shared Care Note`、`Staff view`、共享工作区 | `Glance View` |
| 00:26–01:10 | 在 `Glance View` 选择当前实际可用的 AI-assisted card；指出 action/status/item kind/risk/priority；展开 `Why is this here?`；点击 `Open source`。 | `Original source`、版本、高亮原文；`Technical details` 默认折叠 | 保持来源可见 |
| 01:10–01:47 | 找到 `Voice note`；如无 result，播放音频后只点一次 `Create care-note suggestion`；等待 `Ready for review`；点 transcript segment 和 `View source`。 | 音频、时间戳文字记录、建议和来源链路 | 进入协作 |
| 01:47–02:15 | `Staff note` → `Edit` → `Save revision`；`Comments` → `Comment body` → `@Clinician A` → `Add comment`。 | 新版本、团队讨论、mention | 状态切换 |
| 02:15–02:45 | 在 comment 点击 `Assign task` → `Task title` → 输入 Review synthetic follow-up plan → `Assign to: Clinician A` → `Create task` 一次；回到 `Glance` 看 `Open task`。 | 新 `Assigned task`、Clinician A、Open | 停录切换 |
| 02:45–03:42 | Clinician：`Open task` → 确认 `Open` → 改为 `In progress`；再 `History` → `Compare` → `Before`/`After`；如可用 `Revert`。然后 AI suggestion 1 → `Accept` → `Reviewed`；AI suggestion 2 → `Reject` → disappears。 | Task lifecycle 和 AI review 分开显示 | `Historical context` |
| 03:42–04:16 | 展开 `How historical context is organised`；指出 `Recent context`、`Earlier context`、`Historical summary`；点击 `View original record`。 | 摘要明确不是原始记录，页面滚到相关时间线 | 念 UX-01 evidence |
| 04:16–04:40 | 停录切换 Sarah Patient；确认 `Patient view`、`Your care summary`；展示患者时间线和 `Voice note`。 | 仅患者可见内容，无内部协作控件 | 收尾 |
| 04:40–04:55 | 关闭 drawer，指向 synthetic-only disclosure 和 source/review boundary，鼠标移开，念收尾。 | HTTPS 应用页面稳定 | 停录并做 QA |

> **Task status ≠ AI review**
> Task: Open → In progress → Done
> AI suggestion: Accept / Reject
> Staff：Comment → Assign task → Task title → Clinician A → Create task → Glance
> Clinician task：Open task → Open → In progress
> Clinician AI review：AI suggestion 1 → Accept → Reviewed；AI suggestion 2 → Reject → disappears

## 备用标记

- 当前卡片已是 `Reviewed`：换另一张仍显示 `Needs review` 的卡片；不要写死名称或版本。
- 已有 Voice result：直接展示，不再次点击 `Create care-note suggestion`。
- 已有 task：不要再次 `Create task`；若已是 `In progress`，直接展示；若已是 `Done`，不要改回 `Open`。
- `Compare`/`Revert` 不可用：停在当前 `History`，按实际画面说明。
- `Accept`/`Reject` 不可用：换当前仍显示两个按钮的 AI suggestion；不要改数据来匹配名称。
- 页面状态不稳定：停录、镜头外刷新或重新准备，不把错误状态剪成成功。

## 安全标记

- 密码输入、账号切换、浏览器自动填充和地址栏敏感信息全部离镜头。
- 不展示 API key、数据库 URL、环境变量、Cookie、browser storage、DevTools、Render
  Environment 或外部服务控制台。
- 录制前后不修改 clinical note 原文，不把来源技术细节当作主旁白。
- 视频通过 [`DEMO_VIDEO_QA.md`](DEMO_VIDEO_QA.md) 前，不生成最终 PDF/ZIP/MANIFEST，不 push，
  不发邮件。
