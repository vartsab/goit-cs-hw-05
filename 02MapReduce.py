import requests
from collections import defaultdict
from multiprocessing import Pool
import re
import matplotlib.pyplot as plt

# Функція для завантаження тексту з URL
def fetch_text(url):
    response = requests.get(url)
    response.raise_for_status()  # Перевірка на помилки при запиті
    return response.text

# Функція для розбиття тексту на слова
def tokenize(text):
    words = re.findall(r'\b\w+\b', text.lower())
    return words

# Функція для підрахунку частоти слів
def count_words(words_chunk):
    word_counts = defaultdict(int)
    for word in words_chunk:
        word_counts[word] += 1
    return word_counts

# Функція для об'єднання результатів
def reduce_counts(map_results):
    total_counts = defaultdict(int)
    for word_counts in map_results:
        for word, count in word_counts.items():
            total_counts[word] += count
    return total_counts

# Функція для візуалізації топ слів
def visualize_top_words(word_counts, top_n=10):
    top_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
    words, counts = zip(*top_words)
    
    plt.figure(figsize=(10, 6))
    plt.barh(words, counts, color='skyblue')
    plt.xlabel('Frequency')
    plt.ylabel('Words')
    plt.title(f'Top {top_n} Most Frequent Words')
    plt.gca().invert_yaxis()  # Змінюємо порядок відображення
    plt.show()

# Головна функція
def main(url):
    text = fetch_text(url)
    words = tokenize(text)

    # Розбиваємо список слів на частини для паралельної обробки
    num_chunks = 4  # Кількість процесів
    chunk_size = len(words) // num_chunks
    word_chunks = [words[i:i + chunk_size] for i in range(0, len(words), chunk_size)]

    # Використання багатопотоковості для підрахунку частоти слів
    with Pool(num_chunks) as pool:
        map_results = pool.map(count_words, word_chunks)

    # Зведення результатів
    total_counts = reduce_counts(map_results)

    # Візуалізація результатів
    visualize_top_words(total_counts, top_n=10)

if __name__ == '__main__':
    url = 'https://www.gutenberg.org/files/84/84-0.txt'  # Наприклад, текст "Frankenstein" Мері Шеллі
    main(url)
