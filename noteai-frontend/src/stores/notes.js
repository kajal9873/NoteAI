// src/stores/notes.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { notesAPI } from '@/services/api'

export const useNotesStore = defineStore('notes', () => {
  const notes       = ref([])
  const activeNote  = ref(null)
  const loading     = ref(false)
  const aiLoading   = ref(false)
  const searchQuery = ref('')
  const activeTag   = ref('')

  // ── Filtered notes ──
  const filtered = computed(() => {
    return notes.value.filter(n => {
      const matchSearch = !searchQuery.value ||
        n.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
        n.content.toLowerCase().includes(searchQuery.value.toLowerCase())
      const matchTag = !activeTag.value || n.tags?.includes(activeTag.value)
      return matchSearch && matchTag
    })
  })

  // ── All unique tags ──
  const allTags = computed(() => {
    const tagSet = new Set()
    notes.value.forEach(n => n.tags?.forEach(t => tagSet.add(t)))
    return [...tagSet]
  })

  // ── Fetch all notes ──
  async function fetchNotes() {
    loading.value = true
    try {
      const { data } = await notesAPI.getAll()
      notes.value = data
    } finally {
      loading.value = false
    }
  }

  // ── Create note ──
  async function createNote() {
    const { data } = await notesAPI.create({
      title: 'Untitled',
      content: '',
      tags: []
    })
    notes.value.unshift(data)
    activeNote.value = data
    return data
  }

  // ── Update note (debounced from component) ──
  async function updateNote(id, payload) {
    const { data } = await notesAPI.update(id, payload)
    const idx = notes.value.findIndex(n => n._id === id)
    if (idx !== -1) notes.value[idx] = data
    if (activeNote.value?._id === id) activeNote.value = data
    return data
  }

  // ── Delete note ──
  async function deleteNote(id) {
    await notesAPI.delete(id)
    notes.value = notes.value.filter(n => n._id !== id)
    if (activeNote.value?._id === id) activeNote.value = null
  }

  // ── AI: Summarize ──
  async function summarizeNote(id) {
    aiLoading.value = true
    try {
      const { data } = await notesAPI.summarize(id)
      const idx = notes.value.findIndex(n => n._id === id)
      if (idx !== -1) notes.value[idx] = data
      if (activeNote.value?._id === id) activeNote.value = data
      return data.summary
    } finally {
      aiLoading.value = false
    }
  }

  // ── AI: Auto Tag ──
  async function autoTagNote(id) {
    aiLoading.value = true
    try {
      const { data } = await notesAPI.autoTag(id)
      const idx = notes.value.findIndex(n => n._id === id)
      if (idx !== -1) notes.value[idx] = data
      if (activeNote.value?._id === id) activeNote.value = data
      return data.tags
    } finally {
      aiLoading.value = false
    }
  }

  function setActive(note) { activeNote.value = note }

  return {
    notes, activeNote, loading, aiLoading,
    searchQuery, activeTag, filtered, allTags,
    fetchNotes, createNote, updateNote, deleteNote,
    summarizeNote, autoTagNote, setActive
  }
})
