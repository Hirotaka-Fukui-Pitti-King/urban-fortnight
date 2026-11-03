# Stage 2-Bブランチと先行研究の直接比較

調査日：2026年11月3日。対象ブランチ：research/stage2b-integrated-monetary-ge（コミット 9716f37748fb2741c5e205fd01a600bf1e51899f）。

## 1. 実装状況を先に固定する

GitHub比較で Stage 2-B と research/stage2-optimal-kinetic-foley は同一コミット（ahead/behindゼロ）。したがって、非分離型貨幣・資本モデルは現時点でリモート未実装。PR #3 と source_audit_and_propositions.md、monetary_matching.py、product_embedding.py および paper/article.qmd が実装済みの証拠である。

- [PR #3](https://github.com/Hirotaka-Fukui-Pitti-King/urban-fortnight/pull/3)
- [研究ノート](https://github.com/Hirotaka-Fukui-Pitti-King/urban-fortnight/blob/research/stage2b-integrated-monetary-ge/research/02-kinetic-exchange-yakovenko/notes/source_audit_and_propositions.md)
- [マッチング実装](https://github.com/Hirotaka-Fukui-Pitti-King/urban-fortnight/blob/research/stage2b-integrated-monetary-ge/research/02-kinetic-exchange-yakovenko/src/monetary_matching.py)
- [Product-embedding実装](https://github.com/Hirotaka-Fukui-Pitti-King/urban-fortnight/blob/research/stage2b-integrated-monetary-ge/research/02-kinetic-exchange-yakovenko/src/product_embedding.py)

**実装済み：** 定常Aiyagari、有限貨幣状態、固定1トークン価格での買手・売手双方の最適受容、Bellman価値と定常分布の整合、二次のBoltzmann型ゲイン・ロス作用素、加法分離したAiyagariとの直積、粒子シミュレーション。**未実装：** 内生Nash bargaining、資本・貨幣の共同Bellman、変換可能な資産、共通の労働資源、非分離型GE、均衡選択、集計ショック下の合理的期待。

## 2. 重要な直接競合（論文・機構・差分）

| 論文 | 先行研究が既に示したこと | Stage 2-Bへの含意 |
|---|---|---|
| [Chakrabarti & Chakrabarti (2009)](https://doi.org/10.1016/j.physa.2009.06.038), Physica A | ミクロ的効用最適化を基礎にしたKinetic Exchange、モーメント、財市場の集計価格 | 「最適化から交換則」自体は新規でない |
| [Toscani, Brugna & Demichelis (2013)](https://doi.org/10.1007/s10955-012-0653-0), J. Statistical Physics | Cobb–Douglas効用、双方が得する二財交換から非線形Boltzmann型方程式 | 「自発的取引からBoltzmann」は重複 |
| [Brugna & Toscani (2018)](https://doi.org/10.1016/j.physa.2018.02.070), Physica A | 二集団の財交換、財価格の内生変化、Boltzmann型方程式 | 「異質性と価格の導入」だけでは差分が足りない |
| [Green & Zhou (1998)](https://doi.org/10.1006/jeth.1997.2356), J. Economic Theory | 分割可能な貨幣、ランダムマッチング、単一価格の定常均衡の連続体 | 非分割貨幣・固定価格は一般性で劣る |
| [Zhou (1999)](https://doi.org/10.1111/1468-2354.00051), International Economic Review | 有費用生産、内生的貨幣分布、単一価格と複数均衡 | no-trade/activeの共存自体は新規でない |
| [Green & Zhou (2002)](https://doi.org/10.1111/1468-0262.00315), Econometrica | 無限期間の二者間ダブルオークション、貨幣の内生的分布、単一価格均衡 | **貨幣探索・価格・分布を同時に扱う直接競合** |
| [Rocheteau & Wright (2005)](https://doi.org/10.1111/j.1468-0262.2005.00568.x), Econometrica | Bargaining / price taking / price postingの厚生・政策比較 | Nash bargainingの追加だけでは新規でない |
| [Aruoba & Wright (2003)](https://boraganaruoba.com/research/search-money-and-capital-a-neoclassical-dichotomy/), J. Money Credit Banking | 分散的貨幣探索に労働・資本・新古典派企業を統合。特定の分離性 | **資本・貨幣・GEの共存自体は新規でない** |
| [Aruoba, Waller & Wright (2011)](https://doi.org/10.1016/j.jmoneco.2011.03.003), J. Monetary Economics | 資本と貨幣、集中的・分散的市場、確率的取引と交渉 | **Stage 2-Bで最も危険なマクロ理論競合** |
| [Berentsen, Camera & Waller (2007)](https://doi.org/10.1016/j.jet.2006.03.016), J. Economic Theory | 貨幣、銀行預金、信用制約、インフレ・厚生 | 流動性分布と政策の関係自体に先例 |
| [Baughman & Rabinovich (2019)](https://doi.org/10.1016/j.jet.2019.06.005), J. Economic Theory | 価格分散と貨幣保有分布の共同内生性、インフレ・厚生効果 | 内生価格分布もそれだけでは新規ではない |
| [Farmer (2024)](https://doi.org/10.3386/w32836), NBER WP 32836 | 不完備市場の異質的主体経済に貨幣を追加し、貨幣／非貨幣均衡と安定性を研究 | 「Aiyagari＋貨幣」や複数均衡も既に研究 |
| [Achdou et al. (2022)](https://doi.org/10.1093/restud/rdab002), Review of Economic Studies | HJB–Kolmogorov Forwardによる最適化と分布の一般均衡 | Forward Equationだけでは新規性にならない |
| [Foley (1994)](https://doi.org/10.1006/jeth.1994.1018), J. Economic Theory | 指定されたoffer setsの取引分布の統計均衡 | 貨幣保有分布のentropyとFoleyの取引entropyを区別 |

**文献の危険度判定：** Boltzmannの導出にはToscani et al. (2013)、貨幣探索・分布にはGreen & Zhou (2002)、資本・貨幣の統合にはAruoba, Waller & Wright (2011)が最も近い。Stage 2-Bが単に三つの既存モデルの要素を重ねるだけなら独立論文としての新規性は弱い。

## 3. 既存Stage 2の命題を正しく位置づける

### No-Trade

双方の継続価値が自己資産に厳密単調増加し、他に財・サービス・約束・外部性がなければ、純粋なゼロサム資産移転は双方の参加制約を同時に満たせない。これは正しいが、単純な単調性の帰結であり大型の理論的新規性ではない。

### 自発的サービス取引とBoltzmann作用素

買手保有$b$、売手保有$s$、固定価格1トークンの下で
$$
G_B(b)=u_B+\beta[V(b-1)-V(b)],\quad
G_S(s)=-c_S+\beta[V(s+1)-V(s)]
$$
が双方非負のとき交換を受容する。$\chi(b,s)$を受容政策とすると
$$
q_{bs}(f)=\tfrac{\lambda}{2}w(b,s)\chi(b,s)f_bf_s
$$
であり、分布作用素の弱形式は
$$
\sum_m\varphi(m)Q_m(f)=
\sum_{b\ge1,s<M}q_{bs}(f)
[\varphi(b-1)+\varphi(s+1)-\varphi(b)-\varphi(s)].
$$
$\varphi=1,m$を代入すると質量とトークンの保存を得る。これはマッチング事象を分布のゲイン・ロスとして表した結果である。固定政策の下で二次であること自体は独自のGEの定理ではない。

### EntropyとFoley

一様なマッチングと全取引受容の下では
$$
f_{m+1}/f_m=(1-f_0)/(1-f_M)
$$
の切断幾何分布が生じ、貨幣保有量の平均を固定した最大Shannon entropyと一致する。しかしassortative matchingではKL=0.0060626683で一致しない。条件付きの詳細釣合いの特殊例である。offer setsの異なるFoley-style比較はFoleyの定理への反例ではない。

### Product Equilibrium

加法分離したAiyagariと貨幣探索部門で$V^{GE}(a,z)+V^M(m)$、$\mu^{GE}\otimes f^M$が成り立つことは整合性の検証として有用。ただし資本と貨幣の限界代替、共通労働、政策ショックの共通のマクロ効果を含まない。Aruoba & Wright (2003)の分離性の結果とも比較する必要がある。

## 4. 新しい研究のcruxと比較静学

**Central research question:** 異質的な流動性制約の下で、最適な分散的貨幣取引が貨幣・資本の共同保有分布を内生的に変化させるとき、その分布の変化は生産・資本蓄積・金融政策伝達に、既存Monetary SearchとAiyagariの分離型モデルでは捉えられない効果を生むか。

状態$x=(a,m,z)$、継続価値$V(x;\mu)$、取引核$K^*(x,y\mid V,p,\mu)$と最適消費・貯蓄政策$g$を定義し、
$$
\partial_t\mu=
\mathcal A_{g,p}^*\mu+
\mathcal Q_{K^*(V,p,\mu)}^*(\mu\otimes\mu)
$$
を最適化・交渉・資源制約・市場清算と一緒に解く。ただし、この表現は**研究モデル案**であり、存在や安定性は未証明。

独自性の候補は、外生的な取引遭遇率$\lambda$が金融政策反応や借入制約率$\ell$と交差して効果を生むこと：
$$
\frac{\partial^2 C}{\partial i\,\partial\lambda},
\qquad
\frac{\partial^2 C}{\partial i\,\partial\ell}.
$$
上の交差微分がゼロでないことや符号は**未証明**。完全市場、交換からの追加利益がない経済、貨幣が必要でない経済などを反例として検討する。既存モデルと同じ生産・選好・マッチング環境を揃えて比較し、恣意的なexogenous-kineticモデルを同一環境のGE反実仮想と呼ばない。

## 5. 推奨する順序

第一にAruoba, Waller & Wright (2011)とGreen & Zhou (2002)の原著から、資産状態、価格、取引量、最適化、分布法則、均衡の成立範囲を抽出する。第二に、既存のStage 2に内生的価格・数量と非分離の流動性／資本選択を加える。ただし最初から集計ショック、Calvo、複数市場制度の全てを追加しない。第三に、固定価格・分離経済との同一環境比較で、新しい分布のフィードバックが必要になる比較静学を導出する。最後にNKに拡張する。

**制約：** GitHubの研究ファイル・PRと、出版社・中央銀行・著者の書誌・アブストラクトを照合。すべての競合原著の全文の全定理・仮定まで網羅したわけではない。完全な新規性の証明ではない。
