import Vue from 'vue'
import Router from 'vue-router'

Vue.use(Router)

/* Layout */
import Layout from '@/layout'

/**
 * constantRoutes
 * a base page that does not have permission requirements
 * all roles can be accessed
 */
export const constantRoutes = [
  {
    path: '/login',
    component: () => import('@/views/login/index'),
    hidden: true
  },

  {
    path: '/404',
    component: () => import('@/views/404'),
    hidden: true
  },

  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [{
      path: 'dashboard',
      name: 'Dashboard',
      component: () => import('@/views/dashboard/index'),
      meta: { title: 'Dashboard', icon: 'dashboard' }
    }]
  },

  {
    path: '/vnpy',
    component: Layout,
    redirect: '/vnpy/info',
    name: 'VNPY',
    meta: { title: '量化设置', icon: 'el-icon-money' },
    children: [
      {
        path: 'page',
        name: 'VNPYpage',
        component: () => import('@/views/vnpy/index'),
        meta: { title: '交易接口', icon: 'tree' },
        hidden: true
      },
      {
        path: 'info',
        name: 'VNPYinfo',
        component: () => import('@/views/vnpy/info'),
        meta: { title: '交易信息', icon: 'tree' }
      },
      {
        path: 'period',
        name: 'PeriodConfig',
        component: () => import('@/views/vnpy/period'),
        meta: { title: '策略配置', icon: 'tree' },
        hidden: true
      },
      {
        path: 'edit/:port/:flag',
        name: 'ConfigEditer',
        component: () => import('@/views/vnpy/config'),
        meta: { title: '配置编辑' },
        hidden: true
      }
    ]
  },

  // 404 page must be placed at the end !!!
  { path: '*', redirect: '/404', hidden: true }
]

const createRouter = () => new Router({
  // mode: 'history', // require service support
  scrollBehavior: () => ({ y: 0 }),
  routes: constantRoutes
})

const router = createRouter()

// Detail see: https://github.com/vuejs/vue-router/issues/1234#issuecomment-357941465
export function resetRouter() {
  const newRouter = createRouter()
  router.matcher = newRouter.matcher // reset router
}

export default router
