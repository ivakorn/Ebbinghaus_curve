import asyncio
import sys
import matplotlib.pyplot as plt
import numpy as np

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from database.models import Word
from database.requests import Database

#if you are working on the windows
if sys.platform.lower().startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

#param
FETCH_OBJ = 8
MAX_Y_GRAPH = 110
MIN_Y_GRAPH = 60

# Ebbinghaus formula
def forgetting_curve(t_minutes, coefficient_strength=0):
    safe_minutes = np.maximum(t_minutes, 1)
    log_minutes = np.log10(safe_minutes)
    decay = log_minutes ** 1.25
    return 100 * (1.84 + coefficient_strength) / (
        1.84 + coefficient_strength + decay
    )


async def main():
    engine = create_async_engine(
        url="postgresql+psycopg://superuser:superpassword@127.0.0.1/mydatabase",
        echo=False,
    )
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    db = Database(async_session)

    time_now, list_objs = await db.fetch_object(FETCH_OBJ)

    # find the oldest review time (minutes since last repetition)
    minutes_list = []
    for obj in list_objs:
        obj_word: Word = obj[0]
        # time difference
        delta = time_now - obj_word.last_review
        # in minutes and hours/days
        minutes_since = int(delta.total_seconds() // 60)
        minutes_list.append(minutes_since)

    max_minutes_since = max(minutes_list)

    # x-axis: range from -max_minutes_since to +3 days in minutes.
    x = np.linspace(-max_minutes_since, 60 * 24 * 3, 700)

    plt.figure(figsize=(14, 7))

    for obj in list_objs:
        obj_word: Word = obj[0]
        delta = time_now - obj_word.last_review
        minutes_since = int(delta.total_seconds() // 60)

        # for each point, calculate retention:
        total_minutes = minutes_since + x
        y = forgetting_curve(total_minutes, obj.coefficient_strength)

        # plot the curve
        plt.plot(x / 60, y, label=obj_word.text)

        # point the 'now'
        retention_now = forgetting_curve(minutes_since, obj.coefficient_strength)
        plt.scatter(0, retention_now, color="red", zorder=3)
        plt.text(0.5, retention_now + 2,
                 f"{obj_word.text}: {retention_now:.1f}%",
                 fontsize=9)

    # vertical line 'now'
    plt.axvline(0, color="red", linestyle="-", alpha=0.6, label="NOW")

    # daily grid lines
    max_days = int(np.ceil(max_minutes_since / (60 * 24)))
    for d in range(-max_days, 4):
        plt.axvline(d * 24, color="lightblue", linestyle=":", alpha=0.5)
        if d < 0:
            label = f"{d}d"
        elif d == 0:
            label = "NOW"
        else:
            label = f"+{d}d"
        plt.text(d * 24, 105, label, ha="center", va="bottom",
                 fontsize=8, color="blue")

    plt.title("Ebbinghaus Forgetting Curves (NOW = 0)")
    plt.xlabel("Time relative to NOW (hours)")
    plt.ylabel("Retention (%)")
    plt.ylim(MIN_Y_GRAPH, MAX_Y_GRAPH)
    plt.xlim(-max_minutes_since / 60, (60 * 24 * 3) / 60)
    plt.legend()
    plt.grid(False)
    plt.tight_layout()
    plt.show()

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
