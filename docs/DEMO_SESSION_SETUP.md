# Nightingale 录制 Session Setup

## 录制目标

- 地址：`https://nightingale-shared-care-note.onrender.com`
- 角色顺序：**Staff → Clinician → Patient**
- 页面语言：`English`
- 患者：`Sarah Tan`
- AI/Voice：fixture provider；Voice 仅为 Level-C prerecorded synthetic fixture
- 数据：只使用内置 synthetic data

操作提示用中文，网页按钮保留真实 English label，口播和字幕使用 English。最终视频不应
展示密码、API key、数据库 URL、环境变量、浏览器 storage、DevTools 或 provider console。

## 三个 session

| 顺序 | 角色 | 页面起点 | 录制内容 |
| --- | --- | --- | --- |
| 1 | `Staff A` | `Staff view`、`Sarah Tan` | Top Card、AI source、Voice、Staff note、Comments、mention、Resolve/Unresolve、Pin/Unpin |
| 2 | `Clinician A` | `Clinician view`、`Sarah Tan` | Clinician section、History、available earlier version 的 Compare/Revert、历史上下文 |
| 3 | `Sarah Patient` | `Patient view`、`Sarah Tan` | Patient privacy projection、patient Voice、无内部 source/control |

账号切换用两个镜头外 cut：点击 `Sign out`，离开镜头完成下一次登录，页面稳定后再继续录制。
密码输入永远不在画面中。

## 每个 session 开始前

1. 打开部署地址，等待 Render free instance 唤醒。
2. 确认应用显示 `English`；不要切换到中文录制界面。
3. 确认患者下拉框 `Select patient` 为 `Sarah Tan`。
4. Staff/Clinician 等待 `Live updates: Connected`。
5. 点击/关闭 `Guide`，不要让 Help/Guide 盖住页面。
6. 关闭 DevTools、浏览器通知、系统提示和 password-manager popup。
7. 关闭所有 `Source`、`Comments`、`History`、`Task` drawer；鼠标停在空白处。
8. 重新观察当前 Staff note、Clinician section 的版本和当前 Suggested 卡片；不要假定固定版本。
9. 确认 `VOICE_PROVIDER=fixture` 的可见 fixture disclosure，不打开环境配置页。

## 录制前的状态准备

具体版本/卡片状态见 [`DEMO_STATE_PREP_ZH.md`](DEMO_STATE_PREP_ZH.md)。当前线上数据库不是
pristine seed：已有 Voice-derived entries、revision、comment/mention、review 和 pin feedback。
因此：

- 录制前选择“当前页面实际仍显示”的 Suggested 卡片。
- History 中点击“当前列表里可见的 earlier version”，不要写死 `v1 → v2`。
- 如果当前已有 Voice result，直接展示；不要重复 `Process sample`。
- 如果必须重新处理，Clinical 和 Patient fixture 各最多一次。
- 不要为了恢复编号而 reset、delete 或 seed 数据。

## 角色切换与镜头 cut

| Cut | 镜头外动作 | 镜头重新开始时必须看到 |
| --- | --- | --- |
| Staff → Clinician | 点击 `Sign out`；手动登录 Clinician | `Clinician A`、`Clinician view`、`Sarah Tan`、`Live updates: Connected` |
| Clinician → Patient | 点击 `Sign out`；手动登录 Patient | `Sarah Patient`、`Patient view`、`Sarah Tan` |

不要在切换账号时展示密码框、浏览器自动填充、Cookie 或地址栏中的敏感信息。

## 录制过程中会修改状态的按钮

| 操作 | 状态变化 | 使用规则 |
| --- | --- | --- |
| `Open source`、`Close source`、History、Compare、`View original record` | 只改视图 | 可重复；按实际结果描述 |
| `Process sample` | 创建 Voice session/AI entry/source | 每个 fixture 最多一次 |
| `Save revision` | 增加 note version | 只在指定镜头点击一次 |
| `Add comment` | 增加 internal comment/mention metadata | 只提交一次 synthetic comment |
| `Resolve`、`Unresolve` | 切换 comment 状态 | 做一组切换即可 |
| `Pin`、`Unpin` | 增加 importance feedback metadata | 做一组切换即可 |
| `Revert` | 创建新的 revert version | 只点击一次；不要直接修改数据库 |
| `Accept` / `Reject` | 修改 suggestion review state | 只有当前确实有按钮时才录制 |

## 不要点击或展示

- 不要打开 `Render Environment`、密码、key、数据库、DevTools 或 provider console。
- 不要使用 microphone、upload、Whisper、DeepSeek live call 或真实患者数据。
- 不要录制不存在的新建 note、手动 highlight 选择、双浏览器 SSE、live 409 panel、task
  完整生命周期。
- 不要把 `View original record` 说成 exact-span provenance panel；当前实际行为是滚动到
  canonical timeline entry。

## 录制结束

1. 关闭所有 drawer，鼠标移到空白处。
2. 结束时停在 English synthetic workspace，不打开配置页面。
3. 完整观看视频一次，再填写 [`DEMO_VIDEO_QA.md`](DEMO_VIDEO_QA.md)。
4. 视频通过 QA 后，才进入 PDF/ZIP/MANIFEST 和最终 push 任务。
