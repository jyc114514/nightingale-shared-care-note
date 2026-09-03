# Nightingale Real Clinic Demo Recording Master

**中文操作 / English narration / English subtitles / one recording SSOT**

Date: 2026-09-03
Status: **FINAL DEMO PREPARATION - CODE FROZEN**
Target length: **7:22** (acceptable range: 6:00-8:00)
Target delivery: English UI, English narration, Chinese operator instructions, 95-110 WPM

## Submission decision

`SUBMISSION READY WITH DISCLOSED SUPPLEMENTARY BENCHMARK GAP`

The hosted authenticated benchmark remains pending because the available browser control surface
does not provide a permitted same-origin request/performance channel without extracting browser
credentials. This is an internal engineering limitation, not a requested deliverable and not a
blocker for the final Demo Video. PostgreSQL 18 CI, the existing Render deployment, anonymous
HTTPS canaries, local warm-path evidence, and the 15/15 watch remain documented. They must not be
described as hosted authenticated latency.

## Frozen facts and hard boundaries

| Fact | Current value |
| --- | --- |
| Git main/origin at preparation | `e5f9339` |
| Deployed runtime | `4f4fc84c3451152e63135bd7fdd7b851bb43a1ea` |
| Render deploy | `dep-dacd2lgn74is73co3t2g` |
| Render URL | `https://nightingale-shared-care-note.onrender.com` |
| Runtime tag | `real-clinic-rc6` -> `4f4fc84` |
| Glance algorithm | `importance-v3-protected-first` |
| Backend evidence | 194 passed; 86.62% global `app` coverage |
| Browser evidence | Gate B 20; Voice 4; Publication 2 |
| Migration head | `0015_feedback_backward_compat` |
| Requirements SHA-256 | `4659AF4A414AFF86C1DB6DA0EC3FEB4837236D625669AE7C9CFE5CC69BC934F5` |

This round does not change backend/frontend product code, migrations, dependencies, workflows,
ranking, publication semantics, Voice, DeepSeek, Render runtime, database state, or the existing
54.76-second WebM. Do not open, transform, rename, move, upload, or inspect the original MP4.
Never show a password field, browser autofill, cookie, token, API key, environment value, Render
dashboard, terminal, DevTools, or raw log. Clinical note source text is not automatically
translated or rewritten.

## Recording setup

1. Complete Staff, Clinician, and Patient login outside the camera frame. Do not record passwords.
2. Use the existing HTTPS URL, `English`, and patient `Sarah Tan`. Wait for `Record status: Up to date`.
3. Use a real 1440x900 desktop viewport if possible. Close `Guide`, `Source`, `Comments`, `History`,
   `Tasks`, browser notifications, and DevTools before each take.
4. Use the visible labels in the page, not fixed version numbers, fixed suggestion states, or copied
   UUIDs. If a card is already `Reviewed`, choose another card that currently exposes the needed
   action; do not change data merely to match this script.
5. This is a read-first recording. No task, comment, revision, Accept, Reject, adjudication,
   approval, publication, or Voice suggestion creation is required for the hosted take.
6. If Tasks opens and shows rehearsal-labelled test items, close it and use the evidence-backed
   explanation branch. Do not display those titles and do not delete them during recording.

## One-page cue sheet

| Scene | Time | Role | Main visible path | Cue IDs | Stop/cut |
| --- | --- | --- | --- | --- | --- |
| 1. Opening | 00:00-00:32 | Staff | Stable Staff workspace | 01-04 | Continue |
| 2. Protected Glance | 00:32-01:26 | Staff | Glance View -> Why is this here? | 05-09 | Continue |
| 3. Dual provenance | 01:26-02:12 | Staff | Review conflict -> two sources -> Close | 10-13 | Continue |
| 4. Authority and history | 02:12-03:40 | Staff -> Clinician | Comments/Tasks entry points -> role cut -> History/Compare | 14-22 | Cut outside camera |
| 5. Publication gate | 03:40-04:32 | Clinician | Prepare patient update -> Draft -> source/dosage gate | 23-27 | Continue |
| 6. Voice and failure | 04:32-05:13 | Clinician/Staff | Voice fixture -> Brief/evidence failure boundary | 28-31 | Continue |
| 7. Patient projection | 05:13-05:53 | Patient | Patient view -> current care projection | 32-35 | Cut outside camera |
| 8. Honest gaps | 05:53-06:34 | Patient/Brief | Iteration Brief limitations | 36-39 | Continue |
| 9. Evidence close | 06:34-07:22 | Stable workspace | Repository, tests, CI, Render facts | 40-44 | Stop recording |

## Cue ledger (the English source for the SRT)

