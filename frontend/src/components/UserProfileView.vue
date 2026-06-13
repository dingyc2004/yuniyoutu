<script setup>
import { computed, ref } from "vue";
import { ArrowLeft, Check, Plus, User } from "@element-plus/icons-vue";
import { addFriend, followUser, unfollowUser } from "../services/api";

const props = defineProps({
  profile: { type: Object, required: true },
  currentUserId: { type: String, default: "demo_user" },
  posts: { type: Array, default: () => [] }
});

const emit = defineEmits(["back", "action", "open-post"]);

const socialStorageKey = `fishman_social_${props.currentUserId}`;
const storedSocial = readStoredSocial();
const following = ref(storedSocial[props.profile.id]?.following ?? Boolean(props.profile.following));
const friendStatus = ref(storedSocial[props.profile.id]?.friendStatus || props.profile.friend_status || "none");
const busy = ref(false);

const userPosts = computed(() => props.posts.filter((post) =>
  post.user_id === props.profile.id || post.author === props.profile.nickname
));

const stats = computed(() => ({
  posts: userPosts.value.length,
  likes: userPosts.value.reduce((sum, post) => sum + Number(post.likes || 0), 0),
  catches: 18 + (props.profile.level || 1) * 7
}));

function readStoredSocial() {
  try {
    return JSON.parse(window.localStorage.getItem(socialStorageKey) || "{}");
  } catch {
    return {};
  }
}

function persistSocial() {
  const social = readStoredSocial();
  social[props.profile.id] = {
    following: following.value,
    friendStatus: friendStatus.value
  };
  window.localStorage.setItem(socialStorageKey, JSON.stringify(social));
}

async function toggleFollow() {
  if (busy.value) return;
  busy.value = true;
  try {
    if (following.value) {
      await unfollowUser(props.profile.id, props.currentUserId);
      following.value = false;
      emit("action", `已取消关注 ${props.profile.nickname}`);
    } else {
      await followUser(props.profile.id, props.currentUserId);
      following.value = true;
      emit("action", `已关注 ${props.profile.nickname}`);
    }
    persistSocial();
  } catch {
    following.value = !following.value;
    persistSocial();
    emit("action", `${following.value ? "已关注" : "已取消关注"} ${props.profile.nickname}（本地演示）`);
  } finally {
    busy.value = false;
  }
}

async function requestFriend() {
  if (busy.value || friendStatus.value !== "none") return;
  busy.value = true;
  try {
    const result = await addFriend(props.profile.id, props.currentUserId);
    friendStatus.value = result?.status || "pending";
    persistSocial();
    emit("action", `已向 ${props.profile.nickname} 发送好友申请`);
  } catch {
    friendStatus.value = "pending";
    persistSocial();
    emit("action", `已向 ${props.profile.nickname} 发送好友申请（本地演示）`);
  } finally {
    busy.value = false;
  }
}
</script>

<template>
  <section class="other-profile-page">
    <header class="other-profile-nav">
      <button type="button" aria-label="返回社区" @click="emit('back')"><el-icon><ArrowLeft /></el-icon></button>
      <strong>钓友主页</strong>
      <span></span>
    </header>

    <section class="other-profile-hero">
      <div class="other-profile-cover"></div>
      <div class="other-profile-main">
        <el-avatar :size="72">{{ profile.avatar || profile.nickname?.slice(0, 1) }}</el-avatar>
        <div>
          <span>LV.{{ profile.level || 1 }} · {{ profile.city || "武汉市" }}</span>
          <h2>{{ profile.nickname }}</h2>
          <p>{{ profile.bio || "正在探索更多水域。" }}</p>
        </div>
      </div>
      <div class="other-profile-actions">
        <button type="button" class="profile-follow-action" :class="{ active: following }" @click="toggleFollow">
          <el-icon><component :is="following ? Check : Plus" /></el-icon>
          {{ following ? "已关注" : "关注" }}
        </button>
        <button type="button" class="profile-friend-action" :disabled="friendStatus !== 'none'" @click="requestFriend">
          <el-icon><User /></el-icon>
          {{ friendStatus === "accepted" ? "已是好友" : friendStatus === "pending" ? "申请已发送" : "添加好友" }}
        </button>
      </div>
      <div class="other-profile-stats">
        <div><strong>{{ stats.posts }}</strong><span>动态</span></div>
        <div><strong>{{ stats.likes }}</strong><span>获赞</span></div>
        <div><strong>{{ stats.catches }}</strong><span>鱼获</span></div>
      </div>
    </section>

    <section class="other-profile-preferences">
      <span v-for="item in [...(profile.preferred_methods || []), ...(profile.preferred_species || [])]" :key="item">{{ item }}</span>
    </section>

    <section class="other-profile-feed">
      <div class="other-profile-section-head">
        <h3>他的动态</h3>
        <span>{{ userPosts.length }} 篇</span>
      </div>
      <button v-for="post in userPosts" :key="post.id" type="button" class="other-profile-post" @click="emit('open-post', post)">
        <div :class="['other-profile-post-cover', `cover-${post.coverTone || 'green'}`]"></div>
        <div>
          <strong>{{ post.title }}</strong>
          <p>{{ post.meta || post.postType }}</p>
          <span>{{ post.likes || 0 }} 赞 · {{ post.comments || 0 }} 评论</span>
        </div>
      </button>
      <div v-if="!userPosts.length" class="other-profile-empty">这位钓友还没有公开动态</div>
    </section>
  </section>
</template>
