# Nightingale 最终录制 Operator Runbook

这是录制时的主操作文件。所有操作提示均为中文；网页按钮、字段和状态保留实际 English
label；需要念的内容保持 English。角色顺序固定为 **Staff → Clinician → Patient**，只做两次
镜头外账号切换。

通用规则：

- 页面始终选择 `English`，患者始终选择 `Sarah Tan`。
- 密码输入全部镜头外完成；【不要显示密码】。
- 等待时先让预期结果出现，再继续念旁白。
- 每个镜头念旁白时把鼠标移到空白处；旁白结束再移动鼠标。
- 不要打开 DevTools、Render Environment、browser storage、password manager、API key、
  数据库 URL 或 provider console。
- 当前数据库不是 pristine seed；版本和 suggestion 状态必须录制前现场确认。

## 镜头 1：Staff 打开共享工作区

时间：00:00-00:23
当前角色：`Staff A`
当前页面：部署地址的 `Staff view` / Sarah Tan
录制状态：【继续录制】

操作前检查：

- 【不要显示密码】；登录和账号准备已在镜头外完成。
- 页面显示 `English`，患者选择为 `Sarah Tan`。
- 等待 `Live updates: Connected`。
- 关闭 `Guide`、DevTools、通知和所有 drawer。

操作：

1. 确认页面标题为 `Shared Care Note`。
2. 确认页面显示 `Staff view`。
3. 确认页面显示 `Live updates: Connected`。
4. 将鼠标放到页面空白处。
5. 停顿半秒后开始念旁白。

你应该看到：

- Sarah Tan 的共享工作区。
- synthetic-only trust boundary。
- 人工记录、system suggestion、patient context 和 review metadata 被分开呈现。

念下面这段英文：

> Nightingale is a shared care note for synthetic data. It is a trust system, not an autonomous
> medical system. I start as Staff with one patient workspace and an English interface. The page
> keeps human notes, system suggestions, patient context, and review metadata separate.

对应 requirement：

- Shared care note、real-time workspace、RBAC：`requirements.txt:3-5, 8, 14-15, 33-40`。

如果失败：

- 显示 reconnecting 时等待 `Live updates: Connected`。
- 等待后仍不稳定时刷新一次；不要录制错误状态。

此步骤会修改：

- No。只读。

## 镜头 2：Staff Glance View 与 AI source

时间：00:23-01:04
当前角色：`Staff A`
当前页面：`Top Card` / `What needs attention now`
录制状态：【继续录制】；source panel 打开后保持打开

操作前检查：

- 确认当前仍存在至少一张 `Suggested` AI card。
- 不要预先假定卡片名字、priority 或 version。
- 鼠标先停在 Top Card 外侧。

操作：

1. 在 `Top Card` 指出一张卡片的 content、action、status、item kind 和 risk。
2. 指出文字 `Why ranked? Ranking priority, not a medical risk score.`。
3. 找到当前仍显示 `Suggested` 的 AI nurse card。
4. 点击该卡片的 `Open source`。
5. 【等待】`Immutable source` panel 和 Timeline exact mark 出现。
6. 将鼠标移到 source panel 空白处。
7. 念旁白时保持 source panel 可见。

你应该看到：

- `Top Card` 最多六项。
- card 上同时显示 action、status、item kind、risk 和 source。
- `Immutable source`、当前 immutable version、source reference 和 Python code-point offset。
- Timeline 中的 `<mark>` 与 source quote 一致。

如果失败：

- 当前卡片已经 Accepted 时，换另一张当前显示 `Suggested` 的 AI card。
- 不要把某一张卡片的名称或版本号写死在口播里。
- 如果 source 没出现，等待最多 2 秒；仍失败就停录该镜头并记录。

此步骤会修改：

- No。`Open source` 只改变视图和 query；不要点击 review 按钮。

念下面这段英文：

> The Top Card is designed for a fast glance. It has no more than six source-linked items. Each
> item shows content, an action, a status, an item kind, and a risk label. The ranking explanation
> is clear: ranking priority is not a medical risk score. This AI-scribed nurse entry is still a
> suggestion. Open source jumps to the exact timeline entry. The source panel names an immutable
> version, the source reference, and Python code-point offsets. The highlight is the stored quote.

对应 requirement：

- Glance、entry metadata、AI source、exact provenance：`requirements.txt:8-13, 25-26, 41-44, 87-89`。

## 镜头 3：Staff Voice Level-C fixture

时间：01:04-01:42
当前角色：`Staff A`
当前页面：`Ambient Voice Prototype`
录制状态：【继续录制】；source panel/Voice result 按旁白需要保持可见

