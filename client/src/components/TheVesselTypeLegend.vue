<script setup lang='ts'>
import { Icon } from '@iconify/vue'
import { storeToRefs } from 'pinia'
import { useStore } from '../stores/store'

const store = useStore()
const { vesselTypeColor, vesselTypes } = storeToRefs(store)
const vesselType2Text: any = {
  'Entity.Vessel.FishingVessel': 'FishingVessel',
  'Entity.Vessel.CargoVessel': 'CargoVessel',
  'Entity.Vessel.Tour': 'Tour',
  'Entity.Vessel.Other': 'Other',
  'Entity.Vessel.Research': 'Research',
  'Entity.Vessel.Ferry.Passenger': 'Ferry Passenger',
  'Entity.Vessel.Ferry.Cargo': 'Ferry Cargo',
}
</script>

<template>
  <div class="w-full h-full flex text-xs">
    <div class="flex items-center whitespace-nowrap bg-slate-100">Vessel Type Legend</div>
    <div class="flex gap-1 w-full">
      <div v-for="vesselType in vesselTypes" :key="vesselType" class="flex items-center whitespace-nowrap">
        <Icon icon="ic:round-square" :style="{ color: vesselTypeColor(vesselType) }" class="ml-1" width="16" height="16"/>
        {{ vesselType2Text[vesselType] }}
      </div>
    </div>
  </div>
</template>
