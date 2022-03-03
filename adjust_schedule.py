### This is the code for adjusting schedule. 
### Candidates of combination of days are suggested in two stages. 

import pandas as pd
import numpy as np
import itertools

# params
n_days = 3
char_map = {'x':0, 's':1, 'o':5}

# set data

## read data
data = pd.read_csv("./data.csv")

## convert char -> int
people_cols = data.columns.drop(["day"])
for col in people_cols:
	data[col] = data[col].map(char_map).astype(int)

## set index of row as day
data.set_axis(np.array(data["day"]), axis='index',inplace=True)



# generate candidates of combination of days
comb = list(itertools.combinations(data["day"], n_days))
data.drop(["day"],axis=1,inplace=True)
print("#days", n_days)


# check each candidate
df_candidates = pd.DataFrame(columns=["n","max","comb"])
max_join_score = 0
for c in comb:
	## get each candidate
	candidate_rows = data.filter(items=c, axis='index')

	## reduce rows
	max_rows = candidate_rows.max(axis=0)
	join_score = max_rows.sum()
	df_candidates = df_candidates.append({"n":join_score,"max":max_rows,"comb":c},ignore_index=True)
	
	## max join score
	if max_join_score < join_score:
		max_join_score = join_score;



# intermediate candidates by n_inconvenient
df_intermediate_candidates = df_candidates[df_candidates["n"] == max_join_score]

print("intermediate result")
print("max join score",max_join_score)
print("n_candidates",df_intermediate_candidates.shape[0])



# try to make people with more "o" or "s" join
## number of 'x', 's', and 'o' for each person
n_x = data.shape[0] - np.count_nonzero(data.where(data == char_map['x']).isna(),axis=0)
n_s = data.shape[0] - np.count_nonzero(data.where(data == char_map['s']).isna(),axis=0)
n_o = data.shape[0] - np.count_nonzero(data.where(data == char_map['o']).isna(),axis=0)

## convert these arrays to DataFrame with names
n_x = pd.DataFrame(n_x.reshape(1,n_x.size), columns=data.columns)
n_s = pd.DataFrame(n_s.reshape(1,n_x.size), columns=data.columns)
n_o = pd.DataFrame(n_o.reshape(1,n_x.size), columns=data.columns)



# calculate score for each candidate
scores = []
for i in range(df_intermediate_candidates.shape[0]):
	## get data from data frame
	max_rows = df_intermediate_candidates.iloc[i,1]
	comb = df_intermediate_candidates.iloc[i,2]

	## get list of people who are inconvenient
	who_is_inconvenient = list(data.columns[max_rows == 0])

	## get score of them
	## score is the sum of #o and #s of the people who can't join
	score = n_o[who_is_inconvenient].sum(axis=1)[0] * char_map['o'] + n_s[who_is_inconvenient].sum(axis=1)[0] * char_map['s']
	scores.append(score)
	print(comb, score, data.columns[max_rows == 0])


# get indices with min score
## it means that people who marked "o" or "s" more are likely to be choosen
final_idxs = [i for i, x in enumerate(scores) if x == min(scores)]

# print final candidates
print("final result")
for final_idx in final_idxs:
	## get data of final candidate
	final_sum_rows = df_intermediate_candidates.iloc[final_idx,1]
	final_comb = df_intermediate_candidates.iloc[final_idx,2]

	print("score", scores[final_idx])
	print("days", final_comb)
