# Produtos

## Ranking de marcas (`GET /api/products/analytics` → `brands`)

Critério do ranking: **número total de reviews** dos produtos da marca, por ordem decrescente. Empates: maior avaliação média e, depois, o nome.

Por marca: `reviewCount`, `averageRating` (média de todas as avaliações), `productCount` e `score`.

- Produtos **sem marca** ficam fora do ranking (contam em `summary.withoutBrand`).
- Uma marca cujos produtos não têm reviews aparece com `reviewCount: 0` e `averageRating` / `score` a `null`. Nada é inventado.
- `score` é um indicador **complementar**, não o critério do ranking: média ponderada em que a média global conta como `PRIOR_WEIGHT` (5) reviews extra,

  `score = (reviewCount × averageRating + 5 × médiaGlobal) / (reviewCount + 5)`

  Evita que uma marca com uma só review de 5 estrelas pareça melhor do que uma com cinquenta de 4,8.

## Tabela de produtos (`GET /api/products`)

Usa o `ServerTable` (ver [TABLES.md](TABLES.md)); colunas em `frontend/src/views/productsColumns.js`: foto, nome, marca, categoria, stock, preço e avaliação (esta última escondida por defeito). A lista é filtrada, ordenada e paginada no backend sobre o catálogo em cache (5 min).

| Parâmetro | Efeito |
|---|---|
| `limit`, `skip`, `order`, `sortBy` | paginação e ordenação (`brand`, `category`, `id`, `price`, `rating`, `stock`, `title`; sem valor vai para o fim) |
| `q` | pesquisa geral em nome, marca, categoria e SKU |
| `title`, `brand`, `category` | contém o texto (sem distinguir maiúsculas) |
| `stockMin`, `stockMax`, `priceMin`, `priceMax` | intervalos |
| `lowStock=true` | só produtos com stock baixo |

Parâmetros desconhecidos dão `422`.

## Stock baixo

Um produto tem **stock baixo** com `stock <= LOW_STOCK_THRESHOLD`, o que inclui os produtos sem stock. **Valor predefinido: 10 unidades.**

Configura-se com a variável de ambiente `LOW_STOCK_THRESHOLD` (inteiro ≥ 0; `backend/common/config.py`). O mesmo limiar é usado em:

- o filtro `lowStock` da tabela (botão "Stock baixo" por cima da tabela);
- a lista "Produtos a repor" e os KPIs (`lowStock` = entre 1 e o limiar; `outOfStock` = 0);
- o `lowStockThreshold` devolvido pela API, que o frontend mostra no botão.

A visualização de produtos disponíveis por categoria já existia ("Produtos disponíveis por categoria", gráfico de barras empilhadas).
