# BusGap 公交串车检测

对比计划发车间隔与实际到站间隔，识别串车与大间隔，并给出调班建议。

技术栈：Python 3.12 / FastAPI / SQLAlchemy / PostgreSQL / Vue 3 / TypeScript / Vite

## 启动

```bash
docker compose up --build
```

| 服务 | 地址 |
| --- | --- |
| 前端 | http://localhost:4600 |
| API | http://localhost:9600 |
| API 文档 | http://localhost:9600/docs |
| Postgres | localhost:5447 |

健康检查：`GET http://localhost:9600/api/health`

## 使用说明

1. 在「线路」查看运营线路与阈值阈值。
2. 在「班次」「到站」核对计划与实际到站时间，并可对班次或单条到站登记「载客饱和」标记（勾选持久化，离开再进仍在）。
3. 打开「串车报告」执行间隔判定。间隔落入串车阈值且后车带饱和标记时，升为「加重串车」，建议为满载串车、优先抽稀；未饱和仍为普通串车。饱和不影响大间隔与正常判定。
4. 在「时间轴」观察到站分布，在「建议」查看调班提示，加重串车带独立徽标。

## 开发与测试

```bash
docker compose exec api pytest -q
```
