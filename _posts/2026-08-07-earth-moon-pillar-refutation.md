---
layout: post
title: 地月“实体柱”假说的反证
subtitle: 从材料强度、轨道动力学与潮汐演化出发
date: 2026-08-07 12:00:00 +0800
author: Melting_Pot
header-img: img/bg-little-universe.jpg
header-mask: 0.55
tags: [物理, 天文学, 科学思辨]
mathjax: true
---

## 1. 假说的形式化

将待检验的“实体柱假说”记为 $H_P$，其基本命题为：

1. 地球与月球之间存在连续物质结构；
2. 该结构由岩石、金属、冰或类似天然地质材料组成；
3. 该结构是被动结构，不依靠主动推进、姿态控制或持续维修；
4. 该结构在远长于地月轨道周期的时间内连接两天体；
5. 该结构参与或导致月球从近地位置逐渐移动到远地轨道。

采用以下地月参数：

| 物理量 | 符号 | 数值 |
|---|---:|---:|
| 万有引力常数 | $G$ | $6.67430\times10^{-11}\ \mathrm{m^3\,kg^{-1}\,s^{-2}}$ |
| 地球质量 | $M_E$ | $5.9722\times10^{24}\ \mathrm{kg}$ |
| 月球质量 | $M_M$ | $7.3477\times10^{22}\ \mathrm{kg}$ |
| 地球半径 | $R_E$ | $6.371\times10^6\ \mathrm m$ |
| 月球半径 | $R_M$ | $1.7374\times10^6\ \mathrm m$ |
| 当前地月中心距离 | $a$ | $3.844\times10^8\ \mathrm m$ |
| 当前地月表面间距 | $L$ | $3.763\times10^8\ \mathrm m$ |
| 月球公转角速度 | $n$ | $2.665\times10^{-6}\ \mathrm{s^{-1}}$ |
| 地球自转角速度 | $\Omega_E$ | $7.292\times10^{-5}\ \mathrm{s^{-1}}$ |

---

## 2. 旋转三体坐标系中的静力模型

取地球中心为 $x=0$，月球中心为 $x=a$。地月质心距地球中心为

$$
x_b=\frac{M_M}{M_E+M_M}a
\approx4.67\times10^6\ \mathrm m.
$$

在随月球公转的旋转坐标系中，地月连线上的单位质量有效势为

$$
\Phi(x)=
-\frac{GM_E}{x}
-\frac{GM_M}{a-x}
-\frac12n^2(x-x_b)^2.
$$

有效加速度为

$$
g_{\mathrm{eff}}(x)
=-\frac{d\Phi}{dx}
=-\frac{GM_E}{x^2}
+\frac{GM_M}{(a-x)^2}
+n^2(x-x_b).
$$

令 $g_{\mathrm{eff}}=0$，得到地月 $L_1$ 点的位置

$$
x_{L_1}\approx3.264\times10^8\ \mathrm m.
$$

从地球表面到 $L_1$ 点的有效势差为

$$
\Delta\Phi
=\Phi(x_{L_1})-\Phi(R_E)
\approx6.09\times10^7\ \mathrm{J/kg}.
$$

该势差决定了任何连接结构必须承担的自重载荷数量级。

---

## 3. 恒截面柱的轴向应力反证

设柱体截面积为 $A$、密度为 $\rho$、轴向内力为 $N(x)$。一维静力平衡方程为

$$
\frac{dN}{dx}+\rho A g_{\mathrm{eff}}=0.
$$

从地球表面积分到 $L_1$ 点，有

$$
\frac{N(x_{L_1})-N(R_E)}{A}
=\rho\Delta\Phi.
$$

以 $\sigma=N/A$ 表示轴向应力，则

$$
\Delta\sigma=\rho\Delta\Phi.
$$

取岩石密度

$$
\rho=3000\ \mathrm{kg/m^3},
$$

得到

$$
\Delta\sigma
\approx3000\times6.09\times10^7
=1.83\times10^{11}\ \mathrm{Pa}
=183\ \mathrm{GPa}.
$$

不论怎样在两端分配支撑力，至少有一处必须满足

$$
|\sigma|_{\max}
\geq\frac{\Delta\sigma}{2}
\approx91\ \mathrm{GPa}.
$$

这一应力下限与截面积无关。把柱子做粗会同时增加承载面积和柱体质量，二者在应力公式中相互抵消。

天然宏观岩石的抗拉强度远低于 $1\ \mathrm{GPa}$，其抗压强度也无法在地质年代中承受几十至上百吉帕的差应力。因此恒截面实体柱不存在静力平衡解。

---

## 4. 在月球刚越过洛希极限时仍然失败

流体卫星的洛希极限近似为

