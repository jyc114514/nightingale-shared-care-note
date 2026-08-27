# Nightingale 视频 QA

本文件用于最终视频导出后检查。视频完成前保持未勾选；只有完整观看成片并核对字幕后，才可
把它标记为 ready for final packaging。

## 结构检查

- [ ] 总时长在 4–5 分钟内，目标约 4:30。
- [ ] 英文口播约 105–120 words per minute，句子清晰、适合非英语母语者朗读。
- [ ] 字幕使用 [`DEMO_SUBTITLES_EN.srt`](DEMO_SUBTITLES_EN.srt)，English only，cue 不重叠，
      时间与成片一致。
- [ ] 镜头顺序为 Staff → Clinician → Patient；两次账号切换均为镜头外 cut。
- [ ] 真实 English button label 在发生操作时清晰可读。
- [ ] 画面没有密码框、自动填充、API key、数据库 URL、Cookie、browser storage、环境变量、
      DevTools、Render Environment 或 provider console。

## 产品路径检查

- [ ] Staff 开场显示 `Glance View`、内容、`Next step`、status、item kind、risk 和 priority。
- [ ] `Why is this here?` 的说明清楚表达 priority 不是 medical risk score。
- [ ] `Open source` 打开 `Original source`，并导航到时间线中的正确高亮原文。
- [ ] `Original source` 主区域只展示记录类型、日期、版本和原文；`Technical details` 默认
      折叠。
- [ ] Voice 使用 `Voice note`、音频、prepared timestamped transcript、建议和来源链路；
      不把 prepared transcript 称作 ASR 质量证据。
- [ ] Staff `Edit`/`Save revision`、`Comments`、mention、`Resolve`/`Unresolve` 和
      Clinician `History`/`Compare`/`Revert` 的按钮标签与实际画面一致。
- [ ] Historical context 显示 `Recent context`、`Earlier context`、`Historical summary`，
      并用 `View original record` 导航到时间线。
- [ ] Patient 画面显示 `Your care summary` 和患者可见内容；没有内部 Glance、团队讨论、
      任务或临床审核控件。

## 文案边界检查

- [ ] 主 UI 没有 `Level-C`、`mock transcript fixture`、provider/model 名称或原始 provider
      错误码。
- [ ] 主 Source panel 没有 Python code-point、SHA-256 或内部 source ID；需要时只在明确的
      `Technical details` 折叠区查看。
- [ ] Voice 的 `About this example`（如展开）准确说明：这是预录 synthetic care
      conversation 和 prepared timestamped transcript。
- [ ] clinical note 原文没有被自动翻译或改写。
- [ ] 所有建议仍明确处于可审核路径，不能被旁白说成自主医疗结论。

## UX-01 证据检查

- [ ] 口播准确包含：
      “An independent participant using the Simplified Chinese interface completed the glance task
      in approximately nine seconds without coaching.”
- [ ] 不补写 participant name、role、viewport、device、clinical background 或 English
      proficiency。
- [ ] 不说 all users、clinical users、statistically validated 或 multiple participants。
- [ ] 文档中的 UX-01 状态为 passed，但视频不把一次测试包装成正式 usability study。

## 事实和安全检查

- [ ] Staff → Clinician → Patient 顺序清楚，版本号和 suggestion 状态没有被错误写死。
- [ ] 视频只口播已在脚本中保留的产品价值和已有部署事实；技术边界留在 Technical Brief
      或 evidence。
- [ ] 没有把 Voice prepared transcript 说成 ASR、diarization 或模型质量证明。
- [ ] 没有展示真实患者数据、凭据、配置值或原始日志。

## 通过标准

完整观看视频、字幕同步、三角色顺序、真实按钮、产品文案和安全边界全部正确后，才将视频
标记为 `ready for final packaging`。通过前不生成最终 PDF、ZIP 或 MANIFEST，不 push，不发
邮件。
