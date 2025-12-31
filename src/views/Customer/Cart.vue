<template>
  <v-container fluid class="custom-main pa-4">
    <v-row align="start">
      <v-col cols="12" md="8">
        <v-card class="mb-8 light-border rounded-xl">
          <v-card-title class="font-weight-bold d-flex justify-center mt-4" style="font-size: 1.75em;">購物車內容</v-card-title>
          <v-divider></v-divider>
          <v-card-text>
            <div v-if="customerId.value" class="text-center py-4" style="font-size: 1.25em;">
              請先登入以查看購物車
            </div>
            <div
              v-else-if="Object.keys(groupedCart).length === 0"
              class="text-center py-4" style="font-size: 1.25em;"
            >
              正在載入購物車資料...
            </div>
            <div
              v-else
              v-for="(items, category) in groupedCart"
              :key="category"
              class="mb-4 drop-zone"
              dropzone
              @dragover.prevent
              @drop="handleDrop(category, $event)"
            >
              <div class="d-flex align-center mb-2 ">
                <v-checkbox
                  class="ma-0"
                  hide-details
                  :label="`分類：${category}`"
                  :model-value="isCategorySelected(category)"
                  @update:model-value="toggleCategorySelection(category, $event)"
                  style="font-size: 1.5em;"
                ></v-checkbox>
                <v-btn
                  v-if="category !== '一般'"
                  small
                  @click="openEditCartDialog(category)"
                  style="font-size: 1.2em; background-color: #4CAF50; color: white;margin-right: 3.0vw;"
                  class="rounded-pill ml-auto"
                >
                  編輯
                </v-btn>
              </div>
              <v-data-table
                v-model="selectedItems"
                :headers="cartHeaders"
                :items="items"
                item-value="id"
                class="elevation-1 custom-main rounded-lg"
                hide-default-footer
                show-select
              >
                <template v-slot:no-data>
                  <div class="text-center py-4" style="font-size: 1.25em;">購物車內沒有商品</div>
                </template>
                <template v-slot:item.product_name="{ item }">
                  <router-link
                    :to="`/product/${encodeURIComponent(item.id)}`"
                    class="text-decoration-none accent--text font-weight-medium name-ellipsis"
                    draggable="true"
                    @dragstart="handleDragStart(item, $event)"
                    :data-item-id="item.id"
                    :data-cart-id="item.cart_id"
                    :title="item.product_name"
                    style="font-size: 1.5em;"
                  >
                    {{ item.product_name }}
                  </router-link>
                </template>
                <template v-slot:item.quantity="{ item }">
                  <div class="quantity-control">
                    <v-btn small icon @click="decreaseQuantity(item)">
                      <v-icon>mdi-minus</v-icon>
                    </v-btn>
                    <span class="quantity-display">{{ item.quantity }}</span>
                    <v-btn small icon @click="increaseQuantity(item)">
                      <v-icon>mdi-plus</v-icon>
                    </v-btn>
                  </div>
                </template>
                <template v-slot:item.actions="{ item }">
                  <v-btn
                    small
                    @click="removeFromCartPD(item.cart_id, item.product_id)"
                    style="font-size: 1.2em; background-color: #FF6B6B; color: white;"
                    class="rounded-pill"
                  >
                    移除
                  </v-btn>
                </template>
              </v-data-table>
            </div>
          </v-card-text>
          <div v-if="!customerId.value" class="d-flex justify-center mt-4">
            <v-card-actions class="d-flex align-center flex-wrap">
              <v-btn
                style="font-size: 1.2em; background-color: #FF6B6B; color: white;"
                class="rounded-pill"
                :disabled="selectedItems.length === 0"
                @click="removeSelectedItems"
              >
                刪除所選
              </v-btn>
              <v-btn
                style="font-size: 1.2em; background-color: #FFA07A; color: white;"
                class="rounded-pill ml-2"
                :disabled="selectedItems.length === 0"
                @click="dialogOpen = true"
              >
                分類
              </v-btn>
            </v-card-actions>
          </div>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card class="pa-4 light-border secondary-bg rounded-xl">
          <h3 class="font-weight-bold d-flex justify-center" style="font-size: 1.5em;">訂單摘要</h3>
          <v-list two-line v-if="selectedItemsDetails.length > 0">
            <v-list-item v-for="item in selectedItemsDetails" :key="item.id">
              <div class="d-flex justify-space-between align-center w-100">
                <div>
                  <v-list-item-title 
                  class="name-ellipsis"
                  style="font-size: 1.25em;">
                  {{ item.product_name }}
                  </v-list-item-title>
                </div>
                <div>
                  <span class="font-weight-bold primary--text" style="font-size: 1.25em;">
                    ${{ (item.price * item.quantity).toFixed(2) }}
                  </span>
                </div>
              </div>
            </v-list-item>
          </v-list>
          <div v-else class="text-grey text-center py-6" style="font-size: 1.8em;">
            尚未選取商品
          </div>
          <div class="d-flex justify-space-between align-center w-100">
            <div>
              <v-list-item-title class="font-weight-medium" style="font-size: 1.25em;">
                總計:
              </v-list-item-title>
            </div>
            <div>
              <span class="font-weight-bold primary--text" style="font-size: 1.25em;">
                ${{ cartTotal.toFixed(2) }}
              </span>
            </div>
          </div>
          <div class="d-flex justify-center mt-4">
            <v-btn
              style="font-size: 1.2em;"
              color="primary"
              class="rounded-pill"
              :disabled="selectedItems.length === 0 || customerId.value"
              @click="checkoutSelected"
            >
              結帳所選商品
            </v-btn>
          </div>
        </v-card>
      </v-col>
      <v-dialog v-model="dialogOpen" max-width="500px">
        <v-card class="rounded-lg">
          <v-card-title class="text-h6 font-weight-bold primary--text">分類選擇商品</v-card-title>
          <v-card-text>
            <v-text-field
              label="分類名稱"
              v-model="newCategory"
              outlined
              dense
              color="primary"
            ></v-text-field>
            <v-text-field
              label="預算（非必填）"
              v-model="budget"
              type="number"
              outlined
              dense
              color="primary"
            ></v-text-field>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn text @click="dialogOpen = false">取消</v-btn>
            <v-btn color="primary" @click="applyCategory">確認</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
      <v-dialog v-model="editCartDialog.open" max-width="500px">
        <v-card class="rounded-lg">
          <v-card-title class="text-h6 font-weight-bold primary--text ">編輯分類</v-card-title>
          <v-card-text>
            <v-text-field
              label="分類名稱"
              v-model="editCartDialog.name"
              outlined
              dense
              color="primary"
            />
            <v-text-field
              label="預算（非必填）"
              v-model="editCartDialog.budget"
              type="number"
              outlined
              dense
              color="primary"
            />
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn text @click="editCartDialog.open = false">取消</v-btn>
            <v-btn color="error" @click="deleteCart(editCartDialog.categoryId)">刪除</v-btn>
            <v-btn color="primary" @click="saveCartEdits">儲存</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-row>
  </v-container>
