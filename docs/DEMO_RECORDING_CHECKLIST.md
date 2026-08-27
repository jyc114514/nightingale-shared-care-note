# Nightingale 录制前后 Checklist

录制时以 [`DEMO_RECORDING_MASTER_ZH_EN.md`](DEMO_RECORDING_MASTER_ZH_EN.md) 为唯一操作主文件；本文件保留为 checklist 参考。

## 录制前

- [ ] 打开现有 Render HTTPS 地址，等待服务唤醒。
- [ ] 页面选择 `English`；患者选择 `Sarah Tan`。
- [ ] 按 **Staff → Clinician → Patient** 准备三个 session。
- [ ] 账号切换在镜头外完成；密码框、自动填充和地址栏敏感信息永远不出现在画面中。
- [ ] Staff/Clinician 等待状态显示 `Up to date`。
- [ ] 关闭 `Guide`、`Source`、`Comments`、`History`、`Task` drawer、通知和 DevTools。
- [ ] 阅读 [`DEMO_STATE_PREP_ZH.md`](DEMO_STATE_PREP_ZH.md)，现场确认版本、卡片状态和 Voice result。
- [ ] 确认 Voice 需要时只使用内置 synthetic sample；已有 result 时不重复提交。

## 录制中

- [ ] 按 [`DEMO_RECORDING_MASTER_ZH_EN.md`](DEMO_RECORDING_MASTER_ZH_EN.md) 的中文动作执行。
- [ ] 英文旁白只念 Master Runbook 中与 cue 对应的内容；SRT 使用同一文件的派生版本。
- [ ] 保留真实 English label，例如 `Open source`、`Close source`、`Compare`、`Revert`。
- [ ] `Original source` 的 `Technical details` 默认折叠；主画面保持产品信息简洁。
- [ ] Voice 只展示音频、prepared timestamped transcript、建议和来源链路；不把 transcript
      说成 ASR 质量证据。
- [ ] `@Clinician A` 只通过可见 mention menu 选择；不输入隐藏 user ID。
- [ ] `Compare` 使用页面当前可见的 earlier version；不假定固定版本号。
- [ ] 只有当前确实显示 `Accept`/`Reject` 时才录制 review 动作。
- [ ] `View original record` 如实描述为导航到原始时间线位置。
- [ ] 每个镜头念旁白前让目标结果可见；旁白中鼠标移到空白处。

## 录制后

- [ ] 完整观看视频一次。
- [ ] 检查时长为 4–5 分钟，目标 4:30；口播约 105–120 wpm。
- [ ] 检查字幕与 Staff-first 顺序完全匹配，并包含独立中文 UX-01 结果。
- [ ] 确认没有错误版本号、错误 suggestion 状态或未验证按钮被剪进视频。
- [ ] 确认三类角色、患者隐私、Voice scope 和 HTTPS 边界均按事实呈现。
- [ ] 确认没有密码、API key、数据库 URL、Cookie、环境变量、browser storage 或原始日志。
- [ ] 将结果填写到 [`DEMO_VIDEO_QA.md`](DEMO_VIDEO_QA.md)。
- [ ] 视频通过 QA 后，才启动最终 PDF/ZIP/MANIFEST/push 任务。

## UX-01 当前证据

UX-01 已由一名匿名独立参与者使用 Simplified Chinese 界面完成：约 9 秒、无 coaching、
priority/action-state/risk-versus-ranking/source affordance 四项均正确。role 和 viewport
没有单独记录；不要在视频中补猜。
