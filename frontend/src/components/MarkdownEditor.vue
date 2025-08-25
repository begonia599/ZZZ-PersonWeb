<template>
  <div class="markdown-editor">
    <div class="editor-header">
      <div class="editor-tabs">
        <button 
          :class="['tab', { active: activeTab === 'edit' }]" 
          @click="activeTab = 'edit'"
        >
          编辑
        </button>
        <button 
          :class="['tab', { active: activeTab === 'preview' }]" 
          @click="activeTab = 'preview'"
        >
          预览
        </button>
        <button 
          :class="['tab', { active: activeTab === 'split' }]" 
          @click="activeTab = 'split'"
        >
          分屏
        </button>
      </div>
      <div class="editor-tools">
        <button @click="insertMarkdown('**', '**')" title="加粗" class="tool-btn">
          <strong>B</strong>
        </button>
        <button @click="insertMarkdown('*', '*')" title="斜体" class="tool-btn">
          <em>I</em>
        </button>
        <button @click="insertMarkdown('`', '`')" title="行内代码" class="tool-btn">
          &lt;/&gt;
        </button>
        <button @click="insertCodeBlock" title="代码块" class="tool-btn">
          { }
        </button>
        <button @click="insertMarkdown('[', '](url)')" title="链接" class="tool-btn">
          🔗
        </button>
        <button @click="insertMarkdown('![', '](url)')" title="图片" class="tool-btn">
          🖼️
        </button>
        <button @click="insertHeading" title="标题" class="tool-btn">
          H
        </button>
        <button @click="insertList" title="列表" class="tool-btn">
          📋
        </button>
        <button @click="insertQuote" title="引用" class="tool-btn">
          💬
        </button>
      </div>
    </div>

    <div class="editor-content" :class="{ 'split-mode': activeTab === 'split' }">
      <!-- 编辑区域 -->
      <div 
        v-show="activeTab === 'edit' || activeTab === 'split'" 
        class="editor-panel"
        :class="{ 'half-width': activeTab === 'split' }"
      >
        <textarea
          ref="textareaRef"
          v-model="internalContent"
          @input="handleInput"
          @keydown="handleKeydown"
          class="editor-textarea"
          :placeholder="placeholder"
          spellcheck="false"
        ></textarea>
      </div>

      <!-- 预览区域 -->
      <div 
        v-show="activeTab === 'preview' || activeTab === 'split'" 
        class="preview-panel"
        :class="{ 'half-width': activeTab === 'split' }"
      >
        <MarkdownRenderer :content="internalContent" />
      </div>
    </div>

    <!-- 状态栏 -->
    <div class="editor-footer">
      <span class="editor-info">
        {{ wordCount }} 字 | {{ lineCount }} 行
      </span>
      <span class="markdown-hint">
        支持 Markdown 语法
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue';
import MarkdownRenderer from './MarkdownRenderer.vue';

const props = defineProps<{
  modelValue: string;
  placeholder?: string;
  rows?: number;
}>();

const emit = defineEmits<{
  'update:modelValue': [value: string];
}>();

const activeTab = ref<'edit' | 'preview' | 'split'>('edit');
const textareaRef = ref<HTMLTextAreaElement>();
const internalContent = ref(props.modelValue || '');

// 同步内容
watch(() => props.modelValue, (newValue) => {
  if (newValue !== internalContent.value) {
    internalContent.value = newValue || '';
  }
});

watch(internalContent, (newValue) => {
  emit('update:modelValue', newValue);
});

// 统计信息
const wordCount = computed(() => {
  return internalContent.value.replace(/\s/g, '').length;
});

const lineCount = computed(() => {
  return internalContent.value.split('\n').length;
});

// 处理输入
const handleInput = () => {
  // 已经通过 v-model 处理
};

// 处理按键
const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Tab') {
    event.preventDefault();
    insertAtCursor('  '); // 插入两个空格
  }
};

// 在光标位置插入文本
const insertAtCursor = (text: string) => {
  const textarea = textareaRef.value;
  if (!textarea) return;

  const start = textarea.selectionStart;
  const end = textarea.selectionEnd;
  const value = internalContent.value;
  
  internalContent.value = value.substring(0, start) + text + value.substring(end);
  
  nextTick(() => {
    textarea.focus();
    textarea.setSelectionRange(start + text.length, start + text.length);
  });
};

