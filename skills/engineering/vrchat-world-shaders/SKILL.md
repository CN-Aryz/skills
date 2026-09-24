---
name: vrchat-world-shaders
description: Use when writing VRChat world shaders and VFX under BiRP.
---

# VRChat 世界：特效与风格化材质

让 agent 为 VRChat 世界写 shader / 材质 / 粒子特效时的硬约束与工作流。
适用范围仅限 **世界（world）**，不含 avatar。

## When to Use

- 为 VRChat 世界写 / 改 / 审 shader、材质、粒子与屏幕特效。
- 用户提到 toon、溶解、流动、描边、扭曲、风格化渲染且目标是 VRChat 世界。
- 评审别人给的 Unity shader 是否能在 VRChat 世界里用。

不适用：avatar shader（Quest 有白名单）、非 VRChat 的 Unity 项目、URP/HDRP 项目。

## 1. 硬约束（不可协商）

1. **Unity 锁 2022.3.22f1。** 官方明文：用其他版本上传会导致内容无法加载；Unity Hub 的安全升级警告对 VRChat 项目可忽略。不要引入要求更新 Unity 的包或写 6000.x 才有的 API。
2. **只用 Built-in Render Pipeline (BiRP)。** VRChat 官方说明其选用 BiRP 是因为 SRP 出现晚于 VRChat，Unity 不会为其添加 SRP 支持（URP 仅在 `unity-6` open beta 分支实验，创作者不得上传）。因此以下全部不可用：
   - URP/HDRP、Render Graph、`ScriptableRendererFeature`
   - URP Volume 后处理体系（Bloom/Tonemapping 等按 Volume 配的那一套在 VRChat 世界里不存在）
   - SRP Batcher、`HLSLPROGRAM` + SRP includes 的写法
   - 任何 `com.unity.render-pipelines.*` 包
3. **写法只有两条路：**
   - **Surface Shader（CG/HLSL）**：BiRP 下做光照响应最省事的入口，`#pragma surface` 是默认选择。
   - **手写 vertex/fragment（ShaderLab + CGPROGRAM）**：特效类（溶解、流动、全屏扭曲、描边）通常走这条。
   - Shader Graph：2021.2 起有 Built-in target，**但 Unity 官方声明 BiRP 方向只做 bugfix、不接收功能更新**——能用，不作为首选；若项目里已有 Graph 工作流再用，并预期节点能力弱于 URP 教程演示。
4. **agent 不能直接驱动 Editor。** Unity 官方 `unity-cli` skill 的实时控制依赖 `com.unity.pipeline` 包（Unity 6.0+），2022 装不上；同仓库 `shader-graph-create-custom-node`（shadergraph >=17.5）与全部 URP 系 skill 对本项目硬性不兼容。**不要引用 `Unity-Technologies/skills` 作为本项目的工作流依据。**

## 2. VRChat 平台事实（官方文档核实）

- **PC 世界**：shader 无白名单限制，Standard 及自写 shader 都可用；性能排名主要落在 shader 复杂度与 fillrate。
- **Quest (Android) 世界**：shader 同样不受限制，但官方要求「性能优先」；推荐 baked lighting + `Mobile/VRChat/Lightmapped`（仅世界可用、不支持实时光）。
- **材质**：官方建议所有材质开启 **Enable GPU Instancing**（avatar + world 通用）。
- 粒子系统、Trail Renderer 等标准 Unity VFX 组件在世界里可用；特效的性能预算主要落在 overdraw 与 fillrate，不是三角形数。

来源：

- https://creators.vrchat.com/sdk/upgrade/current-unity-version （版本锁定）
- https://creators.vrchat.com/platforms/android/quest-content-optimization （Quest 世界 shader 政策、GPU instancing）
- https://creators.vrchat.com/platforms/android/quest-content-limitations （Mobile shader 白名单、Lightmapped 仅限世界）
- https://ask.vrchat.com/t/developer-update-29-june-2023/18711 （BiRP 官方立场）
- https://docs.unity3d.com/Packages/com.unity.shadergraph@12.1/manual/Getting-Started.html （Shader Graph 对 BiRP 只修 bug 的声明）

