---
name: vrchat-world-shaders
description: Use when writing VRChat world shaders and VFX under BiRP. Triggers: toon, dissolve, outline, distortion, stylized materials, particle effects, VRChat Build Panel material/shader/texture warnings, SPS-I stereo eye bugs, Quest world shader whitelist questions.
---

# VRChat 世界：特效与风格化材质

让 agent 为 VRChat 世界写 shader / 材质 / 粒子特效时的硬约束与工作流。
适用范围仅限 **世界（world）**，不含 avatar。

## When to Use

- 为 VRChat 世界写 / 改 / 审 shader、材质、粒子与屏幕特效。
- 用户提到 toon、溶解、流动、描边、扭曲、风格化渲染且目标是 VRChat 世界。
- 评审别人给的 Unity shader 是否能在 VRChat 世界里用。
- VRChat SDK Build Panel 报材质 / shader / 贴图相关告警，或头显里出现单眼渲染错误。

不适用：avatar shader（Quest 有白名单）、非 VRChat 的 Unity 项目、URP/HDRP 项目。

## 速查路由

拿到任务先跳到对应章节，不要从头通读：

| 任务 | 先看 |
|---|---|
| 写 / 改风格化 shader、特效 | 第 1 节硬约束 → 第 3 节机制选型 → 第 5 节工作流 |
| Build Panel 出黄条 / 红条 | 第 4 节 → [references/build-validation.md](references/build-validation.md)（严重度模型 + 源码行号 + Auto Fix 副作用） |
| 头显里单眼错位 / 重影 | 第 1.4 条 stereo 宏 → 第 5.4 条失败分类 |
| Editor 有效果、VRChat 里没有 | 第 3.6 条（Reference Camera 禁用）→ 第 4 节 #4、#5 |
| 提交前自查 | 第 5.5 条清单 |
| 场景搭建 / VRC 组件 / 图层 / 上传 / Udon | 不在本 skill，见第 6 节路由 |

## 1. 硬约束（不可协商）

1. **Unity 锁 2022.3.22f1。** 官方明文：用其他版本上传会导致内容无法加载；Unity Hub 的安全升级警告对 VRChat 项目可忽略。不要引入要求更新 Unity 的包或写 6000.x 才有的 API。
2. **只用 Built-in Render Pipeline (BiRP)。** VRChat 官方说明其选用 BiRP 是因为 SRP 出现晚于 VRChat，Unity 不会为其添加 SRP 支持（URP 仅在 `unity-6` open beta 分支实验，创作者不得上传）。因此以下全部不可用：
   - URP/HDRP、Render Graph、`ScriptableRendererFeature`
   - URP Volume 后处理体系（Bloom/Tonemapping 等按 Volume 配的那一套在 VRChat 世界里不存在）
   - SRP Batcher、`HLSLPROGRAM` + SRP includes 的写法
   - 任何 `com.unity.render-pipelines.*` 包
3. **写法只有两条路：**
   - **Surface Shader（CG/HLSL）**：BiRP 下做光照响应最省事的入口，`#pragma surface` 是默认选择；stereo 宏由 Unity 生成代码自动处理。
   - **手写 vertex/fragment（ShaderLab + CGPROGRAM）**：特效类（溶解、流动、全屏扭曲、描边）通常走这条——但必须按第 4 条补齐 stereo 宏链。
   - Shader Graph：2021.2 起有 Built-in target，**但 Unity 官方声明 BiRP 方向只做 bugfix、不接收功能更新**——能用，不作为首选；若项目里已有 Graph 工作流再用，并预期节点能力弱于 URP 教程演示。
4. **手写 shader 必须支持 SPS-I（Single Pass Instanced）。** 依据：VRChat 客户端 2022.1.2 changelog 启用「SPS-I compilation for all shaders at build-time」并修复了 Mobile-ToonLit 的 SPS-I 渲染（说明客户端存在 SPS-I 渲染路径）；VRCSDK 自那以后为上传内容编译 SPS-I 变体。缺 stereo 宏的典型症状：**头显里一只眼画面偏移 / 重影，Editor 里看不出**。要求：
   - 顶点结构体带 `UNITY_VERTEX_INPUT_INSTANCE_ID` + `UNITY_VERTEX_OUTPUT_STEREO`，vert 开头 `UNITY_SETUP_INSTANCE_ID` + `UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO`，fragment 需要眼索引时先 `UNITY_SETUP_STEREO_EYE_INDEX_POST_VERTEX`；instanced 变体需要 `#pragma multi_compile_instancing`。宏链以 Unity 手册「Single Pass Instanced rendering and custom shaders」页为准。
   - surface shader 走 Unity 代码生成，stereo 由生成代码处理，不需要手补。
   - 验收必须 Build & Test 进头显看双眼，Editor Game 视图无法暴露此问题。
