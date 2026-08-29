# 外贸翻译软件 MVP 实现方案

## 1. 文档目的

本文定义外贸翻译软件 MVP（Minimum Viable Product）的功能边界、技术架构、跨平台实现方式、开发顺序与验收标准，作为第一阶段开发、测试和评审的统一依据。

本期只验证一条核心链路：

> 用户在 Windows 或 macOS 的其他应用中选中文字，通过全局快捷键获取文字，调用 DeepSeek API 翻译，在悬浮窗中查看并复制译文。

外贸邮件、询盘回复、语气调整等预设 Mode 不属于 MVP，只作为后续扩展方向记录。

---

## 2. MVP 定位与目标

### 2.1 产品定位

本项目是一款面向外贸业务人员的桌面翻译工具，重点解决浏览器、Word、Outlook、即时通信工具等日常工作软件中的快速取词和中英文翻译问题。

MVP 不追求完整的外贸 AI 助手能力，而是先验证以下体验是否稳定、快速且确实有用：

```text
选中文字
    ↓
按全局快捷键
    ↓
获取所选文字
    ↓
弹出悬浮窗并自动翻译
    ↓
查看或复制译文
```

### 2.2 MVP 目标

1. 提供可独立使用的主翻译窗口。
2. 在 Windows 和 macOS 上提供全局快捷键唤起翻译。
3. 通过轻量、可替换的平台实现获取其他应用中的选中文字。
4. 使用 DeepSeek API 完成中英文翻译，并支持流式显示。
5. 通过 Provider 抽象保证以后更换模型时无需改动 UI 和业务层。
6. 保存基础设置与翻译历史，满足内部试用和问题追踪需要。
7. 翻译请求期间不阻塞 UI，错误状态可理解、可恢复。

### 2.3 平台策略

MVP 的功能定义覆盖 Windows 与 macOS。开发顺序为 Windows 优先，Windows 核心链路稳定后再实现 macOS 平台层，以减少双平台并行调试成本。

从第一天起，公共业务代码必须跨平台；全局快捷键、取词和系统凭据等原生能力通过接口隔离，不能散落在 UI 或翻译业务代码中。

---

## 3. MVP 功能范围

### 3.1 本期必须实现

#### 主翻译窗口

- 输入或粘贴原文。
- 自动识别源语言，MVP 无需单独实现本地语言检测器，可由模型根据提示完成。
- 目标语言支持中文和英文切换。
- 发起翻译、显示流式结果、取消正在进行的请求。
- 一键复制译文。
- 显示必要的加载、取消、网络错误和鉴权错误状态。

#### 全局快捷键翻译

- Windows 默认快捷键：`Ctrl + Shift + T`。
- macOS 默认快捷键：`Command + Shift + T`。
- 用户可在设置中修改快捷键。
- 快捷键冲突或注册失败时给出明确提示，不影响主窗口翻译。

#### 悬浮翻译窗口

- 显示源语言/目标语言方向、原文和译文。
- 获取选中文字后自动发起翻译。
- 支持流式更新译文。
- 支持复制译文和关闭窗口。
- 保持在普通应用窗口之上，但不长期抢占输入焦点。

#### DeepSeek API

- 使用用户提供的 API Key 直接从客户端调用 DeepSeek API。
- 模型名称、接口地址等放在 Provider 配置中，不写死在 UI 或业务代码中。
- 使用流式响应；支持取消、超时和错误映射。
- 翻译任务默认关闭推理/思考模式（前提是所选模型和接口支持该参数），以降低延迟和成本。

#### 历史记录与基础设置

- 使用 SQLite 保存简单翻译历史。
- 保存 API Key、默认目标语言和全局快捷键等基础设置。
- API Key 不得硬编码，不得提交到版本库。

### 3.2 本期明确不做

- 外贸邮件、询盘回复、报价回复、投诉回复等预设 Mode。
- 正式、简洁、口语等语气切换。
- AI 润色、续写或自动回复。
- 企业、客户、产品等术语库。
- OCR、截图翻译、图片翻译和文档批量翻译。
- 替换其他应用中的原文。
- Word、Outlook 等专用插件。
- 用户账号、云端同步和团队管理。
- 自建 API 网关或服务端。
- 面向用户的多模型选择界面。
- 语义缓存、复杂缓存失效策略。
- 开机启动；如实现成本很低可提前加入，但不作为 MVP 验收项。

