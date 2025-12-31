<template>
  <v-container fluid class="white">
    <v-row>
      <v-col cols="12">
        <h1 class="text-center">商品列表</h1>
        <v-text-field
          v-model="search"
          label="搜索商品"
          prepend-icon="mdi-magnify"
          clearable
          class="mb-4"
          style="max-width: 55vw; margin: 0 auto;"
        ></v-text-field>
      </v-col>
    </v-row>
    <v-row v-if="items.length" class="grid-spacing">
      <v-col
        v-for="(item, index) in filteredItems"
        :key="item.id"
        cols="4"
        sm="4"
        md="3"
      >
        <v-card
          class="mx-auto square-card"
          elevation="2"
          @mouseover="showDetails[index] = true"
          @mouseleave="showDetails[index] = false"
          @click="item.stock > 0 && goToProduct(item.id)"
          :class="{ 'disabled-card': item.stock === 0 }"
        >
          <v-img
            :src="item.image_url"
            height="100%"
            width="100%"
            cover
            class="card-image"
          ></v-img>
          <v-expand-transition>
            <div v-if="showDetails[index]" class="card-details">
              <v-card-text class="text-center">
                <v-tooltip bottom>
                  <template v-slot:activator="{ on, attrs }">
                    <h3 v-bind="attrs" v-on="on">{{ item.displayName }}</h3>
                  </template>
                  <span>{{ item.name }}</span>
                </v-tooltip>
                <p>價格: ${{ item.price }}</p>
                <p>庫存: {{ item.stock > 0 ? item.stock + ' 件' : '無庫存' }}</p>
              </v-card-text>
            </div>
          </v-expand-transition>
        </v-card>
      </v-col>
    </v-row>
    <v-row v-else-if="loading" class="text-center">
      <v-col>
        <v-progress-circular indeterminate color="primary"></v-progress-circular>
      </v-col>
    </v-row>
    <v-row v-else class="text-center">
      <v-col>
        <p>無商品可顯示</p>
      </v-col>
    </v-row>
    <v-row v-if="!loading && hasMore" class="text-center">
      <v-col>
        <v-btn @click="loadMore">載入更多</v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { ref, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import { apiBaseUrl} from '@/constants/api.js';
import axios from 'axios';
export default {
  name: 'Home',
  setup() {
    const router = useRouter();
    const headers = ref([
      { text: '商品名稱', value: 'name' },
      { text: '價格', value: 'price' },
      { text: '庫存', value: 'stock' },
    ]);
    const items = ref([]);
    const search = ref('');
    const loading = ref(false);
    const showDetails = ref({});
    const start = ref(0);
    const end = ref(20);
    const total = ref(0);
    const pageSize = 20;
    
    const isSearching = ref(false);
    const filteredItems = computed(() => {
      if (!Array.isArray(items.value)) {
        console.warn('items.value 不是陣列:', items.value);
        return [];
      }
      const itemsWithShortName = items.value.map(item => ({
        ...item,
        displayName: item.name.length > 30 ? item.name.slice(0, 27) + '...' : item.name
      }));
      if (!search.value) return itemsWithShortName;
      return itemsWithShortName.filter(item =>
        Object.values(item).some(value =>
          value.toString().toLowerCase().includes(search.value.toLowerCase())
        )
      );
    });

    const hasMore = computed(() => {
      return end.value < total.value;
    });

    const fetchProducts = async (startIndex, endIndex) => {
      try {
        loading.value = true;
        const response = await axios.get(`${apiBaseUrl}/products`, {
          params: { start: startIndex, end: endIndex },
        });
        if (!response.data || typeof response.data !== 'object') {
          console.error('API 回傳無效 JSON:', response.data);
          items.value = startIndex === 0 ? [] : items.value;
          total.value = 0;
          return;
        }
        const { products, total: totalCount } = response.data;
        if (!Array.isArray(products)) {
          console.error('API 回傳的 products 不是陣列:', products);
          items.value = startIndex === 0 ? [] : items.value;
          total.value = 0;
          return;
        }
        if (startIndex === 0) {
          items.value = products;
        } else {
          items.value = [...items.value, ...products];
        }
        total.value = Number(totalCount) || 0;
      } catch (error) {
        console.error('Error fetching products:', error);
        items.value = startIndex === 0 ? [] : items.value;
      } finally {
        loading.value = false;
      }
    };

    fetchProducts(start.value, end.value);

    const loadMore = () => {
      if (!hasMore.value || loading.value) return;
      start.value = end.value;
      end.value += pageSize;
      if (isSearching.value && search.value) {
        fetchSearchResults(search.value, start.value, end.value);
      } else {
        fetchProducts(start.value, end.value);
      }
    };

    const handleScroll = () => {
      const bottomOfWindow =
        window.innerHeight + window.scrollY >=
        document.documentElement.scrollHeight - 100;
      if (bottomOfWindow && !loading.value && hasMore.value) {
        loadMore();
      }
    };

    window.addEventListener('scroll', handleScroll);

    const cleanup = () => {
      window.removeEventListener('scroll', handleScroll);
    };

    const goToProduct = (id) => {
      router.push({ name: 'ProductDetail', params: { id } });
    };
    const fetchSearchResults = async (keyword, startIndex, endIndex) => {
      try {
        loading.value = true;
        const response = await axios.get(`${apiBaseUrl}/products/search`, {
          params: {
            keyword,
            start: startIndex,
            end: endIndex
          },
        });
        const { products, total: totalCount } = response.data;
        if (!Array.isArray(products)) throw new Error("搜尋結果無效");

        if (startIndex === 0) {
          items.value = products;
        } else {
          items.value = [...items.value, ...products];
        }
        total.value = Number(totalCount) || 0;
      } catch (error) {
        console.error('搜尋 API 發生錯誤:', error);
        if (startIndex === 0) items.value = [];
      } finally {
        loading.value = false;
      }
    };
    watch(search, (newKeyword) => {
      start.value = 0;
      end.value = pageSize;
      if (newKeyword) {
        isSearching.value = true;
        fetchSearchResults(newKeyword, start.value, end.value);
      } else {
        isSearching.value = false;
        fetchProducts(start.value, end.value);
      }
    });
    return {
      headers,
      filteredItems,
      search,
      loading,
      items,
      showDetails,
      goToProduct,
      loadMore,
      hasMore,
      cleanup,
    };
  },
  unmounted() {
    this.cleanup();
  },
};
</script>

<style scoped>
.square-card {
  width: 15vw;
  height: 15vh;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.card-image {
  object-fit: cover;
}

.card-details {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
  font-size: 0.9rem;
  text-align: center;
}

.card-details h3 {
  white-space: normal;
  word-break: break-word;
  max-height: 60%;
  overflow: hidden;
}

.square-card:hover .card-details {
  opacity: 1;
}

.disabled-card {
  opacity: 0.6;
  cursor: not-allowed;
}

.grid-spacing {
  margin: -16px;
}

.grid-spacing > .v-col {
  padding: 16px;
}

.text-center {
  padding: 5vh 0 0 0;
}
</style>