<template>
  <v-dialog
    :model-value="modelValue"
    max-width="480"
    scrollable
    @update:model-value="emit('update:modelValue', $event)"
  >
    <v-card class="table-config-dialog" rounded="xl">
      <v-card-title class="d-flex align-center ga-2 pt-5">
        <v-icon icon="mdi-table-cog" />
        {{ t('table.title') }}
      </v-card-title>
      <v-card-subtitle class="text-wrap">{{ t('table.subtitle') }}</v-card-subtitle>

      <v-card-text>
        <section v-for="group in groups" :key="group.id" class="table-config-dialog__group">
          <h3 class="table-config-dialog__group-title">{{ t(group.titleKey) }}</h3>

          <div
            v-for="item in group.items"
            :key="item.key"
            class="table-config-dialog__row"
            :class="{
              'table-config-dialog__row--dragging': draggedKey === item.key,
              'table-config-dialog__row--over': overKey === item.key && draggedKey !== item.key,
            }"
            draggable="true"
            @dragend="onDragEnd"
            @dragover="onDragOver($event, item)"
            @dragstart="onDragStart($event, item)"
            @drop.prevent="onDrop(item)"
          >
            <v-icon class="table-config-dialog__handle" icon="mdi-drag" />

            <v-switch
              class="table-config-dialog__switch"
              :model-value="item.visible"
              :label="item.label"
              :disabled="isLastVisible(item)"
              color="primary"
              density="compact"
              inset
              hide-details
              @update:model-value="update(setVisible(columns, item.key, $event))"
            />

            <v-btn
              class="table-config-dialog__pin"
              :icon="item.pinned ? 'mdi-pin' : 'mdi-pin-outline'"
              :color="item.pinned ? 'primary' : undefined"
              :aria-label="item.pinned ? t('table.unpin') : t('table.pin')"
              :aria-pressed="Boolean(item.pinned)"
              :title="item.pinned ? t('table.unpin') : t('table.pin')"
              density="compact"
              rounded="circle"
              size="small"
              variant="text"
              @click="update(setPinned(columns, item.key, !item.pinned))"
            />
          </div>
        </section>
      </v-card-text>

      <v-card-actions class="px-6 pb-4">
        <v-btn prepend-icon="mdi-restore" variant="text" @click="emit('reset')">
          {{ t('table.reset') }}
        </v-btn>
        <v-spacer />
        <v-btn color="primary" variant="flat" @click="emit('update:modelValue', false)">
          {{ t('table.close') }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script src="./TableConfigDialog.js"></script>
<style scoped src="./TableConfigDialog.scss"></style>
