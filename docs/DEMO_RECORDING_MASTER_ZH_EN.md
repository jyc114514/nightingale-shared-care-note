# Nightingale 录制主控文件（中文操作 / English narration）

这是正式录制时唯一需要打开的操作主文件。中文负责告诉操作者“现在做什么、等什么、看什么”；
网页上的按钮、字段和状态保留真实的 English label；口播和字幕使用 English。独立的
DEMO_SUBTITLES_EN.srt 仍然保留，作为剪辑软件导入文件；其他 Runbook、Script、Cue Card、
Shotlist、State Prep 和 QA 文件都是参考或审计材料。

目标成片：4:30 · 40 个 recording beats · 40 个 subtitle cues · 105–120 words per minute
页面语言：English · 患者：Sarah Tan · 角色顺序：Staff → Clinician → Patient
数据边界：只使用内置 synthetic data；clinical note 原文不翻译、不改写。

## 使用方式和事实边界

1. 录制前先完成 A 部分 checklist，再按 B 部分快速表定位镜头，最后逐 beat 执行 C 部分。
2. 每个 beat 的“现在念”和“英文字幕”是同一段文字；SRT 的换行只是显示换行，不改变文字。
3. 旁白只描述页面实际可见的产品价值。不要把准备好的文字记录说成 live transcription、模型
   accuracy 或自动角色识别，也不要把建议说成诊断。
4. 不要为了匹配某个旧版本、旧状态或旧截图而重置、删除、重新准备数据或重复提交。
5. 页面慢时只保留能证明功能完成的等待；网络错误、冲突或按钮缺失时停止当前 take，按
   “如果状态不同”处理，不要把失败剪成成功。

## A. 录制前五分钟 checklist

### 设备、窗口和录屏

- [ ] 用 Chrome 打开现有 HTTPS 地址
      https://nightingale-shared-care-note.onrender.com；先等页面完全显示。
- [ ] Chrome zoom 为 100%；建议录制窗口内容为 1440×900，文字可读且不裁切右侧 Source。
- [ ] 关闭浏览器通知、下载栏、书签栏和 DevTools；不要让地址栏、自动填充或密码框进入画面。
- [ ] 检查屏幕录制软件的 capture source、系统声音和麦克风；试听一小句 English narration。
- [ ] 确认录屏文件有足够磁盘空间；开录前不要打开 Render dashboard、配置页或日志页。

### 页面和状态

- [ ] 镜头外完成 Staff 登录；登录页和密码输入永远不录。
- [ ] 页面语言为 English；患者下拉框为 Sarah Tan。
- [ ] Staff 页面显示 Staff A、Staff view 和 Record status: Up to date；若仍在加载或显示
      reconnecting，镜头外等待或刷新后再开始。
- [ ] 关闭 Guide、Source、Comments、History、Task drawer，以及任何临时错误提示。
- [ ] 现场确认 Glance 的当前 card、status、action、risk 和 Priority；不写死卡片名称。
- [ ] 现场确认 Voice 是否已有 result、History 中可用的 earlier version、Comments 中是否已有
      root discussion；已有 result 就只展示，不重复提交。
- [ ] 预先准备两个镜头外角色切换点：Staff → Clinician、Clinician → Patient。
- [ ] 确认画面不会拍到密码、自动填充、Cookie、环境变量、API key、账户信息或 Render dashboard。

### 本轮固定 synthetic 输入

输入前先点击对应字段，不要删除原有 clinical content；可在文本末尾新增一行：

- Staff revision：Synthetic staff rehearsal: review the pending follow-up.
- Clinician revision：Synthetic clinician rehearsal: confirm the next follow-up plan.
- Comment after selecting the visible mention：@Clinician A Synthetic rehearsal: please review this follow-up.
- Optional task title（默认短片只打开 drawer，不创建 task）：Synthetic follow-up task。

这些句子不含真实姓名、号码或其他 PHI；如果页面已有相同或更好的 synthetic 内容，按状态分支
展示，不要再次保存。

## B. 一页式快速 Cue Sheet

| 镜头 | 时间 / cues | 当前角色 | 页面起点 | 下一次要点击的按钮 | 要等待的状态 | 旁白开头 | 结束条件 / 下一个镜头 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 Staff opening | 00:00–00:26 / 01–04 | Staff A | English workspace 顶部 | 无；先展示页面 | Staff A、Staff view、Up to date | Nightingale brings a shared | 工作区稳定，进入 Glance |
| 2 Glance + source | 00:26–01:10 / 05–11 | Staff A | 顶部向下到 Glance View | Why is this here? → Open source → Close source | Original source、timeline exact highlight | Staff starts with Glance | Source 关闭且 patient query 保留，进入 Voice |
| 3 Voice note | 01:10–01:47 / 12–16 | Staff A | 向下到 Voice note | 播放、Create care-note suggestion、transcript、View source | 音频 ready、Ready for review、View source | Here is a Voice note | Voice source 可见，进入 Staff note |
| 4 Staff note + Comments | 01:47–02:15 / 17–20 | Staff A | Source 关闭，Timeline 的 Staff note | Edit → Save revision → Comments → Add comment | textarea、saved version、Team discussion、mention | Back in Staff | comment 和 mention 可见，进入协作状态 |
| 5 Collaboration | 02:15–02:34 / 21–23 | Staff A | Comments drawer 或 Staff/Glance | Resolve/Unresolve → Assign task → Pin/Unpin | Resolved/Open、Tasks、Unpin/Pin | Resolve and Unresolve | 所有 drawer 关闭，停录切换 Clinician |
| 6 Clinician review | 02:34–03:10 / 24–28 | Clinician A | Clinician view 顶部 | Edit → Save revision → History → Compare | Current、Before/After；Revert 若可用 | Now I switch to Clinician | History 结果稳定，进入 context |
| 7 Historical context | 03:10–03:44 / 29–33 | Clinician A | Historical context | 展开 details → View original record | Recent/Earlier/Historical summary、原始 timeline | Historical context brings | UX-01 事实念完，停录切换 Patient |
| 8 Patient privacy | 03:44–04:12 / 34–37 | Sarah Patient | Patient view 顶部 | 无；必要时只点一次 Voice processing | Your care summary、patient Voice、无内部控件 | Finally, I switch to Patient | 患者页面稳定，进入收尾 |
| 9 Product close | 04:12–04:30 / 38–40 | 任一稳定内部角色 | 所有 drawer 关闭 | 无 | English workspace 稳定 | Across the workspace | 念完 cue 40 后停止录制 |

## C. 完整逐拍录制台本

### 镜头 1 — Staff opening（00:00–00:26）

目标：先让评委看到这是一个可读的 shared workspace，而不是登录页或技术控制台。

#### Beat 01 — Start on the stable workspace

- 时间：00:00–00:07
- 当前角色：Staff A
- 录制状态：开始录制
- 页面起点：镜头外已登录；页面顶部已显示 English、Sarah Tan、Staff A 和 Staff view。
- 中文操作：
  1. 不点击任何页面控件，确认页面主体已经稳定。
  2. 点击屏幕录制软件的 Start recording。
  3. 鼠标移到工作区空白处。
- 等待：
  - 等待 Shared Care Note、Staff view 和 Record status: Up to date 同时可见。
- 画面确认：
  - 必须看见 Shared Care Note、Staff A、Staff view。
  - 不应看见密码框、Guide、drawer、Render dashboard 或错误提示。
- 现在念：
  > Nightingale brings a shared care record into one clear workspace for this team.
- Subtitle cue：01 · 00:00:00,000–00:00:07,000
- 英文字幕：Nightingale brings a shared care record into one clear workspace for this team.
- 说话与动作关系：页面稳定后先开始录制，再念；念完保持鼠标不动。
- 本段优势：用一个稳定的起始画面建立产品上下文和 synthetic-only 安全边界。
- Requirement mapping：requirements.txt:3–5, 74–85
- 退出条件：cue 01 念完且 Header 与 Staff view 仍稳定。
- 如果状态不同：若不是 Staff A 或仍显示 Sign in，停止录制并回到镜头外登录；若状态不是
  Up to date，只等待或镜头外刷新，不把登录页录进去。

#### Beat 02 — Confirm the Staff perspective

