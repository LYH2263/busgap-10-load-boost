"""Bus bunching: planned headway vs actual arrival gaps."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime

# 状态档位
STATUS_NORMAL = "normal"
STATUS_BUNCHING = "bunching"
# 加重串车：间隔已落入串车阈值，且后车带载客饱和标记
STATUS_BUNCHING_SATURATED = "bunching_saturated"
STATUS_LARGE_GAP = "large_gap"

@dataclass
class GapEvent:
    stop_name: str
    earlier_trip: str
    later_trip: str
    gap_min: float
    planned_headway_min: float
    status: str
    suggestion: str
    # 后车（later_trip）在该站是否带载客饱和标记
    saturated: bool = False

def classify_gap(gap_min: float, planned_headway_min: float, bunch_threshold: float, large_threshold: float, later_saturated: bool = False) -> tuple[str, str]:
    if gap_min < bunch_threshold:
        if later_saturated:
            return (STATUS_BUNCHING_SATURATED,
                    f"满载串车：间隔 {gap_min:.1f} 分钟低于串车阈值 {bunch_threshold}，且后车已载客饱和，优先抽稀，不建议缓行。")
        return (STATUS_BUNCHING, f"间隔 {gap_min:.1f} 分钟低于串车阈值 {bunch_threshold}，建议后车缓行或抽稀。")
    # 大间隔与正常不受载客饱和影响
    if gap_min > large_threshold:
        return (STATUS_LARGE_GAP, f"间隔 {gap_min:.1f} 分钟超过大间隔阈值 {large_threshold}，建议前车减速或加发。")
    return (STATUS_NORMAL, f"间隔接近计划 {planned_headway_min:.1f} 分钟，保持即可。")

def detect_bunching(arrivals: list[dict], planned_headway_min: float, bunch_threshold: float, large_threshold: float) -> list[GapEvent]:
    by_stop: dict[str, list[dict]] = {}
    for a in arrivals:
        by_stop.setdefault(a["stop_name"], []).append(a)
    events: list[GapEvent] = []
    for stop, items in by_stop.items():
        items = sorted(items, key=lambda x: x["actual_arrive"])
        for i in range(1, len(items)):
            prev, cur = items[i - 1], items[i]
            gap_min = (cur["actual_arrive"] - prev["actual_arrive"]).total_seconds() / 60.0
            later_saturated = bool(cur.get("saturated", False))
            status, suggestion = classify_gap(gap_min, planned_headway_min, bunch_threshold, large_threshold, later_saturated)
            events.append(GapEvent(stop, prev["trip_no"], cur["trip_no"], round(gap_min, 2),
                                   planned_headway_min, status, suggestion, later_saturated))
    return events

def events_to_dicts(events: list[GapEvent]) -> list[dict]:
    return [asdict(e) for e in events]
