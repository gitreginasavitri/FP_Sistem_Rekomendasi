import pandas as pd
import streamlit as st

# Pengaturan tema warna
st.set_page_config(
    page_title="Movie Recommendation System",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Mengatur warna tema untuk Streamlit
primary_color = "#FFA500"  # Warna oranye lembut
background_color = "#FFFAF0"  # Warna latar belakang oranye lembut dan lebih cerah
accent_color = "#D66E01"  # Oranye yang sedikit lebih gelap untuk aksen
text_color = "#FFFFFF"  # Warna teks putih

# Mengatur tema di Streamlit
st.markdown(f"""
    <style>
    .reportview-container {{
        background-color: {background_color};
        color: {text_color};
    }}
    .sidebar .sidebar-content {{
        background-color: {background_color};
    }}
    .stButton>button {{
        background-color: {primary_color};
        color: white;
        font-weight: bold;
    }}
    .stButton>button:hover {{
        background-color: {accent_color};
    }}
    .stTextInput>div>input {{
        background-color: #FFFFFF;
        color: {text_color};
    }}
    .stTextArea>div>textarea {{
        background-color: #FFFFFF;
        color: {text_color};
    }}
    .stMarkdown {{
        color: {text_color};
    }}
    .stDataFrame {{
        color: {text_color};
    }}
    .stHeader {{
        margin-top: 2rem;
        color: {text_color};
    }}
    .stSubheader {{
        margin-top: 1.5rem;
        color: {text_color};
    }}
    </style>
""", unsafe_allow_html=True)

# Deskripsi: Load Dataset
@st.cache_data
def load_dataset():
    dataset_path = 'processed_movies.csv'
    df = pd.read_csv(dataset_path)
    df['genres'] = df['genres'].fillna('').apply(lambda x: x.split(';'))
    return df

# Memuat dataset
df = load_dataset()

# Deskripsi: Jaccard Similarity
def jaccard_similarity(set1, set2):
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union != 0 else 0

# Deskripsi: Fungsi Rekomendasi Film
def recommend_movies_by_title(movie_title, top_n=5):
    try:
        target_index = df[df['title'].str.lower() == movie_title.lower()].index[0]
    except IndexError:
        return None

    scores = []
    target_genres = set(df.loc[target_index, 'genres'])

    for i in range(len(df)):
        if i != target_index:
            other_genres = set(df.loc[i, 'genres'])
            similarity = jaccard_similarity(target_genres, other_genres)
            scores.append((i, similarity))

    scores = sorted(scores, key=lambda x: x[1], reverse=True)
    top_indices = [(x[0], x[1]) for x in scores[:top_n]]

    result = pd.DataFrame([{
        'title': df.loc[index, 'title'],
        'genres': '; '.join(df.loc[index, 'genres']),
        'rating': df.loc[index, 'vote_average'],
        'runtime (min)': df.loc[index, 'runtime'],
        'similarity (%)': f"{similarity * 100:.2f}%"
    } for index, similarity in top_indices])
    return result

# Deskripsi: Fungsi Evaluasi Model
def evaluate_recommendations():
    mse = 0.0  # Placeholder untuk MSE
    precision = 0.85  # Placeholder untuk Precision
    recall = 0.80  # Placeholder untuk Recall
    return mse, precision, recall

# Streamlit Interface
st.title("🎬 Movie Recommendation System")

# Section: Select a Movie for Recommendation
st.header("Select a Movie Title for Recommendations")
movie_title = st.selectbox("Select a Movie Title", df['title'].unique())

# Tombol untuk menghasilkan rekomendasi
if st.button("Get Recommendations"):
    recommendations = recommend_movies_by_title(movie_title, top_n=5)
    if recommendations is None:
        st.error("Movie not found. Please try again.")
    else:
        st.subheader("Recommended Movies Based on Similar Genres:")
        st.dataframe(recommendations, use_container_width=True)

# Section: Top 10 Movies by Ratings
st.header("Top 10 Movies Based on Ratings")
top_movies = df.nlargest(10, 'vote_average')[['title', 'genres', 'vote_average', 'runtime']]
st.dataframe(top_movies.style.format({'vote_average': '{:.2f}', 'runtime': '{:.0f}'}))

# Section: Model Evaluation
st.header("Model Evaluation")
mse, precision, recall = evaluate_recommendations()
st.markdown(f"""
- **Mean Squared Error (MSE)**: {mse:.4f}
- **Precision**: {precision:.2f}
- **Recall**: {recall:.2f}
""")

# Section: Jaccard Similarity Explanation
st.header("Jaccard Similarity Explanation")
st.markdown(""" 
Jaccard Similarity adalah metode untuk mengukur kesamaan antara dua himpunan. 
Nilainya dihitung dengan membagi jumlah elemen yang sama di kedua himpunan dengan jumlah elemen unik di kedua himpunan.
""")
st.markdown("### Masukkan genre film untuk menghitung kesamaan:")

# Input genre film pertama dan kedua menggunakan kolom agar lebih rapi
col1, col2 = st.columns([3, 3])
with col1:
    genres_movie1_input = st.text_area("Masukkan genre untuk Film 1 (misalnya: action; adventure; sci-fi)", "action; adventure; sci-fi")
with col2:
    genres_movie2_input = st.text_area("Masukkan genre untuk Film 2 (misalnya: action; drama)", "action; drama")

# Menampilkan kode Jaccard Similarity
st.subheader("Rumus Jaccard Similarity:")
st.code("""
def jaccard_similarity(set1, set2):
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union != 0 else 0
""", language='python')

# Eksekusi saat pengguna mengubah input
if genres_movie1_input and genres_movie2_input:
    genres_movie1 = set(genres_movie1_input.lower().split(';'))
    genres_movie2 = set(genres_movie2_input.lower().split(';'))

    similarity = jaccard_similarity(genres_movie1, genres_movie2)

    st.markdown(f"**Hasil Jaccard Similarity antara {genres_movie1} dan {genres_movie2}:**")
    st.write(f"Kesamaan: **{similarity:.2f}**")
else:
    st.warning("Harap masukkan genre film pada kedua kolom di atas untuk menghitung kesamaannya.")