Mode 仅作为后续产品扩展项保留。MVP 中不建立 Mode 枚举、不制作 Mode UI，也不为不同 Mode 维护 Prompt。

---

## 4. PySide6 + Python 跨平台总体架构

### 4.1 推荐技术栈

| 模块 | 技术选择 |
| --- | --- |
| UI | PySide6，Qt Quick/QML |
| 核心语言 | Python 3 |
| 网络 | PySide6 `QNetworkAccessManager` |
| 流式协议处理 | SSE 增量解析 |
| 本地数据库 | SQLite（Python 标准库 `sqlite3`） |
| 普通设置 | `QSettings` |
| Windows 原生能力 | Python `ctypes`/pywin32 调用 Win32 API |
| macOS 原生能力 | PyObjC 调用 AppKit、Quartz 与 Accessibility API |
| 依赖管理 | `venv` + `requirements.txt` |
| 自动化测试 | `pytest` + `pytest-qt` |
| 应用部署 | `pyside6-deploy`，按平台分别生成 `.exe`/`.app` |

项目通过 Python 虚拟环境安装 PySide6。PySide6 安装包自带对应的 Qt 运行库，不依赖开发电脑上已有的 Qt 5.15.2，也不要求最终用户预装 Python 或 Qt。平台依赖通过环境标记隔离：Windows 仅安装 pywin32 等 Windows 依赖，macOS 仅安装 PyObjC 及所需 Framework 绑定。

### 4.2 分层结构

```text
┌──────────────────────────────────────────┐
│ UI                                       │
│ MainWindow / FloatingWindow / Settings   │
└───────────────────┬──────────────────────┘
                    │
┌───────────────────▼──────────────────────┐
│ Translation                              │
│ TranslationManager / Request / Result    │
└───────────────┬───────────────┬──────────┘
                │               │
┌───────────────▼────────┐ ┌────▼──────────┐
│ Provider               │ │ Persistence   │
│ TranslationProvider    │ │ History/Settings
│ DeepSeekProvider       │ │ SQLite/QSettings
└────────────────────────┘ └───────────────┘

┌──────────────────────────────────────────┐
│ Platform                                 │
│ GlobalHotkey / TextCapture               │
│ Windows implementations / macOS impls    │
└──────────────────────────────────────────┘
```

### 4.3 核心调用关系

```text
MainWindow ─────────┐
                    ├─→ TranslationManager
FloatingWindow ─────┘           │
                                ▼
                     TranslationProvider
                                │
                                ▼
                       DeepSeekProvider
                                │
                                ▼
                         DeepSeek API
```

`MainWindow` 和 `FloatingWindow` 只负责交互与展示，不能直接拼装 HTTP 请求或依赖 DeepSeek 特有字段。`TranslationManager` 负责请求生命周期、并发控制、取消、错误归一化和历史记录写入。

### 4.4 关键数据对象

`TranslationRequest` 至少包含：

```python
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TranslationRequest:
    text: str
    source_language: str  # MVP 固定为 "auto"
    target_language: str  # 例如 "zh-CN" 或 "en"
    request_id: str
```

统一的结果/事件应覆盖：

- 请求开始。
- 流式文本增量。
- 请求成功完成。
- 请求取消。
- 鉴权、限流、网络、超时、服务端和响应解析错误。

同一窗口发起新任务时，应取消或废弃旧任务，避免旧响应覆盖新结果。所有网络操作必须异步执行，不允许阻塞 UI 线程。

---

## 5. 模型可替换设计

### 5.1 Provider 接口

即使 MVP 只有 DeepSeek，也必须保留模型 Provider 抽象：

```python
from abc import ABC, abstractmethod


class TranslationProvider(ABC):
    @abstractmethod
    def translate(self, request: TranslationRequest) -> None:
        """异步启动翻译，并通过事件或 Qt 信号上报结果。"""

    @abstractmethod
    def cancel(self, request_id: str) -> None:
        """取消指定请求。"""
```

实际 PySide6 实现可让 Provider 同时继承 `QObject` 和抽象接口，通过 Qt 信号上报增量文本、完成和错误；业务层只依赖接口约定，不依赖 `DeepSeekProvider` 的具体类型。网络请求由 Qt 事件循环异步驱动，不为每个请求额外创建线程。

### 5.2 DeepSeekProvider 职责

`DeepSeekProvider` 只负责：

