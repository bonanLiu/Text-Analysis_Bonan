import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem.porter import PorterStemmer
from nltk.stem import WordNetLemmatizer
import re
import os


output_dir = "Part02_TF-IDF_Result"
os.makedirs(output_dir, exist_ok=True)

# pre process
def preprocess(df, content_col='content'):
    
    lemmatizer = WordNetLemmatizer()
    
    def process_text(text):
        if not isinstance(text, str):
            return ""
        

        text = text.lower()
        text = re.sub(r'[0-9]+', '', text)
        text = re.sub(r'[^\w\s]', '', text)
        words = text.split()
        common_words = ['the', 'and', 'to', 'of', 'a', 'in', 'that', 'is', 'it', 'for', 'with', 'on', 'by', 
                        'this', 'as', 'be', 'at', 'are', 'was', 'from', 'has', 'have', 'had', 'been', 'but', 
                        'not', 'what', 'all', 'were', 'when', 'we', 'they', 'their', 'you', 'your', 'his', 
                        'her', 'says', 'said', 'say', 'one', 'two', 'three', 'many', 'much', 'can', 'will', 
                        'just', 'would', 'could', 'should', 'now', 'then', 'than', 'our','here', 'there','why',
                        'these', 'those','year','per','about','who','report','variety','notes','like','she','he',
                        'other','month','daddy']

        filtered_words = [lemmatizer.lemmatize(word) for word in words 
                          if len(word) > 2 and word not in common_words]
        
        return ' '.join(filtered_words)
    
    # new dataframe
    df_processed = df.copy()
    
    # text process
    df_processed['filtered_content'] = df[content_col].apply(process_text)
    
    return df_processed


# 1. each articles
def keywords_perArticle(df, n_keywords=5):

    # prepocess
    if 'filtered_content' not in df.columns:
        df = preprocess(df)
    
    tfidf_vectorizer = TfidfVectorizer(
        max_features=500,
        min_df=2,
        max_df=0.7,
        ngram_range=(1, 2)
    )
    
    tfidf_matrix = tfidf_vectorizer.fit_transform(df['filtered_content'])

    feature_names = tfidf_vectorizer.get_feature_names_out()

    article_keywords = pd.DataFrame(columns=['article_id', 'title', 'top_keywords', 'tfidf_scores'])
    
    for i, row in df.iterrows():
        article_vector = tfidf_matrix[i]
        article_tfidf = pd.Series(article_vector.toarray().flatten(), index=feature_names)
        
        top_article_terms = article_tfidf.sort_values(ascending=False).head(n_keywords)
        
        article_keywords = pd.concat([article_keywords, pd.DataFrame({
            'article_id': [i+1],
            'title': [row['title']],
            'top_keywords': [',\n'.join(top_article_terms.index)],
            'tfidf_scores': [',\n'.join([f"{score:.3f}" for score in top_article_terms.values])]
        })], ignore_index=True)
    
    return article_keywords


# 2. all articles
def keywords_allArticle(df, top_n=20, normalize=True):
    
    if 'filtered_content' not in df.columns:
        df = preprocess(df)
    
    tfidf_vectorizer = TfidfVectorizer(
        max_features=600,
        min_df=1,          # at list exist in 10 articles
        max_df=0.9,        # at most exist in 90% articles
        ngram_range=(1, 2) 
    )
    
    tfidf_matrix = tfidf_vectorizer.fit_transform(df['filtered_content'])

    feature_names = tfidf_vectorizer.get_feature_names_out()

    global_scores = np.array(tfidf_matrix.sum(axis=0)).flatten()

    if normalize:
        min_score = global_scores.min()
        max_score = global_scores.max()
        
        if max_score > min_score:  #  Denominator ！= 0 
            global_scores = (global_scores - min_score) / (max_score - min_score)
    
    global_keywords_df = pd.DataFrame({
        'keyword': feature_names,
        'tfidf_score': global_scores
    })

    global_keywords_df['is_phrase'] = global_keywords_df['keyword'].apply(lambda x: ' ' in x)
    words_df = global_keywords_df[~global_keywords_df['is_phrase']].sort_values('tfidf_score', ascending=False)
    phrases_df = global_keywords_df[global_keywords_df['is_phrase']].sort_values('tfidf_score', ascending=False)
    top_words = words_df.head(top_n // 2)
    top_phrases = phrases_df.head(top_n // 2)
    
    top_keywords = pd.concat([top_words, top_phrases]).sort_values('tfidf_score', ascending=False)
    top_keywords = top_keywords.drop('is_phrase', axis=1)
    
    return top_keywords

# Main execution
if __name__ == "__main__":
    df = pd.read_csv("Articles_Coffee.csv")
    print(f"Loaded {len(df)} articles.")
    
    df_processed = preprocess(df)
    
    # 1. top 5 keywords for each article
    per_keywords = keywords_perArticle(df_processed, 5)    
    per_keywords.to_csv(f"{output_dir}/1. TF-IDF_keywords(per).csv", index=False)

    # 2. top 30 keywords for all articles
    all_keywords = keywords_allArticle(df_processed, 50)    
    all_keywords.to_csv(f"{output_dir}/1. TF-IDF_keywords(all).csv", index=False)

    
print("\nFinishing Processing")