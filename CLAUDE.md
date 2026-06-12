# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个**社团见面会**的完整活动工具包，用于 6.13 底力Ultra音游社见面会的全流程支撑。

| 模块 | 目录 | 说明 | 状态 |
|------|------|------|------|
| 活动流程 | `FLOW.md`（根目录） | 整体 Rundown、物料清单、应急预案 | ✅ 已完成 |
| 你画我猜 | `draw&guess/` + 根目录 `index.html` | Flask 抽词 Web 应用 + GitHub Pages 线上版 + 词库 + 活动规则 | ✅ 已完成（词库 230 条） |
| Bingo 卡片 | `bingo/` | 5×5 音游话题 Bingo 卡片生成（发群用） | 🔲 待开发 |

## 文件结构

```
├── FLOW.md                    # 见面会活动流程（主持人手卡）
├── index.html                 # 【线上版】纯静态抽词页面（GitHub Pages 部署用）
├── 你画我猜词库.csv           # 词库主文件（供 index.html 和 Flask 共用）
├── check_words.py             # 词库维护工具（去重检查 + 序号连续性校验）
├── draw&guess/                # 你画我猜模块
│   ├── 你画我猜词库.csv       # 词库副本（本地 Flask 读取用，与根目录 CSV 同步维护）
│   ├── 你画我猜词库.xlsx       # 原始 Excel 词库（已弃用）
│   ├── app.py                  # Flask 抽词小程序后端（局域网模式）
│   ├── templates/index.html    # 抽词小程序前端页面（局域网模式）
│   └── RULE.md                 # 线下活动规则（纯画传递模式）
├── bingo/                     # Bingo 自我介绍提示卡模块（待创建）
├── requirements.txt           # Python 依赖
└── CLAUDE.md                  # 本文件
```

---

## 模块说明

### 0. 活动流程（`FLOW.md`）

见面会完整流程文档，中文撰写，主持人可直接使用。包含：
- 元信息（时间/地点/人数）
- 四阶段流程详解（开场+自我介绍 → 你画我猜 → 社团展望 → 合影+自由活动）
- 物料清单、PPT 内容需求、应急预案

### 1. 你画我猜（`draw&guess/`）

提供**两种部署模式**：

| 模式 | 入口 | 适用场景 | 说明 |
|------|------|----------|------|
| 🌐 线上版（GitHub Pages） | 根目录 `index.html` | 日常使用、发群分享 | 纯静态，修改 CSV 后 1-2 分钟自动生效 |
| 🏠 局域网版（Flask） | `draw&guess/app.py` | 活动现场（无网环境） | 手机连同一 WiFi 即可访问 |

#### 🌐 线上版（根目录 `index.html`）

纯静态单页应用，托管在 GitHub Pages，无需服务器。

- **原理**：浏览器端用 [Papa Parse](https://www.papaparse.com/) 直接 fetch 并解析 CSV，随机抽词逻辑完全在客户端完成
- **部署**：GitHub Pages 从仓库根目录托管，访问 `https://<username>.github.io/<repo>/`
- **更新词库**：编辑 CSV → Commit → 1-2 分钟自动部署生效（GitHub 网页直接编辑或 git push 均可）
- **依赖**：Papa Parse CDN（`cdn.jsdelivr.net`），首次加载约 19KB

#### 🏠 局域网版（`draw&guess/app.py`）

基于 Flask 的局域网 Web 应用，用于活动现场通过手机抽词。纯画传递模式：起始人抽词作画 → 中间成员看画重画 → 最后一人猜词，全程不写字不说话。

#### 启动方式

```bash
pip install -r requirements.txt
python draw&guess/app.py
```

启动后终端会打印本机 IP 和手机访问地址（如 `http://192.168.x.x:5000`）。

#### 页面流程

1. **抽词页** → 点击「抽词」按钮
2. **选词页** → 从 3 个随机词中 3 选 1
3. **结果页** → 大字展示选中词语，可再抽一轮

#### 架构要点（局域网版）

- **动态读取 CSV**：每次请求实时读文件，修改词库无需重启服务
- **单页前端**：纯 HTML+CSS+JS，三屏切换，无框架依赖，移动端适配
- **API 路由**：
  - `GET /` — 前端页面
  - `GET /api/draw` — 返回 3 个随机词语（JSON）
  - `GET /api/word-count` — 返回词库总数
- **配置项**（`app.py` 顶部）：`DRAW_COUNT`（每次抽词数）、`HOST`、`PORT`

#### 词库（`你画我猜词库.csv`）

UTF-8 with BOM 编码，Excel 可直接打开。共 3 列：

| 列名 | 说明 |
|------|------|
| 序号 | 从 1 开始的连续整数 |
| 词 | 词语或短语（可能包含英文、日文等） |
| 解释（若有） | 可选的提示/备注，部分条目为空 |

#### 词库维护规则

- **根目录 CSV 是主文件**：线上版和局域网版共用词库，Flask 启动时优先读取根目录 CSV；`draw&guess/` 下的 CSV 仅作为回退备件
- **序号必须连续**：增删词条后需重新按 1..N 顺序编号
- **编码**：始终使用 UTF-8 with BOM 保存
- **去重检查**：词库中不得出现重复词条，编辑后运行 `python check_words.py` 检查
- **CSV 格式容忍**：`app.py` 中的 `load_words()` 会自动 strip 列名和数据中的空格；线上版使用 Papa Parse 自动处理各种 CSV 边界情况（引号内逗号等）
- **词库内容方向**：减少街机专属词汇，补充互联网热梗 + 大连理工大学相关词汇，目标约 200 条

#### 词库维护工具（`check_words.py`）

```bash
python check_words.py                    # 检查默认 CSV 文件
python check_words.py 你画我猜词库.csv    # 指定文件
```

自动检查：
- 空词条行
- 序号连续性
- 重复词条
- 输出词库总数统计

### 2. Bingo 自我介绍提示卡（`bingo/`）— 待开发

见面会自我介绍环节使用的 Bingo 提示卡，发到 QQ 群供大家参考。

**需求：**
- 5×5 格子，共 25 个音游相关的故事感词条
- 词条示例："在入学前加入了底力Ultra音游社群聊""第一次 FC 的曲子是中文曲"
- 生成网页链接发到 QQ 群，手机可直接查看
- 不做社交互动（不签名不连线），纯粹作为话题提示

**待收集：** Bingo 词条（已分配给其他人）

---

## 待办优先级

| 优先级 | 任务 | 截止 |
|--------|------|------|
| P0 | 确认最终参会人数 | 6.12 |
| P1 | 词库补充热梗 + 大工词汇 | 6.12 |
| P1 | 收集 Bingo 词条（25 条） | 6.12 |
| P1 | 采购饮品 + 糖果 | 6.12 |
| P1 | 制作 PPT（起始人条件 + 限制条件页 + Keynote） | 6.12 |
| P2 | 开发 Bingo 网页卡片生成器 | 6.12 |
| P2 | 准备白纸 + 笔 | 6.13 上午 |
