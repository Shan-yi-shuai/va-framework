<script setup lang='ts'>
import { storeToRefs } from 'pinia'
import * as d3 from 'd3'
import { watch } from 'vue'
import { useStore } from '../stores/store'

const {
  width,
  height,
} = defineProps({
  width: { default: 1500, type: Number },
  height: { default: 900, type: Number },
})

// acquire pinia store
const store = useStore()
const { vesselTSNE, selectedVesselIDs, selectedLocationIDs, dateInterval, vesselID2Vessel, focusVesselID, vesselTypeColor, vesselID2Name } = storeToRefs(store)

function renderChart(vesselTSNE: [string, [number, number]][]): void {
  const margin = { top: 10, right: 10, bottom: 10, left: 10 }
  const _width = width - margin.left - margin.right
  const _height = height - margin.top - margin.bottom

  // Clear any existing SVG
  d3.select('#tsne').selectAll('*').remove()
  // Set up SVG
  const svg = d3.select('#tsne')
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  const radius = 3

  // Set up scales
  const xScale = d3.scaleLinear()
    .domain(d3.extent(vesselTSNE, (d: [string, [number, number]]) => d[1][0]) as [number, number])
    .range([radius, _width - radius])

  const yScale = d3.scaleLinear()
    .domain(d3.extent(vesselTSNE, (d: [string, [number, number]]) => d[1][1]) as [number, number])
    .range([_height - radius, radius])

  // Brush feature
  const brush = d3.brush()
    .extent([[0, 0], [_width, _height]])
    .on('end', brushed)

  svg.append('g')
    .call(brush)

  function brushed(event: d3.D3BrushEvent<any>) {
    if (!event.selection)
      return
    const [[x0, y0], [x1, y1]] = event.selection
    const selectedVessels = vesselTSNE.filter((d: [string, [number, number]]) =>
      x0 <= xScale(d[1][0]) && xScale(d[1][0]) <= x1
      && y0 <= yScale(d[1][1]) && yScale(d[1][1]) <= y1).map((d: [string, [number, number]]) => d[0])

    store.selectedVesselIDs = selectedVessels
  }

  const tooltip = d3.select('body')
    .append('div')
    .style('position', 'absolute')
    .style('background', '#fff')
    .style('border', '1px solid #000')
    .style('padding', '5px')
    .style('display', 'none')
    .style('pointer-events', 'none')

  // Draw points
  svg.selectAll('circle')
    .data(vesselTSNE)
    .enter()
    .append('circle')
    .attr('cx', (d: [string, [number, number]]) => xScale(d[1][0]))
    .attr('cy', (d: [string, [number, number]]) => yScale(d[1][1]))
    .attr('r', (d: [string, [number, number]]) => {
      if (d[0] === 'snappersnatcher7be' || d[0] === 'roachrobberdb6' || d[0] === focusVesselID.value)
        return radius + 2
      else
        return radius
    })
    .attr('fill', (d: [string, [number, number]]) => vesselTypeColor.value(vesselID2Vessel.value[d[0]].type))
    .attr('stroke', (d: [string, [number, number]]) => {
      if (d[0] === 'snappersnatcher7be' || d[0] === 'roachrobberdb6')
        return 'orange'
      else if (d[0] === focusVesselID.value)
        return 'black'
      else
        return selectedVesselIDs.value.includes(d[0]) ? 'black' : 'none'
    })
    .attr('stroke-width', (d: [string, [number, number]]) => {
      if (d[0] === 'snappersnatcher7be' || d[0] === 'roachrobberdb6' || d[0] === focusVesselID.value)
        return 3
      return 2
    })
    .on('mouseover', (event: d3.D3BrushEvent<any>, d: [string, [number, number]]) => {
      tooltip.style('display', 'block')
        .html(`Vessel: ${vesselID2Name.value[d[0]]}<br>Vessel Type: ${vesselID2Vessel.value[d[0]].type}<br>Vessel Tonnage: ${vesselID2Vessel.value[d[0]].tonnage}`)
      d3.select(event.currentTarget).classed('box', true)
      if (d[0] === 'snappersnatcher7be' || d[0] === 'roachrobberdb6')
        d3.select(event.currentTarget).attr('r', radius + 4)
      else
        d3.select(event.currentTarget).attr('r', radius + 2)
    })
    .on('mousemove', (event: d3.D3BrushEvent<any>) => {
      const [svgX, svgY] = d3.pointer(event)
      const svgBounds = svg.node().getBoundingClientRect()
      const left = svgX + svgBounds.left + 10
      const top = svgY + svgBounds.top + 10

      // Adjust to keep the tooltip within SVG bounds
      // const tooltipWidth = tooltip.node().offsetWidth
      // const tooltipHeight = tooltip.node().offsetHeight
      // let left = svgX + svgBounds.left + 10
      // let top = svgY + svgBounds.top + 10
      // if (left + tooltipWidth > svgBounds.right)
      //   left = left - tooltipWidth - 20
      // if (top + tooltipHeight > svgBounds.bottom)
      //   top = top - tooltipHeight - 20

      tooltip.style('left', `${left}px`)
        .style('top', `${top}px`)
    })
    .on('mouseout', (event: d3.D3BrushEvent<any>, d: [string, [number, number]]) => {
      tooltip.style('display', 'none')
      d3.select(event.currentTarget).classed('box', false)
      if (d[0] === 'snappersnatcher7be' || d[0] === 'roachrobberdb6' || d[0] === focusVesselID.value)
        d3.select(event.currentTarget).attr('r', radius + 2)
      else
        d3.select(event.currentTarget).attr('r', radius)
    })
    .on('click', (event: d3.D3BrushEvent<any>, d: [string, [number, number]]) => {
      focusVesselID.value = d[0]
      tooltip.style('display', 'none')
      d3.select(event.currentTarget).classed('box', false)
    })
}

watch([vesselTSNE, selectedVesselIDs, focusVesselID], ([newVesselTSNE, newSelectedVesselIDs, newFocusVesselID]) => {
  if (newVesselTSNE.length > 0 && newSelectedVesselIDs.length > 0 && newFocusVesselID)
    renderChart(newVesselTSNE)
}, { immediate: true })

watch([selectedLocationIDs, dateInterval], ([newSelectedLocationIDs, newDateInterval]) => {
  if (newSelectedLocationIDs.length > 0
    && d3.timeParse('%Y-%m-%d')('2035-2-1') <= d3.timeParse('%Y-%m-%d')(newDateInterval[0])
    && d3.timeParse('%Y-%m-%d')(newDateInterval[1]) <= d3.timeParse('%Y-%m-%d')('2035-12-31')
  )
    store.getVesselTSNE()
}, { immediate: true })
</script>

<template>
  <div id="tsne" />
</template>
