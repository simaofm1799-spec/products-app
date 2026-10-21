<template>
  <v-container class="product-detail">
    <div class="product-detail__nav">
      <v-btn
        class="product-detail__back"
        icon="mdi-arrow-left"
        size="small"
        variant="text"
        :aria-label="t('product.back')"
        :title="t('product.back')"
        @click="goBack"
      />
      <v-breadcrumbs class="product-detail__breadcrumb" :items="breadcrumbItems">
        <template #divider>
          <v-icon icon="mdi-chevron-right" size="small" />
        </template>
      </v-breadcrumbs>
    </div>

    <!-- Loading -->
    <v-row v-if="loading">
      <v-col cols="12" md="5">
        <v-skeleton-loader height="420" type="image" />
      </v-col>
      <v-col cols="12" md="7">
        <v-skeleton-loader type="article" />
      </v-col>
    </v-row>

    <!-- Error -->
    <v-alert v-else-if="error" type="error" variant="tonal">
      {{ error }}
      <template #append>
        <v-btn size="small" variant="text" @click="load">{{ t('stats.retry') }}</v-btn>
      </template>
    </v-alert>

    <!-- Product -->
    <template v-else-if="product">
      <!-- Main: carousel + info -->
      <v-card class="product-detail__main-card" elevation="2" rounded="xl">
        <v-row class="product-detail__main-row">
          <!-- Carousel -->
          <v-col class="product-detail__carousel-col" cols="12" md="5">
            <v-carousel
              class="product-detail__carousel"
              hide-delimiter-background
              :show-arrows="images.length > 1 ? 'hover' : false"
              :height="400"
            >
              <v-carousel-item
                v-for="(img, index) in images"
                :key="index"
                cover
                :src="img"
              />
            </v-carousel>
          </v-col>

          <!-- Info -->
          <v-col class="product-detail__info" cols="12" md="7">
            <!-- Category + tags -->
            <div class="product-detail__chips">
              <v-chip color="secondary" size="small" variant="tonal">
                {{ categoryLabel(product.category) }}
              </v-chip>
              <v-chip
                v-for="tag in (product.tags ?? [])"
                :key="tag"
                size="small"
                variant="outlined"
              >
                {{ tag }}
              </v-chip>
            </div>

            <!-- Title -->
            <h1 class="product-detail__title">{{ product.title }}</h1>

            <!-- Brand -->
            <p v-if="product.brand" class="product-detail__brand">{{ product.brand }}</p>

            <!-- Rating -->
            <div v-if="product.rating" class="product-detail__rating">
              <v-rating
                :model-value="product.rating"
                color="warning"
                density="compact"
                half-increments
                readonly
                size="small"
              />
              <span class="product-detail__rating-value">{{ product.rating }} / 5</span>
              <span v-if="product.reviews?.length" class="product-detail__rating-count">
                ({{ product.reviews.length }} {{ t('product.reviews') }})
              </span>
            </div>

            <!-- Price -->
            <div class="product-detail__price-block">
              <div class="product-detail__price-row">
                <span class="product-detail__price">{{ money(discountedPrice) }}</span>
                <template v-if="product.discountPercentage">
                  <span class="product-detail__original-price">{{ money(product.price) }}</span>
                  <v-chip color="error" size="small" variant="flat">
                    -{{ Math.round(product.discountPercentage) }}%
                  </v-chip>
                </template>
              </div>
            </div>

            <!-- Availability -->
            <div class="product-detail__availability">
              <v-chip :color="availabilityColor" size="small" variant="tonal">
                {{ product.availabilityStatus }}
              </v-chip>
              <span v-if="product.stock != null" class="product-detail__stock">
                {{ t('product.stock', { count: n(product.stock) }) }}
              </span>
            </div>

            <!-- Description -->
            <p v-if="product.description" class="product-detail__description">
              {{ product.description }}
            </p>

            <!-- SKU + MOQ -->
            <div class="product-detail__meta">
              <div v-if="product.sku" class="product-detail__meta-item">
                <span class="product-detail__meta-label">{{ t('product.sku') }}</span>
                <span class="product-detail__meta-value">{{ product.sku }}</span>
              </div>
              <div v-if="product.minimumOrderQuantity" class="product-detail__meta-item">
                <span class="product-detail__meta-label">{{ t('product.minOrder') }}</span>
                <span class="product-detail__meta-value">{{ product.minimumOrderQuantity }}</span>
              </div>
            </div>
          </v-col>
        </v-row>
      </v-card>

      <!-- Details -->
      <v-card class="product-detail__card" elevation="2" rounded="xl">
        <v-card-title class="product-detail__card-title">
          <v-icon class="product-detail__card-title-icon" icon="mdi-information-outline" size="small" />
          {{ t('product.details') }}
        </v-card-title>
        <v-table class="product-detail__details-table" density="comfortable">
          <tbody>
            <tr v-if="product.weight">
              <td class="product-detail__detail-label">
                <v-icon class="product-detail__detail-icon" icon="mdi-weight" size="x-small" />
                {{ t('product.weight') }}
              </td>
              <td>{{ product.weight }} kg</td>
            </tr>
            <tr v-if="product.dimensions">
              <td class="product-detail__detail-label">
                <v-icon class="product-detail__detail-icon" icon="mdi-cube-scan" size="x-small" />
                {{ t('product.dimensions') }}
              </td>
              <td>
                {{ product.dimensions.width }} × {{ product.dimensions.height }} × {{ product.dimensions.depth }} cm
              </td>
            </tr>
            <tr v-if="product.warrantyInformation">
              <td class="product-detail__detail-label">
                <v-icon class="product-detail__detail-icon" icon="mdi-shield-check-outline" size="x-small" />
                {{ t('product.warranty') }}
              </td>
              <td>{{ product.warrantyInformation }}</td>
            </tr>
            <tr v-if="product.shippingInformation">
              <td class="product-detail__detail-label">
                <v-icon class="product-detail__detail-icon" icon="mdi-truck-outline" size="x-small" />
                {{ t('product.shipping') }}
              </td>
              <td>{{ product.shippingInformation }}</td>
            </tr>
            <tr v-if="product.returnPolicy">
              <td class="product-detail__detail-label">
                <v-icon class="product-detail__detail-icon" icon="mdi-arrow-u-left-top" size="x-small" />
                {{ t('product.policy') }}
              </td>
              <td>{{ product.returnPolicy }}</td>
            </tr>
          </tbody>
        </v-table>
      </v-card>

      <!-- Reviews -->
      <template v-if="product.reviews?.length">
        <div class="product-detail__reviews-header">
          <v-icon class="product-detail__reviews-icon" icon="mdi-star-outline" />
          <span class="product-detail__reviews-title">{{ t('product.reviews') }}</span>
          <span class="product-detail__reviews-count">({{ product.reviews.length }})</span>
        </div>
        <div class="product-detail__reviews-grid">
          <v-card
            v-for="(review, index) in product.reviews"
            :key="index"
            class="product-detail__review-card"
            elevation="1"
            rounded="xl"
          >
            <v-card-text class="product-detail__review-body">
              <div class="product-detail__review-header">
                <span class="product-detail__review-name">{{ review.reviewerName }}</span>
                <span class="product-detail__review-date">{{ reviewDate(review.date) }}</span>
              </div>
              <v-rating
                :model-value="review.rating"
                color="warning"
                density="compact"
                half-increments
                readonly
                size="small"
              />
              <p class="product-detail__review-comment">{{ review.comment }}</p>
            </v-card-text>
          </v-card>
        </div>
      </template>
    </template>
  </v-container>
</template>

<script src="./ProductDetailView.js"></script>
<style scoped src="./ProductDetailView.scss"></style>
