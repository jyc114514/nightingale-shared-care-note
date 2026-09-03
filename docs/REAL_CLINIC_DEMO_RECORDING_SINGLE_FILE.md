# Nightingale Final Real Clinic Demo

## Single-file recording guide

**正式录制时只看这一份 Markdown。**
不要打开其他 Markdown、SRT、HTML、Traceability、QA、终端、DevTools 或 Render dashboard。
所有中文操作、等待条件、英文台词、字幕 cue、下一步和 fallback 都写在当前 Beat 中。
字幕文字已经内嵌；录制时不需要查看字幕文件，录完后再交给剪辑软件导入。

目标：**7:22 / 706 English words / 95-110 WPM / English UI / Staff -> Clinician -> Patient**
当前状态：**FINAL DEMO MATERIALS READY FOR RECORDING; VIDEO QA PENDING**

---

# 第一部分：录制前准备

## 1. 五分钟 checklist

- [ ] 打开现有页面：`https://nightingale-shared-care-note.onrender.com`。
- [ ] Chrome zoom 100%；录屏画面目标 1440x900，至少保持清晰的桌面比例。
- [ ] 页面语言为 `English`，患者为 `Sarah Tan`。
- [ ] Staff、Clinician、Patient 登录都在镜头外完成；密码页和自动填充不能入镜。
- [ ] 麦克风、系统音频、录屏软件窗口和存储空间检查通过。
- [ ] 记住录屏软件的 Start/Stop 热键；录制前不要点击网页写按钮。
- [ ] 浏览器通知、DevTools、终端、Render dashboard 全部关闭。
- [ ] `Guide`、`Source`、`Comments`、`History`、`Tasks` drawer 初始全部关闭。
- [ ] Staff 起始页显示 `Staff A`、`Staff view`、`Sarah Tan`、`Record status: Up to date`。
- [ ] Staff Glance 不超过 6 项，`Conflicting allergy information` 预期位于第一项。
- [ ] 当前线上 Tasks drawer 有 rehearsal 数据；Tasks 不进入正式主流程。
- [ ] Clinician/Patient 的角色切换均在停录后完成。
- [ ] 如果出现登录页、密码框、通知、配置、DevTools 或错误状态，立即停录。

## 2. 当前线上状态

- protected allergy conflict 预期在 Staff Glance 第一项。
- Glance 上限保持 6；不添加 `Show more`，不删除卡片来匹配旧截图。
- `Why is this here?` 应说明 protected-first，并区分 workflow priority 与 medical risk。
- Publication 可能显示 `Draft`；按当前页面实际状态说，不强行推进。
- Tasks drawer 含 rehearsal-labelled 数据，不打开给评委看，也不清理线上 Tasks。
- Comments/Tasks 只是协作入口，不是本次视频主镜头。
- 页面状态、版本号和 suggestion status 与旧截图不同，优先相信当前页面。
- 不为了匹配台词修改线上 clinical truth、版本、任务、评论或 review 状态。

## 3. 录制边界

- 所有内容均为 synthetic prototype data。
- `protected attention policy` 是排序保护，不是 medical risk probability。
- `importance` 是 workflow display ordering，不是 calibrated confidence。
- `immutable source` 和 `clinician review` 是信任边界。
- `Accept is not Publish`；publication 是 portal-only gate，不声称 WhatsApp/SMS delivery。
- Voice 只称为 prerecorded synthetic audio + prepared timestamped transcript。
- Unsupported input 会 abstain；不声称 general clinical NLP。
- Benchmark gap 作为 supplementary disclosed gap 保留，不阻止录制，也不声称 hosted latency 已通过。

明确未实现或仍为 bounded slice：phone-only onboarding、Clinic B provisioning、真实三语 ASR、
live consult 内实时 allergy detection、durable provider queue/replay、external delivery receipt、
general medication interpretation、FHIR/HIPAA compliance、unbiased learning 和 real-time
collaborative editing。不要在视频中使用 `production-ready`、`clinically validated`、`live ASR`、
`diarization`、`trilingual understanding` 或 `medical risk probability` 作为未经限定的声明。

---

# 第二部分：一页式总流程

