from difflib import SequenceMatcher
import html

def _tokenize(text: str):
    """Split text into word+space tokens for readable diffs."""
    import re
    return re.findall(r'\S+|\s+', text)

def highlight_diff(text_a: str, text_b: str) -> dict:
    tokens_a = _tokenize(text_a)
    tokens_b = _tokenize(text_b)
    seq = SequenceMatcher(None, tokens_a, tokens_b, autojunk=False)
    a_html: list = []
    b_html: list = []
    replace_counter = 0
    # circled numbers ①②③... up to 20, then fall back to plain numbers
    def _num(n):
        circles = ""
        return circles[n - 1] if n <= len(circles) else f"({n})"

    for tag, i1, i2, j1, j2 in seq.get_opcodes():
        chunk_a = html.escape("".join(tokens_a[i1:i2]))
        chunk_b = html.escape("".join(tokens_b[j1:j2]))
        if tag == "equal":
            a_html.append(f'<span class="diff-equal">{chunk_a}</span>')
            b_html.append(f'<span class="diff-equal">{chunk_b}</span>')
        elif tag == "replace":
            replace_counter += 1
            num = _num(replace_counter)
            a_html.append(
                f'<span class="diff-replace diff-replace-del">'
                f'{chunk_a}<sup >{num}</sup>'
                f'</span>'
            )
            b_html.append(
                f'<span class="diff-replace diff-replace-ins">'
                f'{chunk_b}<sup >{num}</sup>'
                f'</span>'
            )
        elif tag == "delete":
            a_html.append(f'<span class="diff-del">{chunk_a}</span>')
        elif tag == "insert":
            b_html.append(f'<span class="diff-ins">{chunk_b}</span>')
    return {"a_html": "".join(a_html), "b_html": "".join(b_html)}
