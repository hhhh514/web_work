<template>
  <div class="d-flex justify-center align-center" style="min-height: 85vh;">
    <section class="hero">
      <div class="hero-content">
        <h1>歡迎來到</h1>
          <v-img
            :src="imageSrc"
            alt="Ecom歡迎圖片"
            class="mx-auto"
            width="60vw"
            height="40vh"
          ></v-img>
        <div class="hero-buttons">
          <router-link to="/login" class="btn">立即登入</router-link>
          <router-link to="/register" class="btn btn-outline">註冊帳號</router-link>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import { ref } from 'vue';
export default {
  name: 'main',
  setup() {
    const imageSrc = ref(new URL('@/assets/image.png', import.meta.url).href);
    return { imageSrc };
  }
}
</script>

<style scoped>
.home-page {
  font-family: 'Segoe UI', sans-serif;
  color: #333;
  width: 50vw;
  height: 50vh;
}
.hero {
  background-size: cover;
  text-align: center;
  color: white;
}

.hero-content {
  background-color: rgba(0, 0, 0, 0.5);
  display: inline-block;
  padding: 40px;
  border-radius: 12px;
}

.hero h1 {
  font-size: 3rem;
  margin-bottom: 10px;
}

.hero p {
  font-size: 1.2rem;
  margin-bottom: 30px;
}

.hero-buttons .btn {
  padding: 12px 24px;
  margin: 5px;
  background-color: #42b983;
  border: none;
  color: white;
  border-radius: 6px;
  text-decoration: none;
  font-weight: bold;
  transition: background 0.3s ease;
}

.hero-buttons .btn:hover {
  background-color: #36966f;
}

.btn-outline {
  background-color: transparent;
  border: 2px solid white;
  color: white;
}

.btn-outline:hover {
  background-color: white;
  color: #333;
}
</style>
