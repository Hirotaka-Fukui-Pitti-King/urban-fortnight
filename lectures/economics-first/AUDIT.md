# Stage 2 — Mathematical, Economic, and Numerical Audit

*2026年11月3日、既存PR #5・講義改訂ブランチのみを対象。*

**中心的な判定：** 既存の経済モデルから統計力学的構造を導出するという講義の目標は達成できるが、Stage 2-Bの非分離な貨幣・資本一般均衡を既に構築したと主張してはいけない。分布の不変性、詳細釣合い、Gibbs、競争均衡、合理的期待を区別する。

## 1. Audit matrix

| 区分 | 対象 | 結論 |
|---|---|---|
| **Verified** | Aiyagariの離散Bellman→Euler/KKT、家計政策→Forward、固定Markov核のKL縮小 | 講義IとAppendix A–Cで数学的仮定・証明を明示 |
| **Verified** | 対称二値選択・Gumbel Logit・Exact Potential・非同期更新 | 有限人数の一意Gibbs分布と無限人数の相転移を区別 |
| **Verified** | 自発的な二者間取引のBoltzmann弱形式と貨幣保存 | 最適取引核は制度・Bellman・双方受容の結果として定義 |
| **Corrected** | EGMの人工的な資産上限と予算・Euler/KKTの不一致 | 次期資産の切り詰めとそれに整合する消費の更新を政策反復の**毎回**に実装 |
| **Corrected** | Nash交渉の複合boxed display | 講義IIIの実行可能集合と最適化を別々の数式へ分割し、PDFの生TeX出力を防ぐ |
| **Corrected** | Lecture IVの導出不足 | 価格・投入ネットワーク、Calvo price dispersion、Mean–Variance需要の補足証明を追加 |
| **Numerically Checked** | Aiyagari、Ising、Fixed-price monetary matching | Pythonの保存則・Euler/KKT・Bellman・市場清算等をテスト |
| **Requires Additional Assumptions** | Gibbs則、Maximum Entropy、Boltzmann→Fokker–Planck | 特定の詳細釣合い・契約制度・取引量スケーリングが必要 |
| **Unresolved** | Money–Capital非分離GE、Nash契約の統合、存在・一意性と独自の比較静学 | Stage 2-B研究の未解決課題であり、講義用結果から自動的に従わない |
| **Unresolved** | すべての原著の全定理の精査、全ページの人間によるPDF目視査読 | 公開原著・出版社の研究内容は照合。PDFはCIで全ページを画像化して自動チェックするが、人間の視覚的査読とは区別 |

## 2. Lecture I：バグの原因と経済的意味

元のEGMは、収束後の貯蓄政策のみ人工上限に切り詰めて消費を再計算せず、さらに反復中に上限が反映されないため、資産グリッド上限付近での継続消費とEuler/KKT条件が整合しなかった。現在のコードは、各反復で
$$
a'=\min\{\bar a,\max\{\underline a,(1+r)a+wz-c_{\rm update}\}\},
\qquad
c=(1+r)a+wz-a'
$$
を計算する。この修正前、240点グリッドの最大相対Euler/KKT残差は約5%であった。独立したローカル実験では修正後に$3.7\times10^{-6}$となった。GitHub上の最新値は[数値JSON](figures/numerical-validation.json)とCIログで確認する。これは人工上限付き**教育用離散化経済**の数値精度であり、無限資産Aiyagariの厳密解ではない。

元のAiyagariに存在しない人工上限$a'\le\bar a$が拘束された場合のKKT不等号は、借入下限での不等号と逆向きであることもAppendix Aで明示した。境界のDirac原子質量と測度の弱形式をAppendix Bに、固定Markov核のKL縮小の適用条件と非線形核での破綻をAppendix Cに記載した。

## 3. Lecture II：Gibbsと相転移の適用条件

