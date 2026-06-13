<script setup>
import { onMounted, ref } from "vue";
import { Calendar, ChatDotRound, Check, Goods, Location } from "@element-plus/icons-vue";
import {
  cancelOrder,
  cancelEventRegistration,
  checkinEvent,
  createOrder,
  createRecordFromEvent,
  fetchCollection,
  fetchOrders,
  fetchUserEvents,
  payOrder,
  registerEvent
} from "../services/api";

const props = defineProps({
  currentUserId: { type: String, default: "demo_user" }
});

const emit = defineEmits(["action", "open-chat", "record-created"]);
const active = ref("events");
const events = ref([]);
const equipment = ref([]);
const history = ref([]);
const orders = ref([]);
const registrationMap = ref({});

async function loadData() {
  const [eventData, equipmentData, userEvents, orderData] = await Promise.all([
    fetchCollection("/api/events?status=open", null),
    fetchCollection("/api/equipment", null),
    fetchUserEvents(props.currentUserId),
    fetchOrders(props.currentUserId)
  ]);
  events.value = Array.isArray(eventData) ? eventData : [];
  equipment.value = Array.isArray(equipmentData) ? equipmentData : [];
  history.value = Array.isArray(userEvents) ? userEvents : [];
  orders.value = Array.isArray(orderData) ? orderData : [];
  registrationMap.value = Object.fromEntries(history.value.map((item) => [item.id, item.registration]));
}

onMounted(loadData);

async function joinEvent(event) {
  const result = await registerEvent(event.id, props.currentUserId);
  if (!result) return emit("action", "报名失败，请稍后重试");
  if (result.status !== "already_registered") event.current_participants += 1;
  await loadData();
  emit("action", result.status === "already_registered" ? "你已经报名过该活动" : "报名成功，已自动加入活动群");
}

async function cancelEvent(event) {
  const result = await cancelEventRegistration(event.id, props.currentUserId);
  if (!result) return emit("action", "取消报名失败");
  await loadData();
  emit("action", "已取消报名");
}

async function checkin(event) {
  const result = await checkinEvent(event.id, props.currentUserId);
  if (!result) return emit("action", "请先报名后再签到");
  await loadData();
  active.value = "history";
  emit("action", "签到成功，本次活动已进入你的履历");
}

async function makeRecord(event) {
  const record = await createRecordFromEvent(event.id, props.currentUserId);
  if (!record) return emit("action", "签到后才能生成活动出钓记录");
  emit("record-created", record);
  await loadData();
  emit("action", "已从活动生成出钓记录，可到个人主页继续补充鱼获");
}

async function buyEquipment(item) {
  const order = await createOrder(props.currentUserId, item.id);
  if (!order) return emit("action", "订单创建失败");
  await loadData();
  active.value = "orders";
  emit("action", "订单已创建，可在订单页模拟支付");
}

async function pay(order) {
  const result = await payOrder(order.id, props.currentUserId);
  if (!result) return emit("action", "模拟支付失败");
  await loadData();
  emit("action", "模拟支付成功，未接入真实资金交易");
}

async function cancelPurchase(order) {
  const result = await cancelOrder(order.id, props.currentUserId);
  if (!result) return emit("action", "取消订单失败");
  await loadData();
  emit("action", "订单已取消");
}

function registration(event) {
  return registrationMap.value[event.id] || null;
}