| Scene | 时间 | 当前角色 | 起始位置 | 第一个点击 | 本段核心功能 | 英文口播第一句 | 结束位置 | 是否停录切换角色 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 00:00-00:32 | Staff | Stable workspace | 无 | 产品定位与 synthetic boundary | Nightingale is a shared care workspace... | Glance 入口 | 否 |
| 2 | 00:32-01:26 | Staff | Glance View | `Why is this here?` | 六项上限、protected-first、priority/risk 分离 | I start with Glance View... | Protected card explanation | 否 |
| 3 | 01:26-02:12 | Staff | Protected conflict card | `Review conflict` | 双 immutable source 与 exact span | I open the conflict... | 两个 source 均已查看 | 否 |
| 4 | 02:12-03:40 | Staff -> Clinician | Timeline / conflict | `Comments`（只读） | Staff 边界、Clinician authority、History/Compare | Staff can inspect both sources... | Clinician History/Compare | 是，Scene 4 中段 |
| 5 | 03:40-04:32 | Clinician | Timeline entry | `Prepare patient update` | Draft、dosage gate、Approve/Publish 分离 | From a timeline entry... | Publication Draft | 否 |
| 6 | 04:32-05:13 | Staff/Clinician | Voice 或 evidence 页面 | native play（可选） | Voice fixture、redaction/provider failure boundary | The Voice panel uses... | 稳定 product/evidence page | 否 |
| 7 | 05:13-05:53 | Patient | Patient view | 无 | Patient projection 与隐私边界 | I switch to Patient... | Patient safe projection | 是，Scene 7 前 |
| 8 | 05:53-06:34 | Brief / stable page | limitation 页面 | 无 | SURVIVES/PARTIAL/DOES NOT 与 abstention | The remaining gaps... | Limitations 结束 | 否 |
| 9 | 06:34-07:22 | Stable workspace | README/source/evidence | 无 | tests、coverage、PostgreSQL、Render 和诚实收尾 | The repository includes... | 最后一句后停录 | 否，最终停止 |

---

# 第三部分：正式拍摄跟读版

## Scene 1 — Opening and product thesis

### Beat 01 — Open the stable Staff workspace

**时间：** `00:00-00:16.5`
**当前角色：** Staff
**录制：** 开始

### ① 先做这些操作

1. 确认页面显示 `Staff A` 和 `Staff view`。
2. 确认患者为 `Sarah Tan`。
3. 确认 `Record status: Up to date`。
4. 鼠标缓慢移到页面标题空白处。
5. 等顶部状态稳定 2 秒后开始念 Cue 01。

### ② 等看到这些再念

- 必须出现 `Shared Care Note`。
- 必须出现 Staff 身份、Sarah Tan 和 `Up to date`。
- 页面不能处于 loading 或登录状态。

### ③ 现在念

**Cue 01 · 00:00:00,000 --> 00:00:08,000**
> Nightingale is a shared care workspace that keeps longitudinal records, review decisions, and audience boundaries on one patient page.

**Cue 02 · 00:00:08,500 --> 00:00:16,500**
> This recording uses synthetic data, a hosted HTTPS workspace, and a deliberate separation between sources, suggestions, and publication.

### ④ 念完立刻做什么

- Cue 02 结束后停留 1 秒。
- 继续录制，准备进入 Beat 02。

### ⑤ 出问题时

- 出现登录页或状态不是 `Up to date`：立即停录，镜头外重新登录后从 Beat 01 重录。

### ⑥ 本段对应

`Overall / Direct UI`

---

### Beat 02 — State the trust thesis

**时间：** `00:17-00:32`
**当前角色：** Staff
**录制：** 继续

### ① 先做这些操作

1. 不点击网页按钮。
2. 让标题和 trust boundary 保持在画面内。
3. 鼠标移到空白处。
4. Cue 03 开始念，Cue 04 结束后再准备滚动。

### ② 等看到这些再念

- 标题、synthetic context 和 human-review boundary 可读。
- 没有 toast、loading 或 drawer。

### ③ 现在念

**Cue 03 · 00:00:17,000 --> 00:00:25,000**
> A ranked item is a workflow aid, not a diagnosis, and it never silently replaces a human-authored record.

**Cue 04 · 00:00:25,500 --> 00:00:32,000**
> I will move from Staff to Clinician to Patient, with role changes outside the camera frame.

### ④ 念完立刻做什么

- Cue 04 结束后平滑向下滚动。
- 继续录制，进入 Beat 03。

### ⑤ 出问题时

- 有 drawer 遮挡标题：先关闭 drawer；不要改数据或刷新多次。

### ⑥ 本段对应

`Overall / Direct UI`

---

## Scene 2 — Protected Glance

### Beat 03 — Enter Glance View

**时间：** `00:32.5-00:54`
**当前角色：** Staff
**录制：** 继续

### ① 先做这些操作

1. 平滑向下滚动到 `Glance View`。
2. 等 `What needs attention now` 出现。
3. 鼠标指向 `6 items need attention`。
4. 鼠标移到第一张 card 空白处。
5. 六项稳定后开始念 Cue 05。

### ② 等看到这些再念

- `Glance View` 和至少一张 card 完整出现。
- `Next step`、status、item kind、risk context 和 `Priority` 可读。
- 页面不能出现超过 6 项或 loading。

### ③ 现在念

