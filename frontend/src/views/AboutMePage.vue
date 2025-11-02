<template>
  <div class="about-page-container">
    <div class="about-content">
      <!-- 头像区域 -->
      <div class="avatar-section">
        <img :src="avatarUrl" :alt="userName" class="avatar" />
      </div>

      <!-- 基本信息 -->
      <div class="info-section">
        <h1 class="user-name">{{ userName }}</h1>
        <p class="user-bio">{{ userBio }}</p>
        <p class="user-description">{{ userDescription }}</p>
      </div>

      <!-- 标签/词条 -->
      <div class="tags-section" v-if="userTags.length > 0">
        <h2 class="section-title">技能标签</h2>
        <div class="tags-container">
          <span v-for="(tag, index) in userTags" :key="index" class="tag">
            {{ tag }}
          </span>
        </div>
      </div>

      <!-- 社交平台链接 -->
      <div class="social-section" v-if="socialLinks.length > 0">
        <h2 class="section-title">找到我</h2>
        <div class="social-links">
          <a
            v-for="(link, index) in socialLinks"
            :key="index"
            :href="link.url"
            target="_blank"
            rel="noopener noreferrer"
            class="social-link"
            :title="link.name"
          >
            <i :class="link.icon"></i>
            <span class="social-name">{{ link.name }}</span>
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

// 从环境变量读取配置
const avatarUrl = import.meta.env.VITE_AVATAR_URL || '/images/avatar.jpg';
const userName = import.meta.env.VITE_USER_NAME || '用户名';
const userBio = import.meta.env.VITE_USER_BIO || '这是我的个人简介';
const userDescription = import.meta.env.VITE_USER_DESCRIPTION || '';
const tagsString = import.meta.env.VITE_USER_TAGS || '';

// 解析标签
const userTags = computed(() => {
  if (!tagsString) return [];
  return tagsString.split(',').map((tag: string) => tag.trim()).filter(Boolean);
});

// 社交平台配置
interface SocialLink {
  name: string;
  url: string;
  icon: string;
}

// 解析社交链接
const socialLinks = computed(() => {
  const links: SocialLink[] = [];
  
  const socialConfig = [
    { name: 'GitHub', env: 'VITE_SOCIAL_GITHUB', icon: 'fab fa-github' },
    { name: 'Bilibili', env: 'VITE_SOCIAL_BILIBILI', icon: 'fab fa-bilibili' },
    { name: '微博', env: 'VITE_SOCIAL_WEIBO', icon: 'fab fa-weibo' },
    { name: 'Twitter', env: 'VITE_SOCIAL_TWITTER', icon: 'fab fa-twitter' },
    { name: '知乎', env: 'VITE_SOCIAL_ZHIHU', icon: 'fab fa-zhihu' },
    { name: '掘金', env: 'VITE_SOCIAL_JUEJIN', icon: 'fas fa-code' },
    { name: 'CSDN', env: 'VITE_SOCIAL_CSDN', icon: 'fas fa-blog' },
    { name: 'LinkedIn', env: 'VITE_SOCIAL_LINKEDIN', icon: 'fab fa-linkedin' },
    { name: 'Email', env: 'VITE_SOCIAL_EMAIL', icon: 'fas fa-envelope' },
    { name: 'Blog', env: 'VITE_SOCIAL_BLOG', icon: 'fas fa-rss' },
    { name: 'QQ', env: 'VITE_SOCIAL_QQ', icon: 'fab fa-qq' },
    { name: '微信', env: 'VITE_SOCIAL_WECHAT', icon: 'fab fa-weixin' },
  ];

  socialConfig.forEach(social => {
    const url = import.meta.env[social.env];
    if (url && url.trim()) {
      links.push({
        name: social.name,
        url: url,
        icon: social.icon
      });
    }
  });

  return links;
});
</script>

<style scoped>
.about-page-container {
  padding: 80px 20px 40px;
  min-height: calc(100vh - 60px);
  display: flex;
  justify-content: center;
  align-items: flex-start;
  position: relative;
  z-index: 5;
}

.about-content {
  max-width: 800px;
  width: 100%;
  background: transparent;
  border: 2px solid #00FF00;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
  animation: slideIn 0.5s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 头像区域 */
.avatar-section {
  display: flex;
  justify-content: center;
  margin-bottom: 30px;
}

.avatar {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  border: 4px solid #00FF00;
  box-shadow: 0 0 20px rgba(0, 255, 0, 0.5);
  object-fit: cover;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.avatar:hover {
  transform: scale(1.05);
  box-shadow: 0 0 30px rgba(0, 255, 0, 0.8);
}

/* 基本信息 */
.info-section {
  text-align: center;
  margin-bottom: 30px;
}

.user-name {
  font-size: 2.5em;
  color: #00FF00;
  margin-bottom: 10px;
  font-weight: bold;
  text-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
}

.user-bio {
  font-size: 1.3em;
  color: #B0B0B0;
  margin-bottom: 15px;
  font-style: italic;
}

.user-description {
  font-size: 1.1em;
  color: #E0E0E0;
  line-height: 1.6;
  max-width: 600px;
  margin: 0 auto;
}

/* 标签区域 */
.tags-section {
  margin-bottom: 30px;
}

.section-title {
  font-size: 1.8em;
  color: #00FF00;
  margin-bottom: 15px;
  text-align: center;
  text-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}

.tag {
  background: rgba(0, 255, 0, 0.1);
  border: 1px solid #00FF00;
  color: #00FF00;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.9em;
  transition: all 0.3s ease;
}

.tag:hover {
  background: rgba(0, 255, 0, 0.2);
  box-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
  transform: translateY(-2px);
}

/* 社交链接区域 */
.social-section {
  margin-top: 30px;
}

.social-links {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  margin-top: 20px;
}

.social-link {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 12px 20px;
  background: rgba(0, 255, 0, 0.05);
  border: 1px solid #00FF00;
  border-radius: 8px;
  color: #00FF00;
  text-decoration: none;
  transition: all 0.3s ease;
  font-size: 1em;
}

.social-link:hover {
  background: rgba(0, 255, 0, 0.15);
  box-shadow: 0 0 15px rgba(0, 255, 0, 0.5);
  transform: translateY(-3px);
}

.social-link i {
  font-size: 1.3em;
}

.social-name {
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .about-content {
    padding: 30px 20px;
  }

  .avatar {
    width: 120px;
    height: 120px;
  }

  .user-name {
    font-size: 2em;
  }

  .user-bio {
    font-size: 1.1em;
  }

  .user-description {
    font-size: 1em;
  }

  .section-title {
    font-size: 1.5em;
  }

  .social-links {
    grid-template-columns: 1fr;
  }

  .social-link {
    padding: 10px 15px;
  }
}

@media (max-width: 480px) {
  .about-page-container {
    padding: 70px 10px 20px;
  }

  .avatar {
    width: 100px;
    height: 100px;
  }

  .user-name {
    font-size: 1.8em;
  }

  .tags-container {
    gap: 8px;
  }

  .tag {
    padding: 6px 12px;
    font-size: 0.85em;
  }
}
</style>

