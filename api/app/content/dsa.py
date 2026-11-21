from app.content._build import lesson, question, section

CONTENT = {
    "dsa-big-o": lesson(
        "Big-O describes how an algorithm's work grows as its input grows. It lets you compare approaches before you write them.",
        [
            section(
                "Common growth rates",
                "Count the steps relative to the input size n and keep only the fastest-growing term. O(1) is constant, O(log n) halves the work each step, O(n) is one pass, O(n log n) is efficient sorting, and O(n²) usually means nested loops over the same data. Constants are dropped: 3n + 5 is O(n).",
                r"""
                def first(items):                  # O(1): one step, whatever the size
                    return items[0]


                def total(items):                  # O(n): one pass
                    result = 0
                    for x in items:
                        result += x
                    return result


                def has_pair_sum(items, target):   # O(n^2): checks every pair
                    for i in range(len(items)):
                        for j in range(i + 1, len(items)):
                            if items[i] + items[j] == target:
                                return True
                    return False
                """,
            ),
            section(
                "Measure with timeit",
                "Big-O predicts growth; `timeit` measures real time. Double n and watch: O(n) code roughly doubles, O(n²) code roughly quadruples. Space complexity counts extra memory in the same way.",
                r"""
                import timeit

                for n in (1_000, 2_000, 4_000):
                    data = list(range(n))
                    seconds = timeit.timeit(lambda: has_pair_sum(data, -1), number=3)
                    print(n, round(seconds, 3))
                """,
            ),
        ],
        [
            "Big-O keeps the fastest-growing term and drops constants.",
            "Nested loops over the same input usually mean O(n²).",
            "Confirm your analysis by timing the code with `timeit` at several sizes.",
        ],
        r"""
        import timeit


        def dupes_nested(items):      # O(n^2) time, O(1) extra space
            return any(items[i] == items[j]
                       for i in range(len(items))
                       for j in range(i + 1, len(items)))


        def dupes_sorted(items):      # O(n log n) time, O(n) space
            s = sorted(items)
            return any(a == b for a, b in zip(s, s[1:]))


        def dupes_set(items):         # O(n) time, O(n) space
            return len(set(items)) != len(items)


        data = list(range(3_000))     # no duplicates: the worst case
        for fn in (dupes_nested, dupes_sorted, dupes_set):
            print(fn.__name__, round(timeit.timeit(lambda: fn(data), number=3), 4))
        """,
        [
            question("What is the Big-O of `3n² + 100n + 7`?", ["O(n)", "O(n²)", "O(3n²)", "O(n³)"], 1,
                     "Keep the fastest-growing term (n²) and drop constant factors."),
            question("Binary search halves the remaining items at each step. Its complexity is…", ["O(1)", "O(log n)", "O(n)", "O(n log n)"], 1,
                     "Halving n repeatedly reaches 1 after about log₂(n) steps."),
            question("An O(n²) function takes 1 second for n = 1,000. Roughly how long for n = 2,000?", ["1 s", "2 s", "4 s", "8 s"], 2,
                     "Doubling n multiplies n² by 4."),
        ],
    ),
    "dsa-builtins": lesson(
        "Python's built-in types have very different costs. Knowing them is the quickest way to speed up real code.",
        [
            section(
                "A cost cheat sheet",
                "**list**: indexing O(1), append and pop at the end O(1), insert or pop at the front O(n), `x in list` O(n).\n\n"
                "**dict** and **set** are hash tables: lookup, insert and delete are O(1) on average.\n\n"
                "**collections.deque**: append and pop at both ends O(1), but indexing into the middle is O(n).",
                r"""
                from collections import deque

                items = [1, 2, 3]
                items.append(4)        # O(1) amortised
                items.pop()            # O(1): from the end
                items.insert(0, 0)     # O(n): shifts every element
                items.pop(0)           # O(n)

                queue = deque([1, 2, 3])
                queue.appendleft(0)    # O(1)
                queue.popleft()        # O(1)
                """,
            ),
            section(
                "Membership: list vs set",
                "`x in list` checks items one by one; `x in set` hashes x and jumps straight to it. If you test membership inside a loop, convert the list to a set once, first.",
                r"""
                import timeit

                numbers = list(range(100_000))
                as_set = set(numbers)
                print(timeit.timeit(lambda: 99_999 in numbers, number=1_000))   # O(n): slow
                print(timeit.timeit(lambda: 99_999 in as_set, number=1_000))    # O(1): fast
                """,
            ),
        ],
        [
            "Avoid `list.insert(0, x)` and `list.pop(0)` in loops; use a deque.",
            "Use a set or dict for repeated membership tests.",
            "`sorted()` and `list.sort()` cost O(n log n).",
        ],
        r"""
        import timeit
        from collections import deque

        N = 50_000
        as_list, as_set = list(range(N)), set(range(N))
        print("list membership:", timeit.timeit(lambda: N - 1 in as_list, number=200))
        print("set membership: ", timeit.timeit(lambda: N - 1 in as_set, number=200))


        def fill_list():
            items = []
            for i in range(N):
                items.insert(0, i)      # O(n) each time -> O(n^2) overall


        def fill_deque():
            items = deque()
            for i in range(N):
                items.appendleft(i)     # O(1) each time -> O(n) overall


        print("list front inserts: ", timeit.timeit(fill_list, number=1))
        print("deque front inserts:", timeit.timeit(fill_deque, number=1))
        """,
        [
            question("What is the average cost of `key in my_dict`?", ["O(1)", "O(log n)", "O(n)", "O(n²)"], 0,
                     "Dicts are hash tables, so a lookup jumps straight to the right slot on average."),
            question("Which list operation is O(n)?", ["items[5]", "items.append(x)", "items.pop()", "items.pop(0)"], 3,
                     "Removing the first item shifts every remaining element one place to the left."),
            question("You need a first-in, first-out queue with fast adds and removes. Use…", ["a list with pop(0)", "collections.deque", "a set", "a string"], 1,
                     "deque supports O(1) append and popleft, which is exactly what a queue needs."),
        ],
    ),
    "dsa-arrays": lesson(
        "Two pointers and sliding windows turn many O(n²) array problems into a single O(n) pass.",
        [
            section(
                "Two pointers",
                "On a sorted list, start one pointer at each end. If the pair's sum is too small, move the left pointer right; if it's too big, move the right pointer left. Each step rules out one candidate, so the loop is O(n).",
                r"""
                def pair_with_sum(nums: list[int], target: int) -> tuple[int, int] | None:
                    left, right = 0, len(nums) - 1
                    while left < right:
                        total = nums[left] + nums[right]
                        if total == target:
                            return nums[left], nums[right]
                        if total < target:
                            left += 1
                        else:
                            right -= 1
                    return None


                print(pair_with_sum([1, 3, 4, 6, 9], 10))   # (1, 9)
                """,
            ),
            section(
                "Sliding windows",
                "Keep a window over part of the list. Grow it on the right, and when it breaks a rule, shrink it from the left. Each index enters and leaves the window once, so the whole scan is O(n). A fixed-size window simply adds the new item and removes the old one.",
                r"""
                def max_window_sum(nums: list[int], k: int) -> int:
                    window = sum(nums[:k])
                    best = window
                    for right in range(k, len(nums)):
                        window += nums[right] - nums[right - k]   # slide by one
                        best = max(best, window)
                    return best


                print(max_window_sum([2, 1, 5, 1, 3, 2], 3))   # 9 (5 + 1 + 3)
                """,
            ),
        ],
        [
            "Two pointers work when the data is sorted or the pointers only ever move in one direction.",
            "A sliding window reuses the previous window's work instead of recomputing it.",
            "Both patterns typically turn O(n²) into O(n).",
        ],
        r"""
        def longest_unique_substring(text: str) -> int:
            last_seen: dict[str, int] = {}
            left = best = 0
            for right, char in enumerate(text):
                if char in last_seen and last_seen[char] >= left:
                    left = last_seen[char] + 1      # shrink past the earlier copy
                last_seen[char] = right
                best = max(best, right - left + 1)
            return best


        assert longest_unique_substring("abcabcbb") == 3   # "abc"
        assert longest_unique_substring("bbbb") == 1
        assert longest_unique_substring("") == 0
        # pair_with_sum from the lesson solves the first part of the exercise.
        """,
        [
            question("Why does the two-pointer pair search need a sorted list?", ["So it uses less memory", "So moving a pointer predictably makes the sum bigger or smaller", "Python requires it", "It doesn't"], 1,
                     "Sorting guarantees that moving left increases the sum and moving right decreases it."),
            question("What is the time complexity of the sliding-window maximum sum?", ["O(k)", "O(n)", "O(n·k)", "O(n²)"], 1,
                     "Each step adds one item and removes one, so the scan is a single pass."),
            question("In the longest-unique-substring window, what happens when a character repeats inside the window?", ["Reset both pointers to 0", "Move left to just after the earlier copy", "Move right back", "Stop the scan"], 1,
                     "Moving left past the earlier copy restores the 'no repeats' rule while keeping as much of the window as possible."),
        ],
    ),
    "dsa-stacks-queues": lesson(
        "A stack is last-in, first-out (LIFO); a queue is first-in, first-out (FIFO). Many problems become simple once you see which one they need.",
        [
            section(
                "Stacks with a list",
                "Use a list's `append` and `pop`, which are both O(1) at the end. Stacks fit anything involving nesting or undo: matching brackets, function calls, browser history.",
                r"""
                history = []
                history.append("home")
                history.append("docs")
                history.append("api")
                print(history.pop())   # api  (last in, first out)
                print(history[-1])     # docs (peek without removing)
                """,
            ),
            section(
                "Queues with deque",
                "A queue serves items in arrival order. `collections.deque` adds and removes at both ends in O(1). Use `queue.Queue` instead when several threads share the queue.",
                r"""
                from collections import deque

                jobs = deque()
                jobs.append("report.pdf")
                jobs.append("photo.png")
                while jobs:
                    print("Printing", jobs.popleft())   # first in, first out
                """,
            ),
        ],
        [
            "Stack = LIFO: `append` and `pop` at the end of a list.",
            "Queue = FIFO: `append` and `popleft` on a deque.",
            "If a problem mentions nesting, matching or undo, think stack.",
        ],
        r"""
        from collections import deque

        PAIRS = {")": "(", "]": "[", "}": "{"}


        def is_balanced(text: str) -> bool:
            stack: list[str] = []
            for char in text:
                if char in "([{":
                    stack.append(char)
                elif char in PAIRS:
                    if not stack or stack.pop() != PAIRS[char]:
                        return False
            return not stack


        assert is_balanced("f(a[1]) {ok}")
        assert not is_balanced("(]")
        assert not is_balanced("((")


        def print_queue(documents: list[str]) -> None:
            queue = deque(documents)
            while queue:
                doc = queue.popleft()
                print(f"Printing {doc} ({len(queue)} waiting)")


        print_queue(["cv.pdf", "notes.txt", "photo.png"])
        """,
        [
            question("You push 1, 2 and 3 onto a stack, then pop twice. What's left?", ["[1]", "[3]", "[1, 2]", "[2, 3]"], 0,
                     "Pops remove 3, then 2, leaving 1."),
            question("Which structure does breadth-first search use?", ["Stack", "Queue", "Heap", "Set"], 1,
                     "BFS visits nodes in the order they were discovered, which is first-in, first-out."),
            question("Why is `list.pop(0)` a poor queue?", ["It raises an error", "It's O(n) because every element shifts", "It removes the last item", "Lists can't hold strings"], 1,
                     "Removing from the front shifts all remaining elements; deque.popleft() is O(1)."),
        ],
    ),
    "dsa-linked-lists": lesson(
        "A linked list stores items in nodes that point to the next node. Inserting at the front is O(1), but finding an item is O(n).",
        [
            section(
                "Nodes and traversal",
                "Each node holds a value and a reference to the next node; the last node points to `None`. To visit every item, start at the head and follow `next` until you reach `None`.",
                r"""
                class Node:
                    def __init__(self, value, next=None):
                        self.value = value
                        self.next = next


                head = Node(1, Node(2, Node(3)))   # 1 -> 2 -> 3
                node = head
                while node:
                    print(node.value)
                    node = node.next
                """,
            ),
            section(
                "Reverse in place",
                "Reversal is the classic linked-list exercise: walk the list once and point each node back at the previous one. Keep three references (previous, current and following) so you never lose the rest of the list.",
                r"""
                def reverse(head):
                    previous = None
                    current = head
                    while current:
                        following = current.next   # save the rest of the list
                        current.next = previous    # flip the pointer
                        previous = current
                        current = following
                    return previous                # the new head
                """,
            ),
        ],
        [
            "Linked lists trade O(1) inserts at the front for O(n) lookups.",
            "Draw the pointers on paper before you code a change.",
            "Always handle the empty list (`head is None`) and the one-node case.",
        ],
        r"""
        class Node:
            def __init__(self, value, next=None):
                self.value = value
                self.next = next


        class LinkedList:
            def __init__(self):
                self.head = None

            def append(self, value):
                new = Node(value)
                if self.head is None:
                    self.head = new
                    return
                node = self.head
                while node.next:
                    node = node.next
                node.next = new

            def delete(self, value) -> bool:
                previous, node = None, self.head
                while node:
                    if node.value == value:
                        if previous is None:
                            self.head = node.next
                        else:
                            previous.next = node.next
                        return True
                    previous, node = node, node.next
                return False

            def reverse(self):
                previous, current = None, self.head
                while current:
                    following = current.next
                    current.next = previous
                    previous = current
                    current = following
                self.head = previous

            def to_list(self):
                values, node = [], self.head
                while node:
                    values.append(node.value)
                    node = node.next
                return values


        def test_linked_list():
            items = LinkedList()
            for value in (1, 2, 3):
                items.append(value)
            assert items.to_list() == [1, 2, 3]
            assert items.delete(2) and items.to_list() == [1, 3]
            assert not items.delete(42)
            items.reverse()
            assert items.to_list() == [3, 1]
        """,
        [
            question("What does reading the k-th item of a singly linked list cost?", ["O(1)", "O(log n)", "O(k)", "O(k²)"], 2,
                     "You have to follow k `next` pointers from the head."),
            question("When reversing, why save `current.next` before changing it?", ["To speed it up", "Otherwise you lose the reference to the rest of the list", "Python requires it", "To free memory"], 1,
                     "Once `current.next` points backwards, the only way to reach the rest of the list is the reference you saved."),
            question("Which operation is O(1) for a singly linked list with only a head pointer?", ["Append at the end", "Insert at the front", "Find the maximum", "Delete the last node"], 1,
                     "A new node can point at the old head and become the head in constant time."),
        ],
    ),
    "dsa-recursion": lesson(
        "A recursive function solves a problem by calling itself on smaller versions of it. Backtracking uses recursion to try choices and undo them.",
        [
            section(
                "Base case and recursive case",
                "Every recursive function needs a base case that stops, and a recursive case that moves toward it. Python limits recursion depth (about 1,000 calls by default), so very deep recursion should become a loop.",
                r"""
                def factorial(n: int) -> int:
                    if n <= 1:                      # base case
                        return 1
                    return n * factorial(n - 1)     # a smaller problem


                def total(items: list[int]) -> int:
                    if not items:
                        return 0
                    return items[0] + total(items[1:])


                print(factorial(5), total([1, 2, 3]))   # 120 6
                """,
            ),
            section(
                "Backtracking: choose, explore, undo",
                "To list every possibility, make a choice, recurse, then undo the choice and try the next one. The recursion explores every path; rejecting invalid choices early (pruning) keeps it fast.",
                r"""
                def subsets(items: list[int]) -> list[list[int]]:
                    result: list[list[int]] = []
                    current: list[int] = []

                    def explore(index: int) -> None:
                        if index == len(items):
                            result.append(current.copy())
                            return
                        current.append(items[index])   # choose
                        explore(index + 1)
                        current.pop()                  # undo
                        explore(index + 1)             # skip this item

                    explore(0)
                    return result


                print(subsets([1, 2]))   # [[1, 2], [1], [2], []]
                """,
            ),
        ],
        [
            "Write the base case first.",
            "Backtracking = choose, explore, undo.",
            "n items have 2ⁿ subsets and n! permutations, so expect exponential time.",
        ],
        r"""
        def permutations(items: list[int]) -> list[list[int]]:
            if len(items) <= 1:
                return [items[:]]
            result = []
            for i, first in enumerate(items):
                rest = items[:i] + items[i + 1:]
                for perm in permutations(rest):
                    result.append([first] + perm)
            return result


        print(len(permutations([1, 2, 3])))   # 6


        def solve_queens(n: int) -> list[list[int]]:
            solutions: list[list[int]] = []
            cols: list[int] = []      # cols[row] = column of the queen in that row

            def safe(col: int) -> bool:
                row = len(cols)
                return all(c != col and abs(c - col) != row - r for r, c in enumerate(cols))

            def place() -> None:
                if len(cols) == n:
                    solutions.append(cols.copy())
                    return
                for col in range(n):
                    if safe(col):
                        cols.append(col)   # choose
                        place()            # explore
                        cols.pop()         # undo

            place()
            return solutions


        print(solve_queens(4))   # [[1, 3, 0, 2], [2, 0, 3, 1]]
        """,
        [
            question("What happens if a recursive function never reaches its base case?", ["It returns None", "Python raises RecursionError", "It loops silently forever", "It returns 0"], 1,
                     "Python stops after roughly 1,000 nested calls with RecursionError."),
            question("How many subsets does a 4-item list have?", ["4", "8", "16", "24"], 2,
                     "Each item is either in or out: 2⁴ = 16."),
            question("In backtracking, why do we `pop()` after the recursive call?", ["To save memory", "To undo the choice before trying the next option", "To end the recursion", "To sort the result"], 1,
                     "Undoing restores the state so the next branch starts from the same place."),
        ],
    ),
    "dsa-binary-search": lesson(
        "Binary search finds a value in sorted data by halving the search range at each step: O(log n) instead of O(n).",
        [
            section(
                "The classic loop",
                "Keep `low` and `high` bounds. Look at the middle item: if it's the target you're done; if it's too small, search the right half; otherwise search the left half. A million sorted items need at most about 20 steps.",
                r"""
                def binary_search(nums: list[int], target: int) -> int:
                    low, high = 0, len(nums) - 1
                    while low <= high:
                        mid = (low + high) // 2
                        if nums[mid] == target:
                            return mid
                        if nums[mid] < target:
                            low = mid + 1
                        else:
                            high = mid - 1
                    return -1


                print(binary_search([2, 5, 8, 12, 16], 12))   # 3
                """,
            ),
            section(
                "Boundaries and the bisect module",
                "Many problems need the first position where a condition becomes true, not just any match. Python's `bisect` module does this: `bisect_left` returns the first index where a value could be inserted while keeping the list sorted, and `bisect_right` the index just after any equal items.",
                r"""
                from bisect import bisect_left, bisect_right

                scores = [10, 20, 20, 20, 30]
                print(bisect_left(scores, 20))    # 1: the first 20
                print(bisect_right(scores, 20))   # 4: just after the last 20
                print(bisect_right(scores, 20) - bisect_left(scores, 20))   # 3 copies
                """,
            ),
        ],
        [
            "Binary search needs sorted data (or a condition that flips only once).",
            "Use `while low <= high` and always move a bound past `mid` to avoid infinite loops.",
            "`bisect` gives you tested boundary searches for free.",
        ],
        r"""
        def first_last(nums: list[int], target: int) -> tuple[int, int]:
            def boundary(find_first: bool) -> int:
                low, high, found = 0, len(nums) - 1, -1
                while low <= high:
                    mid = (low + high) // 2
                    if nums[mid] < target:
                        low = mid + 1
                    elif nums[mid] > target:
                        high = mid - 1
                    else:
                        found = mid
                        if find_first:
                            high = mid - 1     # keep looking left
                        else:
                            low = mid + 1      # keep looking right
                return found

            return boundary(True), boundary(False)


        assert first_last([5, 7, 7, 8, 8, 10], 8) == (3, 4)
        assert first_last([5, 7, 7, 8, 8, 10], 6) == (-1, -1)
        assert first_last([], 1) == (-1, -1)
        assert first_last([4], 4) == (0, 0)
        """,
        [
            question("At most how many comparisons does binary search need on 1,024 sorted items?", ["About 11", "About 32", "About 512", "1,024"], 0,
                     "Each step halves the range: 1,024 → 512 → … → 1 takes 10 halvings, so at most 11 comparisons."),
            question("What does `bisect_left([1, 3, 3, 5], 3)` return?", ["0", "1", "2", "3"], 1,
                     "Index 1 is the first position where 3 could go while keeping the list sorted."),
            question("What happens if you binary-search an unsorted list?", ["It works but slower", "It may return wrong answers", "It sorts the list first", "It raises an error"], 1,
                     "The halving logic assumes order; without it the search can skip over the target."),
        ],
    ),
    "dsa-sorting": lesson(
        "Merge sort and quicksort are the two classic O(n log n) divide-and-conquer sorts. Writing them teaches recursion and trade-offs.",
        [
            section(
                "Merge sort",
                "Split the list in half, sort each half recursively, then merge the two sorted halves. It's always O(n log n) and stable (equal items keep their original order), but it needs O(n) extra memory.",
                r"""
                def merge_sort(items: list[int]) -> list[int]:
                    if len(items) <= 1:
                        return items
                    mid = len(items) // 2
                    left, right = merge_sort(items[:mid]), merge_sort(items[mid:])
                    merged, i, j = [], 0, 0
                    while i < len(left) and j < len(right):
                        if left[i] <= right[j]:       # <= keeps the sort stable
                            merged.append(left[i])
                            i += 1
                        else:
                            merged.append(right[j])
                            j += 1
                    return merged + left[i:] + right[j:]
                """,
            ),
            section(
                "Quicksort",
                "Pick a pivot, split the items into smaller, equal and larger groups, and sort the groups recursively. It averages O(n log n) but degrades to O(n²) when pivots are consistently bad, such as always taking the first item of an already sorted list. A random pivot avoids that.",
                r"""
                import random


                def quick_sort(items: list[int]) -> list[int]:
                    if len(items) <= 1:
                        return items
                    pivot = random.choice(items)
                    smaller = [x for x in items if x < pivot]
                    equal = [x for x in items if x == pivot]
                    larger = [x for x in items if x > pivot]
                    return quick_sort(smaller) + equal + quick_sort(larger)
                """,
            ),
        ],
        [
            "Merge sort guarantees O(n log n); quicksort averages it.",
            "Merge sort is stable; the classic in-place quicksort is not.",
            "In real code use `sorted()` or `list.sort()`: Timsort is stable, O(n log n) and written in C.",
        ],
        r"""
        import random
        import timeit

        # merge_sort and quick_sort as defined in the lesson
        data = [random.randint(0, 1_000_000) for _ in range(10_000)]
        assert merge_sort(data) == quick_sort(data) == sorted(data)

        for fn in (merge_sort, quick_sort, sorted):
            seconds = timeit.timeit(lambda: fn(data), number=5)
            print(f"{fn.__name__:<10} {seconds:.3f}s")

        # Stable: merge_sort and sorted (Timsort).
        # Not stable in general: the classic in-place quicksort.
        """,
        [
            question("What is the worst-case time of quicksort?", ["O(n)", "O(n log n)", "O(n²)", "O(2ⁿ)"], 2,
                     "If every pivot splits off only one item, there are n levels of O(n) work."),
            question("What does it mean for a sort to be stable?", ["It never crashes", "Equal items keep their original relative order", "It uses no extra memory", "It's always O(n log n)"], 1,
                     "Stability matters when you sort by one key after another, such as by name and then by grade."),
            question("Which algorithm does Python's `sorted()` use?", ["Quicksort", "Heap sort", "Timsort, a merge sort and insertion sort hybrid", "Bubble sort"], 2,
                     "Timsort takes advantage of runs that are already sorted, which are common in real data."),
        ],
    ),
    "dsa-hashing": lesson(
        "Hash maps (dict) and sets give O(1) average lookups. Many 'find a matching pair' problems become a single pass with them.",
        [
            section(
                "Remember what you've seen",
                "Instead of comparing every pair, store what you've seen in a dict and ask, for each new item, whether its partner is already there. That turns O(n²) into O(n).",
                r"""
                def two_sum(nums: list[int], target: int) -> tuple[int, int] | None:
                    seen: dict[int, int] = {}          # value -> index
                    for i, num in enumerate(nums):
                        partner = target - num
                        if partner in seen:
                            return seen[partner], i
                        seen[num] = i
                    return None


                print(two_sum([2, 7, 11, 15], 9))   # (0, 1)
                """,
            ),
            section(
                "Counting and grouping",
                "`collections.Counter` counts items and `defaultdict(list)` groups them under a computed key. Keys must be hashable: strings, numbers and tuples work, lists don't.",
                r"""
                from collections import Counter, defaultdict

                print(Counter("banana").most_common(1))   # [('a', 3)]

                groups = defaultdict(list)
                for word in ["eat", "tea", "tan", "ate", "nat"]:
                    groups["".join(sorted(word))].append(word)
                print(list(groups.values()))   # [['eat', 'tea', 'ate'], ['tan', 'nat']]
                """,
            ),
        ],
        [
            "Store what you've seen in a dict to avoid nested loops.",
            "`Counter` counts; `defaultdict` groups.",
            "Dict keys must be hashable, so convert lists to tuples or strings.",
        ],
        r"""
        from collections import Counter, defaultdict


        def two_sum(nums, target):
            seen = {}
            for i, num in enumerate(nums):
                if target - num in seen:
                    return seen[target - num], i
                seen[num] = i
            return None


        def group_anagrams(words):
            groups = defaultdict(list)
            for word in words:
                groups["".join(sorted(word))].append(word)
            return list(groups.values())


        def first_unique_char(text):
            counts = Counter(text)
            for i, char in enumerate(text):
                if counts[char] == 1:
                    return i
            return -1


        assert two_sum([3, 2, 4], 6) == (1, 2)
        assert group_anagrams(["eat", "tea", "tan"]) == [["eat", "tea"], ["tan"]]
        assert first_unique_char("leetcode") == 0
        assert first_unique_char("aabb") == -1
        """,
        [
            question("Why can't a list be a dict key?", ["Lists are too big", "Lists are mutable, so they aren't hashable", "Keys must be strings", "It is allowed"], 1,
                     "A key's hash must never change; a list could change after being stored. Use a tuple instead."),
            question("What is the time complexity of the dict-based two-sum?", ["O(1)", "O(n)", "O(n log n)", "O(n²)"], 1,
                     "One pass over the list, with O(1) dict lookups at each step."),
            question("What is `Counter('hello')['l']`?", ["1", "2", "3", "A KeyError"], 1,
                     "'hello' contains two l's. (Counter also returns 0 instead of raising for missing keys.)"),
        ],
    ),
    "dsa-trees": lesson(
        "Trees model hierarchies. A binary search tree keeps smaller values on the left and larger ones on the right, so a search follows a single path from the root.",
        [
            section(
                "Binary search trees",
                "Each node has at most two children. In a BST, everything in a node's left subtree is smaller and everything in its right subtree is larger. Search and insert cost O(h), where h is the tree's height: O(log n) when balanced, but O(n) if values arrive already sorted.",
                r"""
                class TreeNode:
                    def __init__(self, value):
                        self.value = value
                        self.left = None
                        self.right = None


                def insert(root, value):
                    if root is None:
                        return TreeNode(value)
                    if value < root.value:
                        root.left = insert(root.left, value)
                    else:
                        root.right = insert(root.right, value)
                    return root


                def contains(root, value) -> bool:
                    while root:
                        if value == root.value:
                            return True
                        root = root.left if value < root.value else root.right
                    return False
                """,
            ),
            section(
                "Depth-first and breadth-first traversal",
                "Depth-first traversals recurse: pre-order (node, left, right), in-order (left, node, right), which gives a BST's values in sorted order, and post-order (left, right, node). Breadth-first, or level-order, traversal uses a queue to visit the tree level by level.",
                r"""
                from collections import deque


                def in_order(node, out):
                    if node:
                        in_order(node.left, out)
                        out.append(node.value)
                        in_order(node.right, out)
                    return out


                def level_order(root):
                    levels, queue = [], deque([root] if root else [])
                    while queue:
                        level = []
                        for _ in range(len(queue)):
                            node = queue.popleft()
                            level.append(node.value)
                            queue.extend(child for child in (node.left, node.right) if child)
                        levels.append(level)
                    return levels
                """,
            ),
        ],
        [
            "BST rule: left < node < right.",
            "In-order traversal of a BST returns its values sorted.",
            "Use a queue for level-order (BFS) and recursion or a stack for depth-first.",
        ],
        r"""
        # Uses TreeNode, insert, contains, in_order and level_order from the lesson.
        root = None
        for value in [8, 3, 10, 1, 6, 14, 4]:
            root = insert(root, value)


        def pre_order(node, out):
            if node:
                out.append(node.value)
                pre_order(node.left, out)
                pre_order(node.right, out)
            return out


        def height(node) -> int:
            return 0 if node is None else 1 + max(height(node.left), height(node.right))


        assert contains(root, 6) and not contains(root, 7)
        assert in_order(root, []) == [1, 3, 4, 6, 8, 10, 14]
        assert pre_order(root, []) == [8, 3, 1, 6, 4, 10, 14]
        assert level_order(root) == [[8], [3, 10], [1, 6, 14], [4]]
        assert height(root) == 4
        """,
        [
            question("In-order traversal of a BST visits values in…", ["Insertion order", "Sorted order", "Reverse order", "Random order"], 1,
                     "Left subtree (smaller), then the node, then the right subtree (larger) produces ascending order."),
            question("You insert 1, 2, 3, 4, 5 into an empty BST, in that order. What does a search cost now?", ["O(1)", "O(log n)", "O(n): the tree is a straight line", "O(n²)"], 2,
                     "Each value goes to the right of the previous one, so the 'tree' is a linked list. Balanced trees (such as AVL or red-black trees) prevent this."),
            question("Which traversal uses a queue?", ["Pre-order", "In-order", "Post-order", "Level-order"], 3,
                     "Level-order is breadth-first search on a tree."),
        ],
    ),
    "dsa-heaps": lesson(
        "A heap always gives you its smallest item in O(1) and adds or removes items in O(log n). It's the tool for priority queues and 'top k' problems.",
        [
            section(
                "heapq basics",
                "Python's `heapq` module keeps a list arranged as a min-heap: `heap[0]` is always the smallest item. `heappush` and `heappop` are O(log n), and `heapify` turns a list into a heap in O(n). Push `(priority, item)` tuples to order items by priority. For a max-heap of numbers, push negated values (Python 3.14 also adds `heappush_max` and `heappop_max`).",
                r"""
                import heapq

                tasks = []
                heapq.heappush(tasks, (2, "write tests"))
                heapq.heappush(tasks, (1, "fix bug"))
                heapq.heappush(tasks, (3, "update docs"))
                while tasks:
                    priority, name = heapq.heappop(tasks)
                    print(priority, name)      # 1 fix bug, 2 write tests, 3 update docs
                """,
            ),
            section(
                "Top k with a bounded heap",
                "To keep the k largest items from a stream, hold a min-heap of size k. A new item replaces the smallest one only if it's bigger. That's O(n log k) time and O(k) memory, which is far better than sorting everything when k is small.",
                r"""
                import heapq


                def k_largest(stream, k: int) -> list[int]:
                    heap: list[int] = []
                    for value in stream:
                        if len(heap) < k:
                            heapq.heappush(heap, value)
                        elif value > heap[0]:
                            heapq.heapreplace(heap, value)   # pop the smallest, push value
                    return sorted(heap, reverse=True)


                print(k_largest([5, 1, 9, 3, 7, 8], 3))   # [9, 8, 7]
                """,
            ),
        ],
        [
            "`heap[0]` is the minimum; push and pop cost O(log n).",
            "Store `(priority, item)` tuples to order items by priority.",
            "For the k largest items, keep a min-heap of size k.",
        ],
        r"""
        import heapq


        def merge_sorted(lists: list[list[int]]) -> list[int]:
            heap = [(items[0], i, 0) for i, items in enumerate(lists) if items]
            heapq.heapify(heap)
            merged = []
            while heap:
                value, list_index, item_index = heapq.heappop(heap)
                merged.append(value)
                if item_index + 1 < len(lists[list_index]):
                    next_value = lists[list_index][item_index + 1]
                    heapq.heappush(heap, (next_value, list_index, item_index + 1))
            return merged


        assert merge_sorted([[1, 4, 7], [2, 5], [0, 9]]) == [0, 1, 2, 4, 5, 7, 9]
        assert merge_sorted([[], [3]]) == [3]
        # k_largest from the lesson solves the first part of the exercise.
        # The standard library also offers heapq.merge(*lists) and heapq.nlargest(k, items).
        """,
        [
            question("In a heapq min-heap `h`, where is the smallest item?", ["h[-1]", "h[0]", "h[len(h) // 2]", "It varies"], 1,
                     "heapq maintains the invariant that `h[0]` is the smallest element."),
            question("Which approach turns heapq's min-heap into a max-heap for numbers?", ["Push negated values, and negate them again when you pop", "Push values in descending order", "Read heap[-1] instead of heap[0]", "Call heapify twice"], 0,
                     "Negating flips the order, so the largest number becomes the smallest. Python 3.14 also adds dedicated max-heap functions."),
            question("How long does finding the 10 largest of n numbers with a size-10 heap take?", ["O(n log 10), effectively O(n)", "O(n²)", "Always O(n log n)", "O(1)"], 0,
                     "Each of the n items costs at most O(log k) with k = 10, a constant."),
        ],
    ),
    "dsa-graph-traversal": lesson(
        "Graphs model networks such as roads, links and dependencies. Store them as adjacency lists and explore them with breadth-first search (BFS) or depth-first search (DFS).",
        [
            section(
                "Adjacency lists, DFS and BFS",
                "An adjacency list maps each node to its neighbours. DFS goes as deep as possible first, using recursion or a stack. BFS explores level by level with a queue, so in an unweighted graph it finds the path with the fewest edges. Track visited nodes to avoid loops. Both run in O(V + E) for V nodes and E edges.",
                r"""
                from collections import deque

                graph = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}


                def dfs(node, visited=None):
                    visited = visited if visited is not None else set()
                    visited.add(node)
                    for neighbour in graph[node]:
                        if neighbour not in visited:
                            dfs(neighbour, visited)
                    return visited


                def bfs_distance(start, goal):
                    queue, seen = deque([(start, 0)]), {start}
                    while queue:
                        node, distance = queue.popleft()
                        if node == goal:
                            return distance
                        for neighbour in graph[node]:
                            if neighbour not in seen:
                                seen.add(neighbour)
                                queue.append((neighbour, distance + 1))
                    return -1


                print(sorted(dfs("A")), bfs_distance("A", "D"))   # ['A', 'B', 'C', 'D'] 2
                """,
            ),
            section(
                "Grids are graphs too",
                "In a grid, each cell is a node and its neighbours are the cells above, below, left and right. Check the bounds before stepping, and mark cells as visited.",
                r"""
                DIRECTIONS = [(1, 0), (-1, 0), (0, 1), (0, -1)]


                def neighbours(grid, row, col):
                    for dr, dc in DIRECTIONS:
                        r, c = row + dr, col + dc
                        if 0 <= r < len(grid) and 0 <= c < len(grid[0]):
                            yield r, c
                """,
            ),
        ],
        [
            "Adjacency list: a dict mapping each node to a list of neighbours.",
            "BFS (queue) finds fewest-edge paths in unweighted graphs; DFS (stack or recursion) explores fully.",
            "Always track visited nodes; traversal is O(V + E).",
        ],
        r"""
        from collections import deque


        def count_islands(grid: list[list[str]]) -> int:
            rows, cols = len(grid), len(grid[0]) if grid else 0
            seen = set()

            def sink(r: int, c: int) -> None:
                stack = [(r, c)]
                while stack:
                    r, c = stack.pop()
                    if (r, c) in seen or not (0 <= r < rows and 0 <= c < cols) or grid[r][c] != "1":
                        continue
                    seen.add((r, c))
                    stack.extend([(r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)])

            islands = 0
            for r in range(rows):
                for c in range(cols):
                    if grid[r][c] == "1" and (r, c) not in seen:
                        islands += 1
                        sink(r, c)
            return islands


        def maze_steps(maze: list[str]) -> int:
            rows, cols = len(maze), len(maze[0])
            queue, seen = deque([(0, 0, 0)]), {(0, 0)}
            while queue:
                r, c, steps = queue.popleft()
                if (r, c) == (rows - 1, cols - 1):
                    return steps
                for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                    if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] == "." and (nr, nc) not in seen:
                        seen.add((nr, nc))
                        queue.append((nr, nc, steps + 1))
            return -1


        assert count_islands([list("110"), list("010"), list("001")]) == 2
        assert maze_steps(["..#", "#..", "#.."]) == 4
        """,
        [
            question("Which traversal finds the path with the fewest edges in an unweighted graph?", ["DFS", "BFS", "Either, always", "Neither"], 1,
                     "BFS reaches every node at distance d before any node at distance d + 1."),
            question("Why track visited nodes?", ["To sort the output", "To avoid revisiting nodes and looping forever on cycles", "Python requires it", "To use the CPU cache"], 1,
                     "Without a visited set, a cycle such as A → B → A would be followed forever."),
            question("What is the time complexity of BFS on a graph with V nodes and E edges?", ["O(V)", "O(E²)", "O(V + E)", "O(V·E)"], 2,
                     "Each node is dequeued once and each edge is examined once."),
        ],
    ),
    "dsa-shortest-paths": lesson(
        "When edges have weights (distances, times, costs), BFS isn't enough. Dijkstra's algorithm finds shortest paths using a priority queue.",
        [
            section(
                "How Dijkstra's algorithm works",
                "Keep the best known distance to each node. Repeatedly take the closest unfinished node from a min-heap, then try to improve its neighbours' distances by going through it. With heapq it runs in O((V + E) log V). All edge weights must be non-negative.",
                r"""
                import heapq


                def dijkstra(graph: dict[str, list[tuple[str, int]]], start: str) -> dict[str, int]:
                    distances = {start: 0}
                    heap = [(0, start)]
                    while heap:
                        distance, node = heapq.heappop(heap)
                        if distance > distances.get(node, float("inf")):
                            continue                          # a stale heap entry
                        for neighbour, weight in graph[node]:
                            candidate = distance + weight
                            if candidate < distances.get(neighbour, float("inf")):
                                distances[neighbour] = candidate
                                heapq.heappush(heap, (candidate, neighbour))
                    return distances
                """,
            ),
            section(
                "Rebuild the route",
                "To return the route itself, record each node's predecessor whenever you improve its distance, then walk backwards from the destination.",
                r"""
                def path_to(previous: dict[str, str], goal: str) -> list[str]:
                    path = [goal]
                    while path[-1] in previous:
                        path.append(previous[path[-1]])
                    return path[::-1]
                """,
            ),
        ],
        [
            "Dijkstra = BFS with a min-heap ordered by distance.",
            "Skip stale heap entries instead of trying to delete them.",
            "Negative edge weights break Dijkstra; use Bellman-Ford for those.",
        ],
        r"""
        import heapq

        ROADS = {
            "Delhi": [("Agra", 3), ("Jaipur", 5)],
            "Agra": [("Jaipur", 4), ("Gwalior", 2)],
            "Jaipur": [("Udaipur", 6)],
            "Gwalior": [("Udaipur", 9)],
            "Udaipur": [],
        }


        def fastest_route(graph, start, goal):
            distances, previous = {start: 0}, {}
            heap = [(0, start)]
            while heap:
                distance, city = heapq.heappop(heap)
                if city == goal:
                    break
                if distance > distances[city]:
                    continue
                for neighbour, hours in graph[city]:
                    candidate = distance + hours
                    if candidate < distances.get(neighbour, float("inf")):
                        distances[neighbour] = candidate
                        previous[neighbour] = city
                        heapq.heappush(heap, (candidate, neighbour))
            if goal not in distances:
                return None
            path = [goal]
            while path[-1] != start:
                path.append(previous[path[-1]])
            return distances[goal], path[::-1]


        print(fastest_route(ROADS, "Delhi", "Udaipur"))   # (11, ['Delhi', 'Jaipur', 'Udaipur'])
        """,
        [
            question("Why does Dijkstra's algorithm fail with negative edge weights?", ["heapq can't store negative numbers", "A node treated as final could later get a shorter path through a negative edge", "It always loops forever", "It doesn't fail"], 1,
                     "Dijkstra assumes a path can only get longer as you add edges, which negative weights break."),
            question("Which data structure chooses the next node in Dijkstra's algorithm?", ["A stack", "A FIFO queue", "A min-heap (priority queue)", "A set"], 2,
                     "The heap always yields the unfinished node with the smallest known distance."),
            question("What should you do with a popped heap entry whose distance is larger than the best known distance?", ["Return immediately", "Skip it, because it's stale", "Push it again", "Reset all distances"], 1,
                     "A better distance was found after this entry was pushed, so the entry is out of date."),
        ],
    ),
    "dsa-topo-union-find": lesson(
        "Topological sort orders tasks so each one comes after its prerequisites. Union-find tracks which items are connected. Both are staples of interviews and real systems.",
        [
            section(
                "Topological sort (Kahn's algorithm)",
                "Count each node's incoming edges (its in-degree). Start with the nodes that have none, remove them, and reduce their neighbours' counts; any node that reaches zero is ready. If some nodes never reach zero, the graph has a cycle and no valid order exists.",
                r"""
                from collections import deque


                def topo_order(graph: dict) -> list | None:
                    indegree = {node: 0 for node in graph}
                    for node in graph:
                        for nxt in graph[node]:
                            indegree[nxt] += 1
                    ready = deque(node for node, d in indegree.items() if d == 0)
                    order = []
                    while ready:
                        node = ready.popleft()
                        order.append(node)
                        for nxt in graph[node]:
                            indegree[nxt] -= 1
                            if indegree[nxt] == 0:
                                ready.append(nxt)
                    return order if len(order) == len(graph) else None   # None: a cycle


                print(topo_order({"python": ["fastapi", "dsa"], "dsa": [], "fastapi": ["docker"], "docker": []}))
                # ['python', 'fastapi', 'dsa', 'docker']
                """,
            ),
            section(
                "Union-find (disjoint sets)",
                "Union-find keeps groups of connected items. `find` returns a group's representative and `union` merges two groups. With path compression and union by size, each operation is nearly O(1). If `union` finds both items already in the same group, adding that edge would create a cycle.",
                r"""
                class UnionFind:
                    def __init__(self, n: int):
                        self.parent = list(range(n))
                        self.size = [1] * n

                    def find(self, x: int) -> int:
                        while self.parent[x] != x:
                            self.parent[x] = self.parent[self.parent[x]]   # path compression
                            x = self.parent[x]
                        return x

                    def union(self, a: int, b: int) -> bool:
                        ra, rb = self.find(a), self.find(b)
                        if ra == rb:
                            return False                  # already connected
                        if self.size[ra] < self.size[rb]:
                            ra, rb = rb, ra
                        self.parent[rb] = ra
                        self.size[ra] += self.size[rb]
                        return True
                """,
            ),
        ],
        [
            "A topological order exists only when the graph has no cycles (a DAG).",
            "Kahn's algorithm repeatedly takes the nodes whose in-degree is 0.",
            "Union-find answers 'are these connected?' in near O(1).",
        ],
        r"""
        def can_finish(num_courses: int, prerequisites: list[tuple[int, int]]) -> bool:
            graph = {course: [] for course in range(num_courses)}
            for course, needs in prerequisites:
                graph[needs].append(course)
            return topo_order(graph) is not None      # topo_order from the lesson


        def has_cycle(n: int, edges: list[tuple[int, int]]) -> bool:
            # For an undirected graph; UnionFind from the lesson
            groups = UnionFind(n)
            return any(not groups.union(a, b) for a, b in edges)


        assert can_finish(2, [(1, 0)])
        assert not can_finish(2, [(1, 0), (0, 1)])
        assert not has_cycle(3, [(0, 1), (1, 2)])
        assert has_cycle(3, [(0, 1), (1, 2), (2, 0)])
        """,
        [
            question("Kahn's algorithm finishes, but its order is shorter than the number of nodes. What does that mean?", ["The graph is disconnected", "The graph has a cycle", "It sorted in descending order", "Nothing; that's normal"], 1,
                     "Nodes on a cycle always keep an incoming edge, so they never become ready."),
            question("In union-find, `union(a, b)` returns False when…", ["a and b are equal numbers", "a and b were already in the same group", "the structure is full", "b is larger than a"], 1,
                     "If both have the same representative, they're already connected."),
            question("Which problem suits topological sort?", ["The shortest weighted route", "Ordering build steps that depend on each other", "Finding duplicates", "Sorting numbers"], 1,
                     "Dependencies form a directed graph, and a topological order respects every dependency."),
        ],
    ),
    "dsa-dynamic-programming": lesson(
        "Dynamic programming (DP) solves problems whose subproblems overlap by solving each subproblem once and reusing the answer.",
        [
            section(
                "Memoization: top-down",
                "Write the natural recursive solution, then cache results so each subproblem is computed only once. `functools.cache` does the caching for you. Naive Fibonacci is O(2ⁿ); memoized, it's O(n).",
                r"""
                from functools import cache


                @cache
                def fib(n: int) -> int:
                    return n if n < 2 else fib(n - 1) + fib(n - 2)


                print(fib(80))   # 23416728348467685, instantly
                """,
            ),
            section(
                "Tabulation: bottom-up",
                "Fill a table from the smallest subproblems upward. This avoids recursion limits, and often you only need the last row or two. The recipe: define exactly what `dp[i]` means, write the recurrence, set the base cases, then choose the fill order.",
                r"""
                def climb_stairs(n: int) -> int:
                    # dp[i] = number of ways to reach step i taking 1 or 2 steps at a time
                    dp = [0] * (n + 1)
                    dp[0] = 1
                    for i in range(1, n + 1):
                        dp[i] = dp[i - 1] + (dp[i - 2] if i >= 2 else 0)
                    return dp[n]


                print(climb_stairs(5))   # 8
                """,
            ),
        ],
        [
            "DP fits when subproblems overlap and the best answer is built from the best sub-answers.",
            "Top-down = recursion plus a cache; bottom-up = filling a table.",
            "Start by writing down exactly what `dp[i]` (or `dp[i][j]`) means.",
        ],
        r"""
        from functools import cache


        def coin_change(coins: list[int], amount: int) -> int:
            @cache
            def fewest(remaining: int) -> float:
                if remaining == 0:
                    return 0
                if remaining < 0:
                    return float("inf")
                return 1 + min(fewest(remaining - coin) for coin in coins)

            answer = fewest(amount)
            return -1 if answer == float("inf") else int(answer)


        def coin_change_table(coins: list[int], amount: int) -> int:
            dp = [0] + [float("inf")] * amount      # dp[a] = fewest coins that make amount a
            for a in range(1, amount + 1):
                for coin in coins:
                    if coin <= a:
                        dp[a] = min(dp[a], dp[a - coin] + 1)
            return -1 if dp[amount] == float("inf") else int(dp[amount])


        def lcs(a: str, b: str) -> int:
            dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
            for i in range(1, len(a) + 1):
                for j in range(1, len(b) + 1):
                    if a[i - 1] == b[j - 1]:
                        dp[i][j] = dp[i - 1][j - 1] + 1
                    else:
                        dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
            return dp[-1][-1]


        assert coin_change([1, 2, 5], 11) == coin_change_table([1, 2, 5], 11) == 3
        assert coin_change([2], 3) == coin_change_table([2], 3) == -1
        assert lcs("abcde", "ace") == 3
        """,
        [
            question("Which two properties make a problem a good fit for DP?", ["Sorted input and small n", "Overlapping subproblems and optimal substructure", "Recursion and loops", "Graphs and weights"], 1,
                     "Overlap means caching pays off; optimal substructure means best answers combine into a best answer."),
            question("What does `@functools.cache` do?", ["Runs the function in parallel", "Stores results by argument, so repeated calls return instantly", "Raises the recursion limit", "Compiles the function"], 1,
                     "It memoizes the function: each distinct argument is computed once."),
            question("What is the time complexity of the table-based coin change for amount A and C coin types?", ["O(A)", "O(A·C)", "O(2^A)", "O(C log A)"], 1,
                     "For each of the A amounts, it tries each of the C coins."),
        ],
    ),
    "dsa-greedy": lesson(
        "A greedy algorithm makes the best-looking choice at each step and never revisits it. When it works it's simple and fast, but you need to be able to argue why it works.",
        [
            section(
                "Interval scheduling",
                "To fit the most non-overlapping meetings into one room, always pick the meeting that ends earliest. Finishing early leaves the most room for everything else, and an 'exchange argument' proves this is optimal. Sorting dominates the cost: O(n log n).",
                r"""
                def max_meetings(meetings: list[tuple[int, int]]) -> list[tuple[int, int]]:
                    chosen, last_end = [], float("-inf")
                    for start, end in sorted(meetings, key=lambda m: m[1]):   # by end time
                        if start >= last_end:
                            chosen.append((start, end))
                            last_end = end
                    return chosen


                print(max_meetings([(1, 4), (3, 5), (0, 6), (5, 7), (8, 9)]))
                # [(1, 4), (5, 7), (8, 9)]
                """,
            ),
            section(
                "When greedy fails",
                "Greedy isn't always right. To make 6 from coins [1, 3, 4], greedy takes 4 + 1 + 1 (three coins), but 3 + 3 uses only two. When a quick counterexample exists, switch to dynamic programming.",
                r"""
                def greedy_change(coins: list[int], amount: int) -> list[int]:
                    used = []
                    for coin in sorted(coins, reverse=True):
                        while amount >= coin:
                            amount -= coin
                            used.append(coin)
                    return used


                print(greedy_change([1, 3, 4], 6))   # [4, 1, 1]: not optimal, 3 + 3 is better
                """,
            ),
        ],
        [
            "Greedy = commit to the locally best choice and never backtrack.",
            "Prove it (for example with an exchange argument) or look for a counterexample before trusting it.",
            "Many interval problems become easy after sorting by start or end time.",
        ],
        r"""
        def merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
            merged: list[list[int]] = []
            for start, end in sorted(intervals):
                if merged and start <= merged[-1][1]:
                    merged[-1][1] = max(merged[-1][1], end)   # overlaps: extend it
                else:
                    merged.append([start, end])
            return [(start, end) for start, end in merged]


        assert merge_intervals([(1, 3), (2, 6), (8, 10), (15, 18)]) == [(1, 6), (8, 10), (15, 18)]
        assert merge_intervals([(1, 4), (4, 5)]) == [(1, 5)]

        # Why earliest-end-first works for max_meetings: if an optimal schedule starts
        # with a meeting that ends later, swapping in the earliest-ending meeting never
        # causes a clash and keeps the same count, so greedy is never worse.
        """,
        [
            question("To fit the most non-overlapping meetings, sort them by…", ["Start time", "End time", "Duration, longest first", "Room name"], 1,
                     "Picking the earliest finish leaves the most time for the remaining meetings."),
            question("How many coins does greedy use to make 6 from coins [1, 3, 4]?", ["2", "3", "4", "6"], 1,
                     "Greedy takes 4 + 1 + 1 = 3 coins, while the optimal answer, 3 + 3, uses 2."),
            question("What is the usual time complexity of a sort-then-scan greedy algorithm?", ["O(n)", "O(n log n)", "O(n²)", "O(2ⁿ)"], 1,
                     "Sorting costs O(n log n) and the scan is O(n)."),
        ],
    ),
    "dsa-tries-practice": lesson(
        "A trie stores strings character by character, so finding every word with a given prefix is fast. Then you'll put the whole course together with timed practice.",
        [
            section(
                "Build a trie",
                "Each node holds a dict of child characters and a flag that marks the end of a word. Inserting or looking up a word of length m takes O(m), no matter how many words are stored.",
                r"""
                class Trie:
                    def __init__(self):
                        self.children: dict[str, "Trie"] = {}
                        self.is_word = False

                    def insert(self, word: str) -> None:
                        node = self
                        for char in word:
                            node = node.children.setdefault(char, Trie())
                        node.is_word = True

                    def find(self, prefix: str) -> "Trie | None":
                        node = self
                        for char in prefix:
                            node = node.children.get(char)
                            if node is None:
                                return None
                        return node
                """,
            ),
            section(
                "A problem-solving routine",
                "In timed practice, follow the same steps every time:\n\n"
                "1. Restate the problem and work through an example by hand.\n\n"
                "2. Note the input size; it hints at the complexity you need. For n = 10⁵, aim for O(n log n) or better.\n\n"
                "3. Write down the brute-force idea, then look for a pattern: two pointers, hashing, BFS/DFS, a heap, binary search or DP.\n\n"
                "4. Code it, then test the edge cases: empty input, one item, duplicates, negatives.\n\n"
                "5. State the time and space complexity.",
            ),
        ],
        [
            "Trie operations cost O(length of the word), however many words are stored.",
            "The input size hints at the complexity you need.",
            "Always finish by testing edge cases and stating the complexity.",
        ],
        r"""
        class Trie:
            def __init__(self):
                self.children: dict[str, "Trie"] = {}
                self.is_word = False

            def insert(self, word: str) -> None:
                node = self
                for char in word:
                    node = node.children.setdefault(char, Trie())
                node.is_word = True

            def complete(self, prefix: str, limit: int = 5) -> list[str]:
                node = self
                for char in prefix:
                    node = node.children.get(char)
                    if node is None:
                        return []
                results: list[str] = []

                def collect(current: "Trie", word: str) -> None:
                    if len(results) >= limit:
                        return
                    if current.is_word:
                        results.append(word)
                    for char in sorted(current.children):
                        collect(current.children[char], word + char)

                collect(node, prefix)
                return results


        words = Trie()
        for w in ["python", "pytest", "pydantic", "pandas", "docker"]:
            words.insert(w)
        assert words.complete("py") == ["pydantic", "pytest", "python"]
        assert words.complete("x") == []

        # Timed set (60 minutes): 1) valid anagram (hashing), 2) k closest points
        # to the origin (heap), 3) number of ways to decode "226" (DP).
        # Write down each solution's time and space complexity.
        """,
        [
            question("What does checking for a word of length m in a trie of n words cost?", ["O(n)", "O(m)", "O(n·m)", "O(log n)"], 1,
                     "You follow one child link per character, independent of how many words are stored."),
            question("n can be up to 100,000. Which complexity should you aim for?", ["O(n²) is fine", "O(n log n) or better", "O(2ⁿ)", "O(n³)"], 1,
                     "n² would be 10¹⁰ steps, far too slow; n log n is about 1.7 million."),
            question("Your solution passes the first example. What should you do next?", ["Submit immediately", "Test edge cases such as empty input, one item and duplicates", "Rewrite it in another language", "Remove the comments"], 1,
                     "Most wrong answers come from edge cases that the first example doesn't cover."),
        ],
    ),
}
