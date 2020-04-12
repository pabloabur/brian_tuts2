from brian2 import *
import matplotlib.pyplot as plt

N = 1000
tau = 10*ms
vr = -70*mV
vt0 = -50*mV
delta_vt0 = 5*mV
tau_t = 100*ms
sigma = 0.5*(vt0-vr)
v_drive = 2*(vt0-vr)
duration = 100*ms

eqs = '''
dv/dt = (v_drive+vr-v)/tau + sigma*xi*tau**-0.5 : volt
dvt/dt = (vt0-vt)/tau_t : volt
'''

reset = '''
v = vr
vt += delta_vt0
'''

G = NeuronGroup(N, eqs, threshold='v>vt', reset=reset, refractory=5*ms, method='euler')
spikemon = SpikeMonitor(G)
M = StateMonitor(G, 'v', record=0)

G.v = 'rand()*(vt0-vr)+vr'
G.vt = vt0

run(duration)

plt.plot(spikemon.t/ms, spikemon.i, '.')
#_ = plt.hist(spikemon.t/ms, 100, histtype='stepfilled', facecolor='k', weights=ones(len(spikemon))/(N*defaultclock.dt))
#plt.xlabel('Time (ms)')
#plt.ylabel('Instantaneous firing rate (sp/s)');
plt.show()
