#!/usr/local/bin/python
import json
import os, shutil, itertools
from datetime import datetime

with open('/work/news/FaceCloud/Web/server/data/topic_to_persons_kw-all.json') as f:
    data = json.load(f)

search = "nuclear"

ouput_folder = '/work/news/FaceCloud/Web/server/data/muxviz/'
ouput_folder = '/work/muxviz/muxViz-master/data/'
ouput_folder = os.path.join(ouput_folder, search)
search_path = os.path.join('data/', search+'/')
if os.path.isdir(ouput_folder):
    shutil.rmtree(ouput_folder)

if not os.path.isdir(ouput_folder):
    os.makedirs(ouput_folder)

k2res = {}
res2time = {}
time2res = {}
res_list = []
layout_filename = search+'_layout.txt'
layout_file = [['nodeID', 'nodeLabel']]

resID = 0
for x in data:

    for k in data[x]:
        if x in res_list:
            break
        if search in k.lower():
            res_list.append(x)
            layout_file.append([str(resID), x])

            date = datetime.strptime(x.split('-')[0][:10],'%Y_%m_%d')
            res2time[resID] = date
            time2res[date] = time2res.get(date, [])+[resID]

            resID += 1

with open(os.path.join(ouput_folder, layout_filename), 'w') as f:
    for l in layout_file:
        f.write(' '.join(l)+'\n')

res_list = list(set(res_list))
print len(res_list)

for res in res_list:
    klist = data[res]
    for k in klist:
        k2res[k] = k2res.get(k, []) + [res]

layerID = 0
layer_list = []
#layer_info_file = [['layerID', 'layerLabel']]
configuration_file = []

source_min = 20
#source_min = 40

layer2edges = {}

for k,rlist in k2res.iteritems():
    if(len(rlist)) > source_min:
        layer_filename = search+'_%03d.edges'%layerID
        layerLabel = k.strip().replace(' ','_')
        #configuration_file.append([layer_filename, layerLabel, os.path.join(search_path,layout_filename)])
        configuration_file.append([search_path+layer_filename, layerLabel, search_path+layout_filename])
        layerID += 1

        edge_list = []
        nlist = [str(res_list.index(r)) for r in rlist]
        edges = itertools.combinations(nlist, 2)
        for e in edges:
            edge_list.append(list(e)+[str(1)])
            layer2edges[layerID] = layer2edges.get(layerID, []) + [e]

        with open(os.path.join(ouput_folder, layer_filename), 'w') as f:
            for l in edge_list:
                f.write(' '.join(l)+'\n')


configuration_filename = search+'_config.txt'
with open(os.path.join(ouput_folder, configuration_filename), 'w') as f:
    for l in configuration_file:
        f.write(';'.join(l)+'\n')

timeline_file = [['timeStep','labelStep', 'entity', 'layerID', 'nodeID', 'color', 'sizeFactor']]

print layerID


day_padding = 30
day_padding = 90
prev_date = datetime(1980,01,01)
tf2res = {}
tf2label = {}
tfID = -1
for d in sorted(time2res):
    day_delta = (d-prev_date).days
    if day_delta <= day_padding:
        tf2res[tfID] = tf2res.get(tfID, []) + time2res[d]
        tf2label[tfID][1] = d
    else:
        tfID += 1
        tf2res[tfID] = tf2res.get(tfID, []) + time2res[d]
        tf2label[tfID] = [d,d]

    prev_date = d

print tfID

old_nodes = '#fee0d2'
old_nodes_interacting = '#fc9272'
new_nodes = '#fc9272'
future_nodes = '#ffffff'
old_edges = '#fee6ce'
old_edges_interacting = '#fdae6b'
new_edges = '#e6550d'
future_edges = '#ffffff'

timeline_file = [['timeStep','labelStep', 'entity', 'layerID', 'nodeID', 'color', 'sizeFactor']]

old_node_list = []


for tf,(d0,d1) in tf2label.iteritems():
    label = d0.strftime('%Y/%m/%d') + '__' + d0.strftime('%Y/%m/%d') + '__(%d)'%((d1 - d0).days+1)
    new_node_list = sorted(tf2res[tf])
    node2line = {}

    for l, elist in layer2edges.iteritems():
        for (n1,n2) in elist:
            n1 = int(n1)
            n2 = int(n2)
            edge_status = ''
            if n1 in old_node_list and n2 in new_node_list: 
                edge_color = old_edges_interacting
                edge_size = 0.75
                n1_color = old_nodes_interacting
                n2_color = new_nodes
                n1_size = 0.5
                n2_size = 1

            elif n2 in old_node_list and n1 in new_node_list:
                edge_color = old_edges_interacting
                edge_size = 0.75
                n1_color = new_nodes
                n2_color = old_nodes_interacting
                n1_size = 1
                n2_size = 0.5
            elif n1 in old_node_list and n2 in old_node_list:
                edge_color = old_edges
                edge_size = 0.5
                n1_color = old_nodes_interacting
                n2_color = old_nodes_interacting
                n1_size = 0.5
                n2_size = 0.5
            elif n1 in new_node_list and n2 in new_node_list:
                edge_color = new_edges
                edge_size = 1
                n1_color = new_nodes
                n2_color = new_nodes
                n1_size = 1
                n2_size = 1
            else:
                edge_color = future_edges
                edge_size = 0
                n1_color = future_nodes
                n2_color = future_nodes
                n1_size = 0
                n2_size = 0

            if n1 not in node2line:
                node_line = ['%d'%tf, label, 'node', '%d'%l, '%d'%n1, n1_color, '%f'%n1_size]
                node2line[n1] = node_line
                timeline_file.append(node_line)
            if n2 not in node2line:
                node_line = ['%d'%tf, label, 'node', '%d'%l, '%d'%n2, n2_color, '%f'%n2_size]
                node2line[n2] = node_line
                timeline_file.append(node_line)

            edge_line = ['%d'%tf, label, 'edge', '%d'%l, '%d-%d'%(n1,n2), edge_color, '%f'%edge_size]
            timeline_file.append(edge_line)

    old_node_list += new_node_list


timeline_filename = search+'_timeline.txt'
with open(os.path.join(ouput_folder, timeline_filename), 'w') as f:
    for l in timeline_file:
        f.write(' '.join(l)+'\n')








#print tfID


#for t,res in time2res.iteritems():
#    print t, res








