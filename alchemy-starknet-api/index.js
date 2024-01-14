const axios = require('axios');

const apiKey = '374l9-eucheJf7r_lvnEZbEJ3dmtKRqn'; // Replace with your Alchemy API key
const url = `https://starknet-mainnet.g.alchemy.com/v2/${apiKey}`;

const payload = {
  jsonrpc: '2.0',
  id: 1,
  method: 'starknet_blockNumber',
  params: []
};

axios.post(url, payload)
  .then(response => {
    console.log('Block Number:', response.data.result);
  })
  .catch(error => {
    console.error(error);
  });