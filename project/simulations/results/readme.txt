gifs are in folders according to the used election system
(AP = approval, IR = instant runoff, FPTP = first past the post)

gifs folder format:
[notebook_name]_v[first letter of voter strategy used]_c[first letter of candidate approach used]

vH = only HONEST voter agents
vL = only LOYALIST voter agents
vP = only POPULIST voter agents
vR = only RANDOM (for exp1u/exp1n) or only REALIST (for other notebooks) voter agents
vC = custom voter agents composition, ratios specified in the notebook

cR = only RANDOM candidate agents
cH = only HONEST candidate agents
cD = only DEFENSIVE candidate agents
cO = only OFFENSIVE candidate agents
cM = mixed candidate agents composition, ratios specified in the notebook

For exp1n and exp1u, vR means voter RANDOM, while for others, it means voter REALIST.
If the specification of a strategy is omitted in the name, it is considered HONEST.

examples:
exp1n_vR_cH means notebook Exp1n.ipynb, RANDOM voter agents, HONEST candidate agents
exp4_vR means notebook Exp4.ipynb, REALIST voter agents, HONEST candidate agents
exp2_cO2 means notebook Exp2.ipynb, HONEST voter agents, OFFENSIVE candidate agents, second (alternative) run

Plots folder contains the quantitative statistics and long term vote share dynamics of the simulations.
The folder hieararchy and plot names indicate to which notebooks and simulations each plot corresponds to.
