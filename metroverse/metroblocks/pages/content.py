
title = '''
<html><head>
<title>Metroblocks</title>
<meta name="robots" content="nofollow">
<script src="https://cdn.jsdelivr.net/npm/web3@latest/dist/web3.min.js"></script>
<script src="/static/donate.js" defer></script>
<link rel="stylesheet" type="text/css" href="/static/style.css">
<link rel="icon" type="image/x-icon" href="/static/images/favicon.png">
</head>
<body>
'''


def header(page):
  return title + f'''
<div class="topnav">
  <a {'class="active"' if page == 'blocks' else ''} href="/">Blocks</a>
  <a {'class="active"' if page == 'hoods' else ''} href="/hood">Hoods</a>
  <a {'class="active"' if page == 'buildings' else ''} href="/buildings">Buildings</a>
  <a {'class="active"' if page == 'pathways' else ''} href="/pathways">Pathways</a>
  <a {'class="active"' if page == 'ranks' else ''} href="/ranks">Ranks</a>
  <a {'class="active"' if page == 'owners' else ''} href="/owners">Owners</a>
  <a {'class="active"' if page == 'faq' else ''} href="/faq">FAQ</a>
  <div title="If you like Metroblocks, consider donating :)  Anything is much appreciated. Thank you!" onclick='donate()'>Tip Jar!</div>
</div>
<div class="body">
'''


footer = '''
<p>---<p>Feedback? Ideas? See the <a href="/faq">FAQ</a> or contact me on Metroverse discord: GrainOfSalt#1158. Find the site useful? Consider <span onclick='donate()' style='cursor: pointer; color: blue; text-decoration: underline'>tipping</span>!
</div>
</body>
'''


def with_body(body, page):
    return header(page)+body+footer