- 时间：00:07–00:14
- 当前角色：Staff A
- 录制状态：继续录制
- 页面起点：保持页面顶部。
- 中文操作：
  1. 让鼠标短暂指向右上角的 Staff A 和 Staff view。
  2. 不点击 Sign out 或 Language。
  3. 鼠标移回空白处。
- 等待：
  - 等待 Record status: Up to date 不变。
- 画面确认：
  - 必须看见 Staff A、Staff view、Sarah Tan。
  - 不应看见 Patient view、Clinician view 或登录表单。
- 现在念：
  > I begin as Staff with Sarah Tan, then wait for the workspace to settle.
- Subtitle cue：02 · 00:00:07,000–00:00:14,000
- 英文字幕：I begin as Staff with Sarah Tan, then wait for the workspace to settle.
- 说话与动作关系：指向角色后再念，念完移开鼠标。
- 本段优势：明确 Staff 是 brief 要求的起始视角，并确认患者范围。
- Requirement mapping：requirements.txt:3–5, 8, 34–40
- 退出条件：角色和患者名称清晰可读。
- 如果状态不同：若患者不是 Sarah Tan，先停录并在镜头外选择；若出现 stale data 或
  reconnecting，等稳定后重录本 beat。

#### Beat 03 — Show the workspace structure

- 时间：00:14–00:20
- 当前角色：Staff A
- 录制状态：继续录制
- 页面起点：从页面顶部向下滚动到共享工作区和 Voice/Glance 上方区域。
- 中文操作：
  1. 向下滚动一小段，让 workspace heading 和第一批内容进入画面。
  2. 不打开 Guide 或任何 drawer。
  3. 鼠标移到右侧空白处。
- 等待：
  - 等待布局停止移动，Header 不再遮挡内容。
- 画面确认：
  - 必须看见共享工作区标题和至少一个内容区。
  - 不应看见技术配置、原始日志或空白 loading 区。
- 现在念：
  > The page separates notes, suggestions, actions, and review history.
- Subtitle cue：03 · 00:00:14,000–00:00:20,000
- 英文字幕：The page separates notes, suggestions, actions, and review history.
- 说话与动作关系：先滚动并等待稳定，再念。
- 本段优势：把产品的 information architecture 说清楚，帮助评委理解后续动作。
- Requirement mapping：requirements.txt:3–5, 10–13
- 退出条件：Glance View 入口在下一屏可找到。
- 如果状态不同：若滚动后出现 loading，停下等待；若内容为空，镜头外刷新一次，
  不要继续录制不完整画面。

#### Beat 04 — State the decision value

- 时间：00:20–00:26
- 当前角色：Staff A
- 录制状态：继续录制
- 页面起点：共享工作区已稳定，Glance View 即将进入画面。
- 中文操作：
  1. 保持当前滚动位置。
  2. 不点击任何 card。
  3. 鼠标移到空白处。
- 等待：
  - 等待下一段 Glance 标题和 card 区域可见。
- 画面确认：
  - 必须保持 English UI。
  - 不应出现具体版本号或需要临时解释的错误状态。
- 现在念：
  > The team can see what needs attention and why right now for everyone.
- Subtitle cue：04 · 00:00:20,000–00:00:26,000
- 英文字幕：The team can see what needs attention and why right now for everyone.
- 说话与动作关系：稳定后直接念；念完再进入下一 beat。
- 本段优势：用一句短句把 workspace 价值落到“attention and why”。
- Requirement mapping：requirements.txt:8–13
- 退出条件：Glance View 标题进入画面。
- 如果状态不同：若页面已有 source 或 Comments，先关闭后再继续；不要在录制中临时解释
  不相关的 drawer。

### 镜头 2 — Glance View 与 Original source（00:26–01:10）

目标：展示 priority、action、risk、source 和 immutable record connection；不把 priority 说成
medical risk。

#### Beat 05 — Enter Glance View

- 时间：00:26–00:32
- 当前角色：Staff A
- 录制状态：继续录制
- 页面起点：从 workspace 向下滚动到 Glance View。
- 中文操作：
  1. 向下滚动，直到 Glance View 和 What needs attention now 可见。
  2. 让整个 card grid 尽量进入画面。
  3. 鼠标移到 Glance 标题旁的空白处。
- 等待：
  - 等待 card grid 完成布局，并确认最多显示六项。
- 画面确认：
  - 必须看见 Glance View 和至少一张 card。
  - 不应看见 loading、错误 alert 或 Patient view。
- 现在念：
  > Staff starts with Glance View, where items are visible together at once.
- Subtitle cue：05 · 00:00:26,000–00:00:32,000
- 英文字幕：Staff starts with Glance View, where items are visible together at once.
- 说话与动作关系：滚动完成并稳定后再念。
- 本段优势：直接对应 brief 的 Glance View 和快速第一读。
- Requirement mapping：requirements.txt:8–9
- 退出条件：card grid 稳定且可读。
- 如果状态不同：若 Glance 为空，停录并镜头外等待数据；若超过六项，记录为产品异常，
  不在视频里自行解释。

#### Beat 06 — Read one card’s decision fields

- 时间：00:32–00:39
- 当前角色：Staff A
- 录制状态：继续录制
- 页面起点：Glance View card grid。
- 中文操作：
  1. 选择当前仍显示 Needs review 的 card；若没有，选择最能展示 action 的 card。
  2. 鼠标依次指向 content、Next step、status、item kind、risk 和 Priority。
  3. 不点击 Open source。
- 等待：
  - 等待 card 文字可读；不需要等待网络。
- 画面确认：
  - 必须看见内容、Next step、Needs review 或 Reviewed、item kind、Risk flag 或 No risk flag、
    Priority。
  - 不应把 Priority 标成 medical risk。
- 现在念：
  > Each card shows content, a next step, review status, item kind, risk, priority.
- Subtitle cue：06 · 00:00:32,000–00:00:39,000
- 英文字幕：Each card shows content, a next step, review status, item kind, risk, priority.
- 说话与动作关系：先指向字段，再念；念完鼠标移开。
- 本段优势：证明 card 不是单一分数，而是可执行的 decision summary。
- Requirement mapping：requirements.txt:8–13, 25–26
- 退出条件：至少一张 card 的字段清晰可读。
- 如果状态不同：若选中的 card 已是 Reviewed，仍可展示字段但不要声称它需要 review；
  换 card 时不要写死名称或状态。

#### Beat 07 — Explain Why is this here?

- 时间：00:39–00:45
- 当前角色：Staff A
- 录制状态：继续录制
- 页面起点：保持同一 Glance card。
- 中文操作：
  1. 点击 card 内的 Why is this here?。
  2. 等待 Base importance、Recent、Risk flag、Open action、Clinical confirmation、Team feedback
     和 Overall priority 出现。
  3. 鼠标移到 card 空白处。
- 等待：
  - 等待 details 展开；不要用浏览器刷新代替展开。
- 画面确认：
  - 必须看见 Priority helps organise the view. It is not a medical risk score.
  - 不应看见 raw implementation identifier。
- 现在念：
  > Priority organises the view; it is not a medical risk score to guide review.
- Subtitle cue：07 · 00:00:39,000–00:00:45,000
- 英文字幕：Priority organises the view; it is not a medical risk score to guide review.
- 说话与动作关系：先点击并等 details 出现，再念。
- 本段优势：明确 ranking 和 clinical risk 的边界，减少误读。
- Requirement mapping：requirements.txt:8–9, 28–31
- 退出条件：disclaimer 和至少部分 ranking factors 可见。
- 如果状态不同：若 summary 文字不同但仍表达同一 disclaimer，按实际文字念；若 details
  不能展开，保留 card 画面，跳过技术细节，不重复点击。

#### Beat 08 — Open the source

- 时间：00:45–00:50
- 当前角色：Staff A
- 录制状态：继续录制
- 页面起点：同一 Glance card，details 可保持展开或收起。
- 中文操作：
  1. 点击该 card 的 Open source。
  2. 鼠标立即移到页面空白处。
- 等待：
  - 等待右侧 Original source panel 出现；不要在请求未完成时再次点击。
- 画面确认：
  - 必须看见 Original source、记录类型、日期或版本信息。
  - 不应看见错误 alert、空白 Source 或登录页。
- 现在念：
  > I open the source of an AI-assisted note for careful team review.
