import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/Home.vue';
import Login from '../views/Login.vue';
import Register from '../views/Register.vue';
import main from '../views/Main.vue';
import ProductDetail from '../views/ProductDetail.vue';
import NotFound from '../views/NotFound.vue';

import Cart from '../views/Customer/Cart.vue';
import CustomerProfile from '../views/Customer/Profile.vue';
import PurchaseHistory from '../views/Customer/PurchaseHistory.vue';
import Wishlist from '../views/Customer/Wishlist.vue';

import SellerProfile from '../views/Seller/SellerProfile.vue';
import SellerOverview from '../views/Seller/SellerOverview.vue';
import SellerSalesChart from '../views/Seller/SellerSalesChart.vue';

const routes = [
  {
    path: '/',
    redirect: '/main',
  },
  {
    path: '/main',
    name: 'Main',
    component: main,
  },
  {
    path: '/home',
    name: 'Home',
    component: Home,
  },
  {
    path: '/customers',
    children: [
      {
        path: 'cart',
        name: 'Cart',
        component: Cart,
      },
      {
        path: 'profile',
        name: 'CustomerProfile',
        component: CustomerProfile,
      },
      {
        path: 'purchase-history',
        name: 'PurchaseHistory',
        component: PurchaseHistory,
      },
      {
        path: 'wishlist',
        name: 'Wishlist',
        component: Wishlist,
      },
    ],
  },
  {
    path: '/seller',
    children: [
      {
        path: 'profile',
        name: 'SellerProfile',
        component: SellerProfile,
      },
      {
        path: 'overview',
        name: 'SellerOverview',
        component: SellerOverview,
      },
      {
        path: 'sales-chart',
        name: 'SellerSalesChart',
        component: SellerSalesChart,
      },
    ],
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
  },
  {
    path: '/product/:id',
    name: 'ProductDetail',
    component: ProductDetail,
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true';
  const role = localStorage.getItem('role');
  if (!isAuthenticated && to.name !== 'Login' && to.name !== 'Register' && to.name !== 'Main') {
    return next('/login');
  }

  const token = localStorage.getItem('token');
  if (isAuthenticated && token && (to.name === 'Login' || to.name === 'Register')) {
    if (role === 'seller') {
      return next('/home');
    } else if (role === 'customer') {
      return next('/home');
    } else {
      return next('/main');
    }
  }

  if (to.path.startsWith('/seller') && role !== 'seller') {
    return next('/main');
  }

  if (to.path.startsWith('/customers') && role !== 'customer') {
    return next('/main');
  }

  return next();
});

export default router;
