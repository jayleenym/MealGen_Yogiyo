import datetime
import math
import os, sys
import time
import pymysql
import numpy as np
import pandas as pd
from scipy.sparse import data
from tqdm import tqdm
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

# db management libraries
import pymysql
from dbconfig import Insert, Upsert, reduce_mem_usage
from controller import MysqlController

# similarity, prediction
from sklearn.metrics.pairwise import cosine_similarity
from surprise import Reader, Dataset
from surprise import SVD
from surprise import accuracy
from surprise.model_selection import train_test_split

pd.set_option('display.float_format', '{:.2f}'.format)

class UpdateRecommend():
    def __init__(self, file = None):
        if not file:
            _id = input("input id(root) : ")
            _pw = input("input pw       : ")
            _db = input("databases      : ")
            connect_info = ("localhost", 3306, _id, _pw, _db)
        else:
            with open(os.path.join(sys.path[0], file), "r") as f:
                connect_info = f.read().split(",")
        self.controller = MysqlController(*connect_info)

    def get_dataframe(self):
        DF = pd.read_sql("SELECT user_id, menu_id, restaurant_id, like_dislike FROM reviews", self.controller.conn)
        DF = reduce_mem_usage(DF)
        MENU = dict(DF[['menu_id', 'restaurant_id']].drop_duplicates().values)
        return DF, MENU

    # 유저간 코사인 유사도 구하기
    def _user_cosine(self, df, start, end):
        # 한꺼번에 pivot하면 용량 때문에 종료됨
        rated_df = df[start:end].pivot(columns = 'menu_id', index = 'user_id', values = 'like_dislike')
        del df
        rated_df = rated_df.fillna(-1) # 평가 안된 항목 모두 '싫어요' 표시됨 방지
        # 용량 줄이기
        rated_df = reduce_mem_usage(rated_df)
        # 만들어진 pivot table로 User간 코사인 유사도 계산
        cos_sim = pd.DataFrame(cosine_similarity(rated_df), index = rated_df.index, columns= rated_df.index)
        compat_df = pd.DataFrame(cos_sim.unstack())
        del cos_sim
        compat_df.index.names = ['user_id', 'target_user_id']
        compat_df = compat_df.reset_index()
        compat_df.columns = ['user_id', 'target_user_id', 'expect_rate']
        # 용량 줄이기
        compat_df = reduce_mem_usage(compat_df)
        # User간 궁합점수가 0% ~ 100%로 나오기 때문에 이에 맞게 변환
        compat_df['expect_rate'] = compat_df['expect_rate'].apply(lambda x: ((x+1)/2)*100)
        return compat_df
    

    # 식당 예상 평점
    # update하기 위해 numpy형태로 변환
    def make_predict_list(self, df, uid):
        res_list = df['menu_id'].unique()
    #     이 부분은 사용자가 평가한 메뉴는 예측에서 제외할 때(현재는 다 같이 포함해서 예측)
    #     past_res_list = df[(df['account_id'] == int(uid))]['menu_id'].unique()
    #     pred_res_list = list(set(res_list) - set(past_res_list))
        pred_res_list = np.c_[[uid] * len(res_list), res_list]
        return pred_res_list
    
    def make_recommendation(self, algo, uid, pred_res_list):
        rate_list = []
        for i in pred_res_list:
            # 위에서 만든 [user_id, menu_id]를 받아서 이에 대한 예상 점수 계산
            rate = algo.predict(i[0], i[1]).est
            rate_list.append(rate)
        rate_list = np.array(rate_list)
        pred_res_list = np.c_[pred_res_list, rate_list]
        # [user_id, menu_id, rate]를 df로 변환
        recomm_df = pd.DataFrame(pred_res_list, columns = ['user_id', 'menu_id', 'predict'])
        return recomm_df


    def _user_SVD(self):
        df, menu_dict = self.get_dataframe()
        # 점수 범위가 0,1
        reader = Reader(rating_scale = (0, 1))
        # 사용자의 메뉴에 대한 평점이므로, df에서 필요한 부분만 가져와서 데이터셋으로 만들기
        dataset = Dataset.load_from_df(df[['user_id', 'menu_id', 'like_dislike']], reader)
        # 전체 데이터의 25%를 train set으로 활용
        trainset, testset = train_test_split(dataset, test_size = .25)
        # SVD 알고리즘 적용
        svd = SVD()
        # train
        svd.fit(trainset)
        # testset에 prediction확인
        pred = svd.test(testset)
        #rmse로 측정
        print(accuracy.rmse(pred))

        recomm_df = pd.DataFrame(columns = ['user_id', 'menu_id', 'predict'])
        for uid in tqdm(df['user_id'].unique()):
            pred_res_list = self.make_predict_list(df, uid)
            temp = self.make_recommendation(svd, uid, pred_res_list)
            recomm_df = pd.concat([recomm_df, temp]).reset_index(drop = True)

        # 만들어뒀던 menu-restaurant dictionary를 dataframe에 추가
        recomm_df['restaurant_id'] = recomm_df['menu_id'].apply(lambda x: menu_dict[x])
        # 용량 줄이기
        recomm_df = reduce_mem_usage(recomm_df)
        return recomm_df


    # db update
    def update_compatibility(self):
        data, _ = self.get_dataframe()
        del _
        for i in tqdm(range(0, len(data), 10000)):
            cos = self._user_cosine(data, i, i+10000)
            # 한 줄씩 upsert
            for i in tqdm(range(len(cos))):
                Upsert(self.controller, table_name = 'user_comp', line = dict(cos.iloc[i]))
            cos.to_csv(f"./update_comp_{today}_{i}.csv", index = False)
            del cos


    def update_recommend(self):
        df = self._user_SVD()
        # menu_id == -1 제외
        df = df.drop(df[df.menu_id == -1].index)

        m_q = "SELECT DISTINCT menu_id, name FROM menu_info;"
        self.controller.curs.execute(m_q)
        menu = dict(self.controller.curs.fetchall())
        r_q = "SELECT DISTINCT restaurant_id, name FROM restaurant_info;"
        self.controller.curs.execute(r_q)
        res = dict(self.controller.curs.fetchall())
        
        # 메뉴 이름, 식당 이름까지 추가해서 update
        df['menu'] = df['menu_id'].apply(lambda x: menu[x])
        df['restaurant'] = df['restaurant_id'].apply(lambda x: res[x])
        # 순서 정렬
        df = df.reindex(columns = ['user_id', 'menu_id', 'menu', 'restaurant_id', 'restaurant', 'predict'])
        df = reduce_mem_usage(df)
        for i in tqdm(range(len(df))):
            Upsert(self.controller, table_name='user_predict', line = dict(df.iloc[i]))
        
        df.to_csv(f"./update_predict_{today}.csv", index = False)
        del df
        




        
if __name__ == '__main__':
    user = UpdateRecommend(file = "../connection.txt")
    user.controller._connection_info()

    # daily update
    user.update_compatibility()
    # user.update_recommend()

    user.controller.curs.close()