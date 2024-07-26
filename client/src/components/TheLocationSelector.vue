<template>
    <el-select v-model="value" multiple clearable collapse-tags placeholder="Select" popper-class="custom-header"
        :max-collapse-tags="1" style="width: 240px" size="small" filterable remote :remote-method="remoteMethod"
        @change="handleSelectChange" @blur="handleSelectBlur">
        <template #header>
            <el-checkbox v-for="(typeLabel, index) in typeLabels" :key="index" v-model="checkedTypes[typeLabel.type]"
                :indeterminate="getIndeterminate(typeLabel.type)" @change="handleCheckType(typeLabel.type)">
                {{ typeLabel.label }}
            </el-checkbox>
        </template>
        <el-option v-for="item in filteredData" :key="item.id" :label="item.label" :value="item.Name" />
    </el-select>
</template>

<script lang="ts" setup>
import { storeToRefs } from 'pinia'
import { ref, watch, computed } from 'vue'
// import type { CheckboxValueType } from 'element-plus'
import { useStore } from '../stores/store'

const store = useStore()
const { locations, selectedLocationIDs, locationID2Name, locationName2ID } = storeToRefs(store)
const data: Ref<any[]> = locations

const searchQuery = ref<string>('')

const checkedTypes = ref<{ [key: string]: boolean }>({})
const indeterminate = ref<{ [key: string]: boolean }>({})
const value = computed({
    get: () => selectedLocationIDs.value.map(id => locationID2Name.value[id]),
    set: (val: string[]) => {
        selectedLocationIDs.value = val.map(name => locationName2ID.value[name])
    }
})

const typeLabels = ref([
    { type: 'Entity.Location.Point', label: 'Point' },
    { type: 'Entity.Location.City', label: 'City' },
    { type: 'Entity.Location.Region', label: 'Region' },
])

typeLabels.value.forEach(({ type }) => {
    checkedTypes.value[type] = true
    indeterminate.value[type] = false
})

watch(value, (val) => {
    typeLabels.value.forEach(({ type }) => {
        const dataOfType = data.value.filter(data => data.type === type)
        const valuesOfType = dataOfType.map(data => data.Name)

        if (val.length === 0) {
            checkedTypes.value[type] = false
            indeterminate.value[type] = false
        } else if (valuesOfType.every(v => val.includes(v)) && val.every(v => valuesOfType.includes(v))) {
            checkedTypes.value[type] = true
            indeterminate.value[type] = false
        } else {
            checkedTypes.value[type] = valuesOfType.some(v => val.includes(v))
            indeterminate.value[type] = true
        }
    })
})

const handleCheckType = (type: string) => {
    const itemsOfType = data.value.filter(data => data.type === type)
    if (checkedTypes.value[type]) {
        value.value = [...new Set([...value.value, ...itemsOfType.map(data => data.Name)])]
    } else {
        value.value = value.value.filter(val => !itemsOfType.some(data => data.Name === val))
    }
}

const getIndeterminate = (type: string) => {
    const dataOfType = data.value.filter(data => data.type === type)
    const selectedCount = value.value.filter(val => dataOfType.some(data => data.Name === val)).length
    return selectedCount > 0 && selectedCount < dataOfType.length
}

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

// watch(filteredData, (filteredItems) => {
//     const selectedItems = value.value.filter(val => !filteredItems.some(item => item.Name === val))
//     if (selectedItems.length !== value.value.length) {
//         value.value = selectedItems
//         console.log(value.value)
//     }
// })
</script>

<style lang="scss">
.custom-header {
    .el-checkbox {
        display: flex;
        height: unset;
    }
}
</style>
