# Nightingale 最终录制 Shot List

录制时以 [`DEMO_RECORDING_MASTER_ZH_EN.md`](DEMO_RECORDING_MASTER_ZH_EN.md) 为唯一操作主文件；本文件保留为镜头规划参考。

目标时长：约 4:55（允许 4:40–4:55）· 页面 English · 操作提示中文 · 口播/字幕 English。以下是录制目标，不是
已经生成的视频或最终交付包。

| 镜头 | 时间 | 角色 | 中文操作 / 真实按钮 | 应看到的结果 | 录制目标 |
| ---: | --- | --- | --- | --- | --- |
| 1 | 00:00–00:26 | `Staff A` | 镜头外登录，选 `Sarah Tan`；确认 `English`、`Up to date`。 | `Shared Care Note`、`Staff view`、共享工作区 | `01-staff-opening.mp4` |
| 2 | 00:26–01:10 | `Staff A` | 在 `Glance View` 查看 priority/action/status/risk；点击 `Open source`。 | 不超过六项、`Original source`、版本和高亮原文 | `02-staff-glance-source.mp4` |
| 3 | 01:10–01:47 | `Staff A` | `Voice note`；播放；必要时一次 `Create care-note suggestion`；点击 segment/`View source`。 | 音频、prepared timestamped transcript、建议、来源链路 | `03-staff-voice.mp4` |
| 4 | 01:47–02:15 | `Staff A` | `Staff note` → `Edit` → `Save revision`；`Comments` → mention → `Add comment`。 | 新版本、团队讨论、`@Clinician A` | `04-staff-comment.mp4` |
| 5 | 02:15–02:45 | `Staff A` → `Clinician A` | comment → `Assign task` → `Task title` → `Review synthetic follow-up plan` → `Assign to: Clinician A` → `Create task` 一次；回到 `Glance` 看 `Open task`。 | 新 `Assigned task`、Clinician A、Open；一次角色 cut | `05-role-cut.mp4` |
| 6 | 02:45–03:42 | `Clinician A` | `Open task` → `Open` → `In progress`；`History` → `Compare` → `Before`/`After`；如可用 `Revert`；AI suggestion 1 → `Accept` → `Reviewed`；AI suggestion 2 → `Reject` → disappears。 | Task lifecycle 和 AI review 分开；新版本、source 保留 | `06-clinician-review.mp4` |
| 7 | 03:42–04:16 | `Clinician A` | 展开 `How historical context is organised`；查看三类上下文；点击 `View original record`。 | 摘要标注不是原始记录；滚到相关时间线 | `07-history-context.mp4` |
| 8 | 04:16–04:40 | `Sarah Patient` | 镜头外切换账号；确认 `Patient view`、`Your care summary`；展示 Patient Voice。 | 只有患者可见内容，无内部控件 | `08-patient-privacy.mp4` |
| 9 | 04:40–04:55 | 任一稳定内部角色 | 关闭 drawer；指向 synthetic-only disclosure 和 source/review boundary；念收尾。 | HTTPS 应用页面稳定，无配置/日志 | `09-product-close.mp4` |

具体操作、失败处理、英文旁白和逐 cue 时间码见
[`DEMO_RECORDING_MASTER_ZH_EN.md`](DEMO_RECORDING_MASTER_ZH_EN.md)。本文件只保留镜头规划参考。

状态边界：Task = Open → In progress → Done；AI suggestion = Accept / Reject。不要把 task 描述成
accepted，也不要把 AI suggestion 的 Reviewed 当成 task status。