**Cue 05 · 00:00:32,500 --> 00:00:43,000**
> I start with Glance View, where content, status, next action, risk context, and priority appear together.

**Cue 06 · 00:00:43,500 --> 00:00:54,000**
> The screen is deliberately capped at six items, keeping the first clinical read compact instead of overwhelming.

### ④ 念完立刻做什么

- Cue 06 结束后停留 1 秒。
- 继续录制，进入 Beat 04。

### ⑤ 出问题时

- Glance 不是 6 项或为空：只刷新一次；仍不对就停录，从 Scene 2 重录。

### ⑥ 本段对应

`Requirements 9-12 / Direct UI`

---

### Beat 04 — Show protected-first ranking

**时间：** `00:54.5-01:26`
**当前角色：** Staff
**录制：** 继续

### ① 先做这些操作

1. 指向 `Conflicting allergy information`。
2. 指向 `Needs clinician review`。
3. 展开同一张卡的 `Why is this here?`。
4. 鼠标指向 `Protected attention` 和 protected-first explanation。
5. 说明 priority 位置后开始念 Cue 07。

### ② 等看到这些再念

- protected conflict 位于第一项。
- 普通高 priority 卡片仍在下方。
- `Protected attention` 和 priority disclaimer 可读。

### ③ 现在念

**Cue 07 · 00:00:54,500 --> 00:01:04,000**
> The protected allergy conflict appears first even when ordinary candidates carry a higher numerical priority.

**Cue 08 · 00:01:04,500 --> 00:01:15,000**
> Protected attention is a separate selection policy; it does not turn a workflow number into a medical risk score.

**Cue 09 · 00:01:15,500 --> 00:01:26,000**
> The explanation makes the ranking auditable: protected candidates first, then deterministic priority, time, and resource ordering.

### ④ 念完立刻做什么

- Cue 09 结束后停留 2 秒。
- 点击 `Review conflict`，进入 Beat 05。

### ⑤ 出问题时

- protected conflict 不在第一项：立即停录；不要删卡、改分数或制造新数据。

### ⑥ 本段对应

`Scenario 13 / Scenario 14 / Scenario 15 / Direct UI`

---

## Scene 3 — Dual-source provenance

### Beat 05 — Inspect both conflict assertions

**时间：** `01:26.5-01:49`
**当前角色：** Staff
**录制：** 继续

### ① 先做这些操作

1. 点击 `Review conflict` 一次。
2. 等右侧 `Allergy conflict review` drawer 完整打开。
3. 鼠标指向 `ALLERGY REPORTED`。
4. 鼠标指向 `ALLERGY DENIED`。
5. 两侧 source 都可读后开始念 Cue 10。

### ② 等看到这些再念

- `Allergy conflict review` 标题出现。
- `View source: Allergy reported` 和 `View source: Allergy denied` 出现。
- Staff read-only boundary 出现。

### ③ 现在念

**Cue 10 · 00:01:26,500 --> 00:01:37,000**
> I open the conflict to inspect two contradictory assertions without editing or resolving either source.

**Cue 11 · 00:01:37,500 --> 00:01:49,000**
> The reported allergy and the denied allergy remain separate, with their own authors, timestamps, and verification states.

### ④ 念完立刻做什么

- Cue 11 结束后停留 2 秒。
- 点击第一个 `View source`，进入 Beat 06。

### ⑤ 出问题时

- drawer 未完整打开：停当前 take，刷新后从 Beat 05 重录；不要连续点击。

### ⑥ 本段对应

`Scenario 13 / Direct UI`

---

### Beat 06 — Follow exact immutable provenance

**时间：** `01:49.5-02:12`
**当前角色：** Staff
**录制：** 继续

### ① 先做这些操作

1. 点击 `View source: Allergy reported` 一次。
2. 等 `Original source` 和黄色 exact span 出现。
3. 鼠标指向 source version 和 highlighted quote。
4. 回到 conflict drawer，点击另一侧 `View source` 一次。
5. 第二个 source 稳定后开始念 Cue 12。

### ② 等看到这些再念

- `Original source`、日期、版本和原文出现。
- `immutable`（读作 **ih-MYOO-tuh-bul**）的 source version 可被画面核对。
- `provenance`（读作 **PROV-uh-nuhns**）的 exact highlighted span 稳定。
- Technical details 保持折叠。

### ③ 现在念

**Cue 12 · 00:01:49,500 --> 00:02:00,000**
> Each assertion links to an immutable source version and an exact highlighted span, rather than a copied approximation.

**Cue 13 · 00:02:00,500 --> 00:02:12,000**
> The source panel keeps the originating version distinct from the record's current version, so later edits remain explainable.

### ④ 念完立刻做什么

- Cue 13 结束后停留 2 秒。
- 关闭 source，再关闭 conflict drawer，进入 Beat 07。

