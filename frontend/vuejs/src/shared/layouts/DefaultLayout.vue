<!-- Default layout for public pages -->
<template>
  <BaseLayout>
    <!-- Header -->
    <HomeNavbar v-if="isHomeNav" />
    <BaseNavbar v-else />

    <!-- Main Content with Transition -->
    <main class="flex-grow">
      <transition
        name="page"
        mode="out-in"
        @before-enter="beforeEnter"
        @enter="enter"
        @after-enter="afterEnter"
        @enter-cancelled="enterCancelled"
        @before-leave="beforeLeave"
        @leave="leave"
        @after-leave="afterLeave"
        @leave-cancelled="leaveCancelled"
      >
        <slot></slot>
      </transition>
    </main>

    <!-- Footer -->
    <BaseFooter />
  </BaseLayout>
</template>

<script>
import { BaseLayout } from './index'
import { BaseNavbar, BaseFooter } from '@/shared/components'
import { HomeNavbar } from '@/apps/home/components'
import gsap from 'gsap'

export default {
  name: 'DefaultLayout',
  components: {
    BaseLayout,
    BaseNavbar,
    BaseFooter,
    HomeNavbar
  },
  props: {
    isHomeNav: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    currentYear() {
      return new Date().getFullYear()
    }
  },
  methods: {
    beforeEnter(el) {
      el.style.opacity = 0
      el.style.transform = 'translateY(10px)'
    },
    enter(el, done) {
      gsap.to(el, {
        duration: 0.3,
        opacity: 1,
        y: 0,
        onComplete: done,
        ease: 'power2.out'
      })
    },
    afterEnter(el) {
      // Cleanup if needed
    },
    enterCancelled(el) {
      // Handle cancellation if needed
    },
    beforeLeave(el) {
      el.style.opacity = 1
    },
    leave(el, done) {
      gsap.to(el, {
        duration: 0.2,
        opacity: 0,
        y: -10,
        onComplete: done,
        ease: 'power2.in'
      })
    },
    afterLeave(el) {
      // Cleanup if needed
    },
    leaveCancelled(el) {
      // Handle cancellation if needed
    }
  }
}
</script>

<style>
.page-enter-active,
.page-leave-active {
  @apply transition-all duration-300 ease-out;
}

.page-enter-from,
.page-leave-to {
  @apply opacity-0 translate-y-2;
}
</style> 