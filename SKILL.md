---
name: one-click-travel
description: Generate a travel guide HTML page from a user's destination, including attractions, hotel recommendations, map markers, app/web deep links, and optional EdgeOne deployment. Use when the user asks to create or plan a city travel guide, single-city itinerary, cross-city trip such as Shenzhen to Hong Kong, attraction list, hotel shortlist, or shareable HTML travel page. Works with optional meituan-travel and rednote-skill integrations when available, but must still operate without them by using public web/search sources or user-provided data.
---

# One Click Travel

Generate a self-contained, polished Chinese travel guide HTML page for a destination or cross-city trip. Treat `meituan-travel` and `rednote-skill` as optional accelerators, not hard dependencies.

## Bundled Resources

- `references/data-schema.md`: canonical JSON schema for collected data and generated page input.
- `optional-skills/meituan-travel/SKILL.md`: optional Meituan integration adapter; read only when Meituan data is useful or available.
- `optional-skills/rednote-skill/SKILL.md`: optional Xiaohongshu integration adapter; read only when notes, UGC highlights, or note deep links are useful.
- `scripts/collect_attractions.py`: normalize attraction data from specialist skill output, web research, or user-provided JSON.
- `scripts/collect_hotels.py`: normalize hotel data from specialist skill output, web research, or user-provided JSON.
- `scripts/geocode_amap.py`: fill coordinates using AMap geocoding when a key is available.
- `scripts/generate_html.py`: render the final HTML page from normalized JSON and `assets/html-template/template.html`.
- `scripts/deploy_edgeone.py`: deploy a generated HTML page to EdgeOne Pages with the local EdgeOne CLI when the user wants a shareable EdgeOne preview URL.
- `references/edgeone-cli-deploy.md`: EdgeOne CLI setup, login, deployment, and troubleshooting guidance; read when deployment is requested or when the user asks about publishing.

## Inputs

Extract from the user request:

- `destination`: required destination city or region.
- `departure`: optional origin city for cross-city trips.
- `hotel_city`: lodging city; for cross-city trips infer from the request, otherwise ask only when lodging choice affects the result.
- `budget`: hotel budget; default to "300元左右" when not specified.
- `hotel_checkin_date`: default to tomorrow in the user's timezone.
- `hotel_checkout_date`: default to the day after `hotel_checkin_date` for a 1-night stay unless the user specifies nights/dates.
- `hotel_count`: default 4.
- `attraction_count`: default 10.
- `amap_key` and optional `amap_security_js_code`: required by default for the live map experience. Ask the user for these before HTML generation unless they explicitly choose to skip the live map.
- Deployment preference: return the local HTML file by default, then ask whether to publish it to EdgeOne Pages with the local EdgeOne CLI. Do not require GitHub.

Ask the user only for missing information that blocks the intended result. Do not ask for optional integrations before starting.

For ordinary travel-guide requests, treat the map as part of the intended result. If AMap credentials are missing, pause after extracting the destination and ask:

```text
要生成带实时高德地图的攻略页，请提供高德 Web JS API Key；如果你的应用开启了安全密钥，也请一起提供 securityJsCode。
如果还没有 Key，可以在高德开放平台创建应用并添加 Web端(JS API) Key：
https://console.amap.com/dev/key/app
准备说明：
https://lbs.amap.com/api/javascript-api-v2/guide/abc/prepare
也可以回复“跳过地图”，我会先生成静态坐标版。
```

Continue without credentials only when the user says to skip, says they do not have a key, or explicitly asks for a draft/static version.

## Dependency Policy

Before collecting data, inspect available skills/tools from current context.

Use this priority order:

1. **Installed specialist skills**
   - If `meituan-travel` is available, use it for attractions, hotels, prices, ratings, and purchase links.
   - If `rednote-skill` is available, use it for Xiaohongshu notes, user-generated highlights, images, note URLs, route popularity, and attraction ordering.
   - Read the matching file under `optional-skills/` for query shapes and field mapping.
   - If a specialist skill is available but not configured, guide the user through its setup before falling back:
     - Meituan: ask for a Meituan Travel API Token and provide `https://developer.meituan.com/zh/v2/dev/token`.
     - Xiaohongshu: validate login through the rednote skill; if login is missing or expired, run its manual login flow and ask the user to complete browser login.
