# Nightingale 最终录制脚本：中文操作 / English narration

目标时长：**4:30**
目标语速：**105-120 words per minute**
网页界面：English
角色顺序：**Staff → Clinician → Patient**
数据：只使用 synthetic data

这是一份录制 runbook，不是最终视频。独立 UX-01 结果已单独记录；本脚本不把录制 rehearsal
冒充 usability study。密码输入、账号切换、加载等待和错误处理都在镜头外完成。不要录入
或展示密码、API key、数据库 URL、环境变量、浏览器 storage、DevTools 或 provider console。

## 镜头 1：Staff 打开共享工作区

- **时间：** 00:00-00:23
- **当前角色：** Staff A
- **起始状态：** 已在部署地址登录；`English` 已选；`Sarah Tan` 已选；页面显示
  `Live updates: Connected`。
- **中文操作：**
  1. 确认页面语言为 `English`。
  2. 确认 `Select patient` 为 `Sarah Tan`。
  3. 把鼠标移到页面空白处，停顿半秒后开始旁白。
- **预期结果：** 页面显示 `Shared Care Note`、`Staff view`、Sarah Tan 和 synthetic-only
  trust boundary。
- **失败备用：** 如果显示 reconnecting，等待一次 `Connected`；仍未恢复时刷新一次，
  不要继续录制错误状态。
- **此步骤会修改：** No。
- **Requirement mapping：** `requirements.txt:3-5, 8, 14-15, 33-40`。
- **英文旁白：**

  > Nightingale is a shared care note for synthetic data. It is a trust system, not an autonomous
  > medical system. I start as Staff with one patient workspace and an English interface. The page
  > keeps human notes, system suggestions, patient context, and review metadata separate.

## 镜头 2：Staff Glance View 与 AI source

- **时间：** 00:23-01:04
- **当前角色：** Staff A
- **起始状态：** `Top Card` 和 `What needs attention now` 可见；录制前重新确认当前仍有
  `Suggested` AI card。
- **中文操作：**
  1. 在 `Top Card` 中指出内容、action、status、item kind 和 risk label。
  2. 指出 `Why ranked? Ranking priority, not a medical risk score.`。
  3. 在当前仍为 `Suggested` 的 AI nurse card 中点击 `Open source`。
  4. 等待 `Immutable source` 和 Timeline exact mark 出现；旁白时让 source panel 保持打开。
- **预期结果：** 看到 `Immutable source`、当前 immutable version、Python code-point offset
  和与来源一致的 `<mark>`。
- **失败备用：** 如果原卡片已经变成 Accepted，选择另一张当前仍显示 `Suggested` 的 AI card；
  不要口播固定卡片名称或固定版本号。
- **此步骤会修改：** No；打开 source 只修改视图和 query。
- **Requirement mapping：** `requirements.txt:8-13, 25-26, 41-44, 87-89`。
- **英文旁白：**

  > The Top Card is designed for a fast glance. It has no more than six source-linked items. Each
  > item shows content, an action, a status, an item kind, and a risk label. The ranking explanation
  > is clear: ranking priority is not a medical risk score. This AI-scribed nurse entry is still a
  > suggestion. Open source jumps to the exact timeline entry. The source panel names an immutable
  > version, the source reference, and Python code-point offsets. The highlight is the stored quote.

## 镜头 3：Staff Voice Level-C fixture

- **时间：** 01:04-01:42
- **当前角色：** Staff A
- **起始状态：** `Ambient Voice Prototype` 可见；内部页面应只显示
  `Synthetic nurse follow-up · clinical`；没有 session result，或已在镜头外准备好 result。
- **中文操作：**
  1. 确认披露文字包含 `Prerecorded synthetic audio only` 和 `Mock transcript fixture`。
  2. 如尚未有结果，点击 native audio 播放控件，等待约 3 秒，再点击一次 `Process sample`。
  3. 等待 `Voice session status: completed`。
  4. 点击显示 8 秒起点的 transcript segment。
  5. 点击 `Open generated source`，等待 immutable source 出现。
  6. 鼠标移到 source panel 空白处；停顿后念 disclaimer。
- **预期结果：** 显示 mock transcript、3 个 fixture timestamp、`ASR confidence unavailable
  for fixture`、system-authored suggestion 和 exact source；没有 microphone/upload。
- **失败备用：** 如果已有 result，直接展示，不要再次点击 `Process sample`；如果处理失败，
  只记录 safe failure 并删掉整个 Voice 镜头，不要改口声称成功。
