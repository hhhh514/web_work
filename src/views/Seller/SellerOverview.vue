<template>
  <v-container fluid class="white">
    <v-row class="mb-4 shift-up">
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4 gradient-card" elevation="2" @click="openRevenueDialog">
          <v-card-title class="text-h6">總收入</v-card-title>
          <v-card-text class="text-h5">${{ totalRevenue }}</v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4 gradient-card" elevation="2" @click="openOrdersDialog('all')">
          <v-card-title class="text-h6">訂單數量</v-card-title>
          <v-card-text class="text-h5">{{ totalOrders }}</v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4 gradient-card" elevation="2" @click="openLowStockDialog">
          <v-card-title class="text-h6">低庫存商品</v-card-title>
          <v-card-text class="text-h5">{{ lowStockItems }}</v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4 gradient-card" elevation="2" @click="openOrdersDialog('待處理')">
          <v-card-title class="text-h6">待處理訂單</v-card-title>
          <v-card-text class="text-h5">{{ pendingOrders }}</v-card-text>
        </v-card>
      </v-col>
    </v-row>
    <v-dialog v-model="revenueDialog" max-width="800">
      <v-card class="pa-6 gradient-card">
        <v-card-title class="text-h5">總收入組成</v-card-title>
        <v-card-text>
          <v-data-table
            :headers="revenueHeaders"
            :items="salesSummaries"
            hide-default-footer
            class="elevation-1"
          >
            <template v-slot:no-data>
              <div class="text-center py-4">無訂單資料</div>
            </template>
          </v-data-table>
          <div class="text-right text-h6 mt-4">
            總計: <span class="font-weight-bold">${{ totalRevenue }}</span>
          </div>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" text @click="revenueDialog = false">關閉</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-dialog v-model="lowStockDialog" max-width="800">
      <v-card class="pa-6 gradient-card">
        <v-card-title class="text-h5">低庫存商品</v-card-title>
        <v-card-text>
          <v-data-table
            :headers="lowStockHeaders"
            :items="lowStockItemsList"
            hide-default-footer
            class="elevation-1"
          >
            <template v-slot:no-data>
              <div class="text-center py-4">無低庫存商品</div>
            </template>
          </v-data-table>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" text @click="lowStockDialog = false">關閉</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-dialog v-model="ordersDialog" max-width="1000">
      <v-card class="pa-6 gradient-card">
        <v-card-title class="text-h5">
          {{ getFilterLabel(orderFilter)}}
        </v-card-title>
        <v-card-text>
          <v-row>
            <!-- item-title vuetify3 item-text vuetify2 -->
            <v-col cols="12" sm="4">
              <v-select
                v-model="orderFilter"
                :items="filterOptions" 
                item-title="text"  
                item-value="value"
                label="篩選訂單"
                prepend-icon="mdi-filter"
                dense
                outlined
              ></v-select>
            </v-col>
          </v-row>
          <v-data-table
            :headers="orderHeaders"
            :items="filteredOrders"
            hide-default-footer
            class="elevation-1"
          >
            <template v-slot:no-data>
              <div class="text-center py-4">無訂單資料</div>
            </template>
            <template v-slot:item.actions="{ item }">
              <v-btn
                v-if="item.status === '待處理'"
                color="success"
                small
                @click="shipOrder(item)"
              >
                發貨
              </v-btn>
            </template>
          </v-data-table>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" text @click="ordersDialog = false">關閉</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';
