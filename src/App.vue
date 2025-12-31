
<template>
  <v-app>
    <v-container fluid class="nav-section">
      <v-app-bar app color="#FA8072" dark>
        <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>
        <v-toolbar-title>e-commerce</v-toolbar-title>
        <v-spacer></v-spacer>
   
        <template v-if="!isAuthenticated">
          <v-btn to="/login" text>登入</v-btn>
        </template>
     
        <template v-else>
          <v-btn to="/home" text>商品頁面</v-btn>
  
          <template v-if="role === 'seller'">
            <v-btn to="/seller/profile" text>賣家檔案</v-btn>
          </template>
 
          <template v-if="role === 'customer'">
            <v-btn to="/customers/profile" text>個人資料</v-btn>
          </template>
          <v-btn @click="logout" text>登出</v-btn>
        </template>
      </v-app-bar>
      <v-navigation-drawer v-model="drawer" app temporary>
        <v-list>
          <v-list-item
            v-for="item in navItems"
            :key="item.title"
            :to="item.to"
            link
          >
            <v-list-item-title>{{ item.title }}</v-list-item-title>
          </v-list-item>
          <v-list-item v-if="isAuthenticated" @click="logout">
            <v-list-item-title>登出</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-navigation-drawer>
    </v-container>
    <v-container fluid class="content-section">
      <v-main class="custom-main">
        <router-view></router-view>
      </v-main>
    </v-container>
  </v-app>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';

export default {
  name: 'App',
  setup() {
    const router = useRouter();
    const isAuthenticated = ref(false);
    const role = ref('');

    const updateAuthState = () => {
      isAuthenticated.value = localStorage.getItem('isAuthenticated') === 'true';
      role.value = localStorage.getItem('role') || '';
      console.log('Updated auth state:', { isAuthenticated: isAuthenticated.value, role: role.value });
    };

    updateAuthState();

    onMounted(() => {
      window.addEventListener('storage', updateAuthState);
    });

    const navItems = computed(() => {
      if (!isAuthenticated.value) {
        return [{ title: '登入', to: '/login' }];
      }
      const baseItems = [{ title: '商品頁面', to: '/home' }];
      if (role.value === 'seller') {
        baseItems.push(
          { title: '賣家檔案', to: '/seller/profile' },
          { title: '商家功能', to: '/seller/overview' },
          { title: '銷售總結', to: '/seller/sales-chart' }
        );
      } else if (role.value === 'customer') {
        baseItems.push(
          { title: '購物車', to: '/customers/cart' },
          { title: '個人資料', to: '/customers/profile' },
          { title: '購買紀錄', to: '/customers/purchase-history' },
          { title: '願望清單', to: '/customers/wishlist' }
        );
      }
      return baseItems;
    });
    const logout = () => {
      localStorage.removeItem('isAuthenticated');
      localStorage.removeItem('role');
      localStorage.removeItem('cart'); 
      updateAuthState();
      router.push('/login');
    };
    const drawer = ref(false);
    return {
      drawer,
      navItems,
      isAuthenticated,
      role,
      logout,
    };
  },
};

</script>

<style scoped>
.nav-section,
.content-section {
  padding: 0;
  background: linear-gradient(to bottom right, #4a4747, #ebedee); 
}
.custom-main {
  padding: 9vh 15vw;
  min-height: calc(100vh);
  background: linear-gradient(135deg, #FEF3CC, #FFE3D6);
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease-in-out;
}

.v-app-bar {
  background: linear-gradient(to right, #f6d365, #fda085); 
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
</style>