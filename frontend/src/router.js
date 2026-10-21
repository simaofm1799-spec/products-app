import { createRouter, createWebHistory } from 'vue-router'
import AppShell from './layouts/app-shell/AppShell.vue'
import LoginView from './views/login-view/LoginView.vue'
import ProductDetailView from './views/product-detail-view/ProductDetailView.vue'
import ProductsView from './views/products-view/ProductsView.vue'
import StockView from './views/stock-view/StockView.vue'
import UsersView from './views/users-view/UsersView.vue'
import { getRole, getToken } from './api'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { component: LoginView, path: '/login' },
    {
      // authenticated pages share the layout (header + side menu)
      children: [
        { path: '', redirect: '/products' },
        { component: ProductDetailView, path: 'product/:sku' },
        { component: ProductsView, path: 'products' },
        { component: StockView, path: 'stock' },
        { component: UsersView, path: 'users' },
      ],
      component: AppShell,
      meta: { requiresAuth: true },
      path: '/',
    },
  ],
})

router.beforeEach((route) => {
  if (route.meta.requiresAuth && !getToken()) return '/login'
  if (route.path === '/login' && getToken()) return '/products'
  if (route.meta.requiresAdmin && getRole() !== 'admin') return '/'
  return true
})

export default router