- Subtitle cue：08 · 00:00:45,000–00:00:50,000
- 英文字幕：I open the source of an AI-assisted note for careful team review.
- 说话与动作关系：先点击，等 panel 出现后再念。
- 本段优势：把 Glance 的排序结果连接到可核验的 original record。
- Requirement mapping：requirements.txt:42–44, 87–89
- 退出条件：Original source panel 可见。
- 如果状态不同：若按钮 disabled，等待 source request 完成；若 card 已 Reviewed，仍可打开 source，
  但不要声称它仍是 pending。

#### Beat 09 — Reach the matching timeline entry

- 时间：00:50–00:56
- 当前角色：Staff A
- 录制状态：继续录制
- 页面起点：Original source 已打开，页面可能已平滑滚到 Timeline。
- 中文操作：
  1. 不拖动滚动条；等待页面自动平滑滚到对应 timeline entry。
  2. 让该 entry 的 Original source excerpt 进入中央画面。
  3. 鼠标移到 card 外。
- 等待：
  - 等待 timeline entry 的 source excerpt 和高亮 mark 出现。
- 画面确认：
  - 必须看见对应 entry、Original source excerpt 和高亮文字。
  - 不应把当前 entry 的普通文本误称为 source panel。
- 现在念：
  > The page takes me to the matching timeline entry for team verification.
- Subtitle cue：09 · 00:00:50,000–00:00:56,000
- 英文字幕：The page takes me to the matching timeline entry for team verification.
- 说话与动作关系：先等平滑滚动完成，再念。
- 本段优势：证明 source navigation 是可用的 workflow，不是静态 badge。
- Requirement mapping：requirements.txt:10–13, 42–44
- 退出条件：高亮 source excerpt 完整出现在对应 entry 内。
- 如果状态不同：若滚动还未结束，延长等待并删掉这段 silence；若没有 excerpt，停止 take，
  不用当前文本冒充 immutable source。

#### Beat 10 — Confirm the saved version

- 时间：00:56–01:02
- 当前角色：Staff A
- 录制状态：继续录制
- 页面起点：timeline 的 Original source excerpt 和右侧 Original source 同时可见。
- 中文操作：
  1. 让鼠标指向 source excerpt 的版本说明。
  2. 保持 Technical details 折叠。
  3. 不手动选择或改写高亮文字。
- 等待：
  - 等待 saved version、current record version 和 exact mark 同时稳定。
- 画面确认：
  - 必须看见高亮文字仍属于产生它的 saved version。
  - 不应出现内部 offset、hash 或 source ID 作为主标题。
- 现在念：
  > The highlighted passage stays tied to its original record version in context.
- Subtitle cue：10 · 00:00:56,000–00:01:02,000
- 英文字幕：The highlighted passage stays tied to its original record version in context.
- 说话与动作关系：先让版本说明可读，再念。
- 本段优势：向评委证明 AI suggestion 不会覆盖 human-authored source。
- Requirement mapping：requirements.txt:17–19, 42–44
- 退出条件：saved version 和 highlight 可核验。
- 如果状态不同：若当前版本已经变化，照实际显示的 saved/current version 说；不要强行恢复旧编号。

#### Beat 11 — Close Source without changing the record

- 时间：01:02–01:10
- 当前角色：Staff A
- 录制状态：继续录制
- 页面起点：Original source panel 和 inline source excerpt 可见。
- 中文操作：
  1. 点击右侧 panel 的 Close source。
  2. 等待 panel 和 inline source span 消失。
  3. 检查地址栏只在镜头外完成；确认 patient 参数保留、highlight 参数清除后，鼠标移回空白处。
- 等待：
  - 等待 Source panel、inline highlight 和 focus ring 都退出；不要马上滚到 Voice。
- 画面确认：
  - 必须回到普通 Timeline/Source 空状态。
  - 不应出现 record content 被修改的提示。
- 现在念：
  > The evidence is easy to inspect; closing Source leaves the record unchanged.
- Subtitle cue：11 · 00:01:02,000–00:01:10,000
- 英文字幕：The evidence is easy to inspect; closing Source leaves the record unchanged.
- 说话与动作关系：先关闭并等 UI 稳定，再念。
- 本段优势：同时证明 source 是可逆的 view action，且记录本身不变。
- Requirement mapping：requirements.txt:42–44, 87–89
- 退出条件：Source 关闭，进入 Voice note。
- 如果状态不同：若 Close source 不可见，先等待 panel；若 URL 仍有 highlight，镜头外刷新，
  不把 query cleanup 说成已完成。

### 镜头 3 — Voice note（01:10–01:47）

目标：展示 audio → prepared timestamped transcript → reviewable suggestion → source link 的
完整链路；不声称 live transcription。

#### Beat 12 — Find Voice note

- 时间：01:10–01:17
- 当前角色：Staff A
- 录制状态：继续录制
- 页面起点：Source 已关闭；向下滚动到 Voice note。
- 中文操作：
  1. 向下滚动直到 Voice note 和 Review a pre-recorded care conversation 可见。
  2. 确认 About this example 默认折叠。
  3. 鼠标移到 Voice panel 空白处。
- 等待：
  - 等待音频控件和 Length: 24.0s 稳定显示。
- 画面确认：
  - 必须看见 Voice note、Choose a conversation、音频控件和说明文字。
  - 不应看见录音按钮、上传控件或设置页。
- 现在念：
  > Here is a Voice note: a pre-recorded synthetic care conversation with audio.
- Subtitle cue：12 · 00:01:10,000–00:01:17,000
- 英文字幕：Here is a Voice note: a pre-recorded synthetic care conversation with audio.
- 说话与动作关系：先滚动并等待，再念。
- 本段优势：以准确的 prerecorded synthetic audio 边界介绍 Voice。
- Requirement mapping：requirements.txt:21–26, 45–48
- 退出条件：Voice panel 和音频 metadata 可见。
- 如果状态不同：若 panel 仍 loading，只保留 loading 状态的镜头外等待；若没有 Voice panel，
  停止该 take，不从内部角色推断患者页面。

#### Beat 13 — Play the audio and follow the transcript

- 时间：01:17–01:23
- 当前角色：Staff A
- 录制状态：继续录制
- 页面起点：Voice audio 已显示 Length: 24.0s。
- 中文操作：
  1. 如果音频暂停，点击 native play control 一次；如果已经播放，不要再次点击。
  2. 等待播放器时间从 0:00 前进几秒，然后按需要点击 native pause。
  3. 鼠标移到空白处。
- 等待：
  - 等待播放器显示正的播放进度、ready 状态且无媒体错误。
- 画面确认：
  - 必须看见音频正在或已经播放过。
  - 不应出现 microphone、upload 或 error 文案。
- 现在念：
  > I follow the prepared timestamped transcript at every step.
- Subtitle cue：13 · 00:01:17,000–00:01:23,000
- 英文字幕：I follow the prepared timestamped transcript at every step.
- 说话与动作关系：先让播放进度前进，再念；不要边点击边讲话。
- 本段优势：说明页面同时提供可听的 synthetic conversation 和可读的时间信息。
- Requirement mapping：requirements.txt:21–26, 45–48
- 退出条件：播放器进度已经前进，或已有 result 可继续。
- 如果状态不同：若浏览器阻止自动播放，手动点击 native play 一次；若音频 error，停止并
  记录失败，不重复点击 Create care-note suggestion。

#### Beat 14 — Show the reviewable suggestion state

- 时间：01:23–01:30
- 当前角色：Staff A
- 录制状态：继续录制
- 页面起点：Voice panel 的音频下方。
- 中文操作：
  1. 如果已有 Voice result，直接滚到 result；不要点击 Create care-note suggestion。
  2. 如果没有 result，点击 Create care-note suggestion 一次。
  3. 鼠标移到空白处，等待结果。
- 等待：
  - 等待 Suggestion status: Ready for review、Transcript 和 timestamped segments 出现。
- 画面确认：
  - 必须看见 Ready for review 和 prepared transcript。
  - 不应把结果说成 autonomous clinical decision。
- 现在念：
  > Each segment connects to a reviewable care-note suggestion for the care team.
