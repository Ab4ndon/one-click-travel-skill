#!/usr/bin/env python3
"""Render a one-click-travel HTML page from normalized trip JSON."""

from __future__ import annotations

import argparse
import html
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = ROOT / "assets" / "html-template" / "template.html"


def esc(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def tags_html(tags: list[str], class_name: str = "feature-tag") -> str:
    return "".join(f"<span class=\"{class_name}\">{esc(tag)}</span>" for tag in tags)


def link_button(url: str, label: str, class_name: str = "button") -> str:
    if not url:
        return ""
    return f"<a class=\"{class_name}\" href=\"{esc(url)}\" target=\"_blank\" rel=\"noopener\">{esc(label)}</a>"


def attraction_card(item: dict[str, Any], index: int) -> str:
    image = item.get("image_url")
    image_html = (
        f"<img src=\"{esc(image)}\" alt=\"{esc(item.get('name'))}\" class=\"attraction-image\">"
        if image
        else f"<div class=\"attraction-image attraction-placeholder\">{esc(item.get('name') or '景点')}</div>"
    )
    note = ""
    if item.get("rednote_note_id"):
        note = f"<button class=\"attraction-link\" onclick=\"return openWithFallback('xiaohongshu://explore/{esc(item['rednote_note_id'])}', '{esc(item.get('rednote_url') or item.get('source_url'))}')\">查看小红书攻略</button>"
    elif item.get("rednote_url"):
        note = link_button(item["rednote_url"], "查看小红书攻略", "attraction-link")
    return f"""
    <article class="attraction-card">
      {image_html}
      <div class="attraction-content">
        <div class="attraction-header">
          <span class="attraction-rank">{index}</span>
          <h3 class="attraction-name">{esc(item.get('name'))}</h3>
          <span class="attraction-rating">{esc(item.get('rating') or '暂无评分')}</span>
        </div>
        <div class="attraction-location">{esc(item.get('address'))}</div>
        <div class="attraction-description">{esc(item.get('summary'))}</div>
        <div class="attraction-features">{tags_html(item.get('tags') or [], 'attraction-tag')}</div>
        <div class="attraction-price">价格：{esc(item.get('price') or '以平台实时信息为准')}</div>
        <div class="actions">{link_button(item.get('source_url', ''), '查看来源', 'source-link')}{note}</div>
      </div>
    </article>
    """


def hotel_card(item: dict[str, Any]) -> str:
    meituan = ""
    if item.get("meituan_url"):
        meituan = f"<button class=\"hotel-detail-btn\" onclick=\"return openWithFallback('imeituan://www.meituan.com', '{esc(item['meituan_url'])}')\">打开美团</button>"
    return f"""
    <article class="hotel-card">
      <h3 class="hotel-name">{esc(item.get('name'))}</h3>
      <p class="hotel-address">{esc(item.get('address'))}</p>
      <p class="hotel-summary">{esc(item.get('summary'))}</p>
      <div class="hotel-info">
        <span class="hotel-rating">{esc(item.get('rating') or '美团评分暂无')}</span>
        <span class="hotel-price">{esc(item.get('price') or '以平台实时信息为准')}</span>
      </div>
      <div class="hotel-features">{tags_html(item.get('tags') or [], 'feature-tag')}</div>
      <div class="actions">{meituan}{link_button(item.get('source_url', ''), '查看网页', 'hotel-detail-btn secondary')}</div>
    </article>
    """


def map_data(data: dict[str, Any]) -> str:
    points = []
    for kind, items in (("景点", data.get("attractions", [])), ("酒店", data.get("hotels", [])), ("交通", data.get("transit", []))):
        for item in items:
            if item.get("lng") not in (None, "") and item.get("lat") not in (None, ""):
                points.append({"type": kind, "name": item.get("name"), "lng": item.get("lng"), "lat": item.get("lat"), "address": item.get("address", "")})
    return json.dumps(points, ensure_ascii=False)


def trip_notes_html(notes: list[str]) -> str:
    return "".join(f"<li>{esc(note)}</li>" for note in notes)


def render(data: dict[str, Any], template: str) -> str:
    trip = data.get("trip", {})
    destination = trip.get("destination", "目的地")
    departure = trip.get("departure", "")
    title = f"{departure}去{destination}旅行攻略" if departure else f"{destination}旅行攻略"
    updated_at = trip.get("updated_at") or date.today().isoformat()
    sources = data.get("sources", [])
    source_items = "".join(
        f"<li><a href=\"{esc(src.get('url'))}\" target=\"_blank\" rel=\"noopener\">{esc(src.get('name'))}</a> <span>{esc(src.get('used_for'))}</span></li>"
        for src in sources
        if src.get("url")
    )
    map_cfg = data.get("map", {})
    amap_key = map_cfg.get("amap_key", "")
    amap_security = map_cfg.get("amap_security_js_code", "")
    return (
        template.replace("{{TITLE}}", esc(title))
        .replace("{{DESTINATION}}", esc(destination))
        .replace("{{DEPARTURE}}", esc(departure))
        .replace("{{BUDGET}}", esc(trip.get("budget", "")))
        .replace("{{CHECKIN_DATE}}", esc(trip.get("hotel_checkin_date", "")))
        .replace("{{CHECKOUT_DATE}}", esc(trip.get("hotel_checkout_date", "")))
        .replace("{{UPDATED_AT}}", esc(updated_at))
        .replace("{{TRIP_NOTES}}", trip_notes_html(trip.get("notes") or []))
        .replace("{{ATTRACTIONS}}", "\n".join(attraction_card(item, index) for index, item in enumerate(data.get("attractions", []), start=1)))
        .replace("{{HOTELS}}", "\n".join(hotel_card(item) for item in data.get("hotels", [])))
        .replace("{{SOURCES}}", source_items or "<li>未记录外部来源，页面内容需人工核验。</li>")
        .replace("{{MAP_POINTS_JSON}}", html.escape(map_data(data), quote=False))
        .replace("{{AMAP_KEY}}", esc(amap_key))
        .replace("{{AMAP_SECURITY_JS_CODE}}", esc(amap_security))
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--template", default=str(DEFAULT_TEMPLATE))
    parser.add_argument(
        "--allow-static-map",
        action="store_true",
        help="Allow rendering without an AMap key after the user explicitly skips the live map.",
    )
    args = parser.parse_args()

    data = json.loads(Path(args.input).read_text(encoding="utf-8-sig"))
    if not args.allow_static_map and not data.get("map", {}).get("amap_key"):
        raise SystemExit(
            "AMap key is required for the default live-map page. Ask the user for a 高德 Web JS API Key, "
            "or rerun with --allow-static-map only after the user explicitly skips the live map. "
            "Key creation: https://console.amap.com/dev/key/app ; "
            "prepare guide: https://lbs.amap.com/api/javascript-api-v2/guide/abc/prepare"
        )
    template = Path(args.template).read_text(encoding="utf-8")
    Path(args.output).write_text(render(data, template), encoding="utf-8")


if __name__ == "__main__":
    main()
