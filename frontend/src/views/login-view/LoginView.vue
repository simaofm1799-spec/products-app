<template>
  <v-main>
    <div class="login-view">
      <span class="login-view__blob login-view__blob--pink" />
      <span class="login-view__blob login-view__blob--purple" />
      <span class="login-view__blob login-view__blob--cyan" />

      <v-card
        class="login-view__card"
        max-width="420"
        width="100%"
        rounded="xl"
        elevation="12"
      >
        <div class="login-view__header">
          <v-avatar class="login-view__logo" size="64" rounded="lg">
            <v-icon icon="mdi-cube-outline" size="36" color="white" />
          </v-avatar>
          <h1 class="login-view__title">{{ t('login.title') }}</h1>
          <p class="login-view__subtitle">{{ t('login.subtitle') }}</p>
        </div>

        <v-form @submit.prevent="submit">
          <v-text-field
            v-model="username"
            :label="t('login.username')"
            prepend-inner-icon="mdi-account-outline"
            autocomplete="username"
            required
          />
          <v-text-field
            v-model="password"
            :label="t('login.password')"
            prepend-inner-icon="mdi-lock-outline"
            :type="showPassword ? 'text' : 'password'"
            :append-inner-icon="showPassword ? 'mdi-eye-off-outline' : 'mdi-eye-outline'"
            autocomplete="current-password"
            required
            @click:append-inner="showPassword = !showPassword"
          />

          <v-expand-transition>
            <v-alert
              v-if="error"
              class="login-view__alert"
              type="error"
              variant="tonal"
              density="compact"
              :text="error"
            />
          </v-expand-transition>

          <v-btn
            type="submit"
            block
            size="large"
            class="login-view__submit"
            :loading="loading"
            :disabled="loading"
          >
            {{ t('login.submit') }}
          </v-btn>
        </v-form>

        <i18n-t
          keypath="login.testHint"
          tag="p"
          class="login-view__hint"
        >
          <template #user><code class="login-view__code">emilys</code></template>
          <template #pass><code class="login-view__code">emilyspass</code></template>
        </i18n-t>
      </v-card>
    </div>
  </v-main>
</template>

<script src="./LoginView.js"></script>
<style scoped src="./LoginView.scss"></style>