2. **General browsing/search fallback**
   - If a specialist skill is unavailable, use available web/search/browser tools to find public pages for attractions, hotels, official tourism pages, map pages, OTA pages, and Xiaohongshu public result pages.
   - Prefer official tourism sites, map/listing pages, hotel brand pages, major OTA listings, and recent reputable travel guides.
3. **User-provided data fallback**
   - If live search is unavailable or blocked, ask the user for links, hotel names, attraction names, or permission to generate a draft from model knowledge.
   - Clearly label draft or unverified data in the output.

Never fail only because `meituan-travel` or `rednote-skill` is missing. Degrade gracefully:

- Missing Meituan data: omit Meituan deep links or use generic web links.
- Missing Xiaohongshu data: omit note IDs/deep links or link to a search result page.
- Missing exact coordinates: geocode through AMap if possible; otherwise use city-level coordinates and mark items as "待定位".
- Missing images: use public image URLs only when source and license are acceptable; otherwise use CSS placeholders or ask the user for images.

## Data Collection

Use `references/data-schema.md` as the target shape. Prefer structured JSON between steps:

1. Gather raw candidate data with installed skills, web research, or user-provided links.
2. Save or pass candidate JSON into `scripts/collect_attractions.py` and `scripts/collect_hotels.py`.
3. If `amap_key` is missing and the user has not explicitly skipped the live map, ask for it before rendering.
4. Run `scripts/geocode_amap.py` if coordinates are missing and an AMap key is available.
5. Run `scripts/generate_html.py` with the normalized trip JSON.
6. After the HTML is generated and validated, ask whether to publish it to EdgeOne Pages unless the user already requested deployment.

Collect attractions:

- Name, area/address, coordinates if available.
- Rating/popularity when available.
- Price or "免费/以现场为准".
- Short reason to visit.
- Image URL when reliable.
- Source URL.
- Xiaohongshu note ID/link when available.
- Confidence: `high`, `medium`, or `low`.

Attraction recommendations should be Xiaohongshu-informed by default when `rednote-skill` is available:

- Search 3-6 Xiaohongshu notes for `{destination} 必去景点 攻略`, `{destination} 两日游/三日游`, and important neighborhoods.
- Extract note titles, route mentions, tags, and interaction counts.
- Use Xiaohongshu to decide route popularity, practical tips, and card copy.
- Use official/map sources to verify addresses, coordinates, ticket/opening/booking rules.
- Render a `查看小红书攻略` link on attraction cards whenever a stable note URL is available.

Collect hotels:

- Name, area/address, coordinates if available.
- Tomorrow's check-in price by default. Use the exact Meituan returned price string when Meituan data is available; do not replace it with approximate text.
- Meituan rating by default. If Meituan is unavailable, leave rating empty or explicitly label the platform; do not show non-Meituan ratings as the primary hotel rating.
- Tags such as "近地铁", "连锁", "近口岸", "亲子", "高性价比".
- Booking/source URL.
- Meituan link when available.
- Confidence.

For cross-city trips, also collect transit/port context when relevant, such as口岸、车站、机场、通关提示、首末班车 or estimated travel time. Use current sources if the detail may change.

## Source Rules

- Keep a small source list in the generated page footer or metadata.
- Do not invent ratings, prices, coordinates, links, or note IDs.
- If sources disagree, prefer recent official/listing sources and mention "价格/开放状态以平台实时信息为准".
- Avoid scraping behind login walls. If Xiaohongshu requires login and `rednote-skill` is unavailable, use public search snippets or skip note details.

## HTML Output

Create one HTML file named:

- `{destination}-travel.html` for single-city trips.
- `{departure}-{destination}-travel.html` for cross-city trips.

The page should include:

- Compact top navigation: 酒店 | 景点 | 地图 | 交通/贴士 when relevant.
- Hero summary with destination, trip mode, budget, and last updated date.
- Hotel section with selectable cards and links.
- Attraction section with top items, images/placeholders, tags, source links, and optional Xiaohongshu links.
- Map section:
  - Live AMap by default, using the user-provided API key.
  - Static fallback with coordinates/address list only when the user explicitly skips AMap or the key is unavailable after asking.
- Mobile-friendly deep-link buttons:
  - Meituan button only when a Meituan URL exists.
  - Xiaohongshu button only when a note ID or URL exists.
  - Web fallback always available when a source URL exists.