- Subtitle cue：14 · 00:01:23,000–00:01:30,000
- 英文字幕：Each segment connects to a reviewable care-note suggestion for the care team.
- 说话与动作关系：处理或读取完成后再念；如果等待较长，剪掉无内容等待但保留最终状态。
- 本段优势：把 transcript segment 和 human-review boundary 连接起来。
- Requirement mapping：requirements.txt:21–26, 42–44
- 退出条件：Ready for review 和至少三个 timestamped segments 可读。
- 如果状态不同：若状态是 In progress，继续等待；若是 Failed，停止当前 take；若已有 result，
  不重复创建。

#### Beat 15 — Select a timestamped segment and source

- 时间：01:30–01:38
- 当前角色：Staff A
- 录制状态：继续录制
- 页面起点：Voice result 的 Transcript 区域。
- 中文操作：
  1. 点击第二个 timestamped transcript segment（通常显示 8.0s–16.0s）。
  2. 等待 audio position 跳到该 segment 起点。
  3. 点击 View source 一次，鼠标移到空白处。
- 等待：
  - 等待播放器定位完成，再等待 Original source 和 inline source excerpt 出现。
- 画面确认：
  - 必须看见 transcript segment、View source、Original source 或 exact highlighted excerpt。
  - 不应看见内部技术标签作为主要画面。
- 现在念：
  > I select a segment, open its source, and keep the exact highlighted path.
- Subtitle cue：15 · 00:01:30,000–00:01:38,000
- 英文字幕：I select a segment, open its source, and keep the exact highlighted path.
- 说话与动作关系：先点击 segment 并等待，再点击 View source；全部稳定后念。
- 本段优势：展示 Voice provenance 与普通 timeline source 的复用。
- Requirement mapping：requirements.txt:21–26, 42–44, 45–48
- 退出条件：segment 已定位，source 已打开。
- 如果状态不同：若没有第二个 segment，选择页面实际可见的其他 timestamped segment，并按实际
  画面说明；若 View source 不可用，不要重复点击。

#### Beat 16 — Hold the Voice source result

- 时间：01:38–01:47
- 当前角色：Staff A
- 录制状态：继续录制
- 页面起点：Voice source panel 或 timeline source excerpt 已打开。
- 中文操作：
  1. 保持页面不滚动，让 Ready for review、transcript、source 和 highlight 同时尽量可见。
  2. 鼠标移到空白处。
  3. cue 结束后才点击 Close source。
- 等待：
  - 等待所有 source 文本完成渲染；至少保留一段可读的稳定画面。
- 画面确认：
  - 必须看见 suggestion、timestamped transcript 和 source link。
  - 不应出现 ASR accuracy、microphone、upload 或 unsupported production claim。
- 现在念：
  > The suggestion is ready for clinician review today.
- Subtitle cue：16 · 00:01:38,000–00:01:47,000
- 英文字幕：The suggestion is ready for clinician review today.
- 说话与动作关系：等待画面稳定后念；念完再关闭 source。
- 本段优势：用一个完整 hold 证明 Voice 结果不是瞬时 toast。
- Requirement mapping：requirements.txt:21–26, 42–44
- 退出条件：Voice shot 完成，准备回到 Timeline。
- 如果状态不同：若 source panel 遮住 transcript，保留其中一个清晰画面即可；若结果消失，
  停止 take，不重做 processing。

### 镜头 4 — Staff note、Comments 和 mention（01:47–02:15）

目标：展示允许的 Staff revision 和 contextual collaboration；所有输入都必须是 synthetic。

#### Beat 17 — Find Staff note and enter Edit

- 时间：01:47–01:54
- 当前角色：Staff A
- 录制状态：继续录制
- 页面起点：关闭 Voice Source 后向下到 Longitudinal timeline。
- 中文操作：
  1. 向下滚动到标题为 Staff note 的 timeline entry。
  2. 确认 entry 右上角的 Version N 是当前版本，但不要念固定数字。
  3. 点击该 entry 下方的 Edit 一次。
- 等待：
  - 等待 Edit Staff note textarea、Save revision 和 Cancel 出现。
- 画面确认：
  - 必须看见 Staff note、当前版本和编辑框。
  - 不应删除原有 clinical content，也不应编辑 Clinician plan。
- 现在念：
  > Back in Staff, I edit the existing Staff note and save a new revision for review.
- Subtitle cue：17 · 00:01:47,000–00:01:54,000
- 英文字幕：Back in Staff, I edit the existing Staff note and save a new revision for review.
- 说话与动作关系：先完成滚动和 Edit，等 textarea 可见后再念。
- 本段优势：诚实展示现有 note revision path，不虚构不存在的 New note composer。
- Requirement mapping：requirements.txt:14–19, 87–93
- 退出条件：编辑框稳定并聚焦。
- 如果状态不同：若没有 Staff note，停止当前 take；若按钮 disabled 或出现 conflict，暂停录制并
  转到 conflict fallback，不重复点击。

#### Beat 18 — Append the synthetic Staff revision

- 时间：01:54–01:59
- 当前角色：Staff A
- 录制状态：继续录制
- 页面起点：Staff note 的 Edit Staff note textarea。
- 中文操作：
  1. 点击 textarea 末尾，不删除现有文字。
  2. 按 Enter 新增一行，输入 Synthetic staff rehearsal: review the pending follow-up.
  3. 点击 Save revision 一次；鼠标移到空白处。
- 等待：
  - 等待 textarea 关闭、保存后的文本出现、Version N 增加或 Record status: Up to date 恢复。
- 画面确认：
  - 必须看见新的 synthetic sentence 和保存后的普通 entry。
  - 不应看见空文本、重复版本提交或 error alert。
- 现在念：
  > I wait for the saved state before continuing on screen for this recording.
- Subtitle cue：18 · 00:01:54,000–00:01:59,000
- 英文字幕：I wait for the saved state before continuing on screen for this recording.
- 说话与动作关系：先输入并保存，等保存结果出现后念。
- 本段优势：说明 revision 是显式保存的，不是静默覆盖。
- Requirement mapping：requirements.txt:17–19, 41–44
- 退出条件：保存成功，编辑框关闭。
- 如果状态不同：若出现 409/conflict，立刻停止录制，保留错误 panel 供 QA，不能重复 Save；
  若保存很慢，保留最终成功状态即可。

#### Beat 19 — Open contextual Comments and choose a mention

- 时间：01:59–02:06
- 当前角色：Staff A
- 录制状态：继续录制
- 页面起点：保存后的 Staff note，Comments 按钮在 entry 下方。
- 中文操作：
  1. 点击 Staff note 的 Comments 一次。
  2. 等待 Team discussion drawer/dialog 立即出现，直到 Comment body 可用。
  3. 点击 Comment body，输入 @；等待 Choose a teammate 菜单。
  4. 点击包含 @Clinician A 的可见选项，不手动输入隐藏 ID。
- 等待：
  - 等待 drawer、Team discussion、Comment body 和 mention option 可见。
- 画面确认：
  - 必须看见 contextual Comments、Choose a teammate 或 @Clinician A。
  - 不应等待页面最底部的旧式 global panel，也不应出现内部请求细节。
- 现在念：
  > Then I add a team discussion and mention Clinician A from the visible menu.
- Subtitle cue：19 · 00:01:59,000–00:02:06,000
- 英文字幕：Then I add a team discussion and mention Clinician A from the visible menu.
- 说话与动作关系：先打开 drawer、选择 mention，再念。
- 本段优势：证明协作入口紧贴 record，并且 mention 通过可见菜单完成。
- Requirement mapping：requirements.txt:15, 90–93
- 退出条件：Comment body 中已经插入 @Clinician A，Add comment 可点击。
- 如果状态不同：若已有 Comments drawer，直接使用现有 drawer；若没有 mention option，停止输入，
  只展示普通 discussion，不声称 mention 成功。

#### Beat 20 — Add the root comment once

- 时间：02:06–02:15
- 当前角色：Staff A
- 录制状态：继续录制
- 页面起点：Comments drawer，Comment body 已有 @Clinician A。
- 中文操作：
  1. 在 mention 后输入 Synthetic rehearsal: please review this follow-up.
  2. 确认完整内容后点击 Add comment 一次。
  3. 等待 root comment、Mentioned teammates: @Clinician A 和 Reply/Resolve 出现；鼠标移到空白处。
- 等待：
  - 等待新增 comment 出现在 Team discussion 内，不要把 loading 当成完成。
- 画面确认：
  - 必须看见 comment body、Mentioned teammates 和明确的 Open/Resolved 状态。
  - 不应看见真实患者信息或错误 stack trace。
