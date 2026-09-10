# 灵巧操作与机器人系统

用于面试展示的中文静态视频页。包含六段完整视频、三组项目、触觉双视频对照控制和少量已确认的个人交付说明；没有简历、电话、邮箱或头像。

## 本地预览

在本目录执行：

```bash
python3 scripts/serve.py
```

打开 http://localhost:8000 。预览服务仅监听本机，支持视频 Range 请求与进度拖动。网站本身没有 Python 运行时需求。

## 目录

- `public/`：唯一网站发布目录，包含 HTML、CSS、JavaScript、六段 MP4、封面和 VTT 字幕。
- `scripts/`：本地预览、媒体处理与验收工具，不随 Pages 页面发布。
- `.github/workflows/pages.yml`：将 `public/` 发布到 GitHub Pages 的工作流。
- `review/`：本地核对记录与截图，已忽略，不应推送。

## 视频完整性

原始视频位于上一级 `视频demo/`，不做任何修改。网页视频保留全部画面、全部帧、原始画幅与音轨，不剪切、不加速、不混剪。原素材中的剪辑与拍摄速度不作额外推断。

四段 HEVC 视频转换为 H.264/yuv420p，保持原始分辨率和帧率；已经是 H.264 的遥操作与螺母素材仅无损重封装。所有文件将 MP4 索引移至文件头以快速起播。封面是独立截图，不替换视频片头。字幕是可关闭的独立 VTT 说明，未烧录到视频。

重新准备媒体（需要上一级原始素材）：

```bash
python3 -m pip install imageio-ffmpeg
python3 scripts/prepare_media.py
```

已逐一验证原视频与网页视频帧数一致：触觉成功 1006 帧、无触觉 750 帧、扰动 1311 帧、灯泡 550 帧、螺母 2889 帧、遥操作 3155 帧。完整验证输出见本地 `review/media-integrity.json`。

## 内容口径

- 触觉与无触觉为独立演示，只描述可见案例，不声明统计成功率。
- 灯泡视频保留人工扶持灯座的全过程，并注明这一条件。
- 螺母视频为真机画面，但项目档案对本人贡献目前只确认了训练、蒸馏与仿真验证；当前文案明确限定在此范围。未确认本人真机部署归属前，不扩写该贡献。
- 遥操作视频以机器人端为主，没有虚构操作者同框或自主策略执行。
- 本地页面包含所有六段视频。发布前仍需核对视频的公开范围、螺母归因以及目标 GitHub 账户；网站源码保存于私有仓库；Pages 仅支持手动触发，上传代码不会发布网页。

## 检查

```bash
python3 scripts/check_site.py
node --check public/app.js
```

浏览器验收需要启动预览服务，另执行：

```bash
python3 -m pip install playwright
python3 -m playwright install chromium
python3 scripts/test_browser.py
```

覆盖首次加载不请求视频、六段时长与解码、拖动及结束播放、字幕、全屏、双视频控制、互斥播放、键盘入口、手机布局、项目子路径、视频加载失败及无 JavaScript 回退。截图与结果保存在 `review/`。

## 后续发布到 GitHub Pages

以 **website 目录的内容作为独立 Git 仓库根目录**，不要上传上一级简历工作目录。确定目标账户后：个人站点使用 `<username>.github.io` 仓库；已有个人站点时使用独立项目仓库。本页面全部使用相对路径，无需修改资源路径。

1. 审核六段视频公开范围及页面归因，确认目标仓库。
2. 在 GitHub 仓库 Settings → Pages 中选择 GitHub Actions。
3. 将本目录作为仓库根目录推送至 `main`；确认网页访问范围后，手动触发 Pages 工作流。推送不会自动部署。
4. 工作流先校验文件，再仅上传 `public/`，完成 Pages 部署。
5. 检查实际 HTTPS 地址、视频播放与拖动，以及 `#tactile`、`#dexterity`、`#teleoperation` 三个直达链接。

部署配置遵循 [GitHub Pages 自定义工作流文档](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)。当前站点约 34.4 MiB，不包含原简历或内部项目档案。

## 设计参考

独立实现白底、居中页首、分节视频和并排对照。结构参考 [UMI](https://umi-gripper.github.io/)、[Nerfies](https://nerfies.github.io/) 和 [ALOHA 2](https://aloha-2.github.io/)，未复制其代码、视频、论文标识或作者信息。
