# Permissões por role

A autorização é feita **sempre no backend**, a partir da role que vai dentro do JWT emitido pelo próprio backend no login (`common/security.py`). A role nunca é lida do pedido (corpo, query, cabeçalhos), por isso o frontend não a consegue forjar; um token alterado falha a verificação da assinatura (401).

| Ação | Endpoints | user | moderator | admin |
|---|---|:-:|:-:|:-:|
| Consultar | `GET /api/users…`, `GET /api/products…` | ✅ | ✅ | ✅ |
| Atualizar | `PUT` / `PATCH /api/users/{id}`, `/api/products/{id}` | ❌ | ✅ | ✅ |
| Criar | `POST /api/users`, `POST /api/products` | ❌ | ❌ | ✅ |
| Eliminar | `DELETE /api/users/{id}`, `/api/products/{id}` | ❌ | ❌ | ✅ |

- Sem role permitida a resposta é `403` com `code: "FORBIDDEN"` (o frontend já o traduz). Sem token ou com token inválido continua a ser `401`.
- Uma role desconhecida, ou um token sem role, não tem permissões de escrita (só leitura).
- Implementação: `require_role(...)` em `backend/common/security.py`, aplicado por rota nos routers de `users` e `products`.
- Origem da role: no login, é lida do perfil do utilizador na DummyJSON (que não a devolve no `/auth/login`); se não for possível obter, assume-se `user`.
- "Gerir permissões" (admin): não aplicável por agora, as roles são fixas.

## Escritas e persistência

A DummyJSON **não persiste** criações, alterações ou eliminações (responde como se tivessem sido feitas). Hoje nenhuma funcionalidade do frontend usa estas escritas, por isso não há overrides locais. Se vierem a ser necessárias, guardam-se em ficheiros JSON locais aplicados por cima dos dados de origem, sem alterar a fonte externa.

## Testes

```
cd backend
.venv\Scripts\python -m pytest
```

`tests/test_permissions.py` cobre a matriz acima (3 roles × 5 ações × users e products), role desconhecida, token sem role, token forjado e role enviada pelo cliente.