The exact text below is the subtitle text. The operator should read it only after the stated
screen condition is visible. SRT line wrapping does not change the words or punctuation.

| Cue | Time | English narration |
| --- | --- | --- |
| 01 | 00:00-00:08 | Nightingale is a shared care workspace that keeps longitudinal records, review decisions, and audience boundaries on one patient page. |
| 02 | 00:08.5-00:16.5 | This recording uses synthetic data, a hosted HTTPS workspace, and a deliberate separation between sources, suggestions, and publication. |
| 03 | 00:17-00:25 | A ranked item is a workflow aid, not a diagnosis, and it never silently replaces a human-authored record. |
| 04 | 00:25.5-00:32 | I will move from Staff to Clinician to Patient, with role changes outside the camera frame. |
| 05 | 00:32.5-00:43 | I start with Glance View, where content, status, next action, risk context, and priority appear together. |
| 06 | 00:43.5-00:54 | The screen is deliberately capped at six items, keeping the first clinical read compact instead of overwhelming. |
| 07 | 00:54.5-01:04 | The protected allergy conflict appears first even when ordinary candidates carry a higher numerical priority. |
| 08 | 01:04.5-01:15 | Protected attention is a separate selection policy; it does not turn a workflow number into a medical risk score. |
| 09 | 01:15.5-01:26 | The explanation makes the ranking auditable: protected candidates first, then deterministic priority, time, and resource ordering. |
| 10 | 01:26.5-01:37 | I open the conflict to inspect two contradictory assertions without editing or resolving either source. |
| 11 | 01:37.5-01:49 | The reported allergy and the denied allergy remain separate, with their own authors, timestamps, and verification states. |
| 12 | 01:49.5-02:00 | Each assertion links to an immutable source version and an exact highlighted span, rather than a copied approximation. |
| 13 | 02:00.5-02:12 | The source panel keeps the originating version distinct from the record's current version, so later edits remain explainable. |
| 14 | 02:12.5-02:21.5 | Staff can inspect both sources, but the clinical decision controls stay unavailable in this role. |
| 15 | 02:22-02:31.5 | Comments and Tasks are collaboration entry points; opening a drawer does not change clinical truth or create a task. |
| 16 | 02:32-02:41.5 | I now switch to Clinician outside the camera, then return to the same synthetic patient workspace. |
| 17 | 02:42-02:51 | Clinician review exposes adjudication, version history, and conflict choices that Staff cannot submit. |
| 18 | 02:51.5-03:00.5 | A stale same-section write returns a deterministic conflict instead of silently overwriting the newer version. |
| 19 | 03:01-03:10.5 | The audit preserves both submissions, so a reviewer can see what happened and which version was current. |
| 20 | 03:11-03:20 | History shows an earlier version beside the current record, without requiring a fixed version number. |
| 21 | 03:20.5-03:30 | Compare makes the Before and After text explicit, while the original timeline entry remains available. |
| 22 | 03:30.5-03:40 | A revert creates a new version; it never erases previous snapshots, audit metadata, or source provenance. |
| 23 | 03:40.5-03:50.5 | From a timeline entry, Prepare patient update opens an explicit patient-publication review rather than changing visibility. |
| 24 | 03:51-04:01 | The workflow begins in Draft and shows the immutable source evidence behind the proposed patient-facing content. |
| 25 | 04:01.5-04:12 | Accepting an internal AI suggestion does not publish it to the patient; those are separate user actions. |
| 26 | 04:12.5-04:22 | Dosage checks are visible before approval, and unsupported or mismatched dosage remains fail-closed. |
| 27 | 04:22.5-04:32 | Clinician approval and explicit Publish are distinct gates; this prototype does not claim external message delivery. |
| 28 | 04:32.5-04:42.5 | The Voice panel uses a prerecorded synthetic care conversation and a prepared timestamped transcript. |
| 29 | 04:43-04:53 | It demonstrates a reviewable source path, not live ASR, diarization, speaker attribution, or microphone capture. |
| 30 | 04:53.5-05:03.5 | If a provider fails, the system surfaces an explicit failure state and keeps existing records available. |
| 31 | 05:04-05:13 | The failure path is evidence-backed; the prototype does not silently fabricate a successful fixture result. |
| 32 | 05:13.5-05:23 | I switch to Patient outside the camera and show only the audience-specific shared care projection. |
| 33 | 05:23.5-05:33 | The patient view contains current care information and its safe Voice fixture, without internal review controls. |
| 34 | 05:33.5-05:43.5 | Glance, comments, tasks, conflict details, raw AI output, and source workflow identifiers stay outside the Patient projection. |
| 35 | 05:44-05:53 | Publication is therefore a gate before sharing, not an automatic consequence of accepting an internal suggestion. |
| 36 | 05:53.5-06:03.5 | The remaining gaps are stated as evidence boundaries, not hidden claims about a general clinical system. |
| 37 | 06:04-06:14 | Phone-only onboarding, multilingual ASR, external delivery receipts, and broad medication interpretation are not implemented here. |
| 38 | 06:14.5-06:24 | The prototype deliberately abstains when its bounded rules lack support, instead of inventing clinical certainty. |
| 39 | 06:24.5-06:34 | These limits are deliberate scope decisions and point to the next build step rather than a false finish. |
| 40 | 06:34.5-06:44 | The repository includes the required application tests for RBAC, revisions, provenance, and concurrent edits. |
| 41 | 06:44.5-06:54 | The local closure run recorded 194 backend tests and 86.62 percent global application coverage. |
| 42 | 06:54.5-07:04 | PostgreSQL 18 CI passed, and the existing Render service is live on the exact runtime candidate. |
| 43 | 07:04.5-07:12 | The hosted authenticated benchmark remains a disclosed supplementary gap, not a claim we are hiding. |
| 44 | 07:12.5-07:22 | The next step is final human recording, full video QA, and submission packaging after the video exists. |

