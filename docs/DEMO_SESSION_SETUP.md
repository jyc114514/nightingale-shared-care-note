# Nightingale 录制 Session Setup

录制时以 [`DEMO_RECORDING_MASTER_ZH_EN.md`](DEMO_RECORDING_MASTER_ZH_EN.md) 为唯一操作主文件；本文件保留为 session 准备参考。

## 录制目标

- 地址：`https://nightingale-shared-care-note.onrender.com`
- 角色顺序：**Staff → Clinician → Patient**
- 页面语言：`English`
- 患者：`Sarah Tan`
- 数据：只使用内置 synthetic data
- 操作提示用中文；网页标签保留真实 English label；口播和字幕使用 English

最终视频不得展示密码、API key、数据库 URL、环境变量、Cookie、browser storage、DevTools
或外部服务控制台。账号切换用镜头外 cut，密码输入永远不出现在画面中。

## 三个 session

| 顺序 | 角色 | 页面起点 | 录制内容 |
| --- | --- | --- | --- |
| 1 | `Staff A` | `Staff view`、`Sarah Tan` | Glance View、source、Voice、Staff note、Comments、mention、Resolve/Unresolve、Pin/Unpin |
| 2 | `Clinician A` | `Clinician view`、`Sarah Tan` | Clinician plan、History、Compare/Revert、Historical context |
| 3 | `Sarah Patient` | `Patient view`、`Sarah Tan` | Your care summary、Patient Voice、患者可见内容 |

## 每个 session 开始前

1. 打开现有 HTTPS 地址，等待 free instance 唤醒。
2. 确认语言为 `English`，患者为 `Sarah Tan`。
3. Staff/Clinician 等待状态显示 `Up to date`。
4. 关闭 `Guide`、`Source`、`Comments`、`History`、`Task` drawer、通知和 DevTools。
5. 将鼠标放在空白处，等页面布局和音频控件稳定。
6. 读取 [`DEMO_STATE_PREP_ZH.md`](DEMO_STATE_PREP_ZH.md)，现场确认当前版本、卡片状态和
   Voice result；不要假定旧 rehearsal 的具体编号。

## 角色切换

| Cut | 镜头外动作 | 重新录制时必须看到 |
| --- | --- | --- |
| Staff → Clinician | `Sign out`，在镜头外登录 Clinician | `Clinician A`、`Clinician view`、`Sarah Tan`、`Up to date` |
| Clinician → Patient | `Sign out`，在镜头外登录 Patient | `Sarah Patient`、`Patient view`、`Sarah Tan` |

切换后等待页面稳定再开始下一镜头；不要显示密码框、自动填充或地址栏敏感信息。

## 录制前的状态规则

- 当前仍显示 `Needs review` 的卡片才用于 review 说明；如果已经 `Reviewed`，按页面实际状态
  选择另一张，不要写死卡片名称。
- History 中选择页面实际可见的 earlier version，不要写死 `v1 → v2`。
- Voice 已有 result 时直接展示；没有 result 时每个 sample 最多点击一次
  `Create care-note suggestion`。
- 不为了恢复旧编号而 reset、delete 或重新 seed 数据。

## 会修改 synthetic state 的动作

| 动作 | 状态变化 | 使用规则 |
| --- | --- | --- |
| `Open source`、`Close source`、`History`、`Compare`、`View original record` | 只改视图 | 可重复；按实际结果描述 |
| `Create care-note suggestion` | 创建 Voice session/建议/来源 | 每个 sample 最多一次 |
| `Save revision` | 增加 note version | Staff、Clinician 各按脚本执行一次 |
| `Add comment` | 增加团队讨论和 mention | 只提交一次 synthetic comment |
| `Resolve`/`Unresolve` | 切换讨论状态 | 完成一组来回切换 |
| `Pin`/`Unpin` | 写入优先级反馈 | 完成一组来回切换 |
| `Revert` | 创建新的恢复版本 | 只点击一次；保留历史 |
| `Accept`/`Reject` | 修改 suggestion 状态 | 只有页面确实显示时才执行 |

## 不要点击或展示

- 不打开 Render Environment、密码、API key、数据库配置、DevTools、Cookie 或外部服务
  控制台。
- 不录入真实患者信息；临床原文保持原始语言。
- 不把 prepared transcript 说成 ASR 质量证据，也不口播未在画面中验证的技术结果。
- 不为视频制造不存在的控件、固定版本号或固定 suggestion 状态。

## 录制结束

1. 关闭所有 drawer，停在稳定的 English workspace。
2. 完整观看成片一次，按 [`DEMO_VIDEO_QA.md`](DEMO_VIDEO_QA.md) 检查。
3. 视频通过 QA 后，才进入最终 PDF/ZIP/MANIFEST 和最终 push 任务。
