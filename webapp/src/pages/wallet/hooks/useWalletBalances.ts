import { useEffect } from 'react';
import { useTonWallet, toUserFriendlyAddress } from '@tonconnect/ui-react';
import { create } from 'zustand';

export interface BalanceInfo {
  balance: number;
  usdPrice: number;
  usdValue: number;
}

interface BalanceState {
  balances: Record<string, BalanceInfo>;
  totalUsd: number;
  loading: boolean;
  _set: (balances: Record<string, BalanceInfo>, totalUsd: number) => void;
  _setLoading: (v: boolean) => void;
  _clear: () => void;
}

const useStore = create<BalanceState>((set) => ({
  balances: {},
  totalUsd: 0,
  loading: false,
  _set: (balances, totalUsd) => set({ balances, totalUsd, loading: false }),
  _setLoading: (loading) => set({ loading }),
  _clear: () => set({ balances: {}, totalUsd: 0, loading: false }),
}));

let _fetching = false;

async function doFetch(address: string) {
  if (_fetching) return;
  _fetching = true;
  useStore.getState()._setLoading(true);

  try {
    const [accRes, jetRes, ratesRes] = await Promise.all([
      fetch(`https://tonapi.io/v2/accounts/${address}`),
      fetch(`https://tonapi.io/v2/accounts/${address}/jettons?currencies=usd`),
      fetch('https://tonapi.io/v2/rates?tokens=ton&currencies=usd'),
    ]);

    const [accData, jetData, ratesData] = await Promise.all([
      accRes.json(),
      jetRes.json(),
      ratesRes.json(),
    ]);

    const result: Record<string, BalanceInfo> = {};

    const tonBal = parseInt(accData.balance || '0') / 1e9;
    const tonPrice = ratesData.rates?.TON?.prices?.USD || 0;
    result['TON'] = { balance: tonBal, usdPrice: tonPrice, usdValue: tonBal * tonPrice };

    if (jetData.balances) {
      for (const item of jetData.balances) {
        const decimals = item.jetton?.decimals || 9;
        const bal = parseInt(item.balance || '0') / Math.pow(10, decimals);
        const symbol: string = item.jetton?.symbol || '';
        const price = item.price?.prices?.USD || 0;
        result[symbol] = { balance: bal, usdPrice: price, usdValue: bal * price };
      }
    }

    const totalUsd = Object.values(result).reduce((s, t) => s + t.usdValue, 0);
    useStore.getState()._set(result, totalUsd);
  } catch (err) {
    console.error('Failed to fetch balances:', err);
    useStore.getState()._setLoading(false);
  } finally {
    _fetching = false;
  }
}

export const useWalletBalances = () => {
  const wallet = useTonWallet();
  const { balances, totalUsd, loading, _clear } = useStore();

  useEffect(() => {
    if (!wallet) {
      _clear();
      return;
    }

    const address = toUserFriendlyAddress(wallet.account.address);
    doFetch(address);

    const iv = setInterval(() => doFetch(address), 30000);
    return () => clearInterval(iv);
  }, [wallet]);

  return { balances, totalUsd, loading };
};
