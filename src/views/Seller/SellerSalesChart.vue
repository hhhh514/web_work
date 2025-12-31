<template>
  <v-container fluid class="white">
    <v-row class="mt-8">
      <v-col cols="12">
        <h2 class="mb-4">商品銷售比例</h2>
        <v-card elevation="2">
          <v-card-text>
            <div class="chart-container">
              <Chart
                type="pie"
                :data="salesChartData"
                :options="chartOptions"
              />
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { Chart } from 'vue-chartjs';
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  CategoryScale,
} from 'chart.js';
import axios from 'axios';
import { apiBaseUrl } from '@/constants/api';

ChartJS.register(Title, Tooltip, Legend, ArcElement, CategoryScale);

export default {
  components: {
    Chart,
  },
  setup() {
    const productsWithSales = ref([]);
    const fetchProductAndSales = async () => {
      try {
        const sellerId = localStorage.getItem('userId');
        const res = await axios.get(`${apiBaseUrl}/sales-summary/seller`);
        const salesList = res.data; 

        const result = [];

        for (const item of salesList) {
          try {
            const productRes = await axios.get(`${apiBaseUrl}/products/${item.product_id}`);
            const productInfo = productRes.data;

            result.push({
              name: productInfo.name,
              sales: item.total_quantity_sold,
            });
          } catch (err) {
            console.error(`商品 ${item.product_id} 詳細資料獲取失敗`, err);
          }
        }

        productsWithSales.value = result;
      } catch (error) {
        console.error('取得銷售總結失敗:', error);
      }
    };

    onMounted(fetchProductAndSales);

    const salesChartData = computed(() => ({
      labels: productsWithSales.value.map(p => p.name),
      datasets: [
        {
          label: '銷售數量',
          data: productsWithSales.value.map(p => p.sales),
          backgroundColor: productsWithSales.value.map(() => getRandomColor()),
          hoverOffset: 4,
        },
      ],
    }));

    const chartOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'top' },
        title: {
          display: true,
          text: '商品銷售比例（總銷售數量）',
          font: { size: 30 },
        },
        tooltip: {
          callbacks: {
            label: (context) => {
              const label = context.label || '';
              const value = context.raw || 0;
              const total = context.dataset.data.reduce((sum, val) => sum + val, 0);
              const percentage = ((value / total) * 100).toFixed(2);
              return `${label}: ${value} (${percentage}%)`;
            },
          },
        },
      },
    };

    const getRandomColor = () => {
      const letters = '0123456789ABCDEF';
      let color = '#';
      for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
      }
      return color;
    };

    return {
      salesChartData,
      chartOptions,
    };
  },
};
</script>
<style scoped>

.chart-container {
  position: relative;
  height: 400px;
  width: 100%;
  max-width: 600px; 
  margin: 0 auto; 
}
</style>