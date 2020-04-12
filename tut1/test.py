from brian2 import *
import matplotlib.pyplot as plt

N = 100
tau = 10*ms
duration = 1000*ms
v0_max = 3.
sigma = 0.2

eqs="""
dv/dt = (v0 - v)/tau + sigma*xi*tau**-.5: 1 (unless refractory)
v0 : 1
"""

G = NeuronGroup(N, eqs, threshold='v>1.0', reset='v = 0', refractory=5*ms, method='euler')
M = StateMonitor(G, 'v', record=0)
S = SpikeMonitor(G)

G.v0 = 'i*v0_max / (N-1)'

run(duration)

plt.subplot(121)
plt.plot(S.t/ms, S.i, '.')
plt.xlabel('Time (ms)')
plt.ylabel('Index')
plt.subplot(122)
plt.plot(G.v0, S.count/duration)
plt.show()
