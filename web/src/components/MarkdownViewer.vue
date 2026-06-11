<template>
  <div class="markdown-body" v-html="renderedHtml"></div>
</template>

<script setup>
import { computed } from 'vue'
import { marked } from 'marked'

const props = defineProps({
  content: { type: String, default: '' },
})

const renderedHtml = computed(() => {
  if (!props.content) return '<p class="empty">暂无内容</p>'
  return marked(props.content, {
    breaks: true,
    gfm: true,
  })
})
</script>

<style>
.markdown-body {
  font-size: 15px;
  line-height: 1.8;
  color: #333;
  overflow-x: hidden;
}
.markdown-body h1 { font-size: 22px; font-weight: 700; margin: 20px 0 12px; padding-bottom: 8px; border-bottom: 2px solid #1a73e8; }
.markdown-body h2 { font-size: 19px; font-weight: 600; margin: 24px 0 10px; color: #1a73e8; }
.markdown-body h3 { font-size: 17px; font-weight: 600; margin: 18px 0 8px; }
.markdown-body h4 { font-size: 15px; font-weight: 500; margin: 14px 0 6px; }
.markdown-body p { margin: 8px 0; }
.markdown-body ul, .markdown-body ol { padding-left: 24px; margin: 8px 0; }
.markdown-body li { margin: 4px 0; }
.markdown-body code {
  font-family: 'Consolas', 'Courier New', monospace;
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 13px;
  color: #d63384;
}
.markdown-body pre {
  background: #282c34;
  color: #abb2bf;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 12px 0;
}
.markdown-body pre code { background: transparent; color: inherit; padding: 0; }
.markdown-body blockquote {
  border-left: 4px solid #1a73e8;
  padding: 6px 16px;
  margin: 12px 0;
  background: #f8f9ff;
  color: #555;
}
.markdown-body table {
  width: 100%;
  border-collapse: collapse;
  margin: 12px 0;
  font-size: 14px;
}
.markdown-body th, .markdown-body td {
  border: 1px solid #ddd;
  padding: 8px 10px;
  text-align: left;
}
.markdown-body th { background: #f0f4ff; font-weight: 600; }
.markdown-body tr:nth-child(even) { background: #fafafa; }
.markdown-body strong { color: #1a1a1a; }
.markdown-body .empty { color: #999; text-align: center; padding: 40px 0; }
</style>