### ⑤ 出问题时

- source 或 exact span 不出现：停本段，保留已显示的 source，不用 current text 冒充原文。

### ⑥ 本段对应

`Scenario 13 / Scenario 16 / Direct UI`

---

## Scene 4 — Authority, collaboration, and history

### Beat 07 — Show collaboration entry points without writing

**时间：** `02:12.5-02:31.5`
**当前角色：** Staff
**录制：** 继续

### ① 先做这些操作

1. 找到当前 Timeline entry 的 `Comments`。
2. 点击 `Comments` 一次。
3. 等 contextual drawer 出现。
4. 指向 `Team discussion`、`Comment body` 和关闭按钮。
5. 不输入文字；看到 drawer 稳定后开始念 Cue 14。

### ② 等看到这些再念

- Comments drawer 完整出现。
- `Team discussion` 和 `Comment body` 可读。
- 页面没有新 comment、new task 或 rehearsal title。

### ③ 现在念

**Cue 14 · 00:02:12,500 --> 00:02:21,500**
> Staff can inspect both sources, but the clinical decision controls stay unavailable in this role.

**Cue 15 · 00:02:22,000 --> 00:02:31,500**
> Comments and Tasks are collaboration entry points; opening a drawer does not change clinical truth or create a task.

### ④ 念完立刻做什么

- Cue 15 结束后关闭 Comments。
- 不打开 Tasks 内容；停录并进入角色切换卡。

### ⑤ 出问题时

- Tasks drawer 出现 rehearsal-labelled 数据：立即关闭，跳过任务画面，继续角色切换。

### ⑥ 本段对应

`Scenario 10 / Requirements 14-15 / Direct UI + limitation`

---

### Beat 08 — Cut to Clinician authority

**时间：** `02:32-02:51`
**当前角色：** Clinician
**录制：** 停录切换后继续

### ① 先做这些操作

1. 镜头外完成 Clinician 登录。
2. 确认 `Clinician A`、`Clinician view`、`Sarah Tan`。
3. 确认 `English` 和 `Record status: Up to date`。
4. 找到当前 conflict 并点击 `Review conflict` 一次。
5. drawer 稳定后开始念 Cue 16。

### ② 等看到这些再念

- Clinician-only decision controls 可见。
- 两个 source 和 conflict explanation 可见。
- 没有登录页或密码框。

### ③ 现在念

**Cue 16 · 00:02:32,000 --> 00:02:41,500**
> I now switch to Clinician outside the camera, then return to the same synthetic patient workspace.

**Cue 17 · 00:02:42,000 --> 00:02:51,000**
> Clinician review exposes adjudication, version history, and conflict choices that Staff cannot submit.

### ④ 念完立刻做什么

- Cue 17 结束后关闭 conflict drawer。
- 继续在 Clinician Timeline 找到可查看历史的 entry，进入 Beat 09。

### ⑤ 出问题时

- Clinician session 未确认：停录，镜头外重新登录；不要用旧截图替代当前画面。

### ⑥ 本段对应

`Scenario 13 / Direct UI，需当前角色人工复核`

---

### Beat 09 — Explain concurrency, History, Compare, and Revert

**时间：** `02:51.5-03:40`
**当前角色：** Clinician
**录制：** 继续

### ① 先做这些操作

1. 保持在 Clinician Timeline，不注入线上 stale write。
2. 打开一个当前 entry 的 `History`。
3. 选择页面实际存在的 earlier version。
4. 点击该 row 的 `Compare` 一次。
5. 等 `Before` 和 `After` 出现后开始念 Cue 18。

### ② 等看到这些再念

- `History` 区域完整出现。
- earlier row、current row、`Before`、`After` 可读。
- 版本号按页面实际显示；不要假设 `v1 -> v2`。

### ③ 现在念

**Cue 18 · 00:02:51,500 --> 00:03:00,500**
> A stale same-section write returns a deterministic conflict instead of silently overwriting the newer version.

**Cue 19 · 00:03:01,000 --> 00:03:10,500**
> The audit preserves both submissions, so a reviewer can see what happened and which version was current.

**Cue 20 · 00:03:11,000 --> 00:03:20,000**
> History shows an earlier version beside the current record, without requiring a fixed version number.

**Cue 21 · 00:03:20,500 --> 00:03:30,000**
> Compare makes the Before and After text explicit, while the original timeline entry remains available.

**Cue 22 · 00:03:30,500 --> 00:03:40,000**
> A revert creates a new version; it never erases previous snapshots, audit metadata, or source provenance.

### ④ 念完立刻做什么

- Cue 22 结束后停留 2 秒。
- 默认不点击 `Revert`；关闭 History，进入 Beat 10。

### ⑤ 出问题时

- 没有 earlier row 或 Compare：保留 History 画面，直接停本段，不重复点击。

