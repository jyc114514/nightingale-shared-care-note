# Nightingale 双语录制 Cue Card

目标：4:30 · 操作中文 · 网页标签 English · 口播/字幕 English
放在第二块屏幕、平板或手机上；不要把它录进视频。

| 时间 | 中文操作提示 | 念的英文 | 下一步 |
| --- | --- | --- | --- |
| 00:00-00:23 | 【继续录制】Staff；确认 `English`、`Sarah Tan`、`Live updates: Connected`；鼠标移开。 | 【念】“Nightingale is a shared care note for synthetic data. It is a trust system, not an autonomous medical system.” | 继续 `Top Card` |
| 00:23-01:04 | 【继续录制】【点击】查看 `Top Card`；指出 action/status/risk；当前 Suggested AI card → `Open source`；【等待】`Immutable source`。 | 【念】“The Top Card is designed for a fast glance. Ranking priority is not a medical risk score.” | source 保持打开 |
| 01:04-01:42 | 【继续录制】【点击】确认 `Prerecorded synthetic audio only`、`Mock transcript fixture`；播放；必要时只点一次 `Process sample`；点击 8 秒 segment/source。 | 【念】“This optional prototype uses prerecorded synthetic audio and a mock timestamped transcript. It does not claim live ASR or diarization.” | Voice/source 保持 |
| 01:42-02:06 | 【继续录制】【点击】`Staff note` → `Edit` → `Save revision`；`Comments` → `@clinician` → `@Clinician A · clinician` → `Add comment`。 | 【念】“Staff can edit the existing Staff note and add an internal comment. The mention is stored as metadata.” | 继续 collaboration |
| 02:06-02:28 | 【继续录制】【点击】`Resolve` → `Unresolve`；`Pin` → `Unpin`；关 drawer；【停录】`Sign out`；【切换账号】Clinician。 | 【念】“Resolve and Unresolve are explicit collaboration states. Pin and Unpin provide feedback to the importance logic.” | Clinician 登录 |
| 02:28-03:00 | 【不要显示密码】【继续录制】【点击】Clinician `Edit` → `Save revision`；`History`；选 available earlier version 的 `Compare`；【等待】Before/After；必要时 `Revert` 一次。 | 【念】“History keeps full snapshots. Revert creates a new version and restores the prior content.” | 继续 context |
| 03:00-03:32 | 【继续录制】【点击】`Hot context`、`Warm index`、`Derived summary · not the original record`；点击 `View original record`；【等待】滚到 timeline；【念】UX-01。 | 【念】“The summary is labeled not the original record. An independent participant using the Simplified Chinese interface completed the glance task in approximately nine seconds without coaching.” | 【停录】切 Patient |
| 03:32-04:00 | 【不要显示密码】【切换账号】Sarah Patient；确认 `Patient view`、`Internal Glance View is hidden`；唯一 Voice 选项 `Synthetic patient follow-up · patient`。 | 【念】“The patient session is a different server-side projection. No clinical sample or generated-source control is exposed.” | 继续收尾 |
| 04:00-04:30 | 【继续录制】【点击】指向 synthetic-only disclosure；鼠标移开；【念】念完【停录】。 | 【念】“The deployed service uses HTTPS and PostgreSQL, and the demo data is synthetic. Voice remains Level C.” | 完整看视频 |

## 备用标记

- 【备用】`Live updates: Connected` 未出现：等待；仍失败时刷新一次。
- 【备用】当前卡片已 Accepted：选择另一张当前显示 `Suggested` 的 AI card。
- 【备用】已有 Voice result：直接展示，不要再次点击 `Process sample`。
- 【备用】没有 Suggested：删掉 `Accept`/`Reject` 镜头，不要声称 review。
- 【备用】`View original record` 只滚动 timeline：按实际行为描述，不说 exact-span panel。

## 安全标记

- 【不要显示密码】账号切换、密码框、浏览器自动填充全部离镜头。
- 不要显示 API key、数据库 URL、环境变量、Cookie、DevTools、Render Environment 或 provider console。
- 最终视频完成并通过 QA 前，不生成 PDF、ZIP、MANIFEST，不 push，不发邮件。