$$
a_R
\approx2.44R_E
\left(\frac{\rho_E}{\rho_M}\right)^{1/3}
\approx2.9R_E.
$$

即使只考察月球中心位于 $a=2.9R_E$ 时的短柱，重新计算仍有

$$
\Delta\Phi\approx2.94\times10^7\ \mathrm{J/kg},
$$

从而

$$
\Delta\sigma\approx88\ \mathrm{GPa},
\qquad
|\sigma|_{\max}\ge44\ \mathrm{GPa}.
$$

所以实体柱不必延伸到今天的地月距离才会破坏。当月球中心距离只有约 $1.85\times10^7\ \mathrm m$ 时，所需应力就已经远超天然地质材料的长期承载能力。

---

## 5. 变截面结构的指数发散

假设通过改变截面积，使结构处处恰好达到许用应力 $\sigma_y$。由

$$
N=\sigma_yA
$$

及静力平衡方程可得

$$
\frac{dA}{A}
=\frac{\rho}{\sigma_y}\,d\Phi.
$$

积分后得到两处截面积之比

$$
\frac{A_{\max}}{A_{\min}}
=\exp\left(\frac{\rho\Delta\Phi}{\sigma_y}\right).
$$

即使极其乐观地取

$$
\sigma_y=1\ \mathrm{GPa},
$$

也有

$$
\frac{\rho\Delta\Phi}{\sigma_y}\approx183,
$$

因此

$$
\frac{A_{\max}}{A_{\min}}
\approx e^{183}
\approx10^{79}.
$$

若许用应力为 $100\ \mathrm{MPa}$，截面积比则达到

$$
e^{1827}\approx10^{793}.
$$

所以改变截面不能挽救天然柱模型，只会把问题转化为不可接受的尺寸和质量指数发散。

---

## 6. 受压柱的整体屈曲

如果对方把结构解释为由地球和月球表面支撑的受压柱，则必须考虑整体屈曲。

对长度为 $L$、半径为 $r$、弹性模量为 $E$ 的理想圆柱，欧拉屈曲临界力为

$$
P_{\mathrm{cr}}
=\frac{\pi^2EI}{L^2},
\qquad
I=\frac{\pi r^4}{4}.
$$

柱体自身载荷的数量级为

$$
P\sim\rho\pi r^2\Delta\Phi.
$$

要求 $P<P_{\mathrm{cr}}$，得到

$$
r>
L\sqrt{\frac{4\rho\Delta\Phi}{\pi^2E}}.
$$

即使采用远高于普通岩石的

$$
E=10^{12}\ \mathrm{Pa},
$$

也要求

$$
r\gtrsim1.0\times10^8\ \mathrm m,
$$

即半径约十万千米，比地球半径大十余倍。对应质量约为

$$
M_C=\rho\pi r^2L
\gtrsim3.7\times10^{28}\ \mathrm{kg},
$$

约为

$$
6200M_E.
$$

于是得到二难结论：

- 尺寸较小的柱子会屈曲；
- 粗到不屈曲的柱子，其质量会主宰整个系统，使地月系统不复存在。

---

## 7. 松散碎屑结构的开普勒剪切

若放弃固体连续结构，改称柱子由松散岩块、尘埃或碎屑流组成，则各段将按照当地开普勒角速度运动：

$$
\omega(r)=\sqrt{\frac{GM_E}{r^3}}.
$$

取两个代表位置

$$
r_1=10R_E,
\qquad
r_2=60R_E.
$$

它们的轨道周期约为

$$
P_1\approx1.85\ \mathrm d,
\qquad
P_2\approx27.22\ \mathrm d.
$$

相对角速度为

$$
\Delta\omega
=\omega(r_1)-\omega(r_2)
\approx3.66\times10^{-5}\ \mathrm{s^{-1}}.
$$

产生一弧度错位所需时间仅为

$$
t_1=\frac1{\Delta\omega}
\approx7.6\ \mathrm h,
$$

完全错开一周所需时间约为

$$
t_{2\pi}
=\frac{2\pi}{\Delta\omega}
\approx1.99\ \mathrm d.
$$

所以松散径向结构会在数小时内弯曲、数日内卷成环状碎屑盘，不可能保持数百万年或数十亿年。

---

## 8. 刚体共转矛盾

若整根柱子以月球角速度 $n$ 刚体旋转，各点离心加速度为

$$
a_c=n^2r,
$$

而地球引力近似为

$$
g_E=\frac{GM_E}{r^2}.
$$

自由圆轨道要求

$$
n^2r=\frac{GM_E}{r^2}.
$$

该等式只可能在某一个半径成立，不可能对整根柱子的所有半径同时成立。靠近地球的部分会受到巨大的净向内加速度，其残余载荷必须由结构承担。

