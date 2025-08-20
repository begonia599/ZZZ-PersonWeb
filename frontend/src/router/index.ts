import { createRouter, createWebHistory } from 'vue-router';
import HomePage from '../views/HomePage.vue';
import BlogPage from '../views/BlogPage.vue';
import ArticlePage from '../views/ArticlePage.vue';
import ArticleEditorPage from '../views/ArticleEditorPage.vue';
// 导入其他页面组件的占位符
import ToolboxPage from '../views/ToolboxPage.vue';
import DrivePage from '../views/DrivePage.vue'
import DriveAddPage from '../views/DriveAddPage.vue'
import DriveStatsPage from '../views/DriveStatsPage.vue';
import DriveEditPage from '../views/DriveEditPage.vue';
// import AboutMePage from '../components/AboutMePage.vue';
// import ContactPage from '../components/ContactPage.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage,
  },
  {
    path: '/blog',
    name: 'Blog',
    component: BlogPage,
  },
  {
    path: '/blog/:id', // 动态参数 :id
    name: 'Article',
    component: ArticlePage,
    props: true, // 允许将路由参数作为 props 传递给组件
  },
  {
    path: '/blog/new', // 用于创建新文章
    name: 'NewArticle',
    component: ArticleEditorPage,
  },
  {
    path: '/toolbox',
    name: 'Toolbox',
    component: ToolboxPage,
  },
  {
    path: '/toolbox/drive',
    name: 'Drive',
    component: DrivePage
  },
  {
    path: '/toolbox/drive/edit/:id',
    name: 'DriveEdit',
    component: DriveEditPage
  },
  {
    path: '/toolbox/drive/stats',
    name: 'DriveStats',
    component: DriveStatsPage
  },
  {
    path: '/toolbox/drive/add',
    name: 'DriveAdd',
    component: DriveAddPage
  },
  {
    path: '/about',
    name: 'About',
    component:HomePage,
  },
  {
    path: '/contact',
    name: 'Contact',
    component:HomePage,
  },
  // 你可以根据需要添加一个 404 页面
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../components/NotFoundPage.vue'), // 懒加载 404 页面
  },
];

const router = createRouter({
  history: createWebHistory(), // 使用 HTML5 History 模式
  routes,
});

export default router;