操作前检查：

- 内部页面只显示 `Synthetic nurse follow-up · clinical`。
- 看到 `Prerecorded synthetic audio only` 和 `Mock transcript fixture`。
- 如果已有 Voice result，不要再次处理；直接展示已有 result。

操作：

1. 如没有 Voice result，点击 native audio 的 play control。
2. 【等待】播放约 3 秒，确认播放器时间向前走。
3. 如没有 Voice result，点击一次 `Process sample`。
4. 【等待】`Voice session status: completed`。
5. 点击显示 8 秒起点的 transcript segment。
6. 点击 `Open generated source`。
7. 【等待】`Immutable source` 出现。
8. 将鼠标移到空白处。
9. 停顿后念 Voice disclaimer。

你应该看到：

- mock transcript、fixture timestamps 和 `ASR confidence unavailable for fixture`。
- system-authored suggestion，且需要 clinician review。
- exact source provenance。
- 页面没有 microphone 或 upload control。

如果失败：

- 已有 result 时不要再次点击 `Process sample`。
- 处理失败时只记录 safe failure，并从最终视频删除本镜头；不要声称成功。
- 播放器无法播放时不使用 `download` 或其他替代动作。

此步骤会修改：

- 首次点击 `Process sample` 时 Yes：创建一个 Voice session、AI entry 和 source。
- 每个 fixture 最多处理一次。

念下面这段英文：

> This is a Level-C architecture and demo path. The audio is prerecorded synthetic signal data,
> and the timestamps are fixture timestamps. The transcript is a mock fixture because local ASR
> was unavailable in this environment, so confidence is unavailable. This optional prototype uses
> prerecorded synthetic audio and a mock timestamped transcript. It demonstrates audio-to-summary
> provenance, but it does not claim live ASR or diarization. The suggestion remains system-authored
> and requires clinician review.

对应 requirement：

- AI-scribed source、Voice Level C、synthetic/privacy boundary：`requirements.txt:21-26, 45-48, 53`。

## 镜头 4：Staff note、评论和 @mention

时间：01:42-02:06
当前角色：`Staff A`
当前页面：Timeline 中的 `Staff note` 和 contextual Comments drawer
录制状态：【继续录制】；comment drawer 在提交后保持短暂可见

操作前检查：

- 关闭 source panel。
- 确认只使用 synthetic sentence。
- 【不要显示密码】；当前角色仍是 Staff。

操作：

1. 找到 Timeline 的 `Staff note`。
2. 点击 `Edit`。
3. 输入 synthetic rehearsal sentence。
4. 点击 `Save revision`。
5. 【等待】当前版本更新。
6. 点击 `Comments`。
7. 【等待】Comments drawer 出现。
8. 在 `Comment body` 输入以 `@clinician` 结尾的 synthetic comment。
9. 选择 `@Clinician A · clinician`。
10. 点击 `Add comment`。
11. 【等待】`Mentions: @Clinician A` 出现。
12. 鼠标移到 drawer 空白处后念旁白。

你应该看到：

- Staff note 出现一个新 revision。
- Comments drawer 显示 root comment。
- 页面显示 `Mentions: @Clinician A`。
- 当前部署 UI 没有 new-note composer。

如果失败：

- drawer 没出现时刷新一次，再重新点击 `Comments`。
- mention 菜单没出现时删掉 mention 子步骤；不要输入隐藏 user ID。
- 没有 new-note composer 时照实说“编辑既有 Staff note”。

此步骤会修改：

- Yes：增加一个 Staff revision 和一条 internal comment。
- 只提交一次，不重复点击 `Add comment`。

念下面这段英文：

> Staff can edit the existing Staff note and add an internal comment. This deployed UI has no
> new-note composer, so I state that replacement directly. I select Clinician A from the mention
> menu. The mention is stored as metadata, and the discussion remains inside the clinic scope.

对应 requirement：

- Inline collaboration、revision、clinic scope、Scenario B：`requirements.txt:14-19, 37-40, 90-93`。

## 镜头 5：Resolve、Pin 与第一次角色切换

时间：02:06-02:28
当前角色：先 `Staff A`，然后切换 `Clinician A`
当前页面：Comments drawer、Top Card、账号切换页
录制状态：【继续录制】→【停录】→【切换账号】

操作前检查：

- Comment drawer 中存在刚才的 comment。
- 确认没有密码框进入画面。

操作：

