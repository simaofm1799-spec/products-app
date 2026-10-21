<template>
  <v-btn-toggle
    class="users-tabs"
    color="primary"
    density="comfortable"
    mandatory
    rounded="pill"
    variant="text"
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <v-btn class="users-tabs__button" prepend-icon="mdi-table" value="table">
      {{ t('users.tabs.table') }}
    </v-btn>
    <v-btn class="users-tabs__button" prepend-icon="mdi-chart-bar" value="distribution">
      {{ t('users.tabs.distribution') }}
    </v-btn>
  </v-btn-toggle>
</template>

<script src="./UsersTabs.js"></script>
<style scoped src="./UsersTabs.scss"></style>
