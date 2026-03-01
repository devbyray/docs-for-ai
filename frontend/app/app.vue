<template>
  <main class="container">
    <h1>MarkItDown</h1>
    <div class="header-row">
      <p class="subtitle">Convert files to Markdown instantly</p>
      <a href="/docs" target="_blank" rel="noopener" class="api-docs-link">
        📖 API Docs
      </a>
    </div>

    <div class="card">
      <!-- Upload zone -->
      <div
        class="dropzone"
        :class="{ 'dropzone--over': dragging, 'dropzone--filled': file }"
        @dragover.prevent="dragging = true"
        @dragleave.prevent="dragging = false"
        @drop.prevent="onDrop"
        @click="fileInput?.click()"
      >
        <input ref="fileInput" type="file" hidden @change="onFileChange" />
        <template v-if="file">
          <span class="file-icon">📄</span>
          <span class="file-name">{{ file.name }}</span>
          <span class="file-size">{{ formatSize(file.size) }}</span>
        </template>
        <template v-else>
          <span class="upload-icon">⬆️</span>
          <span>Click or drag &amp; drop a file here</span>
          <span class="hint">PDF, DOCX, PPTX, XLSX, HTML, images, audio…</span>
        </template>
      </div>

      <!-- Actions -->
      <div class="actions">
        <button class="btn btn--primary" :disabled="!file || loading" @click="convert">
          <span v-if="loading" class="spinner" />
          {{ loading ? 'Converting…' : 'Convert to Markdown' }}
        </button>
        <button v-if="file || markdown" class="btn btn--ghost" @click="reset">
          Clear
        </button>
      </div>

      <!-- Error -->
      <p v-if="error" class="error">{{ error }}</p>

      <!-- Output -->
      <template v-if="markdown">
        <div class="output-header">
          <label for="markdown-output">Markdown output</label>
          <button class="btn btn--ghost btn--small" @click="copy">
            {{ copied ? '✅ Copied!' : '📋 Copy' }}
          </button>
        </div>
        <textarea
          id="markdown-output"
          v-model="markdown"
          class="output"
          spellcheck="false"
          readonly
        />
      </template>
    </div>
  </main>
</template>

<script setup lang="ts">
const fileInput = ref<HTMLInputElement | null>(null)
const file = ref<File | null>(null)
const markdown = ref('')
const loading = ref(false)
const error = ref('')
const dragging = ref(false)
const copied = ref(false)

function onFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  if (input.files?.[0]) setFile(input.files[0])
}

function onDrop(e: DragEvent) {
  dragging.value = false
  if (e.dataTransfer?.files?.[0]) setFile(e.dataTransfer.files[0])
}

function setFile(f: File) {
  file.value = f
  markdown.value = ''
  error.value = ''
}

function formatSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

async function convert() {
  if (!file.value) return
  loading.value = true
  error.value = ''
  markdown.value = ''
  try {
    const form = new FormData()
    form.append('file', file.value)
    const res = await $fetch<{ markdown: string }>('/v1/convert', {
      method: 'POST',
      body: form,
    })
    markdown.value = res.markdown
  }
  catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err)
    error.value = `Conversion failed: ${msg}`
  }
  finally {
    loading.value = false
  }
}

async function copy() {
  await navigator.clipboard.writeText(markdown.value)
  copied.value = true
  setTimeout(() => (copied.value = false), 2000)
}

function reset() {
  file.value = null
  markdown.value = ''
  error.value = ''
  if (fileInput.value) fileInput.value.value = ''
}
</script>

<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: system-ui, -apple-system, sans-serif;
  background: #0f0f12;
  color: #e8e8f0;
  min-height: 100vh;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 2rem 1rem;
}

.container {
  width: 100%;
  max-width: 760px;
}

h1 {
  font-size: 2rem;
  font-weight: 700;
  letter-spacing: -0.03em;
  background: linear-gradient(135deg, #a78bfa, #60a5fa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  color: #888;
  margin-top: 0.25rem;
}

.header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.api-docs-link {
  font-size: 0.82rem;
  font-weight: 600;
  color: #a78bfa;
  text-decoration: none;
  padding: 0.3rem 0.75rem;
  border: 1px solid #3b2f6e;
  border-radius: 6px;
  transition: background 0.15s;
}
.api-docs-link:hover { background: #1e1829; }

.card {
  background: #18181f;
  border: 1px solid #2a2a35;
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.dropzone {
  border: 2px dashed #2a2a35;
  border-radius: 8px;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
  min-height: 130px;
  text-align: center;
  color: #888;
  font-size: 0.9rem;
  user-select: none;
}

.dropzone:hover, .dropzone--over { border-color: #7c3aed; background: #1e1829; }
.dropzone--filled { border-color: #60a5fa; background: #111827; color: #e8e8f0; }

.upload-icon, .file-icon { font-size: 2rem; }
.file-name { font-weight: 600; color: #e8e8f0; word-break: break-all; }
.file-size { color: #888; font-size: 0.8rem; }
.hint { font-size: 0.75rem; color: #555; }

.actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.btn {
  padding: 0.55rem 1.25rem;
  border-radius: 8px;
  border: none;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: opacity 0.15s, background 0.15s;
}

.btn--primary { background: linear-gradient(135deg, #7c3aed, #2563eb); color: #fff; }
.btn--primary:hover:not(:disabled) { opacity: 0.85; }
.btn--primary:disabled { opacity: 0.4; cursor: not-allowed; }
.btn--ghost { background: #2a2a35; color: #ccc; }
.btn--ghost:hover { background: #33333f; }
.btn--small { padding: 0.3rem 0.75rem; font-size: 0.8rem; }

.spinner {
  width: 14px; height: 14px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.error {
  background: #2d1515;
  border: 1px solid #7f1d1d;
  color: #f87171;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 0.85rem;
}

.output-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.85rem;
  color: #888;
}

.output {
  width: 100%;
  min-height: 320px;
  background: #0f0f12;
  border: 1px solid #2a2a35;
  border-radius: 8px;
  padding: 1rem;
  color: #e8e8f0;
  font-family: 'Fira Code', 'Cascadia Code', monospace;
  font-size: 0.82rem;
  line-height: 1.6;
  resize: vertical;
  outline: none;
}
</style>
