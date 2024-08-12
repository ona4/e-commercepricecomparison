import requests
from serpapi import SerpApiClient
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-mpnet-base-v2')


def analyze_prices(product):
    monky_results = monky_api_1(product)
    monky2_results = monky_api_2(product)
    google_results = google_search(product)
    results = monky_results + monky2_results + google_results
    results = sorted(results, key=lambda x: float(x['price'].replace('$', '').replace(',', '')) if x[
                                                                                                       'price'] != 'Price not available' else float(
        'inf'))
    results = generate_similar_product_suggestions(product, results)
    return results


def monky_api_1(product):
    url = "https://run.mocky.io/v3/dad22e32-2bf5-43ea-aad8-3170300286a5"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            filtered_results = [
                {
                    'site': 'Amazon(Example)',
                    'title': item['name'],
                    'price': f"${item['price']}"
                }
                for item in data['products'] if product.lower() in item['name'].lower()
            ]
            return filtered_results
    except Exception as e:
        print(f"API error: {str(e)}")
    return []


def monky_api_2(product):
    url = "https://run.mocky.io/v3/2b905461-013e-41ca-b8a2-1e9e11907c99"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            filtered_results = [
                {
                    'site': 'Ebay(Example)',
                    'title': item['name'],
                    'price': f"${item['price']}"
                }
                for item in data['products'] if product.lower() in item['name'].lower()
            ]
            return filtered_results
    except Exception as e:
        print(f"API error: {str(e)}")
    return []


def google_search(product):
    client = SerpApiClient(api_key="037d9440ed050b3014b5df805820a9b1c257bb347d81819cf73842032500c85a")
    params = {
        "engine": "google",
        "q": f"{product} price",
        "google_domain": "google.com",
        "gl": "us",
        "hl": "en",
        "tbm": "shop"
    }

    
    results = client.search(params)

    google_results = []
    if "shopping_results" in results:
        for item in results["shopping_results"][:5]:
            google_results.append({
                'site': 'Search result',
                'title': item.get('title', 'N/A'),
                'price': item.get('price', 'Price not available'),
                'link': item.get('link','#'),
                'image': item.get('thumbnail','There is no any data')
            })

    return google_results


def generate_similar_product_suggestions(product, results):
    product_embedding = model.encode([product], convert_to_tensor=True)
    for result in results:
        result_embedding = model.encode([result['title']], convert_to_tensor=True)
        result['similarity'] = util.pytorch_cos_sim(product_embedding, result_embedding)[0][0].item()
    return sorted(results, key=lambda x: x.get('similarity', 0), reverse=True)


def analyze_sentiment(titles):
    positive_example = "This product is excellent and very useful."
    negative_example = "This product is terrible and a waste of money."
    embeddings = model.encode([positive_example, negative_example] + titles)
    positive_embedding = embeddings[0]
    negative_embedding = embeddings[1]
    product_embeddings = embeddings[2:]
    sentiments = []
    for product_embedding in product_embeddings:
        positive_similarity = util.pytorch_cos_sim(positive_embedding, product_embedding)[0][0].item()
        negative_similarity = util.pytorch_cos_sim(negative_embedding, product_embedding)[0][0].item()

        if positive_similarity > negative_similarity:
            sentiments.append("Positive")
        elif negative_similarity > positive_similarity:
            sentiments.append("Negative")
        else:
            sentiments.append("Neutral")

    overall_sentiment = max(set(sentiments), key=sentiments.count)

    return {
        'product_sentiments': sentiments,
        'overall_sentiment': overall_sentiment
    }


if __name__ == '__main__':
    product = "laptop"
    results = analyze_prices(product)
    for item in results:
        print(f"{item['site']}: {item['title']} - {item['price']} - Similarity: {item.get('similarity', 'N/A')}")
