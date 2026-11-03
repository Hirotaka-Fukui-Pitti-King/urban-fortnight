# 講義IV：学習市場・生産ネットワーク・統計均衡・RMT・HANKの数理的導出

**位置づけ。** 異なる六つの経済学研究を統計力学という一つの言葉でまとめることはできない。それぞれのモデルが指定する個人行動、情報、均衡条件に従い、そこから現れる数理的構造を導出する。本講義のうちRandom Matrix Theoryは高次元推定の数学であり、単独では個人最適化も市場均衡も含まない。大きな外部定理を使うときは、何を証明せずに用いるかを明示する。

## 1. Minority Game：少数派への参加と適応的学習

### 1.1 利得関数と集計混雑損失

奇数$N$人が各期$t$に$a_i(t)\in\{-1,+1\}$を選び、集計行動を$A(t)=\sum_{i=1}^Na_i(t)$とする。小さい側への参加が有利という混雑の経済を、連続的な利得代理変数

$$
u_i(t)=-\frac{a_i(t)A(t)}{N}
$$

で表す。全員の利得を実際に和を取ると、

$$
\begin{aligned}
\sum_{i=1}^Nu_i(t)
&=-\frac1N\sum_i a_i(t)\sum_j a_j(t)\\
&=-\frac1N\left(\sum_i a_i(t)\right)^2\\
&=-\frac{A(t)^2}{N}.
\end{aligned}
$$

この式は私的利得の定義に依存する**会計恒等式**。$|A|$が小さいほど、総混雑損失が小さい。個人の戦略選択が均衡で効率的だという結論は出てこない。

### 1.2 戦略スコアから予測可能性へ

公的な情報状態を$\mu(t)\in\{1,\ldots,P\}$、家計$i$が事前に保有する戦略表を$a_{ig}^{\mu}\in\{-1,+1\}$とする。各戦略の仮想スコアを

$$
U_{ig}(t+1)=U_{ig}(t)-\frac{a_{ig}^{\mu(t)}A(t)}{N}
$$

で更新し、その時点でスコアが最も高い戦略を選ぶ（同率は事前に規則指定）。この更新則は、**最適な期待効用に基づく合理的期待**ではなく、過去の成果を使うAdaptive Learningである。

二つの戦略を持つ家計について

$$
\omega_i^\mu=\frac{a_{i1}^\mu+a_{i2}^\mu}{2},\qquad
\xi_i^\mu=\frac{a_{i1}^\mu-a_{i2}^\mu}{2}
$$

と定義し、戦略1を選ぶと$s_i=+1$、戦略2なら$s_i=-1$とする。実際に採用した行動は

$$
a_i^\mu=\omega_i^\mu+\xi_i^\mu s_i.
$$

なぜなら$s_i=1$なら右辺は$a_{i1}^\mu$、$s_i=-1$なら$a_{i2}^\mu$である。従って総行動は

$$
A^\mu=\Omega^\mu+\sum_i\xi_i^\mu s_i,\qquad
\Omega^\mu=\sum_i\omega_i^\mu.
$$

固定された定常環境で各情報パターンが一様に出現するとする。条件付き平均$\bar A^\mu=E[A\mid\mu]$、情報予測可能性$H=P^{-1}\sum_\mu(\bar A^\mu)^2$、全体変動$\sigma_A^2=E[A^2]$を定義すると、条件付き分散の定義

$$
E[A^2\mid\mu]
=\operatorname{Var}(A\mid\mu)+(E[A\mid\mu])^2
$$

を$\mu$で平均して

$$
\sigma_A^2
=H+\frac1P\sum_{\mu=1}^P\operatorname{Var}(A\mid\mu)
$$

となる。$H=0$でも条件付きな変動があれば$\sigma_A^2>0$であり、予測可能性と変動性は異なる。

### 1.3 Spin-Glassの結合行列はどこから生じるか

確率的な戦略選択の平均を$m_i=E[s_i\mid\mu]$と近似し、各情報に対する平均超過行動を$\Omega^\mu+\sum_i\xi_i^\mu m_i$とする。$H(\mathbf m)$の平方を実際に展開すると、

$$
\begin{aligned}
H(\mathbf m)
&=\frac1P\sum_\mu\left(\Omega^\mu+\sum_i\xi_i^\mu m_i\right)^2\\
&=\frac1P\sum_\mu(\Omega^\mu)^2
+\frac2P\sum_i m_i\sum_\mu\Omega^\mu\xi_i^\mu
+\sum_{i,j}J_{ij}m_im_j,
\end{aligned}
$$

$$
J_{ij}=\frac1P\sum_{\mu=1}^P\xi_i^\mu\xi_j^\mu.
$$

この$J_{ij}$は戦略表の乱雑さから内生的に構成されたGram型のランダムな相互作用行列である。ここからSpin-Glassの数学を援用する理由が生じるが、実際の学習動学が常に$H$の勾配を下ると主張するには具体的な更新制度が必要である。

