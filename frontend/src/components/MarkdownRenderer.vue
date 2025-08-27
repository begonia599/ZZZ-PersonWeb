<template>
  <div class="markdown-content" v-html="renderedContent"></div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { marked } from 'marked';
import hljs from 'highlight.js';

const props = defineProps<{
  content: string;
  enableHighlight?: boolean;
}>();

// 配置 marked 和代码高亮
onMounted(() => {
  if (props.enableHighlight !== false) {
    // 配置 marked 使用 highlight.js
    marked.setOptions({
      highlight: function(code, lang) {
        if (lang && hljs.getLanguage(lang)) {
          try {
            return hljs.highlight(code, { language: lang }).value;
          } catch (err) {
            console.warn('Highlight.js error:', err);
          }
        }
        return hljs.highlightAuto(code).value;
      },
      breaks: true, // 支持 GitHub 风格的换行
      gfm: true, // 启用 GitHub 风格的 Markdown
    });
  }
});

// 渲染 Markdown 内容
const renderedContent = computed(() => {
  if (!props.content) return '';
  
  try {
    return marked.parse(props.content);
  } catch (error) {
    console.error('Markdown 解析错误:', error);
    return `<p>Markdown 解析失败: ${error}</p>`;
  }
});
</script>

<style scoped>
.markdown-content {
  line-height: 1.8;
  word-wrap: break-word;
}

/* Markdown 基础样式 */
.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3),
.markdown-content :deep(h4),
.markdown-content :deep(h5),
.markdown-content :deep(h6) {
  color: #fff;
  margin-top: 1.5em;
  margin-bottom: 0.8em;
  font-weight: bold;
}

.markdown-content :deep(h1) {
  font-size: 2.2em;
  border-bottom: 2px solid #333;
  padding-bottom: 0.3em;
}

.markdown-content :deep(h2) {
  font-size: 1.8em;
  border-bottom: 1px solid #333;
  padding-bottom: 0.2em;
}

.markdown-content :deep(h3) {
  font-size: 1.5em;
}

.markdown-content :deep(h4) {
  font-size: 1.3em;
}

.markdown-content :deep(h5) {
  font-size: 1.1em;
}

.markdown-content :deep(h6) {
  font-size: 1em;
  color: #b0b0b0;
}

.markdown-content :deep(p) {
  margin-bottom: 1em;
  color: #e0e0e0;
}

.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  margin-bottom: 1em;
  padding-left: 2em;
  color: #e0e0e0;
}

.markdown-content :deep(li) {
  margin-bottom: 0.3em;
}

.markdown-content :deep(blockquote) {
  border-left: 4px solid #00FF00;
  margin: 1em 0;
  padding: 0.5em 1em;
  background-color: rgba(0, 255, 0, 0.1);
  color: #c0c0c0;
  font-style: italic;
}

.markdown-content :deep(code) {
  background-color: #2a2a2a;
  padding: 0.2em 0.4em;
  border-radius: 3px;
  font-family: 'Courier New', Consolas, Monaco, monospace;
  color: #00FF00;
  font-size: 0.9em;
}

.markdown-content :deep(pre) {
  background-color: #1a1a1a;
  border: 1px solid #333;
  border-radius: 8px;
  padding: 1em;
  overflow-x: auto;
  margin: 1em 0;
  position: relative;
}

.markdown-content :deep(pre code) {
  background-color: transparent;
  padding: 0;
  color: #e0e0e0;
  font-size: 0.9em;
  display: block;
  white-space: pre;
}

.markdown-content :deep(a) {
  color: #00FF00;
  text-decoration: none;
  border-bottom: 1px solid transparent;
  transition: border-color 0.3s ease;
}

.markdown-content :deep(a:hover) {
  border-bottom-color: #00FF00;
}

.markdown-content :deep(table) {
  border-collapse: collapse;
  margin: 1em 0;
  width: 100%;
  max-width: 100%;
  overflow-x: auto;
  display: block;
  white-space: nowrap;
}

.markdown-content :deep(th),
.markdown-content :deep(td) {
  border: 1px solid #333;
  padding: 0.5em 1em;
  text-align: left;
}

.markdown-content :deep(th) {
  background-color: #2a2a2a;
  color: #fff;
  font-weight: bold;
}

.markdown-content :deep(td) {
  background-color: #1a1a1a;
  color: #e0e0e0;
}

.markdown-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 1em 0;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
}

.markdown-content :deep(hr) {
  border: none;
  border-top: 2px solid #333;
  margin: 2em 0;
}

.markdown-content :deep(em) {
  color: #c0c0c0;
  font-style: italic;
}

.markdown-content :deep(strong) {
  color: #fff;
  font-weight: bold;
}

.markdown-content :deep(del) {
  color: #888;
  text-decoration: line-through;
}

/* 代码高亮样式 - VS Code Dark+ 主题风格 */
.markdown-content :deep(.hljs) {
  background: #1a1a1a;
  color: #e0e0e0;
}

.markdown-content :deep(.hljs-keyword) {
  color: #569cd6;
  font-weight: bold;
}

.markdown-content :deep(.hljs-string) {
  color: #ce9178;
}

.markdown-content :deep(.hljs-comment) {
  color: #6a9955;
  font-style: italic;
}

.markdown-content :deep(.hljs-number) {
  color: #b5cea8;
}

.markdown-content :deep(.hljs-function) {
  color: #dcdcaa;
}

.markdown-content :deep(.hljs-variable) {
  color: #9cdcfe;
}

.markdown-content :deep(.hljs-type) {
  color: #4ec9b0;
}

.markdown-content :deep(.hljs-built_in) {
  color: #4ec9b0;
}

.markdown-content :deep(.hljs-selector-tag) {
  color: #f92672;
}

.markdown-content :deep(.hljs-selector-id) {
  color: #a6e22e;
}

.markdown-content :deep(.hljs-selector-class) {
  color: #66d9ef;
}

.markdown-content :deep(.hljs-property) {
  color: #a6e22e;
}

.markdown-content :deep(.hljs-value) {
  color: #e6db74;
}

.markdown-content :deep(.hljs-meta) {
  color: #75715e;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .markdown-content {
    font-size: 0.95em;
  }
  
  .markdown-content :deep(h1) {
    font-size: 1.8em;
  }
  
  .markdown-content :deep(h2) {
    font-size: 1.5em;
  }
  
  .markdown-content :deep(h3) {
    font-size: 1.3em;
  }
  
  .markdown-content :deep(pre) {
    font-size: 0.8em;
    padding: 0.8em;
  }
  
  .markdown-content :deep(table) {
    font-size: 0.9em;
  }
}
</style>







