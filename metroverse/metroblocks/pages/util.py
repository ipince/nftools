def highlight_if(condition):
    HIGHLIGHT_COLOR = "darkseagreen"
    if condition:
        return f"style='background: {HIGHLIGHT_COLOR}'"
    return ""


def fmt_score(score):
    return "{:.0f}".format(score)


def opensea_profile(address):
    return f"https://opensea.io/{address}"


def opensea(block):
    return f"https://opensea.io/assets/0x0e9d6552b85be180d941f1ca73ae3e318d2d4f1f/{block['num']}"
