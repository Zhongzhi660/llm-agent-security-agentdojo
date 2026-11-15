import json, glob
from collections import defaultdict
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
suites=["banking","slack","travel","workspace"]
benign={}; under={}
for s in suites:
    b=[0,0]; u=[0,0]
    for f in glob.glob(f"runs/baseline/gpt-6.1-terra/{s}/user_task_*/none/none.json"):
        d=json.load(open(f)); b[0]+=bool(d["utility"]); b[1]+=1
    for f in glob.glob(f"runs/baseline/gpt-6.1-terra/{s}/user_task_*/important_instructions/*.json"):
        d=json.load(open(f))
        if "utility" in d: u[0]+=bool(d["utility"]); u[1]+=1
    benign[s]=b[0]/b[1]; under[s]=u[0]/u[1]
x=np.arange(len(suites)); w=0.35
fig,ax=plt.subplots(figsize=(6,3.2))
ax.bar(x-w/2,[benign[s]*100 for s in suites],w,label="No attack",color="#4C78A8")
ax.bar(x+w/2,[under[s]*100 for s in suites],w,label="Under attack (imp_instr)",color="#F58518")
ax.set_xticks(x); ax.set_xticklabels(suites); ax.set_ylabel("Task completion (%)"); ax.set_ylim(0,105)
ax.set_title("Benign utility vs. utility under attack (GPT-6.1-terra)"); ax.legend(fontsize=8)
for i,s in enumerate(suites):
    ax.text(i-w/2,benign[s]*100+1,f"{benign[s]:.0%}",ha="center",fontsize=7)
    ax.text(i+w/2,under[s]*100+1,f"{under[s]:.0%}",ha="center",fontsize=7)
fig.tight_layout(); fig.savefig("report/figs/utility_disruption.png",dpi=150)
attacks=["ignore_previous","important_instructions","injecagent","system_message","tool_knowledge"]
asr={}
for a in attacks:
    k=n=0
    for f in glob.glob(f"runs/baseline/gpt-6.1-terra/[bs]*/user_task_*/{a}/*.json"):
        d=json.load(open(f))
        if "utility" in d: k+=bool(d["security"]); n+=1
    asr[a]=(k,n)
fig,ax=plt.subplots(figsize=(6,3))
vals=[asr[a][0]/asr[a][1]*100 for a in attacks]
ax.barh(attacks,vals,color="#E45756")
ax.set_xlabel("Attack success rate (%)"); ax.set_xlim(0,5)
ax.set_title("ASR of 5 published attacks on GPT-6.1 (banking+slack, N=1245)")
for i,a in enumerate(attacks): ax.text(vals[i]+0.05,i,f"{asr[a][0]}/{asr[a][1]}",va="center",fontsize=7)
fig.tight_layout(); fig.savefig("report/figs/asr_by_attack.png",dpi=150)
print("OK", {s:(round(benign[s],2),round(under[s],2)) for s in suites}, asr)
