<template>
  <div class="container">
    <h2>{{ Tp.title }}</h2>

    <div v-if="statusData" class="status-card card" :class="{ active: statusData.has_subscription }">
      <template v-if="statusData.has_subscription">
        <div class="status-title">📋 {{ Tp.current }}</div>
        <div class="status-body">
          <span class="status-plan">{{ statusData.plan_name }}</span>
          <span class="status-badge active">{{ Tp.active }}</span>
        </div>
        <div class="status-quota">{{ Tp.remaining }}: {{ daysRemaining }} days | {{ Tp.remainingToday || 'Today remaining' }}: {{ statusData.remaining_today }}</div>
      </template>
      <template v-else-if="statusData.trial_used">
        <div class="status-title">⚠️ {{ Tp.trialUsed }}</div>
        <div class="status-body">{{ Tp.trialEnded }}</div>
      </template>
      <template v-else>
        <div class="status-title">🎉 {{ Tp.trial }}</div>
        <div class="status-body">{{ Tp.trialMsg.replace('1', trialsLeft) }}</div>
      </template>
    </div>

    <div v-if="paymentMsg" class="pay-msg" :class="paymentOk ? 'ok' : 'err'">{{ paymentMsg }}</div>

    <div class="plans-grid">
      <div v-for="p in defaultPlans" :key="p.type" :class="['card plan-card', { recommended: p.recommended, current: isCurrentPlan(p.type) }]">
        <div v-if="p.recommended" class="plan-badge">🔥 {{ Tp.recommended }}</div>
        <div v-if="isCurrentPlan(p.type)" class="plan-badge current-badge">{{ Tp.currentPlan }}</div>
        <h3>{{ planNameMap[p.type] }}</h3>
        <div class="plan-price">{{ getPlanData(p.type)?.price || '¥—' }}<span class="plan-duration">{{ getPlanData(p.type)?.duration || '' }}</span></div>
        <div class="plan-quota">{{ p.type === 'daily' ? Tp.dailyQuotaText : Tp.unlimitedText }}</div>
        <ul class="plan-features">
          <li v-for="f in planFeatures[p.type]" :key="f">✅ {{ f }}</li>
        </ul>
        <button class="btn btn-primary" style="width:100%" :disabled="payLoading===p.type||isCurrentPlan(p.type)" @click="pay(p.type)">
          {{ isCurrentPlan(p.type) ? Tp.currentPlan : payLoading===p.type ? '...' : Tp.subscribe }}
        </button>
      </div>
    </div>

    <p class="footer-note">{{ Tp.stackNote || 'Subscriptions stack: multiple purchases add days.' }}</p>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import api from '../utils/api'
import { t } from '../utils/i18n'

const route = useRoute()
const Tp = computed(() => t.value.plans)
const planNameMap = computed(() => ({ daily: Tp.value.daily, monthly: Tp.value.monthly, quarterly: Tp.value.quarterly }))
const planFeatures = computed(() => ({
  daily: Tp.value.features_daily || ['1 processing', '1 PDF'],
  monthly: Tp.value.features_monthly || ['Unlimited processing', 'Unlimited exports', 'Multi-format'],
  quarterly: Tp.value.features_quarterly || ['Unlimited processing', 'Unlimited exports', 'Multi-format', 'Wrong-answer book', 'Learning paths'],
}))
const defaultPlans = [
  { type: 'daily', recommended: false },
  { type: 'monthly', recommended: true },
  { type: 'quarterly', recommended: false },
]
const plans = ref([])

function getPlanData(type) { return plans.value.find(p => p.type === type) || defaultPlans.find(p => p.type === type) }
const statusData = ref(null)
const payLoading = ref(null); const paymentMsg = ref(''); const paymentOk = ref(false)

const trialsLeft = computed(() => statusData.value ? Math.max(0, 3 - (statusData.value.trial_count || 0)) : 3)
const daysRemaining = computed(() => { if (!statusData.value?.end_date) return 0; return Math.max(0, Math.ceil((new Date(statusData.value.end_date) - Date.now()) / 86400000)) })

