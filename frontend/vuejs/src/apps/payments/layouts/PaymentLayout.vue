<!-- Payment layout with shared components -->
<template>
  <div class="payment-layout min-h-screen bg-dark-900">
    <!-- Navigation -->
    <PaymentNavbar />

    <!-- Main Content -->
    <main class="min-h-screen py-16">
      <router-view></router-view>
    </main>

    <!-- Footer -->
    <PaymentFooter />
  </div>
</template>

<script>
import PaymentNavbar from '../components/layout/PaymentNavbar.vue'
import PaymentFooter from '../components/layout/PaymentFooter.vue'

export default {
  name: 'PaymentLayout',
  components: {
    PaymentNavbar,
    PaymentFooter
  },
  mounted() {
    // Load Stripe.js if not already loaded
    if (!window.Stripe && !document.querySelector('script[src*="stripe.com"]')) {
      const script = document.createElement('script')
      script.src = 'https://js.stripe.com/v3/'
      script.async = true
      script.defer = true
      script.addEventListener('load', () => {
        console.log('Stripe.js loaded successfully')
      })
      script.addEventListener('error', (error) => {
        console.error('Failed to load Stripe.js:', error)
      })
      document.head.appendChild(script)
    }
  }
}
</script>

<style scoped>
.payment-layout {
  background: radial-gradient(
    circle at top right,
    rgba(0, 255, 204, 0.05),
    transparent 50%
  );
}
</style> 