### ⑥ 本段对应

`Scenario 10 / Scenario 16 / Direct UI + evidence explanation`

---

## Scene 5 — Patient publication safety gate

### Beat 10 — Open the patient publication review

**时间：** `03:40.5-04:01`
**当前角色：** Clinician
**录制：** 继续

### ① 先做这些操作

1. 在 Timeline 找到 `Prepare patient update`。
2. 点击 `Prepare patient update` 一次。
3. 等右侧 `Patient publication review` drawer 完整打开。
4. 鼠标指向 `Workflow state: Draft`。
5. `IMMUTABLE SOURCE` 出现后开始念 Cue 23。

### ② 等看到这些再念

- `Patient publication review` 标题出现。
- `Draft`、`IMMUTABLE SOURCE`、source entry 和 source date 可读。
- 不出现 Publish confirmation 或外部消息页面。

### ③ 现在念

**Cue 23 · 00:03:40,500 --> 00:03:50,500**
> From a timeline entry, Prepare patient update opens an explicit patient-publication review rather than changing visibility.

**Cue 24 · 00:03:51,000 --> 00:04:01,000**
> The workflow begins in Draft and shows the immutable source evidence behind the proposed patient-facing content.

### ④ 念完立刻做什么

- Cue 24 结束后停留 2 秒。
- 保持 Draft，不点击 Save、Approve 或 Publish，进入 Beat 11。

### ⑤ 出问题时

- 当前状态不是 Draft：按页面实际状态说，停留在可读状态，不强行推进 workflow。

### ⑥ 本段对应

`Scenario 12 / Direct UI`

---

### Beat 11 — Explain dosage and explicit publish gates

**时间：** `04:01.5-04:32`
**当前角色：** Clinician
**录制：** 继续

### ① 先做这些操作

1. 指向 `Accepting an AI suggestion does not publish it to the patient`。
2. 指向 `MEDICATION DOSAGE CHECK`。
3. 指向 source dosage、draft dosage 和当前 dosage status。
4. 让 `Approve` 与 `Publish` 的分离保持可读。
5. 不输入 draft；画面稳定后开始念 Cue 25。

### ② 等看到这些再念

- `Draft`、immutable evidence、dosage status 和 patient-facing draft 可见。
- 若页面显示 `No dosage evidence`，保持该真实状态。
- 不出现外部 delivery receipt。

### ③ 现在念

**Cue 25 · 00:04:01,500 --> 00:04:12,000**
> Accepting an internal AI suggestion does not publish it to the patient; those are separate user actions.

**Cue 26 · 00:04:12,500 --> 00:04:22,000**
> Dosage checks are visible before approval, and unsupported or mismatched dosage remains fail-closed.

**Cue 27 · 00:04:22,500 --> 00:04:32,000**
> Clinician approval and explicit Publish are distinct gates; this prototype does not claim external message delivery.

### ④ 念完立刻做什么

- Cue 27 结束后停留 2 秒。
- 关闭 publication drawer，不改变状态，进入 Beat 12。

### ⑤ 出问题时

- dosage evidence 不出现：展示真实 `No dosage evidence`，不要编造数字或修改 draft。

### ⑥ 本段对应

`Scenario 12 / Direct UI + honest boundary`

---

## Scene 6 — Voice fixture and provider failure boundary

### Beat 12 — Show the prerecorded Voice fixture

**时间：** `04:32.5-04:53`
**当前角色：** Staff 或 Clinician
**录制：** 继续

### ① 先做这些操作

1. 找到 `Voice note`。
2. 确认 `Review a pre-recorded care conversation`。
3. 展开 `About this example`，让 fixture disclosure 可读。
4. 若音频未播放，点击 native play 一次。
5. 不点击 `Create care-note suggestion`；audio 稳定后开始念 Cue 28。

### ② 等看到这些再念

- `Voice note`、audio controls 和 `Length: 24.0s` 可见。
- `About this example` 显示 prerecorded synthetic conversation/prepared transcript。
- 若页面已有 result，transcript/source 可读；没有 result 也不制造。

### ③ 现在念

**Cue 28 · 00:04:32,500 --> 00:04:42,500**
> The Voice panel uses a prerecorded synthetic care conversation and a prepared timestamped transcript.

**Cue 29 · 00:04:43,000 --> 00:04:53,000**
> It demonstrates a reviewable source path, not live ASR, diarization, speaker attribution, or microphone capture.

### ④ 念完立刻做什么

- Cue 29 结束后停留 2 秒。
- 停止 audio 或离开 Voice panel，进入 Beat 13。

### ⑤ 出问题时

- 没有 Voice result：不重复点击生成；只展示 fixture disclosure 和 audio，或停止本段。

### ⑥ 本段对应