- 将通用 `TranslationRequest` 转换为 DeepSeek/OpenAI-Compatible 请求。
- 读取 Provider 配置中的 `baseUrl`、`model` 和请求参数。
- 添加鉴权请求头。
- 通过 `QNetworkAccessManager` 发起请求，并通过 `QNetworkReply.abort()` 取消请求。
- 解析 SSE 流式响应。
- 将厂商错误转换为统一错误类型。
- 在响应包含缓存命中统计时采集相关指标。

不属于 `DeepSeekProvider` 的职责：

- 操作窗口控件。
- 注册快捷键或读取剪贴板。
- 直接写入历史记录。
- 决定悬浮窗何时显示。

### 5.3 可配置而非写死

当前项目计划使用 `deepseek-v4-flash`，但应作为配置值处理：

```json
{
  "provider": "deepseek",
  "base_url": "https://api.deepseek.com",
  "model": "deepseek-v4-flash"
}
```

接口地址、模型标识和厂商支持的参数应在接入时根据实际 API 文档确认。以后更换模型时新增 Provider 或调整 Provider 配置，UI、历史记录和平台层无需重构。

MVP 不提供多模型 UI，也不要求实现第二个 Provider；可替换性通过接口边界和自动化测试保证。

---

## 6. Windows/macOS 全局快捷键方案

### 6.1 统一接口

```python
from abc import ABC, abstractmethod


class GlobalHotkey(ABC):
    @abstractmethod
    def register_hotkey(self, hotkey: "Hotkey") -> bool:
        pass

    @abstractmethod
    def unregister_hotkey(self) -> None:
        pass
```

上层只处理“快捷键被触发”和“注册成功/失败”，不感知具体平台 API。

### 6.2 Windows

- 使用 Python `ctypes` 或 pywin32 调用 Win32 `RegisterHotKey` 注册系统级快捷键。
- 通过 PySide6 原生事件过滤器接收热键消息并转成 Qt 信号。
- 默认使用 `Ctrl + Shift + T`。
- 程序退出、快捷键修改或组件销毁时注销旧快捷键。
- 注册失败通常表示组合键被占用，应提示用户重新设置。

### 6.3 macOS

- 使用 PyObjC 调用 macOS 原生全局热键机制，并封装为 `MacGlobalHotkey`。
- 默认使用 `Command + Shift + T`，优先选择包含 Command 或 Control 的组合。
- MVP 只监听注册的快捷键，不监听用户的全部键盘输入。
- 全局快捷键与“读取其他应用选中文字”的权限是两件事：热键注册成功不代表已经取得 Accessibility 权限。

---

## 7. 跨应用取词方案

### 7.1 统一接口

```python
from abc import ABC, abstractmethod


class TextCapture(ABC):
    @abstractmethod
    def capture_selected_text(self) -> None:
        """异步获取所选文字，并通过 Qt 信号返回结果。"""
```

取词过程可能涉及等待剪贴板变化和权限提示，因此推荐使用异步结果信号，不要设计成会阻塞 UI 的同步调用。

### 7.2 Windows：Clipboard MVP

MVP 使用模拟复制的方式：

```text
用户选中文字
    ↓
按 Ctrl + Shift + T
    ↓
保存当前剪贴板内容
    ↓
模拟 Ctrl+C
    ↓
等待剪贴板变化并读取文本
    ↓
尽力恢复原剪贴板
    ↓
显示悬浮窗并翻译
```

实现注意事项：

- 必须设置短超时，不能无限等待剪贴板变化。
- 应避免把按快捷键前已存在的旧文本误当成新选择。
- MVP 至少可靠保存和恢复常见文本内容；对图片、文件列表、复杂自定义格式的完整无损恢复不作保证。
- 没有选中文字、目标应用禁止复制或超时时，显示简洁提示，不提交空翻译请求。
- 某些高权限应用可能无法被普通权限进程模拟复制，这属于已知兼容性边界。
- 后续可增加基于 Windows UI Automation 的 `UIAutomationTextCapture`，替换当前实现而不改变上层代码。

### 7.3 macOS：Accessibility 优先、Clipboard 回退

macOS 采用以下顺序：

1. 通过 PyObjC 调用 Accessibility API，获取当前聚焦元素及其选中文字。
2. 若目标应用不暴露所选文本，则在用户明确触发快捷键后尝试模拟 `Command+C`，从 Pasteboard 读取文本。
3. 两种方式都失败时给出可操作的错误提示。

