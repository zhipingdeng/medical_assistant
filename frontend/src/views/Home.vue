<template>
  <div></div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

onMounted(() => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    const user = JSON.parse(userStr)
    router.replace(user.role === 'doctor' ? '/doctor' : '/patient')
  } else {
    router.replace('/login')
  }
})
</script>
