# Nightingale 录制前 Demo State Prep

更新时间：2026-08-27  ·  部署地址：`https://nightingale-shared-care-note.onrender.com`
录制界面：`English`  ·  数据边界：只使用内置 synthetic data

这份文件是录制前的状态准备卡，不是永久状态声明。线上数据库已经经过 synthetic rehearsal
修改，因此版本号、卡片状态、评论状态和 Voice result 必须在每次录制前现场确认。

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
  已存在；录制前按页面实际状态决定是否执行。
- 内部 Voice 预期提供 clinical conversation，Patient 预期只提供 patient-facing conversation。
  已有 result 时直接展示，不重复处理。
- Historical context 预期包含 `Recent context`、`Earlier context` 和一个或多个
  `Historical summary`；来源按钮为 `View original record`。

## 录制前必须确认

1. 页面语言为 `English`，患者下拉框为 `Sarah Tan`。
2. 关闭 `Guide`、`Source`、`Comments`、`History`、`Task` drawer、通知和 DevTools。
3. Staff/Clinician 页面状态为 `Up to date`；如果显示连接中断，等待或镜头外刷新后再录。
4. Glance 至少有一张适合展示的卡片；记录实际出现的 status、action、risk 和 priority。
5. Voice 如需处理，clinical 与 patient sample 各最多点击一次 `Create care-note suggestion`。
6. History 选择当前列表中的 earlier version，不假定 `v1 → v2`。
7. 所有输入均为 synthetic rehearsal sentence；clinical note 原文不翻译、不改写。

## 录制中会修改什么

| 操作 | 是否修改 synthetic state | 规则 |
| --- | --- | --- |
| `Open source` / `Close source` | 否 | 可重复；关闭后检查 `patient` 保留、`highlight` 清除 |
| `Create care-note suggestion` | 是 | 每个 Voice sample 最多一次 |
| `Save revision` | 是 | Staff、Clinician 各按脚本执行一次 |
| `Add comment` | 是 | 只提交一次 synthetic comment |
| `Resolve` / `Unresolve` | 是 | 完成一组来回切换 |
| `Pin` / `Unpin` | 是 | 完成一组来回切换 |
| `Revert` | 是 | 只点击一次；不要直接修改数据库 |
| `View original record`、History、Compare | 否 | 可重复；按实际画面描述 |

## 不要点击或展示

- 不打开环境变量、密码、API key、Render Environment、browser storage、Cookie、DevTools
  或外部服务控制台。
- 不运行 reset、delete 或 seed 来恢复旧版本号。
- 不把 `View original record` 说成精确来源面板；它的作用是导航到对应时间线位置。
- 不把准备好的 Voice transcript 说成 ASR 质量证据。

## 收尾

- 页面保持 `English`，角色和患者范围正确，所有 drawer 关闭。
- 视频完成后完整观看一次，再填写 [`DEMO_VIDEO_QA.md`](DEMO_VIDEO_QA.md)。
- 视频通过 QA 前不更新 PDF、ZIP、MANIFEST，不 push，不发邮件。