- 现在念：
  > The discussion stays with the record, keeping follow-up context available.
- Subtitle cue：20 · 00:02:06,000–00:02:15,000
- 英文字幕：The discussion stays with the record, keeping follow-up context available.
- 说话与动作关系：先 Add comment 并等 root comment 出现，再念。
- 本段优势：展示 threaded collaboration 的 root entry 和 mention metadata。
- Requirement mapping：requirements.txt:15, 90–93
- 退出条件：root comment 可见，且只提交了一次。
- 如果状态不同：若页面已有相同 synthetic comment，直接展示并不重复提交；若 Add comment 失败，
  停止 take，不刷新后再次发送。

### 镜头 5 — Resolve、Assign task 和 Pin（02:15–02:34）

目标：展示协作状态和 priority feedback；task 默认只开 drawer，避免无必要的线上写入。

#### Beat 21 — Toggle the discussion state

- 时间：02:15–02:21
- 当前角色：Staff A
- 录制状态：继续录制
- 页面起点：Comments drawer 中的 root comment。
- 中文操作：
  1. 读取当前按钮是 Resolve 还是 Unresolve。
  2. 点击当前可用的状态按钮一次，等待 Resolved 或 Open 出现。
  3. 如仍有时间，再点击相反按钮一次展示来回状态；否则保留第一次结果。
- 等待：
  - 每次点击后等待状态文字更新，不要连续双击。
- 画面确认：
  - 必须看见 Resolved 或 Open 的明确状态。
  - 不应把 Resolve 状态说成 clinical truth。
- 现在念：
  > Resolve and Unresolve make discussion status explicit for the whole team.
- Subtitle cue：21 · 00:02:15,000–00:02:21,000
- 英文字幕：Resolve and Unresolve make discussion status explicit for the whole team.
- 说话与动作关系：先完成一次状态切换并等结果，再念。
- 本段优势：说明协作完成度和 clinical content 是两个独立维度。
- Requirement mapping：requirements.txt:15, 90–93
- 退出条件：讨论状态可读，准备关闭 Comments。
- 如果状态不同：若当前已经 Resolved，只点击 Unresolve；若按钮不可用，保留现状并按实际画面
  说明，不重复点击。

#### Beat 22 — Open Assign task and show Pin feedback

- 时间：02:21–02:28
- 当前角色：Staff A
- 录制状态：继续录制
- 页面起点：Comments drawer 可关闭；Staff note 和 Glance View 可定位。
- 中文操作：
  1. 点击 Comments 的 Close，等待 drawer 消失。
  2. 在 Staff note 下点击 Assign task 一次。
  3. 等待 Tasks、Creating a task for: Staff note 和 Task title 出现；默认不填写、不点击 Create task。
  4. 点击 Close tasks。
  5. 回到 Glance View，按当前状态点击 Pin 或 Unpin 一次，再点击相反按钮一次；每次等待标签变化。
- 等待：
  - Task drawer 要先稳定显示；Pin/Unpin 要在每次状态更新后再继续。
- 画面确认：
  - 必须看见 Tasks、Task title、Pin/Unpin 的真实 labels。
  - 不应为了展示而创建重复 task。
- 现在念：
  > Pin and Unpin guide prioritisation; Assign task opens follow-up work when needed.
- Subtitle cue：22 · 00:02:21,000–00:02:28,000
- 英文字幕：Pin and Unpin guide prioritisation; Assign task opens follow-up work when needed.
- 说话与动作关系：先打开并关闭 Tasks，再完成 Pin/Unpin；所有状态稳定后念。
- 本段优势：同时覆盖 assignment entry point 和 team feedback，而不制造多余线上状态。
- Requirement mapping：requirements.txt:15, 28–31
- 退出条件：Task drawer 关闭，Glance card 回到原 Pin/Unpin 状态。
- 如果状态不同：若已有 task，只展示 source entry 和 assignee；若按钮初始是 Unpin，执行
  Unpin → Pin；若 Assign task 不可见，跳过 task drawer，不伪造成功。
- 可选 task 分支（不属于默认短片）：若必须展示完整创建流程，打开 drawer 后输入
  Synthetic follow-up task，Assign to 选择 Clinician A，点击 Create task 一次，等待 task card
  出现后立即停止该分支；这会修改 synthetic state，必须在 state prep 中记录。

#### Beat 23 — Finish the Staff take

- 时间：02:28–02:34
- 当前角色：Staff A
- 录制状态：继续录制；cue 念完后暂停录制
- 页面起点：Comments、Tasks、History、Source 均关闭。
- 中文操作：
  1. 确认页面回到普通 Staff timeline/Glance。
  2. 鼠标移到空白处。
  3. 念完 cue 23 后点击录屏软件的 Pause recording。
- 等待：
  - 等待所有 drawer 完全退出；不需要额外网络等待。
- 画面确认：
  - 必须保持 Staff view 和 synthetic workspace。
  - 不应把 Sign out 或密码页录入。
- 现在念：
  > These collaboration actions stay separate from clinical risk and source content.
- Subtitle cue：23 · 00:02:28,000–00:02:34,000
- 英文字幕：These collaboration actions stay separate from clinical risk and source content.
- 说话与动作关系：状态稳定后念；念完才暂停录制。
- 本段优势：总结 collaboration、risk 和 source 的边界，并给角色切换留干净剪辑点。
- Requirement mapping：requirements.txt:14–19, 28–31, 90–93
- 退出条件：录屏暂停，进入 Cut A。
- 如果状态不同：若有 drawer 未关闭，先关闭；若状态有 pending request，镜头外等完成，
  不把半完成状态带入 Clinician。

### Cut A — Staff → Clinician（镜头外）

- 在 cue 23 结束后暂停录制。
- 镜头外点击 Sign out；手动登录 Clinician A；密码框、自动填充和 Sign in 页面不录。
- 打开现有 HTTPS 地址或保留已登录页面；选择 Sarah Tan、English。
- 等待 Clinician A、Clinician view、Record status: Up to date 和 workspace 稳定。
- 重新开始录制后，从 Beat 24 的稳定 Clinician 页面开始。
- 剪辑衔接：上一句是 “These collaboration actions stay separate from clinical risk and source
  content.”；下一句是 “Now I switch to Clinician, whose authority is focused on review and care
  planning.” 两句语义连续，不要把密码页插入中间。

### 镜头 6 — Clinician review、History、Compare、Revert（02:34–03:10）

目标：展示 clinician review authority、immutable history 和可追踪的 revision 操作。

#### Beat 24 — Resume in Clinician view

- 时间：02:34–02:42
- 当前角色：Clinician A
- 录制状态：开始录制（Cut A 后）
- 页面起点：镜头外登录完成后的稳定 Clinician workspace 顶部。
- 中文操作：
  1. 点击录屏软件的 Resume/Start recording。
  2. 确认右上角 Clinician A、Clinician view、Sarah Tan。
  3. 鼠标移到空白处。
- 等待：
  - 等待 Record status: Up to date；若页面 reconnecting，镜头外等待。
- 画面确认：
  - 必须看见 Clinician view 和 workspace。
  - 不应看见 Staff view、Patient view 或登录页。
- 现在念：
  > Now I switch to Clinician, whose authority is focused on review and care planning.
- Subtitle cue：24 · 00:02:34,000–00:02:42,000
- 英文字幕：Now I switch to Clinician, whose authority is focused on review and care planning.
- 说话与动作关系：先确认角色和状态，再念。
- 本段优势：明确 clinician 是确认与 care planning 的 authority。
- Requirement mapping：requirements.txt:16–19, 34–40, 51
- 退出条件：Clinician 页面稳定。
- 如果状态不同：若仍是 Staff，停止并重新完成镜头外切换；若显示 stale page，等待或刷新后再录。

#### Beat 25 — Edit the Clinician plan

- 时间：02:42–02:50
- 当前角色：Clinician A
- 录制状态：继续录制
- 页面起点：向下滚动到 Longitudinal timeline 中标题为 Clinician plan 的 entry。
- 中文操作：
  1. 向下滚动到 Clinician plan；确认右上角当前 Version N，不念固定数字。
  2. 点击 entry 下方的 Edit。
  3. 在 textarea 末尾新增一行，输入 Synthetic clinician rehearsal: confirm the next follow-up plan.
  4. 点击 Save revision 一次，鼠标移到空白处。
