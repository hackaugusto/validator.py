Validator.py
------------

Validator is a simple way to validate your objects, the intent is to validate
the values, not to convert them.

```python
>>> String.digit('5')
True
```

Validator can be chained togheter, if different values are accepted use a OR:

```python
>>> (Number.even | Number.prime)(5)
True
```

If more than one option is required use a AND:

```python
>>> (Number.between(2, 7) & Number.positive)(5)
True
```

Chaining validator does a implicit AND:

```python
>>> Number.between(2, 7).positive(5)
True
>>> Number.even.prime(2)
True
>>> Number.even.prime(5)
False
```

Validators are callables that accept one argument

```python
>>> list(filter(Number.prime, range(1, 100)))
[2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
>>> list(filter(Number.perfect_square, range(1, 100)))
[1, 4, 9, 16, 25, 36, 49, 64, 81]
>>> list(filter(Number.prime | Number.perfect_square, range(1, 100)))
[1, 2, 3, 4, 5, 7, 9, 11, 13, 16, 17, 19, 23, 25, 29, 31, 36, 37, 41, 43, 47, 49, 53, 59, 61, 64, 67, 71, 73, 79, 81, 83, 89, 97]
```
