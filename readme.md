# AltStore 源模板

这个项目帮助你快速搭建自己的 AltStore 源，集中管理 feed.json 的结构和内容。

## 项目结构

```
├── config
│   ├── apps.yaml        # 每个应用的元数据和版本信息
│   └── source.yaml      # 源的基础信息（名称、图标、联系信息等）
├── scripts
│   └── generate_feed.py # 读取 YAML 配置并生成 feed.json
├── feed.json            # 运行脚本后生成的文件，可直接部署到服务器
└── requirements.txt     # 生成脚本所需的依赖
```

## 快速开始

1. 创建 Python 虚拟环境并安装依赖：

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. 根据自己的信息编辑 `config/source.yaml` 和 `config/apps.yaml`。
   - `source.yaml` 保存源的名称、图标、描述等内容。
   - `apps.yaml` 为每个应用配置元数据，`versions` 数组中记录该应用的所有版本。

3. 运行脚本生成 `feed.json`：

   ```bash
   python scripts/generate_feed.py
   ```

   也可以通过参数指定不同的输入或输出路径：

   ```bash
   python scripts/generate_feed.py --source other_source.yaml --apps other_apps.yaml --output public/feed.json
   ```

4. 将生成的 `feed.json` 上传到你的服务器或静态空间（例如 GitHub Pages），即可在 AltStore 中添加你的源地址。

## 编写应用信息的小贴士

- `date` 字段必须使用包含时区的 ISO 8601 格式，例如 `2024-06-01T12:00:00+08:00`。
- `size` 字段是 IPA 文件的字节数，可使用 `ls -l` 或 `stat` 命令获取。
- 如果暂时没有截图或权限说明，可保持空数组 `[]`，脚本会自动处理。
- 建议将 IPA、图标和截图统一托管到可公开访问的 HTTPS 链接，以便 AltStore 能够加载。

## 后续扩展

- 如果你维护多个应用，可以在 `apps.yaml` 中继续追加条目，并为每个应用添加多个版本信息。
- 结合 GitHub Actions 或其他 CI/CD 服务，在发布新版本时自动运行脚本并部署 `feed.json`。
- 根据需要添加更多 AltStore 支持的字段（例如 `beta`、`appPermissions` 详情等），脚本会自动保留 YAML 中提供的额外键值。
