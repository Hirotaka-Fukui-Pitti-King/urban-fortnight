# Econophysicsと統計力学的マクロ経済モデル：体系的Literature Review

*調査基準日：2026年11月3日／講義「統計力学と経済物理学」の補足文献レビュー*

> **中心的な研究課題**：個人の最適化、相互に自発的な二者間取引、価格・生産・金融市場清算、合理的期待からBoltzmann型の分布動学を導いたうえで、既存のHANK、Monetary Search、Kinetic Exchangeを超える予測を得られるか。

## 0. 調査範囲と証拠の扱い

本レビューは原著論文、出版社・学術誌の書誌ページ、著者による論文概要を優先し、同じ現象を説明する論文を**研究課題／ミクロ的な機構／均衡概念／数学的主張／識別可能な予測**で整理する。出版社のAbstractで確認できる「著者の主張」と、定理の仮定・完全な証明まで確認した「検証済みの定理」は区別する。全文未確認の文献について、その本文の全仮定を確定したかのようには扱わない。原著以外のサーベイは研究の地図として使い、新規性判定では原著を優先する。

分類：

- **A（直接の先行研究）**：最適な取引、財交換、Boltzmann方程式、価格形成の少なくとも二つを直接接続。
- **B（直接の競合する均衡理論）**：二者間取引・貨幣・価格・生産・動学的一般均衡を明示するが、Boltzmann表示は主目的でない。
- **C（技術的な基礎）**：保存的交換、衝突作用素、長期分布、収束・厚い裾。
- **D（追加的な経済メカニズム）**：社会相互作用、戦略学習、金融市場・ネットワーク。
- **E（実装・測定の基準）**：HANK、価格硬直性、分布Forward Equation、RMT、計量識別。

「同じ問い・同じ機構」と「同じ問い・異なる機構」、「同じモデルクラス・異なる対象」、「後続の拡張」を混同しない。

## 1. 最重要の結論：新規性にとって危険な論文

