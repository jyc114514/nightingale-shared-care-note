# Nightingale 视频 QA

本文件用于实际视频导出后检查。本阶段没有录制最终视频。

## 结构检查

- [ ] 总时长为 4-5 分钟，目标 4:30。
- [ ] 英文口播约 105-120 words per minute，句子短、易于非英语母语者朗读。
- [ ] 字幕使用 `DEMO_SUBTITLES_EN.srt`，English only，cue 不重叠，最后时间与成片一致。
- [ ] 镜头顺序是 Staff → Clinician → Patient。
- [ ] 两次角色切换均为镜头外 cut；画面没有密码框。
- [ ] 每个操作发生时，真实 English button label 清晰可读。

## 产品路径检查

- [ ] Staff 开场显示 `Top Card`、内容、action、status、item kind、risk 和 ranking disclaimer。
- [ ] Staff 的当前 Suggested AI card 可通过 `Open source` 到达 exact immutable span。
- [ ] Source panel 显示 immutable version、source reference 和 code-point offset；`Close source`
      后 query 行为正确。
- [ ] Voice 只显示 prerecorded synthetic audio、`Mock transcript fixture`、timestamps 和
      `ASR confidence unavailable for fixture`。
- [ ] Voice 旁白/字幕包含准确 disclaimer：
      “This optional prototype uses prerecorded synthetic audio and a mock timestamped transcript.
      It demonstrates audio-to-summary provenance, but it does not claim live ASR or diarization.”
- [ ] Staff edit 使用现有 `Staff note`；明确说明没有 new-note composer。
- [ ] Comments 显示 `@Clinician A` mention metadata 和 `Resolve`/`Unresolve`。
- [ ] Clinician 使用当前可见 earlier version 做 `Compare` 和 `Revert`，不写死版本编号。
- [ ] Historical context 显示 Hot/Warm/derived cold，并如实描述 `View original record` 的滚动行为。
- [ ] Patient 显示 `Patient view`、`Internal Glance View is hidden`，且无 internal controls/Clinical sample。

## UX-01 证据检查

- [ ] 口播/字幕准确包含：
      “An independent participant using the Simplified Chinese interface completed the glance task
      in approximately nine seconds without coaching.”
- [ ] 不补写 participant name、role、viewport、device、clinical background 或 English proficiency。
- [ ] 不说 all users、clinical users、statistically validated、English test 或 multiple participants。
- [ ] 不把 UX-01 表述为待完成、未独立证明或待人工签字。
- [ ] UX-01 状态在文档中为 passed，但没有包装成正式 usability study。

## Trust / security 检查

- [ ] 不把 fixture transcript 说成 ASR transcript。
- [ ] 不声称 microphone、upload、Whisper inference、diarization、live DeepSeek 或 production PHI audio。
- [ ] 不出现 password、API key、database URL、Cookie、environment value、browser storage 或 raw logs。
- [ ] 不打开 Render Environment、provider console 或配置文件。
- [ ] HTTPS、PostgreSQL、redaction boundary 和 P95 只按已有证据口播，不虚构现场数字。

## 通过标准

只有在完整观看视频、字幕同步、三角色顺序正确、所有边界表述准确后，才将视频标记为
ready for final packaging。视频完成并通过 QA 前，不生成 PDF、ZIP 或 MANIFEST，也不 push。
