import { getContract } from "thirdweb";
import { thirdwebClient, chain } from "./thirdweb";

export interface TokenConfig {
  symbol: string;
  name: string;
  decimals: number;
  address: string;
  color: string;
}

// Base Sepolia testnet — only verified contracts
// On mainnet Base, replace with real contract addresses and add more tokens.
export const TOKENS: TokenConfig[] = [
  {
    symbol: "USDT",
    name: "Tether USD",
    decimals: 6,
    address: "0x7169D38820dfd117C3FA1f22a697dBA58d90BA06",
    color: "#26A17B",
  },
  {
    symbol: "USDC",
    name: "USD Coin",
    decimals: 6,
    address: "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
    color: "#2775CA",
  },
  {
    symbol: "DAI",
    name: "Dai Stablecoin",
    decimals: 18,
    address: "0x7683022d84F726a96c4A6611cD31DBf5409c0Ac9",
    color: "#F5AC37",
  },
  {
    symbol: "WETH",
    name: "Wrapped Ether",
    decimals: 18,
    address: "0x4200000000000000000000000000000000000006",
    color: "#627EEA",
  },
];

export const ETH_TOKEN: TokenConfig = {
  symbol: "ETH",
  name: "Ethereum",
  decimals: 18,
  address: "native",
  color: "#627EEA",
};

export const ALL_TOKENS = [ETH_TOKEN, ...TOKENS];

export const getTokenContract = (tokenAddress: string) =>
  getContract({
    client: thirdwebClient,
    chain,
    address: tokenAddress,
  });
