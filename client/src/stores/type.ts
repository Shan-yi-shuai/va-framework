export interface Vessel {
  id: string
  Name: string
  type: string
}

export interface Location {
  id: string
  Name: string
  type: string
  kind: string
  Activities: string[]
  Description: string
}

export interface Commodity {
  id: string
  name: string
  type: string
}

export interface VesselMovement {
  vessel_id: string
  location_id: string
  start_time: string | Date
  end_time: string | Date
}
