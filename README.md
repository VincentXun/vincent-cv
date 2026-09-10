# Vincent 简历 · 个人项目成果展示

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
- `.github/workflows/pages.yml`：私有源码仓库的验证工作流，不执行部署。发布仓库中另有 Pages 部署工作流。
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
- 本地页面包含所有六段视频。发布前仍需核对视频的公开范围、螺母归因以及目标 GitHub 账户；网站源码保存于私有仓库；另一个公开发布仓库只包含网页资源和 Pages 工作流。

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

## GitHub Pages 发布与更新

展示地址：https://vincentxun.github.io/

当前 GitHub 套餐不支持私有仓库 Pages，因此采用两个仓库：

- 私有源码：`VincentXun/robotics-demo`，包含网站、开发脚本与文档。
- 公开发布：`VincentXun/VincentXun.github.io`，只包含 `public/` 网页资源和 `.github/workflows/pages.yml` 部署工作流。页面、视频、封面与字幕可公开访问。

更新步骤：

1. 在私有源码中修改页面并运行校验；推送私有仓库会自动检查，不发布。
2. 将验证后的 `public/` 同步至公开发布仓库的 `public/`，不要复制开发脚本、原始简历、内部文档或整个父目录。
3. 提交并推送公开发布仓库的 `main`，GitHub Actions 自动发布；也可手动触发工作流。
4. 验证线上页面及 `#tactile`、`#dexterity`、`#teleoperation` 三个项目直达链接。

部署配置遵循 [GitHub Pages 自定义工作流文档](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)。网站约 34.32 MiB。

## 设计参考

独立实现白底、居中页首、分节视频和并排对照。结构参考 [UMI](https://umi-gripper.github.io/)、[Nerfies](https://nerfies.github.io/) 和 [ALOHA 2](https://aloha-2.github.io/)，未复制其代码、视频、论文标识或作者信息。
