import glob
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd

def get_streaks(df, jround, d, player_ids, pid_to_name,):
    # update dict d with info about the longest streak in the round
    max_streak = 0
    max_streak_players = set()
    max_streak_round = None
    for i in (1,2,3):
        streak = 0
        for r in df[df["round"]==jround].sort_values("clue_order").iterrows():
            if r[1][f"p{i}_correct"]:
                streak += 1
                if streak > max_streak:
                    max_streak = streak
                    max_streak_players = set([pid_to_name[player_ids[i-1]]])
                elif streak == max_streak:
                    max_streak_players.add(pid_to_name[player_ids[i-1]])
            else:
                streak = 0
                
    d["max_streak"] = max_streak
    d["max_streak_players"] = sorted(list(max_streak_players))
    d[f"round"] = jround

# use these to get player IDs for each game_id
df = pd.read_csv("games.csv")
gameid_to_p1id = dict(zip(df["game_id"], df["p1_id"]))
gameid_to_p2id = dict(zip(df["game_id"], df["p2_id"]))
gameid_to_p3id = dict(zip(df["game_id"], df["p3_id"]))

p1id_to_name = dict(zip(df["p1_id"], df["p1_name"]))
p2id_to_name = dict(zip(df["p2_id"], df["p2_name"]))
p3id_to_name = dict(zip(df["p3_id"], df["p3_name"]))

pid_to_name = {}
for d in (p1id_to_name, p2id_to_name, p3id_to_name):
    for pid, name in d.items():
        if pid in pid_to_name:
            if pid_to_name[pid] != name:
                raise SystemError(pid, name, d[pid])
        else:
            pid_to_name[pid] = name

rows = []
for csv_file in glob.glob(os.path.join(csv_dir, "*.csv")):
    game = os.path.basename(csv_file)
    season = int(game.split(".")[0])
    game_id = int(game.split(".")[1])
    game_num = int(game.split(".")[2])
    
    player_ids = (gameid_to_p1id[game_id], gameid_to_p2id[game_id], gameid_to_p3id[game_id])
    df = pd.read_csv(csv_file)
    
    for jround in ("J","DJ"):
        d = {}
        d["season"] = season
        d["game_id"] = game_id
        d["game_num"] = game_num
        get_streaks(df, jround, d, player_ids, pid_to_name,)
        rows.append(d)

df = pd.DataFrame(rows)

# make a plot of the histogram of longest streaks
fontsize = 16
fig, ax = plt.subplots(figsize=(10,10))
ax.hist(df["max_streak"], bins=range(0,20,1), edgecolor="k", alpha=0.5)
ax.set_ylim((0,4000))
ax.set_xlabel("# of questions correct in a row", fontsize=fontsize, style="italic")
ax.set_ylabel("# of times that streak length was the max in a round")
ax.annotate("Ken Jennings\n16 correct in a row\nGame #4639",
            xy=(16,1), xytext=(30, 50), color='r', fontsize=fontsize,
            textcoords='offset points', ha='right', va='bottom',
            bbox=dict(boxstyle='round,pad=0.5', fc='white', alpha=0.5),
            arrowprops=dict(arrowstyle = '->', connectionstyle='arc3,rad=0'))
