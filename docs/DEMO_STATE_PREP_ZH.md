# Nightingale 最终录制前 Demo State Prep

更新时间：2026-08-27
部署地址：`https://nightingale-shared-care-note.onrender.com`
录制界面：English
数据边界：只使用内置 synthetic data

这份文件是录制前的状态准备卡，不是产品功能说明。线上数据库已经被前几轮 synthetic
rehearsal 修改，不是 pristine seed。录制前必须重新确认当前页面显示的版本和卡片状态，
不能把下面的版本号当成永久不变的前提。

## 推荐登录顺序

1. **Staff A**：先打开 Sarah Tan 的页面，完成 Staff-first 的 Glance、source、Voice 展示和
   协作入口。
2. **Clinician A**：通过一次离镜头的账号切换，完成 Clinician section、History、Compare、
   Revert 和历史上下文。
3. **Sarah Patient**：通过第二次离镜头的账号切换，完成患者隐私投影和 patient Voice。

录制时不要在镜头中输入密码。每次账号切换都用 `Sign out` 后切镜头，登录完成、页面稳定
后再继续录制。当前已验证只需要这两次角色切换。

## 当前线上状态盘点

以下是最终 Staff-first dry run 前的只读盘点结果：

- 患者：`Sarah Tan`；Staff 页显示 `Staff A` 和 `Staff view`；Clinician 页显示 `Clinician A`
  和 `Clinician view`；Patient 页显示 `Sarah Patient` 和 `Patient view`。
- 内部页面的 SSE 标签为 `Live updates: Connected`。
- Staff note 当前为 **v3**；History 中可见 **v1、v2、v3**，其中两个 earlier version 有
  `Compare` 和 `Revert`。
- Clinician section 当前为 **v3**；History 中可见 **v1、v2、v3**，其中两个 earlier
  version 有 `Compare`，并可见 `Revert` 控件。
- Glance 当前仍有 Suggested 项：`Unresolved cardiology referral` 和
  `Documented symptom after dose change`。另有一个 `Conflict review` 项和多个 Accepted
  项。录制时先找当前仍显示 `Suggested` 的卡片，不要硬编码某一张卡的状态。
- Staff note 已有一条打开状态的内部评论：正文是 synthetic rehearsal comment，页面显示
  `Mentions: @Clinician A`，并有 `Reply`、`Resolve`、`Assign task`。
- 内部 Voice panel 只有 `Synthetic nurse follow-up · clinical`；切换到 Patient 后只有
  `Synthetic patient follow-up · patient`。内部页面当前没有 Voice session result，之前的
  Voice 结果已体现为时间线中的 system-authored AI-scribed 条目。
- 时间线中可见 27 Aug 2026 的 patient-session/nurse-consult Voice-derived 条目，以及
  25 Aug 的手工 Staff/Clinician 条目和更早的历史条目。
- Historical context 显示 9 条 Hot canonical entries、0 条 Warm index older entries、
  April 2025 的 derived summary、2 个 source pointers 和 2 个 `View original record` 按钮。

## 录制前必须准备

1. 打开 Render 服务，等待页面显示 `Live updates: Connected`；先等待 free instance 唤醒。
2. 选择 `English`，患者选择保持为 `Sarah Tan`。
3. 关闭 `Guide`、DevTools、浏览器通知、密码管理器弹窗和任何系统提示。
4. 确认没有 `Source`、`Comments`、`History` 或 `Task` drawer 残留；每个镜头开始前让
   鼠标停在页面空白处。
5. Staff 镜头先检查当前仍有可用的 Suggested 卡片；如果卡片状态已改变，使用当前仍显示
   `Suggested` 的卡片，并同步修改口播中的项目名称。
6. 如果需要展示 Voice 处理，Clinical sample 和 Patient sample 各最多点击一次
   `Process sample`。如果当前已有 result，直接展示已有结果，不要再次处理。
7. 录制前不要点击 `Accept`、`Reject`、`Save revision`、`Add comment`、`Resolve`、
   `Unresolve`、`Pin` 或 `Revert`；这些按钮只在对应镜头中按脚本操作。

## 录制过程中会修改什么

| 操作 | 是否修改线上 synthetic state | 录制要求 |
| --- | --- | --- |
| `Open source` / `Close source` | 否，只修改当前视图和 query | 可重复；关闭后确认 `patient` 保留、`highlight` 消失 |
| `Process sample` | 是，创建 Voice session、AI entry 和 source | 每个 fixture 最多一次 |
| Staff `Save revision` | 是，增加 Staff note 版本 | 记录录制时实际版本，不写死 v1→v2 |
| `Add comment` | 是，增加内部评论和 mention metadata | 只提交一次 synthetic comment |
| `Resolve` / `Unresolve` | 是，切换评论状态并写 metadata | 只做一组切换 |
| `Pin` / `Unpin` | 是，写 importance feedback metadata | 只做一组切换 |
| Clinician `Save revision` | 是，增加 Clinician section 版本 | 只在正式镜头执行 |
| `Revert` | 是，生成新的 revert version | 只点击一次；不要直接改数据库 |
| `View original record`、History、Compare | 否 | 可重复；如实说明 context pointer 的行为 |

## 不要点击

- 不要重置数据库、删除记录或运行 seed。
- 不要打开环境变量、密码、API key、Render Environment、浏览器 storage 或 provider console。
- 不要打开 microphone、upload、Whisper、DeepSeek live call 或任何外部模型配置。
- 不要把当前 `v3`、Accepted 状态或某一张卡片名称写成永久保证；录制前重新观察。
- 不要把 `View original record` 说成 exact-span provenance panel；当前实际行为是滚动到
  canonical timeline entry。

## 收尾检查

- 页面仍为 English，患者和角色范围正确。
- 关闭所有 drawer；鼠标移到空白处后停录。
- 账号切换和密码输入均不出现在画面中。
- 最终视频完成前不更新 PDF、ZIP、MANIFEST，也不 push。