5. **agent 不能直接驱动 Editor。** Unity 官方 `unity-cli` skill 的实时控制依赖 `com.unity.pipeline` 包（Unity 6.0+），2022 装不上；同仓库 `shader-graph-create-custom-node`（shadergraph >=17.5）与全部 URP 系 skill 对本项目硬性不兼容。**不要引用 `Unity-Technologies/skills` 作为本项目的工作流依据。**
6. **版本支持边界：本文告警目录与源码行号按 SDK 3.10.5（2026-09-24 核验）**，Unity 2022.3.22f1。项目 SDK 版本不同时，先查本地包源码再引用这些行号，不要照搬。

## 2. VRChat 平台事实（官方文档 + SDK 3.10.5 源码核实）

- **PC 世界**：shader 无白名单限制，Standard 及自写 shader 都可用；性能排名主要落在 shader 复杂度与 fillrate。
- **Quest 世界的 shader 白名单——「不受限」和「有白名单」两个说法都对，分清层级：**
  - 官方文档「Shaders are not restricted for worlds」= **不阻断上传**，属实。
  - SDK 在 **Android/iOS 构建目标下**（`#if UNITY_ANDROID || UNITY_IOS`）扫描场景 shader；白名单（13 项，源码原文见 [references/build-validation.md](references/build-validation.md)）之外的 shader 触发 **`OnGUIWarning` 黄警**。构建阻断只看 `GUIErrors.Count == 0`（`VRCSdkControlPanelBuilder.cs:129,134`），黄警不阻断。
  - 所以：自定义 shader 上 Quest → 有黄条但**能上传**；官方同时要求「性能优先」，推荐 baked lighting + `Mobile/VRChat/Lightmapped`（仅世界可用、不支持实时光）。
- **材质**：官方建议所有材质开启 **Enable GPU Instancing**（avatar + world 通用）。
- 粒子系统、Trail Renderer 等标准 Unity VFX 组件在世界里可用；特效的性能预算主要落在 overdraw 与 fillrate，不是三角形数。

来源：

- https://creators.vrchat.com/sdk/upgrade/current-unity-version （版本锁定）
- https://creators.vrchat.com/platforms/android/quest-content-optimization （Quest 世界 shader 政策、GPU instancing）
- https://creators.vrchat.com/platforms/android/quest-content-limitations （Mobile shader 白名单、Lightmapped 仅限世界）
- https://ask.vrchat.com/t/developer-update-29-june-2023/18711 （BiRP 官方立场）
- https://docs.unity3d.com/Packages/com.unity.shadergraph@12.1/manual/Getting-Started.html （Shader Graph 对 BiRP 只修 bug 的声明）
- https://docs.vrchat.com/docs/vrchat-202212 （SPS-I 构建期编译 + Mobile-ToonLit 修复）
- https://docs.unity3d.com/2022.3/Documentation/Manual/SinglePassInstancing.html （手写 shader 的 stereo 宏链）
- 官方 SDK 源码 `com.vrchat.worlds` / `com.vrchat.base` 3.10.5（github.com/vrchat/packages releases）

## 3. 风格化 / 特效的常用机制（BiRP 语境）

按机制选型，不按「教程用了什么管线」照搬：

1. **光照风格化**：ramp 贴图 / half-Lambert 控 NdotL，配合自定义阴影色；toon 分段用 `smoothstep`/`step` 保留 feather 避免锯齿。全部在 surface shader 的 lighting function 里完成。
2. **描边**：inverted hull（第二个 pass 沿法线膨胀 + `Cull Front`）是 BiRP 标准做法；注意多一个 draw call 与背面膨胀的拓扑要求。
3. **溶解 / 切割**：`clip()`。在 tile-based GPU 上破坏 early-Z，实体表面尽量少用；Quest 上优先把切割限定在小面积或改用 alpha 混合。
4. **流动 / 扭曲**：UV 滚动、噪声扰动；屏幕空间扭曲需要 GrabPass —— 非常贵（整屏拷贝），VRChat 世界里 mirrors 已经很贵，扭曲叠加前先评估场景里是否有镜面。
5. **粒子特效**：优先靠贴图序列帧 + 粒子系统曲线，而不是在 shader 里堆计算；soft particles（深度淡出）在 BiRP 要自己采样 `_CameraDepthTexture`，注意相机深度纹理由项目设置决定，交付前在 Editor 里验证。
6. **后处理**：VRChat 世界没有 URP Volume。Bloom/色彩分级要么烘进贴图，要么用叠加材质/相机脚本方案；相机脚本受 VRChat 播种机制限制，写之前先查当前 SDK 文档，不要假设 `OnRenderImage` 一定被调用。SDK 会对「PostProcessVolume 挂在 Reference Camera/Main Camera」发黄警——该相机运行时被禁用，挂上去的后处理不生效（这解释了「Editor 里有效果、VRChat 里没有」）。

性能通用规则（移动端 GPU 指南，Quest 属 Adreno）：`half` 优先、避免动态分支、限制每 fragment 纹理采样数、少开 render target 切换。这类通用知识可参考社区 `mobile-shader-optimization` 一类的 skill，但**其中 URP/Shader Graph 段落要按 BiRP 改写后再用**。

## 4. 常见错误（NEVER）

