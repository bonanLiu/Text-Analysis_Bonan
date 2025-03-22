import pandas as pd
import numpy as np
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import os
from nltk.stem import WordNetLemmatizer


output_dir = "Part02_LDA_Result"
os.makedirs(output_dir, exist_ok=True)

def preprocess_for_lda(df, content_col='content'):

    lemmatizer = WordNetLemmatizer()
    common_words = ['the', 'and', 'to', 'of', 'a', 'in', 'that', 'is', 'it', 'for', 'with', 'on', 'by', 
                        'this', 'as', 'be', 'at', 'are', 'was', 'from', 'has', 'have', 'had', 'been', 'but', 
                        'not', 'what', 'all', 'were', 'when', 'we', 'they', 'their', 'you', 'your', 'his', 
                        'her', 'says', 'said', 'say', 'one', 'two', 'three', 'many', 'much', 'can', 'will', 
                        'just', 'would', 'could', 'should', 'now', 'then', 'than', 'our','here', 'there','why',
                        'these', 'those','year','per','about','who','report','variety','notes','like','she','he',
                        'variety']
    
    def textprocess(text):
        text = text.lower()
        text = re.sub(r'[0-9]+', '', text)
        text = re.sub(r'[^\w\s]', '', text)
        words = text.split()

        return words
    
    def clean_text(text):
        if not isinstance(text, str):
            return ""
        
        thewords = textprocess(text)
        filtered_words = [lemmatizer.lemmatize(word) for word in thewords
                         if len(word) > 2 and word not in common_words]
        
        return ' '.join(filtered_words)
    
    def prep_for_phrases(text):
        if not isinstance(text, str):
            return ""
        
        thewords = textprocess(text)
        filtered_words = [word for word in thewords
                         if len(word) > 2 and word not in common_words]
        
        return ' '.join(filtered_words)
    
    df_processed = df.copy()

    df_processed['clean_text'] = df[content_col].apply(clean_text)
    df_processed['phrase_text'] = df[content_col].apply(prep_for_phrases)
    
    return df_processed

def perform_lda_analysis(df, n_topics):

    word_vectorizer = CountVectorizer(
        max_df=0.9,          # %
        min_df=3,            #amount
        max_features=600,    # features
        ngram_range=(1, 1)  # only single word
    )
    
    phrase_vectorizer = CountVectorizer(
        max_df=0.9,
        min_df=1,
        max_features=300,  
        ngram_range=(2, 2) # phrases
    )
    

    word_matrix = word_vectorizer.fit_transform(df['clean_text'])
    phrase_matrix = phrase_vectorizer.fit_transform(df['clean_text'])

    word_features = word_vectorizer.get_feature_names_out()
    phrase_features = phrase_vectorizer.get_feature_names_out()
    

    word_lda = LatentDirichletAllocation(
        n_components=n_topics,
        max_iter=10,    # set
        learning_method='online',
        random_state=0,
        n_jobs=-1,
        doc_topic_prior=0.5,
    )
    
    phrase_lda = LatentDirichletAllocation(
        n_components=n_topics,
        max_iter=10,    # set
        learning_method='online',
        random_state=0,
        n_jobs=-1,
        doc_topic_prior=0.5,
    )
    

    word_lda.fit(word_matrix)
    phrase_lda.fit(phrase_matrix)
    
    word_document_topics = word_lda.transform(word_matrix)
    phrase_document_topics = phrase_lda.transform(phrase_matrix)

    combined_document_topics = (word_document_topics + phrase_document_topics) / 2
    
    return (word_lda, phrase_lda), (word_vectorizer, phrase_vectorizer), (word_features, phrase_features), combined_document_topics

