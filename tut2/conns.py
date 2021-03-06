from brian2 import *
import matplotlib.pyplot as plt

N = 30
neuron_spacing = 50*umetre
width = N/4.0*neuron_spacing

# Neuron has one variable x, its position
G = NeuronGroup(N, 'x : metre')
G.x = 'i*neuron_spacing'

# All synapses are connected (excluding self-connections)
S = Synapses(G, G, 'w : 1')
S.connect(condition='i!=j')
# Weight varies with distance
S.w = 'exp(-(x_pre-x_post)**2/(2*width**2))'

plt.scatter(S.x_pre/um, S.x_post/um, S.w*20)
plt.xlabel('Source neuron position (um)')
plt.ylabel('Target neuron position (um)')
plt.show()
