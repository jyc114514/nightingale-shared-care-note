# Nightingale 录制前 Demo State Prep

录制时以 [`DEMO_RECORDING_MASTER_ZH_EN.md`](DEMO_RECORDING_MASTER_ZH_EN.md) 为唯一操作主文件；本文件只负责录制前状态检查。

更新时间：2026-08-28  ·  部署地址：`https://nightingale-shared-care-note.onrender.com`
录制界面：`English`  ·  数据边界：只使用内置 synthetic data

这份文件是录制前的状态准备卡，不是永久状态声明。线上数据已经经过 synthetic rehearsal
修改，因此版本号、卡片状态、评论状态、任务状态和 Voice result 必须在每次录制前现场确认。
本文件只规定录制前的可见检查，不把某一次 cleanup、supersede 或 review API 的结果写成永久事实。

## 推荐登录顺序

1. **Staff A**：完成 Glance View、source、Voice 和协作入口。
2. **Clinician A**：完成 Clinician plan、History、Compare/Revert 和 Historical context。
3. **Sarah Patient**：完成患者可见内容和 Patient Voice。

账号切换使用镜头外 `Sign out` cut；密码框、自动填充和登录过程不出现在画面中。

## 已知的 rehearsal 基线

以下是上一轮 Staff-first dry run 记录的基线，只用于帮助准备，不得当作录制时的固定事实：

- Staff/Clinician/Patient 三个角色和 `Sarah Tan` 均已可用；内部页面预期显示 `Up to date`。
- Staff note 和 Clinician plan 已有多个版本；History 中通常可看到 earlier version、
  `Compare` 和 `Revert`。
- Glance 通常包含 `Needs review`、`Reviewed` 或其他可审查状态；录制前选择页面实际存在
  的卡片，不写死名称或状态。
- Staff note 的团队讨论、mention、`Reply`、`Resolve`/`Unresolve` 和 `Assign task` 可能
  已存在；录制前按页面实际状态决定是否执行。明显的测试标题（例如 `啊啊啊`、`12345`）
  不得出现在正式录制画面中。
- 内部 Voice 预期提供 clinical conversation，Patient 预期只提供 patient-facing conversation。
  已有 result 时直接展示，不重复处理。
- Historical context 预期包含 `Recent context`、`Earlier context` 和一个或多个
  `Historical summary`；来源按钮为 `View original record`。

## 录制前必须确认

1. 页面语言为 `English`，患者下拉框为 `Sarah Tan`。
2. 关闭 `Guide`、`Source`、`Comments`、`History`、`Task` drawer、通知和 DevTools。
3. Staff/Clinician 页面状态为 `Up to date`；如果显示连接中断，等待或镜头外刷新后再录。
4. Glance 至少有一张适合展示的卡片；记录实际出现的 status、action、risk 和 priority。
5. Glance 保持最多 6 项；不修改 six-item cap，不添加 `Show more`。
6. 不应有两个无区分价值的重复 Glance item；如果看到重复内容，先核对 source、version 和
   provenance，再决定是否由有权限的维护流程标记后续项为替代项。无法确认最终 API 状态时，
   只做现场目视清理检查，不写死具体 highlight 已完成 cleanup。
7. 没有 active rehearsal task；已有 task 必须明确显示 Done；明显测试标题不得保留。
8. 至少保留两张 Clinician 可审核的 AI suggestion：第一张用于 Accept，第二张用于 Reject。
9. 录制前不要点击这两张卡片的 Accept/Reject；只在正式录制已经开始且页面稳定后各点击一次。
10. Voice 如需处理，clinical 与 patient sample 各最多点击一次 `Create care-note suggestion`。
11. History 选择当前列表中的 earlier version，不假定 `v1 → v2`。
12. 所有输入均为 synthetic rehearsal sentence；clinical note 原文不翻译、不改写。

## 录制中会修改什么

| 操作 | 是否修改 synthetic state | 规则 |
| --- | --- | --- |
| `Open source` / `Close source` | 否 | 可重复；关闭后检查 `patient` 保留、`highlight` 清除 |
| `Create care-note suggestion` | 是 | 每个 Voice sample 最多一次 |
| `Save revision` | 是 | Staff、Clinician 各按脚本执行一次 |
| `Add comment` | 是 | 只提交一次 synthetic comment |
| `Create task` | 是 | title 固定为 `Review synthetic follow-up plan`；只点击一次；分配给 Clinician A |
| Task `Open` → `In progress` | 是 | Clinician 只切换一次；不要说 Accept task；`Done` 仅在明确计划时执行 |
| AI suggestion `Accept` | 是 | Clinician 只点击一次；等待 `Reviewed`，卡片保留、source 不变 |
| AI suggestion `Reject` | 是 | Clinician 只点击一次；等待 suggestion 离开 active Glance，source 不删除 |
| `Resolve` / `Unresolve` | 是 | 完成一组来回切换 |
| `Pin` / `Unpin` | 可选 | 不在本轮主路径；只有时间足且状态稳定时展示，不为匹配旧台本重复写入 |
| `Revert` | 是 | 只点击一次；不要直接修改数据库 |
| `View original record`、History、Compare | 否 | 可重复；按实际画面描述 |

## 不要点击或展示

- 不打开环境变量、密码、API key、Render Environment、browser storage、Cookie、DevTools
  或外部服务控制台。
- 不运行 reset、delete 或 seed 来恢复旧版本号。
- 不把 `View original record` 说成精确来源面板；它的作用是导航到对应时间线位置。
- 不把准备好的 Voice transcript 说成 ASR 质量证据。

## Task 与 AI review 的两套状态机

录制前逐项确认并在视频中保持用词一致：

| 对象 | 操作 / 状态 | 视频中必须怎么说 |
| --- | --- | --- |
| Assigned task | `Create task` 后立即 active：`Open` → `In progress` → `Done` | Assigned tasks become active immediately and move through Open, In progress, and Done. |
| AI highlight suggestion | Clinician 的 `Accept` / `Reject` | Accept 后是 `Reviewed` 并留在 Glance；Reject 后离开 active Glance；两者都不覆盖原始 source |

不要说 task is accepted by default、Accept task、Reject task，也不要把 task 的 `Reviewed`
presentation 当成 task acceptance。

## Final cleanup gate（只做可见检查）

- [ ] Glance 仍最多 6 项；没有明显测试标题或两个无区分价值的重复 item。
- [ ] 旧 active task 已不存在；若仍存在，必须显示 Done；不要为了录制删除 task。
- [ ] 至少两张卡在 Clinician 页面实际显示 `Accept` / `Reject`；若卡片已经 `Reviewed` 或
      已离开 Glance，重新选择当前可审核候选，不修改数据库来匹配台本。
- [ ] 新 task 的唯一标题为 `Review synthetic follow-up plan`，唯一 assignee 为 Clinician A。
- [ ] 正式录制前不消耗 Accept/Reject；Create task、Accept、Reject 各只执行一次。
- [ ] 不在 State Prep 中记录密码、Cookie、highlight UUID、patient UUID 或内部标识。

## 收尾

- 页面保持 `English`，角色和患者范围正确，所有 drawer 关闭。
- 视频完成后完整观看一次，再填写 [`DEMO_VIDEO_QA.md`](DEMO_VIDEO_QA.md)。
- 视频通过 QA 前不更新 PDF、ZIP、MANIFEST，不 push，不发邮件。
