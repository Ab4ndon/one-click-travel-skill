# Data Schema

Use this JSON shape between collection, geocoding, rendering, and deployment scripts.

```json
{
  "trip": {
    "destination": "香港",
    "departure": "深圳",
    "hotel_city": "深圳",
    "budget": "300元左右",
    "hotel_checkin_date": "2026-06-04",
    "hotel_checkout_date": "2026-06-05",
    "mode": "cross-city",
    "updated_at": "2026-06-03",
    "notes": ["价格、开放状态以平台实时信息为准"]
  },
  "attractions": [
    {
      "name": "太平山顶",
      "city": "香港",
      "address": "香港中西区",
      "lng": 114.1503,
      "lat": 22.2759,
      "rating": "4.7",
      "price": "以平台实时信息为准",
      "summary": "适合俯瞰维港夜景。",
      "tags": ["夜景", "地标"],
      "image_url": "",
      "source_url": "https://example.com",
      "source_name": "官方旅游网站",
      "rednote_url": "",
      "rednote_note_id": "",
      "confidence": "medium"
    }
  ],
  "hotels": [
    {
      "name": "示例酒店",
      "city": "深圳",
      "address": "深圳福田口岸附近",
      "lng": 114.068,
      "lat": 22.515,
      "price": "300元左右",
      "rating": "美团真实评分4.8",
      "review_count": "",
      "summary": "近口岸，适合次日过关。",
      "tags": ["近口岸", "连锁"],
      "source_url": "https://example.com",
      "source_name": "酒店平台",
      "meituan_url": "",
      "confidence": "medium"
    }
  ],
  "transit": [
    {
      "name": "福田口岸",
      "type": "port",
      "address": "深圳市福田区",
      "lng": 114.068,
      "lat": 22.515,
      "summary": "适合深圳市区前往香港市区。",
      "source_url": "",
      "confidence": "medium"
    }
  ],
  "sources": [
    {
      "name": "官方旅游网站",
      "url": "https://example.com",
      "used_for": "景点介绍"
    }
  ],
  "map": {
    "amap_key": "",
    "amap_security_js_code": "",
    "center_lng": 114.16,
    "center_lat": 22.28,
    "zoom": 11
  }
}
```

Rules:

- Keep unknown fields empty rather than inventing them.
- `confidence` may be kept internally as one of `high`, `medium`, or `low`, but do not render it in the final HTML.
- Hotel `price` defaults to tomorrow's 1-night check-in price. When Meituan is available, preserve the exact returned price string.
- Hotel `rating` defaults to Meituan rating. Do not render non-Meituan ratings as the primary hotel rating unless the source is explicitly labeled.
- Use source fields for every item that came from live research.
- Store Meituan and Xiaohongshu links separately from generic source links so buttons can be shown conditionally.
