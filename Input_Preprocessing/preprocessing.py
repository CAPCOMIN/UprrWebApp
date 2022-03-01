# Setting path variables
import sys
from configs import PROJECT_PATH

sys.path.append(PROJECT_PATH)

# Importing the necessary libraries
import pandas as pd
import ijson
import csv
import time
from Input_Preprocessing import utils


def convert_json_to_csv(src_path, dest_path, nrows=1000):
    '''
    This function converts the json file of the MOOC dataset to usable CSV file\n
    Parameters\n
        src_path: str  
            The absolute or relative path along with the filename, from where the JSON file can be loaded
        dest_path: str 
            The absolute or relative path along with the filename, where you want your converted CSV to be saved
        nrows: int
            Number of rows to be written into the csv at once
    Note: - This function can take long to execute depending on the size of the JSON file

    此函数将 MOOC 件数据集的 json 文件转换为可用的 CSV 文
     参数：
         src_path：str
             可以从其中加载 JSON 文件的绝对或相对路径以及文件名
         dest_path：str
             绝对或相对路径以及文件名，您希望将转换后的 CSV 保存在其中
         nrows：整数
             一次写入 csv 的行数
     注意： - 此函数可能需要很长时间才能执行，具体取决于 JSON 文件的大小
    '''

    # Declaring the local Variables
    curr_courseID = 0
    curr_userID = 0
    curr_sessID = 0
    count = 0
    count_rows = 0

    # Creating an empty dataframe
    column_names = ["courseID", "userID", "sessionID", "activity", "timestamp"]
    df = pd.DataFrame(columns=column_names)

    # Noting the start time
    start = time.time()

    # Writing the header of the CSV as the required column names
    with open(dest_path, "a+", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["courseID", "userID", "sessionID", "activity", "timestamp"])

    # Iteratively parsing the json file, such that it returns each prefix,event,value at a time
    with open(src_path, 'rb') as input_file:
        parser = ijson.parse(input_file, multiple_values=True)

        for prefix, event, value in parser:
            count += 1  # Counting the iterations

            if value == 'None':
                continue

            if (prefix, event) == ('item.item', 'string'):
                curr_courseID = value  # Notes current the course ID
                continue

            elif prefix == 'item.item' and event == 'map_key':
                curr_userID = value  # Notes the current User ID
                continue

            elif (prefix, event) == ('item.item.' + str(curr_userID), 'map_key'):
                curr_sessID = value  # Notes the current session ID
                continue

            # At this stage we have the current courseID, user ID and session ID
            if curr_courseID and curr_userID and curr_sessID:  # Proceeding further only if we have all 3

                # ('item.item.' + str(curr_userID) + '.' + str(curr_sessID) + '.item.item') gives us the item path
                if (prefix, event) == (
                        'item.item.' + str(curr_userID) + '.' + str(curr_sessID) + '.item.item', "string"):

                    # It is an activity if it starts with alpha character or else it is the timestamp
                    if value and value[0].isalpha():
                        activity = value  # Activity noted
                        continue

                    else:
                        timestamp = value  # timestamp corresponding to the recent activity noted

                        count_rows += 1  # Count the rows

                        # Storing the data into a dataframe
                        df = df.append({'courseID': curr_courseID, 'userID': curr_userID, 'sessionID': curr_sessID,
                                        'activity': activity, 'timestamp': timestamp}, ignore_index=True)

                        # Writing the dataframe into a CSV for every 'nrows' rows we have in the dataframe
                        if (count_rows % nrows == 0):
                            df.to_csv(dest_path, mode='a+', header=False, index=False)

                            # To drop all the rows from the dataframe which we have already written in the CSV, so as to free the memory
                            df = df.iloc[0:0]

                            # print(count_rows)

        print("For Loop DONE")

        # To add the remaining rows in the dataframe
    df.to_csv(dest_path, mode='a+', header=False, index=False)
    df = df.iloc[0:0]

    end = time.time()  # Notes the end time

    # Prints out the information
    print("For loop count: {} ".format(count))
    print("Rows count: {} ".format(count_rows))
    print("Time taken to run the program : {}".format(end - start))

    return


def form_feature_matrix(src_path, dest_path, chunksize=10000):
    '''
    Converts the raw data available to a feature matrix of shape [num of pairs of userID & courseID] X [n_features + 2] (+2 for the columns that have courseID and userID)\n

    Parameters\n
        src_path: str 
            The absolute or relative path along with the filename, from where the raw data containing csv file can be loaded 
        dest_path: str 
            The absolute or relative path along with the filename, where you want your feature matrix CSV to be saved
        chunksize: int ,default = 1000
            The no. of rows to be read at once for the conversion operation. Change the value for optimum memory and speed usage 

    将可用的原始数据转换为形状为 [userID & courseID 对数] X [n_features + 2] 的特征矩阵（对于具有 courseID 和 userID 的列，+2）\n

     参数：
         src_path：str
             绝对或相对路径以及文件名，可以从中加载包含 csv 文件的原始数据
         dest_path：str
             绝对或相对路径以及文件名，您希望在其中保存特征矩阵 CSV
          chunksize: int ,default = 1000
             转换操作一次读取的行数。 更改最佳内存和速度使用的值
    '''

    count = 0
    # Reading the csv in chunks
    df_chunks = pd.read_csv(src_path, chunksize=chunksize)
    for df in df_chunks:
        count += 1

        # Dropping the columns we don't rquired
        drop_columns = ['sessionID', 'timestamp']
        df = df.drop(columns=drop_columns)

        # Converting the catogerical values of 'activity' to dummy(indicator) values
        df = pd.concat([df, pd.get_dummies(df['activity'])], axis=1)

        # Final feature matrix of shape [n_userIDs,n_features + 2] (+2 for the columns that have the courseID and userID )
        file = df.groupby(['courseID', 'userID']).sum()
        file = utils.reduce_mem_usage(file)  # Reduces the memory usage

        # Storing the feature vectors as CSV file
        if (count == 1):
            file.to_csv(dest_path, mode="a+", header=True)
        else:
            file.to_csv(dest_path, mode="a+", header=False)

    print("For loop done")

    # Finally aggregating the chunkwise feature_matrices to one complete feature_matrix
    final_df = pd.read_csv(dest_path)

    # Final feature matrix of shape [n_userIDs,n_features + 2] (+2 for the columns that have the courseID and userID )
    file = final_df.groupby(['courseID', 'userID']).sum()
    file = utils.reduce_mem_usage(file)

    # Stroring the feature matrix as CSV file
    file.to_csv(dest_path, mode="a+")

    return
