<template>
    <v-container fluid class="white">
      <v-row>
        <v-col cols="12" class="text-center">
          <h1>404 - 頁面未找到</h1>
          <p>您訪問的頁面不存在。</p>
          <v-btn to="/" color="primary">返回首頁</v-btn>
        </v-col>
      </v-row>
    </v-container>
  </template>
  
  <script>
  export default {
    name: 'NotFound',
  };
  </script>
  
  <style scoped>
  .white {
    background-color: white !important;
    min-height: 100vh;
  }
  </style>