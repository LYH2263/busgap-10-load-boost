from datetime import datetime, timedelta
from app.services.bunch_engine import (
    classify_gap,
    detect_bunching,
    STATUS_BUNCHING,
    STATUS_BUNCHING_SATURATED,
    STATUS_LARGE_GAP,
    STATUS_NORMAL,
)

def test_classify_bunching():
    assert classify_gap(2.0, 8.0, 3.0, 15.0)[0] == STATUS_BUNCHING

def test_classify_bunching_saturated():
    status, suggestion = classify_gap(2.0, 8.0, 3.0, 15.0, later_saturated=True)
    assert status == STATUS_BUNCHING_SATURATED
    assert "满载串车" in suggestion
    assert "优先抽稀" in suggestion

def test_classify_bunching_suggests_holding_without_saturation():
    _, suggestion = classify_gap(2.0, 8.0, 3.0, 15.0, later_saturated=False)
    assert "缓行" in suggestion

def test_saturation_does_not_change_large_gap():
    assert classify_gap(16.0, 8.0, 3.0, 15.0, later_saturated=True)[0] == STATUS_LARGE_GAP

def test_saturation_does_not_change_normal():
    assert classify_gap(8.0, 8.0, 3.0, 15.0, later_saturated=True)[0] == STATUS_NORMAL

def test_classify_large():
    assert classify_gap(16.0, 8.0, 3.0, 15.0)[0] == STATUS_LARGE_GAP

def test_classify_normal():
    assert classify_gap(8.0, 8.0, 3.0, 15.0)[0] == STATUS_NORMAL

def test_detect_bunching_events():
    base = datetime(2026, 1, 1, 8, 0)
    arrivals = [
        {"stop_name": "A", "trip_no": "T1", "actual_arrive": base},
        {"stop_name": "A", "trip_no": "T2", "actual_arrive": base + timedelta(minutes=2)},
        {"stop_name": "A", "trip_no": "T3", "actual_arrive": base + timedelta(minutes=20)},
    ]
    events = detect_bunching(arrivals, 8.0, 3.0, 15.0)
    assert len(events) == 2
    assert events[0].status == STATUS_BUNCHING
    assert events[0].saturated is False
    assert events[1].status == STATUS_LARGE_GAP

def test_detect_escalates_when_later_arrival_saturated():
    base = datetime(2026, 1, 1, 8, 0)
    arrivals = [
        {"stop_name": "A", "trip_no": "T1", "actual_arrive": base, "saturated": True},
        # 只有后车饱和才升档；前车饱和不影响
        {"stop_name": "A", "trip_no": "T2", "actual_arrive": base + timedelta(minutes=2), "saturated": False},
        {"stop_name": "A", "trip_no": "T3", "actual_arrive": base + timedelta(minutes=4), "saturated": True},
    ]
    events = detect_bunching(arrivals, 8.0, 3.0, 15.0)
    assert events[0].status == STATUS_BUNCHING          # T1->T2，后车未饱和
    assert events[1].status == STATUS_BUNCHING_SATURATED  # T2->T3，后车饱和
    assert events[1].saturated is True
