'''
Performance and accuracy of HyperLogLog
'''
import time, logging, random
from datasketch.hyperloglog import HyperLogLogPlusPlus

logging.basicConfig(level=logging.INFO)

# Produce some bytes
int_bytes = lambda x : ("a-%d-%d" % (x, x)).encode('utf-8')

def run_perf(card, p):
    h = HyperLogLog(p=p)
    logging.info("HyperLogLog using p = %d " % p)
    start = time.clock()
    for i in range(card):
        h.update(int_bytes(i))
    duration = time.clock() - start
    logging.info("Digested %d hashes in %.4f sec" % (card, duration))
    return duration


def run_acc_weighted(size, seed, p, weight_high, weight_low):
    logging.info("HyperLogLog using p = %d " % p)
    h = HyperLogLogPlusPlus(p=p)
    mapping = {}
    random.seed(seed)
    for i in range(size):
        rand = random.randint(1, size)
        v = int_bytes(rand)
        rand_weight = mapping.get(v, random.uniform(weight_low, weight_high) ** 2)
        h.update(v, rand_weight)
        mapping[v] = rand_weight
    actual_weight = sum(mapping.values())
    perr = abs(actual_weight - h.count(True)) / actual_weight
    return perr

def run_acc_unweighted(size, seed, p):
    logging.info("HyperLogLog using p = %d " % p)
    h = HyperLogLogPlusPlus(p=p)
    mapping = {}
    random.seed(seed)
    for i in range(size):
        rand = random.randint(1, size)
        v = int_bytes(rand)
        h.update(v)
        mapping[v] = 1
    actual_weight = sum(mapping.values())
    perr = abs(actual_weight - h.count(False)) / actual_weight
    return perr

ps = range(4, 17)
output = "hyperloglog_benchmark.png"

logging.info("> Running performance tests")
card = 5000
#run_times = [run_perf(card, p) for p in ps]

logging.info("> Running accuracy tests")
size = 500000
errs_weighted = [run_acc_weighted(size, 1, p, 15, .1) for p in ps]
errs_unweighted = [run_acc_unweighted(size, 1, p) for p in ps]

logging.info("> Plotting result")
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig, axe = plt.subplots(1, 2, sharex=True, figsize=(10, 4))
ax = axe[1]
#ax.plot(ps, run_times, marker='+')
ax.set_xlabel("P values")
ax.set_ylabel("Running time (sec)")
ax.ticklabel_format(axis='y', style='sci', scilimits=(-2,2))
ax.set_title("HyperLogLog performance")
ax.grid()
ax = axe[0]
ax.plot(ps, errs_weighted, marker='+')
ax.plot(ps, errs_unweighted, marker='+')
ax.set_xlabel("P values")
ax.set_ylabel("Error rate in cardinality estimation")
ax.set_title("HyperLogLog accuracy")
ax.grid()

fig.savefig(output)
logging.info("Plot saved to %s" % output)
