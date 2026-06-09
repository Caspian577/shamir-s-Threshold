import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from sympy import symbols, Poly, GF, interpolate, mod_inverse

------------------------------------------------------------------
# =============================================================
#      Parameters
# =============================================================

prime = 257


def word_to_secret(word: str) -> int:
    # Reads the word as a big-endian integer from its UTF-8 bytes,
    # then reduces it mod prime to keep it inside the finite field GF(p).
    return int.from_bytes(word.encode('utf-8'), 'big') % prime


def coefficients_from_word(word: str, k: int, prime: int) -> list[int]:
    """Generates k-1 deterministic coefficients from the letters of the word."""
    coeffs = []
    for i in range(k - 1):
        idx = i % len(word)                  # cycle through the word's characters
        coeffs.append(ord(word[idx]) % prime)
    return coeffs


# ─── Share generation ────────────────────────────────────────────
def create_shares(secret: int, keyword: str, k: int, n: int,
                  prime: int = prime) -> list[tuple[int, int]]:
    # Build the full coefficient list: [secret, a1, a2, ...]
    coeffs = [secret] + coefficients_from_word(keyword, k, prime)

    def evaluate(x: int) -> int:
        # Horner's method: evaluates the polynomial mod prime efficiently
        result = 0
        for coeff in reversed(coeffs):
            result = (result * x + coeff) % prime
        return result

    # Each share is a point (x, f(x)) for x = 1, 2, ..., n
    return [(x, evaluate(x)) for x in range(1, n + 1)]


# ─── Reconstruction with SymPy ───────────────────────────────────
def reconstruct(shares: list[tuple[int, int]], prime: int = prime) -> int:
    x = symbols('x')
    # Lagrange interpolation in GF(prime) — recovers the polynomial from k points
    points = {xi: yi for xi, yi in shares}
    polynomial = sp.polys.polyfuncs.interpolating_poly(
        len(points), x, list(points.keys()), list(points.values())
    )
    # Evaluate at x=0 to get the secret back
    secret = int(polynomial.subs(x, 0)) % prime
    return secret


