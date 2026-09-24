# VRChat SDK Build Panel：材质 / shader / 贴图相关告警

按 SDK **3.10.5** 官方源码（`com.vrchat.worlds` + `com.vrchat.base`，github.com/vrchat/packages releases）核验，2026-09-24。行号基于该版本解包源文件；项目 SDK 不同时先重新核对本地包源码。

结构借鉴 niaka3dayo/agent-skills-vrc-udon（MIT）的 build-validation 目录，只保留本 skill 范围（材质/shader/贴图/后处理/粒子）内的条目。

## 严重度模型

源码 `VRCSdkControlPanelBuilder.cs:129,134`：构建放行条件是 `GUIErrors.Count == 0`。

| 级别 | API | 颜色 | 是否阻断构建 |
|---|---|---|---|
| Error | `OnGUIError` | 红 | **阻断** |
| Warning | `OnGUIWarning` | 黄 | 不阻断 |
| Information | `OnGUIInformation` | 白 | 不阻断 |

原则：红条必须修；黄条解释影响后由用户决定；白条通常可选优化。默认先解释再点 Auto Fix。

## 告警目录（材质/shader 相关）

| 级别 | 告警原文（节选） | 触发条件 | 处理 | 源码位置 |
|---|---|---|---|---|
| 红 | `Default texture format on Android should be set to the newer ASTC format...` | active build target = Android 且 `androidBuildSubtarget != ASTC` | Auto Fix 或手动设 ASTC；多平台构建流程也会自动设。**ASTC 是本目录唯一的红条** | `VRCSdkControlPanelBuilder.cs:561-571`；MPB 自动设置 `VRCSdkControlPanelWorldBuilder.cs:3423-3431` |
| 黄 | `World uses unsupported shader 'X'. This could cause low performance or future compatibility issues.` | **仅** `#if UNITY_ANDROID \|\| UNITY_IOS` 构建目标下，场景 root GameObject 扫描到白名单外 shader | 不阻断上传。白名单 13 项见下。这是性能自负原则的提示，不是拒收 | `VRCSdkControlPanelWorldBuilder.cs:693-706`；白名单 `WorldValidation.cs:531-546` |
| 黄 | `One or more scene objects have Substance materials. This is not supported and may break in game...` | 场景含 Substance（procedural）材质 | 手动 bake 成普通材质（无 Auto Fix）。原始 Substance 源可移到上传场景外保留 | `VRCSdkControlPanelWorldBuilder.cs:653-658` |
| 黄 | `This scene has textures bigger than 8192. Please reduce them to save memory in your world.` | 材质引用贴图的 importer `maxTextureSize > 8192`（`MAX_SDK_TEXTURE_SIZE = 8192`，`VRCSdkControlPanelBuilder.cs:65`） | Auto Fix 设 8192 + reimport。**全局 importer 变更**：先确认没有平台单独覆盖，源贴图保留备份 | `VRCSdkControlPanelWorldBuilder.cs:897`；收集逻辑 `VRCSdkControlPanelBuilder.cs:1145-1165` |
| 黄 | `Scene has a PostProcessVolume on the Reference Camera (Main Camera). This Camera is disabled at runtime...` | Main Camera 子物体挂 `PostProcessVolume`（后处理 v2 类型存在时才检查） | Auto Fix 移到普通 GameObject。挂 Reference Camera 上的后处理运行时不生效——这也解释了「Editor 里有效果、VRChat 里没有」 | `VRCSdkControlPanelWorldBuilder.cs:213-222` |
| 黄 | `Fog shader stripping is set to Custom, this may lead to incorrect or unnecessary shader variants...` | Graphics 设置里 fog stripping = Custom | Auto Fix 设 Automatic。若世界运行时改 fog 模式则需保留 Custom（此情况下 Auto Fix 不适用） | `VRCSdkControlPanelWorldBuilder.cs:559-567` |
| 黄 | `Automatic lightmap generation is enabled, which may stall the Unity build process...` | `Lightmapping.giWorkflowMode == Iterative` | 关闭 Lighting 窗口的 Auto Generate，上传前有意 bake | `VRCSdkControlPanelBuilder.cs`（GI workflow 检查段） |
| 黄 | `You are not using the recommended Unity version for the VRChat SDK...` | 远端 SDK 配置推荐版本 ≠ 当前 Editor | 对 VRChat 项目：确认推荐版本是否 2022.3.22f1；Unity Hub 的安全升级警告可忽略 | `VRCSdkControlPanelBuilder.cs:545-551` |
| 白 | `This scene uses textures with 'Box' mipmap filtering, which blurs distant textures. Switch to 'Kaiser'...` | Unity 2021+ importer `mipmapFilter == Box` | Auto Fix 设 Kaiser（远景更清晰）。若项目开 DPID mipmaps 会被 DPID 覆盖（设置里可关） | `VRCSdkControlPanelWorldBuilder.cs:921-937` |
| 白 | Billboard 粒子 `allowRoll` 提示 | `ParticleSystemRenderMode.Billboard` 且 `allowRoll == true` | Auto Fix 关 roll——相机 roll 在 VR 里易晕；风格化特效若有意用 roll 先预览再批量改 | `VRCSdkControlPanelWorldBuilder.cs:826-855` |
| 白 | `Your world contains one or more Unity text components, but no TextMeshPro components...` | 场景有 `Text`/`TextMesh` 且无 TMP | 建议（世界内 UI 文字清晰度）；装饰性文字不必全迁 | `VRCSdkControlPanelWorldBuilder.cs:539` |
| 白 | `Found one or more UI graphics using Unity's built-in UI shader...` | uGUI `Graphic` 用 `UI/Default` 且 Supersampled UI shader 存在 | Auto Fix 换 `VRCSuperSampledUIMaterial.mat`；**项目自有材质只考虑换 shader 为 `VRChat/Mobile/Worlds/Supersampled UI`，先确认视觉角色，勿覆盖有意的自定义 UI 材质/shader 效果** | `VRCSdkControlPanelWorldBuilder.cs:707+`（`Shader.Find("VRChat/Mobile/Worlds/Supersampled UI")`） |

