"""
sort_algorithms.py
AllSortAnimationByBar.py のアルゴリズム群を
グローバル変数なし・JSON シリアライズ可能な形に移植
"""

import math
import random
from random import randint
import functools

# ---------------------------------------------------------------------------
# アルゴリズム一覧 / データサイズ一覧
# ---------------------------------------------------------------------------

DataSizeList = [16, 32, 64, 100, 128, 200, 256, 512, 1024, 2048]

DataConditionList = [
    "ランダム",
    "昇順",
    "降順",
    "ほぼ昇順",
    "ステップ値",
]

# ---------------------------------------------------------------------------
# ヘルパー
# ---------------------------------------------------------------------------

def make_frame(data, color, *, arrows=None, texts=None, lines=None,
               bars=None, finished=False):
    """generator が yield する共通フレーム形式を生成する"""
    return {
        "data":     list(data),
        "color":    list(color),
        "arrows":   arrows  or [],   # [[start, end], ...]
        "texts":    texts   or [],   # ["i=3", ...]
        "lines":    lines   or [],   # [[value, start, end], ...]
        "bars":     bars    or [],   # highlight されるバーのインデックス
        "finished": finished,
    }


def make_data(num_items: int, data_max: int, condition: int):
    """指定条件の data / color リストを返す"""
    if condition == 1:          # 昇順
        data = sorted([randint(1, data_max) for _ in range(num_items)])
    elif condition == 2:        # 降順
        data = sorted([randint(1, data_max) for _ in range(num_items)],
                      reverse=True)
    elif condition == 3:        # ほぼ昇順
        lst = sorted([randint(1, data_max) for _ in range(num_items)])
        for _ in range(max(1, num_items // 10)):
            i, j = random.sample(range(num_items), 2)
            lst[i], lst[j] = lst[j], lst[i]
        data = lst
    elif condition == 4:        # ステップ値
        steps = max(2, int(math.sqrt(num_items)))
        pool  = [randint(1, data_max // steps) + i * (data_max // steps)
                 for i in range(steps)]
        data  = random.choices(pool, k=num_items)
    else:                       # ランダム
        data = [randint(1, data_max) for _ in range(num_items)]

    color = ["b"] * num_items
    return data, color


# ---------------------------------------------------------------------------
# ソートアルゴリズム群  (global 変数なし / generator)
# ---------------------------------------------------------------------------

def bubble_sort(data, color):
    n = len(data)
    for i in range(n - 1):
        for j in range(n - i - 1):
            color[j] = "r"; color[j + 1] = "y"
            yield make_frame(data, color,
                             texts=[f"i={i}  {j}⇔{j+1}"], bars=[j, j+1])
            if data[j] > data[j + 1]:
                yield make_frame(data, color, arrows=[[j, j+1]],
                                 texts=[f"i={i}  {j}⇄{j+1}"], bars=[j, j+1])
                data[j], data[j + 1] = data[j + 1], data[j]
                color[j], color[j + 1] = color[j + 1], color[j]
                color[j] = "b"
                yield make_frame(data, color, arrows=[[j, j+1]],
                                 texts=[f"i={i}  {j}⇔{j+1}"], bars=[j, j+1])
            else:
                color[j] = "b"; color[j + 1] = "b"
                yield make_frame(data, color,
                                 texts=[f"i={i}  {j}⇔{j+1}"], bars=[j, j+1])
        color[n - i - 1] = "g"
        yield make_frame(data, color, bars=[n - i - 1])
    yield make_frame(data, color, finished=True)


def selection_sort(data, color):
    n = len(data)
    for i in range(n - 1):
        min_idx = i
        color[min_idx] = "r"
        yield make_frame(data, color,
                         texts=[f"i={i}  min={min_idx}"],
                         lines=[[data[min_idx], i, n - 1]], bars=[i])
        for j in range(i + 1, n):
            color[j] = "y"
            yield make_frame(data, color,
                             texts=[f"i={i}  min={min_idx}  j={j}"],
                             lines=[[data[min_idx], i, n - 1]], bars=[j])
            if data[j] < data[min_idx]:
                color[j], color[min_idx] = "r", "b"
                old_min = min_idx; min_idx = j
                yield make_frame(data, color,
                                 texts=[f"i={i}  min={min_idx}  j={j}"],
                                 lines=[[data[min_idx], i, n - 1]],
                                 bars=[old_min, j])
            else:
                color[j] = "b"
                yield make_frame(data, color,
                                 texts=[f"i={i}  min={min_idx}  j={j}"],
                                 lines=[[data[min_idx], i, n - 1]], bars=[j])
        if i != min_idx:
            yield make_frame(data, color,
                             arrows=[[i, min_idx]],
                             texts=[f"i={i} ⇄ min={min_idx}"],
                             lines=[[data[min_idx], i, n - 1]],
                             bars=[i, min_idx])
            data[i], data[min_idx] = data[min_idx], data[i]
            color[i], color[min_idx] = color[min_idx], color[i]
            yield make_frame(data, color,
                             arrows=[[i, min_idx]],
                             texts=[f"i={i} ⇄ min={min_idx}"],
                             lines=[[data[min_idx], i, n - 1]],
                             bars=[i, min_idx])
        color[i] = "g"
        yield make_frame(data, color,
                         texts=[f"i={i} 確定 min={min_idx}"], bars=[i])
    yield make_frame(data, color, finished=True)


def insertion_sort(data, color):
    n = len(data)
    for i in range(1, n):
        color[i] = "r"
        key = data[i]
        yield make_frame(data, color, texts=[f"i={i}  key={key}"], bars=[i])
        j = i - 1
        while j >= 0 and key < data[j]:
            yield make_frame(data, color, arrows=[[j, j+1]],
                             texts=[f"i={i}  j={j}  key={key}"],
                             bars=[j, j+1])
            data[j + 1], data[j] = data[j], data[j + 1]
            color[j + 1], color[j] = color[j], color[j + 1]
            yield make_frame(data, color, arrows=[[j, j+1]],
                             texts=[f"i={i}  j={j}  key={key}"],
                             bars=[j, j+1])
            j -= 1
        data[j + 1] = key
        color[j + 1] = "b"
        yield make_frame(data, color, texts=[f"i={i}  key={key} 挿入"],
                         bars=[j + 1])
    yield make_frame(data, color, finished=True)


def shell_sort(data, color):
    n = len(data)
    h = 1
    while h < n:
        h = 3 * h + 1
    h = (h - 1) // 3
    while h > 0:
        for i in range(h, n):
            color[i] = "r"
            key = data[i]
            yield make_frame(data, color,
                             texts=[f"h={h}  i={i}"], bars=[i])
            j = i - h
            while j >= 0 and key < data[j]:
                yield make_frame(data, color,
                                 texts=[f"h={h}  i={i}  j={j}⇔j+h={j+h}"],
                                 bars=[j, j + h])
                data[j + h], data[j] = data[j], data[j + h]
                color[j + h], color[j] = color[j], color[j + h]
                yield make_frame(data, color, arrows=[[j, j + h]],
                                 texts=[f"h={h}  i={i}  j={j}⇄j+h={j+h}"],
                                 bars=[j, j + h])
                j -= h
            data[j + h] = key
            color[j + h] = "b"
            yield make_frame(data, color, texts=[f"h={h}  i={i}"],
                             bars=[j + h])
        h = (h - 1) // 3
    yield make_frame(data, color, finished=True)


def quick_sort(data, color, option=None):
    n = len(data)
    stack = [(0, n - 1)]
    while stack:
        first, last = stack.pop()
        if first < last:
            # ピボット選択
            if first + 2 < last:
                if option == "Select3":
                    mid = (first + last) // 2
                    pivd = sorted([(data[first], first),
                                   (data[mid], mid),
                                   (data[last], last)],
                                  key=lambda x: x[0])
                    piv = pivd[1][1]
                    color[first] = color[last] = color[mid] = "m"
                    texts = [f"中央値選択  mid={mid}  first={first}  last={last}"]
                    yield make_frame(data, color,
                                     texts=texts,
                                     lines=[[data[last], first, last]],
                                     bars=[first, last, mid])
                    arrows = [[piv, last]] if piv != last else []
                    color[piv] = "c"
                    yield make_frame(data, color, arrows=arrows,
                                     texts=texts,
                                     lines=[[data[piv], first, last]],
                                     bars=[first, last, mid])
                    data[piv], data[last] = data[last], data[piv]
                    color[first] = color[last] = color[mid] = "b"
                    color[last] = "c"
                elif option == "Random":
                    piv = randint(first, last)
                    color[last] = "y"; color[piv] = "c"
                    texts = [f"ランダム選択={piv}  first={first}  last={last}"]
                    yield make_frame(data, color,
                                     arrows=[[piv, last]], texts=texts,
                                     lines=[[data[piv], first, last]],
                                     bars=[piv, last])
                    data[piv], data[last] = data[last], data[piv]
                    color[last] = "c"; color[piv] = "b"

            pivot = data[last]
            color[last] = "r"
            lines = [[pivot, first, last]]
            texts = [f"pivot={pivot}  first={first}  last={last}"]
            yield make_frame(data, color, texts=texts, lines=lines, bars=[last])
            i = first; j = last - 1
            color[i] = "y"
            if j > first:
                color[j] = "m"
            while True:
                if i < last:   color[i] = "y"
                if j > first:  color[j] = "m"
                while i < last and data[i] < pivot:
                    color[i] = "b"; i += 1
                    if i < last: color[i] = "y"
                    yield make_frame(data, color, texts=texts,
                                     lines=lines, bars=[i])
                while j >= first and data[j] > pivot:
                    color[j] = "b"; j -= 1
                    if j > first: color[j] = "m"
                    yield make_frame(data, color, texts=texts,
                                     lines=lines, bars=[j])
                if i >= j:
                    break
                data[i], data[j] = data[j], data[i]
                color[i], color[j] = color[j], color[i]
                yield make_frame(data, color, arrows=[[i, j]],
                                 texts=texts, lines=lines, bars=[i, j])
                color[i] = color[j] = "b"
                yield make_frame(data, color, texts=texts,
                                 lines=lines, bars=[i, j])
                i += 1; j -= 1
                yield make_frame(data, color, texts=texts,
                                 lines=lines, bars=[i, j])
            yield make_frame(data, color, arrows=[[i, last]],
                             texts=texts, lines=lines, bars=[i, last])
            data[i], data[last] = data[last], data[i]
            color[i], color[last] = color[last], color[i]
            color[i] = "g"; color[last] = "b"
            yield make_frame(data, color, arrows=[[i, last]],
                             texts=texts, lines=lines, bars=[i, last])
            stack.append((i + 1, last))
            stack.append((first, i - 1))
        elif last > 0:
            color[last] = "gray"
            yield make_frame(data, color, bars=[last])
    yield make_frame(data, color, finished=True)


quick_sort_select3  = functools.partial(quick_sort, option="Select3")
quick_sort_random   = functools.partial(quick_sort, option="Random")


# ---------------------------------------------------------------------------
# 並列クイックソート共通部品
# ---------------------------------------------------------------------------

def _gen_partition(data, color, first, last):
    """1回のパーティション処理をステップごとに yield するジェネレータ。
    yield: (done: bool, parts: list[(first,last)], info: dict)
      done=False : 処理継続中
      done=True  : パーティション完了。parts に次の処理範囲を返す。
    """
    if first >= last:
        # 要素が1個以下 → 即確定
        if first == last:
            color[first] = "g"
        if last > 0:
            color[last] = "gray"
        yield (True, [], {"arrows": [], "texts": [], "lines": [], "bars": ([last] if last >= 0 else [])})
        return

    pivot   = data[last]
    color[last] = "r"
    lines   = [[pivot, first, last]]
    texts   = [f"pivot={pivot}  [{first}..{last}]"]
    yield (False, [], {"arrows": [], "texts": texts, "lines": lines, "bars": [last]})

    i = first; j = last - 1
    color[i] = "y"
    if j > first:
        color[j] = "m"

    while True:
        if i < last:   color[i] = "y"
        if j > first:  color[j] = "m"
        while i < last and data[i] < pivot:
            color[i] = "b"; i += 1
            if i < last: color[i] = "y"
            yield (False, [], {"arrows": [], "texts": texts, "lines": lines, "bars": [i]})
        while j >= first and data[j] > pivot:
            color[j] = "b"; j -= 1
            if j > first: color[j] = "m"
            yield (False, [], {"arrows": [], "texts": texts, "lines": lines, "bars": [j]})
        if i >= j:
            break
        data[i], data[j] = data[j], data[i]
        color[i], color[j] = color[j], color[i]
        yield (False, [], {"arrows": [[i, j]], "texts": texts, "lines": lines, "bars": [i, j]})
        color[i] = color[j] = "b"
        yield (False, [], {"arrows": [], "texts": texts, "lines": lines, "bars": [i, j]})
        i += 1; j -= 1
        yield (False, [], {"arrows": [], "texts": texts, "lines": lines, "bars": [i, j]})

    # ピボットを確定位置へ
    yield (False, [], {"arrows": [[i, last]], "texts": texts, "lines": lines, "bars": [i, last]})
    data[i], data[last] = data[last], data[i]
    color[i], color[last] = color[last], color[i]
    color[i] = "g"; color[last] = "b"

    # 次の処理範囲を返す
    parts = []
    if first <= i - 1:
        parts.append((first, i - 1))
    if i + 1 <= last:
        parts.append((i + 1, last))

    yield (True, parts, {"arrows": [[i, last]], "texts": texts, "lines": lines, "bars": [i, last]})


def _quick_sort_parallel_core(data, color, max_tasks=0):
    """並列クイックソートの共通コア。
    max_tasks=0  : 制限なし（全ペンディングを同時実行）
    max_tasks>=2 : 同時実行タスク数を max_tasks に制限
    """
    from collections import deque
    n = len(data)
    pending = deque([(0, n - 1)])
    active  = []          # 実行中のジェネレータリスト

    while pending or active:
        # ペンディングからアクティブへ移動
        while pending:
            if max_tasks > 0 and len(active) >= max_tasks:
                break
            first, last = pending.popleft()
            active.append(_gen_partition(data, color, first, last))

        if not active:
            break

        # 全アクティブタスクを1ステップ進める
        arrows, bars, texts_all, lines_all = [], [], [], []
        new_active = []

        for task in active:
            done, parts, info = next(task)
            arrows.extend(info["arrows"])
            bars.extend(info["bars"])
            texts_all.extend(info["texts"])
            lines_all.extend(info["lines"])
            if not done:
                new_active.append(task)
            else:
                pending.extend(parts)

        n_active = len(active)
        n_pending = len(pending)
        header = [f"並列タスク: 実行中={n_active}  待機={n_pending}"]
        yield make_frame(data, color,
                         arrows=arrows,
                         bars=bars,
                         texts=header + texts_all[:6],   # 多すぎる場合は先頭6件だけ表示
                         lines=lines_all)
        active = new_active

    yield make_frame(data, color, finished=True)


def quick_sort_parallel(data, color):
    """並列クイックソート（上限なし）
    スタックに積まれた全サブ範囲を同時並行でパーティション処理する。
    """
    yield from _quick_sort_parallel_core(data, color, max_tasks=0)


def quick_sort_parallel_limited(data, color, max_tasks=4):
    """並列クイックソート（CPU数制限付き）
    同時に処理するパーティションを max_tasks 個に制限する。
    max_tasks は UI のスライダーで 2〜1024 の範囲で指定できる。
    """
    yield from _quick_sort_parallel_core(data, color, max_tasks=max_tasks)


def quick_sort_3way(data, color):
    """3-way partition クイックソート (Dijkstra Dutch National Flag)
    ピボットより小 / ピボットと等 / ピボットより大 の3領域に分割する。
    重複値が多いデータで通常版より大幅に高速になる。

    色の意味:
      r  = 現在参照中の要素 (i ポインタ)
      c  = ピボット未満と確定した領域 (lt 左側)
      g  = ピボットと等しい領域 (lt..i-1)
      m  = ピボット超過と確定した領域 (gt 右側)
      b  = 未分類
    """
    n = len(data)
    stack = [(0, n - 1)]

    while stack:
        first, last = stack.pop()
        if first >= last:
            # 要素が1つ以下 → 確定
            if first == last:
                color[first] = "g"
                yield make_frame(data, color, bars=[first])
            continue

        # ---- ピボット: 中央値3点選択 ----
        mid = (first + last) // 2
        trio = sorted(
            [(data[first], first), (data[mid], mid), (data[last], last)],
            key=lambda x: x[0]
        )
        piv_idx = trio[1][1]   # 中央値のインデックス
        pivot   = data[piv_idx]

        # ピボットを先頭に移動
        if piv_idx != first:
            data[first], data[piv_idx] = data[piv_idx], data[first]
            color[first], color[piv_idx] = color[piv_idx], color[first]
            yield make_frame(data, color,
                             arrows=[[first, piv_idx]],
                             texts=[f"pivot={pivot}  first={first}  last={last}  (中央値選択)"],
                             bars=[first, piv_idx])

        # ---- Dutch National Flag partition ----
        # 不変条件:
        #   data[first .. lt-1]  < pivot  (cyan)
        #   data[lt    .. i-1]  == pivot  (green)
        #   data[i     .. gt]    未分類   (blue)
        #   data[gt+1  .. last]  > pivot  (magenta)
        lt = first   # 等値領域の左端
        gt = last    # 未分類の右端
        i  = first

        # ピボット要素を等値領域へ
        color[first] = "g"
        yield make_frame(data, color,
                         texts=[f"pivot={pivot}  lt={lt}  gt={gt}"],
                         bars=[first])

        while i <= gt:
            texts = [f"pivot={pivot}  lt={lt}  i={i}  gt={gt}"]
            color[i] = "r"
            yield make_frame(data, color, texts=texts, bars=[i])

            if data[i] < pivot:
                # data[i] を lt 位置へ交換 → lt を右へ, i を右へ
                data[lt], data[i] = data[i], data[lt]
                color[lt], color[i] = color[i], color[lt]
                color[lt] = "c"          # lt 位置は < pivot 確定
                yield make_frame(data, color,
                                 arrows=[[lt, i]],
                                 texts=[f"pivot={pivot}  {i}→lt={lt} (<pivot)"],
                                 bars=[lt, i])
                color[i] = "g"           # i 位置は == pivot 領域へ
                lt += 1
                i  += 1

            elif data[i] == pivot:
                # そのまま等値領域を拡張
                color[i] = "g"
                yield make_frame(data, color,
                                 texts=[f"pivot={pivot}  i={i} ==pivot"],
                                 bars=[i])
                i += 1

            else:
                # data[i] > pivot: gt 位置へ交換 → gt を左へ
                color[gt] = "r"
                yield make_frame(data, color,
                                 texts=[f"pivot={pivot}  {i}→gt={gt} (>pivot)"],
                                 bars=[i, gt])
                data[i], data[gt] = data[gt], data[i]
                color[i], color[gt] = color[gt], color[i]
                color[gt] = "m"          # gt 位置は > pivot 確定
                yield make_frame(data, color,
                                 arrows=[[i, gt]],
                                 texts=[f"pivot={pivot}  {i}⇄gt={gt}"],
                                 bars=[i, gt])
                gt -= 1
                # i は進めない (交換で来た要素を再評価)

        # 等値領域を確定色に
        for k in range(lt, gt + 1):
            color[k] = "g"
        yield make_frame(data, color,
                         texts=[f"pivot={pivot}  確定: lt={lt}..gt={gt}"],
                         bars=list(range(lt, gt + 1)))

        # 右を先にpush → 左(前半)が先に処理される (他のクイックソートと同順)
        stack.append((gt + 1, last))
        stack.append((first, lt - 1))

    yield make_frame(data, color, finished=True)


def bitonic_sort(data, color):
    n = len(data)
    N = math.floor(math.log(n, 2))
    num = 2 ** N          # 実際に使う要素数 (2の冪)
    for fb in range(1, N + 1):
        yield make_frame(data, color, texts=[f"fb={fb}"])
        for sb in range(fb - 1, -1, -1):
            yield make_frame(data, color, texts=[f"fb={fb}  sb={sb}"])
            for i in range(1 << N):
                if ((i >> fb) & 1) ^ ((i >> sb) & 1) == 1:
                    j = i ^ (1 << sb)
                    color[i] = "r"; color[j] = "y"
                    yield make_frame(data, color,
                                     texts=[f"fb={fb}  sb={sb}  {i}⇔{j}"],
                                     bars=[i, j])
                    if data[i] < data[j]:
                        data[i], data[j] = data[j], data[i]
                        color[i], color[j] = color[j], color[i]
                        yield make_frame(data, color, arrows=[[i, j]],
                                         texts=[f"fb={fb}  sb={sb}  {i}⇄{j}"],
                                         bars=[i, j])
                    color[i] = "b"; color[j] = "b"
                    yield make_frame(data, color,
                                     texts=[f"fb={fb}  sb={sb}  {i}⇔{j}"],
                                     bars=[i, j])
    yield make_frame(data, color, finished=True)


def _bitonic_swap_gen(data, color, fb, sb, i):
    """並列バイトニックソート用サブgenerator"""
    j = i ^ (1 << sb)
    color[i] = "r"; color[j] = "y"
    yield False, {"arrows": [[i, j]], "bars": [i, j]}
    if data[i] < data[j]:
        data[i], data[j] = data[j], data[i]
        color[i], color[j] = color[j], color[i]
        yield False, {"arrows": [[i, j]], "bars": [i, j]}
    color[i] = "b"; color[j] = "b"
    yield True,  {"arrows": [], "bars": [i, j]}


def bitonic_sort_parallel(data, color):
    n = len(data)
    N = math.floor(math.log(n, 2))
    for fb in range(1, N + 1):
        yield make_frame(data, color, texts=[f"fb={fb}"])
        for sb in range(fb - 1, -1, -1):
            tasks = []
            for i in range(1 << N):
                if ((i >> fb) & 1) ^ ((i >> sb) & 1) == 1:
                    tasks.append(_bitonic_swap_gen(data, color, fb, sb, i))
            while tasks:
                arrows, bars, new_tasks = [], [], []
                for task in tasks:
                    done, info = next(task)
                    arrows.extend(info["arrows"])
                    bars.extend(info["bars"])
                    if not done:
                        new_tasks.append(task)
                yield make_frame(data, color,
                                 arrows=arrows,
                                 texts=[f"fb={fb}  sb={sb}  tasks={len(tasks)}"],
                                 bars=bars)
                tasks = new_tasks
    yield make_frame(data, color, finished=True)


def comb_sort(data, color):
    n = len(data)
    h = n * 10 // 13
    while True:
        if h in (9, 10):
            h = 11
        swapped = False
        for i in range(n - h):
            color[i] = "r"; color[i + h] = "y"
            yield make_frame(data, color,
                             texts=[f"h={h}  i={i}⇔i+h={i+h}"],
                             bars=[i, i + h])
            if data[i] > data[i + h]:
                data[i + h], data[i] = data[i], data[i + h]
                color[i + h], color[i] = color[i], color[i + h]
                swapped = True
                yield make_frame(data, color, arrows=[[i, i + h]],
                                 texts=[f"h={h}  i={i}⇄i+h={i+h}"],
                                 bars=[i, i + h])
            color[i] = "b"; color[i + h] = "b"
            yield make_frame(data, color,
                             texts=[f"h={h}  i={i}⇔i+h={i+h}"],
                             bars=[i, i + h])
        yield make_frame(data, color, texts=[f"h={h}"])
        if h == 1:
            if not swapped:
                break
        else:
            h = h * 10 // 13
    yield make_frame(data, color, finished=True)


def gnome_sort(data, color):
    n = len(data)
    i = 0
    while i < n:
        color[i] = "r"
        yield make_frame(data, color, texts=[f"i={i}"], bars=[i])
        if i == 0:
            color[i] = "b"
            yield make_frame(data, color, texts=[f"i={i}"], bars=[i])
            i += 1
        else:
            color[i - 1] = "y"
            yield make_frame(data, color, texts=[f"i={i}"], bars=[i - 1, i])
            if data[i - 1] <= data[i]:
                color[i - 1] = "b"
                yield make_frame(data, color, texts=[f"i={i}"], bars=[i - 1])
                i += 1
                color[i - 1] = "b"
            else:
                data[i], data[i - 1] = data[i - 1], data[i]
                color[i - 1] = "r"; color[i] = "y"
                yield make_frame(data, color, arrows=[[i - 1, i]],
                                 texts=[f"i={i}"], bars=[i - 1, i])
                color[i] = "b"
                i -= 1
    yield make_frame(data, color, finished=True)


def merge_sort_iter(data, color):
    """ボトムアップ・マージソート（繰り返し版）
    width=1 から始め、隣り合うサブ列を順にマージして倍々に拡大する。
    バッファ・木構造表示なし: マージ書き戻し時のバーの動きのみを可視化。
    色の意味:
      c = マージ前の左サブ列
      m = マージ前の右サブ列
      r = 比較中の書き込み先
      c = 書き込み完了（一瞬だけ点灯）
    """
    n = len(data)
    width = 1

    while width < n:
        for left in range(0, n, 2 * width):
            mid   = min(left + width - 1,     n - 1)
            right = min(left + 2 * width - 1, n - 1)
            if mid >= right:
                continue                             # マージ不要

            # マージ対象範囲を色分けしてハイライト
            for k in range(left, mid + 1):       color[k] = "c"
            for k in range(mid + 1, right + 1):  color[k] = "m"
            yield make_frame(
                data, color,
                texts=[f"width={width}  [{left}..{mid}] + [{mid+1}..{right}]"],
                bars=list(range(left, right + 1)),
            )
            for k in range(left, right + 1):     color[k] = "b"

            # 一時バッファへコピー → マージして書き戻し
            tmp      = data[left:right + 1]
            left_len = mid - left + 1
            i, j, k  = 0, left_len, left

            while i < left_len and j < len(tmp):
                color[k] = "r"
                yield make_frame(
                    data, color,
                    texts=[f"width={width}  {tmp[i]} vs {tmp[j]}"],
                    bars=[k],
                )
                if tmp[i] <= tmp[j]:
                    data[k] = tmp[i];  i += 1
                else:
                    data[k] = tmp[j];  j += 1
                color[k] = "c"
                yield make_frame(
                    data, color,
                    texts=[f"width={width}  [{k}] ← {data[k]}"],
                    bars=[k],
                )
                color[k] = "b"
                k += 1

            while i < left_len:
                data[k] = tmp[i]
                color[k] = "c"
                yield make_frame(
                    data, color,
                    texts=[f"width={width}  残り左 [{k}] ← {data[k]}"],
                    bars=[k],
                )
                color[k] = "b"
                i += 1;  k += 1

            while j < len(tmp):
                data[k] = tmp[j]
                color[k] = "c"
                yield make_frame(
                    data, color,
                    texts=[f"width={width}  残り右 [{k}] ← {data[k]}"],
                    bars=[k],
                )
                color[k] = "b"
                j += 1;  k += 1

        width *= 2

    yield make_frame(data, color, finished=True)


def heap_sort(data, color):
    """ヒープソート（最大ヒープ）
    Phase 1: ボトムアップでヒープを構築 (sift_down × n/2 回)
    Phase 2: 根と末尾を交換して末尾を確定、根を sift_down で再構築
    バッファ・木構造表示なし: バーの移動だけを可視化。
    色の意味:
      r = sift_down 対象ノード
      y = 比較する子ノード
      g = ソート確定済み（末尾から積み上がる）
    """
    n = len(data)

    def sift_down(root, end, phase):
        """最大ヒープの sift_down をステップ単位で yield するサブジェネレータ"""
        while True:
            largest = root
            lc = 2 * root + 1
            rc = 2 * root + 2

            cands = [root]
            color[root] = "r"
            if lc <= end: color[lc] = "y"; cands.append(lc)
            if rc <= end: color[rc] = "y"; cands.append(rc)
            yield make_frame(data, color,
                             texts=[f"{phase}  node={root}"],
                             bars=cands)

            if lc <= end and data[lc] > data[largest]: largest = lc
            if rc <= end and data[rc] > data[largest]: largest = rc

            if lc <= end: color[lc] = "b"
            if rc <= end: color[rc] = "b"

            if largest == root:
                # これ以上沈まない → 確定
                color[root] = "b"
                yield make_frame(data, color,
                                 texts=[f"{phase}  [{root}] 安定"],
                                 bars=[root])
                break

            # 子と交換して下へ潜る
            color[largest] = "y"
            yield make_frame(data, color,
                             arrows=[[root, largest]],
                             texts=[f"{phase}  {root} ⇄ {largest}"],
                             bars=[root, largest])
            data[root], data[largest] = data[largest], data[root]
            color[root], color[largest] = color[largest], color[root]
            yield make_frame(data, color,
                             texts=[f"{phase}  {root} ⇄ {largest}"],
                             bars=[root, largest])
            color[root] = "b"
            root = largest

    # ─── Phase 1: ヒープ構築 ───────────────────────────────────────────
    for i in range(n // 2 - 1, -1, -1):
        yield from sift_down(i, n - 1, f"ヒープ構築[{i}]")

    # ─── Phase 2: 最大値を末尾へ繰り返し送り出す ──────────────────────
    for end in range(n - 1, 0, -1):
        color[0] = "r"; color[end] = "y"
        yield make_frame(data, color,
                         arrows=[[0, end]],
                         texts=[f"最大 {data[0]} → [{end}]"],
                         bars=[0, end])
        data[0], data[end] = data[end], data[0]
        color[0], color[end] = color[end], color[0]
        color[end] = "g"
        yield make_frame(data, color,
                         texts=[f"[{end}] 確定"],
                         bars=[0, end])
        color[0] = "b"
        if end > 1:
            yield from sift_down(0, end - 1, f"再構築")

    color[0] = "g"
    yield make_frame(data, color, finished=True)


def pancake_sort(data, color):
    n = len(data)
    for i in range(n, 1, -1):
        max_idx = 0
        color[max_idx] = "r"
        yield make_frame(data, color,
                         texts=[f"i={i}  max={max_idx}"],
                         lines=[[data[max_idx], 0, i]], bars=[0])
        for j in range(1, i):
            color[j] = "y"
            yield make_frame(data, color,
                             texts=[f"i={i}  max={max_idx}  j={j}"],
                             lines=[[data[max_idx], 0, i]], bars=[j])
            if data[j] > data[max_idx]:
                color[j], color[max_idx] = "r", "b"
                old_max = max_idx; max_idx = j
                yield make_frame(data, color,
                                 texts=[f"i={i}  max={max_idx}  j={j}"],
                                 lines=[[data[max_idx], 0, i]],
                                 bars=[old_max, j])
            else:
                color[j] = "b"
                yield make_frame(data, color,
                                 texts=[f"i={i}  max={max_idx}  j={j}"],
                                 lines=[[data[max_idx], 0, i]], bars=[j])
        color[max_idx] = "b"
        if max_idx != i - 1:
            # flip 0..max_idx
            if max_idx > 0:
                for k in range((max_idx + 1) // 2):
                    color[k] = "c"; color[max_idx - k] = "y"
                    yield make_frame(data, color,
                                     arrows=[[k, max_idx - k]],
                                     texts=[f"i={i}  反転 0-{max_idx}"],
                                     bars=[k, max_idx - k])
                    data[k], data[max_idx - k] = data[max_idx - k], data[k]
                    color[k] = "y"; color[max_idx - k] = "c"
                    yield make_frame(data, color,
                                     arrows=[[k, max_idx - k]],
                                     texts=[f"i={i}  反転 0-{max_idx}"],
                                     bars=[k, max_idx - k])
                    color[k] = "b"; color[max_idx - k] = "b"
                    yield make_frame(data, color,
                                     texts=[f"i={i}  反転 0-{max_idx}"],
                                     bars=[k, max_idx - k])
            # flip 0..i-1
            if i - 1 > 0:
                for k in range(i // 2):
                    color[k] = "c"; color[i - 1 - k] = "y"
                    yield make_frame(data, color,
                                     arrows=[[k, i - 1 - k]],
                                     texts=[f"i={i}  反転 0-{i-1}"],
                                     bars=[k, i - 1 - k])
                    data[k], data[i - 1 - k] = data[i - 1 - k], data[k]
                    color[k] = "y"; color[i - 1 - k] = "c"
                    yield make_frame(data, color,
                                     arrows=[[k, i - 1 - k]],
                                     texts=[f"i={i}  反転 0-{i-1}"],
                                     bars=[k, i - 1 - k])
                    color[k] = "b"; color[i - 1 - k] = "b"
                    yield make_frame(data, color,
                                     texts=[f"i={i}  反転 0-{i-1}"],
                                     bars=[k, i - 1 - k])
        color[i - 1] = "g"
        yield make_frame(data, color,
                         texts=[f"i={i}  max={max_idx} 確定"], bars=[i - 1])
    yield make_frame(data, color, finished=True)


# ---------------------------------------------------------------------------
# アルゴリズム一覧 (名前, 関数)
# ---------------------------------------------------------------------------

AlgorithmList = [
    ("バブルソート",                        bubble_sort),
    ("選択ソート",                          selection_sort),
    ("挿入ソート",                          insertion_sort),
    ("シェルソート",                        shell_sort),
    ("マージソート (繰り返し)",             merge_sort_iter),
    ("ヒープソート",                        heap_sort),
    ("クイックソート",                      quick_sort),
    ("クイックソート (3点中央値)",          quick_sort_select3),
    ("クイックソート (ランダム選択)",       quick_sort_random),
    ("クイックソート (3-way partition)",    quick_sort_3way),
    ("並列クイックソート (CPU数無制限)",     quick_sort_parallel),
    ("並列クイックソート (CPU数制限)",      quick_sort_parallel_limited),
    ("バイトニックソート",                  bitonic_sort),
    ("並列バイトニックソート",              bitonic_sort_parallel),
    ("コムソート",                          comb_sort),
    ("ノームソート",                        gnome_sort),
    ("パンケーキソート",                    pancake_sort),
]
