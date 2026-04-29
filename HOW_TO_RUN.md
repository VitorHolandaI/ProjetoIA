# Como Rodar

Rode os comandos a partir da raiz do projeto:

```bash
cd /home/vitor/git/ProjetoIA
```

## Comando Principal

Use este comando para abrir a simulacao com Pygame:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python -m implemnentation.main --pygame --generations 20 --humans 12 --minotaurs 3 --time-limit 100 --step-delay 0.35
```

Quando esse comando roda, a primeira tela mostra 5 labirintos. Escolha um deles clicando no mapa ou apertando `1`, `2`, `3`, `4` ou `5`.

## Comando Antigo

Este comando ainda funciona:

```bash
python -m implemnentation.main --pygame --generations 20 --humans 12 --minotaurs 3 --steps 100
```

Mas prefira `--time-limit`, porque ele deixa claro que esse valor e o limite de tempo da rodada.

## Ativando A Venv

```bash
source .venv/bin/activate
python -m implemnentation.main --pygame --generations 20 --humans 12 --minotaurs 3 --time-limit 100 --step-delay 0.35
```

## Escolha De Labirinto

Sem `--maze`, a GUI mostra os 5 labirintos antes do experimento comecar.

Use `--maze 1` ate `--maze 5` se quiser pular a tela de escolha:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python -m implemnentation.main --pygame --maze 3 --generations 20 --humans 12 --minotaurs 3 --time-limit 100
```

Todos os espacos caminhaveis dos 5 labirintos sao conectados. Isso evita salas fechadas onde o Minotauro poderia nascer preso sem conseguir sair.

Cada labirinto tem 20 landmarks, usando as letras `A` ate `R`, mais `T` e `U`.

## Treinar Primeiro E Mostrar So O Melhor

Use este modo quando voce nao quiser assistir a simulacao inteira. Ele roda as geracoes sem animacao ao vivo, procura o melhor resultado humano, e no final abre uma janela mostrando o melhor caminho encontrado.

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python -m implemnentation.main --train-then-show --generations 50 --humans 20 --minotaurs 3 --time-limit 100
```

Tambem pode escolher um labirinto direto:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python -m implemnentation.main --train-then-show --maze 2 --generations 50 --humans 20 --minotaurs 3 --time-limit 100
```

## Visualizacao Mais Lenta

Use `--step-delay` se estiver rapido demais:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python -m implemnentation.main --pygame --generations 20 --humans 12 --minotaurs 3 --time-limit 100 --step-delay 0.35
```

Valores maiores ficam mais lentos:

```bash
--step-delay 0.2
--step-delay 0.5
--step-delay 1.0
```

## Opcoes Uteis

- `--generations 20`: quantidade de geracoes.
- `--humans 12`: quantidade de humanos em cada geracao.
- `--minotaurs 3`: quantidade de Minotauros ativos no labirinto.
- `--minotaur-strategies 8`: quantidade de DNAs/estrategias de Minotauro evoluindo.
- `--maze 1`: escolhe um dos 5 labirintos direto.
- `--time-limit 100`: limite de tempo da rodada em ticks da simulacao.
- `--minotaur-speed 2`: quantos movimentos cada Minotauro faz por tick.
- `--step-delay 0.35`: atraso visual entre ticks.
- `--replay`: imprime o melhor caminho de fuga depois da execucao.

## Rodar Testes

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest implemnentation.test_simulation
```
