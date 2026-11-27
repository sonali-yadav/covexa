import json, os
from covexa.core.grounded import answer_from_policy

fid = os.environ["COVEXA_SAMPLE_POLICY_FILE_ID"]
cases = [json.loads(l) for l in open("evals/golden_day4.jsonl")]
passed = 0
for c in cases:
    a = answer_from_policy(fid, c["q"])
    ok = a.status == c["expect"]
    passed += ok
    pages = sorted({p.page_from for p in a.citations})
    print(f"{'PASS' if ok else 'FAIL'}  [{a.status:10}] pages={pages}  {c['q']}")

print(f"\n{passed}/{len(cases)} passed")
