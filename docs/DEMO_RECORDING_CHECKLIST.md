# Nightingale 录制前后 Checklist

## 录制前

- [ ] 打开现有 Render HTTPS 地址，等待服务唤醒。
- [ ] 页面选择 `English`；患者选择 `Sarah Tan`。
- [ ] 按 **Staff → Clinician → Patient** 准备三个 session。
- [ ] 账号切换在镜头外完成；密码框永远不出现在画面中。
- [ ] 等待内部页面显示 `Live updates: Connected`。
- [ ] 关闭 `Guide`、DevTools、浏览器通知和 password-manager popup。
- [ ] 关闭所有 `Source`、`Comments`、`History`、`Task` drawer。
- [ ] 读取 [DEMO_STATE_PREP_ZH.md](DEMO_STATE_PREP_ZH.md)，重新确认当前版本和 Suggested 卡片。
- [ ] 确认 `LLM_PROVIDER=fixture`、`VOICE_PROVIDER=fixture` 的公开 fixture disclosure；不要打开环境配置页。
- [ ] 确认当前数据库不是 pristine seed；录制时不要硬编码版本号。

## 录制中

- [ ] 按 [DEMO_OPERATOR_RUNBOOK_ZH.md](DEMO_OPERATOR_RUNBOOK_ZH.md) 的中文动作逐行执行。
- [ ] 英文旁白只念脚本中的 `【英文旁白】`，不要临场翻译临床 note 原文。
- [ ] 保留真实 English UI label，例如 `Open source`、`Close source`、`Compare`、`Revert`。
- [ ] Staff 必须先出现；两个角色切换都用 `Sign out` 后的镜头外 cut。
- [ ] 只在需要时处理 Voice；Clinical/Patient fixture 各最多点击一次 `Process sample`。
- [ ] Voice 必须展示 prerecorded synthetic、mock transcript、fixture timestamps 和 confidence unavailable。
- [ ] 不要声称 live ASR、Whisper、diarization、speaker labels、microphone、upload 或 production PHI audio。
- [ ] `@Clinician A` 只通过可见 mention menu 选择；不要输入隐藏 user ID。
- [ ] `Compare` 选择当前可见的 earlier version；不要假定 `v1 → v2`。
- [ ] 只有当前真的有 `Accept`/`Reject` 时才录制 review 动作；没有就删掉该镜头。
- [ ] `View original record` 如实描述为滚动到 canonical timeline entry，不说成 exact-span panel。
- [ ] 每个镜头念旁白前让预期结果可见；旁白中鼠标移到空白处，避免遮挡文字。

## 录制后

- [ ] 完整观看视频一次。
- [ ] 检查时长在 4-5 分钟内，目标 4:30；口播约 105-120 wpm。
- [ ] 检查字幕与 Staff-first 顺序完全匹配，并包含独立中文 UX-01 结果。
- [ ] 确认片中没有把 UX-01 表述为待完成、未独立证明或待人工签字。
- [ ] 确认没有错误版本号、错误 suggestion 状态或未验证按钮被剪进视频。
- [ ] 确认三类场景、患者隐私、Voice disclaimer 和 HTTPS/PostgreSQL 边界均清楚。
- [ ] 确认没有密码、API key、数据库 URL、Cookie、环境变量、browser storage 或原始日志。
- [ ] 将结果填写到 [DEMO_VIDEO_QA.md](DEMO_VIDEO_QA.md)，视频未通过 QA 前不打包。
- [ ] 视频通过 QA 后，才启动最终 PDF/ZIP/MANIFEST/push 任务。

## UX-01 当前证据

UX-01 已由一名匿名独立参与者使用 Simplified Chinese 界面完成：约 9 秒、无 coaching、
priority/action-state/risk-versus-ranking/source affordance 四项均正确。role 和 viewport
没有单独记录；不要在视频中补猜。
