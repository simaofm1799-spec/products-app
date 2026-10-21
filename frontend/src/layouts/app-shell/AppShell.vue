<template>
  <v-app-bar flat border="b">
    <v-app-bar-nav-icon :aria-label="t('nav.toggle')" @click="toggleDrawer" />

    <router-link to="/" class="app-shell__brand">
      <v-avatar class="app-shell__logo" size="36" rounded="lg">
        <v-icon icon="mdi-cube-outline" size="22" color="white" />
      </v-avatar>
      <span class="app-shell__name">{{ APP_NAME }}</span>
    </router-link>

    <v-spacer />

    <ChatBot />

    <v-menu :close-on-content-click="false" location="bottom end" offset="8">
      <template #activator="{ props }">
        <v-btn
          v-bind="props"
          icon
          class="mr-2"
          density="comfortable"
          rounded="circle"
          variant="text"
          :aria-label="t('menu.account')"
        >
          <v-avatar size="36" color="primary">
            <v-img v-if="user?.image" :src="user.image" :alt="fullName" />
            <span v-else class="text-caption font-weight-bold">{{ initials }}</span>
          </v-avatar>
        </v-btn>
      </template>

      <v-card class="app-shell__menu" border elevation="8" min-width="288" rounded="lg">
        <div v-if="user" class="app-shell__profile">
          <v-avatar size="44" color="primary">
            <v-img v-if="user.image" :src="user.image" :alt="fullName" />
            <span v-else class="font-weight-bold">{{ initials }}</span>
          </v-avatar>
          <div class="app-shell__profile-info">
            <p class="app-shell__profile-name">{{ fullName }}</p>
            <p class="app-shell__profile-email">{{ user.email }}</p>
          </div>
        </div>
        <v-divider v-if="user" />

        <v-list class="pa-2" density="compact" nav>
          <v-list-item prepend-icon="mdi-translate" rounded="lg" :title="t('menu.language')">
            <template #append>
              <div class="app-shell__languages">
                <span
                  class="app-shell__lang"
                  :class="{ 'app-shell__lang--active': locale === offLocale }"
                >
                  {{ offLocale.toUpperCase() }}
                </span>
                <v-switch
                  class="app-shell__switch"
                  :model-value="locale === onLocale"
                  :aria-label="t('menu.language')"
                  color="primary"
                  density="compact"
                  inset
                  hide-details
                  @update:model-value="setLocale($event ? onLocale : offLocale)"
                />
                <span
                  class="app-shell__lang"
                  :class="{ 'app-shell__lang--active': locale === onLocale }"
                >
                  {{ onLocale.toUpperCase() }}
                </span>
              </div>
            </template>
          </v-list-item>

          <v-divider class="my-1" />

          <v-list-item
            base-color="error"
            prepend-icon="mdi-logout"
            rounded="lg"
            :title="t('menu.logout')"
            @click="logout"
          />
        </v-list>
      </v-card>
    </v-menu>
  </v-app-bar>

  <v-navigation-drawer v-model="drawer" :permanent="$vuetify.display.mdAndUp" width="240">
    <v-list nav class="app-shell__nav pa-3">
      <v-list-item
        v-for="item in navItems"
        :key="item.to"
        :to="item.to"
        :prepend-icon="item.icon"
        :title="item.title"
        rounded="lg"
        color="primary"
      />
    </v-list>
  </v-navigation-drawer>

  <v-main>
    <router-view v-slot="{ Component }">
      <keep-alive :include="['ProductsView']">
        <component :is="Component" />
      </keep-alive>
    </router-view>
  </v-main>
</template>

<script src="./AppShell.js"></script>
<style scoped src="./AppShell.scss"></style>