权限处理：

- 启动或首次使用悬浮取词时检查 Accessibility 信任状态。
- 未授权时解释用途：“仅在您主动按下快捷键时读取当前所选文字”，并提供前往系统设置的入口。
- 用户拒绝权限后，主窗口手动翻译仍可正常使用。
- Clipboard/Pasteboard 访问应遵循当前 macOS 的隐私提示和授权行为。
- 本期不做截图，因此不申请 Screen Recording 权限。

---

## 8. 悬浮窗设计

### 8.1 布局

```text
┌──────────────────────────────────┐
│ EN → 中文                    ×   │
├──────────────────────────────────┤
│ Could you provide the quotation? │
├──────────────────────────────────┤
│ 请问您能提供报价吗？             │
│                                  │
│                           [复制] │
└──────────────────────────────────┘
```

MVP 只保留：

- 翻译方向。
- 原文。
- 流式更新的译文。
- 复制按钮。
- 关闭按钮。
- 加载和错误状态。

不提供替换原文、重新润色、语气切换、Mode 选择和复杂工具栏。

### 8.2 窗口行为

- 使用无边框、置顶工具窗口实现悬浮效果。
- 优先出现在鼠标附近或当前屏幕的合理位置，并保证窗口完整位于可用屏幕区域。
- 打开时不应破坏用户原应用中的选择状态；非必要不抢占键盘焦点。
- 新的快捷键请求到来时复用窗口并更新内容，不重复创建多个悬浮窗。
- 支持 Esc 或关闭按钮隐藏窗口。
- 翻译失败时保留原文，并提供简短错误信息；用户仍可关闭窗口或回到主窗口。

桌面系统通常不需要类似移动端“显示在其他应用上层”的独立权限。真正需要单独处理的是 macOS Accessibility 等取词权限。

---

## 9. DeepSeek API、固定 Prompt 与缓存考虑

### 9.1 固定 Prompt

MVP 不做动态 Prompt 或 Mode Prompt。System Prompt 使用稳定版本，例如：

```text
You are a professional translation engine.

Translate the user's text accurately and naturally.

Preserve:
- product names
- model numbers
- numbers
- units
- technical terminology

Do not explain the translation.
Only output the translated text.
```

用户消息保持固定结构：

```text
Source language: auto
Target language: Chinese

{text}
```

目标语言为英文时只替换明确的目标语言值，不改变无关前缀。

### 9.2 请求原则

- Prompt 文本和消息顺序固定，维护显式 `promptVersion`。
- 将用户原文放在固定前缀之后。
- 不在 Prompt 中加入随机时间、随机 ID 或会无意义变化的描述。
- 以低随机性参数进行翻译；实际字段和值由接入模型支持情况决定。
- 优先使用流式输出，缩短用户对首字延迟的感知。
- 对最大输入长度设置客户端保护，避免意外提交超长文本。

### 9.3 缓存策略

稳定前缀有利于服务端上下文缓存命中。若 API 响应提供 `prompt_cache_hit_tokens` 和 `prompt_cache_miss_tokens` 等统计，Provider 可记录到调试日志或内部指标中，但不在 MVP UI 中展示。

MVP 的 SQLite 主要保存历史记录，不实现语义缓存。若开发中确认成本低，可增加严格的本地精确缓存，但它不是验收项。精确缓存键至少应包含：

```text
SHA-256(原文 + 源语言 + 目标语言 + provider + model + promptVersion)
```

任何模型或 Prompt 版本变化都必须产生不同缓存键，避免返回过期或语义不一致的译文。

---

## 10. SQLite 历史记录与基础设置

### 10.1 历史记录

建议表结构：

```sql
CREATE TABLE translation_history (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    source_text     TEXT NOT NULL,
    translated_text TEXT NOT NULL,
    source_language TEXT NOT NULL,
    target_language TEXT NOT NULL,
    provider        TEXT NOT NULL,
    model           TEXT NOT NULL,
    created_at      TEXT NOT NULL
);
```

MVP 行为：

- 仅在翻译成功后写入历史。
- 按时间倒序展示。
- 提供简单查看和再次复制，不做收藏、标签、同步和复杂搜索。
- 为历史数量设置合理上限或后续清理策略，避免数据库无限增长。

数据库访问通过 `HistoryRepository` 封装，UI 不直接执行 SQL。

