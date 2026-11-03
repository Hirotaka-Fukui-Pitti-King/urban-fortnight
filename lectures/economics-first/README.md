# Economics-First：経済学の既存モデルから統計力学を導出する

**講義の順序：** Economic primitives → Individual optimization → Stochastic dynamics → Distribution dynamics → Equilibrium → Statistical-mechanical interpretation → Economic implications.

| 講義 | Markdown | Quarto | 主題 |
|---|---|---|---|
| I Aiyagari | [Markdown](01-aiyagari-statistical-mechanics.md) | [Quarto](01-aiyagari-statistical-mechanics.qmd) | HJB、Forward、KL縮小、GE |
| II Blume/Brock–Durlauf | [Markdown](02-social-interactions-ising.md) | [Quarto](02-social-interactions-ising.qmd) | Logit、Gibbs、Detailed Balance、相転移 |
| III Monetary Search | [Markdown](03-monetary-search-boltzmann.md) | [Quarto](03-monetary-search-boltzmann.qmd) | 最適取引、Boltzmann、取引市場清算 |
| IV Other Economic Models | [Markdown](04-other-economic-models.md) | [Quarto](04-other-economic-models.qmd) | Minority Game、金融市場、Networks、Foley、RMT、HANK |

[詳細Literature Matrix](../literature/economics-first-literature-matrix.md) ／ [既存Literature Review](../literature/literature-review.md) ／ [研究ブランチとの比較](../literature/stage2b-branch-comparison.md) ／ [BibTeX](../literature/references.bib)

## 数値図・再現性

各図は別のSVGファイルです。

- [Aiyagariの最適貯蓄政策](figures/aiyagari-savings.svg)
- [Aiyagariの分布Forward Dynamics](figures/aiyagari-distribution.svg)
- [有限人数IsingのGibbs定常分布](figures/ising-finite-population.svg)
- [最適な貨幣探索経済の定常保有分布](figures/monetary-matching.svg)

Pythonで計算した校正点、数値残差、詳細釣合い・参加制約のチェック値は [numerical-validation.json](figures/numerical-validation.json) に収録。原著論文の量的較正の厳密再現ではありません。配布用にコミットしたSVGは軽量なベクター作図で、Pythonスクリプトを再実行するとMatplotlibで同じ対象の図を再生成します（SVGの内部データや装飾は同一ではありません）。

再計算方法（リポジトリのルートで実行）：

~~~bash
python -m pip install -r lectures/economics-first/requirements.txt
python lectures/economics-first/scripts/generate_figures.py --output lectures/economics-first/figures
python -m unittest discover -s lectures/economics-first/tests -v
~~~

Quarto CLIが使用できる場合、各Quarto原稿を以下のようにHTMLまたはTypstでレンダリングします。

~~~bash
quarto render lectures/economics-first/01-aiyagari-statistical-mechanics.qmd --to html
quarto render lectures/economics-first/01-aiyagari-statistical-mechanics.qmd --to typst
~~~

他の三講も同様です。日本語フォントとTypst/Quartoの環境が必要な場合があります。

## 厳密さと研究ブランチの境界

分布の不変性、Detailed Balance、Gibbs、Entropy、Competitive GE、Rational Expectationsは異なる概念です。既存モデルの数学的同値と、経済的な新しい予測を区別しています。元の講義と既存研究資料は削除していません。Stage 2-Bの非分離な貨幣・資本GEは研究案であり、本講義改訂は研究実装ブランチを変更しません。
