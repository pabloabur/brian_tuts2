from brian2 import *

# ###########################################
# Defining network model parameters
# ###########################################

NE = 8000          # Number of excitatory cells
NI = 8000#NE/4          # Number of inhibitory cells

#num_poisson = 1000
#poisson_rates = [x for x in range(5, 30, 2)]*Hz
#poisson_deltav = 1e-3*volt

tau_ampa = 5.0*ms   # Glutamatergic synaptic time constant
tau_gaba = 10.0*ms  # GABAergic synaptic time constant
epsilon = 0.02      # Sparseness of synaptic connections

tau_stdp = 20*ms    # STDP time constant

simtime = 100*ms#10*second # Simulation time
selected_trials = [2, 6, 9]

# ###########################################
# Neuron model
# ###########################################

gl = 10.0*nsiemens   # Leak conductance
el = -60*mV          # Resting potential
ers = {'shunt': -60*mV, 'hyp': -80*mV}          # Inhibitory reversal potential
vt = -50.*mV         # Spiking threshold
memc = 200.0*pfarad  # Membrane capacitance
#bgcurrent = 200*pA   # External current
bgcurrents = [0, 0, 0, 50, 50, 50, 50, 150, 150, 150]*pA#range(325, 350, 2)*pA

# ###########################################
# Initialize neuron group
# ###########################################
eqs_neurons='''
dv/dt=(-gl*(v-el)-g_ampa*v-g_gaba*(v-er)+bgcurrent)/memc : volt (unless refractory)
dg_ampa/dt = -g_ampa/tau_ampa : siemens
dg_gaba/dt = -g_gaba/tau_gaba : siemens
'''

neurons = NeuronGroup(NE+NI, model=eqs_neurons, threshold='v > vt',
                      reset='v=el', refractory=5*ms, method='euler')
neurons.v = el
Pe = neurons[:NE]
Pi = neurons[NE:]

# ###########################################
# Connecting the network
# ###########################################

con_e = Synapses(Pe, neurons, on_pre='g_ampa += 0.3*nS')
con_e.connect(p=epsilon)
con_ii = Synapses(Pi, Pi, on_pre='g_gaba += 3*nS')
con_ii.connect(p=epsilon)
#con_input = Synapses(input_spikes, Pe, on_pre='v+=poisson_deltav')
#con_input.connect(p=epsilon)

# ###########################################
# Inhibitory Plasticity
# ###########################################

eqs_stdp_inhib = '''
w : 1
dapre/dt=-apre/tau_stdp : 1 (event-driven)
dapost/dt=-apost/tau_stdp : 1 (event-driven)
'''
alpha = 3*Hz*tau_stdp*2  # Target rate parameter
gmax = 100               # Maximum inhibitory weight

con_ie = Synapses(Pi, Pe, model=eqs_stdp_inhib,
              on_pre='''apre += 1.
                     w = clip(w+(apost-alpha)*eta, 0, gmax)
                     g_gaba += w*nS''',
              on_post='''apost += 1.
                      w = clip(w+apre*eta, 0, gmax)
                   ''')
con_ie.connect(p=epsilon)
con_ie.w = 0.1

# ###########################################
# Setting up monitors
# ###########################################
sm = SpikeMonitor(Pe)
vm = StateMonitor(Pe, 'v', record=0)
pop_rate = PopulationRateMonitor(Pe)

store()

output_rates = {'shunt': [], 'hyp': []}
selected_Vmem = {'shunt': [], 'hyp': []}
#for i, poisson_rate in enumerate(poisson_rates):
#    # Use same poissonian input for each rate
#    poisson_input = PoissonGroup(num_poisson, poisson_rate)
#    poisson_monitor = SpikeMonitor(poisson_input)
#    net = Network(poisson_input, poisson_monitor)
#    net.run(simtime)
#    poisson_spikes = poisson_monitor.i
#    poisson_spike_times = poisson_monitor.t

for i, bgcurrent in enumerate(bgcurrents):
    for key, er in ers.items():
        #input_spikes = SpikeGeneratorGroup(num_poisson, poisson_spikes,
        #                                   poisson_spike_times)

        # ###########################################
        # Run without plasticity
        # ###########################################
        #net = Network(input_spikes, neurons, con_ie, con_ii, con_e, con_input,
        #          sm, vm, pop_rate)
        restore()
        eta = 0          # Learning rate
        neuron_id = 4000
        run(simtime)
        output_rates[key].append(sm.count[neuron_id]/simtime)
        if i in selected_trials:
            selected_Vmem[key].append(vm)

# ###########################################
# Run with plasticity
# ###########################################
#eta = 1e-2          # Learning rate
#run(simtime-1*second, report='text')

# Beyond 1 second the spikes and the firing rate of the population start
# to more sparse and uniform, respectively

# ###########################################
# Make plots
# ###########################################
#subplot(222)
#plot(t/ms, i, 'k.', ms=0.25)
#xlabel("time (ms)")
#yticks([])
#title("After")
#xlim((simtime-0.2*second)/ms, simtime/ms)
print(selected_Vmem)
subplot(231)
plot(selected_Vmem['hyp'][0].t/ms, 1000*selected_Vmem['hyp'][0].v[0], 'r',
     label='hyperpolarization')
plot(selected_Vmem['shunt'][0].t/ms, 1000*selected_Vmem['shunt'][0].v[0], 'b',
     label='shunting')
title('Neuron #0')
xlabel('time (ms)')
ylabel('Voltage (mV)')
legend()

subplot(232)
plot(selected_Vmem['hyp'][1].t/ms, 1000*selected_Vmem['hyp'][1].v[0], 'r',
     label='hyperpolarization')
plot(selected_Vmem['shunt'][1].t/ms, 1000*selected_Vmem['shunt'][1].v[0], 'b',
     label='shunting')
title('Neuron #0')
xlabel('time (ms)')
ylabel('Voltage (mV)')
legend()

subplot(233)
plot(selected_Vmem['hyp'][2].t/ms, 1000*selected_Vmem['hyp'][2].v[0], 'r',
     label='hyperpolarization')
plot(selected_Vmem['shunt'][2].t/ms, 1000*selected_Vmem['shunt'][2].v[0], 'b',
     label='shunting')
title('Neuron #0')
xlabel('time (ms)')
ylabel('Voltage (mV)')
legend()

subplot(234)
plot(sm.t/ms, sm.i, 'k.', ms=0.5)
#title("Before")
xlabel("")
yticks([])
#xlim(0.8*1e3, 1*1e3)

subplot(235)
plot(pop_rate.t/ms, pop_rate.smooth_rate(window='flat', width=0.1*ms)/Hz)
xlabel('time (ms)')
ylabel('Instantaneous firing rate (spikes/s)')

subplot(236)
#plot(poisson_rates, output_rates['shunt'])
#plot(poisson_rates, output_rates['hyp'])
plot(bgcurrents, output_rates['shunt'])
plot(bgcurrents, output_rates['hyp'])
xlabel('input rate')
ylabel('Output rate');

show()
