# Convenções de código

Regras a seguir em todo o código novo do projeto.

## 1. Nomes de variáveis

As variáveis têm **no mínimo 3 caracteres**. O nome deve dizer o que a variável guarda.

```js
// ❌
const u = users[0]
items.map((i) => i.id)

// ✅
const user = users[0]
items.map((item) => item.id)
```

**Exceção:** nomes que vêm de bibliotecas e que usamos tal como são (ex.: `t` e `te` do `useI18n`).

## 2. CSS segue a norma BEM

Formato: `bloco__elemento--modificador`, tudo em minúsculas, com palavras separadas por hífen.

- **Bloco**: o componente em si. Usa o nome do componente (`UsersView` → `.users-view`).
- **Elemento** (`__`): parte do bloco, sem existir fora dele (`.users-view__title`).
- **Modificador** (`--`): variação de um bloco ou elemento (`.users-view__row--active`).
- Não encadeies elementos: `.card__header__title` ❌ → `.card__title` ✅.
- Estiliza por classe. Evita seletores de etiqueta (`div`, `p`) e de `id`.
- Para alterar componentes do Vuetify, usa `:deep()` a partir da classe do bloco.

```vue
<template>
  <div class="login-card">
    <h1 class="login-card__title">...</h1>
    <v-btn class="login-card__submit login-card__submit--loading" />
  </div>
</template>

<style scoped>
.login-card { ... }
.login-card__title { ... }
.login-card__submit--loading { ... }
</style>
```

## 3. Chaves de objetos por ordem alfabética

As chaves de um objeto ficam por ordem alfabética. A exceção é o `id`, que vem sempre primeiro.

```js
// ❌
const user = { role: 'admin', id: 1, age: 29, firstName: 'Emily' }

// ✅
const user = { id: 1, age: 29, firstName: 'Emily', role: 'admin' }
```

Aplica-se a objetos literais (JS, JSON, dicionários em Python), incluindo as opções passadas a funções e os ficheiros de tradução. Não se aplica à declaração dos campos de classes e modelos (ex.: schemas do Pydantic), que seguem um agrupamento lógico.

## 4. Um único `return`, no fim da função

Cada função tem **um e só um `return`**, e ele está na última linha. Sem *early returns* nem *guard clauses* que devolvam.

- Em vez de sair a meio, guarda o resultado numa variável e devolve-a no fim.
- Lançar erros (`throw` / `raise`) é permitido em qualquer ponto, porque não é um `return`.
- Funções de seta com expressão (`(user) => user.name`) já têm o seu único `return` implícito.
- Funções sem valor a devolver não precisam de `return`.

```js
// ❌
function detectLocale() {
  const saved = localStorage.getItem('locale')
  if (SUPPORTED_LOCALES.includes(saved)) return saved
  return DEFAULT_LOCALE
}

// ✅
function detectLocale() {
  const saved = localStorage.getItem('locale')
  let locale = DEFAULT_LOCALE
  if (SUPPORTED_LOCALES.includes(saved)) locale = saved
  return locale
}
```

```python
# ❌
def _validation_code(error_type: str) -> str:
    if error_type in CODES:
        return CODES[error_type]
    return "INVALID_VALUE"

# ✅
def _validation_code(error_type: str) -> str:
    code = CODES.get(error_type)
    if code is None:
        code = "INVALID_VALUE"
    return code
```

## 5. Ordem dos atributos nos elementos do Vue

Segue as recomendações de **Ordem dos Atributos dos Elementos** do Guia de Estilo Oficial do Vue.js. Do primeiro ao último:

| # | Categoria | Exemplos |
|---|---|---|
| 1 | Definição (muda as opções do componente) | `is` |
| 2 | Renderização de listas | `v-for` |
| 3 | Condicionais | `v-if`, `v-else-if`, `v-else`, `v-show`, `v-cloak` |
| 4 | Modificadores de renderização | `v-pre`, `v-once` |
| 5 | Atributos globais (exigem valor único) | `id` |
| 6 | Atributos únicos | `ref`, `key` |
| 7 | Slots | `v-slot`, `slot` |
| 8 | Ligação bidirecional | `v-model` |
| 9 | Outros atributos (normais e vinculados) | `class`, `:label`, `variant`, `:to` |
| 10 | Eventos | `@click`, `@update:model-value` |
| 11 | Conteúdo | `v-html`, `v-text` |

```vue
<!-- ❌ -->
<v-text-field
  @click:append-inner="showPassword = !showPassword"
  label="Password"
  v-model="password"
  v-if="visible"
/>

<!-- ✅ -->
<v-text-field
  v-if="visible"
  v-model="password"
  label="Password"
  @click:append-inner="showPassword = !showPassword"
/>
```
