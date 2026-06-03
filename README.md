# One Click Travel Skill

`one-click-travel` is a Codex skill for generating a shareable Chinese travel-guide HTML page from a destination city. It combines map markers, Xiaohongshu-informed attraction planning, Meituan hotel prices, deep links, and a responsive HTML template.

## What It Generates

- A self-contained HTML travel guide.
- Live AMap markers for attractions, hotels, and transit points.
- Hotel cards with tomorrow's 1-night Meituan price by default.
- Attraction cards informed by Xiaohongshu route notes, with official/public sources used for factual verification.
- Mobile-friendly fallback links for Meituan, Xiaohongshu, and normal web pages.
- Optional local or EdgeOne deployment flow.

## Repository Layout

```text
one-click-travel/
├── SKILL.md
├── assets/
│   └── html-template/template.html
├── optional-skills/
│   ├── meituan-travel/SKILL.md
│   └── rednote-skill/SKILL.md
├── references/
│   └── data-schema.md
└── scripts/
    ├── collect_attractions.py
    ├── collect_hotels.py
    ├── deploy_edgeone.py
    ├── generate_html.py
    └── geocode_amap.py
```

## Installation

Copy this folder into your Codex skills directory:

```powershell
Copy-Item -Recurse . "$env:USERPROFILE\.codex\skills\one-click-travel"
```

Restart Codex after installation so the skill can be discovered.

## Required Configuration

### AMap

Live map pages require a 高德 Web JS API Key. If your AMap application enables security verification, also provide `securityJsCode`.

- Create a key: https://console.amap.com/dev/key/app
- Web JS API preparation guide: https://lbs.amap.com/api/javascript-api-v2/guide/abc/prepare

If no key is available, the skill can generate a static coordinate-list version only after the user explicitly chooses to skip the live map.

### Meituan Travel

Meituan is optional but preferred for real hotel prices, ratings, and links.

- Token page: https://developer.meituan.com/zh/v2/dev/token
- The skill checks for a configured token before using `meituan-travel`.
- If Meituan is unavailable or times out, the guide falls back to public hotel sources and omits Meituan deep links.

### Xiaohongshu / Rednote

Xiaohongshu is optional but preferred for route popularity, attraction ordering, practical tips, and note links.

- The skill validates login through `rednote-skill`.
- If login is missing or expired, it asks the user to complete browser login.
- If the user skips login, the skill continues with official/public sources.

## Data Contract

The generated guide uses the schema documented in:

```text
references/data-schema.md
```

Important defaults:

- `hotel_checkin_date`: tomorrow in the user's timezone.
- `hotel_checkout_date`: one day after check-in unless otherwise specified.
- `hotel.price`: preserve the exact Meituan price string when available.
- `hotel.rating`: prefer Meituan rating.
- `confidence`: may be kept internally but is not rendered in the final HTML.

## Script Usage

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

## Typical Prompt

```text
使用 $one-click-travel 帮我制作一个杭州旅游攻略
```

The skill will:

1. Extract destination, budget, and dates.
2. Ask for AMap credentials if not already available.
3. Use Meituan for tomorrow's hotel prices when configured.
4. Use Xiaohongshu notes for route-informed attraction recommendations when logged in.
5. Verify factual fields with official or public sources.
6. Generate the final HTML file.

## Notes

- Do not commit generated guide pages, screenshots, or local data exports unless you intentionally want examples in the repository.
- Do not commit API keys, Meituan tokens, Xiaohongshu cookies, or generated credential files.
- Prices, ratings, opening status, and booking rules should always be treated as real-time platform data.

