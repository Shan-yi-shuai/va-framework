<script setup lang='ts'>
import { storeToRefs } from 'pinia'
import * as d3 from 'd3'
import { watch } from 'vue'
import { useStore } from '../stores/store'
import type { VesselMovement } from '~/stores/type'

const {
  width,
  height,
} = defineProps({
  width: { default: 1500, type: Number },
  height: { default: 900, type: Number },
})

// acquire pinia store
const store = useStore()
const { vesselMovements, selectedVesselIDs, selectedLocationIDs, selectedCommodityIDs, dateInterval, vesselID2Vessel, focusVesselID, vesselTypeColor, locationColor, vesselID2Name, locationID2Name } = storeToRefs(store)

function renderChart(vesselMovements: any, focusVesselID: any, selectedVesselIDs: any, dateInterval: any): void {
  const vesselMovementsCopy = JSON.parse(JSON.stringify(vesselMovements))

  const parseDate = d3.timeParse('%Y-%m-%dT%H:%M:%S')

  vesselMovementsCopy.forEach((d: VesselMovement) => {
    d.start_time = parseDate(d.start_time)
    d.end_time = parseDate(d.end_time)
  })

  const vesselIDTypes: { vessel_id: string; vessel_type: string }[] = []

  for (const key of selectedVesselIDs) {
    const vessel = vesselID2Vessel.value[key]
    vesselIDTypes.push({ vessel_id: vessel.id, vessel_type: vessel.type })
  }

  // 按类型对数据进行分组
  const grouped_data = d3.group(vesselIDTypes, (d: { vessel_id: string; vessel_type: string }) => d.vessel_type)

  // 将分组后的数据平铺为一个数组
  const sorted_vessel_data: any[] = []
  grouped_data.forEach((group: any) => {
    sorted_vessel_data.push(...group)
  })

  // const index = sorted_vessel_data.findIndex(item => item.vessel_id === focusVesselID)

  // // 如果值不存在于列表中，直接返回原列表
  // if (index !== -1) {
  //   const [item] = sorted_vessel_data.splice(index, 1)
  //   sorted_vessel_data.unshift(item)
  // }

  const margin = { top: 10, right: 10, bottom: 10, left: 20 }
  const _width = width - margin.left - margin.right
  const _height = height - margin.top - margin.bottom

  d3.select('#vessel_movements').selectAll('*').remove()
  const svg = d3.select('#vessel_movements')
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  // 设置时间轴范围
  const x = d3.scaleTime()
    .domain(dateInterval.map((d: string) => d3.timeParse('%Y-%m-%d')(d)) as [Date, Date])
    .range([0, _width - 40])

  const yVessel = d3.scaleBand()
    .domain(sorted_vessel_data.map((d: { vessel_id: string; vessel_type: string }) => d.vessel_id))
    .range([0, _height - 10])
    .padding(0.1)

  // 绘制时间轴
  svg.append('g')
    .attr('transform', `translate(0,${_height - 10})`)
    .call(d3.axisBottom(x).tickFormat(d3.timeFormat('%Y-%m-%d')))
    .selectAll('text') // 选择所有文本标签
    .style('font-size', '6px') // 设置字体大小为10px

  // 绘制y轴并根据vessel_type设置文本颜色
  const yAxis = svg.append('g')
    .call(d3.axisLeft(yVessel))

  yAxis.selectAll('text')
    .style('fill', (d: string) => {
      const vessel = sorted_vessel_data.find(v => v.vessel_id === d)
      return vessel ? vesselTypeColor.value(vessel.vessel_type) : 'black'
    })
    .text((d: string) => vesselID2Name.value[d] || d)
    .attr('font-size', 3)

  // Tooltip div
  const tooltip = d3.select('body')
    .append('div')
    .style('position', 'absolute')
    .style('background', '#fff')
    .style('border', '1px solid #000')
    .style('padding', '5px')
    .style('display', 'none')
    .style('pointer-events', 'none')

  const focusVesselIndex = sorted_vessel_data.findIndex(d => d.vessel_id === focusVesselID)
  if (focusVesselIndex !== -1) {
    svg.append('rect')
      .attr('x', 0)
      .attr('y', yVessel(sorted_vessel_data[focusVesselIndex].vessel_id))
      .attr('width', _width - 40)
      .attr('height', yVessel.bandwidth())
      .attr('fill', 'none')
      .attr('stroke', 'black')
      .attr('stroke-width', 0.5)
  }

  svg.selectAll('.vessel')
    .data(vesselMovementsCopy)
    .enter().append('rect')
    .attr('class', 'bar vessel')
    .attr('x', (d: VesselMovement) => x(d.start_time as Date))
    .attr('y', (d: VesselMovement) => yVessel(d.vessel_id) as number)
    .attr('width', (d: VesselMovement) => x(d.end_time as Date) - x(d.start_time as Date)) // 占至少一天的长度
    .attr('height', yVessel.bandwidth())
    .attr('fill', (d: VesselMovement) => locationColor.value(d.location_id))
    .attr('stroke', 'none')
    .on('mouseover', (event: d3.D3BrushEvent<any>, d: VesselMovement) => {
      tooltip.style('display', 'block')
        .html(`Vessel: ${vesselID2Name.value[d.vessel_id]}<br>Start time: ${d3.timeFormat('%Y-%m-%d')(d.start_time as Date)}<br>End time: ${d3.timeFormat('%Y-%m-%d')(d.end_time as Date)}<br>Location: ${locationID2Name.value[d.location_id]}`)
      d3.select(event.currentTarget).classed('box', true)
    })
    .on('mousemove', (event: d3.D3BrushEvent<any>) => {
      const [svgX, svgY] = d3.pointer(event)
      const tooltipWidth = tooltip.node().offsetWidth
      const tooltipHeight = tooltip.node().offsetHeight
      const svgBounds = svg.node().getBoundingClientRect()
      let left = svgX + svgBounds.left + 10
      let top = svgY + svgBounds.top + 10

      // Adjust to keep the tooltip within SVG bounds
      if (left + tooltipWidth > svgBounds.right)
        left = left - tooltipWidth - 20
      if (top + tooltipHeight > svgBounds.bottom)
        top = top - tooltipHeight - 20

      tooltip.style('left', `${left}px`)
        .style('top', `${top}px`)
    })
    .on('mouseout', (event: d3.D3BrushEvent<any>) => {
      tooltip.style('display', 'none')
      d3.select(event.currentTarget).classed('box', false)
    })

  // Brush for vessels
  const brushVessel = d3.brushY()
    .extent([[-10, 0], [10, _height]])
    .on('end', (event: any) => {
      if (!event.selection)
        return
      const selected = yVessel.domain().filter((d: string) => {
        const pos = yVessel(d) + yVessel.bandwidth() / 2
        return event.selection[0] <= pos && pos <= event.selection[1]
      })
      store.selectedVesselIDs = selected
    })

  // Brush for x-axis
  const brushX = d3.brushX()
    .extent([[0, _height], [_width, _height + 10]])
    .on('end', (event: any) => {
      if (!event.selection)
        return
      const [start, end] = event.selection.map(x.invert)
      store.dateInterval = [d3.timeFormat('%Y-%m-%d')(start), d3.timeFormat('%Y-%m-%d')(end)]
    })

  svg.append('g')
    .attr('class', 'brushVessel')
    .call(brushVessel)

  svg.append('g')
    .attr('class', 'brushX')
    .call(brushX)
}

watch([vesselMovements, focusVesselID, selectedVesselIDs, selectedLocationIDs, selectedCommodityIDs, dateInterval], ([newVesselMovements, newFocusVesselID, newSelectedVesselIDs, newSelectedLocationIDs, newSelectedCommodityIDs, newDateInterval]) => {
  if (newVesselMovements.length > 0
    && newSelectedVesselIDs.length > 0
    && newSelectedLocationIDs.length > 0
    && newSelectedCommodityIDs.length > 0
    && d3.timeParse('%Y-%m-%d')('2035-2-1') <= d3.timeParse('%Y-%m-%d')(newDateInterval[0])
    && d3.timeParse('%Y-%m-%d')(newDateInterval[1]) <= d3.timeParse('%Y-%m-%d')('2035-12-31')
  )
    renderChart(newVesselMovements, newFocusVesselID, newSelectedVesselIDs, newDateInterval)
}, { immediate: true })
</script>

<template>
  <div id="vessel_movements" />
</template>
