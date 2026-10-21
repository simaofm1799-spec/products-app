<template>
  <v-card class="kpi-card" rounded="xl">
    <v-avatar class="kpi-card__icon" :color="color" rounded="lg" size="44" variant="tonal">
      <v-icon :icon="icon" />
    </v-avatar>
    <div class="kpi-card__body">
      <p class="kpi-card__label">{{ label }}</p>
      <p class="kpi-card__value">{{ value }}</p>
      <p v-if="hint" class="kpi-card__hint">{{ hint }}</p>
    </div>
  </v-card>
</template>

<script src="./KpiCard.js"></script>
<style scoped src="./KpiCard.scss"></style>
