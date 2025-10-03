# Ebbinghaus\_curve

**Ebbinghaus Curve** is a simple demonstration project that shows how Hermann Ebbinghaus’s forgetting theory can be implemented for spaced word repetition.

The project includes:

* a minimal PostgreSQL model
* SQL queries for calculating repetition priority
* Python examples (e.g., plotting forgetting curves)

---

## Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/ivakorn/Ebbinghaus_curve.git
cd Ebbinghaus_curve
```

### 2. Set up the environment

Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Run PostgreSQL with Docker

The project provides a `docker-compose.yml` file to run PostgreSQL.
Start it with:

```bash
docker-compose up -d
```

### 4. Initialize the database

After PostgreSQL is up, create the tables and populate them with test data using the script:

```bash
python update_db.py
```

This will create the `words` table and insert example English words with review dates and correct/incorrect answer statistics.

### 5. Run examples

* Fetch words from the database:

  ```bash
  python get_words.py
  ```

* Plot forgetting curves:

  ```bash
  python draw_graphs.py
  ```

---

## How it works

* **The theory**: the project uses Ebbinghaus’s forgetting curve formula:

$$
 R(t) = \frac{100 \cdot (1.84 + S)}{1.84 + S + (\log_{10} t)^{1.25}}
$$

where **S** is the *strength coefficient* (based on answer statistics).

* **SQL implementation**:
  Priority for each word is calculated directly in the query:

```sql
SELECT
    text,
    100 * (1.84 + GREATEST(correct_count * 0.8 - wrong_count * 0.5, 0))
      / (
          1.84 + GREATEST(correct_count * 0.8 - wrong_count * 0.5, 0)
          + POWER(LOG(GREATEST(EXTRACT(EPOCH FROM (NOW() - last_review)) / 60, 1)), 1.25)
      ) AS priority
FROM words
ORDER BY priority ASC
LIMIT 5;
```

This allows filtering and sorting words that need review directly at the database level, without extra client-side processing.

* **Python implementation**:
  Equivalent formula in Python:

```python
memory_decay_factor = (math.log10(max(minutes_since, 1))) ** 1.25
retention = 100 * (1.84 + strength) / (1.84 + strength + memory_decay_factor)
```

---

## Use cases

This model fits any application where learning depends on repetition and retention, such as:

* language learning
* exam preparation
* memorizing texts or formulas

---

## Feedback

If you’d like to dive deeper into the math behind Ebbinghaus’s formula, check out my detailed article on Habr: *“The Ebbinghaus Forgetting Curve in User Applications.”*

And if you want to see the theory in action, try my Telegram bot [@Duck - Your translater](https://t.me/LingoDuckBot).
It helps you learn English words and uses these algorithms to schedule reviews.
