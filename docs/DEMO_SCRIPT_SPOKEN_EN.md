# Nightingale final recording script: Chinese operation / English narration

目标时长：**4:30**  · 目标语速：**105–120 words per minute**  · 页面：**English**

角色顺序固定为 **Staff → Clinician → Patient**。操作提示用中文；网页按钮、字段和状态保留
实际 English label；需要念的内容只念每个镜头的英文旁白。全部内容使用 synthetic demo data。

密码、账号切换、加载等待和错误处理都在镜头外完成。不要录入或展示密码、API key、数据库
URL、环境变量、浏览器 storage、DevTools 或 provider console。页面上的 clinical note 原文
保持原始语言；不要临场翻译或改写它。

## 镜头 1：Staff 打开共享工作区

- **时间：** 00:00–00:24
- **角色：** Staff A
- **中文操作：** 镜头开始前在镜头外登录 Staff，选择 `Sarah Tan`，确认语言为 `English`。
  等待状态显示 `Up to date`，关闭 `Guide`、所有 drawer 和浏览器提示，把鼠标移到空白处。
- **应看到：** `Shared Care Note`、`Staff view`、`Sarah Tan`、共享照护工作区。
- **Requirement mapping：** `requirements.txt:3–5, 8, 14–15, 33–40`。
- **英文旁白：**

  > Nightingale brings a shared care record into one clear workspace. I begin as Staff with Sarah Tan.
  > The page separates care notes, suggestions, actions, and review history, so the team can see what
  > needs attention and why.

## 镜头 2：Staff Glance View 与来源

- **时间：** 00:24–01:06
- **角色：** Staff A
- **中文操作：** 在 `Glance View` 找到当前页面实际显示的 AI-assisted card。指出卡片上的
  内容、`Next step`、`Needs review` 或 `Reviewed`、item kind、`Risk flag`/`No risk flag` 和
  `Priority`。展开 `Why is this here?`，再点击 `Open source`，等待 `Original source` 和
  时间线中的高亮片段出现。
- **应看到：** 不超过六项；来源面板显示记录类型、日期、版本和高亮原文；`Technical details`
  默认折叠。如需说明实现细节，只在镜头外或技术材料中展开它。
- **Requirement mapping：** `requirements.txt:8–13, 25–26, 41–44, 87–89`。
- **英文旁白：**

  > Staff starts with Glance View. At a glance I can see the items needing attention, the next step,
  > current review status, item kind, risk flag, and priority. Priority organises the view; it is not
  > a medical risk score. I open the source of an AI-assisted note. The page takes me to the matching
  > timeline entry and keeps the highlighted passage tied to its original record version. This makes
  > the suggestion useful immediately while keeping the evidence easy to inspect. I can close the
  > source when I am done, and the record itself is unchanged.

## 镜头 3：Staff Voice note

- **时间：** 01:06–01:44
- **角色：** Staff A
- **中文操作：** 向下找到 `Voice note`。先确认 `About this example` 保持折叠；如没有已有
  result，播放 native audio，等待播放器时间前进后只点击一次 `Create care-note suggestion`。
  等待 `Suggestion status: Ready for review`，点击一个 transcript segment，再点击 `View
  source`。如果已有 result，直接展示，不重复处理。
- **应看到：** 音频、带时间戳的文字记录、可供审核的照护建议和来源跳转。不要打开录音、上传
  或配置页面。
- **Requirement mapping：** `requirements.txt:21–26, 45–48, 53`。
- **英文旁白：**

  > Here is a Voice note. I can review a pre-recorded care conversation, listen to the audio, and
  > follow the prepared timestamped transcript. Each segment is connected to a reviewable care-note
  > suggestion. I select a segment, move through the conversation, and open its source. The same
  > source and highlight path connects the conversation to the longitudinal record. The suggestion
  > is ready for clinician review.

## 镜头 4：Staff note、评论和 mention

- **时间：** 01:44–02:08
- **角色：** Staff A
- **中文操作：** 关闭来源面板，找到 `Staff note`，点击 `Edit`，输入 synthetic rehearsal
  sentence，点击 `Save revision`。然后点击 `Comments`，等待 drawer 出现，在 `Comment body`
  输入以 `@clinician` 开头的内容，从菜单选择 `@Clinician A`，点击 `Add comment`。
- **应看到：** 新版本、团队讨论和 `Mentions: @Clinician A`。只提交一次，不输入隐藏 ID。
- **Requirement mapping：** `requirements.txt:14–19, 37–40, 90–93`。
- **英文旁白：**

  > Back in Staff, I edit the existing Staff note and save a new revision. Then I add a team
  > discussion and mention Clinician A from the visible menu. The conversation stays attached to this
  > record, so follow-up context is available where the work happens.

## 镜头 5：协作状态与角色切换

- **时间：** 02:08–02:30
- **角色：** Staff A，随后切换 Clinician A
- **中文操作：** 在刚才的讨论中按页面实际状态完成一次 `Resolve`/`Unresolve`。在一张当前
  卡片上按页面实际状态完成一次 `Pin`/`Unpin`。关闭 drawer，停录，镜头外点击 `Sign out`
  并登录 Clinician。页面稳定后从 `Clinician view` 继续。
