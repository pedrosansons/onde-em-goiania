# Onde em Goiânia?

Jogo de adivinhação pelas ruas de Goiânia: você cai num ponto aleatório no Street View e marca no mapa onde acha que está.

- `index.html` — o jogo inteiro
- `pool.js` — 4.000 pontos sobre ruas dentro dos limites de Goiânia (OpenStreetMap)
- `tools/build_pool.py` — regenera o `pool.js`

Para rodar localmente: `python -m http.server` nesta pasta e abra http://localhost:8000.