`Overall Voice boundary / Direct UI or honest limitation`

---

### Beat 13 — Explain redaction and provider failure

**时间：** `04:53.5-05:13`
**当前角色：** Staff/Clinician
**录制：** 继续

### ① 先做这些操作

1. 保持在稳定 product page 或已准备好的 Brief 画面。
2. 不在线上注入 provider failure。
3. 指向 `failure is explicit` 和 `existing records remain usable` 的说明。
4. 不打开 dashboard、日志、环境变量或 provider console。
5. 画面稳定后开始念 Cue 30。

### ② 等看到这些再念

- redaction-before-provider、bounded failure 和 metadata-only logging 的文字可读。
- 页面没有 raw prompt、response、API key 或真实日志行。

### ③ 现在念

**Cue 30 · 00:04:53,500 --> 00:05:03,500**
> If a provider fails, the system surfaces an explicit failure state and keeps existing records available.

**Cue 31 · 00:05:04,000 --> 00:05:13,000**
> The failure path is evidence-backed; the prototype does not silently fabricate a successful fixture result.

### ④ 念完立刻做什么

- Cue 31 结束后停留 1 秒。
- 停录，准备 Clinician → Patient 角色切换卡，再进入 Beat 14。

### ⑤ 出问题时

- 页面没有 failure 状态：停留在证据说明，按当前内容完成本段，不制造线上故障。

### ⑥ 本段对应

`Scenario 3 / Scenario 4 / Scenario 8 / Scenario 9 / Evidence explanation`

---

## Scene 7 — Patient projection

### Beat 14 — Show the Patient projection

**时间：** `05:13.5-05:33`
**当前角色：** Patient
**录制：** 停录切换后继续

### ① 先做这些操作

1. 镜头外完成 Patient 登录。
2. 确认 `Patient view`、`Sarah Tan` 和 `English`。
3. 确认 `Your care summary` 或 current care projection。
4. 缓慢滚动到患者可见的 Voice 区域。
5. 不点击 source、comments、tasks 或内部 timeline control，画面稳定后开始念 Cue 32。

### ② 等看到这些再念

- `Patient view` 和 `Your care summary` 可读。
- 只有 patient-facing/current-care 内容加载完成。
- 没有内部 drawer 或 error。

### ③ 现在念

**Cue 32 · 00:05:13,500 --> 00:05:23,000**
> I switch to Patient outside the camera and show only the audience-specific shared care projection.

**Cue 33 · 00:05:23,500 --> 00:05:33,000**
> The patient view contains current care information and its safe Voice fixture, without internal review controls.

### ④ 念完立刻做什么

- Cue 33 结束后停留 2 秒。
- 保持 Patient 页面，进入 Beat 15。

### ⑤ 出问题时

- Patient session 未确认：立即停录，镜头外重新登录；不使用旧截图。

### ⑥ 本段对应

`Scenario 1 / Scenario 12 / Distinct outputs / Direct UI`

---

### Beat 15 — Hold the Patient privacy boundary

**时间：** `05:33.5-05:53`
**当前角色：** Patient
**录制：** 继续

### ① 先做这些操作

1. 鼠标指向 patient-facing summary。
2. 鼠标指向 safe Voice 区域。
3. 不点击任何内部入口。
4. 保持画面静止 2 秒后开始念 Cue 34。

### ② 等看到这些再念

- 页面没有 `Glance`、conflict、internal source、Comments、Tasks 或 History。
- 没有 Staff/Clinician controls 和 raw AI。

### ③ 现在念

**Cue 34 · 00:05:33,500 --> 00:05:43,500**
> Glance, comments, tasks, conflict details, raw AI output, and source workflow identifiers stay outside the Patient projection.

**Cue 35 · 00:05:44,000 --> 00:05:53,000**
> Publication is therefore a gate before sharing, not an automatic consequence of accepting an internal suggestion.

### ④ 念完立刻做什么

- Cue 35 结束后停录。
- 关闭或切换到已准备好的 limitation 画面，继续进入 Beat 16。

### ⑤ 出问题时

- 出现任意内部内容：立即停止整段 take，不用裁剪或字幕掩盖。

### ⑥ 本段对应

`Scenario 1 / Scenario 3 / Scenario 12 / Direct UI + privacy boundary`

---

## Scene 8 — Honest limitations

### Beat 16 — State honest gaps

**时间：** `05:53.5-06:34`
**当前角色：** Brief / stable page
**录制：** 继续

### ① 先做这些操作

1. 打开已准备好的 Iteration Brief limitation 页面。
2. 不打开 Render dashboard、环境变量或日志。
3. 指向 SURVIVES、PARTIAL、DOES NOT 分类。
4. 指向 phone-only onboarding、multilingual ASR、delivery receipt、medication interpretation 的边界。
5. 字幕不遮挡表格后开始念 Cue 36。