## Detailed recording beats

Each beat follows the same order: Chinese operation first, then English narration. Use the cue
ledger as the exact narration/subtitle source.

### Beat 01 - Open the stable Staff workspace

- 时间: `00:00-00:16.5`; 当前角色: Staff; 录制状态: 开始
- 页面起点: 已在镜头外登录，顶部 workspace 可见。
- 中文操作:
  1. 确认页面显示 `Staff A`、`Staff view`、`Sarah Tan` 和 `Record status: Up to date`。
  2. 鼠标缓慢移过页面标题，不要点击登录、Guide、患者下拉框或任何写按钮。
- 等待条件: 顶部状态和患者姓名稳定至少 2 秒。
- 画面必须看到: `Shared Care Note`、Staff 身份、synthetic disclosure 或 trust boundary。
- 画面不能出现: 登录页、密码框、浏览器 autofill、配置或 DevTools。
- 现在念: Cue 01-02；英文字幕: 与 Cue 01-02 完全一致。
- Requirement mapping: overall, #2, #3, #13-16。
- 证据类型: Direct UI + Honest limitation。
- 本段优势: 先给观众角色、患者和信任边界，再进入产品路径。
- 禁止声称: 不说这是临床生产系统或真实患者记录。
- 退出条件: Cue 02 结束，Glance View 方向清楚。
- 如果状态不同: 状态不是 `Up to date` 就停录，镜头外等待或重新登录。
- 剪辑建议: 保留 1 秒环境停顿，隐藏任何浏览器 UI。

### Beat 02 - State the trust thesis

- 时间: `00:17-00:32`; 当前角色: Staff; 录制状态: 继续
- 页面起点: 稳定 workspace，鼠标停在空白区域。
- 中文操作:
  1. 不点击任何 control，只让标题和 trust boundary 留在画面内。
  2. 读 Cue 03-04，Cue 04 结束后准备向下滚动。
- 等待条件: 口播前确认页面没有 toast 或 loading。
- 画面必须看到: stable workspace 和 synthetic context。
- 画面不能出现: 版本号、测试任务标题或内部 source ID。
- 现在念: Cue 03-04；英文字幕: 与 Cue 03-04 完全一致。
- Requirement mapping: requirements.txt:8-9, 41-44; #14-16。
- 证据类型: Direct UI + allowed claim。
- 本段优势: 把“建议”和“事实来源”分开，避免 AI overclaim。
- 禁止声称: 不说 AI 理解所有 clinical notes。
- 退出条件: Cue 04 结束，开始平滑滚动到 Glance。
- 如果状态不同: 只处理遮挡标题的 drawer；不要改数据库状态。
- 剪辑建议: 保留完整句尾，避免从标题直接硬切。

### Beat 03 - Enter Glance View

- 时间: `00:32.5-00:54`; 当前角色: Staff; 录制状态: 继续
- 页面起点: workspace 顶部。
- 中文操作:
  1. 平滑向下滚动到 `Glance View` 和 `What needs attention now`。
  2. 指向 `6 items need attention`，再停在第一张卡片上；不要点击卡片写操作。
