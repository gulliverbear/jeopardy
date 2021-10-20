import collections
import glob
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import scipy.stats

def get_cols_in_order_uninterrupted(df, jround, expected_order):
    sdf = df.sort_values("clue_order")
    
    full_category_chances = 0
    num_in_order = 0
    num_in_order_uninterrupted = 0
    
    for col in range(1,7):
        cdf = sdf[(sdf["column"]==col) & (sdf["round"]==jround)]
        clue_order = list(cdf["row"].values)
        
        
        if len(clue_order) == 5:
            full_category_chances += 1
        
        if clue_order == expected_order:
            num_in_order += 1
            
            last_clue = cdf.tail(1).clue_order.values[0]
            first_clue = cdf.head(1).clue_order.values[0]
            if abs(first_clue - last_clue) == 4: # since 5-1 == 4
                num_in_order_uninterrupted += 1
    in_order_percent = num_in_order / full_category_chances * 100
    in_order_uninterrupted_percent = num_in_order_uninterrupted / full_category_chances * 100
    
    return in_order_percent, in_order_uninterrupted_percent

def get_clue_orders(df, jround):
    '''
    df: game df
    jround: J or DJ
    return a list of lists of the clue orders
    ie [[1,2,3,4,5],[5,4,3,2,1],...]
    would mean 1st column went in order, and 2nd column went in reverse order
    '''
    # TO DO
    pass

def get_first_clue_rank(game_to_orders):
    '''
    game_to_orders: dict of dict of dict 
    [game csv file][jround] = [[1,2,3,4,5],[,1,2,4,3,5],...]
    creates a dataframe with the mean of the 1st clue picked for each column
    one column for J, one column for DJ
    '''
    rows = []
    for game, val in game_to_orders.items():
        d = {}
        game_num = int(game.split(".")[2])
        game_id = int(game.split(".")[1])
        season = int(game.split(".")[0])
        for jround in ("J","DJ"):
            orders = val[jround]
            orders = [i[0] for i in orders if i]
            d[f"{jround}_mean"] = np.mean(orders)
        d["season"] = season
        d["game_number"] = game_num
        d["game_id"] = game_id
        rows.append(d)
    order_df = pd.DataFrame(rows)
    order_df.sort_values(by=["season", "game_number"], inplace=True)
    order_df = order_df[["season", "game_id","game_number", "J_mean", "DJ_mean"]]
    order_df.reset_index(inplace=True, drop=True)
    return order_df

def plot_order(ax, df, suffix, window_size, jround, annotations):    
    '''
    '''
    window_vals = []
    for i in range(len(df)-window_size):
        x = df[i:i+window_size][f"{jround}{suffix}"].mean()
        window_vals.append(x)

    ax.plot(range(1,len(df)+1), df[f"{jround}{suffix}"], ".", markersize=5, color="gray", alpha=0.5)
    ax.plot(range(0, len(df)-window_size), window_vals, color="red", linewidth=1, linestyle="-")
    
    for name, xval, yval in annotations:
        ax.annotate(name,
                    xy=(xval,yval), xytext=(-20, 20),
                    textcoords='offset points', ha='right', va='bottom',
                    bbox=dict(boxstyle='round,pad=0.5', fc='white', alpha=0.5),
                    arrowprops=dict(arrowstyle = '->', connectionstyle='arc3,rad=0'))
