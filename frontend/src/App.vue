<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- 顶部导航 - 仅登录后显示 -->
    <Header v-if="isLoggedIn" />
    
    <!-- 主内容区 -->
    <main :class="isLoggedIn ? 'pt-16' : ''">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import Header from '@/components/Header.vue'

const route = useRoute()
const isLoggedIn = ref(false)

const checkAuth = () => {
  isLoggedIn.value = !!localStorage.getItem('token')
}

onMounted(checkAuth)
watch(() => route.path, checkAuth)
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
