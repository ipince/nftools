
def printb(block):
    print(bstr(block))


def bstr(block):
    strs = []
    types = ['res', 'com', 'ind']
    for t in types:
        bldg_strs = []
        bldgs = list(block['buildings'][t].values())
        bldgs = sorted(bldgs, key=lambda b: b['weight'])
        for build in bldgs:
            s = f"    {build['name']} (score {build['score']}, weight {build['weight']}) "
            if build['weight'] <= 40:
                s += "*"

            if 'boost_name' in build:
                s += f" <b>[{build['boost_name']} - {build['pct']}%]</b>"
            bldg_strs.append(s+"\n")
        strs.append(bldg_strs)

    pubs = []
    for pub in block['buildings']['pub'].values():
        s = f"    {pub['name']}"
        if 'boost_name' in pub:
            s += f" <b>[{pub['boost_name']} - {pub['pct']}%]</b>"
        pubs.append(s)

    return f"\
<b>{block['name']} (see on <a href='https://blocks.metroverse.com/{block['name'][7:]}'>Metroverse</a>)</b>\n\
  <p>Total Score: <b>{block['scores']['Score: Total']}</b>\n\
  <p>Residential (Score {block['scores']['Score: Residential']}):\n<ul><li>{'<li>'.join(strs[0])}</ul>\n\
  <p>Commercial (Score {block['scores']['Score: Commercial']}):\n<ul><li>{'<li>'.join(strs[1])}</ul>\n\
  <p>Industrial (Score {block['scores']['Score: Industrial']}):\n<ul><li>{'<li>'.join(strs[2])}</ul>\n\
  <p>Public:\n<ul><li>{'<li>'.join(pubs)}</ul>\n\
"
