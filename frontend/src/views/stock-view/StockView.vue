<template>
  <v-container class="stock-view">
    <header class="stock-view__header">
      <div>
        <h1 class="stock-view__title">{{ t('stock.title') }}</h1>
        <p class="stock-view__subtitle">{{ t('stock.subtitle') }}</p>
      </div>

      <div class="stock-view__header-actions">
        <v-select
          v-if="isAdmin && warehouses.length > 1"
          v-model="selectedWarehouseId"
          class="stock-view__warehouse-select"
          :items="warehouseItems"
          density="compact"
          hide-details
          prepend-inner-icon="mdi-warehouse"
          variant="outlined"
          @update:model-value="onWarehouseChange"
        />
        <v-chip
          v-else-if="selectedWarehouse"
          class="stock-view__warehouse-chip"
          prepend-icon="mdi-warehouse"
          variant="tonal"
        >
          {{ selectedWarehouse.name }} — {{ selectedWarehouse.city }}, {{ selectedWarehouse.state }}
        </v-chip>

        <v-btn
          :disabled="!selectedWarehouseId"
          :loading="autoSuggestLoading"
          prepend-icon="mdi-auto-fix"
          variant="tonal"
          @click="autoSuggest"
        >
          {{ t('stock.autoSuggest') }}
        </v-btn>

        <v-btn
          color="primary"
          :disabled="orderCount === 0"
          prepend-icon="mdi-cart-check"
          variant="flat"
          @click="confirmDialog = true"
        >
          {{ t('stock.confirmOrder', { count: orderCount }) }}
        </v-btn>
      </div>
    </header>

    <v-alert
      v-if="autoSuggestError"
      class="mb-4"
      closable
      density="compact"
      type="error"
      variant="tonal"
      @click:close="autoSuggestError = ''"
    >
      {{ autoSuggestError }}
    </v-alert>

    <v-alert
      v-if="noOrderNeeded"
      class="mb-4"
      closable
      density="compact"
      type="info"
      variant="tonal"
      @click:close="noOrderNeeded = false"
    >
      {{ t('stock.noOrderNeeded') }}
    </v-alert>

    <v-progress-linear v-if="warehousesLoading" color="primary" height="2" indeterminate />

    <v-alert
      v-else-if="warehousesError"
      density="compact"
      type="error"
      variant="tonal"
    >
      {{ warehousesError }}
    </v-alert>

    <v-alert
      v-else-if="!selectedWarehouseId"
      density="compact"
      type="info"
      variant="tonal"
    >
      {{ t('stock.noWarehouse') }}
    </v-alert>

    <v-progress-linear v-else-if="!filtersReady" color="primary" height="2" indeterminate />

    <ServerTable
      v-else
      :key="tableKey"
      class="stock-view__table"
      :endpoint="tableEndpoint"
      storage-key="stock-table-columns"
      :columns="stockColumns"
      :title="t('stock.tableTitle')"
    >
      <template #item.title="{ item }">
        <router-link
          class="stock-view__product-link"
          :to="productPath(item)"
        >
          {{ item.title }}
        </router-link>
      </template>

      <template #item.image="{ item }">
        <v-avatar size="28">
          <v-img :alt="item.title" :src="item.thumbnail" />
        </v-avatar>
      </template>

      <template #item.stock="{ item }">
        <div class="stock-view__stock-cell">
          <span
            class="stock-view__stock-value"
            :class="`stock-view__stock-value--${stockChipColor(item.availabilityStatus)}`"
          >
            {{ item.stock ?? '—' }}
          </span>
          <v-btn
            density="compact"
            icon="mdi-pencil-outline"
            size="x-small"
            variant="text"
            @click.stop="openEditStock(item)"
          />
        </div>
      </template>

      <template #item.availabilityStatus="{ item }">
        <v-chip
          v-if="item.availabilityStatus"
          :color="stockChipColor(item.availabilityStatus)"
          size="small"
          variant="tonal"
        >
          {{ item.availabilityStatus }}
        </v-chip>
        <span v-else>—</span>
      </template>

      <template #item.price="{ item }">{{ money(item.price) }}</template>

      <template #item.order="{ item }">
        <v-text-field
          class="stock-view__order-input"
          :class="{ 'stock-view__order-input--active': getOrderQty(item.id) > 0 }"
          density="compact"
          hide-details
          min="0"
          :model-value="getOrderQty(item.id) || null"
          :placeholder="'0'"
          type="number"
          variant="outlined"
          @update:model-value="val => setOrderQty(item, val)"
        />
      </template>
    </ServerTable>

    <!-- ── Edit stock dialog ─────────────────────────────────────────────── -->
    <v-dialog v-model="editDialog" max-width="400">
      <v-card class="stock-view__edit-card" rounded="xl">
        <v-card-title class="stock-view__edit-title">{{ t('stock.editStock') }}</v-card-title>
        <v-card-subtitle v-if="editItem" class="stock-view__edit-product">
          {{ editItem.title }}
        </v-card-subtitle>
        <v-card-text class="stock-view__edit-body">
          <v-alert
            v-if="editError"
            class="stock-view__edit-error"
            density="compact"
            type="error"
            variant="tonal"
          >
            {{ editError }}
          </v-alert>
          <v-text-field
            v-model.number="editStock"
            :label="t('fields.stock')"
            autofocus
            hide-details="auto"
            min="0"
            type="number"
            variant="outlined"
            @keydown.enter="saveStock"
          />
        </v-card-text>
        <v-card-actions class="stock-view__edit-actions">
          <v-spacer />
          <v-btn variant="text" @click="editDialog = false">{{ t('table.close') }}</v-btn>
          <v-btn color="primary" :loading="editLoading" variant="flat" @click="saveStock">
            {{ t('stock.save') }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- ── Confirm order dialog ──────────────────────────────────────────── -->
    <v-dialog v-model="confirmDialog" max-width="760" scrollable>
      <v-card class="stock-view__confirm-card" rounded="xl">
        <div class="stock-view__confirm-header">
          <div>
            <h2 class="stock-view__confirm-title">{{ t('stock.confirmTitle') }}</h2>
            <p v-if="selectedWarehouse" class="stock-view__confirm-warehouse">
              {{ selectedWarehouse.name }} — {{ selectedWarehouse.city }}, {{ selectedWarehouse.state }}
            </p>
          </div>
          <v-chip color="primary" variant="tonal">
            {{ t('stock.confirmCount', { count: orderCount }) }}
          </v-chip>
        </div>

        <v-alert
          v-if="confirmError"
          class="mx-4 mb-3"
          density="compact"
          type="error"
          variant="tonal"
        >
          {{ confirmError }}
        </v-alert>

        <v-table class="stock-view__confirm-table" density="compact" fixed-header height="400">
          <thead>
            <tr>
              <th>{{ t('products.columns.title') }}</th>
              <th class="text-right">{{ t('products.columns.stock') }}</th>
              <th class="text-right">{{ t('stock.columns.order') }}</th>
              <th class="text-right">{{ t('stock.newStock') }}</th>
              <th />
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in orderItems" :key="item.id">
              <td>
                <div class="stock-view__confirm-product">
                  <v-avatar rounded="sm" size="24">
                    <v-img :alt="item.title" :src="item.thumbnail" />
                  </v-avatar>
                  {{ item.title }}
                </div>
              </td>
              <td class="text-right">{{ n(item.currentStock) }}</td>
              <td class="text-right">
                <span class="stock-view__confirm-qty">+{{ n(item.qty) }}</span>
              </td>
              <td class="text-right">
                <strong>{{ n(item.newStock) }}</strong>
              </td>
              <td class="text-right">
                <v-btn
                  density="compact"
                  icon="mdi-close"
                  size="x-small"
                  variant="text"
                  @click="removeOrder(item.id)"
                />
              </td>
            </tr>
          </tbody>
        </v-table>

        <div class="stock-view__confirm-totals">
          <span>{{ t('stock.totalOrder') }}</span>
          <strong>{{ n(orderItems.reduce((s, i) => s + i.qty, 0)) }} {{ t('stock.units') }}</strong>
        </div>

        <v-card-actions class="stock-view__confirm-actions">
          <v-spacer />
          <v-btn variant="text" @click="confirmDialog = false">{{ t('table.close') }}</v-btn>
          <v-btn
            color="primary"
            :loading="confirmLoading"
            prepend-icon="mdi-check"
            variant="flat"
            @click="confirmOrder"
          >
            {{ t('stock.confirmOrder', { count: orderCount }) }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="snackbar" color="success" :timeout="3000">
      {{ t('stock.saveSuccess') }}
    </v-snackbar>
  </v-container>
</template>

<script src="./StockView.js"></script>
<style scoped src="./StockView.scss"></style>
