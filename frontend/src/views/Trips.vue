<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api } from '../api'
const trips = ref<any[]>([])
const events = ref<any[]>([])
const pending = ref<Record<number, boolean>>({})
async function loadEvents() {
  try {
    events.value = (await api('/reports/run?line_id=1', { method: 'POST' })).events || []
  } catch { events.value = [] }
}
onMounted(async () => {
  trips.value = await api('/trips')
  await loadEvents()
})
async function toggleTrip(r: any) {
  const next = !r.saturated
  pending.value[r.id] = true
  try {
    await api(`/trips/${r.id}/saturation`, { method: 'PATCH', body: JSON.stringify({ saturated: next }) })
    r.saturated = next
    await loadEvents()
  } finally { pending.value[r.id] = false }
}
function stripClass(s: string) {
  if (s === 'bunching_saturated') return 'bg-bunch-sat'
  return s === 'bunching' ? 'bg-bunch' : s === 'large_gap' ? 'bg-large' : ''
}
function label(s: string) {
  if (s === 'bunching_saturated') return '加重串车'
  return s === 'bunching' ? '串车' : s === 'large_gap' ? '大间隔' : '正常'
}
</script>
<template>
  <h1>班次 · 间隔条带</h1>
  <p class="sub">左侧班次清单可登记载客饱和，右侧串车/间隔竖直条带</p>
  <div class="bg-split">
    <aside class="bg-trip-col">
      <h2>班次列表</h2>
      <div v-for="r in trips" :key="r.id ?? r.trip_no" class="bg-trip-row">
        <div>
          <div>{{ r.trip_no }}</div>
          <div class="bg-trip-meta">线路 {{ r.line_id }} · 车 {{ r.vehicle_no }}</div>
          <label class="sat-check" style="margin-top:0.25rem">
            <input type="checkbox" :checked="r.saturated" :disabled="pending[r.id]" @change="toggleTrip(r)" />
            载客饱和
          </label>
        </div>
        <div class="bg-trip-meta">{{ r.planned_depart }}</div>
      </div>
    </aside>
    <div class="bg-strip-col">
      <article
        v-for="(e, i) in events"
        :key="i"
        class="bg-gap-strip"
        :class="stripClass(e.status)"
      >
        <header>{{ e.stop_name }}</header>
        <div class="bg-gap-body">
          <div class="bg-gap-val">{{ e.gap_min }}′</div>
          <div>计划 {{ e.planned_headway_min }}′</div>
          <div>{{ e.earlier_trip }} → {{ e.later_trip }}</div>
          <span class="badge" :class="e.status === 'bunching_saturated' ? 'badge-crit' : e.status === 'bunching' ? 'badge-bad' : e.status === 'large_gap' ? 'badge-warn' : 'badge-ok'">
            {{ label(e.status) }}
          </span>
        </div>
      </article>
      <p v-if="!events.length" class="muted">暂无间隔事件</p>
    </div>
  </div>
</template>
