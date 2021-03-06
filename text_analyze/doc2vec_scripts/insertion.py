# coding: utf-8
from gensim import models
import numpy as np
from numpy import random
random.seed(555)
# from scipy.cluster.vq import vq, kmeans, whiten
# from sklearn.decomposition import TruncatedSVD
# from collections import defaultdict
# from separatewords import MecabTokenize  # 目的に合わせた形態素解析器を呼びだして下さい
import MySQLdb
import MySQLdb.cursors
import os
from datetime import datetime

REP_ROOT = os.environ['YA_RECOGNIZE_ROOT']
TEXT_ANALYZE = REP_ROOT + '/text_analyze'

conn = MySQLdb.connect(
    host="localhost",
    user=os.environ['YAHOO_AUCTION_DB_USERNAME'],
    passwd=os.environ['YAHOO_AUCTION_DB_PASSWORD'],
    db=os.environ['YAHOO_AUCTION_DB_NAME'],
    charset = "utf8",
    use_unicode=True,
    cursorclass=MySQLdb.cursors.DictCursor
)
cursor = conn.cursor()
cursor.execute(u'SELECT count(id) FROM items;')
cnt = cursor.fetchone()['count(id)']

def check_exist(label_ids=[]):
    query = u"""
        SELECT id FROM similarities
        WHERE (label_id = {0} and pair_label_id = {1}) or (label_id = {1} and pair_label_id = {0});
    """.format(label_ids[0], label_ids[1])
    cursor.execute(query)
    if not cursor.fetchone():
        return False
    else:
        return True

descriptions = {}

# model作成用のデータ作成 => descriptions
# for i in range(1, cnt, 20):
#     query = u"SELECT auction_id, title, non_tagged_description FROM items LIMIT {0}, 20;".format(i)
#     cursor.execute(query)
#     results = cursor.fetchall()
#
#     for result in results:
#         descriptions[result['auction_id']] = result['non_tagged_description'].split(' ')

loaded_model = models.doc2vec.Doc2Vec.load(TEXT_ANALYZE + '/doc2vec_model/model.d2c')

# modelizeしたitemのauction_idをDBへ入れる
now_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
for auction_id, _ in loaded_model.docvecs.doctags.items():
    query = """
        INSERT INTO modelized_item_indexes (auction_id, type) VALUES ('{0}', 'noun_number_only_model')
    """.format(auction_id)
    cursor.execute(query)
    conn.commit()
    print('inserted: ' + auction_id)

# labelsへ挿入
# for i, auction_id in enumerate(desc_auction_ids):
#     cursor.execute(u"INSERT INTO labels (auction_id, label, created_at, updated_at) VALUES ('{0}', '{1}', '{2}', '{3}');".format(auction_id, base_label_name + str(i), now_time, now_time))
#     conn.commit()

# similaritiesへ挿入
# for i, auction_id in enumerate(desc_auction_ids):
#     cursor.execute(u"SELECT id FROM labels WHERE auction_id = '{0}' LIMIT 1".format(auction_id))
#     main_label_id = cursor.fetchone()['id']
#
#     similarities = loaded_model.most_similar_labels(base_label_name + str(i),topn=len(desc_auction_ids))
#
#     for similarity in similarities:
#         cursor.execute(u"SELECT id FROM labels WHERE label = '{0}' LIMIT 1".format(similarity[0]))
#         pair_label_id = cursor.fetchone()['id']
#         # すでに存在するかチェック
#         if check_exist([main_label_id, pair_label_id]):
#             continue
#
#         print('inserting ' + similarity[0])
#         cursor.execute(u"INSERT INTO similarities (label_id, pair_label_id, degree, created_at, updated_at) VALUES ({0}, {1}, {2}, '{3}', '{4}')".format(main_label_id, pair_label_id, similarity[1], now_time, now_time))
#         conn.commit()
#         print('done')