</template>

<script>
import { ref, computed,reactive, onMounted } from 'vue';
import { apiBaseUrl, customerId } from '@/constants/api.js';
import axios from 'axios';
import { onBeforeRouteUpdate } from 'vue-router';
export default {
  setup() {
    const dialogOpen = ref(false);
    const newCategory = ref('');
    const budget = ref('');
    const carts = ref({ cart: null, cart_category: [] });
    const selectedItems = ref([]); 
    const categorySelections = reactive({});
    const cartNames = reactive({ '一般': '一般' });
    const cartBudgets = reactive({ '一般': null });
    const editCartDialog = reactive({
      open: false,
      name: '',
      budget: '',
      originalName: '',
      categoryId: null,
    });
    const fetchCarts = async () => {
      if (!customerId.value) return;
      try {
        const response = await axios.get(`${apiBaseUrl}/carts/`);
        carts.value = response.data || { cart: null, cart_category: [] };
        Object.assign(cartNames, { '一般': '一般' });
        Object.assign(cartBudgets, { '一般': null });
        if (Array.isArray(carts.value.cart_category)) {
          carts.value.cart_category.forEach(cart => {
            if (cart.name) {
              cartNames[cart.name] = cart.name;
              cartBudgets[cart.name] = cart.budget ? cart.budget.toString() : '';
            }
          });
        }
        Object.keys(categorySelections).forEach(category => {
          if (!groupedCart.value[category]) {
            delete categorySelections[category];
          }
        });

        const allCartItemIds = Object.values(groupedCart.value)
          .flat()
          .map(item => item.id)
          .filter(id => id !== undefined && id !== null);
        selectedItems.value = selectedItems.value.filter(id => allCartItemIds.includes(id));
      } catch (error) {
  console.error("❌ API 請求錯誤：", error);
  if (error.response) {
    console.error("📌 後端回傳的錯誤：", error.response.data);
    console.error("📌 HTTP 狀態碼：", error.response.status);
  }
  alert('無法載入購物車資料，請稍後再試');
}
    };
    const cartHeaders = [
      { title: '商品名稱', key: 'product_name', color: 'deep-purple--text' },
      { title: '價格', key: 'price' },
      { title: '數量', key: 'quantity' },
      { title: '操作', key: 'actions', sortable: false },
    ];

    const groupedCart = computed(() => {
      const groups = {};
      if (carts.value.cart && Array.isArray(carts.value.cart.items)) {
        groups['一般'] = carts.value.cart.items
          .filter(item => item && item.id !== undefined && item.id !== null)
          .reduce((acc, item) => {
            if (!acc.some(i => i.id === item.id)) {
              acc.push({
                ...item,
                cart_id: carts.value.cart.cart_id,
                category: '一般',
              });
            }
            return acc;
          }, []);
      }
      if (Array.isArray(carts.value.cart_category)) {
        carts.value.cart_category.forEach(cart => {
          if (cart.name && Array.isArray(cart.items)) {
            groups[cart.name] = cart.items
              .filter(item => item && item.id !== undefined && item.id !== null)
              .reduce((acc, item) => {
                if (!acc.some(i => i.id === item.id)) {
                  acc.push({
                    ...item,
                    cart_id: cart.category_id,
                    category: cart.name,
                  });
                }
                return acc;
              }, []);
          }
        });
      }
      return groups;
    });

    const cartTotal = computed(() => {
      return selectedItems.value.reduce((sum, itemId) => {
        const item = Object.values(groupedCart.value)
          .flat()
          .find(i => i && i.id === itemId);
        return item && item.price && item.quantity ? sum + (item.price * item.quantity) : sum;
      }, 0);
    });

    const selectedItemsDetails = computed(() => {
      return Object.values(groupedCart.value)
        .flat()
        .filter(item => item && selectedItems.value.includes(item.id) && item.id !== undefined && item.id !== null);
    });
    const openEditCartDialog = (categoryName) => {
      const cart = carts.value.cart_category.find(c => c.name === categoryName);
      if (!cart) return;
      editCartDialog.open = true;
      editCartDialog.name = cart.name;
      editCartDialog.originalName = cart.name;
      editCartDialog.budget = cart.budget ? cart.budget.toString() : '';
      editCartDialog.categoryId = cart.category_id;
    };
    const saveCartEdits = async () => {
      if (!editCartDialog.categoryId) return;
      try {
        await axios.put(`${apiBaseUrl}/carts/${editCartDialog.categoryId}`, {
          name: editCartDialog.name,
          budget: editCartDialog.budget ? parseFloat(editCartDialog.budget) : null,
        });
        editCartDialog.open = false;
        await fetchCarts();
      } catch (error) {
        alert('無法更新分類');
      }
    };
    const deleteCart = async (categoryId) => {
      if (!confirm('確定要刪除此分類嗎？刪除後商品也會一起移除！')) return;
      try {
        await axios.delete(`${apiBaseUrl}/carts/${categoryId}`);
        editCartDialog.open = false;
        await fetchCarts();
      } catch (error) {
        alert('無法刪除分類');
      }
    };
    const removeFromCart = async (cartId) => {
      if (!cartId || !customerId.value) return;
      try {
        await axios.delete(`${apiBaseUrl}/carts/${cartId}`);
        await fetchCarts();
      } catch (error) {
        alert('無法移除購物車');
      }
    };
    const removeFromCartPD = async (cartId, productId) => {
      try {
        await axios.delete(`${apiBaseUrl}/carts/${cartId}/items/${productId}`);
        await fetchCarts();
      } catch (error) {
        alert('無法移除商品');
      }
    };

    const removeSelectedItems = async () => {
      if (selectedItems.value.length === 0) {
        alert('請先選擇商品');
        return;
      }
      try {
        const validItems = selectedItems.value
          .map(itemId => Object.values(groupedCart.value).flat().find(i => i && i.id === itemId))
          .filter(item => item !== undefined && item !== null);
        for (const item of validItems) {
          await axios.delete(`${apiBaseUrl}/carts/${item.cart_id}/items/${item.product_id}`);
        }
        selectedItems.value = [];
        await fetchCarts();
      } catch (error) {
        alert( '無法移除所選商品');
      }
    };
    const checkoutSelected = async () => {
      try {
        const itemCount = selectedItems.value.length;
        const groupedItems = Object.values(groupedCart.value).flat();
        const checkoutItems = groupedItems
          .filter(item => selectedItems.value.includes(item.id))
          .map(item => ({
            product_id: item.product_id,
            quantity: item.quantity
          }));

        const payload = {
          customer_id: parseInt(customerId.value),
          items: checkoutItems
        };
        const response = await axios.post(`${apiBaseUrl}/orders`, payload);
        const data = response.data;
        await removeSelectedItems();
        alert(`成功結帳 ${itemCount} 項商品！訂單編號：${data.order_id}`);
      } catch (error) {
        alert(`結帳失敗`);
      }
    };

    const applyCategory = async () => {
      if (!newCategory.value.trim()) {
        alert('請輸入分類名稱');
        return;
      }
      try {
        let targetCart = carts.value.cart_category?.find(c => c.name === newCategory.value);
        let targetCartId;
        if (!targetCart) {
          const response = await axios.post(`${apiBaseUrl}/carts`, {
            customer_id: parseInt(customerId.value),
            name: newCategory.value,
            budget: budget.value ? parseFloat(budget.value) : null,
          });
          targetCartId = response.data.cart_id;
        } else {
          targetCartId = targetCart.category_id;
        }
        const validItems = selectedItems.value
          .map(itemId => Object.values(groupedCart.value).flat().find(i => i && i.id === itemId))
          .filter(item => item !== undefined && item !== null);
        for (const item of validItems) {
          if (item.cart_id !== targetCartId) {
            await axios.delete(`${apiBaseUrl}/carts/${item.cart_id}/items/${item.product_id}`);
            await axios.post(`${apiBaseUrl}/carts/${targetCartId}/items`, {
              product_id: item.product_id,
              quantity: item.quantity,
            });
          }
        }
        selectedItems.value = [];
        newCategory.value = '';
        budget.value = '';
        dialogOpen.value = false;
        await fetchCarts();
      } catch (error) {
        alert('無法更新分類');
      }
    };


    const isCategorySelected = (category) => {
      const itemsInCategory = groupedCart.value[category] || [];
      return itemsInCategory.length > 0 && itemsInCategory.every(item => item && selectedItems.value.includes(item.id));
    };

    const toggleCategorySelection = (category, selected) => {
      const itemsInCategory = groupedCart.value[category] || [];
      const idsInCategory = itemsInCategory
        .map(item => item.id)
        .filter(id => id !== undefined && id !== null);
      if (selected) {
        categorySelections[category] = true;
        selectedItems.value = [...new Set([...selectedItems.value, ...idsInCategory])];
      } else {
        categorySelections[category] = false;
        selectedItems.value = selectedItems.value.filter(id => !idsInCategory.includes(id));
      }
    };

    const handleDragStart = (item, event) => {
      if (!item || !item.id) return;
      event.dataTransfer.setData('text/plain', JSON.stringify({
        id: item.id,
        cart_id: item.cart_id,
        product_id: item.product_id,
        quantity: item.quantity,
      }));
      event.dataTransfer.effectAllowed = 'move';
    };

    const handleDrop = async (targetCategory, event) => {
      event.preventDefault();
      const data = JSON.parse(event.dataTransfer.getData('text/plain'));
      const { id, cart_id, product_id, quantity } = data;
      if (!id || !cart_id || !product_id) {
        console.warn('無效的拖放數據:', data);
        return;
      }
      if (groupedCart.value[targetCategory] && groupedCart.value[targetCategory][0]?.cart_id === cart_id) {
        return;
      }
      try {
        let targetCartId;
        if (targetCategory === '一般') {
          targetCartId = carts.value.cart?.cart_id;
          if (!targetCartId) {
            const response = await axios.post(`${apiBaseUrl}/carts`, {
              customer_id: parseInt(customerId.value),
              name: '一般',
            });
            targetCartId = response.data.cart_id;
          }
        } else {
          let targetCart = carts.value.cart_category.find(c => c.name === targetCategory);
          if (!targetCart) {
            const response = await axios.post(`${apiBaseUrl}/carts`, {
              customer_id: parseInt(customerId.value),
              name: targetCategory,
              budget: cartBudgets[targetCategory] ? parseFloat(cartBudgets[targetCategory]) : null,
            });
            targetCartId = response.data.cart_id;
          } else {
            targetCartId = targetCart.category_id;
          }
        }
        await axios.delete(`${apiBaseUrl}/carts/${cart_id}/items/${product_id}`);
        await axios.post(`${apiBaseUrl}/carts/${targetCartId}/items`, {
          product_id,
          quantity,
        });
        await fetchCarts();
      } catch (error) {
        alert('無法移動商品');
      }
    };

    const increaseQuantity = async (item) => {
      if (!item || !item.cart_id || !item.id) return;
      try {
        await axios.patch(`${apiBaseUrl}/carts/${item.cart_id}/items/${item.id}/quantity`, {
          quantity: item.quantity + 1,
        });
        await fetchCarts();
      } catch (error) {
        alert('無法更新數量');
      }
    };

    const decreaseQuantity = async (item) => {
      if (!item || !item.cart_id || !item.id || item.quantity <= 1) return;
      try {
        await axios.patch(`${apiBaseUrl}/carts/${item.cart_id}/items/${item.id}/quantity`, {
          quantity: item.quantity - 1,
        });
        await fetchCarts();
      } catch (error) {
        alert('無法更新數量');
      }
    };
    onMounted(() => {
      if (customerId.value) {
        fetchCarts();
      }
    });
    onBeforeRouteUpdate((to, from, next) => {
      fetchCarts();
      next();
    });
    return {
      customerId,
      carts,
      selectedItems,
      cartTotal,
      cartHeaders,
      groupedCart,
      dialogOpen,
      newCategory,
      budget,
      selectedItemsDetails,
      cartNames,
      cartBudgets,
      categorySelections,
      editCartDialog,
      removeFromCart,
      removeFromCartPD,
      openEditCartDialog,
      saveCartEdits,
      deleteCart,
      removeSelectedItems,
      checkoutSelected,
      applyCategory,
      isCategorySelected,
      toggleCategorySelection,
      handleDragStart,
      handleDrop,
      increaseQuantity,
      decreaseQuantity
    };
  },
};
</script>
<style>
.name-ellipsis {
  max-width: 95px;
  display: inline-block;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  vertical-align: middle;
}

.v-data-table > .v-table__wrapper > table > thead > tr > th {
  background: #fedada;
  color: rgb(15, 15, 15);
  font-size: 1.5em;
}

.quantity-display {
  font-size: 1.5em;
  font-weight: bold;
  color: #673ab7;
  min-width: 24px;
  text-align: center;
}

.v-btn--icon {
  background-color: #ffffff;
  border-radius: 50%;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.v-btn--icon .v-icon {
  color: #000000;
}

.text-right {
  text-align: right;
}

.light-border {
  border: none;
  box-shadow: none;
}

.quantity-control {
  display: flex;
  align-items: center;
  gap: 8px;
  background-color: #e6f0fa;
  border-radius: 20px;
  padding: 4px 8px;
  width: fit-content;
}

a[draggable="true"] {
  cursor: move;
}

div[draggable="true"]:hover,
div[dropzone] {
  transition: background-color 0.2s;
}

div[dropzone]:hover {
  background-color: #f5f5f5;
}

</style>