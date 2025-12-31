<template>
  <v-container class="white">
    <v-row>
      <v-col cols="12">
        <v-btn @click="$router.back()" class="mb-4" style="background-color: #FFDAB9;">
          <v-icon left>mdi-arrow-left</v-icon>
          返回
        </v-btn>

        <v-card class="mx-auto" max-width="600">
          <v-card-title style="font-size: 1.75em;">我的願望清單</v-card-title>
          <v-divider></v-divider>

          <v-card-text>
            <v-table v-if="wishlistItems.length">
              <thead>
                <tr>
                  <th class="text-left" style="font-size: 1.25em;">商品名稱</th>
                  <th class="text-left" style="font-size: 1.25em;">價格</th>
                  <th class="text-right" style="font-size: 1.25em;">刪除</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in wishlistItems" :key="item.product_id">
                  <td>
                    <v-tooltip bottom>
                      <template #activator="{ on, attrs }">
                        <router-link :to="`/product/${item.product_id}`" class="product-name" v-bind="attrs" v-on="on">
                          {{ item.product_name }}
                        </router-link>
                      </template>
                      <span>{{ item.product_name }}</span>
                    </v-tooltip>
                  </td>
                  <td>${{ item.price }}</td>
                  <td class="text-right">
                    <v-btn icon @click="removeFromWishlist(item.product_id)">
                      <v-icon style="color: #FF6B6B;">mdi-delete</v-icon>
                    </v-btn>
                  </td>
                </tr>
              </tbody>
            </v-table>

            <div v-else class="text-center" style="color: #FA8072;">
              尚無願望清單項目
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { ref, onMounted } from 'vue';
import { apiBaseUrl,customerId } from '@/constants/api';
import axios from 'axios';
export default {
  setup() {
    const wishlistItems = ref([]);
    const wishlistId = ref(null);
    const fetchWishlist = async () => {
      try {
        const res = await axios.get(`${apiBaseUrl}/wishlists`);
        wishlistId.value = res.data.wishlist_id;

        const itemsRes = await axios.get(`${apiBaseUrl}/wishlists/${wishlistId.value}/items`);
        wishlistItems.value = itemsRes.data;
      } catch (error) {
        console.error('無法載入願望清單:', error);
      }
    };

    const removeFromWishlist = async (productId) => {
      try {
        await axios.delete(`${apiBaseUrl}/wishlists/${wishlistId.value}/items/${productId}`);
        wishlistItems.value = wishlistItems.value.filter(item => item.product_id !== productId);
      } catch (error) {
        console.error('刪除失敗:', error);
      }
    };

    onMounted(fetchWishlist);

    return {
      wishlistItems,
      removeFromWishlist
    };
  }
};
</script>

<style scoped>
.product-name {
  font-size: 1.1rem;
  text-decoration: none;
  color: inherit;
  max-width:200px;
  display: inline-block;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.product-name:hover {
  text-decoration: underline;
  color: #FA8072;
}

</style>
