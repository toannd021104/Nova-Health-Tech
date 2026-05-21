"""
Elasticity model:
  SageMaker (Version B): scale-to-0 supported (re:Invent 2024).
    Active 12hr/day = 360hr/month. g5.xlarge $1.9712/hr.
    Student EP cost = 360 * 1.9712 = $710/mo (vs $1,419 always-on = 50% saving)

  PAI-EAS (Version C): min replicas = 1 (cannot scale to 0 on real-time).
    Always 1 instance running. Auto-scale adds replicas at peak.
    Avg utilization factor 0.85 (15% idle saving from scale-in).
    Student EP cost = 720 * 1.50 * 0.85 = $918/mo (vs $1,080 always-on = 15% saving)

Both B and C student endpoints are 10-50% cheaper than Version A's $1,455 LLM total.
"""

# ── VERSION A ─────────────────────────────────────────────────────────────────
haiku_em   = 30_000 * 1500/1e6 * 1.00 + 30_000 * 300/1e6 * 5.00
nova_mic_a = 120_000 * 500/1e6 * 0.035 + 120_000 * 40/1e6 * 0.14
sonnet_sp  = 120_000 * 3000/1e6 * 3.00 + 120_000 * 600/1e6 * 15.00
cohere_a   = 150_000 * 80/1e6 * 0.10
guard_a    = 120_000 * 3.6 * 0.15/1000
cache_a    = -0.40 * sonnet_sp
llm_a = haiku_em + nova_mic_a + sonnet_sp + cohere_a + guard_a + cache_a

infra_a = (2*720*0.24 + 1*720*0.16 + 720*0.166 + 2*720*0.046 +
           0.15*3.50 + 50*0.12 + 100*0.023 + 10*0.50 + 0.15*0.60 + 720*0.05)

total_a = llm_a + infra_a

# ── VERSION B ─────────────────────────────────────────────────────────────────
nova_lite  = 30_000 * 1500/1e6 * 0.06 + 30_000 * 300/1e6 * 0.24
nova_mic_b = 120_000 * 500/1e6 * 0.035 + 120_000 * 40/1e6 * 0.14
nova_pro   = 120_000 * 3000/1e6 * 0.80 + 120_000 * 600/1e6 * 3.20
cohere_b   = 150_000 * 80/1e6 * 0.10
guard_b    = 48_000 * 3.6 * 0.15/1000
# Student: scale-to-0, active 12hr/day = 360hr/month
student_b  = 360 * 1.9712
llm_b = nova_lite + nova_mic_b + nova_pro + cohere_b + guard_b + student_b

ft_b = (10_000 * 500/1e6 * 0.54 + 10_000 * 300/1e6 * 3.40) + 3 * 1.315
infra_b = infra_a  # same infra

total_b = llm_b + ft_b + infra_b

# ── VERSION C ─────────────────────────────────────────────────────────────────
qflash_em  = 30_000 * 1500/1e6 * 0.05 + 30_000 * 300/1e6 * 0.20
qflash_r   = 120_000 * 500/1e6 * 0.05 + 120_000 * 40/1e6 * 0.20
qplus_sp   = 120_000 * 3000/1e6 * 0.115 + 120_000 * 600/1e6 * 0.688
embed_c    = 150_000 * 80/1e6 * 0.07
rerank_c   = 120_000 * 3600/1e6 * 0.10
ctx_c      = -0.40 * qplus_sp
# Student: PAI-EAS min=1, 85% utilization factor
student_c  = 720 * 1.50 * 0.85
llm_c = qflash_em + qflash_r + qplus_sp + embed_c + rerank_c + ctx_c + student_c

ft_c = (10_000 * 500/1e6 * 0.115 + 10_000 * 300/1e6 * 0.688) + 4 * 1.50
infra_c = (2*720*0.24 + 720*0.42 + 720*0.083 +
           150_000*2*0.5*0.0000167 + 0.15*3.50 + 50*0.10 +
           200*0.02 + 10*0.35 + 0.15*0.50 + 720*0.15 + 500*0.10)

total_c = llm_c + ft_c + infra_c

# ── Print ─────────────────────────────────────────────────────────────────────
def rnd(x): return round(x/50)*50

print("=== VERSION A: AWS + Claude ===")
print(f"  LLM:   ${llm_a:,.0f}  (Haiku ${haiku_em:.0f} + Sonnet ${sonnet_sp:.0f} + cache {cache_a:.0f})")
print(f"  Infra: ${infra_a:,.0f}")
print(f"  Total: ${total_a:,.0f}  range: ${rnd(total_a*1.10):,} – ${rnd(total_a*1.20):,}")

print("\n=== VERSION B: AWS + Qwen ===")
print(f"  Nova LLM base: ${nova_lite+nova_mic_b+nova_pro+cohere_b+guard_b:,.0f}")
print(f"  Student EP (scale-to-0, 360hr): ${student_b:,.0f}  (saves ${720*1.9712-student_b:.0f} vs always-on)")
print(f"  LLM+Student: ${llm_b:,.0f}")
print(f"  Fine-tune: ${ft_b:,.0f}")
print(f"  Infra: ${infra_b:,.0f}")
print(f"  Total: ${total_b:,.0f}  range: ${rnd(total_b*1.10):,} – ${rnd(total_b*1.20):,}")
print(f"  vs Version A: {(total_b/total_a-1)*100:+.0f}%")

print("\n=== VERSION C: Alibaba Cloud ===")
print(f"  Qwen LLM base: ${qflash_em+qflash_r+qplus_sp+embed_c+rerank_c+ctx_c:,.0f}")
print(f"  Student EP (PAI-EAS min=1, 85% util): ${student_c:,.0f}  (saves ${720*1.50-student_c:.0f} vs always-on)")
print(f"  LLM+PAI-EAS: ${llm_c:,.0f}")
print(f"  Fine-tune: ${ft_c:,.0f}")
print(f"  Infra: ${infra_c:,.0f}")
print(f"  Total: ${total_c:,.0f}  range: ${rnd(total_c*1.10):,} – ${rnd(total_c*1.20):,}")
print(f"  vs Version A: {(total_c/total_a-1)*100:+.0f}%")

print("\n=== FINAL SLIDE NUMBERS ===")
for ver, tot in [("A", total_a), ("B", total_b), ("C", total_c)]:
    print(f"  Version {ver}: ${rnd(tot*1.10):,} – ${rnd(tot*1.20):,} / month  (base ${tot:,.0f})")

# Export for use in slide script
print("\n# Paste into build_cost_slides_v2.py:")
for ver, tot, llm, ft, infra, ep, ep_note in [
    ("A", total_a, llm_a, 0, infra_a, 0, ""),
    ("B", total_b, llm_b, ft_b, infra_b, student_b, f"scale-to-0, 360hr/mo"),
    ("C", total_c, llm_c, ft_c, infra_c, student_c, f"PAI-EAS min=1, 85% util"),
]:
    lo, hi = rnd(tot*1.10), rnd(tot*1.20)
    print(f"  V{ver}: LLM ${llm:,.0f}  FT ${ft:,.0f}  Infra ${infra:,.0f}  Total ${lo:,}–${hi:,}")
