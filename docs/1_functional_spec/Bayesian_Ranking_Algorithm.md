# 🏆 Bayesian-Weighted Ranking Algorithm

This algorithm uses a **weighted arithmetic mean** to incorporate review confidence tiers and then applies an **Empirical Bayes (Bayesian) Estimate** to stabilize the score of items with few reviews, ensuring all final scores remain between 1 and 5.

---

## 1. Defining Review Weights

The confidence tiers are defined such that each tier is worth $3\times$ the previous one. The base weight is Tier 1 = 1.

The weight $W_t$ for Tier $t$ is calculated as $W_t = 3^{t-1}$:

| Tier ($t$) | Calculation ($3^{t-1}$) | Weight ($W_t$) |
| :---: | :---: | :---: |
| **1** | $3^0$ | $\mathbf{1}$ |
| **2** | $3^1$ | $\mathbf{3}$ |
| **3** | $3^2$ | $\mathbf{9}$ |
| **4** | $3^3$ | $\mathbf{27}$ |
| **5** | $3^4$ | $\mathbf{81}$ |

---

## 2. Calculating the Weighted Average Rating (WAR)

For each item, we calculate the $\text{WAR}$, which is the item's rating before stabilization.

### A. Weighted Sum of Ratings ($\text{WSR}$)

The total weighted sum of all star ratings for the item. $R_{t, s}$ is the count of reviews in tier $t$ with star rating $s$.

$$\text{WSR} = \sum_{t=1}^{5} \sum_{s=1}^{5} (s \times R_{t, s} \times W_t)$$

### B. Total Weight ($\text{TW}$)

This represents the total "effective" number of Tier-1 equivalent reviews for the item. This value is critical for the Bayesian shrinkage.

$$\text{TW} = \sum_{t=1}^{5} \sum_{s=1}^{5} (R_{t, s} \times W_t)$$

### C. The Weighted Average Rating (WAR)

$$\text{WAR} = \frac{\text{WSR}}{\text{TW}}$$

---

## 3. Applying the Bayesian Shrinkage

To prevent items with low $\text{TW}$ (few high-confidence reviews) from dominating the rankings, we regress their scores towards a global average.

### A. Define Global Parameters

| Parameter | Description | Typical Value |
| :--- | :--- | :--- |
| $\mathbf{\mu}$ (Global Average) | The simple arithmetic mean of *all* reviews across *all* items in the dataset. | e.g., $\mathbf{3.5}$ |
| $\mathbf{C}$ (Confidence Threshold) | The **Minimum Effective Weight** (Tier-1 equivalent reviews) required for an item's $\text{WAR}$ to be fully trusted. This is a tunable parameter. | e.g., $\mathbf{10}$ to $\mathbf{25}$ |

### B. The Final Bayesian-Weighted Score ($S$)

The final score $S$ is a proportional mix of the item's $\text{WAR}$ and the Global Average $\mu$, where the proportions are determined by the item's $\text{TW}$ and the threshold $C$.

$$S = \left(\frac{\text{TW}}{\text{TW} + C}\right) \text{WAR} + \left(\frac{C}{\text{TW} + C}\right) \mu$$

The item's ranking should be based on this **Bayesian-Weighted Score ($S$)**.

---

## 📝 Example Scenarios

Assume a global average $\mathbf{\mu = 3.5}$ and a confidence threshold $\mathbf{C = 10}$.

### Example 1: High Confidence, Few Reviews (Item A)

Item A has **one** perfect 5-star review, but it's Tier 5 (highest confidence).

* **Reviews:** $R_{5,5} = 1$
* **WSR:** $5 \times 1 \times 81 = 405$
* **TW:** $1 \times 81 = \mathbf{81}$
* **WAR:** $405 / 81 = 5.0$

$$\mathbf{S_{A}} = \left(\frac{81}{81 + 10}\right) 5.0 + \left(\frac{10}{81 + 10}\right) 3.5 = \left(\frac{81}{91}\right) 5.0 + \left(\frac{10}{91}\right) 3.5$$
$$S_{A} \approx 0.890 \times 5.0 + 0.110 \times 3.5 \approx 4.45 + 0.385 = \mathbf{4.84}$$
*Result: The score is slightly regressed from 5.0, but still very high due to the strong weight.*

### Example 2: Low Confidence, Few Reviews (Item B)

Item B has **one** perfect 5-star review, but it's Tier 1 (lowest confidence).

* **Reviews:** $R_{1,5} = 1$
* **WSR:** $5 \times 1 \times 1 = 5$
* **TW:** $1 \times 1 = \mathbf{1}$
* **WAR:** $5 / 1 = 5.0$

$$\mathbf{S_{B}} = \left(\frac{1}{1 + 10}\right) 5.0 + \left(\frac{10}{1 + 10}\right) 3.5 = \left(\frac{1}{11}\right) 5.0 + \left(\frac{10}{11}\right) 3.5$$
$$S_{B} \approx 0.091 \times 5.0 + 0.909 \times 3.5 \approx 0.455 + 3.18 = \mathbf{3.64}$$
*Result: The score is heavily regressed from 5.0 toward the global average of 3.5, as its $\text{TW}$ (1) is much lower than $C$ (10).*

### Example 3: Stable, High-Volume Item (Item C)

Item C has 81 Tier 1, 5-star reviews. (Total weight matches Item A, but with low confidence reviews).

* **Reviews:** $R_{1,5} = 81$
* **WSR:** $5 \times 81 \times 1 = 405$
* **TW:** $81 \times 1 = \mathbf{81}$
* **WAR:** $405 / 81 = 5.0$
* **$S_{C}$** $\approx \mathbf{4.84}$ (Same as Item A's score, demonstrating that many low-confidence reviews can eventually be trusted equally to a few high-confidence reviews.)