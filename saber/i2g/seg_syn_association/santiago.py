# Copyright 2019 The Johns Hopkins University Applied Physics Laboratory
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Santiago Spine Simulation

# two modes eventually - networkx and adj matrix

def gini(list_of_values):
    # from http://planspace.org/2013/06/21/how-to-calculate-gini-coefficient-from-raw-data-in-python/
    sorted_list = sorted(list_of_values)
    height, area = 0, 0
    for value in sorted_list:
        height += value
        area += height - value / 2.
    fair_area = height * len(list_of_values) / 2.
    return (fair_area - area) / fair_area


def line_graph(edgelist):
    import numpy as np
    #edgelist has three columns:  syn, neu1, neu2.  Undirected graph only.
    # assume that each line represents a valid edge
    import itertools

    synId = edgelist[:,0]
    line_graph = np.zeros([len(synId),len(synId)])

    neuConn = edgelist[:,1:]
    nId = np.unique(neuConn)

    for neuron in nId:

        dataR, dataC = np.where(neuConn == neuron)
        #print dataR
        #sIdMatch = np.unique(edgeList[dataR,0]);
        sIdMatch = np.unique(dataR) # these are already the rows
        for n in itertools.combinations(sIdMatch,2):
            s1 = n[0]
            s2 = n[1]
            line_graph[s1,s2] += 1

    line_graph = line_graph + line_graph.T # make full matrix

    line_graph[line_graph > 0] = 1 #binary, full, undirected
    return line_graph


#def neuron_graph(edgelist):
    #edgelist has three columns:  syn, neu1, neu2.  Undirected graph only.

# All neurons not represented have degree 0
# syn-neuron: Any neuron
#neuGraph = zeros(length(nId));
#for i = 1:size(neuConn,1)
#    n1 = neuConn(i,1);
#    n2 = neuConn(i,2);

#    n1 = find(n1 == nId);
#    n2 = find(n2 == nId);
#    neuGraph(min(n1,n2),max(n1,n2)) = neuGraph(min(n1,n2),max(n1,n2)) + 1;

def graph_error(true_graph,test_graph):
    # works on aligned binary full line graph adjacency matrices only at the moment
    import numpy as np
    true_graph = true_graph > 0
    test_graph = test_graph > 0

    true_graph = np.ravel(true_graph)
    test_graph = np.ravel(test_graph)

    tp = np.sum(np.logical_and(true_graph == 1, test_graph == 1))
    fn = np.sum(np.logical_and(true_graph == 1, test_graph == 0))
    fp = np.sum(np.logical_and(true_graph == 0, test_graph == 1))
    tn = np.sum(np.logical_and(true_graph == 0, test_graph == 0))

    precision = 0
    recall = 0

    if tp + fp > 0:
        precision = 1.0*tp/(tp+fp)

    if tp + fn > 0:
        recall = 1.0*tp/(tp+fn)

    if (precision == 0) or (recall == 0):
        f1 = 0
    else:
        f1 = (2.0*precision*recall)/(precision+recall)
    print('precision: ' + str(precision))
    print('recall: ' + str(recall))
    print('f1: ' + str(f1))
    return f1

def spine_fragment(edge_list, spineidx, pct_loss):
    shuffle_spineidx = np.random.permutation(spineidx)
    shuffle_spineidx = shuffle_spineidx[0:int(round(1.0*len(shuffle_spineidx)/100*pct_loss))]

    edge_list[shuffle_spineidx,2] = cmatrix[shuffle_spineidx,7]
    lg_test = line_graph(edge_list)
    return lg_test

def edge_list_cv(neurons, synapses, dilation=3):

    from scipy.stats import mode
    import numpy as np
    import skimage.morphology as morpho

    synapses_dil = np.zeros_like(synapses)

    for z in range(0,synapses.shape[2]):
        synapses_dil[:,:,z] = morpho.dilation(synapses[:,:,z], selem=morpho.disk(5))    # find synapse objects

    synid = np.unique(synapses_dil)
    synid = synid[synid > 0]
    print(len(synid))

    neusynlist = []
    for s in synid:
        m1 = 0
        m2 = 0
        #print str(s).zfill(4),
        try:
            val = np.ravel(neurons[synapses_dil == s])
            val = val[val > 0]
            m1 = mode(val)[0][0]
            val = val[val != m1]
            m2 = mode(val)[0][0]
        except:
            print('skipping this id')
        neusynlist.append([s, m1, m2])
    neusynlist = np.asarray(neusynlist)
    return neusynlist

def edge_list_ramon(neuron_token, neuron_channel, synapse_token, synapse_channel):
    return 0

def remap_ids(edge_list, lut_source, lut_target):
    import numpy as np
    from copy import copy
    out = copy(edge_list)
    lut_source = np.asarray(lut_source)
    lut_target = np.asarray(lut_target)
    if len(lut_source) != len(lut_target):
        raise('error invalid lengths')

    el_neurons = out[:,1:3]
    for i in range(0, len(lut_source)):
        el_neurons[el_neurons == lut_source[i]] = lut_target[i]

    out[:,1:3] = el_neurons
    return out

def transitive_closure():
    pass