## 3. 风格化 / 特效的常用机制（BiRP 语境）

按机制选型，不按「教程用了什么管线」照搬：

1. **光照风格化**：ramp 贴图 / half-Lambert 控 NdotL，配合自定义阴影色；toon 分段用 `smoothstep`/`step` 保留 feather 避免锯齿。全部在 surface shader 的 lighting function 里完成。
2. **描边**：inverted hull（第二个 pass 沿法线膨胀 + `Cull Front`）是 BiRP 标准做法；注意多一个 draw call 与背面膨胀的拓扑要求。
3. **溶解 / 切割**：`clip()`。在 tile-based GPU 上破坏 early-Z，实体表面尽量少用；Quest 上优先把切割限定在小面积或改用 alpha 混合。
4. **流动 / 扭曲**：UV 滚动、噪声扰动；屏幕空间扭曲需要 GrabPass —— 非常贵（整屏拷贝），VRChat 世界里 mirrors 已经很贵，扭曲叠加前先评估场景里是否有镜面。
5. **粒子特效**：优先靠贴图序列帧 + 粒子系统曲线，而不是在 shader 里堆计算；soft particles（深度淡出）在 BiRP 要自己采样 `_CameraDepthTexture`，注意相机深度纹理由项目设置决定，交付前在 Editor 里验证。
6. **后处理**：VRChat 世界没有 URP Volume。Bloom/色彩分级要么烘进贴图，要么用叠加材质/相机脚本方案；相机脚本受 VRChat 播种机制限制，写之前先查当前 SDK 文档，不要假设 `OnRenderImage` 一定被调用。

性能通用规则（移动端 GPU 指南，Quest 属 Adreno）：`half` 优先、避免动态分支、限制每 fragment 纹理采样数、少开 render target 切换。这类通用知识可参考社区 `mobile-shader-optimization` 一类的 skill，但**其中 URP/Shader Graph 段落要按 BiRP 改写后再用**。

## 4. agent ↔ Editor 协作工作流

agent 无法 headless 驱动 2022 Editor，效果验收在用户一侧：

1. agent 产出：`.shader` / `.hlsl` 完整可编译文件 + 材质参数表（属性名、推荐值、关键词），写进项目 Assets 下的明确路径。
2. 用户在 Editor 里：赋材质 → 调参 → 看 Scene/Game 视图（必要时 Play 模式看粒子）。
3. 用户回传：**控制台报错全文**（编译错误逐字回贴）+ 效果描述或截图。agent 不得凭空推断「应该没问题」。
4. 常见失败分类：编译错误（语法/API 版本）→ 直接修；无报错但无效果 → 查关键词没开、贴图没赋、`_CameraDepthTexture` 未启用、材质 keyword 与 pass 不匹配；性能问题 → 看 overdraw 与采样数，而不是先优化顶点。
5. 交付前自查清单：
   - 无 `using UnityEngine.Rendering.Universal` / `RenderGraph` / `Volume` 引用
   - shader 在 2022.3.22f1 编译零报错（由用户 Editor 确认，agent 只能声明「未在本地验证编译」）
   - 属性都有合理默认值，Keywords 用 `shader_feature` 而非 `multi_compile`（变体数直接进构建体积）
   - 材质勾选 GPU Instancing
   - 若目标含 Quest：采样数与 `clip` 使用已 review

## 5. 边界

- 本 skill 只覆盖世界侧材质/特效；avatar 的 shader 白名单（Quest）、avatar 性能排名是另一套规则（见同仓库 `vrchat-udonsharp` 覆盖的行为层）。
- 不承诺 VRChat upload 流程、SDK 版本差异 —— 用到时查 creators.vrchat.com 当前文档。
- 文中标注来源的条目为 2026-09 核实；未标注来源的机制性描述为通用 Unity/BiRP 知识，未经 VRChat 实机验证。