有限人数のGibbs法則は対称Potential Game、独立Gumbelショック、**一人ずつの**Logit更新を仮定して厳密に成立する。有限状態で温度尺度$\tau>0$なら不変分布は一意。分配関数の微分から
$$
\partial_hE_{\pi_N}[m_N]=\operatorname{Var}_{\pi_N}(S)/(N\tau)\ge0
$$
を導出した。大人数極限の複数典型状態と有限人数の準安定性を同義にしない。模倣の因果効果$J$の識別にはManski (1993)のReflection Problemへの対応が必要である。

## 4. Lecture III：交渉・衝突・一般均衡

連続貨幣、正の両者の参加利得、微分可能な$V$、非拘束な内点という**追加仮定**の下で、Nash交渉の内点条件は
$$
\frac{\eta u'(q)}{G_B}=\frac{(1-\eta)c'(q)}{G_S},
\qquad
\frac{\eta V'(b-d)}{G_B}=\frac{(1-\eta)V'(s+d)}{G_S}.
$$
有限トークン・固定価格モデルにはこれらの内点条件を課さず、双方が取引を受容することを検証する。Boltzmann作用素で保存されるのは人口とペアの貨幣総量であり、実物財、資本、効用ではない。$\lambda/2$の役割はペアと買手・売手の正規化に依存する。原著比較では[Green and Zhou (2002)](https://doi.org/10.1111/1468-0262.00315)、[Aruoba, Waller and Wright (2011)](https://doi.org/10.1016/j.jmoneco.2011.03.003)、[Toscani et al. (2013)](https://doi.org/10.1007/s10955-012-0653-0)を直接競合として優先する。

## 5. Lecture IV：経済的原始条件からの導出を追加

Mean–Varianceの最適ポートフォリオを微分して異質的需要・市場清算へ進む証明、Cobb–Douglas投入費用の最適化からネットワークの対数価格方程式を導く証明、CESからCalvo価格指数と相対価格分散を導く証明を追加した。Minority Gameの適応学習はRational Expectationsと別物。Random Matrix Theoryは高次元共分散の統計的推定法であり、資産市場均衡や因果的な金融感染を自動的に示さない。

## 6. 再現性とPDF品質

[Pythonスクリプト](scripts/generate_figures.py)をSVGと[数値チェック結果](figures/numerical-validation.json)の一元的な生成元にした。単体テストはKLのData Processingと非線形反例、AiyagariのEuler/KKTと予算、貨幣のBellman・受容・保存、Gibbs詳細釣合い、Markdown/Quarto同一本文、SVGパーサーを検証する。

[PDF QAスクリプト](scripts/check_pdf_render.py)はTypstで生成したPDFの全ページをPNG画像へ変換し、空白、文字のページ外はみ出し、TeXコマンドの生表示を自動検出する。GitHub Actionsアーティファクトには生成PDFと全ページの画像を含む。ただし、**自動検出の成功を全ページの数学記号に関する人間の目視確認の完了とはしない**。組版エラーが発生した場合はPDFに残った具体的な文字列をログへ出し、Markdown・Quarto両版を同時に修正する。

## 7. 原著の確認範囲とマージ判定

照合した主要資料：[Achdou et al. (2022)](https://doi.org/10.1093/restud/rdab002)、[Brock and Durlauf (2001)](https://doi.org/10.1111/1467-937X.00168)、[Green and Zhou (2002)](https://doi.org/10.1111/1468-0262.00315)、[Aruoba, Waller and Wright (2011)](https://doi.org/10.1016/j.jmoneco.2011.03.003)、[Toscani et al. (2013)](https://doi.org/10.1007/s10955-012-0653-0)等。各論文で閲覧可能な本文・要約の範囲が異なり、全論文の全定理を原著全文で独立再証明したものではない。講義の独自導出は本文で規定した**講義用の特殊モデル**についての結果である。CIの正常終了、最新HEADでの数値再現とPDF QAの成功を確認してからレビュー対象とする。PRは自動マージしない。研究実装ブランチは変更しない。
