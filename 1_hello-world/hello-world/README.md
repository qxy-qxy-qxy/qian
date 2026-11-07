# Hello World 课堂示例

用于《让世界看到你的Hello World》的课堂演示。Python 3.9 或更新版本即可运行，不需要安装第三方库。

## 本地启动

在这个文件夹内打开终端。Windows：

```powershell
python app.py
```

macOS / Linux：

```bash
python3 app.py
```

浏览器打开 <http://localhost:8000>，点击“向服务器打个招呼”。终端保持运行，按 `Ctrl+C` 停止。

如果系统使用 `py` 启动 Python，可把 `python` 替换成 `py`。如果 8000 端口已被占用，使用 `python app.py --port 8001`，并把浏览器与隧道的目标地址同步改为 8001。

## 文件与演示内容

- `app.py`：页面、一个问候接口及启动入口。课堂中只需修改开头的 `MESSAGE` 和 `VERSION`，重启后即可观察新版。
- `hello-world.service`：systemd 演示配置，假设用户为 `ubuntu`，目录为 `/home/ubuntu/hello-world`。实际使用前核对用户名、目录和 Python 路径。
- `.gitignore`：忽略本地缓存、虚拟环境、私密配置与日志。
- `课堂命令.txt`：课堂压缩包附带的命令，按标注的位置执行，替换占位内容。

接口：`/` 是网页，`/api/hello` 返回问候与版本，`/health` 返回状态和版本。服务不会直接提供仓库文件的下载。

## 范围

这是学习用的最小 HTTP 应用，使用 Python 标准库 `http.server`。它用于课堂练习。