- Footer with data sources and "信息以平台实时页面为准". Do not display internal confidence labels in the generated page.

Keep styling self-contained in the HTML unless the project already has a build system. Prefer a clean, practical travel-planning UI over a marketing landing page.

Render with:

```bash
python scripts/generate_html.py --input trip-data.json --output output.html
```

If and only if the user explicitly skipped the live map:

```bash
python scripts/generate_html.py --input trip-data.json --output output.html --allow-static-map
```

## Deep Link Guidance

Use defensive fallbacks. Define `startTime` before mobile deep-link checks.

```javascript
function openWithFallback(deepLink, webUrl, timeout = 1800) {
  const isMobile = /Mobile|Android|iPhone/i.test(navigator.userAgent);
  if (!isMobile || !deepLink) {
    window.open(webUrl, "_blank");
    return false;
  }

  const startTime = Date.now();
  const iframe = document.createElement("iframe");
  iframe.style.display = "none";
  iframe.src = deepLink;
  document.body.appendChild(iframe);

  setTimeout(() => {
    iframe.remove();
    if (Date.now() - startTime < timeout + 500) {
      window.open(webUrl, "_blank");
    }
  }, timeout);

  return false;
}
```

For Xiaohongshu notes, use `xiaohongshu://explore/{noteId}` only when a valid `noteId` is known. Otherwise link to the public note/search URL.

## AMap Guidance

AMap credentials are required for the default live-map page. Before rendering, check whether `map.amap_key` is populated.

If `map.amap_key` is empty and the user has not opted out, stop and ask for a 高德 Web JS API Key. If the user says their AMap app has JS API security enabled, also request `securityJsCode`.

Use this wording:

```text
要生成带实时高德地图的攻略页，请提供高德 Web JS API Key；如果你的应用开启了安全密钥，也请一起提供 securityJsCode。
如果还没有 Key，可以在高德开放平台创建应用并添加 Web端(JS API) Key：
https://console.amap.com/dev/key/app
准备说明：
https://lbs.amap.com/api/javascript-api-v2/guide/abc/prepare
也可以回复“跳过地图”，我会先生成静态坐标版。
```

When the user provides AMap credentials, include:

```javascript
window._AMapSecurityConfig = {
  securityJsCode: "USER_SECURITY_JS_CODE"
};
```

Load the AMap script with the user's key. If the user explicitly skips credentials, do not include a broken script; render an address/coordinate list and a message that the map can be enabled after adding a key.

## Deployment

Use EdgeOne CLI local deployment when the user asks for a public/shareable URL or agrees to publish after generation. Do not require GitHub for deployment. EdgeOne Pages direct-upload deployments can return tokenized preview URLs; treat the full token URL as the shareable output.

After generating the HTML, if the user did not mention deployment, ask:

```text
攻略页已经生成。是否要发布到 EdgeOne Pages 获取可分享的预览链接？我可以用 EdgeOne CLI 从本地直接部署，不需要 GitHub。
```

If the user agrees, read `references/edgeone-cli-deploy.md`, then run:

```bash
python scripts/deploy_edgeone.py --html output.html --project-name destination-travel
```

Deployment behavior:

- Check whether the `edgeone` CLI is installed.
- If missing, guide the user to install it with `npm install -g edgeone`.
- If not logged in, guide the user to run `edgeone login` and complete the browser login.
- Copy the generated HTML into a temporary publish directory as `index.html`.
- Run `edgeone pages deploy <publish-dir> -n <project-name> -e production`.
- Return the full EdgeOne preview token URL only when the CLI reports a successful deployment. Prefer the exact `EDGEONE_DEPLOY_URL=...` value from CLI/script output, keep `eo_token` and `eo_time`, and do not replace it with the bare `edgeone.cool` root domain.
- When returning the link, note that it is a shareable preview URL and may expire; if visitors later see `401 UNAUTHORIZED`, generate a fresh Preview link from the EdgeOne console or redeploy.

If deployment is not requested or cannot be completed, save the HTML locally and tell the user the absolute path. Do not claim a shareable EdgeOne URL was deployed unless the deployment actually completed and returned a full token URL.

## Validation

Before finishing:

- Open or render the HTML when possible.
- Check that navigation, deep-link fallbacks, and map fallback do not throw JavaScript errors.
- Verify mobile layout does not overlap.
- Confirm every external link either exists in collected data or is omitted.
