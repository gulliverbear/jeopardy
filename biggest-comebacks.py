import glob
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd

def get_winners(df):
    '''
    df: game df
    return list of winning player numbers
    (there can be multiple "winners" if there is a tie)
    '''
    pass
    # TO DO

def get_max_comeback(df, winner_num, d, player_ids, pid_to_name, game_number):
    '''
    '''
    if int(game_number) < 3966:
        multiplier = 2
    else:
        multiplier = 1

    d["max_diff"] = 0
    d["round"] = "J"
    d["clue_#"] = 0
    d["their_score_at_nadir"] = 0
    d["leading_score_at_nadir"] = 0
    d["leader_at_nadir"] = np.nan
    
    for jround in ("J", "DJ"):
        for r in df[df["round"]==jround].sort_values("clue_order").iterrows():
            current_scores = []
            for i in (1,2,3):
                current_scores.append(r[1][f"p{i}_running_total"])
            
            diff = max(current_scores) - r[1][f"p{winner_num}_running_total"]
            diff *= multiplier
                
            if diff > d["max_diff"]:
                d["max_diff"] = diff
                d["round"] = jround
                d["clue_#"] = r[1]["clue_order"]
                d["their_score_at_nadir"] = r[1][f"p{winner_num}_running_total"] * multiplier
                d["leading_score_at_nadir"] = max(current_scores) * multiplier
                
                # find who is currently in lead
                leading_scores = [i for i in (1,2,3) if r[1][f"p{i}_running_total"]==max(current_scores)]
                d["leader_at_nadir"] = ", ".join([pid_to_name[player_ids[i-1]] for i in leading_scores])

i = 0
excluded = 0
rows = []
for csv_file in glob.glob(os.path.join(csv_dir, "*.csv")):
    game = os.path.basename(csv_file)
    season = int(game.split(".")[0])
    game_id = int(game.split(".")[1])
    game_num = int(game.split(".")[2])
    
    if game_id in gameids_to_exclude:
        excluded += 1
        continue
        
    i += 1
    if i % 1000 == 0:
        print(i)
    
    player_ids = (gameid_to_p1id[game_id], gameid_to_p2id[game_id], gameid_to_p3id[game_id])
    df = pd.read_csv(csv_file)
    winner_nums = get_winners(df)
    for winner_num in winner_nums:
        d = {}
        d["game_id"] = game_id
        d["game_number"] = game_num
        d["season"] = season
        d["player_id"] = player_ids[winner_num-1]
        d["player_name"] = pid_to_name[d["player_id"]]
        
        max_diff = get_max_comeback(df, winner_num, d, player_ids, pid_to_name, game_num)
        rows.append(d)
        
cdf = pd.DataFrame(rows)

tdf = cdf.copy()
rename_cols = {"game_number":"game #",
          "max_diff":"deficit",
          "player_name":"player",
          "leader_at_nadir":"leader to catch",
          "clue_#":"clue #",
          "their_score_at_nadir":"player's score",
          "leading_score_at_nadir":"score to catch"}
tdf.rename(columns=rename_cols, inplace=True)
tdf["clue #"] = tdf["clue #"].astype(int)
cols = ["season","game #","round","clue #","player","leader to catch","player's score", "score to catch", "deficit"]
#tdf[cols].sort_values("deficit", ascending=False)[:20]

# get this info for annotating the plot
max_player = tdf.sort_values("deficit").tail(1).player.values[0]
max_deficit = tdf.sort_values("deficit").tail(1).deficit.values[0]
max_game_num = tdf.sort_values("deficit").tail(1)["game #"].values[0]
#max_game_num

fontsize=24
fig, ax = plt.subplots(figsize=(17,17))
ax.hist(cdf["max_diff"], bins = 25, edgecolor="k", alpha=0.5)
ax.set_ylabel("# of games", fontsize=fontsize)
ax.set_xlabel("largest deficit overcome", fontsize=fontsize)

ax.annotate("\n".join([max_player, f"deficit: ${max_deficit}", f"game # {max_game_num}"]),
            xy=(tdf["deficit"].max(),1), xytext=(0, 50), color='r', fontsize=fontsize,
            textcoords='offset points', ha='right', va='bottom',
            bbox=dict(boxstyle='round,pad=0.5', fc='white', alpha=0.5),
            arrowprops=dict(arrowstyle = '->', connectionstyle='arc3,rad=0'))

fig.tight_layout()
output_file = "deficit-distribution.png"
output_file = os.path.join(output_dir, output_file)
fig.savefig(output_file, facecolor='white', transparent=False)
