# 4 条头条 · 用自己已登录的 Chrome（无弹窗）

脚本 **不会** 再弹 MessageBox，也不会开 Playwright 专用登录窗。

## 一次性准备

1. **完全退出** 所有 Chrome（托盘也退出）。
2. 用调试端口启动 Chrome（登录态仍在你的用户配置里）：

```powershell
& "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
```

3. 若未登录，在 **这个** 窗口打开 [今日头条](https://www.toutiao.com/) 登录（你已登录可跳过）。

## 采集 4 条

```powershell
python e:\carbon-silicon-canonical\scripts\recapture_toutiao4_login_wait.py --attach
```

- 附加到你当前的 Chrome，在已有会话里依次打开 4 篇文章并 P0 截图。
- **采完前不要关浏览器。**

若提示无法连接 CDP，说明 Chrome 不是用 `--remote-debugging-port=9222` 启动的，请按上面第 2 步重来。
