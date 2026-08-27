# Nightingale 最终录制 Shot List

目标时长：4:30 · 页面 English · 操作提示中文 · 口播/字幕 English。以下是录制目标，不是
本阶段已经生成的视频或截图文件。

| 镜头 | 时间 | 角色 | 中文操作 / 真实按钮 | 应看到的结果 | 录制目标 |
| ---: | --- | --- | --- | --- | --- |
| 1 | 00:00-00:23 | `Staff A` | 确认 `English`、`Sarah Tan`、`Live updates: Connected`；鼠标移开。 | `Shared Care Note`、`Staff view`、trust boundary | `01-staff-opening.mp4` |
| 2 | 00:23-01:04 | `Staff A` | 查看 `Top Card`；点击当前 Suggested AI card 的 `Open source`；【等待】`Immutable source`。 | 内容/action/status/risk/ranking、exact mark、immutable source | `02-staff-glance-source.mp4` |
| 3 | 01:04-01:42 | `Staff A` | 检查 fixture disclosure；播放；必要时只点一次 `Process sample`；点 8 秒 segment/source。 | prerecorded WAV、mock transcript、timestamps、confidence unavailable、source | `03-staff-voice.mp4` |
| 4 | 01:42-02:06 | `Staff A` | `Edit` → `Save revision`；`Comments` → `@clinician` → `@Clinician A · clinician` → `Add comment`。 | Staff revision、root comment、`Mentions: @Clinician A` | `04-staff-comment.mp4` |
| 5 | 02:06-02:28 | `Staff A` → `Clinician A` | `Resolve` → `Unresolve`；`Pin` → `Unpin`；关闭 drawer；【停录】`Sign out`；【切换账号】。 | 状态切换完成；只发生一次角色 cut | `05-role-cut.mp4` |
| 6 | 02:28-03:00 | `Clinician A` | `Edit` → `Save revision`；`History`；选 available earlier version 的 `Compare`；【等待】Before/After；必要时 `Revert` 一次。 | Before/After、new revert version、history 保留 | `06-clinician-review.mp4` |
| 7 | 03:00-03:32 | `Clinician A` | 指向 `Hot context`、`Warm index`、`Derived summary · not the original record`；点击 `View original record`；念 UX-01。 | 滚到 canonical Patient summary；不虚构 exact-span panel | `07-history-context.mp4` |
| 8 | 03:32-04:00 | `Sarah Patient` | 【停录】切换账号；【不要显示密码】；确认 `Patient view`、`Internal Glance View is hidden`；只显示 `Synthetic patient follow-up · patient`。 | 无 Top Card/internal controls/Clinical sample/source control | `08-patient-privacy.mp4` |
| 9 | 04:00-04:30 | 任一稳定内部角色 | 指向 synthetic-only disclosure；鼠标移开；念完【停录】。 | HTTPS/PostgreSQL/fixture boundary，未打开配置页 | `09-honest-close.mp4` |

## 不能作为成功镜头录制

不要录制新建 note、手动 phrase highlight、第二浏览器 SSE、live 409 conflict、task 完整
生命周期、live DeepSeek、microphone、upload、Whisper inference、diarization 或 clinical
validation。对应步骤已在 rehearsal 中移除或改写，详见 [demo_rehearsal.md](evidence/demo_rehearsal.md)。
