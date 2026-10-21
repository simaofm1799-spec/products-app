# Tabelas

Todas as tabelas de dados usam o componente [`ServerTable`](../frontend/src/components/ServerTable.vue). Cada tabela nova só declara as colunas e o endpoint; o resto vem de graça:

- filtros por coluna numa linha por baixo do cabeçalho
- ordenação e paginação feitas pela API
- configuração das colunas (mostrar/esconder, reordenar a arrastar, fixar à esquerda), guardada no `localStorage`
- scroll horizontal sem barra, colunas fixas, rodapé compacto, estados de carregamento e erro

## Criar uma tabela

**1. Definir as colunas** (ex.: [`usersColumns.js`](../frontend/src/views/usersColumns.js)):

```js
export const PRODUCT_COLUMNS = [
  {
    filter: { param: 'title', type: 'text' },
    key: 'title',
    labelKey: 'products.columns.title',
    visible: true,
    width: 240,
  },
  {
    filter: { max: 2000, min: 0, param: 'price', type: 'range' },
    key: 'price',
    labelKey: 'products.columns.price',
    visible: true,
    width: 150,
  },
]
```

| Campo | Descrição |
|---|---|
| `key` | chave do dado; é também o valor enviado em `sortBy` (`address.state` para campos aninhados) |
| `labelKey` | chave i18n do título da coluna (acrescentar em `pt.json` e `en.json`) |
| `width` | em pixéis; obrigatório, o Vuetify usa-o para posicionar as colunas fixas |
| `visible` | visível por defeito (o utilizador altera na configuração da tabela) |
| `sortable` | `false` para desativar a ordenação (por defeito é ordenável) |
| `value` | função opcional `(item) => valor mostrado` |
| `filter` | filtro opcional da coluna (ver abaixo) |

**Tipos de filtro** (`param` é o parâmetro de query da API):

| `type` | Controlo | Envia |
|---|---|---|
| `text` | caixa de texto | `?<param>=texto` (contém, sem distinguir maiúsculas) |
| `select` | lista; `options` e, opcionalmente, `labelGroup` (traduções em `<labelGroup>.<opção>`) | `?<param>=opção` |
| `number` | número exato | `?<param>=5` |
| `range` | campo único com *slider* de duas pontas; `min`, `max`, `step?` | `?<param>Min=..&<param>Max=..` (uma ponta no extremo = sem limite) |

**2. Usar o componente** (ex.: [`UsersView.vue`](../frontend/src/views/UsersView.vue)):

```vue
<ServerTable
  endpoint="/api/products"
  storage-key="products-table-columns"
  :columns="PRODUCT_COLUMNS"
  :title="t('products.title')"
>
  <!-- opcional: células personalizadas, um slot `item.<key>` por coluna -->
  <template #item.price="{ item }">{{ item.price }} €</template>
</ServerTable>
```

- `storage-key` tem de ser único por tabela (é onde se guarda a configuração das colunas).
- O slot `actions` junta botões ao lado do título.

## O que a API tem de fazer

`GET <endpoint>` recebe `limit`, `skip`, `sortBy`, `order` (`asc`/`desc`) e os parâmetros dos filtros, e responde:

```json
{ "items": [ ... ], "limit": 10, "skip": 0, "total": 208 }
```

Cada item deve ter um `id`. Se a API receber um parâmetro que não conhece, deve responder `422` (como a dos utilizadores). Um exemplo completo está em [`backend/users/query.py`](../backend/users/query.py): modelo de query com os filtros, funções de filtrar e ordenar, e o serviço que lê a lista uma vez e a guarda alguns minutos.

## Onde está cada coisa

| Ficheiro | Papel |
|---|---|
| `components/ServerTable.vue` | a tabela completa (cabeçalho, linha de filtros, rodapé, estilos) |
| `composables/useServerTable.js` | estado e lógica: paginação, ordenação, filtros, pedidos à API |
| `composables/useColumnConfig.js` | configuração das colunas e persistência |
| `components/ColumnFilter.vue` | o controlo de cada filtro |
| `components/TableConfigDialog.vue` | a janela de configuração das colunas |
| `utils/columnConfig.js` | funções puras (ordem, fixar, esconder) |
