Detect a sequences of similar structures in html and contruct xpath for them.

Ex: products, forms, polls on a webpage.

Each detected sequence:

1. has not less than min_elements
2. has not less than mintreeheight
3. everything started from maxtreeheight is unimportant
4. similarity should be less than maxmismatch

This is quick prototype. Worked. A lot of improvements may be here.