def display_topics(lda_models, feature_names_sets, n_words, n_phrases):

    word_lda, phrase_lda = lda_models
    word_features, phrase_features = feature_names_sets
    
    topics_text = "\n=== Topics Discovery by LDA ===\n"
    topics_data = []
    
    for topic_idx in range(len(word_lda.components_)):
        topic_header = f"Topic #{topic_idx + 1}:\n"
        topics_text += topic_header
        
        # word
        word_topic = word_lda.components_[topic_idx]
        top_word_indices = word_topic.argsort()[:-n_words-1:-1]
        top_words = [word_features[i] for i in top_word_indices]
        top_word_weights = [word_topic[i] for i in top_word_indices]
        
        # phrase
        phrase_topic = phrase_lda.components_[topic_idx]
        top_phrase_indices = phrase_topic.argsort()[:-n_phrases-1:-1]
        top_phrases = [phrase_features[i] for i in top_phrase_indices]
        top_phrase_weights = [phrase_topic[i] for i in top_phrase_indices]


        # REPORT!!!
        words_header = "  Words:\n"
        topics_text += words_header
        
        for word, weight in zip(top_words, top_word_weights):
            word_line = f"    - {word} ({weight:.4f})\n"
            topics_text += word_line
            
            topics_data.append({
                'topic_id': topic_idx + 1,
                'term': word,
                'weight': weight,
                'type': 'word'
            })
        
        
        phrases_header = "  Phrases:\n"
        topics_text += phrases_header
        
        for phrase, weight in zip(top_phrases, top_phrase_weights):
            phrase_line = f"    - {phrase} ({weight:.4f})\n"
            topics_text += phrase_line
            
            topics_data.append({
                'topic_id': topic_idx + 1,
                'term': phrase,
                'weight': weight,
                'type': 'phrase'
            })
        
    
    pd.DataFrame(topics_data).to_csv(f"{output_dir}/lda_topics_with_phrases.csv", index=False)

    with open(f"{output_dir}/topics_discovery.txt", "w") as f:
        f.write(topics_text)
    
    return topics_data

def analyze_document_topics(document_topics, df):

    dominant_topics = document_topics.argmax(axis=1)
    
    results = []
    for i, (idx, row) in enumerate(df.iterrows()):
        
        topic_dist = document_topics[i]
        dominant_topic = dominant_topics[i]
        
        article_info = {
            'article_id': idx,
            'title': row['title'],
            'dominant_topic': dominant_topic + 1,
            'dominant_topic_prob': topic_dist[dominant_topic]
        }
        
        for topic_idx, prob in enumerate(topic_dist):
            article_info[f'topic_{topic_idx+1}_prob'] = prob
        
        results.append(article_info)
    

    df_results = pd.DataFrame(results)

    df_results.to_csv(f"{output_dir}/article_topic_distribution.csv", index=False)

    topic_counts = df_results['dominant_topic'].value_counts().sort_index()
    
    # REPORT!
    distribution_text = "=== Articles Distribution ===\n\n"
    for topic_id, count in topic_counts.items():
        percentage = count / len(df) * 100
        line = f"Topic #{topic_id}: {count} articles ({percentage:.1f}%)\n"
        distribution_text += line

    print("\n" + distribution_text)
    with open(f"{output_dir}/topic_distribution.txt", "w") as f:
        f.write(distribution_text)

    return df_results

# execusion
if __name__ == "__main__":

    df = pd.read_csv("Articles_Coffee.csv")

    content_col = 'content'  # define the column be processed
    if content_col not in df.columns:
        possible_cols = [col for col in df.columns if 'content' in col.lower() or 'text' in col.lower()]
        if possible_cols:
            content_col = possible_cols[0]
        else:
            print("Error")
            exit(1)

    df_processed = preprocess_for_lda(df, content_col)

    # setting
    n_topics = 5
    n_words = 6
    n_phrases = 10
    lda_models, vectorizers, feature_names_sets, document_topics = perform_lda_analysis(df_processed, n_topics=n_topics)


    display_topics(lda_models, feature_names_sets, n_words, n_phrases)
    article_topics = analyze_document_topics(document_topics, df_processed)
    
print("\nFinishing Processing")