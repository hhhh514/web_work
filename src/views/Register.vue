<template>
  <v-container fluid class="white">
    <v-row justify="center" class="shift-up">
      <v-col cols="12" sm="12" md="12">
        <v-card class="pa-10 gradient-card">
          <v-row>

            <v-col cols="12" md="5" class="new_role">
              <div class="text-center pa-8">
                <h1 class="display-4 font-weight-bold mb-6">Join Us</h1>
                <v-img
                  :src="imageSrc"
                  alt="註冊歡迎圖片"
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
                <v-card-title class="text-center text-h3">註冊</v-card-title>
                <v-card-text>
                  <v-form @submit.prevent="register">
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
                    <div v-if="password" class="text-caption mt-1">
                      密碼強度: {{ passwordScore }}/4
                      <span v-if="passwordFeedback">, 建議: {{ passwordFeedback }}</span>
                    </div>
                    <v-text-field
                        v-model="confirmPassword"
                        label="確認密碼"
                        prepend-icon="mdi-lock-check"
                        type="password"
                        required
                        class="large-input"
                      />
                      <v-text-field
                      v-model="name"
                      label="姓名"
                      prepend-icon="mdi-account"
                      required
                      class="large-input"
                    ></v-text-field>
                    <v-text-field
                      v-model="email"
                      label="電子郵件"
                      prepend-icon="mdi-email"
                      type="email"
                      required
                      class="large-input"
                    ></v-text-field>

                    <template v-if="role === 'customer'">
                      <v-text-field
                        v-model="phone"
                        label="電話"
                        prepend-icon="mdi-phone"
                        required
                        class="large-input"
                      ></v-text-field>
                      <v-text-field
                        v-model="address"
                        label="地址"
                        prepend-icon="mdi-map-marker"
                        required
                        class="large-input"
                      ></v-text-field>
                    </template>

                    <v-btn color="primary" type="submit" block class="large-btn">註冊</v-btn>
                  </v-form>
                  <v-btn to="/login" text class="mt-4 large-btn" block>已有帳號？前往登入</v-btn>
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
import { ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { apiBaseUrl } from '@/constants/api.js';
import zxcvbn from 'zxcvbn'; // <-- 加入 zxcvbn

export default {
  setup() {
    const confirmPassword = ref('');
    const router = useRouter();
    const role = ref('customer');
    const username = ref('');
    const password = ref('');
    const passwordScore = ref(0); // 密碼強度分數 0~4
    const passwordFeedback = ref(''); // 密碼建議
    const name = ref('');
    const email = ref('');
    const phone = ref('');
    const address = ref('');
    const imageSrc = ref(new URL('@/assets/image.png', import.meta.url).href);

    watch(password, (newVal) => {
      const result = zxcvbn(newVal);
      passwordScore.value = result.score; 
      passwordFeedback.value = result.feedback.warning || result.feedback.suggestions.join(', ');
    });

    const register = async () => {
      if (password.value !== confirmPassword.value) {
        alert('兩次輸入的密碼不一致！');
        return;
      }
      if (!username.value || !password.value || !name.value || !email.value) {
        alert('請填寫所有必填欄位！');
        return;
      }
      if (role.value === 'customer' && (!phone.value || !address.value)) {
        alert('請填寫電話和地址！');
        return;
      }
      if (passwordScore.value < 3) {
        alert('密碼太弱，請使用更複雜的密碼！建議：' + passwordFeedback.value);
        return;
      }

      try {
        const payload = {
          role: role.value,
          account: username.value,
          password: password.value,
          name: name.value,
          email: email.value,
        };
        if (role.value === 'customer') {
          payload.phone = phone.value;
          payload.address = address.value;
        }
        await axios.post(`${apiBaseUrl}/register`, payload);
        alert('註冊成功！');
        router.push('/login');
      } catch (error) {
        alert(`註冊失敗：${error.response?.data?.error || error.message}`);
      }
    };

    return {
      role,
      username,
      password,
      passwordScore,
      passwordFeedback,
      confirmPassword,
      name,
      email,
      phone,
      address,
      imageSrc,
      register,
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
@media (max-width: 960px) {
  .v-col-md-5, .v-col-md-7 {
    margin-bottom: 0.5rem;
  }
  .shift-up {
    margin-top: 0.5rem;
  }
  .v-img:first-child {
    width: 100%;
    max-width: 600px;
    height: 200px;
  }
  .v-img:last-child {
    max-width: 300px;
    height: 80px;
  }
  .display-4 {
    font-size: 3rem !important;
  }
  .text-h3 {
    font-size: 1.5rem !important;
  }
  .large-input, .large-btn {
    font-size: 1.2rem;
  }
}
</style>
