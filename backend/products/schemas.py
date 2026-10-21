from pydantic import BaseModel, ConfigDict, Field


class Dimensions(BaseModel):
    width: float | None = None
    height: float | None = None
    depth: float | None = None


class Review(BaseModel):
    rating: int | None = None
    comment: str | None = None
    date: str | None = None
    reviewerName: str | None = None


class ProductOut(BaseModel):
    """RESPONSE model. On create/update, DummyJSON only returns part of the fields."""

    id: int
    title: str | None = None
    description: str | None = None
    category: str | None = None
    price: float | None = None
    discountPercentage: float | None = None
    rating: float | None = None
    stock: int | None = None
    tags: list[str] | None = None
    brand: str | None = None
    sku: str | None = None
    weight: float | None = None
    dimensions: Dimensions | None = None
    warrantyInformation: str | None = None
    shippingInformation: str | None = None
    availabilityStatus: str | None = None
    reviews: list[Review] | None = None
    returnPolicy: str | None = None
    minimumOrderQuantity: int | None = None
    images: list[str] | None = None
    thumbnail: str | None = None


class BrandRank(BaseModel):
    """Brands are ranked by `reviewCount`. `averageRating` and `score` are null without reviews."""

    brand: str
    productCount: int
    reviewCount: int  # total reviews of the brand's products: the ranking criterion
    averageRating: float | None = None
    score: float | None = None  # complementary weighted average (formula in products/analytics.py)


class CategorySummary(BaseModel):
    category: str
    products: int
    available: int  # with stock
    outOfStock: int
    lowStock: int
    minPrice: float
    maxPrice: float
    spread: float  # maxPrice - minPrice
    stock: int  # total units


class LowStockProduct(BaseModel):
    id: int
    title: str | None = None
    category: str | None = None
    stock: int
    thumbnail: str | None = None


class AnalyticsSummary(BaseModel):
    products: int
    categories: int
    totalStock: int
    lowStock: int
    outOfStock: int
    averageRating: float
    withoutBrand: int  # left out of the brand ranking


class ProductAnalytics(BaseModel):
    summary: AnalyticsSummary
    brands: list[BrandRank]  # most reviews first
    categories: list[CategorySummary]  # biggest first
    lowStockProducts: list[LowStockProduct]  # emptiest first
    lowStockThreshold: int


class ProductFields(BaseModel):
    """Base of the REQUEST models (create/update): the editable fields.
    Unknown fields are rejected (422) so the frontend gets feedback."""

    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    category: str | None = Field(None, max_length=100)
    price: float | None = Field(None, ge=0)
    discountPercentage: float | None = Field(None, ge=0, le=100)
    stock: int | None = Field(None, ge=0)
    tags: list[str] | None = None
    brand: str | None = Field(None, max_length=100)
    sku: str | None = Field(None, max_length=100)
    weight: float | None = Field(None, ge=0)
    thumbnail: str | None = None
    images: list[str] | None = None


class ProductCreate(ProductFields):
    title: str = Field(min_length=1, max_length=200)
    price: float = Field(ge=0)


class ProductUpdate(ProductFields):
    """Partial update: only the fields sent are changed."""