- 等待：
  - 等待 textarea 关闭、保存文本出现和新的版本状态恢复。
- 画面确认：
  - 必须看见 Clinician plan 和保存后的 synthetic sentence。
  - 不应编辑 Staff note 或删除原有 content。
- 现在念：
  > I edit the Clinician plan, save, then open History for safe review carefully.
- Subtitle cue：25 · 00:02:42,000–00:02:50,000
- 英文字幕：I edit the Clinician plan, save, then open History for safe review carefully.
- 说话与动作关系：先保存并等成功，再念；念完再点 History。
- 本段优势：演示 clinician-only revision path，并保留原有历史。
- Requirement mapping：requirements.txt:16–19, 41–44
- 退出条件：保存成功，entry 回到非编辑状态。
- 如果状态不同：若当前 Clinician plan 已有同一 synthetic sentence，直接跳过保存；若出现
  conflict，停止并按页面提示 review both versions，不重复 Save。

#### Beat 26 — Open History and Compare an earlier version

- 时间：02:50–02:59
- 当前角色：Clinician A
- 录制状态：继续录制
- 页面起点：Clinician plan entry，History 按钮可见。
- 中文操作：
  1. 点击 History 一次，等待 History region 展开。
  2. 选择列表中实际可见的 earlier version，不假定 v1 或 v2。
  3. 点击该 row 的 Compare 一次，鼠标移到空白处。
- 等待：
  - 等待 Changes from version、Before: 和 After: 出现。
- 画面确认：
  - 必须看见 Current row、earlier row、Compare、Before 和 After。
  - 不应在旁白中硬编码当前版本号。
- 现在念：
  > I compare an earlier version with the current one.
- Subtitle cue：26 · 00:02:50,000–00:02:59,000
- 英文字幕：I compare an earlier version with the current one.
- 说话与动作关系：先完成 Compare 并等待 Before/After，再念。
- 本段优势：把 revision history 转成评委可以直接看懂的 before/after。
- Requirement mapping：requirements.txt:17–19, 41–44
- 退出条件：Before/After 对照稳定可读。
- 如果状态不同：若只有一个 earlier row，就使用它；若没有 Compare，保留 History 画面并跳到
  Beat 28，不重复点击。

#### Beat 27 — Revert only when the real button is available

- 时间：02:59–03:05
- 当前角色：Clinician A
- 录制状态：继续录制
- 页面起点：History region 和 Compare result。
- 中文操作：
  1. 检查 earlier row 是否有 Revert。
  2. 只有按钮可用且计划要展示时，点击 Revert 一次；否则不点击。
  3. 若已点击，等待新的 current version 出现并确认 earlier rows 仍在。
- 等待：
  - 等待新版本或明确的保存状态；不要用刷新制造新版本。
- 画面确认：
  - 必须看见历史仍保留；若执行 Revert，必须看见新版本。
  - 不应声称删除了旧历史。
- 现在念：
  > Before and After show the change; Revert creates a new version for review.
- Subtitle cue：27 · 00:02:59,000–00:03:05,000
- 英文字幕：Before and After show the change; Revert creates a new version for review.
- 说话与动作关系：若执行 Revert，先等新版本出现再念；若不执行，按 conditional narration
  念并保持 History 画面。
- 本段优势：说明 revert 是 additive revision，而不是删除历史。
- Requirement mapping：requirements.txt:17–19, 41–44
- 退出条件：History 画面稳定，或 conditional branch 已记录。
- 如果状态不同：若 Revert 不可用、权限不足或页面正在保存，跳过该动作；不要为了匹配脚本
  改权限或重复点击。

#### Beat 28 — Keep human review explicit

- 时间：03:05–03:10
- 当前角色：Clinician A
- 录制状态：继续录制
- 页面起点：History 稳定；必要时向上回到 Glance card。
- 中文操作：
  1. 只有页面实际显示 Accept 或 Reject 时，才指向该 review control。
  2. 默认不点击；若已在本轮 state prep 中决定 review，最多点击一次并等待状态。
  3. 鼠标移到空白处。
- 等待：
  - 等待当前 review/status 完成；没有按钮则不需要等待。
- 画面确认：
  - 必须让 suggestion 保持 reviewable，且 source 没有被覆盖。
  - 不应把 Accept 说成修改原始 record。
- 现在念：
  > History stays available; review confirms suggestions; the source remains unchanged.
- Subtitle cue：28 · 00:03:05,000–00:03:10,000
- 英文字幕：History stays available; review confirms suggestions; the source remains unchanged.
- 说话与动作关系：先确认实际状态，再念；不为旁白强行点击。
- 本段优势：收束 clinician authority、history 和 suggestion review boundary。
- Requirement mapping：requirements.txt:17–19, 42–44, 51
- 退出条件：可以进入 Historical context。
- 如果状态不同：若没有 Accept/Reject，保持 History/Compare 的已验证画面；若 status 已 Reviewed，
  不把它说成仍待确认。

### 镜头 7 — Historical context 与 UX-01（03:10–03:44）

目标：展示 recent/earlier/historical summary 到 original record 的导航，并准确记录独立 UX-01
事实。

#### Beat 29 — Find Historical context

- 时间：03:10–03:16
- 当前角色：Clinician A
- 录制状态：继续录制
- 页面起点：History、Comments、Source 已关闭；向下滚动到 Historical context。
- 中文操作：
  1. 向下滚动到 Historical context 和 Recent context, earlier context, and historical summaries。
  2. 鼠标移到 section 标题旁。
- 等待：
  - 等待 section 完整布局稳定。
- 画面确认：
  - 必须看见 Historical context。
  - 不应看见旧式技术命名或配置说明。
- 现在念：
  > Historical context brings recent and earlier summaries together for review.
- Subtitle cue：29 · 00:03:10,000–00:03:16,000
- 英文字幕：Historical context brings recent and earlier summaries together for review.
- 说话与动作关系：先滚动到 section 并等待，再念。
- 本段优势：说明 longitudinal context 不只是一条当前记录。
- Requirement mapping：requirements.txt:10–13, 32, 94–97
- 退出条件：Historical context section 可读。
- 如果状态不同：若没有 summary，保留 Recent/Earlier context 画面；不要编造 historical summary。

#### Beat 30 — Expand the organisation details

- 时间：03:16–03:22
- 当前角色：Clinician A
- 录制状态：继续录制
- 页面起点：Historical context section。
- 中文操作：
  1. 点击 How historical context is organised。
  2. 等待 Recent context、Earlier context、Historical summary 和 source pointer 出现。
  3. 鼠标移到 details 外。
- 等待：
  - 等待 details 展开，不要点击 Refresh history。
- 画面确认：
  - 必须看见 Historical summary · not the original record。
  - 不应把 summary 说成原始医疗记录。
- 现在念：
  > Each summary is labelled clearly and links to original records for team verification.
- Subtitle cue：30 · 00:03:16,000–00:03:22,000
- 英文字幕：Each summary is labelled clearly and links to original records for team verification.
- 说话与动作关系：先展开并等待，再念。
- 本段优势：清楚区分快速阅读的 summary 和可核验的 original record。
- Requirement mapping：requirements.txt:10–13, 32
- 退出条件：至少一个 View original record 可见。
- 如果状态不同：若 details 已经展开，不重复点击；若只有部分 labels，按实际可见内容念，
  不补写不存在的分类。

#### Beat 31 — View original record

- 时间：03:22–03:29
- 当前角色：Clinician A
- 录制状态：继续录制
- 页面起点：Historical summary details 展开。
- 中文操作：
  1. 点击一个实际可见的 View original record 一次。
  2. 不点击第二个按钮。
  3. 等待页面平滑滚到对应 original timeline entry，鼠标移到空白处。
- 等待：
  - 等待原始 entry 标题、日期和版本进入画面。
- 画面确认：
  - 必须看见 original record 的 timeline 位置。
  - 不应把此导航说成 Voice source 或手动 highlight。
- 现在念：
  > I open an original record and reach the relevant timeline point when needed.
