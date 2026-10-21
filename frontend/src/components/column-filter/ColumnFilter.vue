<template>
  <div class="column-filter">
    <v-select
      v-if="filter.type === 'select'"
      :model-value="valueOf(filter.param) || null"
      :items="selectItems"
      :aria-label="ariaLabel"
      :placeholder="$t('filters.placeholder')"
      clearable
      density="compact"
      hide-details
      single-line
      variant="outlined"
      @update:model-value="change(filter.param, $event)"
    />

    <v-menu
      v-else-if="filter.type === 'range'"
      :close-on-content-click="false"
      location="bottom start"
      offset="4"
    >
      <template #activator="{ props: activatorProps }">
        <v-text-field
          v-bind="activatorProps"
          :model-value="rangeText"
          :append-inner-icon="hasRange ? 'mdi-close-circle' : 'mdi-menu-down'"
          :aria-label="ariaLabel"
          :placeholder="$t('filters.placeholder')"
          density="compact"
          hide-details
          readonly
          single-line
          variant="outlined"
          @click:append-inner="onRangeIconClick"
        />
      </template>

      <v-card class="column-filter__panel" border elevation="8" rounded="lg" width="260">
        <v-range-slider
          :model-value="rangeValue"
          :aria-label="ariaLabel"
          :max="filter.max"
          :min="filter.min"
          :step="filter.step ?? 1"
          color="primary"
          hide-details
          strict
          thumb-label="always"
          @update:model-value="onRangeChange"
        />
        <div class="column-filter__actions">
          <v-btn size="x-small" variant="text" @click="clearRange">{{ $t('filters.reset') }}</v-btn>
        </div>
      </v-card>
    </v-menu>

    <v-text-field
      v-else
      :model-value="valueOf(filter.param)"
      :aria-label="ariaLabel"
      :placeholder="$t('filters.placeholder')"
      :type="filter.type === 'number' ? 'number' : 'text'"
      clearable
      density="compact"
      hide-details
      hide-spin-buttons
      single-line
      variant="outlined"
      @update:model-value="change(filter.param, $event)"
    />
  </div>
</template>

<script src="./ColumnFilter.js"></script>
<style scoped src="./ColumnFilter.scss"></style>