function formatEventTime(value) {
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? value
    : new Intl.DateTimeFormat("zh-CN", { month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", hour12: false }).format(date);
}
</script>

<template>
  <section class="services-page">
    <header class="services-hero">
      <span>从一次出钓，连接下一次服务</span>
      <h2>参与活动，也能买到被真实鱼获验证的装备</h2>
      <p>报名、签到、群聊与活动履历形成闭环；装备展示真实使用次数和代表战绩。</p>
    </header>

    <nav class="services-switch services-switch-four" aria-label="活动与装备">
      <button type="button" :class="{ active: active === 'events' }" @click="active = 'events'"><el-icon><Calendar /></el-icon>活动</button>
      <button type="button" :class="{ active: active === 'history' }" @click="active = 'history'"><el-icon><Check /></el-icon>履历</button>
      <button type="button" :class="{ active: active === 'equipment' }" @click="active = 'equipment'"><el-icon><Goods /></el-icon>装备</button>
      <button type="button" :class="{ active: active === 'orders' }" @click="active = 'orders'">订单</button>
    </nav>

    <section v-if="active === 'events'" class="services-list">
      <article v-for="event in events" :key="event.id" class="service-card">
        <div class="service-card-top">
          <div><span class="service-kicker">{{ event.fee ? `¥${event.fee}/人` : "免费活动" }}</span><h3>{{ event.title }}</h3></div>
          <b>{{ event.current_participants }}/{{ event.max_participants }}人</b>
        </div>
        <p>{{ event.description }}</p>
        <div class="service-meta"><span><el-icon><Location /></el-icon>{{ event.water_name }}</span><span>{{ formatEventTime(event.event_time) }}</span></div>
        <div class="service-actions service-actions-wrap">
          <button v-if="!registration(event) || registration(event).status === 'cancelled'" class="btn" type="button" @click="joinEvent(event)">立即参与</button>
          <button v-else-if="registration(event).status === 'registered'" class="btn" type="button" @click="checkin(event)">现场签到</button>
          <button v-else class="btn" type="button" disabled>已签到</button>
          <button v-if="registration(event)?.status === 'registered'" class="btn secondary" type="button" @click="cancelEvent(event)">取消报名</button>
          <button class="btn secondary" type="button" @click="emit('open-chat')"><el-icon><ChatDotRound /></el-icon>活动群</button>
        </div>
      </article>
    </section>

    <section v-else-if="active === 'history'" class="services-list">
      <article v-if="!history.length" class="service-card"><h3>还没有活动履历</h3><p>报名并签到一次活动后，这里会沉淀你的同城钓鱼经历。</p></article>
      <article v-for="event in history" :key="event.id" class="service-card history-card">
        <div class="service-card-top"><div><span class="service-kicker">{{ event.registration.status === 'checked_in' ? '已签到履历' : event.registration.status === 'cancelled' ? '已取消' : '待签到' }}</span><h3>{{ event.title }}</h3></div></div>
        <p>{{ formatEventTime(event.event_time) }} · {{ event.water_name }}</p>
        <div class="service-actions">
          <button v-if="event.registration.status === 'checked_in' && !event.registration.record_id" class="btn" type="button" @click="makeRecord(event)">生成出钓记录</button>
          <button v-else-if="event.registration.record_id" class="btn" disabled>已生成记录</button>
          <button class="btn secondary" type="button" @click="emit('open-chat')">回看活动群</button>
        </div>
      </article>
    </section>

    <section v-else-if="active === 'equipment'" class="services-list">
      <article v-for="item in equipment" :key="item.id" class="service-card equipment-card">
        <div class="equipment-visual"><el-icon><Goods /></el-icon></div>
        <div class="equipment-copy">
          <span class="service-kicker">{{ item.category }} · {{ item.merchant_name || "平台精选" }}</span>
          <h3>{{ item.name }}</h3><p>{{ item.description }}</p>
          <div class="equipment-proof"><span>真实使用 {{ item.usage_count }} 次</span><span>代表战绩 {{ item.best_catch }}</span></div>
          <div class="service-actions"><strong>¥{{ item.price }}</strong><button class="btn" type="button" @click="buyEquipment(item)">生成演示订单</button></div>
        </div>
      </article>
    </section>

    <section v-else class="services-list">
      <article v-if="!orders.length" class="service-card"><h3>还没有装备订单</h3><p>从装备服务选择商品后，会生成一笔不涉及真实支付的演示订单。</p></article>
      <article v-for="order in orders" :key="order.id" class="service-card order-card">
        <div class="service-card-top">
          <div><span class="service-kicker">{{ order.status === 'paid_demo' ? '模拟支付成功' : order.status === 'cancelled' ? '已取消' : '待模拟支付' }}</span><h3>{{ order.equipment_name }}</h3></div>
          <strong>¥{{ order.total_amount }}</strong>
        </div>
        <p>{{ order.merchant_name || "平台精选商家" }} · 数量 {{ order.quantity }}</p>
        <div v-if="order.status === 'pending_payment'" class="service-actions">
          <button class="btn" type="button" @click="pay(order)">模拟支付</button>
          <button class="btn secondary" type="button" @click="cancelPurchase(order)">取消订单</button>
        </div>
      </article>
    </section>
  </section>
</template>