### ② 等看到这些再念

- limitation 页面和 status 完整出现。
- abstention 文案清楚可读。
- 不出现未经限定的 clinical claim。

### ③ 现在念

**Cue 36 · 00:05:53,500 --> 00:06:03,500**
> The remaining gaps are stated as evidence boundaries, not hidden claims about a general clinical system.

**Cue 37 · 00:06:04,000 --> 00:06:14,000**
> Phone-only onboarding, multilingual ASR, external delivery receipts, and broad medication interpretation are not implemented here.

**Cue 38 · 00:06:14,500 --> 00:06:24,000**
> The prototype deliberately abstains when its bounded rules lack support, instead of inventing clinical certainty.

**Cue 39 · 00:06:24,500 --> 00:06:34,000**
> These limits are deliberate scope decisions and point to the next build step rather than a false finish.

### ④ 念完立刻做什么

- Cue 39 结束后停留 2 秒。
- 切到安全的 README/source/evidence 画面，进入 Beat 17。

### ⑤ 出问题时

- Brief 页面打不开：停止本段，回到稳定 product page，按当前可见边界重录。

### ⑥ 本段对应

`Scenarios 1, 5-9, 11 / Honest limitation`

---

## Scene 9 — Evidence and closing

### Beat 17 — Point to repository and quality evidence

**时间：** `06:34.5-07:04`
**当前角色：** Stable workspace / repository page
**录制：** 继续

### ① 先做这些操作

1. 打开安全的 README 或 public source tree 画面。
2. 指向 required tests。
3. 指向 `194 backend tests` 和 `86.62% global coverage`。
4. 指向 PostgreSQL 18 CI 和 Render live evidence。
5. 不打开 settings、secrets、Environment、database connection 或 raw logs，画面稳定后开始念 Cue 40。

### ② 等看到这些再念

- tests、coverage、PostgreSQL CI、Render deployment 文字可读。
- 画面没有 MP4、ZIP、password file 或凭据。

### ③ 现在念

**Cue 40 · 00:06:34,500 --> 00:06:44,000**
> The repository includes the required application tests for RBAC, revisions, provenance, and concurrent edits.

**Cue 41 · 00:06:44,500 --> 00:06:54,000**
> The local closure run recorded 194 backend tests and 86.62 percent global application coverage.

**Cue 42 · 00:06:54,500 --> 00:07:04,000**
> PostgreSQL 18 CI passed, and the existing Render service is live on the exact runtime candidate.

### ④ 念完立刻做什么

- Cue 42 结束后回到稳定 English product screen。
- 关闭所有 drawer，进入 Beat 18。

### ⑤ 出问题时

- README/source 画面不稳定：切回稳定 product screen，不现场寻找 settings。

### ⑥ 本段对应

`Deliverables / Scenarios 2-4, 10, 16 / Direct documentation`

---

### Beat 18 — Close with the disclosed gap

**时间：** `07:04.5-07:22`
**当前角色：** Stable workspace
**录制：** 继续后停止

### ① 先做这些操作

1. 保持 stable English product screen。
2. 确认所有 drawer 关闭。
3. 鼠标停在空白处。
4. Cue 43 开始念；Cue 44 结束后停留 1 秒。
5. 点击录屏软件 `Stop recording`，不要再点击网页。

### ② 等看到这些再念

- synthetic data disclosure 或 human review boundary 可见。
- 最后 subtitle cue 完整结束。
- 录屏控制台不出现在画面中。

### ③ 现在念

**Cue 43 · 00:07:04,500 --> 00:07:12,000**
> The hosted authenticated benchmark remains a disclosed supplementary gap, not a claim we are hiding.

**Cue 44 · 00:07:12,500 --> 00:07:22,000**
> The next step is final human recording, full video QA, and submission packaging after the video exists.

### ④ 念完立刻做什么

- 停止录制并确认视频文件保存。
- 录完后再做最终 QA；不要在此处生成 ZIP、MANIFEST 或邮件。

### ⑤ 出问题时

- 念错或录屏未保存：只重录 Beat 18，不重新操作前面的网页状态。

### ⑥ 本段对应

`Communication / Honest limitation / Direct close`

---

# 第四部分：角色切换卡

## Staff -> Clinician

1. 在 Beat 07 结束后关闭 Comments；不要打开或展示 Tasks 内容。
2. 点击录屏软件 `Stop recording`。
3. 镜头外点击应用 `Sign out`。
4. 镜头外完成 Clinician 登录；密码页不入镜。
5. 检查 `Clinician A`、`Clinician view`、`English`、`Sarah Tan`。
6. 等待 `Record status: Up to date`。
7. 定位到 Scene 4 / Beat 08 的 conflict review 起点。
8. 确认没有错误 role、错误患者、loading 或 drawer 后重新开始录制。

