"""Compare the CGA dumps of two bench.py runs: python compare.py DIR1 DIR2"""
import os, sys

d1, d2 = sys.argv[1:3]
names = sorted(os.listdir(d1))
diff = [n for n in names if not os.path.exists(os.path.join(d2, n))
        or open(os.path.join(d1, n)).read() != open(os.path.join(d2, n)).read()]
for n in diff:
    print('DIFF', n)
print('%d screens compared, %d differ' % (len(names), len(diff)))
sys.exit(1 if diff else 0)