- Subtitle cue：31 · 00:03:22,000–00:03:29,000
- 英文字幕：I open an original record and reach the relevant timeline point when needed.
- 说话与动作关系：先点击并等平滑滚动完成，再念。
- 本段优势：证明 summary 仍然能回到 detail。
- Requirement mapping：requirements.txt:32, 94–97
- 退出条件：对应 original timeline entry 可见。
- 如果状态不同：若第一条按钮目标不明显，选择有清楚日期和类型的可见按钮；若滚动失败，
  停止并重录本 beat，不手动滚到别的记录冒充结果。

#### Beat 32 — Explain the verification relationship

- 时间：03:29–03:38
- 当前角色：Clinician A
- 录制状态：继续录制
- 页面起点：原始 timeline entry 已可见；鼠标移到空白处。
- 中文操作：
  1. 保持页面不动，让摘要说明和 original record 关系尽量可读。
  2. 不再点击 View original record。
- 等待：
  - 等待平滑滚动完全结束。
- 画面确认：
  - 必须能看出摘要不是 original record，且 original records remain the source of truth。
  - 不应添加代码或内部数据解释。
- 现在念：
  > An independent participant used Simplified Chinese; the glance task had no coaching.
- Subtitle cue：32 · 00:03:29,000–00:03:38,000
- 英文字幕：An independent participant used Simplified Chinese; the glance task had no coaching.
- 说话与动作关系：先让页面稳定，再念；不要把 UX-01 句子说成当前录制者结果。
- 本段优势：把独立 UX evidence 的语言和 coaching 边界准确说出。
- Requirement mapping：requirements.txt:8–9, 99–104；UX-01 evidence
- 退出条件：summary/source 关系和 UX-01 句子念完。
- 如果状态不同：若当前页面没有 summary，仍可念独立 UX 事实但不要指向错误记录；不得补写
  participant name、role、viewport 或背景。

#### Beat 33 — Complete the independent UX result

- 时间：03:38–03:44
- 当前角色：Clinician A
- 录制状态：继续录制；cue 念完后暂停录制
- 页面起点：Historical context 或原始 timeline 稳定画面。
- 中文操作：
  1. 保持鼠标移开。
  2. 念完 cue 33 后点击录屏软件的 Pause recording。
- 等待：
  - 不需要网络等待；只确认录音没有被系统提示打断。
- 画面确认：
  - 不应把一次独立测试包装成统计研究或所有用户结论。
- 现在念：
  > The result was approximately nine seconds, with all four observations correct.
- Subtitle cue：33 · 00:03:38,000–00:03:44,000
- 英文字幕：The result was approximately nine seconds, with all four observations correct.
- 说话与动作关系：稳定后念，念完才暂停；Cut B 在暂停后完成。
- 本段优势：保留 UX-01 的真实事实，同时不夸大样本。
- Requirement mapping：requirements.txt:8–9, 99–104；docs/evidence/ux_01_independent_test.md
- 退出条件：录屏暂停，进入 Cut B。
- 如果状态不同：若页面滚动或提示遮挡，先等待或镜头外恢复；不要在遮挡中念结果。

### Cut B — Clinician → Patient（镜头外）

- 在 cue 33 结束后暂停录制。
- 镜头外点击 Sign out；手动登录 Sarah Patient；密码框、自动填充和 Sign in 页面不录。
- 选择 English、Sarah Tan；等待 Patient view 和 workspace 稳定。
- 重新开始录制后，从 Beat 34 的 Patient view 顶部开始。
- 剪辑衔接：上一句是 “The result was approximately nine seconds, with all four observations correct.”
  下一句是 “Finally, I switch to Patient; the patient view contains only shared information.”
- 如果 Patient 页面仍在 loading，保留镜头外等待；不要用内部 Staff 页面代替 Patient privacy 证据。

### 镜头 8 — Patient privacy 与 Patient Voice（03:44–04:12）

目标：证明患者收到的是 server-side patient-facing projection，而不是内部 workspace 的缩小版。

#### Beat 34 — Resume in Patient view

- 时间：03:44–03:51
- 当前角色：Sarah Patient
- 录制状态：开始录制（Cut B 后）
- 页面起点：镜头外登录完成后的 Patient workspace 顶部。
- 中文操作：
  1. 点击录屏软件的 Resume/Start recording。
  2. 确认右上角 Sarah Patient、Patient view、Sarah Tan。
  3. 鼠标移到空白处。
- 等待：
  - 等待 Patient view 和 Voice note 稳定。
- 画面确认：
  - 必须看见 Sarah Patient、Patient view。
  - 不应看见 Staff view、Clinician view 或登录页。
- 现在念：
  > Finally, I switch to Patient; the patient view contains only shared information.
- Subtitle cue：34 · 00:03:44,000–00:03:51,000
- 英文字幕：Finally, I switch to Patient; the patient view contains only shared information.
- 说话与动作关系：先确认角色和页面稳定，再念。
- 本段优势：把最后一次角色切换明确为 privacy proof，而不是普通导航。
- Requirement mapping：requirements.txt:34–40, 51
- 退出条件：Patient view 稳定，进入 Your care summary。
- 如果状态不同：若仍为 Clinician，停止并重新镜头外切换；若页面提示失效，镜头外等待或刷新。

#### Beat 35 — Show Your care summary

- 时间：03:51–03:58
- 当前角色：Sarah Patient
- 录制状态：继续录制
- 页面起点：Patient view 顶部。
- 中文操作：
  1. 向下滚动到 Patient privacy 和 Your care summary。
  2. 保持 patient-facing summary 在画面中央。
  3. 鼠标移到空白处。
- 等待：
  - 等待 Your care summary 和说明文字完整显示。
- 画面确认：
  - 必须看见 Your care summary、Only information shared with you appears here。
  - 不应看见 Glance View、Comments、Tasks 或临床 review controls。
- 现在念：
  > It shows care summaries, instructions, and patient conversation.
- Subtitle cue：35 · 00:03:51,000–00:03:58,000
- 英文字幕：It shows care summaries, instructions, and patient conversation.
- 说话与动作关系：先滚动到 summary 并等待，再念。
- 本段优势：说明患者看到的是 shared care context，而不是内部编辑界面。
- Requirement mapping：requirements.txt:34–40
- 退出条件：Your care summary 稳定可读。
- 如果状态不同：若 summary 文字略有变化，按实际页面说明；不要把内部 entry 名称念给患者。

#### Beat 36 — Confirm internal controls are absent

- 时间：03:58–04:05
- 当前角色：Sarah Patient
- 录制状态：继续录制
- 页面起点：向下到 patient timeline。
- 中文操作：
  1. 向下滚动到 Timeline。
  2. 让两条 patient-facing records 和 Voice 区域尽量可见。
  3. 不尝试点击不存在的 Comments、History、Assign task、Edit 或 View source。
- 等待：
  - 等待患者时间线稳定；不需要打开任何内部 panel。
- 画面确认：
  - 必须只有患者可见记录和 patient-facing context。
  - 不应出现内部 discussions、tasks、clinical review 或 raw care-note suggestion text。
- 现在念：
  > Internal items, team discussions, tasks, and clinician-only controls stay out.
- Subtitle cue：36 · 00:03:58,000–00:04:05,000
- 英文字幕：Internal items, team discussions, tasks, and clinician-only controls stay out.
- 说话与动作关系：先把 privacy projection 放稳，再念。
- 本段优势：把 privacy boundary 变成评委可观察的 UI absence。
- Requirement mapping：requirements.txt:34–40, 51
- 退出条件：Patient timeline 和 absence evidence 可读。
- 如果状态不同：若任何内部控件出现，停止录制并记录；不要通过 CSS 或前端隐藏来补救。

#### Beat 37 — Show Patient Voice without overclaiming

- 时间：04:05–04:12
- 当前角色：Sarah Patient
- 录制状态：继续录制
- 页面起点：Patient Voice note。
- 中文操作：
  1. 确认 Choose a conversation 显示 patient follow-up；若已有 result，直接展示。
  2. 若没有 result 且 state prep 明确允许，先点击 native play 一次，之后只点击
     Create care-note suggestion 一次。
  3. 等待 Ready for review 和 timestamped transcript；若时间不足，只展示 audio 和
     pre-recorded care conversation，不点击第二次。
- 等待：
  - 等待 audio ready、Length: 24.0s；若处理，等待 Suggestion status: Ready for review。
- 画面确认：
  - 必须只展示 patient follow-up 和患者可见内容。
  - 不应出现 View source、clinical sample、microphone 或 upload。