| # | NEVER | 为什么 | 改为 |
|---|-------|--------|------|
| 1 | 用 URP / Render Graph / Volume 写法做特效 | BiRP 下 pink shader 或包装不上 | surface shader 或手写 CGPROGRAM（第 1 节） |
| 2 | 手写 vert/frag 却跳过 stereo 宏 | 头显里单眼偏移/重影，Editor 看不出 | 按第 1.4 条补宏链，Build & Test 进头显验双眼 |
| 3 | 效果开关全用 `multi_compile` | 变体爆炸，构建体积直涨 | `shader_feature`，交付前数一遍关键词 |
| 4 | Editor Play 正常就认为 VRChat 里也正常 | Editor Play ≠ SDK 运行时；深度纹理、相机钩子、后处理在客户端行为不同 | Build & Test 验证，不要用 Play 模式当验收 |
| 5 | 忽略 Build Panel 红条（如 Android 非 ASTC） | 红条**直接阻断构建**；黄条里的 Substance / >8192 贴图则是运行时质量与 VRAM 问题 | 见 [references/build-validation.md](references/build-validation.md)：严重度模型 + 每条 Auto Fix 的副作用分级 |
| 6 | 看到「unsupported shader」黄条就以为上传被拒 | 那是 Android/iOS 目标的黄警，不阻断；阻断只看红错 | 先确认是黄是红；黄条按性能自负原则评估，红条必须修 |

Auto Fix 副作用分级（借鉴 niaka3dayo/agent-skills-vrc-udon 的 fix-safety 分类）：设 ASTC = 触发全量 reimport（慢但常规）；贴图降到 8192 = 全局 importer 变更，先确认没有平台单独覆盖；Kaiser mipmap = 远景观感变化；PPV 移动 = 层级变更。**默认先解释再动手，不盲点 Auto Fix。**

## 5. agent ↔ Editor 协作工作流

agent 无法 headless 驱动 2022 Editor，效果验收在用户一侧：

1. **agent 交付固定三件套**（缺一即视为未完成）：
   - `.shader` / `.hlsl` 完整可编译文件，写入项目 Assets 下的明确路径。文件头注释三行：管线（BiRP）；stereo 状态（surface 自动生成 / 宏链已补齐 / 未处理——未处理必须显式标出）；目标平台（PC / 含 Quest）。
   - 材质参数表（markdown 表格）：属性名 | 类型 | 默认值 | 说明 | 关联 Keyword。
   - 验证声明一行：哪些已在本地日志确认编译、哪些**未经验证**（头显效果、Quest 性能、Editor 外行为一律归入未验证，除非有实测证据）。
2. 用户在 Editor 里：赋材质 → 调参 → 看 Scene/Game 视图（必要时 Play 模式看粒子）。
3. **日志由同机 agent 直接读**（Codex、Pi 等能自动拉 Editor 日志的环境不需要用户回贴控制台文本）；用户只需回传**视觉结果**：效果描述、截图、头显观感。跨机无法读日志时才让用户回贴报错原文。
4. 常见失败分类：编译错误（语法/API 版本）→ 读日志直接修；无报错但无效果 → 查关键词没开、贴图没赋、`_CameraDepthTexture` 未启用、材质 keyword 与 pass 不匹配；Editor 正常但头显异常 → 优先查 stereo 宏（第 1.4 条）与客户端运行时差异（第 4 节 #4）；性能问题 → 看 overdraw 与采样数，而不是先优化顶点。
5. 交付前自查清单：
   - 无 `using UnityEngine.Rendering.Universal` / `RenderGraph` / `Volume` 引用
   - 手写 shader 的 stereo 宏链齐全（对照 Unity SPI 手册页）
   - shader 在 2022.3.22f1 编译零报错（同机 agent 读日志确认；读不到时只能声明「未在本地验证编译」）
   - 属性都有合理默认值，Keywords 用 `shader_feature` 而非 `multi_compile`
   - 材质勾选 GPU Instancing
   - 若目标含 Quest：采样数与 `clip` 使用已 review；预期 Build Panel 可能出现的材质类黄条已向用户说明

## 6. 边界与相关 skill

- 本 skill 只覆盖世界侧材质 / 特效 / 风格化 shader 一层。
- **场景搭建、VRC 组件、图层碰撞、烘焙流程、上传** → `niaka3dayo/agent-skills-vrc-udon` 的 `unity-vrc-world-sdk-3`（MIT，last verified SDK 3.10.5；本 skill 的告警目录结构借鉴自它）。
- **UdonSharp 行为、网络同步** → 同仓库 `vrchat-udonsharp`。
- **avatar 的 shader 白名单与性能排名**是另一套规则，不在本 skill 范围。
- 不承诺 VRChat upload 流程、SDK 版本差异 —— 用到时查 creators.vrchat.com 当前文档。
- 文中标注来源的条目为 2026-09 核实（官方文档 + SDK 3.10.5 源码）；未标注来源的机制性描述为通用 Unity/BiRP 知识，未经 VRChat 实机/头显验证。
