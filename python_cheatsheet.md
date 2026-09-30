# Python Cheat Sheet: Plain English

Use this while **learning**. Don't use it during the **graduation rewrite**, because that one tests memory.

## Builtin functions

| Code | In plain English |
|---|---|
| `print(x)` | "Show x on the screen." |
| `input("...")` | "Ask the player something and give back what they typed, as text." |
| `int(x)` | "Turn x into a whole number." (Crashes on `"abc"`.) |
| `len(x)` | "How many items are in x?" |
| `range(n)` | "Count from 0 up to, but not including, n." |
| `range(a, b)` | "Count from a up to, but not including, b." |
| `list(x)` | "Turn x into a real list." |
| `enumerate(x, start=1)` | "Go through x, and number each item as you go." |

## Text and dictionary methods

| Code | In plain English |
|---|---|
| `text.strip()` | "Cut off spaces at the start and end." |
| `text.lower()` | "Make it all lowercase." |
| `d.items()` | "Give me every key and value in the dictionary, in pairs." |
| `d[key]` | "Look up the value for this key." |
| `nums[i]` | "Give me the item at position i." (Positions start at 0.) |

## Keywords

| Code | In plain English |
|---|---|
| `def name(a, b):` | "Here's a recipe called name. It needs a and b." |
| `return x` | "Hand x back to whoever called me, and stop." |
| `for x in y:` | "Do this once for every item in y." |
| `while True:` | "Keep doing this forever, until something stops it." |
| `if / elif / else` | "If this, do that; otherwise, if this, ...; otherwise ..." |
| `x in y` | "Is x inside y?" |
| `try: / except ValueError:` | "Try this, and if it fails with a ValueError, do this instead of crashing." |
| `==` vs `=` | "Are these equal?" vs. "Store this value." |
| `import random` | "Load Python's random tools." |
| `random.sample(x, k=n)` | "Pick n random items from x, with no repeats." |

## Going from English to Python (pseudocode)

Before writing code, write the steps as comments. Then translate **one comment at a time** into one line of Python, using the tables above.

```python
# for every position in the list
# pair it with every position after it
# if the two numbers add up to the target
# give back both positions
```

becomes:

```python
for i in range(len(nums)):
    for j in range(i + 1, len(nums)):
        if nums[i] + nums[j] == target:
            return [i, j]
```
