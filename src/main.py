import csv
import time
from dataclasses import dataclass
from pathlib import Path

# MODEL INPUT
@dataclass
class Book:
    book_id: str
    title: str
    authors: str
    publisher: str
    published_date: str
    page_count: int | None
    categories: str
    average_rating: float | None

    @property
    def search_key(self):
        return self.title.casefold()


@dataclass
class SearchInput:
    keyword: str
    data_size: int

# MODEL OUTPUT
@dataclass
class SearchResult:
    algorithm: str
    keyword: str
    found: bool
    book: Book | None
    comparisons: int
    elapsed_time: float

# MEMBACA DATASET
def load_books(file_path):
    books = []

    with open(
        file_path, "r", encoding="utf-8-sig",
        newline=""
    ) as file:
        reader = csv.DictReader(file)

        required = [
            "book_id", "title", "authors", "publisher",
            "published_date", "page_count",
            "categories", "average_rating"
        ]

        if not reader.fieldnames:
            raise ValueError("Header CSV tidak ditemukan.")

        missing = [
            column for column in required
            if column not in reader.fieldnames
        ]

        if missing:
            raise ValueError(
                f"Kolom CSV tidak ditemukan: {missing}. "
                f"Header tersedia: {reader.fieldnames}"
            )

        for row in reader:
            title = (row.get("title") or "").strip()

            if not title:
                continue

            try:
                page_count = int(row["page_count"])
            except (ValueError, TypeError):
                page_count = None

            try:
                rating = float(row["average_rating"])
            except (ValueError, TypeError):
                rating = None

            books.append(Book(
                book_id=(row.get("book_id") or "").strip(),
                title=title,
                authors=(row.get("authors") or "").strip(),
                publisher=(row.get("publisher") or "").strip(),
                published_date=(
                    row.get("published_date") or ""
                ).strip(),
                page_count=page_count,
                categories=(
                    row.get("categories") or ""
                ).strip(),
                average_rating=rating
            ))

    if not books:
        raise ValueError("Tidak ada data buku yang valid.")

    return books

# LINEAR SEARCH
def linear_search(books, keyword):
    target = keyword.casefold()
    comparisons = 0

    start = time.perf_counter()

    for book in books:
        comparisons += 1

        if book.search_key == target:
            elapsed = time.perf_counter() - start
            return SearchResult(
                "Linear Search", keyword, True, book,
                comparisons, elapsed
            )

    elapsed = time.perf_counter() - start

    return SearchResult(
        "Linear Search", keyword, False, None,
        comparisons, elapsed
    )


# BINARY SEARCH
def binary_search(books, keyword):
    target = keyword.casefold()
    left = 0
    right = len(books) - 1
    comparisons = 0

    start = time.perf_counter()

    while left <= right:
        mid = (left + right) // 2
        current = books[mid].search_key

        # Perbandingan kesamaan
        comparisons += 1

        if current == target:
            elapsed = time.perf_counter() - start
            return SearchResult(
                "Binary Search", keyword, True, books[mid],
                comparisons, elapsed
            )

        # Perbandingan untuk menentukan arah
        comparisons += 1

        if current < target:
            left = mid + 1
        else:
            right = mid - 1

    elapsed = time.perf_counter() - start

    return SearchResult(
        "Binary Search", keyword, False, None,
        comparisons, elapsed
    )


# MENAMPILKAN HASIL
def display_result(result):
    print(f"\nAlgoritma      : {result.algorithm}")
    print(f"Kata kunci     : {result.keyword}")
    print(
        "Status         : "
        + ("Ditemukan" if result.found else "Tidak ditemukan")
    )
    print(f"Perbandingan   : {result.comparisons}")
    print(f"Waktu          : {result.elapsed_time:.9f} detik")

    if result.book is not None:
        book = result.book
        print(f"ID buku        : {book.book_id}")
        print(f"Judul          : {book.title}")
        print(f"Penulis        : {book.authors}")
        print(f"Penerbit       : {book.publisher}")
        print(f"Tanggal terbit : {book.published_date}")
        print(f"Jumlah halaman : {book.page_count}")
        print(f"Kategori       : {book.categories}")
        print(f"Rating         : {book.average_rating}")


# BENCHMARK
def benchmark(books, output_path):
    sizes = [100, 1000, 10000, 15139]
    rows = []

    for n in sizes:
        if len(books) < n:
            print(
                f"Pengujian n={n} dilewati: "
                f"data valid hanya {len(books)} buku."
            )
            continue

        # Pilih n buku yang sama untuk kedua algoritma,
        # kemudian urutkan berdasarkan judul.
        data = sorted(
            books[:n],
            key=lambda book: book.search_key
        )

        # Semua skenario menggunakan dataset yang sama.
        scenarios = [
            ("Awal", data[0].title),
            ("Tengah", data[n // 2].title),
            ("Akhir", data[n - 1].title),
            ("Tidak ditemukan",
             "zzzz_keyword_tidak_ada_987654321")
        ]

        for scenario, keyword in scenarios:
            for search_function in (
                linear_search, binary_search
            ):
                result = search_function(data, keyword)

                rows.append({
                    "n": n,
                    "algoritma": result.algorithm,
                    "skenario": scenario,
                    "ditemukan": result.found,
                    "perbandingan": result.comparisons,
                    "waktu_detik": (
                        f"{result.elapsed_time:.9f}"
                    )
                })

    if not rows:
        print("Tidak ada hasil pengujian.")
        return

    output_path = Path(output_path)
    output_path.parent.mkdir(
        parents=True, exist_ok=True
    )

    with open(
        output_path, "w", encoding="utf-8-sig",
        newline=""
    ) as file:
        writer = csv.DictWriter(
            file, fieldnames=rows[0].keys()
        )
        writer.writeheader()
        writer.writerows(rows)

    print("\nHASIL BENCHMARK")
    print(
        f"{'n':>6} | {'Algoritma':<15} | "
        f"{'Skenario':<17} | {'Operasi':>7} | "
        f"{'Waktu (detik)':>14}"
    )
    print("-" * 75)

    for row in rows:
        print(
            f"{row['n']:>6} | "
            f"{row['algoritma']:<15} | "
            f"{row['skenario']:<17} | "
            f"{row['perbandingan']:>7} | "
            f"{row['waktu_detik']:>14}"
        )

    print(f"\nHasil tersimpan di: {output_path}")


# PROGRAM UTAMA
def main():
    dataset_path = Path("src/data/books.csv")

    try:
        books = load_books(dataset_path)
    except (OSError, ValueError) as error:
        print(f"Gagal membaca dataset: {error}")
        return

    print(f"Jumlah buku valid: {len(books)}")

    keyword = input(
        "\nMasukkan judul buku yang ingin dicari: "
    ).strip()

    if keyword:
        # Linear Search tidak mensyaratkan data terurut.
        display_result(linear_search(books, keyword))

        # Binary Search memerlukan data terurut.
        sorted_books = sorted(
            books, key=lambda book: book.search_key
        )
        display_result(binary_search(sorted_books, keyword))

    benchmark(books, "src/results/hasil_pengujian.csv")


if __name__ == "__main__":
    main()
