# Trade Translator

Trade Translator 是一个使用 Python 和 PySide6 构建的桌面翻译工具 MVP，支持自动翻译、流式输出、自定义 OpenAI 兼容模型，以及 Windows/macOS 跨应用快捷键取词。

当前 MVP 版本：`0.1.1`

## 当前 MVP

- 输入停止约 800 毫秒后自动翻译。
- 翻译结果流式显示，并在新译文到达前保留旧译文。
- 支持 DeepSeek 和自定义 OpenAI 兼容接口。
- API Key 保存到操作系统凭据存储，不写入项目文件。
- Windows 默认使用 `Ctrl+Shift+T` 获取所选文字。
- macOS 默认使用 `Command+Shift+T` 获取所选文字。
- 支持修改全局快捷键、测试模型连接和复制译文。
- 快捷键取词后使用独立置顶悬浮窗显示流式译文。
- 使用 SQLite 保存最近的翻译历史，并支持复制和再次使用。
- 自动保存主窗口或悬浮窗最后选择的目标语言。
- 关闭主窗口后默认在后台运行，通过系统托盘恢复窗口或退出。

## 环境要求

- Python 3.10 或更高版本
- PySide6 6.10.1
- Windows 10/11，或 macOS 13 及以上（Intel / Apple Silicon）

## 本地运行

```bash
python -m pip install -r requirements.txt
python app/main.py
```

开发和测试环境：

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

## 后台运行与退出

点击主窗口的关闭按钮（Windows 的 × / macOS 的红色关闭按钮）后，窗口隐藏，应用继续在后台运行。当前翻译和全局快捷键仍然有效；再次使用快捷键取词会显示悬浮翻译窗。关闭悬浮窗也不会结束后台程序。

- Windows：点击任务栏通知区域的 Trade Translator 图标恢复主窗口；右键图标打开菜单。如果图标被折叠，可在通知区域的上箭头中找到。
- macOS：点击顶部菜单栏的 Trade Translator 图标，选择“显示主窗口”。
- 直接打开悬浮窗：在图标菜单中选择“打开悬浮窗”，无需显示主窗口；保留已有内容，也可直接输入文字进行翻译。
- 完全退出：在上述图标的菜单中选择“退出”，会停止翻译、注销快捷键并关闭历史数据库。

每次启动后首次关闭主窗口会尝试显示后台运行提示（系统可能禁止通知）。如果系统托盘不可用，关闭主窗口会按正常方式退出，不会留下没有恢复入口的后台程序。本功能不会设置开机自启动。

## macOS 权限

macOS 第一次使用快捷键取词时，需要在“系统设置 → 隐私与安全性”中允许：

1. 输入监控：监听全局快捷键。
2. 辅助功能：向前台应用发送 `Command+C`。

开发环境中权限列表可能显示 Python 或 Terminal；打包后显示 Trade Translator。授权后请彻底退出并重新启动应用。

## 数据与密钥

模型配置通过 Qt 设置系统保存。API Key 使用系统 Keyring：Windows 对应凭据管理器，macOS 对应钥匙串。`.env`、证书、构建产物和本机 IDE 配置均已排除在 Git 仓库之外。

## 打包

PyInstaller 不是交叉编译器，因此 Windows 安装包必须在 Windows 构建，macOS `.app` 必须在 Mac 构建。

先安装打包依赖：

```bash
python -m pip install -r requirements-build.txt
```

然后执行统一构建脚本：

```bash
python tools/build_app.py
```

脚本会依次校验各处版本号、运行完整测试、生成平台图标、构建应用并运行打包后冒烟测试。只有全部通过后，才会将发布压缩包和对应的 `.sha256` 校验文件写入 `release/`：

- Windows：`TradeTranslator-0.1.1-windows-x86_64.zip`
- Apple Silicon：`TradeTranslator-0.1.1-macos-arm64.zip`
- Intel Mac：`TradeTranslator-0.1.1-macos-x86_64.zip`

正式发布时应同时上传 ZIP 和同名的 `.zip.sha256` 文件。构建脚本只生成本地产物，不会自动创建 Git 标签或上传 GitHub Release。

当前发布包没有代码签名。Windows 可能显示 SmartScreen 提示；macOS 给其他设备分发时，需要后续加入 Apple Developer ID 签名和公证。

## 项目结构

```text
app/                 应用入口和平台组装
platforms/           Windows 与 macOS 原生能力
providers/           模型 Provider 和流式网络处理
settings/            设置及系统凭据存储
history/             SQLite 翻译历史模型与仓储
translation/         翻译请求管理
ui/                  Qt 窗口和 UI 文件
tests/               自动化测试
```

更完整的产品边界和设计记录见 [MVP_Implementation_Plan.md](MVP_Implementation_Plan.md)。
