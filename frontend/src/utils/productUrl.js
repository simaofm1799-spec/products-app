// Product detail URLs use the SKU, e.g. "/product/BEA-DIO-DIO-008".
// The SKU is a public catalogue code (already shown in the table and on the detail page),
// unique and URL-safe, so it resolves exactly — unlike a title slug, which strips
// apostrophes and dots and so breaks for titles like "Dior J'adore" or "MotoGP CI.H1".
// It also avoids putting the internal numeric id in user-facing URLs.

export function productPath(product) {
  return `/product/${encodeURIComponent(product.sku)}`
}
