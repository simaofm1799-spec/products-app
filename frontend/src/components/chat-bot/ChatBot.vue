<template>
  <v-menu v-model="open" :close-on-content-click="false" location="bottom end" offset="8">
    <template #activator="{ props }">
      <v-btn
        v-bind="props"
        icon
        class="chat-bot__trigger"
        color="error"
        density="comfortable"
        rounded="circle"
        variant="tonal"
        :aria-label="t('chat.button')"
      >
        <v-icon icon="mdi-robot-outline" />
      </v-btn>
    </template>

    <v-card class="chat-bot" border elevation="8" rounded="lg" width="360">
      <div class="chat-bot__header">
        <v-icon class="chat-bot__header-icon" icon="mdi-robot-outline" size="18" />
        <span class="chat-bot__title">{{ t('chat.title') }}</span>
        <v-spacer />
        <v-btn
          density="compact"
          icon="mdi-delete-sweep-outline"
          variant="text"
          :disabled="messages.length === 0"
          :title="t('chat.clearHistory')"
          @click="clearHistory"
        />
        <v-btn
          density="compact"
          icon="mdi-close"
          variant="text"
          @click="open = false"
        />
      </div>

      <v-divider />

      <div ref="messagesRef" class="chat-bot__messages">
        <p v-if="messages.length === 0" class="chat-bot__empty">
          {{ t('chat.empty') }}
        </p>

        <div
          v-for="(msg, index) in messages"
          :key="index"
          class="chat-bot__message"
          :class="`chat-bot__message--${msg.role}`"
        >
          <!-- eslint-disable-next-line vue/no-v-html -->
          <span v-html="renderMarkdown(msg.text)" />
        </div>

        <div v-if="loading" class="chat-bot__message chat-bot__message--assistant chat-bot__message--loading">
          <span class="chat-bot__dot" />
          <span class="chat-bot__dot" />
          <span class="chat-bot__dot" />
        </div>
      </div>

      <v-divider />

      <div class="chat-bot__input">
        <v-textarea
          v-model="input"
          :disabled="loading"
          :placeholder="t('chat.placeholder')"
          auto-grow
          density="compact"
          hide-details
          :max-rows="3"
          rows="1"
          variant="plain"
          @keydown.enter.exact.prevent="send"
        />
        <v-btn
          :disabled="loading || !input.trim()"
          color="primary"
          density="compact"
          icon="mdi-send"
          variant="text"
          @click="send"
        />
      </div>
    </v-card>
  </v-menu>
</template>

<script src="./ChatBot.js"></script>
<style scoped src="./ChatBot.scss"></style>
