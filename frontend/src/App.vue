<template>
  <el-container class="app-container">
    <el-header class="app-header">
      <div class="header-content">
        <h1>🔍 HyperLiquid 钱包分析系统</h1>
        <el-menu
          mode="horizontal"
          :default-active="activeMenu"
          router
          class="header-menu"
        >
          <el-menu-item index="/dashboard">📊 看板</el-menu-item>
          <el-menu-item index="/wallets">💼 钱包列表</el-menu-item>
          <el-menu-item index="/notifications">🔔 通知</el-menu-item>
        </el-menu>
      </div>
    </el-header>
    <el-main class="app-main">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const activeMenu = computed(() => route.path)
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.app-container {
  min-height: 100vh;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  padding: 0 20px;
}

.header-content h1 {
  font-size: 20px;
  font-weight: 600;
}

.header-menu {
  background: transparent;
  border: none;
}

.header-menu .el-menu-item {
  color: rgba(255,255,255,0.9);
  border-bottom: 2px solid transparent;
}

.header-menu .el-menu-item:hover,
.header-menu .el-menu-item.is-active {
  color: white;
  border-bottom-color: white;
  background: rgba(255,255,255,0.1);
}

.app-main {
  padding: 20px;
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
}
</style>

