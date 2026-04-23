import { createThirdwebClient } from "thirdweb";
import { baseSepolia } from "thirdweb/chains";
import { inAppWallet } from "thirdweb/wallets";

export const THIRDWEB_CLIENT_ID = import.meta.env.VITE_THIRDWEB_CLIENT_ID || "";

export const thirdwebClient = createThirdwebClient({
  clientId: THIRDWEB_CLIENT_ID,
});

export const chain = baseSepolia;

export const wallet = inAppWallet({
  executionMode: {
    mode: "EIP4337",
    smartAccount: {
      chain: baseSepolia,
      sponsorGas: true,
    },
  },
});
