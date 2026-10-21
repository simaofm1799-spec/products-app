<template>
  <v-card class="distribution-chart" rounded="xl">
    <header class="distribution-chart__header">
      <v-icon v-if="icon" :color="color" :icon="icon" />
      <div>
        <h2 class="distribution-chart__title">{{ title }}</h2>
        <p class="distribution-chart__subtitle">
          {{ t('stats.summary', { groups: items.length, total }) }}
        </p>
      </div>
    </header>

    <v-progress-linear v-if="loading" :color="color" height="2" indeterminate />

    <v-alert v-if="error" class="distribution-chart__alert" density="compact" type="error" variant="tonal">
      {{ error }}
      <template #append>
        <v-btn size="small" variant="text" @click="$emit('retry')">{{ t('stats.retry') }}</v-btn>
      </template>
    </v-alert>

    <p v-else-if="!loading && items.length === 0" class="distribution-chart__empty">
      {{ t('stats.empty') }}
    </p>

    <div
      v-else
      class="distribution-chart__scroll"
      :class="{ 'distribution-chart__scroll--open': showAll }"
    >
      <div class="distribution-chart__canvas" :style="{ height: chartHeight }">
        <Bar :data="chartData" :options="chartOptions" :plugins="[ChartDataLabels]" />
      </div>
    </div>

    <footer v-if="canExpand" class="distribution-chart__footer">
      <v-btn
        :append-icon="showAll ? 'mdi-chevron-up' : 'mdi-chevron-down'"
        :color="color"
        size="small"
        variant="text"
        @click="showAll = !showAll"
      >
        {{
          showAll
            ? t('stats.showTop', { count: visibleCount })
            : t('stats.showAll', { count: items.length })
        }}
      </v-btn>
    </footer>
  </v-card>
</template>

<script src="./DistributionChart.js"></script>
<style scoped src="./DistributionChart.scss"></style>
