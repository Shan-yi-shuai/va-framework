/**
 * This pinia store demonstrate a way to load dynamic json resources from server.
 **/

import { defineStore } from 'pinia'
import axios from 'axios'

const DATA_SERVER_URL = 'http://127.0.0.1:5000'

/**
 * The exampleData in client is a copy of the server,
 * we update the copy via the get method and modify the ontology via the post method
 */

export const useExampleStore = defineStore({
  id: 'example',
  state: () => {
    return {
      exampleData: [],
    }
  },
  getters: {
    exampleDataLength(): number {
      return this.exampleData.length
    },
  },
  actions: {
    // generic HTTP GET request
    get(api: string, callback: Function) {
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
    post(api: string, param: object, callback: Function) {
      axios.post(`${DATA_SERVER_URL}/${api}`, param).then(
        (response) => {
          callback(response.data)
        },
        (errResponse) => {
          console.error(errResponse)
        },
      )
    },
    // the async and await version if you do not use generic requests
    async get_example_data_async() {
      try {
        const response = await axios.get(`${DATA_SERVER_URL}/get_example_data`)
        this.exampleData = response.data
      }
      catch (error) {
        console.error(error)
        // display a user-friendly error message on the UI
      }
    },
    get_example_data() {
      this.get('get_example_data', (data: []) => {
        this.exampleData = data
      })
    },
    modify_example_data() {
      this.post('modify_example_data', { example: 100 }, (data: []) => {
        this.exampleData = data
      })
    },
  },
})
