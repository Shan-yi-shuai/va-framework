<template>

    <el-date-picker v-model="value" type="daterange" unlink-panels range-separator="To" start-placeholder="Start date"
        end-placeholder="End date" :shortcuts="shortcuts" size="small" />

</template>

<script lang="ts" setup>
import { storeToRefs } from 'pinia'
import { computed } from 'vue'
import { useStore } from '../stores/store'

const store = useStore()
const { dateInterval } = storeToRefs(store)

const formatDate = (date: Date) => {
  const year = date.getFullYear()
  const month = date.getMonth() + 1 // getMonth() is zero-based
  const day = date.getDate()
  return `${year}-${month}-${day}`
}

const value = computed({
    get: () => dateInterval.value,
    set: (val: any[]) => {
        console.log(val)
        dateInterval.value = val.map(formatDate)
    }
})

const shortcuts = [
    {
        text: 'Last week',
        value: () => {
            const end = new Date()
            const start = new Date()
            start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
            return [start, end]
        },
    },
    {
        text: 'Last month',
        value: () => {
            const end = new Date()
            const start = new Date()
            start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
            return [start, end]
        },
    },
    {
        text: 'Last 3 months',
        value: () => {
            const end = new Date()
            const start = new Date()
            start.setTime(start.getTime() - 3600 * 1000 * 24 * 90)
            return [start, end]
        },
    },
]
</script>

<style scoped>
.demo-date-picker {
    display: flex;
    width: 100%;
    padding: 0;
    flex-wrap: wrap;
}

.demo-date-picker .block {
    padding: 30px 0;
    text-align: center;
    border-right: solid 1px var(--el-border-color);
    flex: 1;
}

.demo-date-picker .block:last-child {
    border-right: none;
}

.demo-date-picker .demonstration {
    display: block;
    color: var(--el-text-color-secondary);
    font-size: 14px;
    margin-bottom: 20px;
}
</style>