#!/usr/bin/env python3
"""Generate AltStore feed.json from YAML configuration."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

import yaml

REQUIRED_SOURCE_FIELDS = {
    "name",
    "identifier",
    "iconURL",
    "tintColor",
    "subtitle",
    "description",
}

REQUIRED_APP_FIELDS = {
    "name",
    "bundleIdentifier",
    "developerName",
    "subtitle",
    "localizedDescription",
    "iconURL",
    "versions",
}

REQUIRED_VERSION_FIELDS = {
    "version",
    "date",
    "localizedDescription",
    "downloadURL",
    "size",
}


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fp:
        return yaml.safe_load(fp) or {}


def validate_required(data: dict[str, Any], required: set[str], context: str) -> None:
    missing = required - data.keys()
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(f"缺少必要字段 {missing_list} ({context})")


def ensure_iso8601(date_str: str, context: str) -> str:
    try:
        parsed = dt.datetime.fromisoformat(date_str)
    except ValueError as exc:  # pragma: no cover - defensive
        raise ValueError(f"{context} 使用的日期必须是 ISO 8601 格式，例如 2024-01-01T12:00:00+08:00") from exc

    if parsed.tzinfo is None:
        raise ValueError(f"{context} 必须包含时区信息，例如 +08:00")
    return date_str


def merge_source_and_apps(source_cfg: dict[str, Any], apps_cfg: dict[str, Any]) -> dict[str, Any]:
    source = source_cfg.get("source", {})
    validate_required(source, REQUIRED_SOURCE_FIELDS, "source")

    apps = apps_cfg.get("apps", [])
    if not isinstance(apps, list) or not apps:
        raise ValueError("至少需要在 config/apps.yaml 中配置一个应用")

    normalized_apps: list[dict[str, Any]] = []
    for idx, app in enumerate(apps, start=1):
        validate_required(app, REQUIRED_APP_FIELDS, f"apps[{idx}]")

        versions = app.get("versions", [])
        if not isinstance(versions, list) or not versions:
            raise ValueError(f"apps[{idx}] 必须包含至少一个版本")

        normalized_versions: list[dict[str, Any]] = []
        for vidx, version in enumerate(versions, start=1):
            validate_required(version, REQUIRED_VERSION_FIELDS, f"apps[{idx}].versions[{vidx}]")
            ensure_iso8601(str(version["date"]), f"apps[{idx}].versions[{vidx}].date")

            normalized_versions.append(
                {
                    "version": str(version["version"]),
                    "date": str(version["date"]),
                    "localizedDescription": str(version["localizedDescription"]),
                    "downloadURL": str(version["downloadURL"]),
                    "size": int(version["size"]),
                }
            )

        normalized_apps.append(
            {
                "name": str(app["name"]),
                "bundleIdentifier": str(app["bundleIdentifier"]),
                "developerName": str(app["developerName"]),
                "subtitle": str(app["subtitle"]),
                "localizedDescription": str(app["localizedDescription"]),
                "iconURL": str(app["iconURL"]),
                "tintColor": app.get("tintColor"),
                "category": app.get("category"),
                "screenshots": app.get("screenshots", []),
                "appPermissions": app.get("appPermissions", []),
                "versions": normalized_versions,
            }
        )

    feed: dict[str, Any] = {
        **source,
        "apps": normalized_apps,
    }
    return {key: value for key, value in feed.items() if value not in (None, [], {})}


def generate_feed(source_path: Path, apps_path: Path, output_path: Path) -> None:
    source_cfg = load_yaml(source_path)
    apps_cfg = load_yaml(apps_path)

    feed = merge_source_and_apps(source_cfg, apps_cfg)

    output_path.write_text(json.dumps(feed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate AltStore feed.json from YAML configuration")
    parser.add_argument("--source", type=Path, default=Path("config/source.yaml"), help="源信息的 YAML 文件路径")
    parser.add_argument("--apps", type=Path, default=Path("config/apps.yaml"), help="应用列表的 YAML 文件路径")
    parser.add_argument("--output", type=Path, default=Path("feed.json"), help="输出 feed.json 的路径")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    generate_feed(args.source, args.apps, args.output)
    print(f"已生成 {args.output.resolve()}")


if __name__ == "__main__":
    main()
