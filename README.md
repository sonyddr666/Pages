# Pages

Hub de páginas HTML estáticas.

## Estrutura

```text
/
├── index.html
├── pages.json
├── .nojekyll
└── paginas/
    └── *.html
```

## Nova página

1. Adicione o HTML em `paginas/`.
2. Adicione uma entrada em `pages.json`.
3. O `index.html` lê o catálogo automaticamente.

Exemplo:

```json
{
  "title": "Minha página",
  "file": "minha-pagina.html",
  "description": "Descrição curta.",
  "category": "Experimento",
  "tags": ["HTML", "JS"],
  "created": "2026-10-17"
}
```

## Hospedagem

O projeto não depende de framework, build ou backend.

- GitHub Pages: publicar a raiz da branch `main`.
- Cloudflare Pages: conectar o repositório, sem comando de build, diretório de saída `/`.
- Render Static Site: conectar o repositório e publicar a raiz.

Todos os links internos são relativos para funcionar nos três ambientes.