地球表面与地月连线之间的相对速度为

$$
\Delta v
=(\Omega_E-n)R_E
\approx448\ \mathrm{m/s}.
$$

因此固定在地球表面的柱脚会与地表产生接近每秒448米的相对运动。如果强行固定，结构或地壳会被剪断；如果允许滑动，它就不再是稳定连接地月的天然柱。

---

## 9. $L_1$ 点的不稳定性

在 $L_1$ 附近令轴向微扰为 $\xi$。线性展开得

$$
\ddot\xi
\approx g'_{\mathrm{eff}}(x_{L_1})\xi,
$$

其中

$$
g'_{\mathrm{eff}}(x)
=\frac{2GM_E}{x^3}
+\frac{2GM_M}{(a-x)^3}
+n^2>0.
$$

代入地月参数，有

$$
g'_{\mathrm{eff}}(x_{L_1})
\approx8.02\times10^{-11}\ \mathrm{s^{-2}}.
$$

微扰解呈指数增长：

$$
\xi(t)\propto e^{t/\tau},
\qquad
\tau=\frac1{\sqrt{g'}}
\approx1.12\times10^5\ \mathrm s
\approx1.3\ \mathrm d.
$$

因此未经主动控制的轴向偏差会以“天”为尺度放大，而不能以地质年代尺度保持稳定。

---

## 10. 径向柱不能提供轨道角动量

对于近似圆轨道，月球轨道角动量为

$$
L_{\mathrm{orb}}(a)
=\mu\sqrt{G(M_E+M_M)a},
$$

其中约化质量为

$$
\mu=\frac{M_EM_M}{M_E+M_M}.
$$

假设月球从洛希极限附近

$$
a_0=2.9R_E
$$

迁移到当前距离 $a_1$，则

$$
L(a_0)\approx6.27\times10^{33}
\ \mathrm{kg\,m^2/s},
$$

$$
L(a_1)\approx2.86\times10^{34}
\ \mathrm{kg\,m^2/s}.
$$

月球需要获得的角动量为

$$
\Delta L
\approx2.23\times10^{34}
\ \mathrm{kg\,m^2/s}.
$$

但径向柱对月球施加的力可写为

$$
\mathbf F_C=F_C\hat{\mathbf r}.
$$

该力关于地球的力矩严格为零：

$$
\boldsymbol\tau_C
=\mathbf r\times\mathbf F_C
=0.
$$

所以

$$
\frac{d\mathbf L}{dt}=0.
$$

因此，纯径向柱无论作用多久，都不能把月球从一个近地圆轨道送到远地圆轨道。它可以改变径向运动，却不能提供圆轨道扩大所必需的角动量。

若柱子通过弯曲提供切向力，它就必须承担巨大的剪切和扭转载荷，并再次面对地球自转与月球公转不一致的问题。

---

## 11. 轨道能量要求

圆轨道机械能为

$$
E(a)=-\frac{GM_EM_M}{2a}.
$$

从 $a_0=2.9R_E$ 移动到当前轨道，需要增加

$$
\Delta E
=\frac{GM_EM_M}{2}
\left(\frac1{a_0}-\frac1{a_1}\right)
\approx7.55\times10^{29}\ \mathrm J.
$$

若历时45亿年，平均功率约为

$$
\bar P
=\frac{\Delta E}{4.5\times10^9\ \mathrm{yr}}
\approx5.3\times10^{12}\ \mathrm W.
$$

能量条件本身不是绝对反证，因为地球自转能可以通过潮汐作用转移给月球。但是这说明任何分离模型都必须同时解释：

1. 能量从何而来；
2. 所需角动量从何而来；
3. 什么机制持续施加切向力矩；
4. 产生的形变和耗散去了哪里。

被动径向柱无法回答这些问题，潮汐模型则可以自然地提供能量与角动量转移机制。

---

## 12. 漫长潮汐外移与实体分离不是同一过程

地球潮汐对月球产生的力矩近似为

$$
\tau
\sim
\frac{3k_2}{Q}
\frac{GM_M^2R_E^5}{a^6},
$$

其中 $k_2$ 是地球的潮汐勒夫数，$Q$ 是潮汐耗散品质因数。

由于

$$
L_{\mathrm{orb}}\propto\sqrt a,
$$

可以推出

$$
\dot a\propto a^{-11/2}.
$$

在简化的恒定 $k_2/Q$ 模型中，积分得到

$$
t\propto a_f^{13/2}-a_i^{13/2}.
$$

所以月球早期距离较近时，轨道演化速度通常远大于今天，不能把当前约 $37.9\ \mathrm{mm/yr}$ 的外移速度线性外推到45亿年前。月球激光测距直接测得了这一潮汐主导的半长轴变化率。

月球形成模拟给出的时间尺度则明显更短：

- 纯碎屑盘模拟可在一年以内形成一个大月球；
- 包含洛希极限内流体盘扩散的模型，月球吸积总时间约为 $10^2$ 年；
- 此后地月轨道才通过潮汐交换角动量，经历数十亿年的缓慢演化。

合理的物理时间顺序是

$$
\text{形成事件}
\longrightarrow
\text{环地碎屑盘}
\longrightarrow
\text{数年到约百年内吸积}
\longrightarrow
\text{数十亿年潮汐外移}.
$$

而不是

$$
\text{地月实体相连}
\longrightarrow
\text{物质柱缓慢拉长数十亿年}.
$$

---

## 13. 对所有柱模型的穷尽分类

对不同的情况进行模拟：

| 各种情况 | 数学或物理后果 | 判定 |
|---|---|---|
| 恒截面坚硬实体柱 | 轴向应力至少几十至上百吉帕 | 材料破坏 |
| 变截面柱 | 截面积比约 $10^{79}$ 或更高 | 尺寸与质量发散 |
| 受压柱 | 发生欧拉屈曲 | 需要超过行星尺度的半径 |
| 松散岩石柱 | 开普勒差速剪切 | 数小时至数日内卷成盘 |
| 自引力碎屑柱 | 洛希区内被瓦解，洛希区外发生吸积 | 形成环或天体，不形成长柱 |
| 刚体共转柱 | 不同半径所需角速度不一致 | 产生巨大残余载荷 |
| 固定于地球表面 | 约 $448\ \mathrm{m/s}$ 的相对运动 | 撕裂、扭断或滑脱 |
| 经过 $L_1$ 的平衡柱 | $L_1$ 为不稳定平衡 | 偏差以天为尺度放大 |
| 只施加径向力的柱 | $\mathbf r\times\mathbf F=0$ | 不能增加轨道角动量 |
| 完全不施加力的细丝 | 不影响轨道 | 不能解释所谓分离 |
| 主动控制的超材料结构 | 依赖推进、能源、控制和维修 | 已不属于天然地质柱 |

这些情况覆盖了连续结构、松散结构、承载结构、非承载结构、刚性结构和主动结构等主要逻辑可能性。

---

## 14. 最终结论

在普通引力、经典连续介质力学、开普勒轨道动力学以及观测到的地月质量和距离参数下，不存在一种由天然地质材料构成、无需主动控制、可以连接地球和月球并维持地质年代的柱状结构。

证明链条如下：

1. 若它是连续承载结构，所需轴向应力达到几十至上百吉帕；
2. 若通过变截面降低应力，截面积和质量呈指数发散；
3. 若主要承受压力，它会整体屈曲；
4. 若它是松散物质，会在数小时至数日内被差速剪切成盘；
5. 若它经过 $L_1$ 平衡区，扰动会在约一天的时间尺度上指数增长；
6. 若它只施加径向力，则严格不能提供轨道外移所需的角动量；
7. 若它提供切向力，又必须承担无法容忍的剪切、扭转和地表相对运动；
8. 若它不施加任何显著作用力，它便不能解释所谓地月分离。

因此，“地月长期实体柱分离模型”不是证据不足，而是其内部要求彼此不相容。

科学上应接受的区分是：

> 月球的形成或吸积是较短时间尺度的动力学过程；月球此后的轨道外移则是持续数十亿年的潮汐演化过程。轨道外移不需要、也不允许长期实体地月柱的存在。

---

## 参考资料

1. Dickey, J. O. et al. (1994). *Lunar Laser Ranging: A Continuing Legacy of the Apollo Program*. Science 265, 482–490. [DOI: 10.1126/science.265.5171.482](https://pubmed.ncbi.nlm.nih.gov/17781305/)
2. Williams, J. G. et al. (2004). *Lunar Laser Ranging Science*. [arXiv:gr-qc/0411095](https://arxiv.org/abs/gr-qc/0411095)
3. Ida, S., Canup, R. M. & Stewart, G. R. (1997). *Lunar accretion from an impact-generated disk*. Nature 389, 353–357. [DOI: 10.1038/38669](https://www.nature.com/articles/38669)
4. Salmon, J. & Canup, R. M. (2012). *Lunar Accretion from a Roche-Interior Fluid Disk*. The Astrophysical Journal 760, 83. [DOI: 10.1088/0004-637X/760/1/83](https://doi.org/10.1088/0004-637X%2F760%2F1%2F83)
5. Wilhelms, D. E., McCauley, J. F. & Trask, N. J. (1987). *The Geologic History of the Moon*. U.S. Geological Survey Professional Paper 1348. [USGS](https://www.usgs.gov/publications/geologic-history-moon)
