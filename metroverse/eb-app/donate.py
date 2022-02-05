


def donate():
  return html



html = """
<html>
    <head>
<script src="https://cdn.jsdelivr.net/npm/web3@latest/dist/web3.min.js" type="text/javascript" />
        <style>
        tip-button:hover 
            {
            position:relative;
            left: 3px;
            }
        .tip-button:active 
            {
            color:gold;
            }
        </style>
    </head>
  <body>
    <img class="tip-button" src="https://www.srcmake.com/uploads/5/3/9/0/5390645/donateetherbutton_orig.png" alt="Metamask tip button" style="width:97%;">
    <div class="message"></div>
  </body>

    <script>
    var MY_ADDRESS = '0x7891338cC2d668bA268B69e3b8f85Cdf3660495E'
    var tipButton = document.querySelector('.tip-button')

    tipButton.addEventListener('click', function() 
        {
        if (typeof ethereum === 'undefined') 
            {
            return renderMessage('<div>You need to install <a href=“https://metmask.io“>MetaMask </a> to use this feature.  <a href=“https://metmask.io“>https://metamask.io</a></div>')
            }

        var user_address = ethereum.eth.accounts[0]

        ethereum.eth.sendTransaction(
            {
            to: MY_ADDRESS,
            from: user_address,
            value: ethereum.toWei('0.01', 'ether'),
            }, 
            function (err, transactionHash) 
                {
                if (err) return renderMessage('There was a problem!: ' + err.message)
                renderMessage('Thanks for the generosity!!')
            })
        })

    function renderMessage (message) 
        {
        var messageEl = document.querySelector('.message')
        messageEl.innerHTML = message
        }
    </script>
</html>
"""
