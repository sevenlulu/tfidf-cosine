# -*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('UTF-8')

import json
import jieba
import xlrd
import random


#get query from postman collection json
def get_postman(file_path):
    with open(file_path) as f:
        collection = json.load(f)

    item_list = collection["item"]
    query_list = []
    for word in item_list:
        query_list.append(word["name"])
    return query_list


# col_num start from 0
def read_xlsx(filename, worksheetname, col_num):
    test_cases = []
    workbook = xlrd.open_workbook(filename)
    booksheet = workbook.sheet_by_name(worksheetname)
    for row in range(booksheet.nrows):
        test_cases.append(booksheet.cell(row, col_num).value)

    return test_cases


# read txt file to list
def read_txt(filename):
    query_list = []
    with open(filename) as f:
        for line in f:
            query_list.append(line)
    return query_list


# calculate cosine similarity
def cal_sim(query_list, dictionary, check_class):
    total = len(query_list)
    counter = 0
    for query in query_list:
        bad = query
        query = ' '.join(jieba.cut(query, cut_all=False))
        vec_bow = dictionary.doc2bow(query.split())
        vec_tfidf = tfidf[vec_bow]    # query分词的tfidf值
        sims = index[vec_tfidf]   #计算query与三类中每个query的相似度
        similarity = list(sims)

        if max(similarity) == 0:
            # counter = counter + 1
            print json.dumps(bad, ensure_ascii=False)
            print similarity
            print check_result[similarity.index(max(similarity))]
        elif check_result[similarity.index(max(similarity))] == check_class:
            counter = counter + 1
        else:
            print json.dumps(bad, ensure_ascii=False)
            print similarity
            print check_result[similarity.index(max(similarity))]
    return counter, total


# calculate testing accuracy
def testing_acc(class_name, test_tag):
    ranking_list = class_name
    counter, total = cal_sim(ranking_list, dictionary, test_tag)
    print "ranking test accuracy = %f" % (float(counter) / total)


if __name__ == "__main__":
    music_raw = read_xlsx("/home/lulu/Desktop/137_3classes_testcases.xlsx", "musicSheet", 0)
    tool_raw = read_xlsx("/home/lulu/Desktop/137_3classes_testcases.xlsx", "toolSheet", 0)

    # randomly choose 1000 music testcases and 100 testcases to form the testset
    music_test_collection = random.sample(music_raw, 1000)
    tool_test_collection = random.sample(tool_raw, 100)

    music = [i for i in music_raw if i not in music_test_collection]
    tool = [j for j in tool_raw if j not in tool_test_collection]


    # unigram
    all_jieba_unigram = []

    tmp_music = []
    for word in music:
        tmp_jieba = jieba.cut(word.replace('-', ''), cut_all=False)
        tmp_jieba = ' '.join(tmp_jieba).split(' ')
        for segment in tmp_jieba:
            tmp_music.append(segment)

    all_jieba_unigram.append(["music", tmp_music])

    tmp_tool = []
    for word in tool:
        tmp_jieba = jieba.cut(word.replace("-", ""), cut_all=False)
        tmp_jieba = ' '.join(tmp_jieba).split(' ')
        for segment in tmp_jieba:
            tmp_tool.append(segment)

    all_jieba_unigram.append(["tool", tmp_tool])


    texts = []
    for line in all_jieba_unigram:
        texts.append(line[1])


    from gensim import corpora, models, similarities
    import logging
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

    dictionary = corpora.Dictionary(texts)

    corpus = [dictionary.doc2bow(text) for text in texts]
    tfidf = models.TfidfModel(corpus)  # 由bow做的tfidf模型
    corpus_tfidf = tfidf[corpus]    # corpus的tfidf值

    index = similarities.MatrixSimilarity(corpus_tfidf)
    check_result = ["music", "tool"]

    testing_acc(tool, "tool")