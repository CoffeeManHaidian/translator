# Trade Translator

Trade Translator 是一个使用 Python 和 PySide6 构建的桌面翻译工具 MVP，支持自动翻译、流式输出、自定义 OpenAI 兼容模型，以及 Windows/macOS 跨应用快捷键取词。

## 当前 MVP

- 输入停止约 800 毫秒后自动翻译。
- 翻译结果流式显示，并在新译文到达前保留旧译文。
- 支持 DeepSeek 和自定义 OpenAI 兼容接口。
- API Key 保存到操作系统凭据存储，不写入项目文件。
- Windows 默认使用 `Ctrl+Shift+T` 获取所选文字。
- macOS 默认使用 `Command+Shift+T` 获取所选文字。
- 支持修改全局快捷键、测试模型连接和复制译文。

## 环境要求

- Python 3.10 或更高版本
- PySide6 6.10.1
- Windows 10/11，或 macOS 15（Intel / Apple Silicon）

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

## macOS 权限

macOS 第一次使用快捷键取词时，需要在“系统设置 → 隐私与安全性”中允许：

1. 输入监控：监听全局快捷键。
2. 辅助功能：向前台应用发送 `Command+C`。

开发环境中权限列表可能显示 Python 或 Terminal；打包后显示 Trade Translator。授权后请彻底退出并重新启动应用。

## 数据与密钥

模型配置通过 Qt 设置系统保存。API Key 使用系统 Keyring：Windows 对应凭据管理器，macOS 对应钥匙串。`.env`、证书、构建产物和本机 IDE 配置均已排除在 Git 仓库之外。

## 兼容性测试

GitHub Actions 会在以下环境运行完整测试：

- macOS 15 / Apple Silicon
- macOS 15 / Intel

CI 还会直接加载 ApplicationServices 和 CoreFoundation，以检查 Quartz 原生接口是否可用。系统级权限交互和真实跨应用取词仍需在实体 Mac 上完成最终验收。

## 项目结构

```text
app/                 应用入口和平台组装
platforms/           Windows 与 macOS 原生能力
providers/           模型 Provider 和流式网络处理
settings/            设置及系统凭据存储
translation/         翻译请求管理
ui/                  Qt 窗口和 UI 文件
tests/               自动化测试
```

更完整的产品边界和设计记录见 [MVP_Implementation_Plan.md](MVP_Implementation_Plan.md)。
