import requests
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# developed on python 3.8.13
# MIT license, github.com/M055

def get_set_data():
    # Read CSV file
    allsets_df = pd.read_csv('allsetinfo.csv')
    
    # Fix Dates
    allsets_df['Release date'] = [pd.Timestamp(x) for x in allsets_df['Release date']]
    allsets_df.sort_values(by='Release date',inplace=True)
    allsets_df['Released'] = [str(pd.Timestamp(x).month)+'-'+str(pd.Timestamp(x).year) for x in allsets_df['Release date']]
    
    # Add in March of Machines
    dumdf = pd.DataFrame({'Set':'March of Machines','Set code':'MOM','Released':'4-2023'},index=[allsets_df.index.max()+1])
    allsets_df = pd.concat((allsets_df,dumdf))
    
    # Get set codes
    setcodes = allsets_df['Set code'].tolist()
    # NOTE: Timespiral is special...
    # Fix - add in TSB at end
    setcodes = [x[:3] for x in setcodes]
    setcodes.extend(['TSB'])
    
    return allsets_df, setcodes


def query_scryfall(setcodes):
    # Main loop!
    haste_creatures = []
    haste_all = []

    #### DEBUG
    #setcodes = setcodes[:6]
    #setcodes.extend(['TSP','TBP','MOM'])
    
    # Main loop - NB: very important to include the time.sleep(0.11) in the loop
    for scode in setcodes:
        getquery = 'https://api.scryfall.com/cards/search?q=o%3Ahaste+set%3A' + scode + '&unique'
        response = requests.get(getquery)

        if response.ok:
            # Get the data
            curr_haste_all = int(response.json()['total_cards'])
            curr_haste_creatures = len([x['type_line'] for x in response.json()['data'] if 'creature' in x['type_line'].lower()])    
        else:
            print('Fails for ' + scode)
            curr_haste_all = 0
            curr_haste_creatures = 0

        # add
        haste_all.extend([curr_haste_all])
        haste_creatures.extend([curr_haste_creatures])
        # pause
        time.sleep(0.11)

    print('\nDone')
    
    haste_df = pd.DataFrame({'Set code':setcodes, 'Haste_creatures':haste_creatures, 'Haste_cards':haste_all})
    
    return haste_df
    
    
def clean_haste_df(haste_df,allsets_df):
    # Fix TimeSpiral
    tspdf = haste_df.loc[[x[:2]=='TS' for x in haste_df['Set code']]]
    haste_df.loc[haste_df['Set code']=='TSP','Haste_creatures'] = tspdf.Haste_creatures.sum()
    haste_df.loc[haste_df['Set code']=='TSP','Haste_cards'] = tspdf.Haste_cards.sum()
    haste_df.drop(haste_df.loc[haste_df['Set code']=='TSB'].index,inplace=True)
        
    # Join with allsets info, manually adjust MOM
    haste_final_df = allsets_df.set_index('Set code').join(haste_df.set_index('Set code'))
    # Reset index
    haste_final_df.reset_index(inplace=True)
    haste_final_df.loc[haste_final_df['Set code']=='MOM','Total Cards'] = 296
    
    return haste_final_df
    

def plot_haste(haste_final_df):
    haste_final_df['Haste_creatures_normed'] = [(x/y)*100 for x,y in zip(haste_final_df['Haste_creatures'],haste_final_df['Total Cards'])]
    setlist4plotting = ['       '+y if np.mod(x,2)==0 else y+'       ' for x,y in enumerate(haste_final_df['Set code'].tolist()) ]
    f,a = plt.subplots(2,1,figsize=(20,7), sharex=True)
    a[0].plot(haste_final_df.index, haste_final_df['Haste_creatures'],'m^')
    a[0].set_yticks(range(0,21,3))
    a[0].set_ylabel('Number of creatures \nwith HASTE in their text')
    a[0].set_xlim(haste_final_df.index.min()-0.5,haste_final_df.index.max()+0.5)
    a[0].grid('on')
    a[1].plot(haste_final_df.index, haste_final_df['Haste_creatures_normed'],'ro')
    a[1].set_xticks(haste_final_df.index, setlist4plotting, rotation='vertical')
    a[1].set_yticks(range(0,10,2))
    a[1].set_ylabel('(%) of creatures with HASTE in text\n with respect to total # of cards in set')
    a[1].set_xlim(haste_final_df.index.min()-0.5,haste_final_df.index.max()+0.5)
    plt.grid('on')
    plt.show()
    f.savefig('hastecreatures1.png',bbox_inches='tight')
    
    return None

    
    
if __name__=='__main__':
    
    # Prepare info
    allsets_df, setcodes = get_set_data()
    
    # Gather data
    haste_df = query_scryfall(setcodes)
    
    # Clean data
    haste_final_df = clean_haste_df(haste_df,allsets_df)
    
    # Plot and save figure
    plot_haste(haste_final_df)
    
    

    
    
    
    