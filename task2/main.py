import asyncio
import aiohttp
import multiprocessing as mp
import re
import matplotlib.pyplot as plt


def map_chunk(chunk: str):
    words = re.findall(r"\b\w+\b", chunk.lower())
    return [(w, 1) for w in words]


def group_words(mapped):
    groups = {}
    for word, count in mapped:
        groups.setdefault(word, []).append(count)
    return groups


def reduce_groups(groups):
    return {word: sum(counts) for word, counts in groups.items()}


async def fetch_text(url: str) -> str:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                resp.raise_for_status()
                return await resp.text()

    except aiohttp.ClientResponseError as e:
        print(f"HTTP error {e.status}: {e.message}")
    except aiohttp.ClientConnectorError:
        print("Connection error: cannot reach the server.")
    except aiohttp.InvalidURL:
        print(f"Invalid URL: {url}")
    except asyncio.TimeoutError:
        print("Request timed out.")
    except Exception as e:
        print(f"Unexpected error: {e}")

    return ""


def visualize_top_words(word_counts, top_n=10):
    sorted_items = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    top_words = sorted_items[:top_n]

    words = [w for w, _ in reversed(top_words)]
    counts = [c for _, c in reversed(top_words)]

    plt.figure(figsize=(10, 6))
    plt.xlabel("Frequency")
    plt.ylabel("Words")
    plt.barh(words, counts)
    plt.title(f"Top {top_n} Most Frequent Words")
    plt.tight_layout()
    plt.show()


async def main():
    url = "https://www.gutenberg.org/files/1342/1342-0.txt"
    print("Getting text")
    text = await fetch_text(url)
    print("Splitting text into chunks")

    chunks = text.split("\n\n")

    print(f"Processing {len(chunks)} chunks in parallel")

    with mp.Pool(mp.cpu_count()) as pool:
        mapped_parts = pool.map(map_chunk, chunks)

    mapped = [pair for part in mapped_parts for pair in part]
    grouped = group_words(mapped)
    reduced = reduce_groups(grouped)

    visualize_top_words(reduced, top_n=10)


if __name__ == "__main__":
    asyncio.run(main())
