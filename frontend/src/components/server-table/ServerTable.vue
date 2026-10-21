<template>
  <div class="server-table">
    <div class="server-table__toolbar">
      <h1 v-if="title" class="server-table__title">{{ title }}</h1>
      <slot name="leading" />
      <v-spacer />
      <slot name="actions" :filters="filters" :on-filter-change="onFilterChange" />
      <v-btn
        v-if="hasFilters"
        prepend-icon="mdi-filter-off-outline"
        size="small"
        variant="text"
        @click="clearFilters"
      >
        {{ t('filters.clear') }}
      </v-btn>
      <v-btn
        icon="mdi-table-cog"
        rounded="circle"
        variant="text"
        :aria-label="t('table.configure')"
        :title="t('table.configure')"
        @click="configOpen = true"
      />
    </div>

    <v-card rounded="xl" elevation="4">
      <v-alert
        v-if="error"
        type="error"
        variant="tonal"
        density="compact"
        class="server-table__error"
        :text="error"
      />

      <v-data-table-server
        v-model:page="page"
        v-model:items-per-page="itemsPerPage"
        v-model:sort-by="sortBy"
        class="server-table__table"
        :headers="headers"
        :items="items"
        :items-length="total"
        :loading="loading"
        :items-per-page-options="[10, 25, 50, 100]"
        item-value="id"
        hover
      >
        <template #thead="{ columns: tableColumns }">
          <thead class="server-table__filters">
            <tr>
              <td
                v-for="column in tableColumns"
                :key="column.key"
                class="server-table__filter-cell"
                :class="{
                  'v-data-table-column--fixed': column.fixed,
                  'v-data-table-column--last-fixed': column.lastFixed,
                }"
                :style="column.fixed ? { left: `${column.fixedOffset}px` } : undefined"
              >
                <ColumnFilter
                  v-if="definitions[column.key]?.filter"
                  :filter="definitions[column.key].filter"
                  :label="column.title"
                  :values="filters"
                  @change="onFilterChange"
                />
              </td>
            </tr>
          </thead>
        </template>

        <template v-for="name in cellSlots" :key="name" #[name]="slotProps">
          <slot :name="name" v-bind="slotProps" />
        </template>
      </v-data-table-server>
    </v-card>

    <TableConfigDialog
      v-model="configOpen"
      :columns="dialogColumns"
      @reset="resetColumns"
      @update:columns="setColumns"
    />
  </div>
</template>

<script src="./ServerTable.js"></script>
<style scoped src="./ServerTable.scss"></style>