- **此步骤会修改：** 如点击 `Process sample`，Yes；每个 fixture 最多一次。
- **Requirement mapping：** `requirements.txt:21-26, 45-48, 53`。
- **英文旁白：**

  > This is a Level-C architecture and demo path. The audio is prerecorded synthetic signal data,
  > and the timestamps are fixture timestamps. The transcript is a mock fixture because local ASR
  > was unavailable in this environment, so confidence is unavailable. This optional prototype uses
  > prerecorded synthetic audio and a mock timestamped transcript. It demonstrates audio-to-summary
  > provenance, but it does not claim live ASR or diarization. The suggestion remains system-authored
  > and requires clinician review.

## 镜头 4：Staff note、评论和 @mention

- **时间：** 01:42-02:06
- **当前角色：** Staff A
- **起始状态：** `Staff note` 可见；先关闭 source panel；鼠标停在 note 操作区外。
- **中文操作：**
  1. 点击 Staff note 的 `Edit`。
  2. 输入一段 synthetic rehearsal sentence；不要使用真实患者信息。
  3. 点击 `Save revision`，等待当前版本更新。
  4. 点击 `Comments`；等待 contextual drawer 出现。
  5. 在 `Comment body` 输入以 `@clinician` 结尾的 synthetic comment。
  6. 选择 `@Clinician A · clinician`，再点击 `Add comment`。
- **预期结果：** Staff note 出现新 revision；Comments drawer 显示 root comment 和
  `Mentions: @Clinician A`。
- **失败备用：** 如果 drawer 没出现，刷新一次后重新点击 `Comments`；如果 mention 菜单没
  出现，删掉 mention 子步骤，不要输入隐藏 user ID。
- **此步骤会修改：** Yes；增加 Staff revision 和一条 internal comment。
- **Requirement mapping：** `requirements.txt:14-19, 37-40, 90-93`。
- **英文旁白：**

  > Staff can edit the existing Staff note and add an internal comment. This deployed UI has no
  > new-note composer, so I state that replacement directly. I select Clinician A from the mention
  > menu. The mention is stored as metadata, and the discussion remains inside the clinic scope.

## 镜头 5：Resolve、Pin 与角色切换

- **时间：** 02:06-02:28
- **当前角色：** 先 Staff A，随后切换 Clinician A
- **起始状态：** Staff comment drawer 中已有刚才的评论；录制准备时确认浏览器没有密码
  输入画面。
- **中文操作：**
  1. 点击 `Resolve`，确认状态改变。
  2. 点击 `Unresolve`，确认回到 open/unresolved 状态。
  3. 在当前 Glance card 点击 `Pin`，再点击 `Unpin`。
  4. 关闭所有 drawer。
  5. 停录，点击 `Sign out`；离开镜头完成 Clinician 登录。
  6. 页面恢复稳定后再继续录制，不要展示账号密码。
- **预期结果：** 评论状态和 pin feedback 都完成一次显式切换；角色切换只产生一个视频 cut。
- **失败备用：** 如果当前 comment 已经是 resolved，按页面实际显示的反向按钮操作一次；
  如果卡片已有 `Unpin`，不要再次 Pin，改为只解释当前 feedback 状态。
- **此步骤会修改：** Resolve/Unresolve、Pin/Unpin 会写 synthetic metadata；角色切换本身 No。
- **Requirement mapping：** `requirements.txt:15, 27-31, 90-93`。
- **英文旁白：**

  > Resolve and Unresolve are explicit collaboration states. Pin and Unpin provide feedback to the
  > importance logic, but one click is not proof of learning. The next view uses a separate
  > Clinician role, so the audit action is visible without sharing Staff authority.

## 镜头 6：Clinician review、Compare 与 Revert

- **时间：** 02:28-03:00
- **当前角色：** Clinician A
- **起始状态：** `Clinician view`、`Clinician section` 和当前 timeline 可见；版本号以录制前
  实际页面为准。
- **中文操作：**
  1. 点击 `Clinician section` 的 `Edit`。
  2. 修改为 synthetic plan sentence，点击 `Save revision`。
  3. 点击 `History`，从列表中选择任意一个 available earlier version 的 `Compare`。
  4. 等待 `Diff`、`Before` 和 `After` 出现；让 History panel 保持打开。
  5. 点击该 earlier version 对应的 `Revert` 一次。
  6. 确认页面显示一个新的 revert version，且 earlier history rows 仍保留。
  7. 如果存在当前 `Suggested` card，可点击 `Accept` 一次；若没有，删除该子步骤。
- **预期结果：** Before/After 清楚可见；Revert 恢复 earlier content 并创建新 version；历史
  不被删除。
- **失败备用：** 如果 Compare 或 Revert 不可用，停在 History 画面并解释当前状态；不要
  硬编码 `v1 → v2`，也不要直接改数据库。若没有 Suggested card，不声称 Accept/Reject。
- **此步骤会修改：** Yes；增加 Clinician revision、revert version，Accept 也会写 review metadata。
- **Requirement mapping：** `requirements.txt:16-19, 41-44, 90-93`。
- **英文旁白：**

  > Now I switch to Clinician. I edit only the Clinician section. History keeps full snapshots. I
  > choose an available earlier version and compare it with the current version. Before and After
  > make the change visible. Revert creates a new version and restores the prior content, while the
  > earlier history stays. A review action can accept a suggestion without rewriting its source.