### 10.2 基础设置

设置项包括：

| 设置项 | MVP 行为 |
| --- | --- |
| API Key | 用户输入；不得硬编码或提交版本库 |
| 默认目标语言 | 中文或英文 |
| 全局快捷键 | 按平台提供默认值并允许修改 |
| Provider 配置 | 内部配置，MVP 不提供多模型 UI |
| 开机启动 | 后续可选，不作为验收项 |

普通设置由 PySide6 `QSettings` 管理。API Key 优先通过 Python `keyring` 保存到 Windows Credential Manager 或 macOS Keychain；若内部试用阶段暂时使用本地配置，必须明确其安全限制并确保不进入版本控制，随后再迁移到系统凭据存储。

---

## 11. 推荐目录结构

```text
TradeTranslator/
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── main.py
├── app/
│   ├── __init__.py
│   └── application.py
├── ui/
│   ├── MainWindow.qml
│   ├── FloatingWindow.qml
│   ├── SettingsPage.qml
│   └── HistoryPage.qml
├── translation/
│   ├── __init__.py
│   ├── manager.py
│   └── models.py
├── providers/
│   ├── __init__.py
│   ├── base.py
│   └── deepseek.py
├── network/
│   ├── __init__.py
│   └── sse_parser.py
├── platform/
│   ├── __init__.py
│   ├── hotkey.py
│   ├── text_capture.py
│   ├── windows/
│   │   ├── __init__.py
│   │   ├── global_hotkey.py
│   │   └── text_capture.py
│   └── macos/
│       ├── __init__.py
│       ├── global_hotkey.py
│       └── text_capture.py
├── persistence/
│   ├── __init__.py
│   ├── database.py
│   ├── history_repository.py
│   ├── settings.py
│   └── credentials.py
├── resources/
│   ├── icons/
│   └── resources.qrc
├── packaging/
│   ├── windows/
│   └── macos/
└── tests/
    ├── provider/
    ├── translation/
    ├── network/
    └── persistence/
```

平台目录只包含确实需要原生 API 的 Python 代码。业务对象、网络协议解析、数据库和大部分 UI 在两个平台上共用。公共模块不得在导入阶段直接加载 Win32 或 PyObjC；应用启动时根据 `sys.platform` 创建对应实现，保证另一平台可以正常导入和测试公共代码。

---

## 12. 分阶段开发顺序

### 阶段 1：工程骨架与主窗口翻译

1. 建立 Python 虚拟环境、PySide6 依赖和公共模块目录。
2. 定义 `TranslationRequest`、`TranslationProvider` 和 `TranslationManager`。
3. 实现 `DeepSeekProvider` 的普通请求。
4. 完成主窗口输入、目标语言切换、翻译和复制。
5. 验证 API Key 缺失、鉴权失败和普通网络错误。

完成标志：用户可以在主窗口稳定完成中英翻译，UI 不直接依赖 DeepSeek。

### 阶段 2：流式输出与请求生命周期

1. 实现 SSE 增量解析。
2. 实现流式渲染、取消和超时。
3. 防止过期响应覆盖最新任务。
4. 统一错误类型和用户提示。
5. 为 SSE 解析与 Provider 映射编写测试。

完成标志：长文本可逐步显示，取消后不再写入 UI 或历史，网络异常不会卡死界面。

### 阶段 3：Windows 快捷键、取词和悬浮窗

1. 使用 `ctypes`/pywin32 实现 `WindowsGlobalHotkey`。
2. 使用 Win32 与 Qt Clipboard 实现 Clipboard MVP 取词与超时处理。
3. 实现悬浮窗及屏幕边界定位。
4. 串联“选择文字—快捷键—取词—翻译—复制”。
5. 在浏览器、Word、Outlook/邮件客户端和常用即时通信工具中测试。

完成标志：Windows 核心悬浮翻译链路可供真实用户试用。

### 阶段 4：SQLite 与设置

1. 建立数据库及迁移/建表逻辑。
2. 写入和展示简单历史记录。
3. 保存默认目标语言和快捷键。
4. 通过 Python `keyring` 或平台凭据接口保存 API Key，优先使用 Windows Credential Manager。
5. 验证程序重启后设置和历史仍然可用。

完成标志：MVP 在 Windows 上功能完整，具备持续试用条件。

### 阶段 5：macOS 平台层

