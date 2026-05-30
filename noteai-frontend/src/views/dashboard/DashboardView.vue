<template>
  <div class="dashboard">
    <!-- Sidebar -->
    <aside class="sidebar">
      <!-- Logo -->
      <div class="sidebar-logo">
        <span class="logo-icon">✦</span>
        <span class="logo-text">NoteAI</span>
      </div>

      <!-- New Note Button -->
      <button class="btn btn-primary new-note-btn" @click="handleNewNote" :disabled="notesStore.loading">
        <span>+</span> New Note
      </button>

      <!-- Search -->
      <div class="search-wrap">
        <span class="search-icon">🔍</span>
        <input
          v-model="notesStore.searchQuery"
          type="text"
          class="input search-input"
          placeholder="Search notes..."
        />
      </div>

      <!-- Tags filter -->
      <div v-if="notesStore.allTags.length" class="tags-section">
        <p class="section-label">Tags</p>
        <div class="tag-list">
          <button
            class="tag"
            :class="{ 'tag-active': notesStore.activeTag === '' }"
            @click="notesStore.activeTag = ''"
          >
            All
          </button>
          <button
            v-for="tag in notesStore.allTags"
            :key="tag"
            class="tag tag-ai"
            :class="{ 'tag-active': notesStore.activeTag === tag }"
            @click="notesStore.activeTag = tag"
          >
            # {{ tag }}
          </button>
        </div>
      </div>

      <!-- Notes list -->
      <div class="notes-list">
        <p class="section-label">Notes ({{ notesStore.filtered.length }})</p>
        <div v-if="notesStore.loading" class="loading-state">
          <div class="spinner"></div>
        </div>
        <div v-else-if="!notesStore.filtered.length" class="empty-state">
          <p>No notes yet.</p>
          <span>Click "New Note" to start</span>
        </div>
        <button
          v-for="note in notesStore.filtered"
          :key="note._id"
          class="note-item"
          :class="{ 'note-active': notesStore.activeNote?._id === note._id }"
          @click="notesStore.setActive(note)"
        >
          <div class="note-item-title">{{ note.title || 'Untitled' }}</div>
          <div class="note-item-preview">{{ getPreview(note.content) }}</div>
          <div class="note-item-meta">
            <span>{{ formatDate(note.updated_at) }}</span>
            <span v-if="note.tags?.length" class="note-tag-count">{{ note.tags.length }} tags</span>
          </div>
        </button>
      </div>

      <!-- User section -->
      <div class="sidebar-footer">
        <div class="user-pill">
          <div class="user-avatar">{{ authStore.initials }}</div>
          <div class="user-info">
            <p class="user-name">{{ authStore.user?.name }}</p>
            <p class="user-email">{{ authStore.user?.email }}</p>
          </div>
        </div>
        <button class="btn btn-ghost btn-sm logout-btn" @click="authStore.logout">Logout</button>
      </div>
    </aside>

    <!-- Editor -->
    <main class="editor-area">
      <div v-if="!notesStore.activeNote" class="editor-empty fade-in">
        <div class="empty-icon">✦</div>
        <h2>Select a note to edit</h2>
        <p>Or create a new one to get started</p>
        <button class="btn btn-primary" @click="handleNewNote">+ New Note</button>
      </div>

      <div v-else class="editor-content fade-in" :key="notesStore.activeNote._id">
        <!-- Editor toolbar -->
        <div class="editor-toolbar">
          <input
            v-model="localTitle"
            class="title-input"
            placeholder="Untitled"
            @input="debouncedSave"
          />
          <div class="toolbar-actions">
            <!-- AI Summarize -->
            <button
              class="btn btn-ai btn-sm"
              :disabled="notesStore.aiLoading || !localContent.trim()"
              @click="handleSummarize"
            >
              <span v-if="notesStore.aiLoading" class="spinner" style="width:14px;height:14px;"></span>
              <span>✦ Summarize</span>
            </button>
            <!-- AI Auto Tag -->
            <button
              class="btn btn-ai btn-sm"
              :disabled="notesStore.aiLoading || !localContent.trim()"
              @click="handleAutoTag"
            >
              <span>🏷️ Auto Tag</span>
            </button>
            <!-- Delete -->
            <button class="btn btn-ghost btn-sm danger-btn" @click="handleDelete">
              🗑️
            </button>
          </div>
        </div>

        <!-- Tags row -->
        <div class="tags-row" v-if="notesStore.activeNote.tags?.length">
          <span v-for="tag in notesStore.activeNote.tags" :key="tag" class="tag tag-ai">
            # {{ tag }}
          </span>
        </div>

        <!-- AI Summary box -->
        <div v-if="notesStore.activeNote.summary" class="summary-box fade-in">
          <div class="summary-header">
            <span class="summary-label">✦ AI Summary</span>
          </div>
          <p class="summary-text">{{ notesStore.activeNote.summary }}</p>
        </div>

        <!-- Markdown textarea -->
        <div class="editor-body">
          <textarea
            v-model="localContent"
            class="note-textarea"
            placeholder="Start writing in Markdown..."
            @input="debouncedSave"
          ></textarea>

          <!-- Preview toggle -->
          <div v-if="showPreview" class="markdown-preview" v-html="renderedMarkdown"></div>
        </div>

        <!-- Footer bar -->
        <div class="editor-footer">
          <span class="word-count">{{ wordCount }} words</span>
          <button class="preview-toggle" @click="showPreview = !showPreview">
            {{ showPreview ? 'Hide Preview' : 'Show Preview' }}
          </button>
          <span class="save-status" :class="{ saving: isSaving }">
            {{ isSaving ? 'Saving...' : 'Saved ✓' }}
          </span>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, watch, inject } from 'vue'
