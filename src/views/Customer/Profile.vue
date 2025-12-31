<template>
  <v-container fluid class="white">
    <v-row justify="center" class="shift-up">
      <v-col cols="12" sm="12" md="12">
        <v-card class="pa-10 gradient-card rounded-xl">
          <v-row>
            <v-col cols="12" md="5" class="new_role">
              <div class="text-center pa-8">
                <h1 class="display-4 font-weight-bold mb-6"></h1>
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
              <v-card flat class="pa-8 wide-form rounded-xl">
                <v-card-title class="text-center text-h3 " style="font-size: 2.8em;">
                  顧客資料
                </v-card-title>
                <v-card-text>
                  <v-form @submit.prevent="saveProfile">
                    <v-text-field
                      v-model="profile.name"
                      label="姓名"
                      prepend-icon="mdi-account"
                      required
                      class="large-input"
                    ></v-text-field>
                    <v-text-field
                      v-model="profile.phone"
                      label="電話號碼"
                      prepend-icon="mdi-phone"
                      required
                      class="large-input"
                    ></v-text-field>
                    <v-text-field
                      v-model="profile.email"
                      label="電子郵件"
                      prepend-icon="mdi-email"
                      type="email"
                      required
                      class="large-input"
                    ></v-text-field>
                    <v-text-field
                      v-model="profile.address"
                      label="地址"
                      prepend-icon="mdi-map-marker"
                      required
                      class="large-input"
                    ></v-text-field>
                    <v-btn color="primary" type="submit" block class="large-btn rounded-xl">
                      儲存
                    </v-btn>
                  </v-form>
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
import { ref, onMounted } from 'vue';
import { apiBaseUrl,customerId } from '@/constants/api.js';
import axios from 'axios';
export default {
  name: 'CustomerProfile',
  setup() {
    const imageSrc = ref(new URL('@/assets/image.png', import.meta.url).href);
    const profile = ref({
      name: '',
      email: '',
      phone: '',
      address: '',
    });

    const getProfile = async () => {
      try {
        const response = await axios.get(`${apiBaseUrl}/customers`);
        profile.value = response.data;
      } catch (error) {
        console.error('載入顧客資料失敗:', error);
        alert('無法載入顧客資料');
      }
    };

    const saveProfile = async () => {
      try {
        await axios.put(`${apiBaseUrl}/customers`, profile.value);
        alert('資料已更新！');
      } catch (error) {
        alert('更新資料時發生錯誤');
      }
    };

    onMounted(() => {
      getProfile();
    });

    return {
      profile,
      saveProfile,
      imageSrc,
    };
  },
};
</script>


<style scoped>
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

.new_role {
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