| 優先 | 先行研究 | 既存論文が達成したこと | まだ区別し得る研究対象 |
|---|---|---|---|
| 最優先 A | **Chakrabarti & Chakrabarti (2009)**, [Microeconomics of the ideal gas like market models](https://doi.org/10.1016/j.physa.2009.06.038) | 消費者の最適化からKinetic Exchange型の資産交換方程式を説明し、財市場と集計価格決定も扱う | 生産・異質的企業・動学的最適化・資産市場・合理的期待を完全に閉じた一般均衡 |
| 最優先 A | **Toscani, Brugna & Demichelis (2013)**, [Kinetic Models for the Trading of Goods](https://doi.org/10.1007/s10955-012-0653-0) | Cobb–Douglas選好、Edgeworth Box、双方の効用改善を伴う二財の交換から**非線形Boltzmann型方程式**を構成。線形化・準不変取引極限と裾の分析 | 生産・消費・資産価格・異質的家計の動的Bellman最適化とマクロ政策への接続 |
| 最優先 A | **Chakrabarti et al. (2013), 第6章**, [Microeconomic foundation of the kinetic exchange models](https://doi.org/10.1017/CBO9781139004169.007) | 効用・市場制度の仮定からKinetic Exchange型の結果を再現するミクロ的解釈、資産分布と時間変化するマクロ変数を検討 | 上記の延長をただ再提案せず、標準的HANK/GEが説明できない反応を示す |
| 高 A | **Brugna & Toscani (2018)**, [Kinetic models for goods exchange in a multi-agent market](https://doi.org/10.1016/j.physa.2018.02.070) | 財のCobb–Douglas型交換と二集団（dealers/speculators）からBoltzmann型方程式と価格変化を扱う | 経済的な最適反応・均衡条件を完全な動学的一般均衡に組み込む |
| 高 B | **Kiyotaki & Wright (1989)**, [On Money as a Medium of Exchange](https://doi.org/10.1086/261634) | 専門化された生産・消費、ランダムな二者間マッチング、貨幣の受容を戦略的均衡で扱う | 財・貨幣保有の**分布全体**をBoltzmann型作用素で追跡する計算・解析上の付加価値 |
| 高 B | **Lagos & Wright (2005)**, [A Unified Framework for Monetary Theory and Policy Analysis](https://doi.org/10.1086/429804) | 貨幣の役割を生む取引摩擦をミクロ的にモデル化し、金融政策分析と接続 | 単純化された分布の縮約を超えて、任意の非線形取引核を用いた分布の動学 |
| 高 B | **Foley (1994)**, [A Statistical Equilibrium Theory of Markets](https://doi.org/10.1006/jeth.1994.1018) | 実行可能な取引集合と多数主体の配置数からGibbs型統計均衡とentropy pricesを考察。Pareto効率性とのずれも明示 | エントロピーによる最頻配分と、実際の最適取引から得る確率過程の不変分布・市場清算の違い |
| 高 C | **Düring, Matthes & Toscani (2008)**, [Kinetic equations modelling wealth redistribution: A comparison of approaches](https://doi.org/10.1103/PhysRevE.78.056103) | Boltzmann方程式のモーメントと確率測度の距離からPareto Tail・安定性を分析 | 最適化と価格に応じた衝突核の定理・保存則・収束 |
| 高 B | **Nirei (2015)**, [An interaction-based foundation of aggregate investment fluctuations](https://doi.org/10.3982/TE1611) | 企業の非分割投資・異質的ショックと動学的一般均衡から非消失的な集計投資変動を構成 | 異なる相互作用（最適取引）の独自の集計予測と識別 |
| 高 E | **Achdou et al. (2022)**, [Income and Wealth Distribution in Macroeconomics](https://doi.org/10.1093/restud/rdab002) | 家計のHJB最適化とKolmogorov Forwardによる資産・所得分布の一般均衡 | 二者間相互作用に由来する衝突項の付加と、その均衡価格への影響 |

**判断：** 「自発的で最適な二者間の財交換からBoltzmann型方程式を導く」だけでは既存研究との差分がありません。とりわけToscani et al. (2013) は *同じ問い・同じ機構* に非常に近く、Chakrabarti & Chakrabarti (2009) は最適化と財市場価格にも踏み込んでいます。既存の最適化モデルを単なる恣意的な取引モデルとして描写することは不適切です。

## 2. 原著を機構で読む：最適化からBoltzmann方程式まで

### 2.1 Chakrabarti & Chakrabarti (2009)：「最適化」の先取り

**確認できた内容。** *Physica A* 388, 4151–4158。著者の説明によれば、消費者の最適化を用いて従来の資産交換方程式を特殊ケースとして導き、交換方程式のモーメントを分析し、財市場でのグローバルな価格決定も導入する。したがって「標準的Kinetic Exchangeは全て非最適化」と述べるのは不正確である。

**まだ慎重に扱う点。** Abstractと出版社の導入部からは、異質的家計の*無限期間のBellman最適化*、資本蓄積・金融資産・合理的期待の全条件を同時に閉じているかどうかまで断定できない。モデルの全状態変数・均衡定義・実証予測を原著の全文で確認するまでは、網羅的な新規性否定・肯定を避ける。

### 2.2 Toscani, Brugna & Demichelis (2013)：「双方が得する取引」の先取り

**確認できた内容。** *Journal of Statistical Physics* 151, 549–566。二財に対するCobb–Douglas効用を使い、Edgeworth Boxで双方が改善する交換領域を考え、そこでの二者間交換から非線形Boltzmann型方程式を導く。線形化した模型や準不変取引（小規模取引）のFokker–Planck極限の下で、Pareto型の裾が現れ得ることを分析する。

**経済学的な中心点。** 自発的な両者改善と非線形な衝突作用素が両立することは、既に存在する。新しい研究が必要になるのは、取引が繰り返される動学的な最適反応、企業の生産・価格、市場清算、資産価格付け、集計ショックへの反応を、一つの均衡概念で整合させる場合である。

**区別可能な新予測（候補、未証明）。** 取引頻度・選好分散・労働所得リスクと金融政策乗数の交差効果。単純な二財交換の価格線への収束と、借入制約下での持続的な実物分配効果を比較する。

### 2.3 Brugna & Toscani (2018)：「価格と異質的集団」の先取り

**確認できた内容。** *Physica A*、DOI上記。二財に対しCobb–Douglas型の交換規則を設定し、dealersとspeculatorsという二つの集団が部分的な財の交換比率を変える。線形Boltzmann型の体系における平均価格の変化を解析し、非線形体系は数値分析する。

**危険な重複。** 「異質的な交易者が効用を高めながら取引し、価格を内生化するBoltzmannモデル」という説明は、この論文と重なる。価格形成・異質性の導入をそれだけで独自性とするべきではない。

### 2.4 必要な数理的モデル構造

主体状態を $x=(a,z,\ell,\ldots)$、現在の価格を $p$、集計分布を $\mu$、外生的な交渉・マッチングショックを $\eta$ とする。二者間交換で事前状態$(x,y)$から事後状態$(x',y')$へ移行する確率核を
$$
K(x,y;dx',dy'\mid p,\mu,V)
$$
と表す。$V$ は個人の継続価値である。個人最適化と自主的受容は、事後の実行可能な選択集合に対する最適反応または交渉解、および参加条件から $K$ を生成する必要がある。単に $K$ を仮定して「最適取引」と呼んではならない。

ペア遭遇の対称率を$\lambda$とし、分子混沌仮説を採用した連続時間のBoltzmann型分布方程式は、試験関数$\varphi$に対して
$$
\begin{aligned}
\frac{d}{dt}\int\varphi(x)\mu_t(dx)
=\frac{\lambda}{2}\iint\mu_t(dx)\mu_t(dy)
\int K(x,y;dx',dy'\mid p_t,\mu_t,V_t)
\big[\varphi(x')+\varphi(y')-\varphi(x)-\varphi(y)\big].
\end{aligned}
$$
この弱形式から、取引ペアで保存される量$\psi$（$\psi(x')+\psi(y')=\psi(x)+\psi(y)$）は$\frac d{dt}\int\psi d\mu_t=0$を満たす。

しかし家計が生産、消費、労働所得ショック、資産の売買・発行を行う場合には、分布の全生成作用素は
$$
\boxed{\partial_t\mu_t=\mathcal A_{g_t,p_t}^*\mu_t
+\mathcal Q_{K(p_t,\mu_t,V_t)}^*(\mu_t\otimes\mu_t)}
$$
となる。$\mathcal A^*$ は単一主体の政策関数・所得変化・生産・消費を、$\mathcal Q^*$ は二者間遭遇を表す。この分解は**研究の候補モデル**であり、特定の既存論文の定理と取り違えない。

### 2.5 取引が止まる問題：静学的な自発交換の限界

**命題（静学的取引モデルに対する条件付き観察）。** 各人が固定された効用関数 $u_i(x_i)$ を持ち、取引以外の状態変化・割引・選好ショックがないとする。すべての成立取引が当事者双方の効用を弱く改善し、少なくとも一人に正の効用改善を与えるなら、有限期待値を持つ効用総和 $U_t=\sum_i u_i(x_{it})$ が**分布の意味で定常**かつ毎期正の改善確率を維持することはできない。

**証明。** 各取引は$\Delta U_t\ge0$を満たす。正の確率で$\Delta U_t>0$なら、期待値が存在する限り $E[\Delta U_t]>0$。一方、定常性から$E[U_{t+1}]=E[U_t]$なので$E[\Delta U_t]=0$。矛盾する。$\square$

この命題は新しい一般均衡存在定理ではなく、単純な仮定からの会計的な帰結である。したがって、静学的なPareto改善の取引を無限回続け、非退化な定常取引分布を主張するには注意が必要である。所得ショック、新しい生産・消費、財の減耗、選好・技術の変化、探索摩擦、継続価値の変化などが、長期の取引需要を維持する候補となる。**既存のEdgeworth Box型Boltzmann模型を標準的な動学的一般均衡へ移す際の中心的な技術課題**である。

## 3. 交換過程の数学・富分布：何が証明され、何が近似か

| 研究 | モデルと結果 | 証明水準・注意点 |
|---|---|---|
| **Drăgulescu & Yakovenko (2000)** [Statistical mechanics of money](https://doi.org/10.1007/s100510070114) | 保存的なランダム貨幣交換と指数型の定常貨幣分布 | 特定の交換則の帰結。貨幣から所得・富への直接拡張は不可 |
| **Chakraborti & Chakrabarti (2000)** [Statistical mechanics of money](https://doi.org/10.1007/s100510070173) | 貯蓄性向が分布形を変化させる | 共通貯蓄の二次モーメントとGammaフィットを区別 |
| **Chatterjee, Chakrabarti & Manna (2004)** [Pareto law in a kinetic model](https://doi.org/10.1016/j.physa.2003.11.014) | 固定された異質的貯蓄性向とPareto型の裾 | 主たる分布の報告には数値結果が含まれる |
| **Bouchaud & Mézard (2000)** [Wealth condensation in a simple model of economy](https://doi.org/10.1016/S0378-4371(00)00205-3) | 交換と乗法的ショック、Pareto分布と富の集中 | Mean-fieldとネットワーク効果を区別 |
| **Cordier, Pareschi & Toscani (2005)** [On a kinetic model for a simple market economy](https://doi.org/10.1007/s10955-005-5456-0) | 交換とリスク的投資、準不変取引極限でFokker–Planck型分布 | 準不変取引は極限近似であり、すべての衝突過程で自動的に成立しない |
| **Matthes & Toscani (2008)** [Analysis of a model for wealth redistribution](https://doi.org/10.3934/krm.2008.1.1) | 固定貯蓄性向のBoltzmann模型で定常解の一意性・動学的安定性・緩和速度 | 正確な関数空間と正則性は原著の定理に依存 |
| **Düring, Matthes & Toscani (2008)** [Kinetic equations modelling wealth redistribution](https://doi.org/10.1103/PhysRevE.78.056103) | モーメント法・確率測度の距離でPareto Tailと安定性を整理 | 既存の数学的基準。裾の直感だけを新定理としない |
| **Calbet, López & López-Ruiz (2011)** [Equilibrium distributions and relaxation times](https://doi.org/10.1103/PhysRevE.83.036108) | 交換則から確率密度の厳密な発展方程式と緩和を解析 | 解析解が得られるモデルと数値解が必要なモデルを区別 |
| **Boghosian (2014)** [Kinetics of wealth and the Pareto law](https://doi.org/10.1103/PhysRevE.89.042804) | Yard-Sale型の富交換からBoltzmann方程式、富の集中を分析 | 保存的取引でも一様な定常分布を保証しない |
| **Greenberg & Gao (2024)** [Twenty-five years of random asset exchange modeling](https://doi.org/10.1140/epjb/s10051-024-00695-3) | ランダム資産交換研究の体系的レビュー | 経済構造・制度を明示する方向への拡張を主張するサーベイ |

**補足（指数分布）。** $m_i'=\varepsilon(m_i+m_j)$、$m_j'=(1-\varepsilon)(m_i+m_j)$、$\varepsilon\sim U[0,1]$という均等分割規則では、一定総貨幣$M$の単体上で一様な不変測度を持つ。有限$N$の一人の周辺密度は
$$
f_N(m)=\frac{N-1}{M}\left(1-\frac mM\right)^{N-2}.
$$
$M/N\to T$なら$f_N(m)\to T^{-1}e^{-m/T}$。交換則を変えた場合に指数定常分布が残るとは限らない。

**補足（Gammaの近似）。** 共通貯蓄性向$\lambda$、独立事前保有・一様$\varepsilon$では
$$
\operatorname{Var}(m)/E[m]^2=(1-\lambda)/(1+2\lambda).
$$
Gamma$(k,\vartheta)$の二次モーメントと整合する $k=(1+2\lambda)/(1-\lambda)$ は、**分布そのものが厳密にGammaという証明ではない**。

**補足（ParetoとKesten）。** Kesten型の個人資産過程 $W_{t+1}=A_tW_t+B_t$ における裾指数を決める条件$E[A_t^\kappa]=1$と、個人の固定貯蓄性向の分布$\rho(\lambda)$から生じる裾は異なるメカニズムである。同じ裾指数で両者は識別できない。

## 4. 二者間取引の経済学：何をcanonicalな基準として残すか

### 4.1 Monetary Search／Random Matching

**Kiyotaki & Wright (1989)**, [On Money as a Medium of Exchange](https://doi.org/10.1086/261634), *Journal of Political Economy* 97, 927–954：専門化された生産・消費により物々交換の二重の欲求一致が困難な経済で、二者間遭遇と貨幣受容の戦略的均衡を研究。**同じ問い・異なる分析手法**の最も重要な起点である。

**Kiyotaki & Wright (1991)**, [A contribution to the pure theory of money](https://doi.org/10.1016/0022-0531(91)90154-V), *Journal of Economic Theory* 53, 215–235：探索摩擦のある一般均衡における貨幣の役割。生産・取引摩擦を省略したBoltzmann交換と比較する。

**Lagos & Wright (2005)**, [A Unified Framework for Monetary Theory and Policy Analysis](https://doi.org/10.1086/429804), *Journal of Political Economy* 113, 463–484：貨幣が必要になるミクロ的摩擦を明示しつつ、政策比較を可能にした枠組み。新モデルの基準は、貨幣と取引の実質効果が**市場制度と均衡条件**から発生する点である。

**Greene & Zhou (2000)**, [Dynamic Monetary Equilibrium in a Random-Matching Economy](https://www.chicagofed.org/publications/working-papers/2000/2000-01), Federal Reserve Bank of Chicago WP 2000-01：二者間ダブルオークション、分割可能な貨幣、無限期間の経済で個人・集計の貨幣保有分布の発展を扱う。Boltzmann表示を前面に出していなくても、**動学的な貨幣分布と最適取引の併存**について比較が不可欠である。

**Gode & Sunder (1993)**, [Allocative Efficiency of Markets with Zero-Intelligence Traders](https://doi.org/10.1086/261868), *Journal of Political Economy* 101, 119–137：予算・取引の制約を課したゼロ知能の取引者でもダブルオークションに高い配分効率が現れ得る。行動の最適化がないことを、そのまま経済的結果が無意味という評価に結びつけてはならない。

### 4.2 一般均衡でなく「統計均衡」と呼ぶ条件

**Foley (1994)**, [A Statistical Equilibrium Theory of Markets](https://doi.org/10.1006/jeth.1994.1018), *Journal of Economic Theory* 62, 321–345：各主体が受け入れ可能な取引集合と、許される取引配置を数えることからGibbs型の統計均衡を考察。著者はPareto効率性との相違を明示する。**最大エントロピー推論**と**価格を通じて最適化・清算する一般均衡**の橋渡しの文献であって、同じ意味の均衡とは限らない。

静学的な取引過程に分布不変性$\mu^*Q=0$があるだけで、動学的一般均衡を得たことにはならない。次を同時に要する：
$$
\begin{cases}
g_i\in\arg\max\{\text{期待効用}\},\\
\mu_{t+1}=\mathcal K(g_t,p_t,\mu_t),\\
\mathcal E(p_t,g_t,\mu_t)=0,\\
\text{主観的な集計法則}=\text{実現する集計法則},\\
\text{家計・企業・政府の予算制約と資産価格付けの整合性}.
\end{cases}
$$

## 5. 集計的相互作用・マクロ変動の直接の競合研究

### 5.1 Interaction-Based Aggregate Fluctuations

**Nirei (2015)**, [An interaction-based foundation of aggregate investment fluctuations](https://doi.org/10.3982/TE1611), *Theoretical Economics* 10, 953–985：企業固有の非分割投資と異質性から、集計外生ショックなしの投資変動を動学的一般均衡モデルで分析する。**「異質的ミクロショックによる内生的集計変動」だけでは新規ではない。**

**Acemoglu, Carvalho, Ozdaglar & Tahbaz-Salehi (2012)**, [The Network Origins of Aggregate Fluctuations](https://doi.org/10.3982/ECTA9623), *Econometrica* 80, 1977–2016：生産ネットワークの非対称性がミクロショックの集計効果を決める。粒子系の相互作用に似た増幅を、最適化と生産構造の経済学で説明する重要な比較対象。

**Acemoglu, Ozdaglar & Tahbaz-Salehi (2015)**, [Systemic Risk and Stability in Financial Networks](https://doi.org/10.1257/aer.20130456), *American Economic Review* 105, 564–608：負のショックが小さいと結び付きは安定化、大きいと伝播・脆弱性を生むという**非線形なネットワーク効果**を分析。相転移に似た結果が、統計力学を明示しない経済理論にも存在する。

### 5.2 Ising／Brock–DurlaufとCoordination Games

**Brock & Durlauf (2001)**, [Discrete Choice with Social Interactions](https://doi.org/10.1111/1467-937X.00168), *Review of Economic Studies* 68, 235–260：一般化Logitの個人の最適選択と社会的補完性から平均行動の自己整合条件と複数均衡を導く。個人のランダム効用$u_i(s_i)=s_i(Jm+h)+\epsilon_i(s_i)$、極値型選択ショック$\tau$なら
$$
m=\tanh((Jm+h)/\tau),\quad
J/\tau=1\ \text{が対称解の臨界条件}.
$$
社会的相互作用を用いる新しいNKモデルは、この結果自体を新規性としない。**家計の資産分布・市場清算を通じて政策効果がどう変わるか**が差分となる。

**Kirman (1993)**, [Ants, Rationality, and Recruitment](https://doi.org/10.2307/2118498), *Quarterly Journal of Economics* 108, 137–156：模倣のランダム過程と群集行動。有限人数の状態間移動や準安定性を、厳密な複数均衡と区別するために重要。

**Manski (1993)**, [Identification of Endogenous Social Effects: The Reflection Problem](https://doi.org/10.2307/2298123), *Review of Economic Studies* 60, 531–542：集団平均と個人の相関から社会的な因果効果を識別できるとは限らない。他者への処置やネットワーク構造の独立な変動が必要となる。

### 5.3 Minority Game

**Challet & Zhang (1997)**, [Emergence of cooperation and organization in an evolutionary game](https://doi.org/10.1016/S0378-4371(97)00419-6), *Physica A*：少数派への報酬と適応学習の起点。

**Challet & Marsili (1999)**, [Phase transition and symmetry breaking in the minority game](https://doi.org/10.1103/PhysRevE.60.R6271), *Physical Review E*：情報に応じた予測可能性の相転移。

**Challet, Marsili & Zecchina (2000)**, [Statistical Mechanics of Systems with Heterogeneous Agents: Minority Games](https://doi.org/10.1103/PhysRevLett.84.1824), *Physical Review Letters*：定常状態を無秩序なスピンモデルとして解析し、個人Nash均衡と異なることを明示。**学習の定常状態＝個人最適化の一般均衡**という誤認を避ける。

**Heimel & Coolen (2001)**, [Generating functional analysis of the dynamics of the batch minority game with random external information](https://doi.org/10.1103/PhysRevE.63.056121), *Physical Review E*：情報パターン比$\alpha=P/N$、臨界応答、初期スコアへの依存とVolatilityの異なる漸近挙動を分析。単一の臨界値とVolatilityパターンをすべての変種に当てはめない。

**Challet & Marsili (2003)**, [Criticality and market efficiency in a simple realistic model of the stock market](https://doi.org/10.1103/PhysRevE.68.036132), *Physical Review E*：Stylized Factsが臨界領域で現れることを分析。市場効率性と大きな変動が同時に観測されることを区別する。

## 6. 価格形成、金融相関、HANK/NK：競合する説明

### 6.1 Asset Pricing・市場ミクロ構造

**Lux (1995)**, [Herd Behaviour, Bubbles and Crashes](https://doi.org/10.2307/2235156), *Economic Journal*：投資家の模倣とバブル・クラッシュ。

**Brock & Hommes (1998)**, [Heterogeneous beliefs and routes to chaos in a simple asset pricing model](https://doi.org/10.1016/S0165-1889(98)00011-6), *Journal of Economic Dynamics and Control*：異質的予測ルールの成績に応じた切替から複雑な価格動学。

**Lux & Marchesi (1999)**, [Scaling and criticality in a stochastic multi-agent model of a financial market](https://doi.org/10.1038/17290), *Nature*：株価変動のFat Tails・Volatility Clusteringに似た性質を含むマルチエージェント模型。

**Farmer & Joshi (2002)**, [The price dynamics of common trading strategies](https://doi.org/10.1016/S0167-2681(02)00065-3), *Journal of Economic Behavior & Organization*：取引戦略と価格インパクトの動学。

**Bouchaud, Farmer & Lillo (2009)**, [How Markets Slowly Digest Changes in Supply and Demand](https://doi.org/10.1016/B978-012374258-2.50006-3), *Handbook of Financial Markets*：注文フローの持続性と価格インパクトの関係。金融市場の長期相関を見たとき、反応する主体の適応学習だけでなく、流動性供給とインパクトの変化も比較する。

**評価**：価格の確率的変動を再現するだけならGARCH・Stochastic Volatility・Heterogeneous-Agent Asset Pricing等も存在する。注文の符号、板流動性、価格インパクト、ポジション制約を分けて測定する必要がある。

### 6.2 Random Matrix Theory（RMT）は機構でなく推定技術

**Laloux et al. (1999)**, [Noise Dressing of Financial Correlation Matrices](https://doi.org/10.1103/PhysRevLett.83.1467)、**Plerou et al. (1999)**, [Universal and Nonuniversal Properties of Cross Correlations in Financial Time Series](https://doi.org/10.1103/PhysRevLett.83.1471)、**Ledoit & Wolf (2012)**, [Nonlinear shrinkage estimation of large-dimensional covariance matrices](https://doi.org/10.1214/12-AOS989)、**Ledoit & Wolf (2022)**, [The Power of (Non-)Linear Shrinking](https://doi.org/10.1093/jjfinec/nbaa007) を関連させる。

$S=XX^\top/T$、$N/T\to q$の白色雑音基準ではMPの支持は$\sigma^2(1\pm\sqrt q)^2$。固有値構造はノイズとFactorの識別には有用だが、どの企業や金融機関から危機が伝播したかを**因果的に**識別しない。

### 6.3 HANK、Behavioral NKと数値解法

**Kaplan, Moll & Violante (2018)**, [Monetary Policy According to HANK](https://doi.org/10.1257/aer.20160042)、**Auclert (2019)**, [Monetary Policy and the Redistribution Channel](https://doi.org/10.1257/aer.20160137)、**Achdou et al. (2022)** [Continuous-Time Approach](https://doi.org/10.1093/restud/rdab002) は、異質的家計の動学的最適化と分布Forward Equationの経済学的基礎。

**Auclert, Bardóczy, Rognlie & Straub (2021)**, [Using the Sequence-Space Jacobian to Solve and Estimate Heterogeneous-Agent Models](https://doi.org/10.3982/ECTA17434), *Econometrica*：分布型一般均衡のJacobianと非線形経路の計算がすでに確立している。新しい衝突作用素を導入するなら、このcanonicalな解法で扱えない理由を示す。

**Gabaix (2020)**, [A Behavioral New Keynesian Model](https://doi.org/10.1257/aer.20162005)：認知的な非完全合理性からNew Keynesian経済の反応を分析。合理的期待の最適選択に社会的外部性を含める模型と、適応的・行動的期待の模型は**異なる**。

**Auclert, Rognlie & Straub (2025)**, [Fiscal and Monetary Policy with Heterogeneous Agents](https://doi.org/10.1146/annurev-economics-091624-044646), *Annual Review of Economics*：最新のHANK研究地図。新モデルがすでに知られた再分配経路・直接／間接効果・財政経路を単に再現するだけなら、新規性は弱い。

**Golosov & Lucas (2007)**, [Menu Costs and Phillips Curves](https://doi.org/10.1086/512625)：価格改定の状態依存性と貨幣政策の実質効果。社会的相互作用で需要が変化する場合も、価格硬直性が必ず増幅要因になるとは限らない。

## 7. 新しい論文を書くための具体的な識別可能予測

### 7.1 Candidate A：最適交易の相互作用と分布動学

**既存と同じもの：** 「効用増進的な二者間交換からBoltzmann方程式を導出する」「二財の交換価格を持つ」「Pareto Tailが出る」。これだけなら2009・2013・2018の文献に直接重なる。

**追加的に狙うもの（未証明）：** 不完備市場の借入制約、所得ショック、最適な取引拒否が**価格・生産と同時に決まる**とき、取引発生率と分布の収束速度、マクロ政策乗数に異なる比較静学が現れること。

理想実験は、同じ資産・所得分布、同じ総資源と情報を持つ多数主体で、マッチング率や参加費用だけを外生的に変更し、取引の選択、実物消費、取引後の資産分布を比較すること。モデルでは
$$
\frac{\partial^2 C_t}{\partial \lambda_{\rm meet}\,\partial R_t}
$$
を適切な政策ショック定義の下で比較する。効用に交易外部性がなく、全取引が既に効率的な一括市場で瞬間的に実行できる環境は、効果が消える**反例の候補**である。

### 7.2 Candidate B：社会的相互作用とHANK

Ising型選択に相互作用$J$、Logit尺度$\tau$を置くと、対称部分模型の平均選択は
$$
m=\tanh((Jm+h)/\tau).
$$
$J/\tau=1$は部分模型の臨界点。一般均衡の家計・価格・分布を$X$とし
$$
m=F(m,X),\quad X=G(m,X)
$$
なら総フィードバックは
$$
F_m+F_X(I-G_X)^{-1}G_m
$$
で、臨界点も安定性も変わる。社会的状態が消費・貯蓄を変えなければ、相転移があってもインフレ・産出に影響しない。

**判定すべき交差効果：** 借入制約家計の比率$\ell$と社会的相互作用$J$が政策乗数$M$に及ぼす$\partial^2M/(\partial J\,\partial\ell)$。これは結果の符号もゼロでないことも未証明。Brock–DurlaufとHANKを「組み合わせた」だけに終わらないよう、両メカニズムの交差効果と反例を示す。

### 7.3 Candidate C：金融市場と相転移

Nirei (2015) やAcemoglu et al. (2012, 2015) などの**最適化・一般均衡の中での非線形集計変動**が強い競合である。統計力学的手法の独自性は、有限人数・ネットワーク分布・危機発生確率・マクロの実物効果において、標準モデルが導きにくい検証可能予測があるかで判断する。

## 8. 読む順番と論文設計上の判定基準

**最初に通読すべき6本**は、(1) Chakrabarti & Chakrabarti (2009)、(2) Toscani et al. (2013)、(3) Brugna & Toscani (2018)、(4) Kiyotaki & Wright (1989)、(5) Lagos & Wright (2005)、(6) Achdou et al. (2022) である。いずれも主要な研究課題との重複、または一般均衡の欠落を確定するために必要である。次にDüring et al. (2008)、Foley (1994)、Nirei (2015)、Greenberg & Gao (2024)、Auclert et al. (2021)を読む。

各論文について確認する事項は次の六つである。

1. **状態変数**：貨幣・資産・所得・消費財・企業・価格のどれを内生的に追跡するか。
2. **個人行動**：外生的な衝突ルール／静学的効用最大化／動学的Bellman最適化／戦略的な交渉のどれか。
3. **市場制度**：一括清算、二者間交渉、探索、価格インパクトのどれか。
4. **数学的結果**：定常解の存在、唯一性、Pareto指数、収束速度、複数均衡、安定性のどれを定理で示すか。
5. **政策と厚生**：均衡金利・価格・所得・生産・厚生が内生的か。
6. **検証可能性**：取引単位の選択、分布の遷移、価格、マクロ応答のどの変動で既存説と区別するか。

**最終的なNovelty Test：** 「Toscani et al. (2013) がすでに存在しても、なぜこの論文が必要か」に対して、*最適な取引と合理的期待・市場清算を同時に満たす動学的一般均衡において、取引機会と借入制約が金融政策の消費・物価への伝達を変えるかを、新しい比較静学とミクロ取引データで識別するため* と答えられる必要がある。ただしこれは**研究上の仮説的な位置づけ**であり、全文の網羅調査や理論結果が完成したことを意味しない。

## 9. 調査の到達点と未解決事項

- 出版社・学術誌の書誌情報と公開要約を用いて主要論文の実在、研究対象、代表的な主張を確認した。
- Cambridge University Pressの2013年単行本第6章と、2009年の最適化付きKinetic Exchange、2013・2018年の効用改善型Goods Exchangeを**直接競合**として追加した。
- 数学的な長期結果（存在・一意性・安定性・裾）の証明は、Düring–Matthes–ToscaniおよびMatthes–Toscaniの結果と比較すべきと特定した。
- Search Monetary Theory、HANK、Network Aggregate Fluctuations、Behavioral NKとの重複・差分を整理した。
- **制約**：有料原著の全文は全て確認できたわけではなく、本文中の細かな仮定や定理番号の網羅的照合は未実施。本文が未確認の箇所について存在しない結果を付け足していない。レビューは主要研究の精査であり、全分野の完全網羅や新規性の確定を主張しない。

## 10. 文献情報

主要論文のタイトル、著者、年、出版社DOIは本文の直接リンクで追跡できる。Quartoおよび文献管理用に、同じディレクトリに検証した主要文献のBibTeXデータ \`references.bib\` を置く。プロジェクト全体の講義との関係は親ディレクトリのREADMEを参照する。


## 11. Economics-First講義への対応（2026年11月3日追補）

この講義改訂では、統計力学の概念からではなく、既存の経済モデルの原始的な選好・生産・制約と個人最適化から導出する構成へ変更した。対応する原著と数学的な区別は[Economics-First Literature Matrix](economics-first-literature-matrix.md)にまとめた。Aiyagari／AchdouのHJB–Forward、Blume／Brock–DurlaufのLogit・Potential Game・Gibbs測度、Monetary Searchの最適取引とBoltzmann弱形式を中心にする。原著の単なる数学的別表現を新規な経済メカニズムと呼ばず、Stage 2-Bの研究主張はGreen–Zhou (2002)、Aruoba–Waller–Wright (2011)、Toscani et al. (2013)と比較する。