# ─── Visualization with Matplotlib ──────────────────────────────
def visualize(secret: int, shares: list[tuple[int, int]],
              coeffs: list[int], k: int, prime: int = prime):

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor('#0f0f1a')
    colors = ['#7F77DD', '#1D9E75', '#D85A30', '#EF9F27', '#D4537E']

    # ── Left panel: polynomial over the reals (visual intuition) ──
    ax1 = axes[0]
    ax1.set_facecolor('#161625')

    xs_cont = np.linspace(0, len(shares) + 1, 500)
    ys_cont = np.zeros_like(xs_cont)
    for i, c in enumerate(coeffs):
        ys_cont += c * xs_cont**i

    ax1.plot(xs_cont, ys_cont, color='#7F77DD', linewidth=2,
             label=f'f(x) — degree {len(coeffs)-1} polynomial', zorder=3)
    ax1.axhline(y=secret, color='#EF9F27', linewidth=1.2,
                linestyle='--', alpha=0.7, label=f'f(0) = secret = {secret}')
    ax1.scatter([0], [secret], color='#EF9F27', s=120, zorder=5,
                label=f'Secret S={secret}')

    for i, (xi, yi) in enumerate(shares):
        color = colors[i % len(colors)]
        ax1.scatter([xi], [yi], color=color, s=100, zorder=5)
        ax1.annotate(f'share {i+1}\n({xi}, {yi})', xy=(xi, yi),
                     xytext=(xi + 0.1, yi + 0.8),
                     color=color, fontsize=8.5,
                     arrowprops=dict(arrowstyle='->', color=color, lw=0.8))

    ax1.set_xlabel('x', color='#aaa', fontsize=11)
    ax1.set_ylabel('f(x)', color='#aaa', fontsize=11)
    ax1.set_title('Polynomial and share distribution (ℝ)', color='white', fontsize=12, pad=10)
    ax1.tick_params(colors='#888')
    for spine in ax1.spines.values():
        spine.set_edgecolor('#333')
    ax1.legend(fontsize=8, facecolor='#1e1e30', edgecolor='#444', labelcolor='white')
    ax1.grid(True, color='#2a2a3a', linewidth=0.5)

    # ── Right panel: share table and reconstruction ──
    ax2 = axes[1]
    ax2.set_facecolor('#161625')
    ax2.axis('off')

    # Title
    ax2.text(0.5, 0.97, f'Shares in GF({prime})', transform=ax2.transAxes,
             ha='center', va='top', color='white', fontsize=13, fontweight='bold')

    # Share table
    headers = ['Share', 'x', 'f(x) mod p', 'Used?']
    rows = [[f'share {i+1}', str(xi), str(yi),
             '✓ yes' if i < k else '✗ no']
            for i, (xi, yi) in enumerate(shares)]

    table = ax2.table(cellText=rows, colLabels=headers,
                      loc='center', bbox=[0.0, 0.38, 1.0, 0.52])
    table.auto_set_font_size(False)
    table.set_fontsize(9.5)

    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor('#333')
        if row == 0:
            cell.set_facecolor('#3C3489')
            cell.set_text_props(color='white', fontweight='bold')
   
        elif row <= len(rows) and rows[row-1][3] == '✓ yes':
            cell.set_facecolor('#0F2820')
            cell.set_text_props(color='#9FE1CB')
        else:
            cell.set_facecolor('#1e1e2e')
            cell.set_text_props(color='#666')

    # Polynomial equation display
    terms = ' + '.join([f'{c}·x^{i}' if i > 0 else str(c)
                        for i, c in enumerate(coeffs)])
    ax2.text(0.5, 0.35, f'f(x) = {terms}  (mod {prime})',
             transform=ax2.transAxes, ha='center', va='top',
             color='#AFA9EC', fontsize=9, fontstyle='italic')

    # Correct reconstruction
    shares_used = shares[:k]
    secret_rec = reconstruct(shares_used, prime)
    ok = '✓ Correct' if secret_rec == secret else '✗ Wrong'
    color_ok = '#1D9E75' if secret_rec == secret else '#D85A30'

    ax2.text(0.5, 0.22,
             f'Reconstructed with {k} shares:  f(0) = {secret_rec}  {ok}',
             transform=ax2.transAxes, ha='center', va='top',
             color=color_ok, fontsize=10, fontweight='bold')

  
    secret_bad = reconstruct(shares[:k-1], prime)
    ax2.text(0.5, 0.12,
             f'With only {k-1} shares:  f(0) = {secret_bad}  ✗ Wrong value',
             transform=ax2.transAxes, ha='center', va='top',
             color='#D85A30', fontsize=9)

    ax2.text(0.5, 0.04,
             f'Threshold k={k}  |  Total shares n={len(shares)}  |  Prime p={prime}',
             transform=ax2.transAxes, ha='center', va='bottom',
             color='#555', fontsize=8.5)

    plt.suptitle("Shamir's Secret Sharing Scheme",
                 color='white', fontsize=14, y=1.01)
    plt.tight_layout()
    plt.savefig('shamir.png', dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.show()
    print("Chart saved as shamir.png")


# ─── Main ────────────────────────────────────────────────────────
if __name__ == "__main__":

    WORD    = input("Enter your secret word: ")
    K       = 3    # minimum threshold
    N       = 5    # total shares
    P       = 257  # prime of the finite field 

    secret = word_to_secret(WORD)
    coeffs = [secret] + coefficients_from_word(WORD, K, P)

    print(f"\nWord:    '{WORD}'")
    print(f"Secret:  {secret}  (UTF-8 bytes mod {P})")
    print(f"Coeffs:  {coeffs}")

    shares = create_shares(secret, WORD, K, N, P)
    print(f"\nGenerated shares:")
    for i, (x, y) in enumerate(shares, 1):
        print(f"  share {i}: ({x}, {y})")

    print(f"\nReconstructing with the first {K} shares...")
    rec = reconstruct(shares[:K], P)
    print(f"  Result: {rec}  ->  {'OK ✓' if rec == secret else 'FAILED ✗'}")

    visualize(secret, shares, coeffs, K, P)
