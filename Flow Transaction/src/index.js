import { query, mutate, tx, reauthenticate } from "@onflow/fcl";
import "./testnet-config";

const getFlowBalance = async (address) => {
  const cadence = `
    import FlowToken from 0xFLOW
    import FungibleToken from 0xFT
    
    pub fun main(address: Address): UFix64{
      let account = getAccount(address)
      let path = /public/flowTokenBalance

      let vaultRef = account.getCapability(path)
        .borrow<&FlowToken.Vault{FungibleToken.Balance}>()
        ?? panic("Could not borrow Balance reference to the Vault")

      return vaultRef.balance
    }
  `;
  const args = (arg, t) => [arg(address, t.Address)];
  const balance = await query({ cadence, args });
  console.log({ balance });
  return balance;
};

const sendFlow = async (recepient, amount) => {
  const cadence = `
    import FungibleToken from 0xFT
    import FlowToken from 0xFLOW

    transaction(recepient: Address, amount: UFix64){
      prepare(signer: AuthAccount){
        let sender = signer.borrow<&FlowToken.Vault>(from: /storage/flowTokenVault)
          ?? panic("Could not borrow Provider reference to the Vault")

        let receiverAccount = getAccount(recepient)

        let receiver = receiverAccount.getCapability(/public/flowTokenReceiver)
          .borrow<&FlowToken.Vault{FungibleToken.Receiver}>()
          ?? panic("Could not borrow Receiver reference to the Vault")
 
        receiver.deposit(from: <- sender.withdraw(amount: amount))
      }
    }
  `;
  const args = (arg, t) => [arg(recepient, t.Address), arg(amount, t.UFix64)];
  const limit = 500;

  const txId = await mutate({
    cadence,
    args,
    limit,
  });
  console.log("Waiting for transaction to be sealed...");
  const txDetails = await tx(txId).onceSealed();
  console.log({ txDetails });
};

(async () => {
  console.clear();
  // "reauthenticate" will ensure your session works properly
  // and present you a popup to sign in
  await reauthenticate();

  const recipient = document.getElementById("recipient").value;
  const amount = document.getElementById("amount").value;

  // Display initial balance
  let balance = await getFlowBalance(recipient);

  document.getElementById("balance").innerText =
    "Recipient Balance: " + balance + " FLOW";

  // Update status message
  document.getElementById("status").innerText =
    "Sending " + amount + " FLOW to " + recipient + "...";

  // Send FLOW tokens
  await sendFlow(recipient, amount);

  // Check updated balance
  balance = await getFlowBalance(recipient);

  document.getElementById("balance").innerText =
    "Recipient Balance: " + balance + " FLOW";

  // Update status message
  document.getElementById("status").innerText = "Transaction complete!";
})();
