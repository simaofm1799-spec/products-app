<template>
  <v-card class="low-stock-list" rounded="xl">
    <header class="low-stock-list__header">
      <v-icon color="warning" icon="mdi-alert-outline" />
      <div>
        <h2 class="low-stock-list__title">{{ title }}</h2>
        <p v-if="subtitle" class="low-stock-list__subtitle">{{ subtitle }}</p>
      </div>
    </header>

    <v-progress-linear v-if="loading" color="warning" height="2" indeterminate />

    <v-alert v-if="error" class="low-stock-list__alert" density="compact" type="error" variant="tonal">
      {{ error }}
      <template #append>
        <v-btn size="small" variant="text" @click="$emit('retry')">{{ t('stats.retry') }}</v-btn>
      </template>
    </v-alert>

    <p v-else-if="!loading && items.length === 0" class="low-stock-list__empty">
      {{ t('products.lowStock.none') }}
    </p>

    <v-list v-else class="low-stock-list__list" density="compact">
      <v-list-item
        v-for="item in items"
        :key="item.id"
        :subtitle="item.category"
        :title="item.title"
      >
        <template #prepend>
          <v-avatar class="low-stock-list__thumbnail" rounded="lg" size="36">
            <v-img v-if="item.thumbnail" :alt="item.title" :src="item.thumbnail" />
          </v-avatar>
        </template>
        <template #append>
          <v-chip :color="stockColor(item.stock)" size="small" variant="tonal">
            {{
              item.stock === 0
                ? t('products.lowStock.out')
                : t('products.lowStock.units', { count: item.stock })
            }}
          </v-chip>
        </template>
      </v-list-item>
    </v-list>
  </v-card>
</template>

<script src="./LowStockList.js"></script>
<style scoped src="./LowStockList.scss"></style>
