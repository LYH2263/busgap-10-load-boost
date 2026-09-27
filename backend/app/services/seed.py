from datetime import datetime, timedelta
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models.models import Arrival, Line, Trip

def seed_if_empty(db: Session) -> None:
    if (db.scalar(select(func.count()).select_from(Line)) or 0) > 0:
        return
    base = datetime(2026, 9, 17, 7, 0, 0)
    line = Line(code="B12", name="城东环线", planned_headway_min=8.0, bunch_threshold=3.0, large_threshold=15.0)
    db.add(line); db.flush()
    # (班次, 车牌, 发车偏移分钟, 班次级载客饱和)
    specs = [
        ("T01", "粤A1001", 0, False),
        ("T02", "粤A1002", 2, True),   # 紧贴 T01 且全车满载 -> 各站加重串车
        ("T03", "粤A1003", 18, True),  # 与 T02 拉开大间隔；饱和不影响大间隔判定
        ("T04", "粤A1004", 26, False),
        ("T05", "粤A1005", 28, False), # 紧贴 T04；仅火车站一站登记到站饱和
    ]
    stops = ["起点站", "市民中心", "火车站", "终点站"]
    for trip_no, vehicle, offset, trip_saturated in specs:
        trip = Trip(line_id=line.id, trip_no=trip_no,
                    planned_depart=base + timedelta(minutes=offset),
                    vehicle_no=vehicle, saturated=trip_saturated)
        db.add(trip); db.flush()
        for seq, stop in enumerate(stops):
            arrive = base + timedelta(minutes=offset + seq * 6)
            # 到站级饱和：只在该班次该站生效
            arrival_saturated = trip_no == "T05" and stop == "火车站"
            db.add(Arrival(trip_id=trip.id, stop_name=stop, stop_seq=seq,
                           actual_arrive=arrive, saturated=arrival_saturated))
    db.commit()
