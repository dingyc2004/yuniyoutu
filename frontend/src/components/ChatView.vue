<script setup>
import { computed, nextTick, ref } from "vue";
import { ArrowLeft, Search } from "@element-plus/icons-vue";
import { addFriend, fetchDirectMessages, followUser, sendDirectMessage, sendGroupMessage } from "../services/api";

const props = defineProps({
  groups: { type: Array, default: () => [] },
  messages: { type: Array, default: () => [] },
  contacts: { type: Array, default: () => [] },
  currentUserId: { type: String, default: "demo_user" }
});

const emit = defineEmits(["action", "back"]);

const fallbackContacts = [
  { id: "user_jiangfeng", nickname: "江风路亚", avatar: "江", city: "武汉", online: true, following: true, friend_status: "accepted", lastMsg: "周六东湖入口见", lastTime: "刚刚" },
  { id: "user_aming", nickname: "不空军的阿明", avatar: "明", city: "武汉", online: true, following: false, friend_status: "none", lastMsg: "新手调漂局还有名额", lastTime: "5分钟前" },
  { id: "user_tanchang", nickname: "钓场探路客", avatar: "探", city: "武汉", online: false, following: false, friend_status: "none", lastMsg: "更新了南湖钓场收费", lastTime: "1小时前" }
];

const activeContact = ref(null);
const activeGroup = ref(null);
const newMessage = ref("");
const chatList = ref(null);
const searchText = ref("");
const directMessages = ref([]);
const groupMessages = ref([...props.messages]);

const contactSource = computed(() => props.contacts.length ? props.contacts : fallbackContacts);
const filteredContacts = computed(() => {
  const text = searchText.value.trim();
  if (!text) return contactSource.value;
  return contactSource.value.filter((contact) => contactName(contact).includes(text) || contact.city?.includes(text));
});
const chatMessages = computed(() => {
  if (activeGroup.value) return groupMessages.value.filter((message) => message.group_id === activeGroup.value.id);
  if (activeContact.value) return directMessages.value;
  return [];
});

function contactName(contact) {
  return contact?.nickname || contact?.name || "钓友";
}

function scrollToBottom() {
  nextTick(() => {
    if (chatList.value) chatList.value.scrollTop = chatList.value.scrollHeight;
  });
}

function openGroup(group) {
  activeGroup.value = group;
  activeContact.value = null;
  scrollToBottom();
}

async function openContact(contact) {
  activeContact.value = contact;
  activeGroup.value = null;
  directMessages.value = await fetchDirectMessages(props.currentUserId, contact.id);
  scrollToBottom();
}

function backToList() {
  activeContact.value = null;
  activeGroup.value = null;
}

async function sendMessage() {
  const content = newMessage.value.trim();
  if (!content) return;
  if (activeGroup.value) {
    const message = await sendGroupMessage(activeGroup.value.id, props.currentUserId, content);
    if (message) groupMessages.value.push(message);
  } else if (activeContact.value) {
    const message = await sendDirectMessage(activeContact.value.id, props.currentUserId, content);
    if (message) directMessages.value.push(message);
  }
  newMessage.value = "";
  scrollToBottom();
}

async function handleFollow(contact) {
  await followUser(contact.id, props.currentUserId);
  contact.following = true;
  emit("action", `已关注 ${contactName(contact)}`);
}

async function handleFriend(contact) {
  await addFriend(contact.id, props.currentUserId);
  contact.friend_status = "accepted";
  emit("action", `已添加 ${contactName(contact)} 为好友`);
}

function formatTime(value) {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "" : date.toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit" });
}

function isMyMessage(message) {
  return message.user_id === props.currentUserId || message.sender_id === props.currentUserId || message.author === "我";
}
</script>

<template>
  <section class="chat-page">
    <div v-if="!activeContact && !activeGroup" class="chat-panel">
      <header class="chat-header">
        <button class="icon-btn" type="button" @click="emit('back')"><el-icon><ArrowLeft /></el-icon></button>
        <div class="chat-header-info"><strong>消息与钓友</strong><span>关注、加好友、私聊和活动群</span></div>
      </header>
      <div class="chat-search"><el-icon><Search /></el-icon><input v-model="searchText" type="search" placeholder="搜索钓友..." /></div>

      <div v-if="groups.length" class="chat-section">
        <h3 class="chat-section-title">活动群聊 · {{ messages.length }} 条新动态</h3>
        <button v-for="group in groups" :key="group.id" class="chat-contact" type="button" @click="openGroup(group)">
          <span class="chat-avatar group-avatar">群</span>
          <div class="chat-contact-info"><strong>{{ group.name }}</strong><span>{{ group.member_count || 0 }}人 · 点击查看活动讨论</span></div>
          <span class="chat-unread">{{ messages.length }}</span>
        </button>
      </div>

      <div class="chat-section">
        <h3 class="chat-section-title">发现同城钓友</h3>
        <button v-for="contact in filteredContacts" :key="contact.id" class="chat-contact" type="button" @click="openContact(contact)">
          <span class="chat-avatar" :class="{ online: contact.online }">{{ contact.avatar || contactName(contact)[0] }}</span>
          <div class="chat-contact-info"><strong>{{ contactName(contact) }}</strong><span>{{ contact.lastMsg || contact.bio || "查看资料并开始聊天" }}</span></div>
          <span class="chat-time">{{ contact.lastTime || (contact.friend_status === 'accepted' ? '好友' : '新钓友') }}</span>
        </button>
      </div>
    </div>

    <div v-else class="chat-panel">
      <header class="chat-header">
        <button class="icon-btn" type="button" @click="backToList"><el-icon><ArrowLeft /></el-icon></button>
        <div class="chat-header-info">
          <strong>{{ activeGroup?.name || contactName(activeContact) }}</strong>
          <span>{{ activeGroup ? `${activeGroup.member_count || 0}人 · 活动群` : activeContact?.city }}</span>
        </div>
      </header>

      <div v-if="activeContact" class="social-actions">
        <button type="button" :disabled="activeContact.following" @click="handleFollow(activeContact)">{{ activeContact.following ? "已关注" : "关注" }}</button>
        <button type="button" :disabled="activeContact.friend_status === 'accepted'" @click="handleFriend(activeContact)">{{ activeContact.friend_status === "accepted" ? "已是好友" : "加好友" }}</button>
      </div>

      <div ref="chatList" class="chat-message-list">
        <div v-if="chatMessages.length" class="chat-msgs">
          <div v-for="message in chatMessages" :key="message.id" :class="['chat-bubble-wrap', isMyMessage(message) ? 'mine' : 'other']">
            <span v-if="!isMyMessage(message)" class="chat-bubble-avatar">{{ (message.author || contactName(activeContact))[0] }}</span>
            <div class="chat-bubble">
              <span v-if="!isMyMessage(message) && message.author" class="chat-bubble-name">{{ message.author }}</span>
              <p>{{ message.content }}</p>
              <small>{{ formatTime(message.created_at) }}</small>
            </div>
          </div>
        </div>
        <div v-else class="chat-empty"><p>还没有聊天记录</p><span class="meta">发送第一条消息开始交流</span></div>
      </div>

      <form class="chat-input-bar" @submit.prevent="sendMessage">
        <input v-model="newMessage" placeholder="聊聊鱼情、装备或约钓计划..." />
        <button type="submit" class="chat-send-btn" :disabled="!newMessage.trim()">发送</button>
      </form>
    </div>
  </section>
</template>
