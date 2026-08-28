# Nightingale 最终录制 Operator Runbook

录制时以 [`DEMO_RECORDING_MASTER_ZH_EN.md`](DEMO_RECORDING_MASTER_ZH_EN.md) 为唯一操作主文件；本文件保留为中文参考。

目标时长：约 4:55（允许 4:40–4:55）；任务和 AI review 的逐步动作以 Master Runbook 为准。

这是中文操作参考文件。所有操作提示均为中文；网页按钮、字段和状态保留实际 English
label；需要念的内容以 Master Runbook 中的 English narration 和 SRT cue 为准。角色顺序固定
为 **Staff → Clinician → Patient**。

## 通用规则

- 地址使用现有 HTTPS 部署；页面语言选 `English`，患者选 `Sarah Tan`。
- 登录、密码和角色切换都在镜头外完成。密码框、自动填充、Cookie、配置和地址栏敏感信息
  永远不能出现在画面中。
- 页面上的 clinical note 原文保持原始语言，不要临场翻译；所有输入只用 synthetic rehearsal
  sentence。
- 每个镜头先等目标状态稳定，再开始旁白；旁白时鼠标移到空白处。
- 录制前关闭 `Guide`、`Source`、`Comments`、`History`、`Task` drawer、浏览器通知和
  DevTools。
- 当前线上数据已经经历过 rehearsal；版本号、卡片状态和 Voice result 以录制时页面为准，
  不把某个版本号或 suggestion 状态写死。

## 镜头顺序

### 1. Staff 开场：共享工作区

镜头外登录 Staff，选择 `Sarah Tan`，确认 `English`。等待 `Up to date`，画面稳定后展示
`Shared Care Note`、`Staff view` 和共享照护工作区。旁白见脚本镜头 1。

### 2. Glance View 与来源

1. 找到 `Glance View` 中当前页面实际显示的 AI-assisted card。
2. 指出内容、`Next step`、`Needs review`/`Reviewed`、item kind、`Risk flag`/`No risk
   flag` 和 `Priority`。
3. 展开 `Why is this here?`，让 priority disclaimer 清晰可读。
4. 点击 `Open source`，等待 `Original source` 和时间线高亮片段出现。
5. 保持 `Technical details` 折叠；主画面只展示记录类型、日期、版本和高亮原文。

如果当前卡片已经是 `Reviewed`，选择另一张仍显示 `Needs review` 的卡片。不要口播固定卡片
名称、固定版本或技术字段。

### 3. Voice note

1. 向下找到 `Voice note`，确认 `About this example` 默认折叠。
2. 如果已有 result，直接展示；没有 result 时先播放 native audio，确认播放器时间前进。
3. 只点击一次 `Create care-note suggestion`，等待 `Suggestion status: Ready for review`。
4. 点击一个 timestamped transcript segment，再点击 `View source`。
5. 旁白只描述预录 synthetic care conversation、prepared timestamped transcript、reviewable
   suggestion 和 source link。不要把 prepared transcript 说成 ASR 质量证据。

如果处理失败，停止该镜头并记录；不要把失败剪成成功，也不要重复提交。

### 4. Staff note、Comments 和 mention

1. 关闭 Source，找到 `Staff note`，点击 `Edit`。
2. 在原有内容末尾新增一行 synthetic rehearsal sentence，点击 `Save revision`，等待版本更新。
3. 点击 `Comments`，等待 contextual drawer 立即出现。
4. 在 `Comment body` 输入 `@`，从可见菜单选择 `@Clinician A`。
5. 在 mention 后输入 `Synthetic rehearsal: please review this follow-up.`，点击 `Add comment` 一次。
6. 等待新增 root comment、`Mentioned teammates: @Clinician A` 和 `Reply`/`Resolve` 出现。

只提交一次；不要输入隐藏 user ID。root comment 必须在下一节的 `Assign task` 前可见。

### 5. Discussion 和 Assigned task

1. 在刚才的 root comment 上按实际状态点击 `Resolve` 或 `Unresolve` 一次；等待 `Resolved` 或 `Open`。
2. 点击该 comment 上的 `Assign task`，不要从其他 entry 重新创建。
3. 等待 `Tasks` drawer 显示 comment/entry context、`Task title` 和 `Assign to`。
4. 点击 `Task title`，输入 `Review synthetic follow-up plan`。
5. 在 `Assign to` 中选择 `Clinician A · Clinician`。
6. 确认 title 和 assignee 后点击 `Create task` 一次，等待 task card 出现。
7. 点击 `Close tasks`，回到 `Glance View`，等待新 `Assigned task` 进入 top-six。
8. 指向 `Clinician A`、`Open` 和 `Open task`；不要把通用 `Reviewed` presentation 说成 task acceptance。
9. 关闭 drawer，停录；镜头外点击 `Sign out`，登录 Clinician。