## Quest world shader 白名单（Android/iOS 目标构建时的黄警依据）

源码原文 `WorldValidation.cs:531-546`（13 项，literal）：

```
VRChat/Mobile/Standard Lite
VRChat/Mobile/Diffuse
VRChat/Mobile/Bumped Diffuse
VRChat/Mobile/Bumped Mapped Specular
VRChat/Mobile/Toon Lit
VRChat/Mobile/MatCap Lit
VRChat/Mobile/Lightmapped
VRChat/Mobile/Skybox
VRChat/Mobile/Particles/Additive
VRChat/Mobile/Particles/Multiply
VRChat/Mobile/World/Supersampled UI
FX/MirrorReflection
UI/Default
```

调用链：`VRCSdkControlPanelWorldBuilder.cs:693-706`（`#if UNITY_ANDROID || UNITY_IOS` 包裹）→ `WorldValidation.FindIllegalShaders(go)` → `ValidationUtils.FindIllegalShaders(target, ShaderWhiteList)`（实现在 `VRCSDKBase.dll`，扫描匹配逻辑未核）→ 每个命中发一条 `OnGUIWarning`。

注意事项：

- 该检查**不阻断构建**（黄警）；官方文档「worlds shader 不受限」指的就是不拒收，两者不矛盾：不阻断 ≠ 无告警。
- PC 构建目标下 `#if` 不编译，此告警根本不会出现。
- 疑似不一致（**未核验，DLL 匹配逻辑未知**）：白名单第 11 项写作 `VRChat/Mobile/World/Supersampled UI`（单数 `World`），而 builder 推荐用的 shader 实名是 `VRChat/Mobile/Worlds/Supersampled UI`（复数，`Shader.Find` 可找到）。若匹配是精确字符串比对，官方推荐的 Supersampled UI shader 本身可能反而命中白名单外——遇到 Supersampled UI 在 Android 构建报「unsupported shader」时先想到这一点，不要因此换掉它。

## 不在本目录的告警

场景描述符、Pipeline Manager、spawn、图层碰撞、PhysBone/Contact、ObjectSync、音频组件、AssetBundle 大小、SDK2/3 混用等 → 属 `unity-vrc-world-sdk-3`（niaka3dayo）范围，本文件不重复。