### 1.4 Generating Functionalと相関・応答

学習により生じる経路確率$\mathbb P(\{s_i(t)\})$に対し、補助源$\psi_i(t)$を導入し、

$$
Z[\psi]=E\exp\left(i\sum_{i,t}\psi_i(t)s_i(t)\right)
$$

とする。有限期間・有限状態なら期待と微分の交換ができ、

$$
\left.\frac{\partial Z}{\partial\psi_i(t)}\right|_{\psi=0}
=iE[s_i(t)],\qquad
\left.\frac{\partial^2Z}{\partial\psi_i(t)\partial\psi_j(t')}\right|_{\psi=0}
=-E[s_i(t)s_j(t')].
$$

学習スコアへ外生的摂動$h_j(t')$を加え、遷移確率がその摂動に滑らかに依存するなら

$$
G_{ij}(t,t')=\frac{\delta E[s_i(t)]}{\delta h_j(t')}
$$

を応答関数と定義できる。完全なGenerating Functional Analysisは経路確率・乱雑な戦略集合に関する統計平均を必要とする。単に$Z[\psi]$の記号を書くだけでReplica法や相転移の完全な解析を済ませたと称しない。[Challet and Marsili (1999)](https://doi.org/10.1103/PhysRevE.60.R6271)、[Heimel and Coolen (2001)](https://doi.org/10.1103/PhysRevE.63.056121)の特定のゲームに関する外部結果を区別する。

## 2. Heterogeneous Beliefs：個人の需要から資産価格へ

### 2.1 リスクと需要の最適化

一期の価格$p_t$、次期配当$d_{t+1}$、割引しないリスクフリーの粗利率$R>1$を定義する。タイプ$h$の投資家は資産数量$z_{h,t}$を選び、主観的条件付き期待$E_{h,t}$と共通の条件付き分散$\sigma^2>0$を持つ。線形正規の近似的な平均分散選好

$$
\max_{z_h}\left\{
z_h(E_{h,t}[p_{t+1}+d_{t+1}]-Rp_t)
-\frac{\gamma\sigma^2}{2}z_h^2
\right\}
$$

を解く。$\gamma>0$なので目的関数の二階微分は$-\gamma\sigma^2<0$。一階条件を計算して

$$
E_{h,t}[p_{t+1}+d_{t+1}]-Rp_t-\gamma\sigma^2 z_h=0
$$

だから、一意の需要は

$$
z_{h,t}=\frac{E_{h,t}[p_{t+1}+d_{t+1}]-Rp_t}{\gamma\sigma^2}.
$$

タイプ人口比$n_{h,t}\ge0$、$\sum_hn_{h,t}=1$、一人当たりの外部資産供給$\bar z$に対する市場清算を課すと、

$$
\begin{aligned}
\sum_hn_{h,t}z_{h,t}=\bar z
&\iff \sum_h n_{h,t}E_{h,t}[p_{t+1}+d_{t+1}]-Rp_t
=\gamma\sigma^2\bar z\\
&\iff Rp_t=\sum_hn_{h,t}E_{h,t}[p_{t+1}+d_{t+1}]
-\gamma\sigma^2\bar z.
\end{aligned}
$$

この価格方程式は、主観的な期待が異なる投資家の**最適需要と市場清算**から導かれている。各期待が真の条件付き期待に一致する必要はないので、合理的期待価格形成と区別する。

### 2.2 Logitによる予測ルールの切替

投資家が予測ルール$h$を使った過去の実績$\Pi_{h,t}$を評価し、独立なGumbelショックを受けると、講義IIの積分と同様に

$$
n_{h,t+1}=
\frac{\exp(\eta\Pi_{h,t})}
{\sum_j\exp(\eta\Pi_{j,t})}
$$

が得られる。$\eta>0$は選択感応度。価格$p_t$は人口比$n_{h,t}$に依存し、当期価格の予測誤差から$\Pi_{h,t}$が変化し、次の人口比が変わる。こうして価格と予測ルールの分布の非線形写像が生じる。[Brock and Hommes (1998)](https://doi.org/10.1016/S0165-1889(98)00011-6)との数学的な関係である。

経済的な解釈としては、市場価格のVolatility Clusteringが生じても、それが真にルール切替によるかをStochastic Volatility、GARCH、注文価格インパクトなどのモデルと比較して識別する必要がある。[Lux and Marchesi (1999)](https://doi.org/10.1038/17290)のABMとの観察的な類似だけでは同じメカニズムだと断定できない。

## 3. 生産ネットワーク：投入需要から行列の逆へ

### 3.1 企業の費用最小化を明示する

部門$i$の生産技術を

$$
Y_i=A_iL_i^{\ell_i}\prod_{j=1}^J X_{ij}^{\gamma_{ij}},
\qquad
\ell_i=1-\sum_j\gamma_{ij}>0,\quad A_i>0
$$

とする。企業は賃金$w$、各中間投入価格$p_j$を所与にし、$Y_i$を生産する費用$wL_i+\sum_jp_jX_{ij}$を最小化する。生産制約のLagrange乗数を$\lambda_i$とし、

$$
\mathcal L=wL_i+\sum_jp_jX_{ij}
+\lambda_i\left[Y_i-A_iL_i^{\ell_i}\prod_jX_{ij}^{\gamma_{ij}}\right].
$$

一階条件は

$$
w=\lambda_i\ell_i\frac{Y_i}{L_i},\qquad
p_j=\lambda_i\gamma_{ij}\frac{Y_i}{X_{ij}}.
$$

両辺に投入量を掛けると$wL_i=\lambda_i\ell_iY_i$、$p_jX_{ij}=\lambda_i\gamma_{ij}Y_i$。合計して、$\ell_i+\sum_j\gamma_{ij}=1$から

$$
wL_i+\sum_jp_jX_{ij}=\lambda_iY_i.
$$

競争的なゼロ利潤の下では単位費用$\lambda_i$が販売価格$p_i$に等しい。ゆえに中間投入の名目費用シェアは$p_jX_{ij}/(p_iY_i)=\gamma_{ij}$となる。

投入需要を生産関数へ戻すと、

$$
Y_i=A_i\left(\frac{\ell_i p_iY_i}{w}\right)^{\ell_i}
\prod_j\left(\frac{\gamma_{ij}p_iY_i}{p_j}\right)^{\gamma_{ij}}.
$$

両辺に共通に現れる$Y_i$が一次同次性で相殺し、

$$
p_i=
A_i^{-1}\ell_i^{-\ell_i}
\left(\prod_j\gamma_{ij}^{-\gamma_{ij}}\right)
w^{\ell_i}\prod_jp_j^{\gamma_{ij}}.
$$

対数を取ると$\log p_i=-\log A_i-\ell_i\log\ell_i-\sum_j\gamma_{ij}\log\gamma_{ij}+\ell_i\log w+\sum_j\gamma_{ij}\log p_j$。係数と賃金が固定の生産性変動$\varepsilon_i=\Delta\log A_i$に対して

$$
\Delta\log p_i=-\varepsilon_i+\sum_j\gamma_{ij}\Delta\log p_j.
$$

行列$\Gamma=(\gamma_{ij})$と書けば

$$
(I-\Gamma)\Delta\log\mathbf p=-\varepsilon.
$$

### 3.2 Leontief逆行列の存在とネットワーク増幅

**命題IV.1（Neumann級数）。** 行列$A$のスペクトル半径$\rho(A)<1$なら$I-A$は可逆で

$$
(I-A)^{-1}=\sum_{k=0}^\infty A^k.
$$

**証明。** 右辺の有限和$S_n=I+A+\cdots+A^n$へ左から$I-A$を掛けると$(I-A)S_n=I-A^{n+1}$と望遠鏡型に相殺される。$\rho(A)<1$ならJordan標準形または適合する行列ノルムの評価から$A^n\to0$。従って$S_n$は収束し、その極限$S$は$(I-A)S=I$を満たす。正方行列なので$S=(I-A)^{-1}$である。$\square$

よって価格応答は$\Delta\log\mathbf p=-(I-\Gamma)^{-1}\varepsilon=-\sum_{k\ge0}\Gamma^k\varepsilon$。$k$段目は$k$回の産業投入連関を通った価格波及である。産出の方程式$y=\varepsilon+Ay$は**別のReduced Form**であり、その導出には最終需要、集計支出、労働制約などの追加条件が必要となる。

### 3.3 ミクロショックの集計分散

ショック$\varepsilon$が平均0、共分散$\Sigma_\varepsilon$を持ち、対象の集計量が$x=\omega^\top(I-A)^{-1}\varepsilon$と表される**指定された線形模型**を考える。$v^\top=\omega^\top(I-A)^{-1}$とすると$x=v^\top\varepsilon$だから

$$
\begin{aligned}
\operatorname{Var}(x)
&=E[(v^\top\varepsilon)^2]
=v^\top E[\varepsilon\varepsilon^\top]v\\
&=\omega^\top(I-A)^{-1}\Sigma_\varepsilon(I-A)^{-T}\omega.
\end{aligned}
$$

独立な等分散ショック$\Sigma_\varepsilon=\sigma^2I$なら$\operatorname{Var}(x)=\sigma^2\sum_iv_i^2$。均等な$v_i=O(1/N)$なら$O(1/N)$だが、実効ウェイトの集中により変動は大きくなり得る。これは[Acemoglu et al. (2012)](https://doi.org/10.3982/ECTA9623)のネットワーク増幅の核心と数学的に対応する。適切な家計需要・企業均衡を指定せずにこの線形模型を同論文の完全な構造式と断定しない。

金融ネットワークの有限責任清算$p_i=\min\{\bar p_i,\max(0,e_i+\sum_j\Pi_{ji}p_j)\}$には、ショックによるデフォルト閾値がある。この非線形性は、Ising的な模倣の存在がなくてもネットワークに急な状態転換を生むことを示す。[Acemoglu et al. (2015)](https://doi.org/10.1257/aer.20130456)を参照する。

### 3.4 中間投入のショック伝播の符号を証明する

企業の対数価格方程式を$(I-\Gamma)\Delta\log p=-\varepsilon$としたとき、$\Gamma$の各要素が非負、$\rho(\Gamma)<1$なら、Leontief逆の各要素は非負である。なぜなら$\Gamma^0=I$の要素は非負、非負行列の積は非負なので、すべての$\Gamma^k$も非負だからである。

**命題IV.3（部門の生産性ショックと価格の符号）。** 非負行列$\Gamma$と$\rho(\Gamma)<1$を仮定し、賃金と費用シェアを固定する。ある部門$j$の生産性だけが改善する$\varepsilon_j>0$に対し、すべての部門の対数価格変化は非正である。

**証明。** 既に証明したNeumann級数を用いると

$$
\Delta\log p_i=-\sum_{k=0}^\infty\sum_j(\Gamma^k)_{ij}\varepsilon_j.
$$

各係数$(\Gamma^k)_{ij}\ge0$、生産性の変化は$j$にのみ正で他の部門は0だから、各$i$の右辺は非正。$\square$

これはCobb–Douglasの費用最小化・ゼロ利潤・固定賃金を与えた**価格方程式の比較静学**である。賃金が一般均衡で変化する場合、同じ符号が全ての相対価格・実質賃金について成立すると主張してはいけない。

## 4. FoleyのStatistical Equilibriumを制約付き最大化から導く

家計タイプ$k=1,\ldots,K$の人口比$w_k>0$、$\sum_kw_k=1$、許容する取引ベクトルの有限集合$X_k$を指定する。$h_k(x)\ge0$をタイプ$k$が取引$x\in X_k$を選ぶ確率とし、各タイプの正規化と市場の実行可能性

$$
\sum_{x\in X_k}h_k(x)=1,\qquad
\sum_kw_k\sum_{x\in X_k}h_k(x)x=0
$$

を課す。Foley型の統計均衡について、離散集合に基づく講義用のエントロピー問題は

$$
\max_h-\sum_kw_k\sum_{x\in X_k}h_k(x)\log h_k(x)
$$

である。基準測度が一様でない場合は**相対エントロピー**を使う必要があり、任意の取引座標変換の下で同じShannon式が不変というわけではない。

### 4.1 Lagrange計算と厳密凹性

市場実行可能性の乗数を$\lambda$、タイプ別の正規化乗数を$\alpha_k$とすると、

$$
\mathcal L=
-\sum_kw_k\sum_xh_k(x)\log h_k(x)
-\lambda^\top\sum_kw_k\sum_xh_k(x)x
-\sum_k\alpha_k\left(\sum_xh_k(x)-1\right).
$$

内点で$h_k(x)$を微分すると、

$$
-w_k(\log h_k(x)+1)-w_k\lambda^\top x-\alpha_k=0,
$$

すなわち

$$
h_k(x)=\exp[-1-\alpha_k/w_k-\lambda^\top x].
$$

正規化のため$\sum_x h_k(x)=1$を使うと

$$
h_k^*(x)=\frac{\exp(-\lambda^\top x)}
{\sum_{y\in X_k}\exp(-\lambda^\top y)}.
$$

**命題IV.2（有限取引集合での条件付き一意性）。** 実行可能集合が非空で、上の最適化が内点解を持つとき、Entropy最大解は一意である。

**証明。** $g(p)=-p\log p$の二階微分は$g''(p)=-1/p<0$であり、全ての$w_k>0$だから目的関数は確率単体の内部で厳密凹。市場清算と正規化は線形制約なので実行可能集合は凸である。異なる二つの最大点が存在すると仮定すれば、その中点は厳密凹性により両者より高い目的値を持つので矛盾する。$\square$

この問題の影価格$\lambda$は実行可能性のLagrange乗数である。家計がBellman最適化を行い、合理的期待と市場価格を同時に満たしたことは示していない。**統計均衡と競争的GEは異なる均衡概念**。[Foley (1994)](https://doi.org/10.1006/jeth.1994.1018)の数学的な比較基準である。

## 5. Random Matrix Theory：WishartからMarchenko–Pasturの支持端点へ

### 5.1 高次元標本共分散

$N$資産、$T$期間の収益率イノベーションを$X\in\mathbb R^{N\times T}$とし、各要素が独立・平均0・分散$\sigma^2$である白色雑音の基準経済を考える。標本共分散を$S=XX^\top/T$と定義する。真の共分散が$\sigma^2I$でも、$N/T$が小さくないとき標本固有値は一点に集まらない。$q=N/T\to q_0>0$の大きな行列の極限を考える。

Stieltjes変換$m_N(z)=N^{-1}\operatorname{Tr}(S-zI)^{-1}$、$z\in\mathbb C$の上半平面で$\operatorname{Im}z>0$を定義する。Marchenko–Pasturの既知の**外部極限定理**は、適切な独立性・モーメント条件で$m_N(z)$が決定論的極限$m(z)$へ収束することを保証し、その$m$は

$$
z=-\frac1{m(z)}+\frac{\sigma^2}{1+q\sigma^2m(z)}
$$

を満たす。大規模行列の収束定理そのものの証明にはResolventの集中不等式等が必要であり、この講義ではこれを外部定理として用いる。

### 5.2 Resolvent Equationの代数的な解と端点

両辺に$m(1+q\sigma^2m)$を掛けると

$$
zm(1+q\sigma^2m)=-(1+q\sigma^2m)+\sigma^2m
$$

なので、

$$
q\sigma^2z\,m^2+[z-\sigma^2(1-q)]m+1=0.
$$

$m$の二次方程式の判別式が0になる点は連続的な固有値密度の支持端点である。判別式を展開すると

$$
\begin{aligned}
D(z)&=[z-\sigma^2(1-q)]^2-4q\sigma^2z\\
&=z^2-2\sigma^2(1+q)z+\sigma^4(1-q)^2.
\end{aligned}
$$

$D(z)=0$を二次方程式で解くと、

$$
\begin{aligned}
z_\pm
&=\sigma^2[(1+q)\pm\sqrt{(1+q)^2-(1-q)^2}]\\
&=\sigma^2[(1+q)\pm2\sqrt q]
=\sigma^2(1\pm\sqrt q)^2.
\end{aligned}
$$

これが$\lambda_\pm$である。複素平方根の枝は$m(z)\sim-1/z$（$|z|\to\infty$）と上半平面での適切な符号から選ぶ。Stieltjes反転公式$\rho(\lambda)=\pi^{-1}\lim_{\eta\downarrow0}\operatorname{Im}m(\lambda+i\eta)$を用いると、

$$
\rho(\lambda)=
\frac{\sqrt{(\lambda_+-\lambda)(\lambda-\lambda_-)}}
{2\pi q\sigma^2\lambda}
\mathbf1_{\{\lambda\in[\lambda_-,\lambda_+]\}}.
$$

$q>1$なら$S$の階数が最大$T<N$なので、少なくとも$N-T$個の固有値は正確に0である。極限の零固有値の比率は$1-1/q$。これは市場価格や投資家の選好ではなく**標本共分散の高次元推定**の性質である。[Laloux et al. (1999)](https://doi.org/10.1103/PhysRevLett.83.1467)の金融データにおけるノイズ診断はこの分野に属する。

### 5.3 Marchenko–Pasturの$q=1$を二次方程式から直接計算する

前節の二次方程式に$q=1$を代入すると

$$
\sigma^2 z\,m(z)^2+z\,m(z)+1=0.
$$

二次方程式の解は

$$
m(z)=\frac{-z\pm\sqrt{z^2-4\sigma^2z}}{2\sigma^2z}.
$$

$|z|\to\infty$で$m(z)\sim-1/z$を満たし、$\operatorname{Im}z>0$で$\operatorname{Im}m(z)>0$となる枝を選ぶ。実数$0<\lambda<4\sigma^2$に境界から近づくと、平方根の判別式は$\lambda(\lambda-4\sigma^2)<0$なので、分布のStieltjes反転公式から密度は

$$
\rho(\lambda)
=\frac{\sqrt{4\sigma^2-\lambda}}{2\pi\sigma^2\sqrt\lambda}
\mathbf1_{\{0<\lambda<4\sigma^2\}}
$$

となる。$q=1$は零に近い固有値が高密度に集中するが、$q>1$での原点の**点質量**とは異なる。この計算は**Resolventの極限方程式を所与にした結果**であり、有限行列の収束を証明する代用ではない。

## 6. New Keynesian HANK：Calvo最適化からNKPCへ

### 6.1 CES需要と価格指数

最終財生産者は中間財$Y_{it}$をCES集計

$$
Y_t=\left(\int_0^1Y_{it}^{(\epsilon-1)/\epsilon}di\right)^{\epsilon/(\epsilon-1)},
\qquad\epsilon>1
$$

で組み合わせる。総費用$\int_0^1P_{it}Y_{it}di$を所与の$Y_t$について最小化する。Lagrange条件から各財の限界費用は共通の集計乗数に比例するので、財$i$と$j$について

$$
\frac{P_{it}}{P_{jt}}
=\left(\frac{Y_{it}}{Y_{jt}}\right)^{-1/\epsilon}.
$$

従って各財需要は$Y_{it}=(P_{it}/P_t)^{-\epsilon}Y_t$となる。これを集計式へ戻すと

$$
P_t=\left(\int_0^1P_{it}^{1-\epsilon}di\right)^{1/(1-\epsilon)}
$$

が得られる。これがCESから導出された価格指数である。

### 6.2 Reset-Price最適化

各企業は毎期確率$1-\theta$で価格を再設定し、確率$\theta$で前期価格を維持する。再設定企業は同じ価格$P_t^*$を選ぶ。消費家計の実質確率的割引因子を$\Lambda_{t,t+k}>0$、企業の実質限界費用を$mc_{t+k}$とする。時点$t$で設定した名目価格$x=P_t^*$が$k$期先も維持される確率は$\theta^k$。その期の相対需要は$(x/P_{t+k})^{-\epsilon}Y_{t+k}$、実質単位利潤は$x/P_{t+k}-mc_{t+k}$なので、企業は

$$
\max_{x>0}
E_t\sum_{k=0}^{\infty}\theta^k\Lambda_{t,t+k}Y_{t+k}
\left[\left(\frac{x}{P_{t+k}}\right)^{1-\epsilon}
-mc_{t+k}\left(\frac{x}{P_{t+k}}\right)^{-\epsilon}\right]
$$

を選ぶ。級数の収束と微分・期待値の交換を仮定する。各項を$x$で微分して、

$$
\begin{aligned}
0=E_t\sum_{k\ge0}\theta^k\Lambda_{t,t+k}Y_{t+k}
\big[&(1-\epsilon)x^{-\epsilon}P_{t+k}^{\epsilon-1}\\
&+\epsilon mc_{t+k}x^{-\epsilon-1}P_{t+k}^{\epsilon}\big].
\end{aligned}
$$

$x^{\epsilon+1}$を掛けて移項すると

$$
P_t^*=\frac{\epsilon}{\epsilon-1}
\frac{E_t\sum_{k\ge0}\theta^k\Lambda_{t,t+k}Y_{t+k}P_{t+k}^{\epsilon}mc_{t+k}}
{E_t\sum_{k\ge0}\theta^k\Lambda_{t,t+k}Y_{t+k}P_{t+k}^{\epsilon-1}}.
$$

これは将来の実質限界費用を予想した**最適Reset Price**であり、Calvo価格を単なる外生的改定式で定義したものではない。

### 6.3 Aggregate Price IndexとPrice Dispersion

既存企業の比率$\theta$が前期価格を維持し、$1-\theta$がReset Priceへ変わるため、CES価格指数の定義を二群へ分割して

$$
P_t^{1-\epsilon}
=\theta P_{t-1}^{1-\epsilon}+(1-\theta)(P_t^*)^{1-\epsilon}
$$

を得る。相対価格分散

$$
\Delta_t=\int_0^1(P_{it}/P_t)^{-\epsilon}di
$$

も同様に二群へ分ける。既存価格の相対価格は前期比で$P_{t-1}/P_t=\Pi_t^{-1}$だけ変わるので

$$
\Delta_t=\theta\Pi_t^\epsilon\Delta_{t-1}
+(1-\theta)(P_t^*/P_t)^{-\epsilon}.
$$

もし企業が共通の線形生産$Y_{it}=AN_{it}$を使うなら、総労働投入は

$$
N_t=\int Y_{it}/A\,di
=\frac{Y_t}{A}\int(P_{it}/P_t)^{-\epsilon}di
=\frac{Y_t}{A}\Delta_t.
$$

したがって価格分布は実物資源の必要労働投入に影響する。

### 6.4 Log-Linearized NKPCを導く

ゼロ定常インフレ、同質企業、定常Reset価格は集計価格に等しい、価格Indexationなし、共通の実質限界費用、定常実質割引因子$\beta$という追加仮定を置く。$x_t=\log(P_t^*/P_t)$、$\pi_t=\log(P_t/P_{t-1})$、$\widehat{mc}_t$を定常からの実質限界費用の対数偏差とする。

価格指数を定常近傍で一次展開し、$\log P_{t-1}-\log P_t=-\pi_t$を使うと

$$
0=-\theta(1-\epsilon)\pi_t
+(1-\theta)(1-\epsilon)x_t.
$$

$(1-\epsilon)\neq0$を約して

$$
x_t=\frac{\theta}{1-\theta}\pi_t.
$$

Reset PriceのFOCの将来加重平均も一次近似し、定常の相対需要・割引重みが$(1-\beta\theta)(\beta\theta)^k$になることを使うと、

$$
x_t=(1-\beta\theta)\widehat{mc}_t+
\beta\theta E_t[x_{t+1}+\pi_{t+1}].
$$

最後に一つ目の$x_t$式を代入すると、

$$
\begin{aligned}
\frac{\theta}{1-\theta}\pi_t
&=(1-\beta\theta)\widehat{mc}_t+
\beta\theta E_t\left[\frac{\theta}{1-\theta}\pi_{t+1}+\pi_{t+1}\right]\\
&=(1-\beta\theta)\widehat{mc}_t+
\frac{\beta\theta}{1-\theta}E_t\pi_{t+1}.
\end{aligned}
$$

よって

$$
\pi_t=\beta E_t\pi_{t+1}
+\frac{(1-\theta)(1-\beta\theta)}{\theta}\widehat{mc}_t.
$$

これが**この限定条件のNew Keynesian Phillips Curve**。非ゼロのTrend Inflation、価格Indexation、企業固有資本、非線形な厚生評価では係数・状態変数・分散項が変わり得る。

### 6.4.1 Reset-Price FOCの一次近似を途中式から示す

第6.2節で導いたReset Priceは、二つの将来加重和の比率である。$\omega_{t,k}=\theta^k\Lambda_{t,t+k}Y_{t+k}$、$A_t=\sum_{k\ge0}\omega_{t,k}P_{t+k}^{\epsilon}mc_{t+k}$、$B_t=\sum_{k\ge0}\omega_{t,k}P_{t+k}^{\epsilon-1}$とすると

$$
P_t^*=\frac{\epsilon}{\epsilon-1}\frac{A_t}{B_t}.
$$

定常インフレが0で、実質限界費用の定常値が$\bar{mc}=(\epsilon-1)/\epsilon$、家計の実質確率的割引因子が定常状態で$\beta^k$、生産が定常であると仮定する。定常$A,B$の第$k$項の総和に占める比率は

$$
w_k=(1-\beta\theta)(\beta\theta)^k,\qquad
\sum_{k=0}^{\infty}w_k=1,
$$

後の等号は等比級数$\sum_{k=0}^\infty(\beta\theta)^k=1/(1-\beta\theta)$による。各変数の対数偏差をハットで書くと、和の対数の一次変化は定常ウェイトで加重した各項の対数変化に等しい。従って

$$
\begin{aligned}
\widehat A_t
&=\sum_{k\ge0}w_kE_t[
\widehat\omega_{t,k}+
\epsilon\widehat P_{t+k}+
\widehat{mc}_{t+k}],\\
\widehat B_t
&=\sum_{k\ge0}w_kE_t[
\widehat\omega_{t,k}+
(\epsilon-1)\widehat P_{t+k}].
\end{aligned}
$$

比率の対数変化は差なので、$\widehat\omega_{t,k}$が**同じ係数で相殺**され、

$$
\widehat P_t^*
=\widehat A_t-\widehat B_t
=\sum_{k\ge0}w_kE_t[\widehat P_{t+k}+\widehat{mc}_{t+k}].
$$

両辺から当期の集計価格$\widehat P_t$を引くと、$x_t=\widehat P_t^*-\widehat P_t$と$\widehat P_{t+k}-\widehat P_t=\sum_{j=1}^k\pi_{t+j}$より

$$
x_t=(1-\beta\theta)
\sum_{k=0}^\infty(\beta\theta)^k
E_t\left[\widehat{mc}_{t+k}+\sum_{j=1}^k\pi_{t+j}\right].
$$

$k=0$の項を分け、$k\ge1$の項の条件付き期待に期待値の反復法則を使えば

$$
x_t=(1-\beta\theta)\widehat{mc}_t
+\beta\theta E_t[x_{t+1}+\pi_{t+1}]
$$

となる。ここまででReset Priceの線形化を**将来加重和の展開から**導出した。第6.4節の価格指数の線形化$x_t=\theta\pi_t/(1-\theta)$を代入することでNKPCが得られる。

**命題IV.4（ゼロ定常インフレのCalvo NKPC）。** 共通の実質限界費用、定常$\beta$、独立なCalvoハザード$\theta\in(0,1)$、正の収束割引和、ゼロ定常インフレ、Indexationなし、定常近傍での一次微分可能性を仮定する。対称企業の最適Reset PriceとCES価格指数は

$$
\pi_t=\beta E_t\pi_{t+1}+
\frac{(1-\theta)(1-\beta\theta)}{\theta}\widehat{mc}_t
$$

を一次近似で満たす。

**証明。** 上で示した二つの線形化式を代入し、$x_t$を消去すれば第6.4節の最終式となる。すべての出発式は第6.1–6.3節の需要最適化と企業価格最適化から導いた。$\square$

この命題は**厳密な非線形関係ではなく一次近似結果**である。長期のTrend Inflation、企業固有資本、企業間の異なる費用や利潤、インデクセーションが存在する場合、同じ単一係数をそのまま当てはめてはいけない。

### 6.5 HANKの家計分布とSequence-Space Jacobian

HANKでは個別家計$(a,z)$が利子率、税、賃金、将来価格の予想に応じて消費・貯蓄政策$g_t$を選び、分布は$\mu_{t+1}=\mu_t P(g_t,z_t)$で変化する。同時に企業の価格分布がCalvoの法則に従い、財、労働、資産、政府の清算を課す。合理的期待は**全ての家計・企業が予想する将来の価格・政策系列が実際の均衡系列と一致すること**である。

均衡残差を、集計変数系列$X$と外生ショック系列$Z$について$F(X,Z)=0$と定義する。定常点$(X^*,Z^*)$で微分可能とすると、

$$
0=F(X^*+\delta X,Z^*+\delta Z)
=D_XF\,\delta X+D_ZF\,\delta Z+o(\|\delta\|).
$$

$D_XF$が可逆なら一次摂動に対して

$$
\delta X=-(D_XF)^{-1}D_ZF\,\delta Z
$$

となる。これがSequence-Space Jacobianの均衡線形化の核心。家計分布の推移についても

$$
\delta\mu_{t+1}
=\delta\mu_t P^*+\mu^*\delta P_t
$$

が積の一次展開から従う。[Auclert et al. (2021)](https://doi.org/10.3982/ECTA17434)はこの体系を効率的に計算する既存手法を研究した。上の記法だけで無限次元作用素の可逆性や非線形HANKの大域的一意性を証明していない。

### 6.6 借入制約付きHANK家計と集計反応の具体例

New Keynesian HANKで家計が保有する債券は名目金利$R_t$を払い、価格水準が$\Pi_{t+1}=P_{t+1}/P_t$倍になるとする。時点$t$の実質的な次期債券の限界利得は$R_t/\Pi_{t+1}$である。簡単化した家計予算

$$
c_t+a_{t+1}=(R_{t-1}/\Pi_t)a_t+w_tz_t-T_t
$$

と下限$a_{t+1}\ge\underline a$を考える。名目金利とインフレ率の予想が家計の意思決定に影響するので、最適化問題を一期間摂動し、

$$
u'(c_t)=\beta E_t\left[
\frac{R_t}{\Pi_{t+1}}u'(c_{t+1})\right]
$$

を内点で得る。下限が拘束される家計では左辺が右辺以上となる。ここでも家計状態$(a_t,z_t)$と価格・所得の将来系列への合理的期待を指定しなければならない。単に代表家計のIS式を全員に適用しただけではHANKでない。

平均資産が同じでも限界消費性向（MPC）の分布が異なれば、政府移転や所得のショックへの総消費反応は異なる。単純な二期間の分析では、制約付き家計のMPCは1、内点家計のMPCは

$$
m_U=\frac{1+r}{1+r+[\beta(1+r)]^{1/\gamma}}<1.
$$

制約付きの人口比を$\ell$とし、ショックが両群へ同額$\Delta b$届くとすれば、集計消費の一次反応は

$$
\Delta C\approx[\ell+(1-\ell)m_U]\Delta b.
$$

これは借入制約と家計分布から生じる再分配的なマクロ反応を示す**二期間の教育用例**であり、時間変化するインフレ・税・賃金・企業利潤を全て含むHANKのインパルス応答の解析解ではない。金融政策の一般均衡では家計の実質所得・賃金・資産価格・政府移転も変化するため、Sequence-Space Jacobianを構築する必要がある。

## 7. 統計力学に相当する数学は何を追加するか

Minority Gameの乱雑な戦略結合、予測ルールのLogit切替、生産・金融ネットワークの行列逆、Foleyの取引Entropy、金融標本共分散のRandom Matrix Theory、HANKのForward Equationは、**異なる経済的対象と識別対象**に対して用いられる。数学的な類似を見つけることは経済メカニズムの新規性を意味しない。以下は各講義で用いた数学的構造の位置づけである。

| 経済モデル | 使う数理構造 | 本文で証明した範囲 | 外部定理・未解決部分 |
|---|---|---|---|
| Minority Game | 混雑、スピン結合、生成汎関数 | 集計混雑損失、条件付き分散分解、生成微分 | 非エルゴード相の存在と厳密臨界指数 |
| Brock–Hommes | 最適資産需要とLogit切替 | 需要FOC、価格清算、人口比法則 | 構造パラメータの実証識別 |
| Production Networks | Leontief逆、共分散伝播 | 費用シェア、Neumann級数、集計分散 | 任意の多部門GEへの外挿 |
| Foley | Entropyと実行可能取引集合 | Lagrange解と内点一意性 | 経済的なBellman最適性 |
| RMT | Wishart、Resolvent、MP | Resolvent方程式を所与にした支持端点の代数 | 高次元Resolvent収束そのもの |
| NK-HANK | Calvo、資産分布、Sequence Jacobian | Reset Price FOC、NKPC、線形化 | 非定常・非線形GEの存在・一意性 |

**最終判断。** 既存の経済モデルに現れる統計力学の構造を正確に理解することは、一般均衡の代わりになるものではなく、分布・相互作用・高次元推定を扱う手段を豊かにする。新しい論文の必要性は、既存モデルとの明確に異なる比較静学または識別可能な経済的予測で判断する。
