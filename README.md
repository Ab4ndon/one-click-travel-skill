# One Click Travel Skill

语言 / Language: [中文](#中文) | [English](#english)

## 中文

`one-click-travel` 是一个用于生成中文旅游攻略 HTML 页面 的 skill，可用于支持 skill 机制的 Agent。用户给出目的地城市后，它会结合高德地图、美团酒店实时价格、小红书攻略路线、景点/酒店卡片和 App/网页跳转链接，生成一个可分享、可本地打开的旅行攻略页。

### 在线 Demo

- Demo 页面：https://www.travel.aihub.wiki/shenzhen-hongkong-map.html

这个示例展示了地图优先布局、酒店卡片、跨城路线说明、景点 Tab 和 App/网页跳转的最终效果。

### 可以生成什么

- 一个自包含的 HTML 旅游攻略页面。
- 高德实时地图，标记景点、酒店和交通点位。
- 默认查询明天入住 1 晚的美团酒店价格。
- 结合小红书笔记路线热度生成景点推荐，再用官方/公开来源核验地址、票价、预约规则等事实信息。
- 移动端支持美团、小红书 App 唤起；失败时 fallback 到网页。
- 可选用 EdgeOne CLI 从本地直接部署，不需要 GitHub；返回可分享的预览 token 链接。

### 仓库结构

```text
one-click-travel/
├── SKILL.md
├── assets/
│   └── html-template/template.html
├── optional-skills/
│   ├── meituan-travel/SKILL.md
│   └── rednote-skill/SKILL.md
├── references/
│   ├── data-schema.md
│   └── edgeone-cli-deploy.md
└── scripts/
    ├── collect_attractions.py
    ├── collect_hotels.py
    ├── deploy_edgeone.py
    ├── generate_html.py
    └── geocode_amap.py
```

### 安装方法

把整个目录复制到 支持 skill 的 Agent 对应 skills 目录：

```powershell
Copy-Item -Recurse . "$env:USERPROFILE\.codex\skills\one-click-travel"
```

安装后重启对应 Agent，新的 skill 才会被发现。

### 必要配置

#### 高德地图

默认生成实时地图页面，因此需要高德 Web JS API Key。如果你的高德应用开启了安全密钥校验，还需要提供 `securityJsCode`。

- 创建 Key：https://console.amap.com/dev/key/app
- Web JS API 准备说明：https://lbs.amap.com/api/javascript-api-v2/guide/abc/prepare

如果没有 Key，只有在用户明确回复“跳过地图”后，skill 才会生成静态坐标清单版。

#### 美团旅行

美团是硬依赖，必须配置后才能生成攻略。配置后可以获取真实酒店价格、评分和美团链接。

- Token 创建地址：https://developer.meituan.com/zh/v2/dev/token
- skill 会先检查本地是否已配置美团 Token。
- 如果美团不可用、Token 缺失或接口鉴权失败，skill 会暂停并要求完成配置，不会降级使用公开酒店来源替代。

#### 小红书 / Rednote

小红书是硬依赖，必须通过 `rednote-skill` 完成登录后才能生成攻略。登录后可以用于判断路线热度、景点排序、实用贴士和攻略链接。

- skill 会通过 `rednote-skill` 校验登录状态。
- 如果登录失效，会引导用户在浏览器中重新登录。
- 如果用户选择跳过登录，skill 会暂停生成，不会继续使用官方/公开来源替代小红书数据。

### 数据结构

生成页面使用的标准数据结构见：

```text
references/data-schema.md
```

关键默认值：

- `hotel_checkin_date`：默认使用用户时区的明天。
- `hotel_checkout_date`：默认入住后一天，即 1 晚。
- `hotel.price`：美团可用时保留美团返回的原始价格字符串。
- `hotel.rating`：优先使用美团评分。
- `confidence`：可在内部保留，但最终 HTML 页面不展示。

### 脚本用法

从标准化 JSON 生成 HTML：

```powershell
python scripts\generate_html.py --input trip-data.json --output output.html
```

只有在用户明确跳过实时地图时，才允许无高德 Key 渲染静态地图版：

```powershell
python scripts\generate_html.py --input trip-data.json --output output.html --allow-static-map
```

标准化景点候选数据：

```powershell
python scripts\collect_attractions.py --input raw-attractions.json --output attractions.json --city 杭州
```

标准化酒店候选数据：

```powershell
python scripts\collect_hotels.py --input raw-hotels.json --output hotels.json --city 杭州 --budget 300元左右
```

使用高德补全缺失坐标：

```powershell
python scripts\geocode_amap.py --input trip-data.json --output trip-data.json --amap-key YOUR_AMAP_KEY --city 杭州
```

使用 EdgeOne CLI 本地部署：

```powershell
python scripts\deploy_edgeone.py --html output.html --project-name hangzhou-travel
```

首次部署前需要安装并登录 EdgeOne CLI：

```powershell
npm install -g edgeone
edgeone login
```

### 典型用法

```text
使用 $one-click-travel 帮我制作一个杭州旅游攻略
```

skill 会：

1. 解析目的地、预算和日期。
2. 如果没有高德 Key，先引导用户提供。
3. 确认美团已配置并查询明天入住 1 晚的酒店实时价。
4. 确认小红书已登录并读取攻略笔记用于景点路线和热度判断。
5. 用官方/公开来源核验地址、坐标、票价、开放和预约规则。
6. 生成最终 HTML 页面。
7. 询问是否需要发布到 EdgeOne Pages；如果需要，用本地 EdgeOne CLI 部署并返回完整预览 token 链接。

### 注意事项

- 不建议把生成的攻略 HTML、截图或本地数据导出提交到仓库，除非你明确想保留示例。
- 不要提交高德 Key、美团 Token、小红书 cookies 或任何凭证文件。
- 酒店价格、评分、开放状态、预约规则都应视为实时平台数据，出行前需要再次核验。

## English

`one-click-travel` is a skill for agents that support skill-based workflows. It is used for generating a shareable Chinese travel-guide HTML page from a destination city. It combines map markers, Xiaohongshu-informed attraction planning, Meituan hotel prices, deep links, and a responsive HTML template.

### Online Demo

- Demo page: https://www.travel.aihub.wiki/shenzhen-hongkong-map.html

This demo shows the map-first layout, hotel cards, cross-city route guidance, attraction tabs, and app/web fallback links.

### What It Generates

- A self-contained HTML travel guide.
- Live AMap markers for attractions, hotels, and transit points.
- Hotel cards with tomorrow's 1-night Meituan price by default.
- Attraction cards informed by Xiaohongshu route notes, with official/public sources used for factual verification.
- Default route planning page with day-by-day route data and AMap route visualization.
- Mobile-friendly fallback links for Meituan, Xiaohongshu, and normal web pages.
- Optional local EdgeOne CLI deployment without GitHub, returning a shareable preview token URL.

### Repository Layout

```text
one-click-travel/
├── SKILL.md
├── assets/
│   └── html-template/template.html
├── optional-skills/
│   ├── meituan-travel/SKILL.md
│   └── rednote-skill/SKILL.md
├── references/
│   ├── data-schema.md
│   └── edgeone-cli-deploy.md
└── scripts/
    ├── collect_attractions.py
    ├── collect_hotels.py
    ├── deploy_edgeone.py
    ├── collect_routes.py
    ├── generate_html.py
    └── geocode_amap.py
```

### Installation

Copy this folder into your skills directory:

```powershell
Copy-Item -Recurse . "$env:USERPROFILE\.codex\skills\one-click-travel"
```

Restart your Agent after installation so the skill can be discovered.

### Required Configuration

#### AMap

Live map pages require a 高德 Web JS API Key. If your AMap application enables security verification, also provide `securityJsCode`.

- Create a key: https://console.amap.com/dev/key/app
- Web JS API preparation guide: https://lbs.amap.com/api/javascript-api-v2/guide/abc/prepare

If no key is available, the skill can generate a static coordinate-list version only after the user explicitly chooses to skip the live map.

#### Meituan Travel

Meituan is required for real hotel prices, ratings, and links.

- Token page: https://developer.meituan.com/zh/v2/dev/token
- The skill checks for a configured token before using `meituan-travel`.
- If Meituan is unavailable, times out, or lacks a valid Token, the skill pauses for setup instead of falling back to public hotel sources.

#### Xiaohongshu / Rednote

Xiaohongshu is required for route popularity, attraction ordering, practical tips, and note links.

- The skill validates login through `rednote-skill`.
- If login is missing or expired, it asks the user to complete browser login.
- If the user skips login, the skill pauses generation instead of continuing with official/public sources as a substitute for Xiaohongshu data.

### Data Contract

The generated guide uses the schema documented in:

```text
references/data-schema.md
```

Important defaults:

- `hotel_checkin_date`: tomorrow in the user's timezone.
- `hotel_checkout_date`: one day after check-in unless otherwise specified.
- `hotel.price`: preserve the exact Meituan price string returned by `meituan-travel`.
- `hotel.rating`: prefer Meituan rating.
- `confidence`: may be kept internally but is not rendered in the final HTML.

### Script Usage

Render HTML from a normalized trip JSON file:

```powershell
python scripts\generate_html.py --input trip-data.json --output output.html
```

Render without a live AMap key only after the user explicitly skips the live map:

```powershell
python scripts\generate_html.py --input trip-data.json --output output.html --allow-static-map
```

Normalize raw attraction candidates:

```powershell
python scripts\collect_attractions.py --input raw-attractions.json --output attractions.json --city 杭州
```

Normalize raw hotel candidates:

```powershell
python scripts\collect_hotels.py --input raw-hotels.json --output hotels.json --city 杭州 --budget 300元左右
```

Fill missing coordinates with AMap geocoding:

```powershell
python scripts\geocode_amap.py --input trip-data.json --output trip-data.json --amap-key YOUR_AMAP_KEY --city 杭州
```

Deploy locally with EdgeOne CLI:

```powershell
python scripts\deploy_edgeone.py --html output.html --project-name hangzhou-travel
```

Install and log in before the first deployment:

```powershell
npm install -g edgeone
edgeone login
```

### Typical Prompt

```text
Use $one-click-travel to create a Hangzhou travel guide.
```

The skill will:

1. Extract destination, budget, and dates.
2. Ask for AMap credentials if not already available.
3. Use Meituan for tomorrow's hotel prices when configured.
4. Use Xiaohongshu notes for route-informed attraction recommendations when logged in.
5. Verify factual fields with official or public sources.
6. Generate default route planning data and render the route timeline plus map route visualization.
7. Generate the final HTML file.
8. Ask whether to publish to EdgeOne Pages; if requested, deploy with the local EdgeOne CLI and return the full preview token URL.

### Notes

- Do not commit generated guide pages, screenshots, or local data exports unless you intentionally want examples in the repository.
- Do not commit API keys, Meituan tokens, Xiaohongshu cookies, or generated credential files.
- Prices, ratings, opening status, and booking rules should always be treated as real-time platform data.
