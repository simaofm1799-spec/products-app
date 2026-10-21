<template>
  <v-container class="products-view">
    <header class="products-view__header">
      <h1 class="products-view__title">{{ t('products.title') }}</h1>
      <p class="products-view__subtitle">{{ t('products.subtitle') }}</p>
    </header>

    <v-alert
      v-if="error"
      class="products-view__alert"
      type="error"
      variant="tonal"
    >
      {{ error }}
      <template #append>
        <v-btn size="small" variant="text" @click="load">{{ t('stats.retry') }}</v-btn>
      </template>
    </v-alert>

    <section class="products-view__kpis">
      <KpiCard
        v-for="kpi in kpis"
        :key="kpi.label"
        :color="kpi.color"
        :hint="kpi.hint"
        :icon="kpi.icon"
        :label="kpi.label"
        :value="loading && !analytics ? '…' : kpi.value"
      />
    </section>

    <section class="products-view__grid">
      <AnalyticsBarChart
        color="primary"
        icon="mdi-trophy-outline"
        :datasets="brandsChart.datasets"
        :format-label="(value) => n(value)"
        :format-tooltip="brandTooltip"
        :labels="brandsChart.labels"
        :loading="loading"
        :subtitle="t('products.brands.subtitle', { brands: brands.length, excluded: summary?.withoutBrand ?? 0 })"
        :title="t('products.brands.title')"
      />

      <AnalyticsBarChart
        color="success"
        icon="mdi-check-circle-outline"
        stacked
        :datasets="availabilityChart.datasets"
        :format-label="(value) => (value > 0 ? String(value) : '')"
        :format-tooltip="availabilityTooltip"
        :labels="availabilityChart.labels"
        :loading="loading"
        :subtitle="t('products.availability.subtitle')"
        :title="t('products.availability.title')"
      />

      <AnalyticsBarChart
        color="secondary"
        icon="mdi-currency-usd"
        show-axis
        :datasets="priceChart.datasets"
        :format-label="(value) => `${money(value[1] - value[0])} diff`"
        :format-tooltip="priceTooltip"
        :labels="priceChart.labels"
        :loading="loading"
        :subtitle="t('products.prices.subtitle')"
        :title="t('products.prices.title')"
      />

      <AnalyticsBarChart
        color="info"
        icon="mdi-warehouse"
        :datasets="stockChart.datasets"
        :format-label="(value) => n(value)"
        :format-tooltip="stockTooltip"
        :labels="stockChart.labels"
        :loading="loading"
        :subtitle="t('products.stock.subtitle')"
        :title="t('products.stock.title')"
      />
    </section>

    <ServerTable
      class="products-view__table"
      endpoint="/api/products"
      storage-key="products-table-columns"
      :columns="PRODUCT_COLUMNS"
      :title="t('products.table.title')"
    >
      <template #actions="{ filters, onFilterChange }">
        <v-btn
          color="warning"
          prepend-icon="mdi-alert-outline"
          size="small"
          :variant="filters.lowStock ? 'flat' : 'tonal'"
          @click="onFilterChange('lowStock', filters.lowStock ? '' : 'true')"
        >
          {{ lowStockLabel }}
        </v-btn>
      </template>

      <template #item.image="{ item }">
        <v-avatar size="28">
          <v-img :alt="item.title" :src="item.thumbnail" />
        </v-avatar>
      </template>

      <template #item.title="{ item }">
        <router-link
          class="products-view__product-link"
          :to="productPath(item)"
        >
          {{ item.title }}
        </router-link>
      </template>

      <template #item.category="{ item }">{{ categoryName(item.category ?? '') }}</template>

      <template #item.price="{ item }">{{ money(item.price) }}</template>

      <template #item.availabilityStatus="{ item }">
        <v-chip
          v-if="item.availabilityStatus"
          :color="availabilityColor(item.availabilityStatus)"
          size="small"
          variant="tonal"
        >
          {{ item.availabilityStatus }}
        </v-chip>
        <span v-else>—</span>
      </template>
    </ServerTable>
  </v-container>
</template>

<script src="./ProductsView.js"></script>
<style scoped src="./ProductsView.scss"></style>