import { marked } from 'marked'
import { useAuthStore }  from '@/stores/auth'
import { useNotesStore } from '@/stores/notes'

const authStore  = useAuthStore()
const notesStore = useNotesStore()
const toast      = inject('toast')

const localTitle   = ref('')
const localContent = ref('')
const showPreview  = ref(false)
const isSaving     = ref(false)
let   saveTimer    = null

// ── Sync active note → local state ──
watch(() => notesStore.activeNote, (note) => {
  if (!note) return
  localTitle.value   = note.title   || ''
  localContent.value = note.content || ''
}, { immediate: true })

// ── Debounced auto-save ──
function debouncedSave() {
  clearTimeout(saveTimer)
  saveTimer = setTimeout(saveNote, 800)
}

async function saveNote() {
  if (!notesStore.activeNote) return
  isSaving.value = true
  try {
    await notesStore.updateNote(notesStore.activeNote._id, {
      title: localTitle.value,
      content: localContent.value
    })
  } finally {
    isSaving.value = false
  }
}

// ── New note ──
async function handleNewNote() {
  const note = await notesStore.createNote()
  localTitle.value   = ''
  localContent.value = ''
}

// ── AI Summarize ──
async function handleSummarize() {
  await saveNote()
  try {
    await notesStore.summarizeNote(notesStore.activeNote._id)
    toast('Summary generated!', 'success')
  } catch {
    toast('Summarization failed', 'error')
  }
}

// ── AI Auto Tag ──
async function handleAutoTag() {
  await saveNote()
  try {
    const tags = await notesStore.autoTagNote(notesStore.activeNote._id)
    toast(`Tagged: ${tags.join(', ')}`, 'success')
  } catch {
    toast('Auto-tagging failed', 'error')
  }
}

// ── Delete ──
async function handleDelete() {
  if (!confirm('Delete this note?')) return
  await notesStore.deleteNote(notesStore.activeNote._id)
  toast('Note deleted', 'info')
}

// ── Computed ──
const renderedMarkdown = computed(() => marked(localContent.value || ''))
const wordCount = computed(() => {
  if (!localContent.value.trim()) return 0
  return localContent.value.trim().split(/\s+/).length
})

function getPreview(content) {
  return content?.replace(/[#*`]/g, '').slice(0, 60) || 'Empty note'
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })
}

// ── Fetch notes on mount ──
notesStore.fetchNotes()
</script>

<style scoped>
.dashboard {
  display: flex;
  height: 100vh;
  overflow: hidden;
  background: var(--bg);
}

/* ── Sidebar ── */
.sidebar {
  width: 280px;
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  background: var(--bg-card);
  flex-shrink: 0;
  overflow: hidden;
}

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 20px 20px 0;
  margin-bottom: 16px;
}

.logo-icon {
  font-size: 18px;
  color: var(--accent);
  filter: drop-shadow(0 0 8px var(--accent));
}

.logo-text {
  font-family: var(--font-display);
  font-size: 18px;
  color: var(--text-primary);
}

.new-note-btn {
  margin: 0 16px 16px;
  justify-content: center;
  font-size: 14px;
}