1. 点击 `Resolve`。
2. 【等待】comment 状态改变。
3. 点击 `Unresolve`。
4. 在当前 Glance card 点击 `Pin`。
5. 再点击 `Unpin`。
6. 关闭所有 drawer。
7. 将鼠标移到空白处，念旁白。
8. 【停录】点击 `Sign out`。
9. 【不要显示密码】在镜头外登录 Clinician。
10. 【继续录制】等页面显示 `Clinician A`、`Clinician view` 和 `Live updates: Connected`。

你应该看到：

- Resolve/Unresolve 完成一次来回切换。
- Pin/Unpin 完成一次 feedback 切换。
- 只出现一次角色切换 cut。

如果失败：

- comment 已 resolved 时按实际显示的反向按钮操作一次。
- card 已显示 `Unpin` 时不要再次 Pin，按实际状态解释。
- 登录切换不稳定时停录，等 Clinician 页面稳定后重录本镜头。

此步骤会修改：

- Resolve/Unresolve 和 Pin/Unpin 会写 synthetic metadata。
- 账号切换本身 No。

念下面这段英文：

> Resolve and Unresolve are explicit collaboration states. Pin and Unpin provide feedback to the
> importance logic, but one click is not proof of learning. The next view uses a separate
> Clinician role, so the audit action is visible without sharing Staff authority.

对应 requirement：

- Collaboration states、importance feedback、RBAC：`requirements.txt:15, 27-31, 90-93`。

## 镜头 6：Clinician review、Compare 与 Revert

时间：02:28-03:00
当前角色：`Clinician A`
当前页面：`Clinician view` / `Clinician section` / History
录制状态：【继续录制】；History panel 在 Compare/Revert 时保持打开

操作前检查：

- 确认页面显示 `Clinician A`、`Clinician view`、`Sarah Tan`。
- 不要假设当前版本编号；先看页面。
- 确认当前存在至少一个 available earlier version。

操作：

1. 点击 `Clinician section` 的 `Edit`。
2. 输入 synthetic plan sentence。
3. 点击 `Save revision`。
4. 点击 `History`。
5. 选择列表中任意一个 available earlier version 的 `Compare`。
6. 【等待】`Diff`、`Before` 和 `After` 出现。
7. 点击同一 earlier version 对应的 `Revert` 一次。
8. 【等待】新的 revert version 出现。
9. 确认 earlier history rows 仍可见。
10. 如果当前存在 `Suggested` card，可点击一次 `Accept`；没有就删掉该子步骤。
11. 鼠标移到 History 空白处后念旁白。

你应该看到：

- Before/After 清楚显示本次 plan 修改。
- Revert 恢复 earlier content，并创建新的 version。
- earlier history rows 未被删除。
- Accept 只在页面确实显示该按钮时录制。

如果失败：

- Compare 或 Revert 不可用时停在 History 画面，照实解释。
- 不要硬编码 `v1 → v2`。
- 没有 Suggested card 时不要声称 Accept/Reject。

此步骤会修改：

- Yes：增加 Clinician revision 和 revert version。
- Accept 若执行，也会写 review metadata。

念下面这段英文：

> Now I switch to Clinician. I edit only the Clinician section. History keeps full snapshots. I
> choose an available earlier version and compare it with the current version. Before and After
> make the change visible. Revert creates a new version and restores the prior content, while the
> earlier history stays. A review action can accept a suggestion without rewriting its source.

对应 requirement：

- Revision history、diff、revert、trust review：`requirements.txt:16-19, 41-44, 90-93`。

## 镜头 7：Clinician historical context 与 UX-01 evidence

时间：03:00-03:32
当前角色：`Clinician A`
当前页面：`Historical context` / Timeline
录制状态：【继续录制】

操作前检查：

- 关闭 History、Comments 和 Source drawer。
- 确认 `Historical context` 可见。
- 鼠标先停在 context panel 外侧。

操作：

1. 指向 `Hot context`。
2. 指向 `Warm index`。
3. 指向 `Derived summary · not the original record`。
4. 点击任意当前可见的 `View original record`。
5. 【等待】页面滚动到 canonical timeline entry。
6. 不要寻找不存在的 exact-span panel。
7. 鼠标移到 timeline 空白处。
8. 念 UX-01 英文旁白。

你应该看到：

- Hot/Warm/derived cold 的分层说明。
- 页面滚动到原始 Patient summary 或 Patient instruction timeline entry。
- source-of-truth 文案仍然可见。

如果失败：

- 目标不在视口时使用正常页面滚动找到同一日期的 timeline entry。
- 不要把 `View original record` 说成 exact-span provenance panel。