import { apiBaseUrl } from '@/constants/api';
export default {
  setup() {
    const sellerId = localStorage.getItem('userId');
    const items = ref([]);
    const orders = ref([]);
    const revenueHeaders = [
      { title: '商品ID', key: 'product_id' },
      { title: '總售出數量', key: 'total_quantity_sold' },
      { title: '總收入', key: 'total_revenue' },
      { title: '最後更新', key: 'last_updated' },
    ];
    const reverseStatusMap = {
      'pending': '待處理',
      'shipped': '已發貨',
      'delivered': '已送達',
      'completed': '已完成',
    };
    const filterOptions = [
      { text: '所有訂單', value: 'all' },
      { text: '待處理訂單', value: '待處理' },
      { text: '已發貨訂單', value: '已發貨' },
      { text: '已完成訂單', value: '已完成' },
    ];
    const lowStockHeaders = [
      { title: '商品名稱', key: 'product_name' },
      { title: '庫存量', key: 'stock' },
    ];
    const orderHeaders = [
      { title: '訂單ID', key: 'order_id' },
      { title: '商品ID', key: 'product_id' },
      { title: '數量', key: 'quantity' },
      { title: '金額', key: 'subtotal' },
      { title: '狀態', key: 'status' },
      { title: '操作', key: 'actions' },
    ];
    const revenueDialog = ref(false);
    const lowStockDialog = ref(false);
    const ordersDialog = ref(false);
    const orderFilter = ref('all');
    
    const getFilterLabel = (val) => {
      const found = filterOptions.find(opt => opt.value === val);
      return found ? found.text : '';
    };
    const totalRevenue = computed(() =>
      salesSummaries.value.reduce((sum, item) => sum + item.total_revenue, 0)
    );
    const totalOrders = computed(() => orders.value.length);
    const lowStockItems = computed(() =>
      items.value.filter(item => item.stock < 60).length
    );
    const pendingOrders = computed(() =>
      orders.value.filter(order => order.status === '待處理').length
    );

    const lowStockItemsList = computed(() =>
      items.value.filter(item => item.stock < 60)
    );
    
    const filteredOrders = computed(() => {
      if (orderFilter.value === 'all') return orders.value;
      return orders.value.filter(order => order.status === orderFilter.value);
    });
    
    const openRevenueDialog = () => (revenueDialog.value = true);
    const openLowStockDialog = () => (lowStockDialog.value = true);
    const openOrdersDialog = (filter) => {
      orderFilter.value = filter;
      ordersDialog.value = true;
    };
    const fetchProducts = async () => {
      try {
        const res = await axios.get(`${apiBaseUrl}/products/seller`);
        items.value = res.data;
      } catch (error) {
        console.error('取得商品資料失敗:', error);
      }
    };
    const fetchOrders = async () => {
      try {
        const res = await axios.get(`${apiBaseUrl}/orders/seller`);
        orders.value = res.data.map(order => ({
          ...order,
          status: reverseStatusMap[order.status] || order.status,
        }));
      } catch (error) {
        console.error('取得訂單資料失敗:', error);
      }
    };
    const shipOrder = async (order) => {
      try {
        await axios.put(`${apiBaseUrl}/orders/item/${order.order_item_id}/status`, {
          status: 'delivered',
        });
        const index = orders.value.findIndex(o => o.order_item_id === order.order_item_id);
        if (index !== -1) {
          orders.value[index].status = '已發貨';
        }
      } catch (error) {
        alert('發貨失敗');
      }
    };
    const salesSummaries = ref([]);

    const fetchSalesSummaries = async () => {
      try {
        const res = await axios.get(`${apiBaseUrl}/sales-summary/seller`);
        salesSummaries.value = res.data;
      } catch (error) {
        console.error('取得銷售總結失敗:', error);
      }
    };
    onMounted(() => {
      fetchProducts();
      fetchOrders();
      fetchSalesSummaries();
    });
    return {
      revenueDialog,
      lowStockDialog,
      ordersDialog,
      orderFilter,
      filterOptions,
      totalRevenue,
      totalOrders,
      lowStockItems,
      pendingOrders,
      lowStockItemsList,
      filteredOrders,
      revenueHeaders,
      lowStockHeaders,
      orderHeaders,
      getFilterLabel,
      openRevenueDialog,
      openLowStockDialog,
      openOrdersDialog,
      shipOrder,
      salesSummaries,
    };
  },
};
</script>


<style scoped>
.shift-up {
  margin-top: 1rem;
}
.gradient-card {
  background: linear-gradient(to bottom right, #e0f7fa, #e1bee7);
  border: 1px solid #e0e0e0;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}
.v-card {
  cursor: pointer;
}
</style>