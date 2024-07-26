<script setup lang="ts" generic="T extends any, O extends any">
import { storeToRefs } from 'pinia'
import { Icon } from '@iconify/vue'
import { useStore } from '../stores/store'
import TheVesselSelector from '~/components/TheVesselSelector.vue';
import TheLocationSelector from '~/components/TheLocationSelector.vue';
import TheCommoditySelector from '~/components/TheCommoditySelector.vue';
import TheDateSelector from '~/components/TheDateSelector.vue';
import TheVesselTypeLegend from '~/components/TheVesselTypeLegend.vue';
import TheVesselTSNE from '~/components/TheVesselTSNE.vue';

defineOptions({
  name: 'IndexPage',
})

const store = useStore()
const { vesselMovements, selectedVesselIDs, dateInterval, selectedLocationIDs } = storeToRefs(store)

// 系统初始化
onMounted(() => {
  store.initialize()
})

// 监听变量
watch([selectedLocationIDs, dateInterval], ([newSelectedLocationIDs, newDateInterval]) => {
  if (newSelectedLocationIDs.length > 0
    && new Date('2035-2-1') <= new Date(newDateInterval[0])
    && new Date(newDateInterval[1]) <= new Date('2035-12-31')
  )
    store.getVesselMovements()
}, { immediate: true })

watch([vesselMovements, selectedVesselIDs], ([newVesselMovements, newSelectedVesselIDs]) => {
  if (newVesselMovements.length > 0
    && newSelectedVesselIDs.length > 0
  )
    store.getAggregatedVesselMovements()
}, { immediate: true })

// 动态布局
const vesselTSNEContainer = ref(null)
const vesselTSNEWidth = ref(0)
const vesselTSNEHeight = ref(0)

const vesselMovementContainer = ref(null)
const vesselMovementWidth = ref(0)
const vesselMovementHeight = ref(0)

const aggregatedVesselMovementViewContainer = ref(null)
const aggregatedVesselMovementViewWidth = ref(0)
const aggregatedVesselMovementViewHeight = ref(0)

onMounted(() => {
  if (vesselTSNEContainer.value) {
    const observer = new ResizeObserver(entries => {
      for (let entry of entries) {
        if (entry.target === vesselTSNEContainer.value) {
          const rect = entry.contentRect
          vesselTSNEWidth.value = rect.width
          vesselTSNEHeight.value = rect.height
        }
      }
    })
    observer.observe(vesselTSNEContainer.value)
  }

  if (vesselMovementContainer.value) {
    const observer = new ResizeObserver(entries => {
      for (let entry of entries) {
        if (entry.target === vesselMovementContainer.value) {
          const rect = entry.contentRect
          vesselMovementWidth.value = rect.width
          vesselMovementHeight.value = rect.height
        }
      }
    })
    observer.observe(vesselMovementContainer.value)
  }

  if (aggregatedVesselMovementViewContainer.value) {
    const observer = new ResizeObserver(entries => {
      for (let entry of entries) {
        if (entry.target === aggregatedVesselMovementViewContainer.value) {
          const rect = entry.contentRect
          aggregatedVesselMovementViewWidth.value = rect.width
          aggregatedVesselMovementViewHeight.value = rect.height
        }
      }
    })
    observer.observe(aggregatedVesselMovementViewContainer.value)
  }
})
</script>

<template>
  <div class="w-full h-26 border-2 border-slate-200 m-1">
    <div class="h-6 w-full flex  bg-white gap-2">
      <TheVesselSelector />
      <TheLocationSelector />
      <TheCommoditySelector />
      <TheDateSelector />
    </div>
    <div class="mx-1 h-6 w-[calc(100%-0.5rem)] flex border-1 border-slate-50 bg-white p-1">
      <TheVesselTypeLegend />
    </div>
    <div class="mx-1 h-12 w-[calc(100%-0.5rem)] flex border-1 border-slate-50 bg-white p-1">
      <TheLocationLegend />
    </div>
  </div>

  <div class="h-[calc(100%-6.5rem)] w-full flex border-2 border-slate-200 bg-slate-100 gap-4 m-1 ">
    <div class="h-full w-50% bg-white px-2">
      <div class="w-full h-6 flex border-b-2">
        <div class="w-8 h-full flex items-center justify-center">
          <Icon icon="vaadin:cluster" />
        </div>
        <div class="">Cluster View</div>
      </div>
      <div class="h-[calc(100%-1.5rem)] w-full bg-white" ref="vesselTSNEContainer">
        <TheVesselTSNE :width="vesselTSNEWidth" :height="vesselTSNEHeight" />
      </div>
    </div>
    <div class="h-full w-50% bg-white px-2">
      <div class="w-full h-6 flex border-b-2">
        <div class="w-8 h-full flex items-center justify-center">
          <Icon icon="icon-park-outline:timeline" />
        </div>
        <div class="">Timeline View</div>
      </div>
      <div class="h-[calc(70%-1.5rem)] w-full bg-white " ref="vesselMovementContainer">
        <TheVesselMovementView :width="vesselMovementWidth" :height="vesselMovementHeight" />
      </div>
      <div class="h-30% w-full bg-white " ref="aggregatedVesselMovementViewContainer">
        <TheAggregatedVesselMovementView :width="aggregatedVesselMovementViewWidth"
          :height="aggregatedVesselMovementViewHeight" />
      </div>
    </div>
  </div>
</template>
