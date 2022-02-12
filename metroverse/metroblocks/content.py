
title = '''
<html><head>
<title>Metroblocks</title>
<script src="https://cdn.jsdelivr.net/npm/web3@latest/dist/web3.min.js"></script>
<script src="/static/donate.js" defer></script>
<link rel="stylesheet" type="text/css" href="/static/style.css">
</head>
<body>
'''

def header(page):
  return title + f'''
<div class="topnav">
  <a {'class="active"' if page == 'blocks' else ''} href="/">Blocks</a>
  <a {'class="active"' if page == 'hoods' else ''} href="/hood">Hoods</a>
  <a {'class="active"' if page == 'buildings' else ''} href="/buildings">Buildings</a>
  <a {'class="active"' if page == 'ranks' else ''} href="/ranks">Ranks</a>
  <a {'class="active"' if page == 'owners' else ''} href="/owners">Owners</a>
  <a {'class="active"' if page == 'faq' else ''} href="/faq">FAQ</a>
  <div title="If you like Metroblocks, consider donating :)  Anything is much appreciated. Thank you!" onclick='donate()'>Donate</div>
</div>
<div class="body">
'''

footer = '''
<p>---<p>Feedback? Ideas? See the <a href="/faq">FAQ</a> or contact me on Metroverse discord: GrainOfSalt#1158
</div>
</body>
'''

FAQ = '''
<h1>FAQ</h1>
<ul>

<li>What is Metroblocks.io?
<ul><li>It's a website to look up and analyze <a href="https://metroverse.com/">Metroverse</a> blocks, so you can make informed strategic and financial decisions! You're always told to DYOR—here, you can!
</ul>

<li>Why not use the <a href="https://blocks.metroverse.com">Metroverse block explorer</a>?
<ul><li>The Metroverse block explorer is absolutely <em>beautiful</em>, but it's a bit hard to find all the buildings in your block at-a-glance, and to see whether you'll get neighborhood boosts or not with your set of blocks.
</ul>

<li>Where does the data come from?
<ul><li>There's two types of data. The data for a block itself comes the NFTs themselves. I extracted the data from IPFS. Here's an <a href="https://ipfs.io/ipfs/QmR2wmDSCcbZnByZJrhJk92ZxtSmxxw5965cyJ4veV8qXA/1">example</a> of the raw data for a block.
<li>The data for buildings, their scores, "weights", and the neighborhood boosts, come straight out of the <a href="https://docs.metroverse.com/introduction/summary">Metroverse docs</a> (buildings and boosts).
</ul>

<li>How do Metroverse blocks work?
<ul><li>The best source of information are the <a href="https://docs.metroverse.com/introduction/summary">Metroverse docs</a> themselves, but here's a quick tl;dr:
  <ul><li>Each block has a set of buildings. Each building has a "score." A block's score is computed by (a) summing up the scores of all its buildings, and (b) applying the boosts from the <a href="https://docs.metroverse.com/overview/building-scores#public-buildings">public buildings</a> in that block. That leaves you with the total score for the block.
  <li>When staked, a block will generate MET in a daily amount equal to its score. That is, if the block's score is X, then it will produce X MET per day.
  <li>Your "hood" is the set of all your staked blocks. If your hood has a particular combination of buildings, it may unlock <a href="https://docs.metroverse.com/overview/neighborhood-boost">neighborhood boosts</a> which increase your MET production.
</ul></ul>

<li>Why is the site so fugly?
<ul><li>I'm sorry, I don't have much web experience. If you can help me with the design, I would greatly appreciate it!
</ul>

<li>How do I contact you?
<ul><li>If you have any feedback, questions, or ideas, please contact me on the Metroverse Discord at GrainOfSalt#1158
<li>If you're feeling generous, drop me a tip (either ETH or MET ;)): <code style="font-weight: bold">0x130137F563e12bF4592B4280b488A270C96Cb2A3</code>
</ul>
</ul>

<h1>Features</h1>

<ul><li>DONE
  <ul><li>(see <a href="/ranks">Ranks</a>) Create a ranking for the best blocks, as measured by their MET production capacity. This answers the question: if you wanted to maximize MET and could only afford one block, which one is the most efficient? Note that this is not only determined by the block's score, because we also need to consider neighborhood boosts (a single block may contain all the buildings needed for a neighborhood boost).
  <li>(use the <a href="/hood">Hood Simulator</a> with 1 block) Expanding the above, if you could have _two_ blocks, which two blocks are best? Which blocks synergize with which?
  <li>(same as above) If you have one block, which other block should you get?
  <li>(see <a href="/hood">Hood Simulator</a>!) If you had a bunch of blocks, what would your total score (with neighborhood boost) be? What's the best way to expand that hood?
  <li>(see <a href="/buildings">Buildings</a>) Compute building and block rarity. (note: I didn't implement block rarity because it's too subjective).
</ul>
<li>Upcoming
<ul>
<li>Add Pathway Boosts to Hood Simulator
<li>Add more visible tip jar
<li>Show whether a block is staked or not (automatic). Right now I update this manually.

<li>Add Pathway Boost page to see which blocks have which pathways
<li>Improve hood expansion calculation to prioritize hoods that add pathway boosts
<li>Implement stackable boosts (with 0.5 decay), as mentioned in AMA.
<li>Show whether a block is listed on OpenSea, and its price. I'm waiting on an OpenSea API key for this.
<li>Win-Wins: Given two hoods, does there exist a block trade that results in <b>both</b> hoods being better off?
<li>Trading Platform: link up your wallet to the site. If you want a specific block, you can message the owner of that block. When the owner links up their wallet, they'll be able to see your message and message you back!
</ul>

'''

def with_body(body, page):
  return header(page)+body+footer

def faq():
  return with_body(FAQ, 'faq')
