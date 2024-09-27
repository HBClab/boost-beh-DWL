# run Quality Check against new sub data

import os
import sys
import pandas as pd
import sys

def parse_cmd_args():
    import argparse
    parser = argparse.ArgumentParser(description='QC for ATS')
    parser.add_argument('-s', type=str, help='Path to submission')
    parser.add_argument('-o', type=str, help='Path to output for QC plots and Logs')
    parser.add_argument('-sub', type=str, help='Subject ID')

    return parser.parse_args()

def df(submission):
    submission = pd.read_csv(submission)
    return submission

def qc(submission):
    errors = []
    submission = df(submission)
    # Check if submission is a DataFrame
    if not isinstance(submission, pd.DataFrame):
        errors.append('Submission is not a DataFrame. Could not run QC')
    
    # Check if submission is empty
    if len(submission) == 0:
        errors.append('Submission is empty')
    
    #Check if submission has correct number of rows (within 5% of expected = 16)
    if len(submission) < 13 or len(submission) > 18:
        errors.append('Submission has incorrect number of rows')
    # If there are any errors, print them and exit
    if errors:
        for error in errors:
            print(error)
        sys.exit(1)

    print("All QC checks passed.")
        
    
def plots(submission, output, sub, version):
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    from math import pi
    from fuzzywuzzy import fuzz
    from fuzzywuzzy import process

    df = pd.read_csv(submission)

    listA = [['book', 'flower', 'train', 'rug', 'meadow', 'harp', 'salt', 'finger', 'apple', 'log', 'button', 'key', 'gold', 'rattle'],['bowl', 'dawn', 'judge', 'grant', 'insect', 'plane', 'county', 'pool', 'seed', 'sheep', 'meal', 'coat', 'bottle', 'peach', 'chair']]
    listB = [['street', 'grass', 'door', 'arm', 'star', 'wife', 'window', 'city', 'pupil', 'cabin', 'lake', 'pipe', 'skin', 'fire', 'clock'],['baby', 'ocean', 'palace', 'lip', 'bar', 'dress', 'steam', 'coin', 'rock', 'army', 'building', 'friend', 'storm', 'village', 'cell']]
    listC = [['tower', 'wheat', 'queen', 'sugar', 'home', 'boy', 'doctor', 'camp', 'flag', 'letter', 'corn', 'nail', 'cattle', 'shore', 'body'],['sky', 'dollar', 'valley', 'butter', 'hall', 'diamond', 'winter', 'mother', 'christmas', 'meat', 'forest', 'tool', 'plant', 'money', 'hotel']]
    
    #for text in version, assign variable version to corresponding list, if .csv is in version, remove it
    if '.csv' in version:
        version = version[:-4]
    
    if 'A' in version:
        key = listA
    elif 'B' in version:
        key = listB
    elif 'C' in version:
        key = listC

    def fuzzy(sub_list, word_list):

        from fuzzywuzzy import fuzz
        from fuzzywuzzy import process
        print(sub_list)
        print(word_list)
        count =0
        used = []
        passed =[]
        #iterate through the list of lists and compare the first element of each list to all in list of words
        #the word in sub_list that has the highest ratio to a word in word_list is the word that is most similar
        #if that ratio is greater than 80, add 1 to count
        for i in range(len(sub_list)):
            for j in range(len(word_list)):
                ratio = fuzz.ratio(sub_list[i], word_list[j])
                if ratio > 80 and word_list[j] not in used:
                    count += 1
                    used.append(word_list[j])
                    passed.append(sub_list[i])
                    break
        return count/len(word_list), passed 


    def plot_circular_bar_graph(percentages, name):
        from math import pi
        startangle = 90
        colors = ['#4393E5', '#43BAE5', '#7AE6EA', '#E5A443']
        
        # Convert data to fit the polar axis
        ys = [i *1.1 for i in range(len(percentages))]   # One bar for each block
        left = (startangle * pi * 2) / 360  # This is to control where the bar starts

        # Figure and polar axis
        fig, ax = plt.subplots(figsize=(6, 6))
        ax = plt.subplot(projection='polar')

        # Plot bars and points at the end to make them round
        for i, (block, percentage) in enumerate(percentages.items()):
            ax.barh(ys[i], percentage * 2 * pi, left=left, height=1, color=colors[i % len(colors)], label=block)
            ax.text(percentage + left + 0.02, ys[i], f'{percentage:.0%}', va='center', ha='left', color='black', fontsize=12)

        plt.ylim(-1, len(percentages))

        # Custom legend
        ax.legend(loc='center', bbox_to_anchor=(0.5, -0.1), frameon=True) 

        # Clear ticks and spines
        plt.xticks([])
        plt.yticks([])
        ax.spines.clear()
        plt.title(name, fontsize=15, pad=20, color="white")
        plt.savefig(os.path.join(output, f'{sub}_rt_acc_fuzzy_delay.png'))
        plt.close()

    word_duration = []
    for i in range(len(df)-1):
        if i ==0:
            word_duration.append(df['block_dur'][i])
        else:
            word_duration.append(df['block_dur'][i+1] - df['block_dur'][i])\
   
    word_list = df['multichar_response'].tolist()
    for i in range(len(word_list)):
        word_list[i] = word_list[i][:-5]
    delay_fuzz = fuzzy(word_list, key[0])
    correct = []
    for i in range(len(word_list)):
        if word_list[i] in delay_fuzz[1]:
            correct.append(1)
        else:
            correct.append(0)
    percentages = {'Correct': delay_fuzz[0]}
    plot_circular_bar_graph(percentages, 'Accuracy')

    backspace = []
    for i in range(len(df)):
        if 'backspace' in df['multichar_response'][i]:
            backspace.append(1)
        else:
            backspace.append(0)
    df_delay = pd.DataFrame({'word': word_list, 'response_time': df['response_time'], 'correct': correct, 'backspace': backspace})

    import seaborn as sb
    plt.figure(figsize=(10, 6))
    #plot the duratiion of each word for dist where blue is no backspace and red is backspace
    sb.scatterplot(x = 'word', y = 'response_time', data = df_delay, hue = 'backspace', s=75)
    sb.set(rc={'figure.figsize':(20,10)})
    plt.title('Distraction Condition')
    #add an x if the word is wrong
    for i in range(len(df_delay)):
        if df_delay.iloc[i]['word'] not in delay_fuzz[1]:
            plt.text(i, df_delay.iloc[i]['response_time'], 'x', fontsize=12, color='black')
    plt.savefig(os.path.join(output, f'{sub}_rt_acc_fuzzy_delay.png'))
    plt.close()


        
def main():

    #parse command line arguments
    args = parse_cmd_args()
    submission = args.s
    output = args.o
    sub = args.sub

    # check if submission is a csv
    if not submission.endswith('.csv'):
        raise ValueError('Submission is not a csv')
    # check if submission exists
    if not os.path.exists(submission):
        raise ValueError('Submission does not exist')
    # run QC
    qc(submission)
    
    print(f'QC passed for {submission}, generating plots...')
    version = submission.split('_')[2]
    print(version)
    # generate plots
    plots(submission, output, sub, version)
    return submission, print('Plots generated')
    
    
if __name__ == '__main__':
    main()



    
    


