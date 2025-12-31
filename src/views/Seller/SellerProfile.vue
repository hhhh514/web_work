<template>
  <v-container class="pa-6 text-lg">
    <h1 class="text-h4 font-weight-bold mb-6 text-center">📦 商品管理</h1>
    <v-card class="mb-6 elevation-3 rounded-xl">
      <v-card-title class="font-weight-medium text-center text-mb">👤 賣家資訊</v-card-title>
      <v-card-text v-if="seller">
        <v-row class="text-sm">
          <v-col >名稱：{{ seller.name }}</v-col>
          <v-col >Email：{{ seller.email }}</v-col>
          <v-col >評分：{{ seller.rating }}</v-col>
        </v-row>
      </v-card-text>
    </v-card>
    <v-card class="elevation-3 rounded-xl">
      <v-card-title class="font-weight-medium text-center text-mb ">📋 商品列表</v-card-title>
      <v-data-table
        :headers="headers"
        :items="filteredItems"
        item-value="product_id"
        class="elevation-1 striped hoverable"
        density="comfortable"
      >
        <template #top>
          <v-text-field
            v-model="search"
            label="🔍 搜尋商品名稱"
            class="mx-4 mt-2"
            density="compact"
            clearable
            prepend-inner-icon="mdi-magnify"
          />
        </template>
        <template v-slot:item.product_name="{ item }">
          <router-link
            :to="`/product/${encodeURIComponent(item.product_id)}`"
            class="text-decoration-none accent--text font-weight-medium name-ellipsis"
            draggable="true"
            @dragstart="handleDragStart(item, $event)"
            :data-item-id="item.id"
            :data-cart-id="item.cart_id"
            :title="item.product_name"
            style="font-size: 1.5em; max-width: 20vw;"
          >
            {{ item.product_name }}
          </router-link>
        </template>
        <template #item.actions="{ item, index }">
          <v-icon class="me-2 text-primary" @click="editItem(index)">mdi-pencil</v-icon>
          <v-icon class="text-error" @click="confirmDelete(index)">mdi-delete</v-icon>
        </template>
      </v-data-table>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="primary" variant="elevated" @click="addDialog = true">
          ➕ 新增商品
        </v-btn>
      </v-card-actions>
    </v-card>
    <v-dialog v-model="addDialog" max-width="600">
      <v-card class="elevation-5 rounded">
        <v-card-title class="text-h6 font-weight-medium text-center">新增商品</v-card-title>
        <v-card-text>
          <v-form ref="addForm">
            <v-text-field v-model="newItem.product_name" label="商品名稱" required />
            <v-text-field v-model.number="newItem.price" label="價格" type="number" required />
            <v-text-field v-model.number="newItem.stock" label="庫存" type="number" required />
            <v-text-field v-model="newItem.product_type" label="商品類型" />
            <v-textarea v-model="newItem.description" label="商品描述" />
            <v-text-field v-model.number="newItem.discount" label="折扣 (%)" type="number" />
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="addDialog = false">取消</v-btn>
          <v-btn color="primary" variant="flat" @click="addItem">新增</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>


    <v-dialog v-model="editDialog" max-width="600">
      <v-card class="elevation-5 rounded">
        <v-card-title class="text-h6 font-weight-medium text-center">編輯商品</v-card-title>
        <v-card-text>
          <v-form ref="editForm">
            <v-text-field v-model="editedItem.product_name" label="商品名稱" required />
            <v-text-field v-model.number="editedItem.price" label="價格" type="number" required />
            <v-text-field v-model.number="editedItem.stock" label="庫存" type="number" required />
            <v-text-field v-model="editedItem.product_type" label="商品類型" />
            <v-textarea v-model="editedItem.description" label="商品描述" />
            <v-text-field v-model.number="editedItem.discount" label="折扣 (%)" type="number" />
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="editDialog = false">取消</v-btn>
          <v-btn color="primary" variant="flat" @click="updateItem">儲存</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>


    <v-dialog v-model="removeDialog" max-width="400">
      <v-card class="elevation-4 rounded">
        <v-card-title class="text-h6 font-weight-bold text-center">❗確定刪除此商品？</v-card-title>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="removeDialog = false">取消</v-btn>
          <v-btn color="red darken-1" text @click="removeItem">刪除</v-btn>
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
    const headers = [
      { title: '商品名稱', key: 'product_name' },
      { title: '價格', key: 'price' },
      { title: '庫存', key: 'stock' },
      { title: '類型', key: 'product_type' },
      { title: '描述', key: 'description' },
      { title: '折扣 (%)', key: 'discount' },
      { title: '動作', key: 'actions', sortable: false },
    ];
    const items = ref([]);
    const search = ref('');
    const filteredItems = computed(() =>
      items.value.filter((item) =>
        item.product_name?.toLowerCase().includes(search.value.toLowerCase())
      )
    );
    const seller = ref(null);
    const newItem = ref({
      product_name: '',
      price: 0,
      stock: 0,
      product_type: '',
      description: '',
      discount: 0,
    });
    const editedItem = ref({});
    const removeIndex = ref(null);
    const addDialog = ref(false);
    const editDialog = ref(false);
    const removeDialog = ref(false);
    const addForm = ref(null);
    const editForm = ref(null);
    const sellerId = localStorage.getItem('userId');
    const loadProducts = async () => {
      try {
        const res = await axios.get(`${apiBaseUrl}/products/seller`);
        items.value = res.data;
      } catch (err) {
        console.error('載入商品失敗:', err);
      }
    };

    const loadSeller = async () => {
      try {
        const res = await axios.get(`${apiBaseUrl}/sellers`);
        seller.value = res.data;
        console.log('賣家資料:', seller.value);
      } catch (err) {
        console.error('載入賣家失敗:', err);
      }
    };

    const addItem = async () => {
      if (addForm.value?.validate()) {
        try {
          const payload = { ...newItem.value, seller_id: sellerId };
          console.log('新增商品資料:', payload);
          await axios.post(`${apiBaseUrl}/products`, payload);
          await loadProducts();
          addDialog.value = false;
        } catch (err) {
          console.error('新增商品失敗:', err);
        }
      }
    };

    const editItem = (index) => {
      editedItem.value = { ...filteredItems.value[index] };
      editDialog.value = true;
    };

    const updateItem = async () => {
      if (editForm.value?.validate()) {
        try {
          await axios.put(`${apiBaseUrl}/products/${editedItem.value.product_id}`, editedItem.value);
          await loadProducts();
          editDialog.value = false;
        } catch (err) {
          console.error('更新商品失敗:', err);
        }
      }
    };

    const confirmDelete = (index) => {
      removeIndex.value = index;
      removeDialog.value = true;
    };

    const removeItem = async () => {
      if (removeIndex.value !== null) {
        const product = filteredItems.value[removeIndex.value];
        try {
          await axios.delete(`${apiBaseUrl}/products/${product.product_id}`);
          await loadProducts();
          removeDialog.value = false;
        } catch (err) {
          console.error('刪除商品失敗:', err);
        }
      }
    };

    onMounted(() => {
      loadSeller();
      loadProducts();
    });

    return {
      headers,
      items,
      search,
      filteredItems,
      seller,
      newItem,
      editedItem,
      removeIndex,
      addDialog,
      editDialog,
      removeDialog,
      addForm,
      editForm,
      addItem,
      editItem,
      updateItem,
      confirmDelete,
      removeItem,
      loadSeller,
      loadProducts,
    };
  }
};
</script>


<style scoped>
.text-lg {
  font-size: 2.75rem; 
}
.text-mb{
  font-size: 1.75rem; 
}
.text-sm {
  font-size: 1.25rem; 
  line-height: 1.6;
  padding:2.3vh;
}
</style>