## Clinician -> Patient

1. 在 Beat 13 结束后关闭所有 drawer。
2. 点击录屏软件 `Stop recording`。
3. 镜头外点击应用 `Sign out`。
4. 镜头外完成 Patient 登录；不读取或代填密码。
5. 检查 `Patient view`、`English`、`Sarah Tan`。
6. 等待 `Record status: Up to date` 或患者 projection 完整出现。
7. 定位到 Scene 7 / Beat 14 的 `Your care summary` 起点。
8. 确认页面没有内部内容后重新开始录制。

每次切换都只在停录后完成。角色、患者、页面语言或权限不对时，停留在切换卡，不继续拍摄。

---

# 第五部分：紧急情况速查

| 情况 | 一个动作结论 |
| --- | --- |
| 登录失效或出现登录页 | 立即停录，镜头外重新登录，从当前 Scene 重录。 |
| Render 冷启动 | 停录等待页面稳定，不保留 loading。 |
| protected conflict 不见 | 只刷新一次；仍不见就停录，不改数据。 |
| publication 状态不同 | 按当前页面状态描述，不强行推进。 |
| drawer 打不开 | 停当前段，从该 Beat 开头重录。 |
| SSE reconnecting | 等待 `Up to date`，不要重复点击。 |
| 页面不是 English | 停录切回 `English`。 |
| 念错一句 | 停在安全画面，只重录当前 Beat。 |
| 点错按钮 | 立即停录，不用第二次写操作抵消。 |
| 浏览器通知弹出 | 停录，关闭通知，重录当前 Scene。 |
| 密码意外入镜 | 删除该 take，整理窗口后从当前 Scene 重录。 |

不要为了修复拍摄状态运行 reset、delete、seed、数据库 SQL 或修改线上 clinical truth。

---

# 第六部分：录完后的完整 QA

只有完整观看最终人工视频后才能勾选；视频完成前保持全部未勾选。

## 画面和顺序

- [ ] 已剪掉全部登录页、Sign out、密码框和自动填充。
- [ ] 没有密码、API key、token、cookie、配置、DevTools、终端、Render dashboard 或原始日志。
- [ ] 顺序为 Staff -> Clinician -> Patient，角色切换均在停录后完成。
- [ ] 页面语言为 English，患者和 role 始终正确。
- [ ] 页面没有意外通知、遮挡、长时间 loading 或未解释 error。
- [ ] 页面在录屏分辨率下可读，没有水平溢出或裁切。

## 产品核心路径

- [ ] Staff Glance 不超过 6 项。
- [ ] protected conflict 和双 source 可见。
- [ ] `priority` 明确不是 medical risk。
- [ ] `protected-first` 说明清楚，未被描述成医学概率。
- [ ] `immutable source`、source version 和 exact span 可读。
- [ ] `Accept is not Publish` 明确出现。
- [ ] publication Draft、dosage gate、Approve/Publish 分离没有被误说成已发送。
- [ ] Patient projection 只显示患者可见内容，不出现内部控件。
- [ ] honest limitations 和 unsupported input abstention 被准确保留。
- [ ] Tasks rehearsal 数据没有进入正式主流程或画面。

## 声音、字幕和口播

- [ ] 旁白声音清楚，native audio 没有盖住旁白。
- [ ] 706 words 的 English narration 与 44 个 cue 逐字一致。
- [ ] 字幕时间无重叠，与画面动作和旁白同步。
- [ ] provenance（PROV-uh-nuhns）、immutable（ih-MYOO-tuh-bul）、adjudication（uh-joo-duh-KAY-shun）、
      diarization（dy-uh-rye-ZAY-shun）和 concurrency（kun-KUR-un-see）发音可辨。
- [ ] 没有把 prerecorded Voice transcript 说成 live ASR、diarization 或模型质量证明。

## 事实边界

- [ ] 没有声称 production-ready、clinically validated、general clinical NLP 或 trilingual understanding。
- [ ] 没有声称 calibrated confidence、medical risk probability、FHIR/HIPAA compliance。
- [ ] 没有声称 WhatsApp delivery、unbiased learning 或 real-time collaborative editing。
- [ ] 没有把 test/evidence explanation 说成现场真实故障注入。
- [ ] benchmark gap 仍作为 disclosed supplementary gap，未被说成 hosted latency 通过。
- [ ] 最终视频从头到尾可以播放，最后停在稳定工作区。

## 录制结束后

- [ ] 保留原始视频文件，不转码、不压缩、不裁剪、不重命名。
- [ ] 完成上述 QA 后，再决定最终 ZIP/MANIFEST 和邮件步骤。
- [ ] 本文件是录制期间唯一需要查看的文件；其他材料无需打开。