- 等待条件: 六张卡片、status、next step 和 priority 均渲染完成。
- 画面必须看到: 六项上限、至少一张可读卡片、`Next step`、`Priority`、risk 文案。
- 画面不能出现: 超过六项、`Show more`、空白 Glance 或 loading。
- 现在念: Cue 05-06；英文字幕: 与 Cue 05-06 完全一致。
- Requirement mapping: requirements.txt:9-12; #14-15。
- 证据类型: Direct UI。
- 本段优势: 直接回应 under-10-second glanceability，而不是展示信息洪流。
- 禁止声称: 不把六项上限说成完整临床 triage。
- 退出条件: 六张卡片都稳定，进入 protected card。
- 如果状态不同: 若不是六项，停录并使用 fallback；不改 cap、不刷新多次。
- 剪辑建议: 让鼠标移动慢，避免覆盖卡片文字。

### Beat 04 - Show protected-first ranking

- 时间: `00:54.5-01:26`; 当前角色: Staff; 录制状态: 继续
- 页面起点: Glance 第一项。
- 中文操作:
  1. 指向 `Conflicting allergy information` 和 `Needs clinician review`。
  2. 展开该卡的 `Why is this here?`，让 `Protected attention` 和 protected-first explanation 可读。
  3. 指向 priority 数字与普通卡片的相对位置，不要点击 `Accept`、`Reject` 或 `Pin`。
- 等待条件: explanation 完全展开，鼠标移开文字后再念 Cue 07-09。
- 画面必须看到: protected conflict 在第一项、普通候选仍存在、priority/risk 区分。
- 画面不能出现: “medical risk probability” 或未经证实的 confidence badge。
- 现在念: Cue 07-09；英文字幕: 与 Cue 07-09 完全一致。
- Requirement mapping: #13, #14, #15; `importance-v3-protected-first`。
- 证据类型: Direct UI + automated test evidence。
- 本段优势: 展示真正解决的 starvation 问题，同时保留六项上限。
- 禁止声称: 不说 protected floor 是医学风险分数或 calibrated probability。
- 退出条件: Cue 09 结束，准备打开 conflict。
- 如果状态不同: 若 protected item 不在第一项，停录；不要通过删卡或改 priority 修复。
- 剪辑建议: Cue 08 时保持 explanation 静止，便于评委阅读。

### Beat 05 - Inspect both conflict assertions

- 时间: `01:26.5-01:49`; 当前角色: Staff; 录制状态: 继续
- 页面起点: protected card。
- 中文操作:
  1. 点击 `Review conflict` 一次，等待 `Allergy conflict review` drawer。
  2. 先指向 `ALLERGY REPORTED`，再指向 `ALLERGY DENIED`；不要点击 clinical decision。
- 等待条件: 两个 source button 和 Staff read-only boundary 都出现。
- 画面必须看到: `View source: Allergy reported`、`View source: Allergy denied`、Staff read-only 说明。
- 画面不能出现: Record clinical decision、Confirm present/absent 的可提交动作。
- 现在念: Cue 10-11；英文字幕: 与 Cue 10-11 完全一致。
- Requirement mapping: #13; requirements.txt:42-44。
- 证据类型: Direct UI。
- 本段优势: 把冲突呈现为两条可核验事实，不把系统选择伪装成答案。
- 禁止声称: 不说系统已经判断谁正确。
- 退出条件: 两条 assertion 均可读。
- 如果状态不同: 若 drawer loading 超过正常等待，停当前 take，不重复点击。
- 剪辑建议: 保留两个 source label 的完整画面。

### Beat 06 - Follow exact immutable provenance

- 时间: `01:49.5-02:12`; 当前角色: Staff; 录制状态: 继续
- 页面起点: conflict drawer。
- 中文操作:
  1. 点击 `View source: Allergy reported` 一次，等待 `Original source` 和 timeline highlight。
  2. 回到 conflict drawer 后点击另一条 `View source` 一次；最后关闭 source 和 conflict drawer。
- 等待条件: source panel 显示版本、日期、原文和 exact highlight；不要展开 Technical details。
- 画面必须看到: immutable source、exact highlighted span、源版本与 current version 的分离。
- 画面不能出现: 近似字符串、未验证 current content 或内部 UUID。
- 现在念: Cue 12-13；英文字幕: 与 Cue 12-13 完全一致。
- Requirement mapping: #13, #16; `test_highlight_provenance.py`。
- 证据类型: Direct UI + automated test evidence。
- 本段优势: 直接展示 provenance 不是 decorative badge。
- 禁止声称: 不说编辑后的 current text 会替代原始 source。
- 退出条件: 两个 source 都被看见，所有 drawer 关闭。
- 如果状态不同: 若第二个 source 不稳定，保留第一个 source 的完整 take，并用 test evidence 解释。
- 剪辑建议: Source panel 稳定后再念，避免鼠标挡住 mark。

### Beat 07 - Show collaboration entry points without writing

