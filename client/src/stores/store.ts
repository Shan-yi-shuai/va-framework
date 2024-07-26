/**
 * This pinia store demonstrate a way to load dynamic json resources from server.
 **/

import { defineStore } from 'pinia'
import axios from 'axios'
import * as d3 from 'd3'
import type { Commodity, Location, Vessel, VesselMovement } from '~/stores/type'

// import { get } from 'node_modules/axios/index.cjs'

const DATA_SERVER_URL = 'http://127.0.0.1:5000'

type Callback<T> = (data: T) => void

export const useStore = defineStore({
  id: 'example',
  state: () => ({
    dateInterval: ['2035-02-01', '2035-03-17'],
    vessels: [] as Vessel[],
    locations: [] as Location[],
    commodities: [] as Commodity[],
    selectedVesselIDs: [] as string[],
    selectedLocationIDs: [] as string[],
    selectedCommodityIDs: [] as string[],
    vesselTSNE: [] as [string, [number, number]][],
    vesselMovements: [] as VesselMovement[],
    aggregatedVesselMovements: [] as VesselMovement[],
    focusVesselID: 'snappersnatcher7be',
  }),
  getters: {
    vesselTypeColor(): any {
      return d3.scaleOrdinal(d3.schemeCategory10).domain(this.vesselTypes)
    },
    locationColor(): any {
      return d3.scaleOrdinal(d3.schemeSet3.concat(d3.schemeTableau10, d3.schemePastel1)).domain(this.locationIDs)
    },
    commodityColor(): any {
      return d3.scaleOrdinal(d3.schemeSet1).domain(this.commodityIDs)
    },
    locationIDs(): string[] {
      return [...new Set(this.locations.map((location: Location) => location.id))] as string[]
    },
    vesselIDs(): string[] {
      return [...new Set(this.vessels.map((vessel: Vessel) => vessel.id))] as string[]
    },
    commodityIDs(): string[] {
      return [...new Set(this.commodities.map((commodity: Commodity) => commodity.id))] as string[]
    },
    vesselTypes(): string[] {
      return [...new Set(this.vessels.map((vessel: Vessel) => vessel.type))] as string[]
    },
    locationNames(): string[] {
      return [...new Set(this.locations.map((location: Location) => location.Name))] as string[]
    },
    vesselNames(): string[] {
      return [...new Set(this.vessels.map((vessel: Vessel) => vessel.Name))] as string[]
    },
    commodityNames(): string[] {
      return [...new Set(this.commodities.map((commodity: Commodity) => commodity.name))] as string[]
    },
    vesselName2ID(): { [key: string]: string } {
      const vesselName2ID: { [key: string]: string } = {}
      this.vessels.forEach((vessel: any) => {
        vesselName2ID[vessel.Name] = vessel.id
      })
      return vesselName2ID
    },
    locationName2ID(): { [key: string]: string } {
      const locationName2ID: { [key: string]: string } = {}
      this.locations.forEach((location: any) => {
        locationName2ID[location.Name] = location.id
      })
      return locationName2ID
    },
    commodityName2ID(): { [key: string]: string } {
      const commodityName2ID: { [key: string]: string } = {}
      this.commodities.forEach((commodity: any) => {
        commodityName2ID[commodity.name] = commodity.id
      })
      return commodityName2ID
    },
    vesselID2Vessel(): { [key: string]: any } {
      const vesselID2Vessel: { [key: string]: any } = {}
      this.vessels.forEach((vessel: any) => {
        vesselID2Vessel[vessel.id] = vessel
      })
      return vesselID2Vessel
    },
    locationID2Location(): { [key: string]: any } {
      const locationID2Location: { [key: string]: any } = {}
      this.locations.forEach((location: any) => {
        locationID2Location[location.id] = location
      })
      return locationID2Location
    },
    commodityID2Commodity(): { [key: string]: any } {
      const commodityID2Commodity: { [key: string]: any } = {}
      this.commodities.forEach((commodity: any) => {
        commodityID2Commodity[commodity.id] = commodity
      })
      return commodityID2Commodity
    },
    vesselID2Name(): { [key: string]: string } {
      const vesselID2VesselName: { [key: string]: string } = {}
      this.vessels.forEach((vessel: any) => {
        vesselID2VesselName[vessel.id] = vessel.Name
      })
      return vesselID2VesselName
    },
    locationID2Name(): { [key: string]: string } {
      const locationID2LocationName: { [key: string]: string } = {}
      this.locations.forEach((location: any) => {
        locationID2LocationName[location.id] = location.Name
      })
      return locationID2LocationName
    },
    commodityID2Name(): { [key: string]: string } {
      const commodityID2CommodityName: { [key: string]: string } = {}
      this.commodities.forEach((commodity: any) => {
        commodityID2CommodityName[commodity.id] = commodity.name
      })
      return commodityID2CommodityName
    },
  },
  actions: {
    // generic HTTP GET request
    get(api: string, callback: Callback<any>) {
      axios.get(`${DATA_SERVER_URL}/${api}`).then(
        (response) => {
          callback(response.data)
        },
        (errResponse) => {
          console.error(errResponse)
        },
      )
    },
    // generic HTTP POST request
    post(api: string, param: object, callback: Callback<any>) {
      axios.post(`${DATA_SERVER_URL}/${api}`, param).then(
        (response) => {
          callback(response.data)
        },
        (errResponse) => {
          console.error(errResponse)
        },
      )
    },
    initialize() {
      this.get('get_all_entities', (data: []) => {
        this.vessels = data.filter((node: any) => node.type.includes('Entity.Vessel'))
        this.locations = data.filter((node: any) => node.type.includes('Entity.Location'))
        this.commodities = data.filter((node: any) => node.type.includes('Entity.Commodity'))
        this.selectedVesselIDs = this.vessels.map((node: any) => node.id)
        this.selectedLocationIDs = this.locations.map((node: any) => node.id)
        this.selectedCommodityIDs = this.commodities.map((node: any) => node.id)
        this.getVesselTSNE()
        this.getVesselMovements()
      })
    },
    getVesselTSNE() {
      this.post('get_vessel_tsne', { start_date: this.dateInterval[0], end_date: this.dateInterval[1], vessel_ids: this.vesselIDs, location_ids: this.selectedLocationIDs }, (data: []) => {
        this.vesselTSNE = data
      })
    },
    getVesselMovements() {
      this.post('get_vessel_movements', { start_date: this.dateInterval[0], end_date: this.dateInterval[1], vessel_ids: this.selectedVesselIDs, location_ids: this.selectedLocationIDs }, (data: { vessel_movements: VesselMovement[]; aggregated_vessel_movements: VesselMovement[] }) => {
        this.vesselMovements = data.vessel_movements
        this.aggregatedVesselMovements = data.aggregated_vessel_movements
      })
    },
  },
})
