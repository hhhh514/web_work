<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-btn @click="$router.back()" class="mb-2" style="background-color: #FFDAB9;">
          <v-icon left>mdi-arrow-left</v-icon>
          返回
        </v-btn>

        <v-progress-circular v-if="loading" indeterminate color="primary" class="mx-auto d-block mt-4" />

        <v-card v-else-if="product" class="mx-auto" max-width="600">
          <v-img :src="product.image_url" height="300px" cover />

          <v-card-title class="product-title">
            {{ product.name }}
          </v-card-title>

          <v-card-text>
            <p style="font-size: 1.0em;">價格: ${{ product.price.toFixed(2) }}</p>
            <p style="font-size: 1.0em;">庫存: {{ product.stock }} 件</p>
            <p style="font-size: 1.0em;">商品描述: {{ product.description }}</p>

            <v-text-field v-model.number="quantity" label="數量" type="number" min="1" :max="product.stock"
              style="width: 100px; font-size: 1.0em;" :rules="[v => v >= 1 && v <= product.stock || '數量無效']" />
          </v-card-text>

          <v-card-actions>
            <v-btn color="primary" @click="addToCart" style="font-size: 1.0em;">
              加入購物車
            </v-btn>
            <v-btn color="pink" @click="addToWishlist" style="font-size: 1.0em;">
              加入願望清單
            </v-btn>
          </v-card-actions>
        </v-card>

        <v-alert v-else type="error" style="font-size: 1.5em;">
          商品未找到！
        </v-alert>

        <v-card v-if="comments.length" class="mx-auto mt-4" max-width="600">
          <v-card-title style="font-size: 1.5em; font-weight: bold;">顧客留言</v-card-title>
          <v-divider></v-divider>
          <v-card-text>
            <v-list>
              <v-list-item v-for="comment in comments" :key="comment.review_id">
                <v-list-item-content>
                  <v-rating v-model="comment.rating" readonly color="amber" dense half-increments size="20" />
                  <div class="mt-1" style="font-size: 1.25em;">
                    {{ comment.comment }} (by {{ comment.customer_name }})
                  </div>
                  <div class="text-caption grey--text" style="font-size: 1.15em;">
                    {{ formatDate(comment.review_date) }}
                  </div>
                </v-list-item-content>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>

        <v-card v-else-if="product" class="mx-auto mt-4" max-width="600">
          <v-card-text class="text-center grey--text" style="font-size: 1.2em;">
            尚無顧客留言
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useRoute} from 'vue-router';
import { apiBaseUrl ,customerId} from '@/constants/api.js';
import axios from 'axios';
export default {
  setup() {
    const route = useRoute();
    const product = ref(null);
    const quantity = ref(1);
    const comments = ref([]);
    const loading = ref(true);
    const error = ref(null);
    const fetchProduct = async () => {
      try {
        loading.value = true;
        const response = await axios.get(`${apiBaseUrl}/products/${route.params.id}`);
        product.value = response.data;
        comments.value = response.data.reviews || [];
      } catch (err) {
        error.value = '無法載入商品資料';
        product.value = null;
      } finally {
        loading.value = false;
      }
    };
    const formatDate = (dateStr) => {
      const date = new Date(dateStr);
      return date.toLocaleDateString('zh-TW', { year: 'numeric', month: 'long', day: 'numeric' });
    };
    const addToCart = async () => {
      if (!product.value || quantity.value < 1 || quantity.value > product.value.stock) {
        alert('請輸入有效的數量或商品資訊錯誤！');
        return;
      }
      try {
        console.log(product.value.product_id,quantity.value,customerId.value)
        const response = await axios.post(`${apiBaseUrl}/carts/add`, {
          customer_id: parseInt(customerId.value),
          product_id: product.value.product_id,
          quantity: quantity.value
        });
        if (response.status === 200) {
          alert(`${product.value.name} 已加入購物車！`);
        }
      } catch (err) {
        console.error('Add to cart error:', err);
      }
    };

    const addToWishlist = async () => {
      if (!customerId) {
        alert('用戶未登入OR賣家無法使用');
        return;
      }
      try {
        await axios.post(`${apiBaseUrl}/wishlists/customer/items`, {
          product_id: product.value.product_id
        });
        alert(`${product.value.name} 已加入願望清單！`);
      } catch (err) {
        if (err.response && err.response.status === 409) {
          alert('該商品已在願望清單中');
        }
      }
    };

    onMounted(() => {
      fetchProduct();
    });
    return {
      product,
      quantity,
      comments,
      loading,
      error,
      formatDate,
      addToCart,
      addToWishlist,
    };
  },
};
</script>

<style scoped>
.product-title {
  font-size: 1.5em;
  font-weight: bold;
  white-space: normal;
  word-break: break-word;
  overflow-wrap: break-word;
  line-height: 1.2;
  padding: 16px;
}
</style>