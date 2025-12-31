<template>
  <v-container fluid class="white">
    <v-row justify="center" class="shift-up">
      <v-col cols="12" sm="12" md="12">
        <v-card class="pa-10 gradient-card">
          <v-row>
            <v-col cols="12" md="5" class="new_role">
              <div class="text-center pa-8">
                <h1 class="display-4 font-weight-bold mb-6">Welcome to</h1>
                <v-img
                  :src="imageSrc"
                  alt="Ecom歡迎圖片"
                  class="mx-auto"
                  max-width="900"
                  height="300"
                ></v-img>
              </div>
              <v-img
                max-width="400"
                height="100"
              ></v-img>
            </v-col>
            <v-col cols="12" md="7" class="d-flex align-center">
              <v-card flat class="pa-8 wide-form">
                <v-card-title class="text-center text-h3">登入</v-card-title>
                <v-card-text>
                  <v-form @submit.prevent="login">
                    <v-select
                      v-model="role"
                      :items="['customer', 'seller']"
                      label="角色"
                      prepend-icon="mdi-account-group"
                      required
                      class="large-input"
                    ></v-select>
                    <v-text-field
                      v-model="username"
                      label="帳號"
                      prepend-icon="mdi-account"
                      required
                      class="large-input"
                    ></v-text-field>
                    <v-text-field
                      v-model="password"
                      label="密碼"
                      prepend-icon="mdi-lock"
                      type="password"
                      required
                      class="large-input"
                    ></v-text-field>
                    <v-btn color="primary" type="submit" block class="large-btn" :disabled="isLocked">
                      {{ isLocked ? `請等待 ${lockSeconds} 秒` : '登入' }}
                    </v-btn>
                  </v-form>
                  <v-btn to="/register" text class="mt-4 large-btn" block>尚未註冊？前往註冊</v-btn>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { ref, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { apiBaseUrl } from '@/constants/api.js';

export default {
  setup() {
    const router = useRouter();

    const role = ref('customer');
    const username = ref('');
    const password = ref('');
    const imageSrc = ref(new URL('@/assets/image.png', import.meta.url).href);

    // 🔒 鎖定狀態
    const isLocked = ref(false);
    const lockSeconds = ref(0);
    let timer = null;

    const startCountdown = (seconds) => {
      isLocked.value = true;
      lockSeconds.value = seconds;

      timer && clearInterval(timer);
      timer = setInterval(() => {
        lockSeconds.value--;
        if (lockSeconds.value <= 0) {
          clearInterval(timer);
          isLocked.value = false;
        }
      }, 1000);
    };

    const login = async () => {
      if (isLocked.value) {
        alert(`登入已鎖定，請 ${lockSeconds.value} 秒後再試`);
        return;
      }

      if (!username.value || !password.value) {
        alert('請輸入帳號和密碼！');
        return;
      }

      try {
        const response = await axios.post(`${apiBaseUrl}/login`, {
          role: role.value,
          account: username.value,
          password: password.value,
        });

        const { token, user_id } = response.data;

        localStorage.setItem('isAuthenticated', 'true');
        localStorage.setItem('role', role.value);
        localStorage.setItem('userId', user_id);
        localStorage.setItem('token', token);

        window.dispatchEvent(new Event('storage'));
        router.push('/home');
        window.location.reload();

      } catch (error) {
        if (error.response) {
          // 🔥 被鎖定
          if (error.response.status === 429) {
            const seconds = error.response.data.lock_seconds || 60;
            startCountdown(seconds);
            alert(`嘗試次數過多，請 ${seconds} 秒後再試`);
            return;
          }

          // 一般登入失敗
          if (error.response.data?.error) {
            alert(`登入失敗：${error.response.data.error}`);
            return;
          }
        }

        alert('登入失敗，請稍後再試。');
      }
    };

    onUnmounted(() => {
      timer && clearInterval(timer);
    });

    return {
      role,
      username,
      password,
      login,
      imageSrc,
      isLocked,
      lockSeconds,
    };
  },
};
</script>



<style scoped>

.shift-up {
  margin-top: 1rem;
}
.v-card {
  border: 1px solid #e0e0e0;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}
.wide-form {
  width: 100%;
  max-width: 700px;
  margin: 0 auto;
}
.v-img {
  border-radius: 8px;
}
.large-input {
  font-size: 1.4rem;
}
.large-btn {
  font-size: 1.4rem;
  padding: 14px;
}
.new_role{
  display: flex;
  flex-direction: column;
  padding: 15vh 1rem 1rem 1rem;
}
.gradient-card {
  background: linear-gradient(to bottom right, #e0f7fa, #e1bee7);
  border: 1px solid #e0e0e0;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}
</style>
