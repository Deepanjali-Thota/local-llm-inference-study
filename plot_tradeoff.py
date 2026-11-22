import matplotlib.pyplot as plt

models = ["llama3.2:3b", "phi4-mini", "mistral:7b"]
latency = [2.32, 3.07, 6.56]       # seconds per ticket (Run 2)
acc_orig = [95, 98, 95]            # % on original 40 tickets
acc_heldout = [69, 88, 88]         # % on held-out 16 tickets
ram = [4.1, 4.8, 6.8]              # GB

fig, ax = plt.subplots(figsize=(8, 5))

for i, m in enumerate(models):
    ax.plot([latency[i], latency[i]], [acc_heldout[i], acc_orig[i]],
            color="gray", linestyle="--", linewidth=1)
    ax.scatter(latency[i], acc_orig[i], s=ram[i] * 60, color="tab:blue",
               label="Original 40 tickets" if i == 0 else None)
    ax.scatter(latency[i], acc_heldout[i], s=ram[i] * 60, color="tab:orange",
               label="Held-out 16 tickets" if i == 0 else None)
    ax.annotate(f"{m}\n{ram[i]} GB RAM", (latency[i], acc_heldout[i]),
                textcoords="offset points", xytext=(10, -25), fontsize=9)

ax.set_xlabel("Median latency per ticket (s) — lower is better")
ax.set_ylabel("Category accuracy (%)")
ax.set_title("Accuracy vs latency on CPU (i5-1335U, Q4_K_M, temp 0)")
ax.set_ylim(60, 102)
ax.set_xlim(1.5, 8)
ax.grid(alpha=0.3)
ax.legend(loc="lower right")

plt.tight_layout()
plt.savefig("tradeoff.png", dpi=150)
print("Saved tradeoff.png")