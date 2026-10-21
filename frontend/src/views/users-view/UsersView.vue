<template>
  <v-container class="users-view">
    <header class="users-view__header">
      <h1 class="users-view__title">{{ t('users.title') }}</h1>
      <p class="users-view__subtitle">{{ t('users.subtitle') }}</p>
    </header>

    <ServerTable
      v-if="tab === 'table'"
      endpoint="/api/users"
      storage-key="users-table-columns"
      :columns="USER_COLUMNS"
    >
      <template #leading>
        <UsersTabs v-model="tab" />
      </template>

      <template #item.image="{ item }">
        <v-avatar size="28" color="surface-variant">
          <v-img :src="item.image" :alt="item.firstName" />
        </v-avatar>
      </template>

      <template #item.gender="{ item }">
        {{ label('gender', item.gender) }}
      </template>

      <template #item.role="{ item }">
        <v-chip
          v-if="item.role"
          size="small"
          variant="tonal"
          :color="ROLE_COLORS[item.role] ?? 'secondary'"
        >
          {{ label('roles', item.role) }}
        </v-chip>
      </template>
    </ServerTable>

    <template v-else>
      <div class="users-view__toolbar">
        <UsersTabs v-model="tab" />
      </div>
      <UsersDistribution />
    </template>
  </v-container>
</template>

<script src="./UsersView.js"></script>
<style scoped src="./UsersView.scss"></style>
