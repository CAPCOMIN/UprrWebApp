# -*- coding: utf-8 -*-
__author__ = 'heroli'

# wordcloud生成中文词云
from wordcloud import WordCloud
import jieba
# 词频计算
import jieba.analyse as analyse
import imageio
from os import path


# import matplotlib.pyplot as plt

class WC(object):

    # 绘制词云
    def draw_wordcloud(self):
        # 读入一个txt文件
        # comment_text = open('features.txt', 'r', encoding='utf-8').read()
        comment_text = open('./static/test.txt', 'r', encoding='utf-8').read()
        # 结巴分词，生成字符串，如果不通过分词，无法直接生成正确的中文词云
        cut_text = " ".join(jieba.cut(comment_text))
        # print(cut_text)
        result = jieba.analyse.tfidf(cut_text, topK=1000, withWeight=True)
        # print(result)
        # 生成关键词比重字典
        keywords = dict()

        for i in result:
            keywords[i[0]] = i[1]
        print(keywords)

        d = path.dirname(__file__)  # 当前文件文件夹所在目录
        color_mask = imageio.imread("static/images/alice.png")  # 读取背景图片
        cloud = WordCloud(
            # 设置字体，不指定就会出现乱码
            font_path="./fonts/Gilroy-ExtraBold.otf",
            # font_path=path.join(d,'simsun.ttc'),
            width=500,
            height=500,
            # 设置背景色
            background_color='black',
            # 词云形状
            mask=color_mask,
            # 允许最大词汇
            max_words=2000,
            # 最大号字体
            max_font_size=55,
            scale=3.3,
            repeat=True
        )
        # text = {'hello':0.5,'world':1,'微信':1,'五星级':1}
        # text = {(u'\u7ecf\u9a8c', 1.0), (u'\u6027\u683c', 0.9648001018966549), (u'\u4e2a\u4eba', 0.9503282426083249),
        #  (u'\u4eba\u7fa4', 0.9369477618306996),('微信',1),('五星级',1)}
        word_cloud = cloud.generate_from_frequencies(keywords)  # 产生词云
        # word_cloud = cloud.generate(cut_text)
        # words = [['hello',float(3/8)],['meer',float(15/16)],['family',float(9/21)],['red',float(7/9)],['Tmac',float(12/99)]]
        # word_cloud = cloud.generate_from_frequencies(words);
        word_cloud.to_file("static/images/user_img.jpg")  # 保存图片
        print("success")
        #  显示词云图片
        # plt.imshow(word_cloud)
        # plt.axis('off')
        # plt.show()


if __name__ == '__main__':
    wc = WC()
    wc.draw_wordcloud()
