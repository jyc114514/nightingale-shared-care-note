# Nightingale Real Clinic Demo State Prep

**用途：** 录制前状态检查，不是永久线上状态声明。
**唯一录制主控：** [`REAL_CLINIC_DEMO_RECORDING_MASTER_ZH_EN.md`](REAL_CLINIC_DEMO_RECORDING_MASTER_ZH_EN.md)
**部署地址：** `https://nightingale-shared-care-note.onrender.com`
**页面语言：** `English`
**数据边界：** synthetic data only

## 当前工程基线

- Git preparation commit: `e5f9339`。
- Render runtime: `4f4fc84c3451152e63135bd7fdd7b851bb43a1ea`。
- Release tag: `real-clinic-rc6` -> `4f4fc84`。
- Glance policy: `importance-v3-protected-first`。
- Backend: 194 passed; global application coverage 86.62%。
- Render Auto-Deploy: disabled。

## 镜头外登录

1. Staff A、Clinician A 和 Sarah Patient 均在镜头外完成登录。
2. 不读取密码文件、不代填密码、不把密码或 autofill 放进录屏。
3. 每次角色切换用 clean cut；切换后确认 `Sarah Tan`、`English` 和对应 role view。
4. 页面显示 `Record status: Up to date` 后，才开始新的 take。

## Staff 录制前检查

- [ ] `Staff A`、`Staff view`、`Sarah Tan` 可见。
- [ ] `Glance View` 不超过 6 项。
- [ ] `Conflicting allergy information` 位于第一项，且显示 protected attention/protected-first 说明。
- [ ] priority 与 medical risk 的文案仍然分开。
- [ ] `Review conflict` 能打开 `Allergy conflict review`。
- [ ] `View source: Allergy reported` 与 `View source: Allergy denied` 可见。
- [ ] Staff read-only 说明可见；不点击 clinical decision。
- [ ] `Comments` 和 `Assign task` 作为入口可以打开；不输入、不提交。
- [ ] 所有 drawer 关闭后再开始 Scene 2。

## 当前线上 rehearsal 事实（仅供拍摄决策）

本次只读 rehearsal 已确认：

- Glance 当前为 6 项，protected allergy conflict 为第一项。
- Conflict 两侧 source 都可以打开，并显示 immutable source panel。
- Staff 看不到可提交的 clinical adjudication 控件。
- `History` 可以打开并显示 current/earlier 结构；版本号不固定。
- `Comments` 可以打开，当前抽屉显示 `Team discussion` 和 `Comment body`。
- `Tasks` 可以打开，但当前数据含有多条 rehearsal-labelled 测试任务。
- Voice 可见 native audio、`Length: 24.0s` 和 `About this example`；说明准确写着 prerecorded synthetic conversation/prepared transcript。
- 当前 Voice sample 没有现成 result；本次 rehearsal 没有点击 `Create care-note suggestion`。
- `View original record` 按钮存在；在本次 AX-only 观察窗口中没有把新的 source panel 作为可确认结果，因此正式录制优先用 timeline/source 直接路径，不能声称该按钮打开 exact-span panel。

## 正式录制中的写操作策略

默认不需要写操作。除非录制前你人工确认有干净、可审查的状态，否则不要执行：

- `Create care-note suggestion`；
- `Save revision`；
- `Add comment`；
- `Create task`；
- Task status change；
- AI `Accept`/`Reject`；
- conflict adjudication；
- publication approval/publish。

若为了额外演示某个写操作而单独录制，必须先确认录屏已开始，每个写操作只执行一次，并在视频中
使用实际出现的版本和状态。不要为了匹配台本恢复 `v1 -> v2` 或制造固定 suggestion 状态。

## Clinician 复核

当前浏览器会话没有重新建立 Clinician 登录，因此正式录制前必须镜头外人工确认：

- [ ] `Clinician A`、`Clinician view`、`Sarah Tan`、`Up to date`。
- [ ] conflict drawer 显示两个 immutable sources 和可用 adjudication controls。
- [ ] `History`、`Compare`、`Before`、`After` 标签真实可见。
- [ ] `Prepare patient update` 显示当前真实 publication state。
- [ ] `Approve` 与 `Publish` 是独立动作；本台本默认只展示，不提交。
- [ ] 当前可审核 suggestion 才能决定是否做 Accept/Reject；不要把状态写死。

若任何一项未确认，在 Master 对应 Scene 保留 `REVERIFY AFTER MANUAL LOGIN BEFORE RECORDING`，
不使用旧截图替代。

## Patient 复核

当前浏览器会话没有重新建立 Patient 登录，因此正式录制前必须镜头外人工确认：

- [ ] `Patient view`、`Sarah Tan`、`Your care summary`。
- [ ] 只能看到 patient-facing/current-care projection。
- [ ] 不出现 Glance、conflict、internal source、comments、tasks、history、raw AI 或 Staff/Clinician controls。
- [ ] Voice 只展示 patient-safe synthetic sample。

若出现任意内部内容，立即停止录制并视为 P0 privacy blocker；不要靠裁剪或字幕遮盖。

## Tasks/Comments 的现场规则

当前 Tasks drawer 含 rehearsal-labelled test data，正式视频不要展示该 drawer 内容。可以保留
`Comments` 入口的短镜头；如果需要讲解 tasks、mentions 或 409，使用 Master 的
automated-test/evidence branch，不声称本次线上 take 创建了任务或评论。

## Voice 现场规则

- 这是 prerecorded synthetic audio + prepared transcript fixture。
- 不允许 microphone、upload、Whisper/ASR、diarization 或 live provider call。
- 如果页面只有 audio 和 About 文案，没有 result：保留文案和播放控件即可；不重复点击生成。
- 如果已有 result：直接展示已有 transcript/source；不重新生成。
- native audio button 可能显示浏览器本地化的 `播放`/`暂停`，以三角播放控件为准。

## 最后一分钟 checklist

- [ ] 浏览器只保留应用窗口；无密码、通知、DevTools、终端、Render dashboard。
- [ ] `English`、`Sarah Tan`、当前 role 正确；状态为 `Up to date`。
- [ ] 所有 drawer 关闭；鼠标停在空白处。
- [ ] protected conflict 仍在 Glance 第一项；六项上限未改变。
- [ ] 版本号和 suggestion status 已按页面实际状态确认，不照读旧台本固定值。
- [ ] Master、SRT、QA 和录屏软件已准备好。
- [ ] 原始视频文件在录制结束后只做存在性检查，不重命名、不转码、不压缩。

## Emergency fallback

| 情况 | 处理 |
| --- | --- |
| protected conflict 不在第一项 | 只刷新一次；仍不在则停录，不改数据。 |
| drawer 不打开 | 停当前 take，从该 Scene 开头重录；不连续点击。 |
| Tasks 有测试标题 | 关闭 drawer，改用 evidence branch。 |
| Voice 没有 result | 不创建 suggestion，展示 fixture boundary 或跳过。 |
| Clinician/Patient 登录失效 | 停录，镜头外人工登录。 |
| Patient 出现内部内容 | 立即停止；这是 privacy blocker。 |
| 页面长时间 loading | 等待稳定，不保留 loading 画面冒充成功。 |
| 页面语言错误 | 停录切换回 `English`。 |
