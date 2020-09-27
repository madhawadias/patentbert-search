from google.cloud import bigquery
from google.oauth2 import service_account
import os
from pandas.io import gbq
from sentence_transformers import SentenceTransformer, util
import numpy as np
import time

def patent_filter(a_query):
  start_time = time.time()

  os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'static/keys/project01.json'

  credentials = service_account.Credentials.from_service_account_file('static/keys/project01.json')

  # Construct a BigQuery client object.
  client = bigquery.Client(credentials = credentials)

  project_id = 'project-01-288013'

  print("Starting the query...")
  query = '''
    SELECT title_localized, abstract_localized
    FROM `project-01-288013.Patent_dataset.Patent_publication_abstract_title`
    LIMIT 100
  '''
  print('End of Query')
  results_df = gbq.read_gbq(query, project_id=project_id, private_key='keys/project01.json')

  results_df.head()

  descriptions = []
  print('starting iteration...')
  for index, row in results_df.iterrows() :
    title = row['title_localized']
    abstract = row['abstract_localized']
    title = str(title)
    abstract = str(abstract)
    try:
      title = title.split("[{'text': '",1)[1]
    except:
      title = ''
    try:
      abstract = abstract.split("[{'text': '",1)[1]
    except:
      abstract = ''
    try:
      title = title.split("', 'language':",1)[0]
    except:
      title = ''
    abstract = abstract.split("', 'language':",1)[0]
    description = title + ". " + abstract
    descriptions.append(description)
  print('iteration done')

  embedder = SentenceTransformer('distilbert-base-nli-stsb-mean-tokens')

  # Corpus with example sentences
  corpus = []
  corpus = descriptions

  # print(corpus)

  corpus_embeddings = embedder.encode( corpus, convert_to_tensor=True )

  # Query sentences:
  query = a_query

  # Find the closest 5 sentences of the corpus for each query sentence based on cosine similarity
  top_k = 5

  query_embedding = embedder.encode(query, convert_to_tensor=True)
  cos_scores = util.pytorch_cos_sim(query_embedding, corpus_embeddings)[0]
  cos_scores = cos_scores.cpu()

  #We use np.argpartition, to only partially sort the top_k results
  top_results = np.argpartition(-cos_scores, range(top_k))[0:top_k]

  print("\n\n======================\n\n")
  print("Query:", query)
  print("\nTop 5 most similar sentences in corpus:")

  all_data_list = []
  all_corpus_des = []
  all_score = []

  for idx in top_results[0:top_k]:
   combined = (corpus[idx].strip()) + "\n" + ("(Score: %.4f)" % (cos_scores[idx])+"\n")
   print(combined)
   all_data_list.append(combined)
   all_data_string = ' '.join(map(str, all_data_list))
   corpus_des = (corpus[idx].strip())
   score =  ("(Score: %.4f)" % (cos_scores[idx]))
   all_corpus_des.append(corpus_des)
   all_score.append(score)


  data = {   'result1': [{
               'corpus': all_corpus_des[0],
               'points': all_score[0]
                }],
               'result2': [{
                 'corpus': all_corpus_des[1],
                 'points': all_score[1]
                }],
               'result3': [{
               'corpus': all_corpus_des[2],
               'points': all_score[2]
                }],
               'result4': [{
               'corpus': all_corpus_des[3],
               'points': all_score[3]
                }],
                'result5': [{
                'corpus': all_corpus_des[4],
                'points': all_score[4]
                }]
          }


  print("End Time")
  print(time.time() - start_time)

  print(all_data_string)
  print(data)
  return data