- 现在念：
  > Patient Voice follows this path: audio, timestamped transcript, and care context.
- Subtitle cue：37 · 00:04:05,000–00:04:12,000
- 英文字幕：Patient Voice follows this path: audio, timestamped transcript, and care context.
- 说话与动作关系：先确认 Patient Voice 当前状态，再念；不要在旁白中描述未出现的 result。
- 本段优势：展示同一 traceable interaction 在 Patient projection 下仍尊重隐私。
- Requirement mapping：requirements.txt:45–48, 51–53
- 退出条件：Patient Voice 画面稳定，准备收尾。
- 如果状态不同：若没有 patient result，展示 audio metadata 并删掉 transcript 相关画面；
  若 processing 失败，停止该镜头，不重试。

### 镜头 9 — Product close（04:12–04:30）

目标：用稳定画面收束产品价值、human review 和 synthetic/HTTPS 边界。

#### Beat 38 — Return to a clean workspace

- 时间：04:12–04:18
- 当前角色：任一稳定内部角色；若保留 Patient，则不指向内部 controls。
- 录制状态：继续录制
- 页面起点：所有 drawer 已关闭，页面处于最清楚的 English workspace。
- 中文操作：
  1. 不再打开 Guide、Source、Comments、History 或 Task。
  2. 如页面在 Patient，保持 Patient view；如回到内部角色，保持稳定的 workspace。
  3. 鼠标移到空白处。
- 等待：
  - 等待页面布局、audio 和状态文字稳定。
- 画面确认：
  - 必须看见清晰的 workspace 和 synthetic-data disclosure。
  - 不应看见密码、配置、日志、Render dashboard 或错误状态。
- 现在念：
  > Next steps stay visible; the original record stays verifiable.
- Subtitle cue：38 · 00:04:12,000–00:04:18,000
- 英文字幕：Next steps stay visible; the original record stays verifiable.
- 说话与动作关系：先清理画面并等待，再念。
- 本段优势：把 Glance、source 和 timeline 的主线重新汇总。
- Requirement mapping：requirements.txt:8–13, 42–44
- 退出条件：稳定的收尾画面已经建立。
- 如果状态不同：若 drawer 意外打开，先关闭再念；不要用回退键改变状态。

#### Beat 39 — Point to the review boundary

- 时间：04:18–04:23
- 当前角色：保持上一 beat 的角色。
- 录制状态：继续录制
- 页面起点：稳定 workspace。
- 中文操作：
  1. 鼠标指向 synthetic-only disclosure 或 trust boundary 文字，但不要点击。
  2. 鼠标移到空白处。
- 等待：
  - 不需要网络等待；只确认文字没有被 tooltip 遮挡。
- 画面确认：
  - 必须看见 synthetic data 和 human review boundary。
  - 不应出现内部实现名词或未验证指标。
- 现在念：
  > Human review remains at every suggestion boundary throughout.
- Subtitle cue：39 · 00:04:18,000–00:04:23,000
- 英文字幕：Human review remains at every suggestion boundary throughout.
- 说话与动作关系：先指向文字，再念；念完移开鼠标。
- 本段优势：把 AI suggestion 的核心 trust principle 留给评委。
- Requirement mapping：requirements.txt:21–26, 42–44, 50–54
- 退出条件：最后一句旁白准备开始。
- 如果状态不同：若 disclosure 在当前角色不可见，保持稳定 workspace，不补说页面未显示的细节。

#### Beat 40 — Final line and stop

- 时间：04:23–04:30
- 当前角色：保持上一 beat 的角色。
- 录制状态：继续录制；cue 念完后停止录制
- 页面起点：稳定 English workspace。
- 中文操作：
  1. 保持画面和鼠标不动。
  2. 念完旁白后等待约一秒。
  3. 点击录屏软件的 Stop recording；不要再点击网页。
- 等待：
  - 等待字幕 cue 结束，不要提前切黑。
- 画面确认：
  - 必须以稳定页面结束。
  - 不应把录制软件控制台、文件路径或后续登录动作录进去。
- 现在念：
  > The demo uses synthetic data and a hosted HTTPS workspace for a traceable workflow.
- Subtitle cue：40 · 00:04:23,000–00:04:30,000
- 英文字幕：The demo uses synthetic data and a hosted HTTPS workspace for a traceable workflow.
- 说话与动作关系：先念完整句子，停一秒后停止录制。
- 本段优势：诚实收束 hosted demo 的价值和限制。
- Requirement mapping：requirements.txt:50–54, 74–85, 99–104
- 退出条件：视频文件已保存，进入视频 QA；不在此文件内生成 PDF/ZIP/MANIFEST。
- 如果状态不同：若录制软件没有保存确认，先确认文件存在再关闭；不要重录网页状态或重复线上写入。

## D. 失败恢复、慢页面和重录规则

### 通用恢复

- 页面加载慢：保留镜头外等待；只有目标 heading、button、status 和结果同时可见时才继续。
- API 或音频失败：停止当前 take，记录失败时间和可见错误，按 QA 重新准备；不连续点击。
- Source 失败：不要用 current content 冒充 source；关闭 take 后重新从同一 card 开始。
- 409/conflict：停止写入，保留 conflict panel；不要刷新来覆盖、不要重复 Save。
- 角色错误：暂停录制，镜头外 Sign out/login；不要把角色名从旁白里剪掉来掩盖错误。
- 按钮不可用：按对应 beat 的 conditional 分支跳过；不要通过改变地址参数或数据来制造按钮。
- 已有 Voice result/comment/revision：展示现状，跳过会产生新状态的 click。

### 必须重录的情况

- 密码框、自动填充、Cookie、API key、环境变量、Render dashboard 或日志进入画面。
- Staff、Clinician、Patient 角色顺序错误，或患者不是 Sarah Tan。
- Voice 被重复提交、comment 被重复发送、revision 被重复保存。
- 旁白描述了页面没有出现的版本、status、按钮或 transcript。
- Patient 页面出现内部内容或内部 controls。
- SRT cue 与旁白不同步，或字幕超过两行、明显遮挡 UI。

## E. 剪辑点和正式 QA

### 两个剪辑点

| 剪辑点 | 前一 take 的最后一句 | 后一 take 的第一句 | 必须剪掉 |
| --- | --- | --- | --- |
| Cut A | These collaboration actions stay separate from clinical risk and source content. | Now I switch to Clinician, whose authority is focused on review and care planning. | Staff Pause、Sign out、密码输入、Clinician 登录和加载等待 |
| Cut B | The result was approximately nine seconds, with all four observations correct. | Finally, I switch to Patient; the patient view contains only shared information. | Clinician Pause、Sign out、密码输入、Patient 登录和加载等待 |

保留的等待：Glance 的 source navigation、Voice 的 ready/result、Comments drawer、Save revision、
History Compare、Patient privacy projection。
应剪掉的等待：free instance 唤醒、登录、角色切换、长 loading、录屏软件控制操作。

### 停止录制后

1. 立即确认视频文件存在，不要先修改线上页面。
2. 用 DEMO_SUBTITLES_EN.srt 导入剪辑软件；不要手动重打字幕。
3. 完整观看一次，逐项填写 DEMO_VIDEO_QA.md。
4. 检查成片约 4:30、口播清晰、字幕同步、三角色顺序正确、没有敏感信息。
5. 视频通过 QA 前，不生成最终 PDF、ZIP 或 MANIFEST，不 push，不发邮件。

## F. 对照文件

- 独立字幕导入文件：DEMO_SUBTITLES_EN.srt
- 旧版逐镜头旁白参考：DEMO_SCRIPT_SPOKEN_EN.md
- 中文操作参考：DEMO_OPERATOR_RUNBOOK_ZH.md
- 快速卡片：DEMO_CUE_CARD_ZH_EN.md
- Shot 列表：DEMO_SHOTLIST.md
- 状态准备：DEMO_STATE_PREP_ZH.md
- 录制前后 checklist：DEMO_RECORDING_CHECKLIST.md
- 视频 QA：DEMO_VIDEO_QA.md
- Requirement traceability：DEMO_REQUIREMENT_TRACEABILITY.md
- 已验证线上证据：evidence/demo_rehearsal.md

本文件的 beat、旁白、时间码和 SRT 是本次录制的 single source of truth；其他文件不得与本文件
形成第二套“最终顺序”。