- 时间: `02:12.5-02:31.5`; 当前角色: Staff; 录制状态: 继续
- 页面起点: Timeline 第一条可见 entry。
- 中文操作:
  1. 点击一个当前 Timeline entry 的 `Comments`，等待 contextual drawer 出现。
  2. 只展示 `Team discussion`、Comment body 和关闭按钮；不要输入、Add comment 或 Resolve。
  3. 关闭 Comments；如需验证 Task 入口，点击 `Assign task` 后只看 drawer，立即关闭。
- 等待条件: drawer 可见，焦点进入 panel 后再念。
- 画面必须看到: `Comments`、`Team discussion`、`Comment body` 或 `Tasks`。
- 画面不能出现: rehearsal-labelled task title、密码、任何新的 comment/task。
- 现在念: Cue 14-15；英文字幕: 与 Cue 14-15 完全一致。
- Requirement mapping: requirements.txt:14-15; collaboration evidence。
- 证据类型: Direct UI entry point + Honest limitation。
- 本段优势: 证明协作入口存在，同时不污染线上状态。
- 禁止声称: 不说本 take 创建了 comment 或 task；不说 task 被 Accept。
- 退出条件: 所有 drawer 关闭。
- 如果状态不同: 当前 Tasks drawer 含 rehearsal-labelled items 时，立刻关闭并跳到 Beat 08。
- 剪辑建议: 这段可缩短为 Comments drawer 的 4-6 秒插入。

### Beat 08 - Cut to Clinician authority

- 时间: `02:32-02:51`; 当前角色: Clinician; 录制状态: 停录切换后继续
- 页面起点: 镜头外完成 Clinician 登录，保持 `English`、`Sarah Tan`、`Clinician view` 和 `Up to date`。
- 中文操作:
  1. 开始新 take 前确认没有登录页或密码框。
  2. 找到当前可见的 conflict，打开 review drawer；只展示 decision controls，不提交。
- 等待条件: Clinician drawer 完整渲染，控件文字稳定。
- 画面必须看到: Clinician-only adjudication controls、两个 source、source/review boundary。
- 画面不能出现: Staff 页面、错误患者、实际 clinical decision 提交。
- 现在念: Cue 16-17；英文字幕: 与 Cue 16-17 完全一致。
- Requirement mapping: #10, #13; RBAC evidence。
- 证据类型: Direct UI if manually reverified; otherwise Honest limitation。
- 本段优势: 清楚区分 Staff inspect 与 Clinician adjudicate。
- 禁止声称: 当前会话未重新登录时，不说 exact-commit Clinician canary 已完成。
- 退出条件: 控件展示完毕，关闭 conflict drawer。
- 如果状态不同: 标记 `REVERIFY AFTER MANUAL LOGIN BEFORE RECORDING`，不要用旧截图冒充当前 take。
- 剪辑建议: 角色切换使用干净 cut，不录 sign-out/login。

### Beat 09 - Explain concurrency, History, Compare, and Revert

- 时间: `02:51.5-03:40`; 当前角色: Clinician; 录制状态: 继续
- 页面起点: Clinician timeline。
- 中文操作:
  1. 通过 Brief 或 stable timeline entry 说明 stale same-section write 的 409 结果；不注入线上冲突。
  2. 打开当前 entry 的 `History`，选择页面实际存在的 earlier version。
  3. 点击 `Compare`，等待 `Before`/`After`；只有台本明确且状态适合时才展示 `Revert`，本次默认不点。
- 等待条件: History rows、Compare result 和 current row 可读。
- 画面必须看到: earlier/current distinction、Before、After、版本历史保留。
- 画面不能出现: 固定 `v1 -> v2` 叙述、删除历史、数据库控制台。
- 现在念: Cue 18-22；英文字幕: 与 Cue 18-22 完全一致。
- Requirement mapping: #10, #16; `test_concurrent_edits.py`, `test_revision_history.py`。
- 证据类型: Direct UI + Automated test evidence。
- 本段优势: 覆盖 revision/concurrency 的可解释结果，不制造 live failure injection。
- 禁止声称: 不说这是 CRDT 或 real-time co-editing。
- 退出条件: Compare 已读完，关闭 History。
- 如果状态不同: 若没有 earlier row/Compare，保留 History 画面，口播 test evidence，不重复点击。
- 剪辑建议: Revert 默认不录；如实际录制，单独短镜头并确认新版本出现。

### Beat 10 - Open the patient publication gate

- 时间: `03:40.5-04:01`; 当前角色: Clinician; 录制状态: 继续
- 页面起点: Timeline entry 的 `Prepare patient update`。
- 中文操作:
  1. 点击 `Prepare patient update` 一次，等待 `Patient publication review`。
  2. 保持 panel 顶部和 `Draft` 状态在画面内；不要 Save、Approve 或 Publish。
