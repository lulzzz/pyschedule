from __future__ import absolute_import as _absolute_import

#! /usr/bin/env python
'''
Copyright 2015 Tim Nonner

Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
'''



def plot(scenario,img_filename=None,resource_height=1.0,show_task_labels=True,color_prec_groups=False,hide_tasks=[],task_colors=dict(),fig_size=(15,5)) :
	"""
	Plot the given solved scenario using matplotlib

	Args:
		scenario:    scenario to plot
		kind:        the MIP-solver to use: CPLEX, GLPK
		msg:         0 means no feedback (default) during computation, 1 means feedback
		lp_filename: if set, then a .lp file will be written here

	Returns:
		0: good
	"""
	try :
		import matplotlib.patches as patches, matplotlib.pyplot as plt
	except :
		raise Exception('ERROR: matplotlib is not installed')
	import random

	S = scenario
	# trivial connected components implementation to avoid
	# having to import other packages just for that
	def get_connected_components(edges) :
		comps = dict()
		for v,u in edges :
			if v not in comps and u not in comps :
				comps[v] = v
				comps[u] = v
			elif v in comps and u not in comps :
				comps[u] = comps[v]
			elif v not in comps and u in comps :
				comps[v] = comps[u]
			elif v in comps and u in comps and comps[v] != comps[u] :
				old_comp = comps[u]
				for w in comps :
					if comps[w] == old_comp :
						comps[w] = comps[v]
		# replace component identifiers by integers startting with 0
		values = list(comps.values())
		comps = { T : values.index(comps[T]) for T in comps }
		return comps

	tasks = [ T for T in S.tasks() if T not in hide_tasks ] #TODO: upload since hide_tasks might contain string
	#tasks = S.tasks()
	
	# get connected components dict for coloring
	# each task is mapping to an integer number which corresponds
	# to its connected component
	edges = [ (str(T),str(T)) for T in tasks ]
	if color_prec_groups :
		edges += [ (str(T),str(T_)) for P in set(S.precs_lax()) | set(S.precs_tight()) \
	                   for T in P.tasks() for T_ in P.tasks() \
                           if T in tasks and T_ in tasks ]
	comps = get_connected_components(edges)

	# color map
	colors = ['#7EA7D8','#A1D372','#EB4845','#7BCDC8','#FFF79A'] #pastel colors
	#colors = ['red','green','blue','yellow','orange','black','purple'] #basic colors
	colors += [ [ random.random() for i in range(3) ] for x in range(len(S.tasks())) ] #random colors
	# replace colors with fixed task colors		
	for T in task_colors : colors[comps[str(T)]] = task_colors[T]
	color_map = { T : colors[comps[T]] for T in comps }

	solution = S.solution()
	hide_tasks_str = [ str(T) for T in hide_tasks ]
	solution = [ (T,R,x,y) for (T,R,x,y) in solution if T not in hide_tasks_str ] #tasks of zero length are not plotted

	# resources list incl null resource
	resources = sorted(list(set([ R for (T,R,x,y) in solution ])))

	# plot solution
	#fig = plt.figure()
	fig, ax = plt.subplots(1, 1, figsize=fig_size)
	#ax = fig.add_subplot(111, aspect='equal')
	for (T,R,x,x_) in solution :
		y = resources.index(R)*resource_height
		ax.add_patch(
		    patches.Rectangle(
			(x, y),       # (x,y)
			max(x_-x,0.5),   # width
			resource_height,   # height
			color = color_map[T],
		    )
		)
		if show_task_labels :
			plt.text(x,y+0.1*resource_height,str(T),fontsize=14,color='black')	

	# format graph
	plt.title(str(S))	
	plt.yticks([ resource_height*x + resource_height/2.0 for x in range(len(resources)) ],resources)
	plt.ylim(0,resource_height*len(resources))
	plt.xlim(0,max([ x_ for (I,R,x,x_) in solution ]))
	if img_filename :
		fig.figsize=(1,1)
		plt.savefig(img_filename,dpi=200,bbox_inches='tight')
	else :
		plt.show()

	return 0


