<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <h1 class="text-center">購買紀錄</h1>
        <v-alert v-if="error" type="error" dismissible @click:close="error = ''">
          {{ error }}
        </v-alert>
        <v-data-table
          :headers="headers"
          :items="orders"
          :loading="loading"
          item-value="order_id"
          class="elevation-1 rounded-lg"
          @click:row="onRowClick"
          items-per-page="5"
        >
          <template #no-data>
            <div class="text-center py-4">目前沒有訂單</div>
          </template>
          <template #item.order_date="{ item }">
            {{ formatDate(item.order_date) }}
          </template>
        </v-data-table>
      </v-col>
    </v-row>
    <v-dialog v-model="dialog" max-width="600">
      <v-card class="rounded-xl">
        <v-card-title class="text-h6">訂單商品明細</v-card-title>
        <v-card-text>
          <v-row v-if="selectedOrder">
            <v-col cols="12">
              <p><strong>訂單編號:</strong> {{ selectedOrder.order_id }}</p>
              <p><strong>訂單日期:</strong> {{ formatDate(selectedOrder.order_date) }}</p>
              <p><strong>總金額:</strong> ${{ selectedOrder.total_amount }}</p>
            </v-col>
          </v-row>
          <v-list v-if="selectedOrder?.items && selectedOrder.items.length > 0">
            <v-list-item
              v-for="(item, index) in selectedOrder.items"
              :key="index"
            >
              <v-list-item-content>
                <v-list-item-title>
                  <router-link
                    :to="`/product/${encodeURIComponent(item.product_id)}`"
                    class="text-decoration-none accent--text font-weight-medium name-ellipsis"
                    style="max-width: 15vw;"
                  >
                    {{ item.product_name }}
                  </router-link>
                  - ${{ item.subtotal }} x {{ item.quantity }}
                </v-list-item-title>
                <v-list-item-subtitle>
                  <v-chip
                    :color="item.status === 'delivered' ? 'green' : item.status === 'completed' ? 'blue' : 'grey'"
                    small
                    dark
                  >
                    狀態：{{ item.status }}
                  </v-chip>
                </v-list-item-subtitle>
              </v-list-item-content>
              <v-list-item-action>
                <v-btn
                  v-if="item.status === 'delivered'"
                  color="success"
                  @click="acceptOrder(item)"
                >
                  接受
                </v-btn>
                <v-btn
                  v-if="item.status === 'completed'"
                  color="primary"
                  @click="openReviewDialog(item)"
                >
                  評論
                </v-btn>
              </v-list-item-action>
            </v-list-item>
          </v-list>
          <div v-else class="text-center text-grey">此訂單內沒有商品</div>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text color="primary" @click="dialog = false">關閉</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="reviewDialog" max-width="500">
      <v-card class="rounded-xl">
        <v-card-title class="text-h6">撰寫評論</v-card-title>
        <v-card-text>
          <v-form ref="reviewForm">
            <v-row>
              <v-col cols="12">
                <v-rating
                  v-model="review.rating"
                  color="yellow darken-3"
                  background-color="grey lighten-1"
                  hover
                  length="5"
                  size="30"
                ></v-rating>
              </v-col>
              <v-col cols="12">
                <v-textarea
                  v-model="review.comment"
                  label="評論內容"
                  rows="4"
                  counter
                  :rules="[v => !!v || '請輸入評論內容']"
                ></v-textarea>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text color="grey" @click="reviewDialog = false">取消</v-btn>
          <v-btn color="primary" @click="submitReview">提交</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import { ref, onMounted } from 'vue';
import { apiBaseUrl, customerId } from '@/constants/api.js';
import axios from 'axios';
export default {
  setup() {
    const orders = ref([]);
    const dialog = ref(false);
    const selectedOrder = ref(null);
    const loading = ref(false);
    const error = ref('');
    const reviewDialog = ref(false);
    const review = ref({
      rating: 0,
      comment: '',
      product_id: null,
    });
    const headers = [
      { title: '訂單編號', key: 'order_id' },
      { title: '總金額', key: 'total_amount' },
      { title: '日期', key: 'order_date' },
    ];

    const formatDate = (dateStr) => {
      const date = new Date(Date.parse(dateStr));
      if (isNaN(date)) return 'Invalid Date';
      return new Intl.DateTimeFormat('zh-TW', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true,
      }).format(date);
    };

    const onRowClick = (event, { item }) => {
      selectedOrder.value = item;
      dialog.value = true;
    };

    const fetchOrders = async () => {
      try {
        loading.value = true;
        if (!customerId.value) throw new Error('請先登入');
        const res = await axios.get(`${apiBaseUrl}/orders/customer`);
        orders.value = res.data;
      } catch (err) {
        console.error('載入失敗:', err);
        error.value = '無法載入訂單';
      } finally {
        loading.value = false;
      }
    };

    const acceptOrder = async (item) => {
      try {
        await axios.put(`${apiBaseUrl}/orders/item/${item.order_item_id}/status`, {
          status: 'completed',
        });
        item.status = 'completed';
      } catch (err) {
        console.error('狀態更新失敗:', err);
        error.value = '無法更新訂單狀態';
      }
    };

    const openReviewDialog = (item) => {
      review.value = {
        rating: 0,
        comment: '',
        product_id: item.product_id,
      };
      reviewDialog.value = true;
    };

    const submitReview = async () => {
      try {
        if (!review.value.rating || !review.value.comment) {
          error.value = '請提供評分和評論內容';
          return;
        }
        const payload = {
          customer_id: customerId.value,
          product_id: review.value.product_id,
          rating: review.value.rating,
          comment: review.value.comment,
        };
        const res = await axios.post(`${apiBaseUrl}/reviews`, payload);
        if (res.status === 201) {
          error.value = '';
          reviewDialog.value = false;
          review.value = { rating: 0, comment: '', product_id: null };
        }
      } catch (err) {
        console.error('評論提交失敗:', err);
        error.value = '無法提交評論';
      }
    };

    onMounted(() => {
      fetchOrders();
    });

    return {
      orders,
      dialog,
      selectedOrder,
      loading,
      error,
      headers,
      formatDate,
      onRowClick,
      fetchOrders,
      acceptOrder,
      reviewDialog,
      review,
      openReviewDialog,
      submitReview,
    };
  },
};
</script>


<style scoped>
.v-data-table {
  margin-top: 20px;
}
.v-card-title {
  background-color: #f5f5f5;
}
</style>