1. 使用 PyObjC 实现 `MacGlobalHotkey`。
2. 使用 PyObjC 实现 Accessibility 权限检测、引导和选中文字读取。
3. 增加 Clipboard/Pasteboard 回退路径。
4. 调整 macOS 悬浮窗行为和多屏定位。
5. 通过 `keyring` 或 PyObjC 使用 Keychain 保存 API Key。
6. 在常用 macOS 应用中完成兼容性测试。

完成标志：macOS 达到与 Windows 一致的 MVP 核心体验；不支持 Accessibility 取词的应用可通过回退路径处理或给出明确提示。

### 阶段 6：应用打包与发布

1. 固定 Python、PySide6 和第三方依赖版本，生成可复现的依赖清单。
2. 在 Windows 上使用 `pyside6-deploy` 生成独立运行目录或 `.exe`，并在未安装 Python 和 Qt 的干净环境中测试。
3. 将 Windows 发布目录制作成带快捷方式和卸载入口的安装包。
4. 在 macOS 构建机上使用 `pyside6-deploy` 生成 `.app`；macOS 包不得直接复用 Windows 构建产物。
5. 为 `.app` 配置图标、Bundle Identifier、版本、Accessibility 用途说明和必要的 entitlements。
6. 使用 Developer ID 对 macOS 应用签名，提交 Apple 公证并生成 `.dmg`。
7. 分别在 Intel/Apple Silicon、Windows 常用版本和无开发环境的机器上验证安装、升级、卸载及首次运行。

完成标志：Windows 用户可通过单个安装程序完成安装；macOS 用户可通过已签名、公证的 `.dmg` 安装，目标机器均无需预装 Python、PySide6 或 Qt。

---

## 13. MVP 验收标准

以下条件全部满足，才视为 MVP 完成。

### 13.1 功能验收

1. Windows 与 macOS 主窗口均可输入文本并完成中文、英文目标语言翻译。
2. DeepSeek 返回内容可流式显示，用户可取消请求，翻译过程不阻塞 UI。
3. Windows 用户可在至少浏览器、Word 和一种常用通信/邮件应用中选中文字，按 `Ctrl + Shift + T` 唤起翻译。
4. macOS 用户可在至少浏览器和一种常用办公应用中选中文字，按 `Command + Shift + T` 唤起翻译。
5. macOS 缺少 Accessibility 权限时有清晰说明和设置入口，主窗口翻译仍可使用。
6. 悬浮窗显示原文、译文、翻译方向、加载/错误状态，并可一键复制译文和关闭。
7. 快捷键冲突、未选中文字、取词超时、API Key 无效、网络失败和服务端限流均有可理解提示。
8. 成功翻译会写入 SQLite，重启程序后历史仍可查看。
9. API Key、默认目标语言和快捷键可保存；API Key 不存在于源码和版本库中。
10. Windows 安装包可在未安装 Python、PySide6 和 Qt 的干净系统中完成安装、运行和卸载。
11. macOS 发布包必须在 macOS 构建机生成，并完成签名、公证和目标机安装验证。

### 13.2 架构验收

1. UI 不直接调用 DeepSeek API。
2. `TranslationManager` 只依赖 `TranslationProvider` 抽象接口，更换 Provider 不要求修改主窗口或悬浮窗。
3. Windows/macOS 的快捷键和取词实现位于各自平台目录，并通过统一接口接入。
4. Prompt 具有明确版本且固定前缀，用户原文始终放在公共前缀之后。
5. SSE 解析、请求取消、错误映射和历史仓储至少具备核心自动化测试。
6. 公共模块在 Windows 和 macOS 上均可导入，不会因提前加载另一平台的原生依赖而失败。

### 13.3 稳定性验收

1. 连续执行多次主窗口翻译和悬浮取词，程序不崩溃、不明显泄漏资源、不冻结 UI。
2. 快速连续触发快捷键时，最终只展示最新有效任务的结果，不出现响应串线。
3. 请求取消、超时或网络断开后可以立即发起下一次翻译。
4. 多屏、不同缩放比例下悬浮窗不会完全出现在屏幕之外。

---

## 14. MVP 完成后的扩展方向

在真实用户验证悬浮翻译链路之后，再评估预设 Mode，例如外贸邮件、邮件润色、正式表达、询盘回复和报价回复。它们属于后续产品差异化能力，不进入本 MVP 的功能、数据结构和验收范围。