async function loadStatus() { try { const { data } = await api.get('/subscription/status'); statusData.value = data } catch(e){} }
async function loadPlans() { try { const { data } = await api.get('/plans'); if (data.length) { plans.value = data.map(p => ({ type: p.plan_type, price: `¥${(p.price_cents/100).toFixed(0)}`, duration: `/${p.duration_days}d`, quota: p.daily_quota>1?'Unlimited':`${p.daily_quota}/day`, features: p.features||[] })) } } catch(e){} }

onMounted(async () => {
  await loadStatus(); loadPlans()
  if (route.query.paid==='success') { paymentOk.value=true; paymentMsg.value='Payment successful! Subscription activated.'; await loadStatus() }
  else if (route.query.paid==='cancel') { paymentOk.value=false; paymentMsg.value='Payment cancelled.' }
})

async function pay(planType) {
  payLoading.value = planType
  try { const { data } = await api.post('/payment/order',{plan_type:planType}); if(data.checkout_url){ window.location.href=data.checkout_url } else { try { await api.post('/payment/dev-activate',{plan_type:planType}); paymentOk.value=true; paymentMsg.value='Dev: Activated!'; await loadStatus() } catch(e){ paymentMsg.value='Payment not configured.'; paymentOk.value=false } } }
  catch(e) { paymentMsg.value = e.response?.data?.detail||'Order failed'; paymentOk.value=false }
  finally { payLoading.value = null }
}

function isCurrentPlan(t) { return statusData.value?.has_subscription && statusData.value?.plan_type===t && statusData.value?.status==='active' }
</script>

<style scoped>
h2 { font-size:22px;font-weight:700;color:#0f172a;margin-bottom:20px }
.status-card { margin-bottom:24px;background:#fafaf9 }
.status-card.active { background:#fffbeb;border-color:#d97706 }
.status-title { font-size:16px;color:#292524;margin-bottom:12px }
.status-body { display:flex;align-items:center;gap:12px;margin-bottom:8px;font-size:14px;color:#475569 }
.status-plan { font-size:22px;font-weight:700;color:#d97706 }
.status-badge { font-size:12px;padding:2px 12px;border-radius:12px }
.status-badge.active { background:#dcfce7;color:#166534 }
.status-quota { font-size:14px;color:#78716c }
.pay-msg { padding:12px 18px;border-radius:10px;margin-bottom:20px;font-size:14px;font-weight:500 }
.pay-msg.ok { background:#dcfce7;color:#166534 }
.pay-msg.err { background:#fee2e2;color:#991b1b }
.plans-grid { display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:24px }
.plan-card { position:relative;text-align:center;padding:36px 28px }
.plan-card.recommended { border:2px solid #d97706 }
.plan-card.current { border:2px solid #16a34a;background:#f0fdf4 }
.plan-badge { position:absolute;top:-12px;left:50%;transform:translateX(-50%);background:#d97706;color:#fff;padding:2px 24px;border-radius:12px;font-size:13px;font-weight:600 }
.plan-badge.current-badge { background:#16a34a }
.plan-card h3 { font-size:20px;font-weight:700;color:#0f172a;margin-bottom:8px }
.plan-price { font-size:40px;font-weight:800;color:#d97706;margin:16px 0 4px }
.plan-duration { font-size:14px;color:#a8a29e;font-weight:400 }
.plan-quota { font-size:13px;color:#a8a29e;margin-bottom:16px }
.plan-features { text-align:left;list-style:none;margin:20px 0 }
.plan-features li { padding:6px 0;font-size:14px;color:#292524;border-bottom:1px solid #f1f5f9 }
.plan-features li:last-child { border-bottom:none }
button[disabled] { opacity:0.5;cursor:not-allowed }
.footer-note { margin-top:40px;text-align:center;font-size:13px;color:#a8a29e }
</style>
