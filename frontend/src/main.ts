import { createApp } from 'vue';
import App from './App.vue';
import router from './router'; // 确保正确导入路由实例

const app = createApp(App); // 创建 Vue 应用实例
app.use(router); // 关键步骤：让 Vue 应用使用 Vue Router
app.mount('#app'); // 将 Vue 应用挂载到 index.html 中的 #app 元素