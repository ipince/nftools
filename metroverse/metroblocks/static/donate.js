
TIP_ADDRESS = "0x130137F563e12bF4592B4280b488A270C96Cb2A3";
DEFAULT_AMOUNT_ETH = "0.01";

function donate() {
    console.log("clicked!");

    // 1) Metamask not installed, show address.
    // 2) Metamask installed, not enabled -> enable. If fail, then show address.
    // 3) Metamask installed, enabled -> send transaction.

    if (typeof ethereum === 'undefined') {
        show("Looks like you don't have MetaMask installed. Consider donating with whatever wallet you use.\n\nSee the tip wallet address in the FAQ.\n\nThank you for using Metroblocks <3");
    } else {  // metamask installed.
        if (ethereum.selectedAddress != null) {
            sendDonation(ethereum.selectedAddress, TIP_ADDRESS, DEFAULT_AMOUNT_ETH);
        } else {
            ethereum.request({method: "eth_requestAccounts"})
                .then((accounts) => sendDonation(accounts[0], TIP_ADDRESS, DEFAULT_AMOUNT_ETH))
                .catch((err) => show("Looks like you didn't connect your MetaMask wallet. That's OK! Feel free to donate directly to:\n\nSee the tip wallet address in the FAQ.\n\nThank you <3"));
        }
    }
}

function sendDonation(from, to, ethValue) {
    var params = {
        from: from,
        to: to,
        value: Web3.utils.toHex(Web3.utils.toWei(ethValue, 'ether')),
    };
    ethereum
        .request({
            method: "eth_sendTransaction",
            params: [params],
        })
        .then((txn) => show("THANK YOU!!! Really, thank you so much. This helps motivate me to keep spending time improving the site.\n\nYou're the best <3"))
        .catch((err) => show("Looks like the transaction was rejected.\n\nPlease note that you can change the amount by clicking 'Edit' in the MetaMask pop-up.\n\nEither way, I appreciate you for being here!"));
}

function show(msg) {
    // For now, just a shitty alert. Make it a nice popup later.
    alert(msg);
}
