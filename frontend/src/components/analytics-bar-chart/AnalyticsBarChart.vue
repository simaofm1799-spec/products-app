<template>
  <v-card class="analytics-bar-chart" rounded="xl">
    <header class="analytics-bar-chart__header">
      <v-icon v-if="icon" :color="color" :icon="icon" />
      <div>
        <h2 class="analytics-bar-chart__title">{{ title }}</h2>
        <p v-if="subtitle" class="analytics-bar-chart__subtitle">{{ subtitle }}</p>
      </div>
    </header>

    <v-progress-linear v-if="loading" :color="color" height="2" indeterminate />

    <v-alert v-if="error" class="analytics-bar-chart__alert" density="compact" type="error" variant="tonal">
      {{ error }}
      <template #append>
        <v-btn size="small" variant="text" @click="$emit('retry')">{{ t('stats.retry') }}</v-btn>
      </template>
    </v-alert>

    <p v-else-if="!loading && labels.length === 0" class="analytics-bar-chart__empty">
      {{ t('stats.empty') }}
    </p>

    <div
      v-else
      class="analytics-bar-chart__scroll"
      :class="{ 'analytics-bar-chart__scroll--open': showAll }"
    >
      <div class="analytics-bar-chart__canvas" :style="{ height: chartHeight }">
        <Bar :data="chartData" :options="chartOptions" :plugins="[ChartDataLabels]" />
      </div>
    </div>

    <footer v-if="canExpand" class="analytics-bar-chart__footer">
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
            : t('stats.showAll', { count: labels.length })
        }}
      </v-btn>
    </footer>
  </v-card>
</template>

<script src="./AnalyticsBarChart.js"></script>
<style scoped src="./AnalyticsBarChart.scss"></style>