// 插入 Markdown 语法
const insertMarkdown = (before: string, after: string) => {
  const textarea = textareaRef.value;
  if (!textarea) return;

  const start = textarea.selectionStart;
  const end = textarea.selectionEnd;
  const value = internalContent.value;
  const selectedText = value.substring(start, end);
  
  const newText = before + selectedText + after;
  internalContent.value = value.substring(0, start) + newText + value.substring(end);
  
  nextTick(() => {
    textarea.focus();
    if (selectedText) {
      // 如果有选中文本，光标移到结尾
      textarea.setSelectionRange(start + newText.length, start + newText.length);
    } else {
      // 如果没有选中文本，光标移到 before 和 after 之间
      textarea.setSelectionRange(start + before.length, start + before.length);
    }
  });
};

// 插入代码块
const insertCodeBlock = () => {
  const textarea = textareaRef.value;
  if (!textarea) return;

  const start = textarea.selectionStart;
  const end = textarea.selectionEnd;
  const value = internalContent.value;
  const selectedText = value.substring(start, end);
  
  const newText = '```\n' + selectedText + '\n```';
  internalContent.value = value.substring(0, start) + newText + value.substring(end);
  
  nextTick(() => {
    textarea.focus();
    if (selectedText) {
      textarea.setSelectionRange(start + newText.length, start + newText.length);
    } else {
      textarea.setSelectionRange(start + 4, start + 4); // 移到第一行末尾
    }
  });
};

