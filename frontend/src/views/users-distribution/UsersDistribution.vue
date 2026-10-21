<template>
  <div class="users-distribution">
    <DistributionChart
      color="primary"
      icon="mdi-map-marker-outline"
      :error="byState.error.value"
      :items="byState.items.value"
      :loading="byState.loading.value"
      :title="t('stats.byState')"
      :total="byState.total.value"
      @retry="byState.load"
    />

    <DistributionChart
      color="secondary"
      icon="mdi-school-outline"
      :error="byUniversity.error.value"
      :items="byUniversity.items.value"
      :loading="byUniversity.loading.value"
      :title="t('stats.byUniversity')"
      :total="byUniversity.total.value"
      @retry="byUniversity.load"
    />
  </div>
</template>

<script src="./UsersDistribution.js"></script>
<style scoped src="./UsersDistribution.scss"></style>
