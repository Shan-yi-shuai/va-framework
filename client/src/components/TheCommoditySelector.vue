<template>
    <el-select v-model="value" multiple clearable collapse-tags placeholder="Select" popper-class="custom-header"
        :max-collapse-tags="1" style="width: 240px" size="small" filterable remote :remote-method="remoteMethod"
        @change="handleSelectChange" @blur="handleSelectBlur">
        <el-option v-for="item in filteredData" :key="item.id" :label="item.label" :value="item.name" />
    </el-select>
</template>

<script lang="ts" setup>
import { storeToRefs } from 'pinia'
import { ref, watch, computed } from 'vue'
import type { CheckboxValueType } from 'element-plus'
import { useStore } from '../stores/store'

const store = useStore()
const { commodities, selectedCommodityIDs, commodityID2Name, commodityName2ID} = storeToRefs(store)
const data: Ref<any[]> = commodities

const searchQuery = ref<string>('')

const value = computed({
    get: () => selectedCommodityIDs.value.map(id => commodityID2Name.value[id]),
    set: (val: CheckboxValueType[]) => {
        selectedCommodityIDs.value = val.map(name => commodityName2ID.value[name])
    }
})


const remoteMethod = (query: string) => {
    searchQuery.value = query
}

const filteredData = computed(() => {
    if (searchQuery.value) {
        return data.value.filter(item =>
            item.label.toLowerCase().includes(searchQuery.value.toLowerCase())
        )
    }
    return data.value
})

const handleSelectChange = () => {
    // Handle select change event if needed
}

const handleSelectBlur = () => {
    // Handle select blur event if needed
}

watch(filteredData, (filteredItems) => {
    const selectedItems = value.value.filter(val => !filteredItems.some(item => item.id === val))
    if (selectedItems.length !== value.value.length) {
        value.value = selectedItems
    }
})
</script>

<style lang="scss">
.custom-header {
    .el-checkbox {
        display: flex;
        height: unset;
    }
}
</style>