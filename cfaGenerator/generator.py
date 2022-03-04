# Setting path variables
import sys
from configs import PROJECT_PATH

sys.path.append(PROJECT_PATH)
# Importing required libraries
import pandas as pd
from PreProcessing import utils
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


# Defining the main class
class RecommendationGenerator:
    # Attributes 属性
    userID = 0
    N = 0

    def __init__(self, userID, N):
        self.userID = userID
        self.N = N

    def change_attributes(self, userID, N):
        self.userID = userID
        self.N = N

    def load_data(self, datapath):
        '''
        Loads the required data into pandas.DataFrames to generate the recommendations\n
        Parameters:
            datapath: str  
                Absolute or relative path to the csv file containing the complete data
        Returns:
            1-features dataframe which contains the feature matrix
            2-data dataframe which contains the corresponding (courseID,userID) tuple

        将所需数据加载到 pandas.DataFrames 以生成推荐\n
         参数：
             datapath: str
                 包含完整数据的 csv 文件的绝对或相对路径
         Returns:
             包含特征矩阵的 1 个特征数据框
             包含相应 (courseID,userID) 元组的 2 数据数据帧
        '''

        # Loading the features and converting their type from object to numeric
        # 加载特征并将它们的类型从对象转换为数字
        features = utils.reduce_mem_usage(pd.read_csv(datapath,
                                                      usecols=['click_courseware', 'load_video', 'pause_video',
                                                               'problem_check', 'problem_get', 'seek_video',
                                                               'stop_video']))
        features = features.apply(pd.to_numeric, errors='coerce')
        features = features.fillna(0)
        # print(features)

        # Loading courseID and userID data and converting userID from type object to numeric
        # 加载 courseID 和 userID 数据并将 userID 从类型对象转换为数字
        data = pd.read_csv(datapath, usecols=['courseID', 'userID'])
        cols = data.columns.drop('courseID')
        data[cols] = data[cols].apply(pd.to_numeric, errors='coerce')
        data = data.fillna(0)

        return features, data

    def generate_recommendations(self, features, data, print_rec=False):
        """
        Generates and prints the recommendations taking the userID and N (the number of recommendations to be generated)\n
        Parameters:
            features: pd.DataFrame
                The features dataframe obtained from the function load_data
            data: pd.DataFrame
                The data dataframe obtained from the function load_data
            print_rec: bool, default False
                If true, the recommendations are printed. If false, the recommendations are stored in a list
        Returns:
            If print_rec = False, the function returns an ordered list of recommendations

            使用用户 ID 和 N（要生成的推荐数量）生成并打印推荐\n
         参数：
             features: pd.DataFrame
                 从函数 load_data 获得的特征数据框
             data: pd.DataFrame
                 从函数load_data得到的数据dataframe
             print_rec: bool, default False
                 如果为真，则打印推荐。 如果为 false，则推荐存储在列表中
         Returns:
             如果 print_rec = False，该函数返回一个有序的推荐列表
        """
        index = data[data['userID'] == self.userID].index.tolist()

        # Storig the rows into a new dataframe
        X = features.iloc[index]
        # print(X.shape)
        # print(features.shape)

        # Applying cosine similarity and storing the matrix
        # 应用余弦相似度并存储矩阵
        cossim_mat = cosine_similarity(X=X.to_numpy(copy=True), Y=features.to_numpy(copy=True), dense_output=False)

        print(cossim_mat)
        fcm = open("tmp/tmp_cossim_mat.txt", "w")
        fcm.truncate(0)
        np.savetxt("tmp/tmp_cossim_mat.txt", cossim_mat, fmt='%f', delimiter=',')
        fcm.close()
        # Get top N recommendations
        recomm_indices = self.largest_indices(cossim_mat, self.N, data)

        print(recomm_indices)
        fri = open("tmp/tmp_recomm_indices.txt", "w")
        fri.truncate(0)
        np.savetxt("tmp/tmp_recomm_indices.txt", recomm_indices, fmt='%d', delimiter=',')
        fri.close()

        if print_rec:
            # Print the recommendations from the obtained recomm_indices
            self.print_recommendations(recomm_indices, data)

            return

        else:
            # Return the list of recommendations
            recomm = []
            i = 0
            for x in data['courseID'][recomm_indices].unique():
                i += 1
                recomm.append(x)
                if i == self.N:
                    break
            return recomm

    def print_recommendations(self, recomm_indices, data):
        """
        Prints out the unique courses from the obtained recommnded indices.\n
        Parameters:
            recomm_indices: list
                The list of recommendation indices generated from the function generate_recommendation()
            data: pd.DataFrame
                The data dataframe obtained from the function load_data()
        """
        i = 0

        # print("Based on the courses {} has previously done".format(self.userID))

        for x in data['courseID'][recomm_indices].unique():
            i += 1
            print("Recommendation #{} : {}".format(i, x))
            if i == self.N:
                break

    '''Utility Methods'''

    def largest_indices(self, ary, top_N, data):
        """
        Returns the n largest indices from a numpy array.\n
        Parameters:\n
            ary: numpy array 
            top_N: int 
                The number of largest indices to return
            data: pd.DataFrame
                The data dataframe obtained from the function load_data()

        从 numpy 数组中返回 n 个最大的索引。\n
         参数：\n
             ary: numpy 数组
             top_N: 整数
                 要返回的最大索引数
             data: pd.DataFrame
                 从函数 load_data() 获得的数据数据帧
        """
        # Flatten the array, find the indices of the top N values then sort the values in a decreasing order

        flat = ary.flatten()
        indices = np.argpartition(flat, -top_N)[-top_N:]
        indices = indices[np.argsort(-flat[indices])]
        indices = indices % ary.shape[1]

        '''
        There might be some repeated recommendations and hence the total recommendation might not be equal to N
        Hence we call the function in a recursive manner until the no. of unique recommendations = N
        '''
        n = data['courseID'][indices].unique().shape[0]
        # print(n)
        if n < self.N:
            indices = self.largest_indices(ary, top_N + (top_N - n), data)

        # Performing MOD by the orignal size as we initially flattened the array
        indices = indices % ary.shape[1]
        # print("indices")
        # print(indices)
        # print("indices end")
        return indices

    # def done_courses(self)
