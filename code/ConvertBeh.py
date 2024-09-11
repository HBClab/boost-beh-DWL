# %%
import pandas as pd
import numpy as np
import os
import json

def parse_args():
    import argparse
    parser = argparse.ArgumentParser(description='Convert Behavior Data')
    parser.add_argument('-submission', type=str, help='Path to the submission file')
    parser.add_argument('-out', type=str, help='Output directory')
    parser.add_argument('-sub', type=str, help='Subject ID')
    parser.add_argument('-task', type=str, help='Task name')
    parser.add_argument('-taskvers', type=str, help='Task version')
    return parser.parse_args()


def rename_files(submission, subject, task, taskvers):
    #rename raw text files to be subject_task_taskvers.txt
    for root, dirs, files in os.walk(submission):
        for file in files:
            if file.endswith(".txt"):
                os.rename(os.path.join(root, file), os.path.join(root, f"{subject}_{task}_{taskvers}.txt"))
                submission = os.path.join(root, 'raw', f"{subject}_{task}_{taskvers}.txt")
                print(submission)
    return submission




def convert_beh(submission, out):

    if not os.path.isfile(submission):
        print(f"file does not exist: {submission}")

    # Use list_txt to store one file since I don't want to screw with Marco's code
    

    count = 0
    dic = {}

    count += 1
    tweets = []
    with open(submission, 'r') as file:
        for line in file:
            tweets.append(json.loads(line))
    dic[count]= pd.json_normalize(tweets,'data')

    print(dic)


    paths = []
    for i in range(len(dic)):
        i += 1
        for sub in np.unique(dic[i]['subject_id']):
            print(sub)
            paths.append((out+"/{0}_{1}_{2}"+".csv").format(sub,dic[i]['task'][0],dic[i]['task_vers'][0]))

        for path in paths:
            dic[i].to_csv(path, index=False)
            print(f"saved {path}")

def main():
    args = parse_args()
    submissive = rename_files(args.submission, args.sub, args.task, args.taskvers)
    convert_beh(submissive, args.out)

if __name__ == "__main__":
    main()