此步骤会修改：

- No。只读。

念下面这段英文：

> Longitudinal context combines current entries with older history. Hot context, the Warm index,
> and the derived cold summary have different jobs. The summary is labeled not the original
> record. View original record scrolls to the canonical Patient summary; it is not an exact-span
> panel. An independent participant using the Simplified Chinese interface completed the glance
> task in approximately nine seconds without coaching.

对应 requirement：

- Longitudinal context、data decay representation、独立 UX-01：`requirements.txt:10-13, 32, 41-44, 94-97`；
  UX evidence 见 `docs/evidence/ux_01_independent_test.md`。

## 镜头 8：Patient privacy 与 Patient Voice

时间：03:32-04:00
当前角色：`Sarah Patient`
当前页面：`Patient view` / patient Voice panel
录制状态：【停录】→【切换账号】→【继续录制】

操作前检查：

- 【停录】点击 `Sign out`。
- 【不要显示密码】在镜头外登录 Patient。
- 确认 `Sarah Patient`、`Patient view`、`Sarah Tan`。
- 等页面稳定；不要从 Clinician 页面推断 Patient 结果。

操作：

1. 指向 `Internal Glance View is hidden`。
2. 展示 Patient-facing timeline。
3. 确认没有 `Top Card`、`Comments`、`Assign task` 或 `History`。
4. 打开 `Ambient Voice Prototype`。
5. 确认唯一选项为 `Synthetic patient follow-up · patient`。
6. 如果尚未有 result，播放 native audio。
7. 如需展示处理结果，只点击一次 `Process sample`。
8. 【等待】completed result。
9. 确认没有 `Open generated source`。
10. 鼠标移到空白处后念旁白。

你应该看到：

- Patient-facing entries only。
- Internal Glance、internal collaboration controls、Clinical sample 和 generated source 不可见。
- Patient Voice 只保留 patient-safe fixture。

如果失败：

- Patient 会话不可用时删除整个镜头。
- 不要从内部页面推断患者隐私结果。
- Voice 已有 result 时不要重复 `Process sample`。

此步骤会修改：

- 只有首次处理 patient fixture 时 Yes；每个 fixture 最多一次。

念下面这段英文：

> Finally, I switch to Patient. This is a different server-side projection. The internal Glance
> View, comments, tasks, and history controls are absent. Only patient-facing records and the
> patient Voice fixture appear. The patient sample is prerecorded synthetic audio, with a mock
> timestamped transcript. No clinical sample or generated-source control is exposed.

对应 requirement：

- Patient RBAC、patient Voice、privacy/security：`requirements.txt:34-40, 45-48, 51-53`。

## 镜头 9：最终边界收尾

时间：04:00-04:30
当前角色：任一稳定的内部 English workspace
当前页面：应用主页面；所有 drawer 已关闭
录制状态：【继续录制】→【停录】

操作前检查：

- 不要打开 Render Environment、PDF、ZIP、MANIFEST 或 provider console。
- 确认画面没有账号、密码、key、数据库 URL 或 raw logs。

操作：

1. 指向 synthetic-only disclosure。
2. 指向页面中可见的 source/trust boundary（不要打开配置页）。
3. 将鼠标移到空白处。
4. 停顿半秒后念最后一段。
5. 旁白结束后【停录】。

你应该看到：

- HTTPS 应用页面保持稳定。
- 口播只引用已有 PostgreSQL、P95、fixture 和 redaction evidence。
- 没有 live DeepSeek 或 full Ambient Voice 画面。

如果失败：

- 页面出现登录、错误或配置页时直接停录，重新录制收尾。
- 不要剪接成未验证的成功状态。

此步骤会修改：

- No。只读。

念下面这段英文：

> The deployed service uses HTTPS and PostgreSQL, and the demo data is synthetic. The measured
> warm-path P95 remains below the three-hundred-millisecond target in the repository benchmark.
> DeepSeek is only an optional redacted adapter; no live call is shown. Voice remains Level C.
> This project does not claim clinical compliance, production PHI capture, or a final video until
> the recording is reviewed.

对应 requirement：

- Technical constraints、deliverables、scoring boundary：`requirements.txt:50-54, 74-85, 99-104`。

## 录制后

1. 完整观看视频一次。
2. 使用 [`DEMO_VIDEO_QA.md`](DEMO_VIDEO_QA.md) 逐项检查。
3. 确认没有旧的 UX pending 文案、错误版本号或未验证按钮。
4. 视频通过 QA 前，不生成 PDF、ZIP、MANIFEST，不 push，不发邮件。