- 等待条件: source evidence、draft state 和 dosage section 完整出现。
- 画面必须看到: `Patient publication review`、`Workflow state: Draft`、`IMMUTABLE SOURCE`。
- 画面不能出现: Publish confirmation、外部短信/WhatsApp、真实患者信息。
- 现在念: Cue 23-24；英文字幕: 与 Cue 23-24 完全一致。
- Requirement mapping: #11-12; `PATIENT_PUBLICATION_BOUNDARY.md`。
- 证据类型: Direct UI。
- 本段优势: 直接展示 Accept 与 Publish 的分离。
- 禁止声称: 不说 Draft 已发送给患者。
- 退出条件: source evidence 和 Draft 均稳定可读。
- 如果状态不同: 若当前状态不是 Draft，按实际状态描述，不强行回到 Draft。
- 剪辑建议: 用 2 秒静止 pause 让评委读标题。

### Beat 11 - Explain dosage and explicit publish gates

- 时间: `04:01.5-04:32`; 当前角色: Clinician; 录制状态: 继续
- 页面起点: publication review panel。
- 中文操作:
  1. 指向 `Accepting an AI suggestion does not publish it to the patient`。
  2. 指向 `MEDICATION DOSAGE CHECK`、source/draft dosage 和 disabled/available controls；不要输入 draft。
  3. 只展示 `Approve`/`Publish` 的分离逻辑；不执行写动作。
- 等待条件: dosage status 和 patient-facing draft 都稳定。
- 画面必须看到: Draft、immutable evidence、dosage status、approval/publish separation。
- 画面不能出现: unsupported dosage 被自动修正、external delivery receipt。
- 现在念: Cue 25-27；英文字幕: 与 Cue 25-27 完全一致。
- Requirement mapping: #11-12; publication tests。
- 证据类型: Direct UI + Automated test evidence。
- 本段优势: 展示“Accept is not Publish”和 fail-closed dosage boundary。
- 禁止声称: 不说 dosage interpretation 是 general medical NLP，也不说已经发送。
- 退出条件: 关闭 publication review，不改变状态。
- 如果状态不同: 若没有 dosage evidence，展示页面的 `No dosage evidence`，不要编造一个数字。
- 剪辑建议: 这一段是评分核心，宁可延长停留，不要快切。

### Beat 12 - Show the Voice fixture boundary

- 时间: `04:32.5-04:53`; 当前角色: Staff 或 Clinician; 录制状态: 继续
- 页面起点: `Voice note` panel。
- 中文操作:
  1. 确认 `Review a pre-recorded care conversation`、`About this example` 和 audio controls。
  2. 如音频未播放，点击 native play 一次；只等待播放状态，不点击 `Create care-note suggestion`。
  3. 如已有 result，直接展示现有 transcript/source；不要重复生成。
- 等待条件: audio metadata 稳定；若 result 存在，transcript/source 完整。
- 画面必须看到: `Voice note`、pre-recorded synthetic disclosure、audio、prepared transcript（如已有）。
- 画面不能出现: microphone/upload、provider key、ASR quality claim。
- 现在念: Cue 28-29；英文字幕: 与 Cue 28-29 完全一致。
- Requirement mapping: requirements.txt:45-48; Voice evidence。
- 证据类型: Direct UI if result exists; otherwise Honest limitation。
- 本段优势: 诚实展示 Level-C fixture 的可见边界。
- 禁止声称: 不说 prepared transcript 是 ASR、diarization 或 speaker attribution 结果。
- 退出条件: Voice take 完成，停止 audio 或离开 panel。
- 如果状态不同: 当前线上没有 result 时跳到 Brief/evidence，不创建新 suggestion；本段可用 supplementary clip 替换。
- 剪辑建议: Voice 只保留 15-20 秒，避免抢占核心 provenance/publication 时间。

### Beat 13 - Explain provider failure and redaction evidence

- 时间: `04:53.5-05:13`; 当前角色: Staff/Clinician; 录制状态: 继续
- 页面起点: 稳定产品页或 Iteration Brief/evidence 页面。
- 中文操作:
  1. 不在 Render 注入 provider failure；打开 Brief 中 safe logging/provider boundary 对应段落。
  2. 指向“failure is explicit / existing records remain usable”的文字，不打开 dashboard 或日志。
