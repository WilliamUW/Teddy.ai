import {
    emulator,
    getAccountAddress,
    getFlowBalance,
    init,
} from "@onflow/flow-js-testing"

const main = async () => {
    const basePath = path.resolve(__dirname, "../cadence")
  
    await init(basePath)
    await emulator.start()
  
    const Alice = await getAccountAddress("Alice")
  
    const [result, error] = await getFlowBalance(Alice)
    console.log(result, error)
  
    await emulator.stop()
  }
  
  main()
  