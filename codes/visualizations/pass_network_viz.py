import pandas as pd
from utilites.utilites import Pitch_class, add_locations
from utilites.data_loading import home_team,home_event,away_event,home_passes,away_passes
from utilites.dictionary import my_dictionary as dct

def pass_network(passes, event):
    #Plotting pass network visualization
    
    #sperate locations from [x,y] to x column y column
    passes = add_locations(passes)
    
    #Unsuccessfull passes have unsuccessfull info. But success passes don't. So, fill nan values.
    passes[dct['pass_outcome']].fillna(dct['Success'], inplace=True)
    passes_success = passes[passes[dct['pass_outcome']] == dct['Success']]
    
    #We create pass network until first substitution.
    subs = event[event[dct['type']] == dct['Substitution']]
    subs = subs[dct['minute']]
    first_sub = subs.min()
    
    passes_success = passes[passes[dct['minute']] < first_sub]     #get all passes until first substitution
    pas = pd.to_numeric(passes_success[dct['player_id']], downcast='integer') #Passer id
    rec = pd.to_numeric(passes_success[dct['pass_recipient_id']], downcast='integer') #Pass recipient id
    passes_success[dct['player_id']] = pas #success passers
    passes_success[dct['pass_recipient_id']] = rec #success pass recipients
    average_locations = passes_success.groupby(dct['player_id']).agg({dct['x'] : ['mean'], dct['y']:[dct['mean'], dct['count']]}) #SQL code. Groups players by mean(x) and mean(y)
    average_locations.columns = [dct['x'], dct['y'], dct['count']]
    pass_between = passes_success.groupby([dct['player_id'], dct['pass_recipient_id']]).id.count().reset_index() #SQL code. Groups passers and recipients
    pass_between.rename({dct['id']:dct['pass_count']}, axis='columns', inplace=True)
    pass_between = pass_between.merge(average_locations, left_on=dct['player_id'], right_index=True)
    pass_between = pass_between.merge(average_locations, left_on=dct['pass_recipient_id'], right_index=True, suffixes=['', dct['_end']])
    pass_between = pass_between[pass_between[dct['pass_count']] > 3]
    
    return pass_between, average_locations

def plot_pn_viz(pass_between, average_locations):
    pitch = Pitch_class()
    pitch, fig, ax = pitch.create_pitch()
    pitch.arrows(1.2*pass_between.x, .8*pass_between.y, 1.2*pass_between.x_end, .8*pass_between.y_end, ax=ax,
                      width = 3, headwidth = 3, color='black', zorder=1, alpha = .5)

    pitch.scatter(1.2*average_locations.x, .8*average_locations.y, s = 300, color = '#d3d3d3', edgecolors = 'black',
                     linewidth = 2.5, alpha = 1, zorder = 1, ax=ax)

def pn_main(team):
    if team == home_team: #home team's pass network
        home_pass_between, home_average_locations = pass_network(home_passes, home_event) #gets home passes and average locations
        plot_pn_viz(home_pass_between, home_average_locations) #Plots
    else:
        away_pass_between, away_average_locations = pass_network(away_passes, away_event)
        plot_pn_viz(away_pass_between, away_average_locations)
    


