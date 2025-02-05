import BuilderDashboard from '../views/BuilderDashboard.vue'
import BuilderWorkspace from '../views/BuilderWorkspace.vue'
import Dashboard from '../views/Dashboard.vue'

export const routes = [
  {
    path: '/dashboard',
    name: 'dashboard',
    component: Dashboard,
    meta: {
      requiresAuth: true,
      title: 'Dashboard'
    }
  },
  {
    path: '/builder/dashboard',
    name: 'builder-dashboard',
    component: BuilderDashboard,
    meta: {
      requiresAuth: true,
      title: 'Builder Dashboard'
    }
  },
  {
    path: '/builder/project/:projectId',
    name: 'builder-workspace',
    component: BuilderWorkspace,
    props: route => ({ 
      projectId: route.params.projectId ? route.params.projectId.toString() : null 
    }),
    meta: {
      requiresAuth: true,
      title: 'Project Workspace'
    },
    beforeEnter: (to, from, next) => {
      // Ensure projectId is present
      if (!to.params.projectId) {
        next({ name: 'builder-dashboard' })
      } else {
        next()
      }
    }
  }
]

export default routes 