<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api } from '../api'
const rows = ref<any[]>([])
const pending = ref<Record<number, boolean>>({})
onMounted(async () => { rows.value = await api('/arrivals') })
async function toggleRow(r: any) {
  const next = !r.saturated
  pending.value[r.id] = true
  try {
    await api(`/arrivals/${r.id}/saturation`, { method: 'PATCH', body: JSON.stringify({ saturated: next }) })
    r.saturated = next
  } finally { pending.value[r.id] = false }
}
</script>
<template>
  <h1>到站</h1>
  <p class="sub">各班次实际到站记录，可按站登记载客饱和（班次已饱和时随班次生效）</p>
  <div class="card">
    <table>
      <thead><tr><th>班次</th><th>站序</th><th>站点</th><th>实际到站</th><th>载客饱和</th></tr></thead>
      <tbody>
        <tr v-for="r in rows" :key="r.id ?? JSON.stringify(r)">
          <td>{{ r.trip_no }}</td>
          <td>{{ r.stop_seq }}</td>
          <td>{{ r.stop_name }}</td>
          <td>{{ r.actual_arrive }}</td>
          <td>
            <label class="sat-check">
              <input
                type="checkbox"
                :checked="r.trip_saturated || r.saturated"
                :disabled="pending[r.id] || r.trip_saturated"
                @change="toggleRow(r)"
              />
              <span v-if="r.trip_saturated" class="muted">随班次</span>
              <span v-else>本站</span>
            </label>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