Task 状态机是 `Open → In progress → Done`；不要说 `Accept task`、`Reject task` 或 task 默认已接受。
这一节只能点击一次 `Create task`。如果 task 没有进入 top-six，不重复创建，只回到 Tasks drawer 展示并如实说明。

### 6. Clinician task、AI review、History 和 Revert

1. 页面稳定后确认 `Clinician A`、`Clinician view` 和 `Sarah Tan`。
2. 在 `Glance View` 找到 `Review synthetic follow-up plan` 的 `Assigned task`，点击 `Open task`。
3. 等待 `Tasks` drawer、assignee `Clinician A` 和当前 `Open` 出现。
4. 将 `Status` 从 `Open` 改为 `In progress`，等待该状态真正显示；不要点击 `Done`。
5. 关闭 Tasks，向下到 `Clinician plan`，点击 `Edit`，追加 synthetic plan sentence 并点击 `Save revision`。
6. 点击 `History`，选择实际可见的 earlier version，点击 `Compare`，等待 `Before` 和 `After`。
7. 如 `Revert` 可用且录制计划包含它，点击一次并确认新版本出现、旧 rows 保留；否则跳过。
8. 关闭 History/Source，找到第一张实际显示 `Accept`/`Reject` 的 AI suggestion；录屏已开始且页面稳定后点击 `Accept` 一次。
9. 等待 status 变为 `Reviewed`、按钮消失且 card 保留。
10. 找到第二张仍显示 `Accept`/`Reject` 的 AI suggestion，点击 `Reject` 一次。
11. 等待该 suggestion 离开 active `Glance`；确认原始 source 仍可查看，不说 source 被删除。

Accept/Reject 只属于 AI-generated suggestion，且只在 Clinician 页面显示；Task 的 `Open → In progress → Done`
不能和 AI review status 混用。每个写操作只点击一次；状态已变化时按实际候选录制，不改数据匹配旧台本。

不要假设 `v1 → v2`，也不要直接修改数据库。

### 7. Historical context 与 UX-01

1. 关闭 History、Comments 和 Source。
2. 找到 `Historical context`，展开 `How historical context is organised`。
3. 指出 `Recent context`、`Earlier context` 和 `Historical summary`。
4. 点击任意 `View original record`，等待页面滚到对应的原始时间线位置。
5. 移开鼠标，念脚本中的 UX-01 英文句子。

这里展示的是摘要到原始记录的导航，不要把它说成 source panel 或 exact-span panel。

### 8. Patient privacy 与 Patient Voice

1. 停录，镜头外 `Sign out` 并登录 Patient。
2. 确认 `Patient view`、`Sarah Tan` 和 `Your care summary`。
3. 展示患者时间线和 `Voice note`；如没有 result，播放 patient audio 后只点击一次
   `Create care-note suggestion`。
4. 确认只显示患者可见的摘要、指引和患者对话；内部 Glance、团队讨论、任务和临床审核
   控件不出现。

如果 Patient session 不稳定，删除整个镜头并重新录制；不要从内部页面推断患者隐私结果。

### 9. 收尾

关闭所有 drawer，停在稳定的 English workspace，指向 synthetic-only disclosure 和
source/review boundary，念脚本镜头 9。不要打开配置、日志、PDF、ZIP、MANIFEST 或外部服务
控制台。

## 会修改线上 synthetic state 的动作

| 动作 | 录制规则 |
| --- | --- |
| `Open source`、`Close source`、`History`、`Compare`、`View original record` | 只改视图；可重复 |
| `Create care-note suggestion` | 每个 Voice sample 最多一次 |
| `Save revision` | Staff 和 Clinician 各按脚本点击一次 |
| `Add comment` | 只提交一次 synthetic comment |
| `Create task` | 只提交一次；title 为 `Review synthetic follow-up plan`；assignee 为 Clinician A |
| Task `Open` → `In progress` | Clinician 只切换一次；`Done` 仅在明确计划时执行 |
| AI suggestion `Accept` | Clinician 只点击一次；等待 `Reviewed`，card 保留、source 不变 |
| AI suggestion `Reject` | Clinician 只点击一次；等待 suggestion 离开 active Glance，source 不删除 |
| `Resolve`/`Unresolve` | 按当前状态完成一次；如有时间可展示来回切换 |
| `Pin`/`Unpin` | 可选，不在本轮主路径；不为匹配旧台本重复写入 |
| `Revert` | 只点击一次；保留所有历史 |

## 录制结束后

1. 完整观看视频一次。
2. 按 [`DEMO_VIDEO_QA.md`](DEMO_VIDEO_QA.md) 检查顺序、字幕、标签、隐私和事实边界。
3. 视频通过 QA 前，不生成最终 PDF/ZIP/MANIFEST，不 push，不发邮件。
