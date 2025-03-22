import matplotlib.pyplot as plt
from wordcloud import WordCloud
import pandas as pd
import os

def visualize_global_keywords(csv_file_path, output_dir="Part02_TF-IDF_Result"):

    # output path
    os.makedirs(output_dir, exist_ok=True)
    global_keywords = pd.read_csv(csv_file_path)
    
    if 'keyword' not in global_keywords.columns or 'tfidf_score' not in global_keywords.columns:
        column_names = global_keywords.columns.tolist()
        print(f"Erorr: {column_names}")

        if len(global_keywords.columns) >= 2:
            global_keywords.columns = ['keyword', 'tfidf_score'] + list(global_keywords.columns[2:])
            print("rename 'keyword' and 'tfidf_score'")
    

    create_wordcloud(global_keywords, output_dir)
    create_barchart(global_keywords, output_dir)
    

def create_wordcloud(global_keywords, output_dir):

    word_dict = dict(zip(global_keywords['keyword'], global_keywords['tfidf_score']))
    

    wordcloud = WordCloud(
        width=800, 
        height=400, 
        background_color='#FAF3E0',
        max_words=100,
        colormap='copper',  # color customize
        max_font_size=100,
        random_state=42
    ).generate_from_frequencies(word_dict)

    # create view
    plt.figure(figsize=(10, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Coffee Articles Keywords', fontsize=25, fontfamily='Chalkboard', fontweight='bold',pad=20)
    plt.gcf().patch.set_facecolor('#FAF3E0') #whole bg
    plt.tight_layout()
    
    # store view
    plt.savefig(f"{output_dir}/1-1. TF-IDF_wordcloud.png", dpi=300)
    plt.close()

def create_barchart(global_keywords, output_dir, top_n=20):

    df = global_keywords.head(top_n).copy()
    df = df.sort_values('tfidf_score')
    
    # create bar chart
    plt.figure(figsize=(12, 8))
    bars = plt.barh(df['keyword'], df['tfidf_score'], color='skyblue')
    
    # value mark
    for bar in bars:
        width = bar.get_width()
        plt.text(width + 0.01, bar.get_y() + bar.get_height()/2, 
                 f'{width:.3f}', ha='left', va='center')
    

    plt.title('Top Keywords in Coffee Articles (TF-IDF Score)', fontsize=18)
    plt.xlabel('TF-IDF Score', fontsize=14)
    plt.ylabel('Keywords', fontsize=14)
    plt.tight_layout()
    
    plt.savefig(f"{output_dir}/1-2. TF-IDF_barchart.png", dpi=300)
    plt.close()


# excusion
if __name__ == "__main__":

    global_keywords_csv = "Part02_TF-IDF_Result/1. TF-IDF_keywords(all).csv"

    visualize_global_keywords(global_keywords_csv)

    print("\nFinishing Processing")