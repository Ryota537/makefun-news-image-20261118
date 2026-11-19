# One Day in the World — news-image-20261118

[![Bounty](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118) [![Rank](https://make.fun/badge/news-image-20261118/Ryota537/makefun-news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118) [![Reward](https://make.fun/badge/news-image-20261118/Ryota537/makefun-news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118)

A program that draws a one-page newspaper poster summing up the world's
news of Wednesday, 18 November 2026, in a single 1024x1024 image: the war
in the Gulf (US strikes on Iran, Tehran's drone attacks on Kuwait and
Bahrain), the Xi–Putin meeting in Shenzhen ahead of the first-ever Trump
trilateral, plus the Kerch bridge, the US Senate result, NVIDIA's record
quarter, Voyager 1 and Cyclone Akvan.

## Run it

```sh
python3 main.py
```

`main.py` (Python 3, standard library only) writes `entry.png` to
`/output` (or to `$MAKEFUN_OUTPUT_DIR` when that is set). It is
deterministic: two runs write byte-identical output. No network, no
randomness, no timestamps.

## How the image is drawn

Everything is drawn in code: a hand-made 5x7 bitmap font and a hand-rolled
PNG encoder (filter 0, zlib level 9), no image libraries, no copied
assets. Layout: a navy masthead with the date, the main Gulf story with a
labelled schematic map, the APEC Shenzhen story, and five small panels for
the rest of the day's news. Facts are taken from reports of 18 November
2026; events announced 17 November US time and widely reported on the
18th are framed as the news of 18 November, without mis-dating them.

## Layout

- `main.py` — the whole entry: font, canvas, PNG encoder, poster layout
- `LICENSE` — MIT
- `.makefun/owner.json` — the entry owner's wallet