- 等待条件: Brief 页面加载后无滚动遮挡。
- 画面必须看到: redaction-before-provider、bounded failure、metadata-only logging 的解释。
- 画面不能出现: raw prompt/response、API key、真实日志行、假造的 503。
- 现在念: Cue 30-31；英文字幕: 与 Cue 30-31 完全一致。
- Requirement mapping: #3, #4, #8, #9; `test_uvicorn_access_logging.py`, provider tests。
- 证据类型: Automated test + Honest limitation。
- 本段优势: 用证据说明 failure path，而不是制造线上事故。
- 禁止声称: 不说已经在视频中真实注入 provider outage。
- 退出条件: Brief 证据点说完，回到 stable page。
- 如果状态不同: 页面没有 failure UI 就直接使用 explanation branch，不重复刷新。
- 剪辑建议: 可把这段剪成 Brief 卡片与产品页之间的短切。

### Beat 14 - Show Patient projection

- 时间: `05:13.5-05:33`; 当前角色: Patient; 录制状态: 停录切换后继续
- 页面起点: 镜头外完成 Patient 登录，保持 `English`、`Sarah Tan`、`Patient view`。
- 中文操作:
  1. 确认页面显示 `Your care summary` 或患者可见的 current care projection。
  2. 缓慢滚动到 Patient Voice；不打开 source、comments、tasks 或内部 timeline controls。
- 等待条件: Patient projection 和 safe Voice fixture 稳定。
- 画面必须看到: patient-facing content、当前共享照护信息、患者角色。
- 画面不能出现: Glance、internal source、raw AI、团队讨论、任务或临床审核控件。
- 现在念: Cue 32-33；英文字幕: 与 Cue 32-33 完全一致。
- Requirement mapping: #1, #12, distinct outputs。
- 证据类型: Direct UI if manually reverified; otherwise Automated test + required recheck。
- 本段优势: 把 audience-specific projection 作为最终 privacy proof。
- 禁止声称: 不说患者可访问内部 clinical workspace。
- 退出条件: Patient safe projection 可读，准备 privacy boundary。
- 如果状态不同: 若 Patient session 未在镜头外确认，标记 reverify，不用旧截图。
- 剪辑建议: 不录 sign-out/login；用 clean cut 连接角色。

### Beat 15 - Hold the Patient privacy boundary

- 时间: `05:33.5-05:53`; 当前角色: Patient; 录制状态: 继续
- 页面起点: Patient current care projection。
- 中文操作:
  1. 鼠标指向页面可见的 patient-facing summary 和 Voice 区域。
  2. 不点击任何内部入口；等待观众看清页面没有 Staff/Clinician controls。
- 等待条件: 页面无 loading、error 或意外 drawer。
- 画面必须看到: safe projection、无内部控件。
- 画面不能出现: internal source span、conflict detail、comments/tasks/history、raw AI。
- 现在念: Cue 34-35；英文字幕: 与 Cue 34-35 完全一致。
- Requirement mapping: #1, #3, #12; `test_rbac_scope.py` 和 publication tests。
- 证据类型: Direct UI if manually reverified; otherwise Automated test + Honest limitation。
- 本段优势: 以“看不见什么”说明患者隔离，而不是只展示一个角色标签。
- 禁止声称: 不说这是 independent privacy certification。
- 退出条件: Cue 35 完成，切回 Brief 或 stable workspace。
- 如果状态不同: 任何内部内容出现都立即停止 take，不尝试用裁剪掩盖。
- 剪辑建议: 留出 2 秒静止画面，让 privacy boundary 可被检查。

### Beat 16 - State honest gaps

- 时间: `05:53.5-06:34`; 当前角色: Brief / stable workspace; 录制状态: 继续
- 页面起点: 3-page Iteration Brief 的 limitation 页面。
- 中文操作:
  1. 打开已核对的本地 Brief 或等价 evidence 页面，不打开 Render dashboard。
  2. 只指向四类 limitation：phone-only onboarding、multilingual ASR、external delivery receipt、general medication interpretation。
  3. 不逐字朗读整张表，Cue 36-39 期间保持表格和 status visible。
- 等待条件: Brief 页面无分页跳动，字幕不遮挡关键信息。
- 画面必须看到: SURVIVES/PARTIAL/DOES NOT 的诚实分类和 abstention language。
- 画面不能出现: “everything is production ready” 或未经限定的 clinical claim。
- 现在念: Cue 36-39；英文字幕: 与 Cue 36-39 完全一致。
- Requirement mapping: scenarios 1, 5-9, 11, overall capability list。
- 证据类型: Honest limitation。
- 本段优势: 直接响应评审最看重的 overclaiming 风险。
- 禁止声称: 不把未实现功能包装成 roadmap 已完成。
- 退出条件: limitation 口播结束，切到最终 evidence。
- 如果状态不同: 以当前 PDF/Brief 实际文字为准，不补充页面没有的指标。
- 剪辑建议: 这一段可以用 2-3 个画面切换，但不要滚动过快。