// 插入标题
const insertHeading = () => {
  const textarea = textareaRef.value;
  if (!textarea) return;

  const start = textarea.selectionStart;
  const value = internalContent.value;
  
  // 找到当前行的开始
  const lineStart = value.lastIndexOf('\n', start - 1) + 1;
  const lineEnd = value.indexOf('\n', start);
  const currentLine = value.substring(lineStart, lineEnd === -1 ? value.length : lineEnd);
  
  // 检查当前行是否已经是标题
  const headingMatch = currentLine.match(/^(#{1,6})\s/);
  let newLine = '';
  
  if (headingMatch) {
    // 如果已经是标题，增加级别
    const currentLevel = headingMatch[1].length;
    if (currentLevel < 6) {
      newLine = '#' + currentLine;
    } else {
      // 如果已经是 6 级标题，移除标题格式
      newLine = currentLine.replace(/^#{1,6}\s/, '');
    }
  } else {
    // 如果不是标题，添加一级标题
    newLine = '# ' + currentLine;
  }
  
  const realLineEnd = lineEnd === -1 ? value.length : lineEnd;
  internalContent.value = value.substring(0, lineStart) + newLine + value.substring(realLineEnd);
  
  nextTick(() => {
    textarea.focus();
    textarea.setSelectionRange(lineStart + newLine.length, lineStart + newLine.length);
  });
};

// 插入列表
const insertList = () => {
  const textarea = textareaRef.value;
  if (!textarea) return;

  const start = textarea.selectionStart;
  const value = internalContent.value;
  
  // 找到当前行的开始
  const lineStart = value.lastIndexOf('\n', start - 1) + 1;
  const lineEnd = value.indexOf('\n', start);
  const currentLine = value.substring(lineStart, lineEnd === -1 ? value.length : lineEnd);
  
  // 检查当前行是否已经是列表
  const listMatch = currentLine.match(/^(\s*)([-*+]|\d+\.)\s/);
  let newLine = '';
  
  if (listMatch) {
    // 如果已经是列表，移除列表格式
    newLine = currentLine.replace(/^(\s*)([-*+]|\d+\.)\s/, '$1');
  } else {
    // 如果不是列表，添加无序列表
    newLine = '- ' + currentLine;
  }
  
  const realLineEnd = lineEnd === -1 ? value.length : lineEnd;
  internalContent.value = value.substring(0, lineStart) + newLine + value.substring(realLineEnd);
  
  nextTick(() => {
    textarea.focus();
    textarea.setSelectionRange(lineStart + newLine.length, lineStart + newLine.length);
  });
};

// 插入引用
const insertQuote = () => {
  const textarea = textareaRef.value;
  if (!textarea) return;

  const start = textarea.selectionStart;
  const value = internalContent.value;
  
  // 找到当前行的开始
  const lineStart = value.lastIndexOf('\n', start - 1) + 1;
  const lineEnd = value.indexOf('\n', start);
  const currentLine = value.substring(lineStart, lineEnd === -1 ? value.length : lineEnd);
  
  // 检查当前行是否已经是引用
  const quoteMatch = currentLine.match(/^>\s/);
  let newLine = '';
  
  if (quoteMatch) {
    // 如果已经是引用，移除引用格式
    newLine = currentLine.replace(/^>\s/, '');
  } else {
    // 如果不是引用，添加引用
    newLine = '> ' + currentLine;
  }
  
  const realLineEnd = lineEnd === -1 ? value.length : lineEnd;
  internalContent.value = value.substring(0, lineStart) + newLine + value.substring(realLineEnd);
  
  nextTick(() => {
    textarea.focus();
    textarea.setSelectionRange(lineStart + newLine.length, lineStart + newLine.length);
  });
};
</script>

<style scoped>
.markdown-editor {
  border: 1px solid #333;
  border-radius: 8px;
  background-color: #1a1a1a;
  overflow: hidden;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  background-color: #2a2a2a;
  border-bottom: 1px solid #333;
}

.editor-tabs {
  display: flex;
  gap: 5px;
}

.tab {
  padding: 6px 12px;
  border: 1px solid transparent;
  border-radius: 4px;
  background: none;
  color: #b0b0b0;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.9em;
}

.tab:hover {
  color: #fff;
  background-color: #333;
}

.tab.active {
  color: #000;
  background-color: #00FF00;
  border-color: #00FF00;
}

.editor-tools {
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
}

.tool-btn {
  width: 28px;
  height: 28px;
  border: 1px solid #444;
  border-radius: 3px;
  background-color: #333;
  color: #e0e0e0;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8em;
}

.tool-btn:hover {
  background-color: #444;
  border-color: #00FF00;
  color: #00FF00;
}

.editor-content {
  display: flex;
  min-height: 300px;
}

.editor-content.split-mode {
  height: 400px;
}

.editor-panel,
.preview-panel {
  flex: 1;
  overflow: hidden;
}

.editor-panel.half-width,
.preview-panel.half-width {
  flex: 0 0 50%;
  border-right: 1px solid #333;
}

.preview-panel.half-width {
  border-right: none;
  border-left: 1px solid #333;
}

.editor-textarea {
  width: 100%;
  height: 100%;
  border: none;
  background-color: #1a1a1a;
  color: #e0e0e0;
  padding: 15px;
  font-family: 'Courier New', Consolas, Monaco, monospace;
  font-size: 14px;
  line-height: 1.6;
  resize: vertical;
  outline: none;
  box-sizing: border-box;
}

.editor-textarea::placeholder {
  color: #666;
}

.preview-panel {
  background-color: #1a1a1a;
  padding: 15px;
  overflow-y: auto;
  box-sizing: border-box;
}

.editor-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 15px;
  background-color: #2a2a2a;
  border-top: 1px solid #333;
  font-size: 0.8em;
  color: #888;
}

.editor-info {
  color: #b0b0b0;
}

.markdown-hint {
  color: #666;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .editor-header {
    flex-direction: column;
    gap: 10px;
    align-items: stretch;
  }
  
  .editor-tabs {
    justify-content: center;
  }
  
  .editor-tools {
    justify-content: center;
    max-width: 100%;
  }
  
  .tool-btn {
    width: 24px;
    height: 24px;
    font-size: 0.7em;
  }
  
  .editor-content.split-mode {
    flex-direction: column;
    height: auto;
  }
  
  .editor-panel.half-width,
  .preview-panel.half-width {
    flex: 1;
    border-right: none;
    border-left: none;
    border-bottom: 1px solid #333;
  }
  
  .preview-panel.half-width {
    border-bottom: none;
    border-top: 1px solid #333;
  }
  
  .editor-footer {
    flex-direction: column;
    gap: 5px;
    text-align: center;
  }
}

@media (max-width: 480px) {
  .editor-header {
    padding: 8px 10px;
  }
  
  .tab {
    padding: 5px 8px;
    font-size: 0.8em;
  }
  
  .tool-btn {
    width: 22px;
    height: 22px;
    font-size: 0.6em;
  }
  
  .editor-textarea {
    padding: 10px;
    font-size: 13px;
  }
  
  .preview-panel {
    padding: 10px;
  }
}
</style>



