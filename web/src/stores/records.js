// stores/records.js — Pinia store for study records state
import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../utils/api'

export const useRecordsStore = defineStore('records', () => {
  const records = ref([])
  const total = ref(0)
  const loading = ref(false)

  async function fetchRecords(page = 1, pageSize = 20) {
    loading.value = true
    try {
      const { data } = await api.get('/records', { params: { page, page_size: pageSize } })
      records.value = data.items || []
      total.value = data.total
    } catch (e) {
      console.error('Fetch records error:', e)
    } finally {
      loading.value = false
    }
  }

  async function getRecord(id) {
    const { data } = await api.get(`/records/${id}`)
    return data
  }

  return { records, total, loading, fetchRecords, getRecord }
})