### Beat 17 - Point to repository and quality evidence

- 时间: `06:34.5-07:04`; 当前角色: stable workspace / repository page; 录制状态: 继续
- 页面起点: 可安全展示的 README、GitHub source tree 或 Brief evidence summary；不要展示 settings/secrets。
- 中文操作:
  1. 指向 required tests、README setup、PostgreSQL 18 CI 和 Render live evidence 的链接或文字。
  2. 不打开 workflow secret、Render Environment、database connection 或 raw logs。
- 等待条件: repository/source tree 清晰可读，页面没有登录凭据。
- 画面必须看到: test names、194 backend tests、86.62% coverage、PostgreSQL CI、Render deployment。
- 画面不能出现: cookie/token、MP4、ZIP、password file 或未验证 benchmark 数字。
- 现在念: Cue 40-42；英文字幕: 与 Cue 40-42 完全一致。
- Requirement mapping: deliverables, #2-4, #10, #16。
- 证据类型: Automated test + Direct documentation。
- 本段优势: 将演示价值连接到可审查的代码和测试，而非只依赖视频。
- 禁止声称: 不说 86.62% 是 clinical validation 或 hosted P95。
- 退出条件: Cue 42 结束，回到干净 product screen。
- 如果状态不同: 用 README/evidence 页面替代 GitHub 页面；不要临场寻找 settings。
- 剪辑建议: GitHub 停留不超过 8 秒，避免破坏叙事节奏。

### Beat 18 - Close with the disclosed gap

- 时间: `07:04.5-07:22`; 当前角色: stable workspace; 录制状态: 继续后停止
- 页面起点: stable English product screen，所有 drawer 关闭。
- 中文操作:
  1. 鼠标停在空白处，念 Cue 43-44。
  2. Cue 44 结束后停 1 秒，再点击录屏软件的 `Stop recording`；不要再操作网页。
- 等待条件: final subtitle cue 完整结束。
- 画面必须看到: synthetic data disclosure、human review boundary、稳定产品页。
- 画面不能出现: 录屏控制台、文件路径、密码或提交邮箱。
- 现在念: Cue 43-44；英文字幕: 与 Cue 43-44 完全一致。
- Requirement mapping: communication, evidence integrity, submission boundary。
- 证据类型: Honest limitation + Direct close。
- 本段优势: 明确 benchmark gap 是 disclosed supplementary gap，不假装完成。
- 禁止声称: 不说 hosted authenticated benchmark 已通过，不说 `real-clinic-live1` 存在。
- 退出条件: 视频文件保存后进入人工 QA；本文件不生成 ZIP 或邮件。
- 如果状态不同: 若录屏软件未确认保存，先确认文件存在，不重录网页。
- 剪辑建议: 最后一帧保留 stable workspace，不加入 password/login cut。

## Emergency fallback card

| Situation | 操作 |
| --- | --- |
| Protected conflict 不在第一项 | 只刷新一次；仍不在则停录，不删卡、不改分数、不改数据库。 |
| Drawer 不打开 | 停止当前 take，刷新后从该 Scene 开头重录；不重复点击写按钮。 |
| Tasks 出现测试标题 | 立即关闭，不展示、不删除；改用 collaboration evidence branch。 |
| Voice 没有 result | 不点击 `Create care-note suggestion`；展示 prerecorded disclosure，或剪入已有 supplementary clip。 |
| Clinician/Patient session 失效 | 停录，镜头外人工登录；不读密码文件、不代填密码。 |
| Patient 页面出现内部内容 | 立即停止并标记 P0 privacy blocker；不要用剪辑遮盖。 |
| Render cold start/loading | 停录等待页面稳定；不要保留 loading 画面冒充成功。 |
| 版本号或 status 与台本不同 | 使用页面实际文字；不写死版本、不强行改变 synthetic state。 |
| 出现密码/通知/DevTools | 立即停止并删除该 take；重新整理窗口后再录。 |

## Pronunciation quick help

- provenance: **PROV-uh-nuhns**
- immutable: **ih-MYOO-tuh-bul**
- adjudication: **uh-joo-duh-KAY-shun**
- contradiction: **kon-truh-DIK-shun**
- abstain: **ab-STAYN**
- diarization: **dy-uh-rye-ZAY-shun**
- concurrency: **kun-KUR-un-see**

## After recording

1. Keep the original recorded MP4 byte-for-byte unchanged; do not rename or transcode it.
2. Complete [`REAL_CLINIC_DEMO_VIDEO_QA.md`](REAL_CLINIC_DEMO_VIDEO_QA.md) after watching the full take.
3. Do not create the final ZIP, MANIFEST, or email until video QA is complete.