## 镜头 7：Clinician historical context 与 UX-01 evidence

- **时间：** 03:00-03:32
- **当前角色：** Clinician A
- **起始状态：** `Historical context` 可见；所有 History/Comments/Source drawer 已关闭。
- **中文操作：**
  1. 指向 `Hot context`、`Warm index` 和 `Derived summary · not the original record`。
  2. 点击任意当前可见的 `View original record`。
  3. 等待页面滚动到对应 canonical timeline entry；不要把它说成 exact-span panel。
  4. 鼠标停在 timeline 空白处后念 UX-01 evidence。
- **预期结果：** 页面到达原始 Patient summary 或 Patient instruction timeline entry；derived
  summary 的 source-of-truth 文案仍可见。
- **失败备用：** 如果滚动目标不在视口，使用正常页面滚动找到同一日期的 timeline entry；
  不要声称出现 immutable source panel。
- **此步骤会修改：** No。
- **Requirement mapping：** `requirements.txt:10-13, 32, 41-44, 94-97`；UX-01 evidence in
  `docs/evidence/ux_01_independent_test.md`。
- **英文旁白：**

  > Longitudinal context combines current entries with older history. Hot context, the Warm index,
  > and the derived cold summary have different jobs. The summary is labeled not the original
  > record. View original record scrolls to the canonical Patient summary; it is not an exact-span
  > panel. An independent participant using the Simplified Chinese interface completed the glance task in approximately nine seconds without coaching.

## 镜头 8：Patient privacy 与 Patient Voice

- **时间：** 03:32-04:00
- **当前角色：** Sarah Patient
- **起始状态：** 离镜头完成第二次 `Sign out`；Patient 页面为 English、Sarah Tan、`Patient view`。
- **中文操作：**
  1. 指向 `Internal Glance View is hidden`。
  2. 展示 Patient-facing timeline；不要点击内部按钮，因为它们不应存在。
  3. 打开 `Ambient Voice Prototype`，确认唯一选项为 `Synthetic patient follow-up · patient`。
  4. 如尚未处理且需要展示结果，播放 native audio，并只点击一次 `Process sample`；否则展示
     已有 result。
  5. 确认没有 `Open generated source`，鼠标移到空白处停录。
- **预期结果：** Internal Glance、Comments、Assign task、History、Clinical sample 和
  generated-source control 均不可见；Patient Voice 只保留 patient-safe fixture。
- **失败备用：** 如果 Patient 会话不可用，删除整个镜头，不要从 Clinical 页面推断患者隐私。
- **此步骤会修改：** 仅在首次处理 patient fixture 时 Yes；每个 fixture 最多一次。
- **Requirement mapping：** `requirements.txt:34-40, 45-48, 51-53`。
- **英文旁白：**

  > Finally, I switch to Patient. This is a different server-side projection. The internal Glance
  > View, comments, tasks, and history controls are absent. Only patient-facing records and the
  > patient Voice fixture appear. The patient sample is prerecorded synthetic audio, with a mock
  > timestamped transcript. No clinical sample or generated-source control is exposed.

## 镜头 9：最终边界收尾

- **时间：** 04:00-04:30
- **当前角色：** 不要求固定角色；优先使用已稳定的 English Clinician/Staff 页面
- **起始状态：** 所有 drawer 已关闭；鼠标移到空白处；画面中没有账号、密码或配置。
- **中文操作：**
  1. 指向 synthetic-only disclosure。
  2. 停顿半秒后念完最后一段，念完停录。
- **预期结果：** 画面保持在 HTTPS 应用页面；不打开 Render Environment、PDF、ZIP 或
  provider console。
- **失败备用：** 如果页面出现登录或错误状态，直接结束视频并重新录制收尾，不要剪接成
  未验证的成功状态。
- **此步骤会修改：** No。
- **Requirement mapping：** `requirements.txt:50-54, 74-85, 99-104`。
- **英文旁白：**

  > The deployed service uses HTTPS and PostgreSQL, and the demo data is synthetic. The warm-path
  > P95 remains below three hundred milliseconds in the repository benchmark. DeepSeek is only an
  > optional redacted adapter; no live call is shown. Voice remains Level C. This project makes no
  > clinical compliance claim. The final video must be reviewed before packaging.

## 录制中不要声称

不要声称新建 note、手动选中文本创建 highlight、双浏览器 SSE、live 409 conflict、task 完整
生命周期、live DeepSeek、microphone、upload、Whisper inference、diarization 或 clinical
validation。它们要么没有在本次部署 dry run 中可靠复现，要么超出 Level-C 边界。
