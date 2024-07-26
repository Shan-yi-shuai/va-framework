<script setup lang='ts'>
import { Icon } from '@iconify/vue'
import { storeToRefs } from 'pinia'
import { useStore } from '../stores/store'

const store = useStore()
const { locationColor, locationIDs, locationID2Name } = storeToRefs(store)
</script>

<template>
  <div class="w-full h-full flex text-xs">
    <div class="flex items-center whitespace-nowrap bg-slate-100">Location Legend</div>
    <div class="flex gap-1 w-full flex-wrap">
      <div v-for="locationID in locationIDs" :key="locationID" class="flex items-center whitespace-nowrap">
        <Icon icon="ic:round-square" :style="{ color: locationColor(locationID) }" class="ml-1" width="16" height="16"/>
        {{ locationID2Name[locationID] }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.overflow-x-hidden {
  white-space: nowrap;
  overflow-x: hidden;
}

.text-xxs {
  font-size: 0.625rem; /* 10px */
}
</style>
