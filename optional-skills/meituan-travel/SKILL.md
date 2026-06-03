---
name: one-click-travel-meituan-adapter
description: Optional adapter notes for using an installed meituan-travel skill inside one-click-travel. Read when Meituan hotel, attraction, ticket, rating, price, or purchase-link data is useful.
---

# Meituan Travel Adapter

This is not a standalone replacement for the external `meituan-travel` skill. It documents how one-click-travel should use that skill when it is already available, and how to continue when it is not.

## Availability Check

Use `meituan-travel` only if it appears in the current available skills/tools. If it is missing, skip directly to public web/search fallback. Do not ask the user to install it unless they explicitly want Meituan-only data.

## Setup Prompt

Before using the external `meituan-travel` skill, confirm that its Token is configured. If it is missing or the tool reports an authentication error, pause and ask:

```text
要使用美团实时酒旅数据，需要配置美团旅行 API Token。
请前往美团开发者中心创建 Token：
https://developer.meituan.com/zh/v2/dev/token
创建后把 Token 发给我，我会保存到本地配置后继续查询。Token 属于敏感凭证，我不会在最终页面或回复里明文展示。
```

Save the token according to the installed `meituan-travel` skill's own instructions. If the user does not want to provide a Token, continue with public web/search fallback and leave `meituan_url` empty.

## Queries

Attractions:

```text
{destination} 热门景点 TOP10 门票 评分 地址 图片
```

Hotels:

```text
{hotel_city} 酒店 明天入住 1晚 {budget} 连锁品牌 近地铁 评分4.5以上 返回酒店名称 地址 明天价格 美团评分 美团链接
```

Cross-city transit/ports:

```text
{departure} 到 {destination} 口岸 交通 过关 酒店
```

## Mapping

Map returned fields into `references/data-schema.md`:

- hotel/attraction name -> `name`
- address/area -> `address`
- longitude/latitude -> `lng`/`lat`
- price text -> `price` exactly as returned
- Meituan rating -> `rating` exactly as returned, preferably in a form like `美团真实评分4.8`
- Meituan detail or booking link -> `meituan_url` for hotels, `source_url` for attractions
- image URL -> `image_url`
- platform name -> `source_name: "美团"`
- real-time or direct listing data -> `confidence: "high"`

Never reconstruct masked prices such as `￥4XX起`. Preserve them exactly.

## Fallback

When Meituan is unavailable or authentication fails:

- Use hotel brand pages, major OTA pages, map listing pages, or official attraction pages.
- Set `meituan_url` to an empty string.
- Keep `source_url` as the public web source.
- Use `confidence: "medium"` unless the source is official and current.