- **应看到：** 讨论状态和优先级反馈都被明确切换；只出现一次镜头外角色切换。
- **Requirement mapping：** `requirements.txt:15, 27–31, 90–93`。
- **英文旁白：**

  > Discussion states are explicit: Resolve and Unresolve show whether follow-up is complete. Pin and
  > Unpin let the team provide feedback to prioritisation. These actions are recorded separately from
  > clinical risk and source content.

## 镜头 6：Clinician review、Compare 与 Revert

- **时间：** 02:30–03:05
- **角色：** Clinician A
- **中文操作：** 在 `Clinician section` 点击 `Edit`，修改 synthetic plan sentence 并点击
  `Save revision`。打开 `History`，选择一个页面实际可用的 earlier version，点击 `Compare`，
  等待 `Before` 和 `After`。如 `Revert` 可用，点击一次并确认新版本出现；不写死版本号。
- **应看到：** 变化前后内容、可继续查看的历史版本和新的恢复版本。只有页面确实显示 review
  按钮时才执行该动作。
- **Requirement mapping：** `requirements.txt:16–19, 41–44, 90–93`。
- **英文旁白：**

  > Now I switch to Clinician. Clinician authority is focused on review and care planning. I edit the
  > Clinician section, open History, and compare an earlier version with the current one. Before and
  > After make the change visible. Revert restores earlier content by creating a new version, while
  > the full history remains available. A review action can confirm a suggestion without rewriting
  > its source.

## 镜头 7：历史上下文与 UX-01 evidence

- **时间：** 03:05–03:37
- **角色：** Clinician A
- **中文操作：** 关闭 History、Comments 和 Source。找到 `Historical context`，展开
  `How historical context is organised`，指出 `Recent context`、`Earlier context` 和
  `Historical summary`。点击任意 `View original record`，等待页面滚动到对应时间线位置。
  最后移开鼠标，念 UX-01 evidence。
- **应看到：** 历史摘要明确标注“不是原始记录”，并提供 `View original record`。
- **Requirement mapping：** `requirements.txt:10–13, 32, 41–44, 94–97`；UX-01 evidence 见
  `docs/evidence/ux_01_independent_test.md`。
- **英文旁白：**

  > Historical context brings recent information, earlier context, and concise historical summaries
  > together. A summary is labelled clearly and links to the original records. I can open an original
  > record to reach the relevant point in the timeline. This keeps a quick overview connected to
  > detail when I need to verify it. An independent participant using the Simplified Chinese interface
  > completed the glance task in approximately nine seconds without coaching.

## 镜头 8：Patient privacy 与 Patient Voice

- **时间：** 03:37–04:10
- **角色：** Sarah Patient
- **中文操作：** 停录，镜头外 `Sign out` 并登录 Patient。确认 `Patient view`、`Sarah Tan` 和
  `Your care summary`。展示患者可见时间线和 `Voice note`；如需要处理，播放 patient audio
  后只点击一次 `Create care-note suggestion`。不打开或寻找内部 source/control。
- **应看到：** 只有患者可见的摘要、指引和患者对话；没有内部 Glance、团队讨论、任务或临床
  审核控件。
- **Requirement mapping：** `requirements.txt:34–40, 45–48, 51–53`。
- **英文旁白：**

  > Finally, I switch to Patient. The patient view contains only information shared for the patient,
  > including care summaries, instructions, and the patient conversation. Internal Glance items, team
  > discussions, tasks, and clinician-only review controls stay out of this view. The patient Voice
  > note follows the same reviewable path: audio, timestamped transcript, and patient-facing care-note
  > context.

## 镜头 9：收尾

- **时间：** 04:10–04:30
- **角色：** 任一稳定的内部角色
- **中文操作：** 关闭所有 drawer，停在稳定的 English workspace；不要打开配置页。指向页面的
  synthetic-only disclosure 和 source/review boundary，鼠标移到空白处后念完旁白。
- **应看到：** HTTPS 应用页面保持稳定；没有密码、配置、日志或 provider console。
- **Requirement mapping：** `requirements.txt:50–54, 74–85, 99–104`。
- **英文旁白：**

  > Across the workspace, the principle is simple: make the next step visible, keep the original record
  > easy to verify, and preserve human review at every suggestion boundary. The demo uses synthetic
  > data and the deployed service provides the hosted HTTPS workspace. Nightingale turns shared care
  > context into a clear, traceable workflow.

## 录制前事实边界

- 版本号、卡片状态和当前 Voice result 以录制时页面为准，不在口播中硬编码。
- Voice 旁白只描述音频、准备好的时间戳文字记录、建议和来源链路；不把 prepared transcript
  当作 ASR 质量证据。
- 需要解释实现边界、provider、redaction、P95、部署安全或 Voice 级别时，放到 Technical
  Brief 或 evidence，不放进主旁白。
- 视频完成并完整观看通过 QA 前，不生成最终 PDF/ZIP/MANIFEST，不 push，不发邮件。
