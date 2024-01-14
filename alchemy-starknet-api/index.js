const axios = require('axios');

const apiKey = '374l9-eucheJf7r_lvnEZbEJ3dmtKRqn'; // Replace with your Alchemy API key
const url = `https://starknet-mainnet.g.alchemy.com/v2/${apiKey}`;

const payload = {
  jsonrpc: '2.0',
  id: 1,
  method: 'starknet_getTransactionReceipt',
  params: ["0xe703a1507781952ce4f63cbf1985f6f5c4e2f51fb442c31c6679dfd8e09ee06d"]
};

axios.post(url, payload)
  .then(response => {
    console.log('Block Number:', response.data.result);
  })
  .catch(error => {
    console.error(error);
  });