.search-wrap {
  position: relative;
  margin: 0 16px 16px;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 13px;
  pointer-events: none;
}

.search-input {
  padding-left: 36px;
  font-size: 13px;
  height: 36px;
}

.tags-section {
  padding: 0 16px 12px;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}

.tag-active {
  background: var(--accent-soft) !important;
  color: var(--accent) !important;
  border-color: rgba(91,91,214,0.3) !important;
}

.section-label {
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: var(--text-muted);
  padding: 0 16px 8px;
}

.notes-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 8px;
}

.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 32px 16px;
  color: var(--text-muted);
  font-size: 13px;
  text-align: center;
}

.note-item {
  width: 100%;
  padding: 12px 12px;
  border-radius: var(--radius-md);
  text-align: left;
  margin-bottom: 2px;
  transition: background 0.15s;
  cursor: pointer;
  border: 1px solid transparent;
}

.note-item:hover {
  background: var(--bg-hover);
}

.note-active {
  background: var(--accent-soft) !important;
  border-color: rgba(91,91,214,0.2) !important;
}

.note-item-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 3px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.note-item-preview {
  font-size: 12px;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 4px;
}

.note-item-meta {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: var(--text-muted);
  font-family: var(--font-mono);
}

.note-tag-count {
  color: var(--ai);
}

/* Sidebar footer */
.sidebar-footer {
  border-top: 1px solid var(--border);
  padding: 14px 16px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-pill {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  min-width: 0;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--accent);
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.user-info {
  min-width: 0;
}

.user-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-email {
  font-size: 11px;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.logout-btn {
  flex-shrink: 0;
  font-size: 12px;
  padding: 5px 10px;
}

/* ── Editor Area ── */
.editor-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--bg);
}

.editor-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: var(--text-muted);
  text-align: center;
  padding: 40px;
}

.empty-icon {
  font-size: 36px;
  color: var(--accent);
  filter: drop-shadow(0 0 16px var(--accent));
  opacity: 0.5;
  margin-bottom: 8px;
}

.editor-empty h2 {
  font-family: var(--font-display);
  font-size: 24px;
  color: var(--text-secondary);
}

.editor-empty p {
  font-size: 14px;
}

.editor-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

/* Toolbar */
.editor-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 24px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.title-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  font-family: var(--font-display);
  font-size: 22px;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.title-input::placeholder {
  color: var(--text-muted);
}

.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.danger-btn {
  color: var(--danger) !important;
  border-color: rgba(224,92,92,0.2) !important;
}
.danger-btn:hover {
  background: var(--danger-soft) !important;
}

/* Tags row */
.tags-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  padding: 10px 24px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

/* Summary box */
.summary-box {
  margin: 16px 24px 0;
  padding: 14px 16px;
  background: var(--ai-soft);
  border: 1px solid rgba(0,201,167,0.15);
  border-radius: var(--radius-md);
  flex-shrink: 0;
}

.summary-header {
  margin-bottom: 8px;
}

.summary-label {
  font-size: 12px;
  font-weight: 500;
  color: var(--ai);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.summary-text {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.7;
}

/* Editor body */
.editor-body {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.note-textarea {
  flex: 1;
  padding: 20px 24px;
  background: transparent;
  border: none;
  outline: none;
  color: var(--text-primary);
  font-family: var(--font-mono);
  font-size: 14px;
  line-height: 1.8;
  resize: none;
  overflow-y: auto;
}

.note-textarea::placeholder {
  color: var(--text-muted);
}

.markdown-preview {
  flex: 1;
  padding: 20px 24px;
  overflow-y: auto;
  border-left: 1px solid var(--border);
  font-size: 14px;
  line-height: 1.8;
  color: var(--text-secondary);
}

/* Editor footer */
.editor-footer {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 10px 24px;
  border-top: 1px solid var(--border);
  font-size: 12px;
  color: var(--text-muted);
  flex-shrink: 0;
  font-family: var(--font-mono);
}

.preview-toggle {
  color: var(--accent);
  font-size: 12px;
  cursor: pointer;
  background: none;
  border: none;
  font-family: var(--font-mono);
  transition: opacity 0.15s;
}

.save-status {
  margin-left: auto;
  color: var(--success);
}

.save-status.saving {
  color: var(--text-muted);
}

@media (max-width: 768px) {
  .sidebar { width: 220px; }
}
</style>
