import { useState } from 'react';
import { ChevronRight } from 'lucide-react';
import { useTranslation } from '../../../../i18n';
import { haptic } from '../../../../utils';
import { WALLET_TOKENS, type WalletToken } from '../walletTokens';
import { TokenDetailSheet } from './TokenDetailSheet';
import { TokenIcon } from '../TokenIcon';
import { useWalletBalances } from '../../hooks';

const MOCK_TXS: { type: 'deposit' | 'transfer'; label: string; amount: string; symbol: string; date: string }[] = [];

export const TokenList = () => {
  const { t } = useTranslation();
  const [selected, setSelected] = useState<WalletToken | null>(null);
  const { balances } = useWalletBalances();

  const open  = (token: WalletToken) => { haptic.light(); setSelected(token); };
  const close = () => setSelected(null);

  const tokenTxs = MOCK_TXS.filter((tx) => tx.symbol === selected?.symbol);

  return (
    <>
      <div className="bg-zinc-900 border border-zinc-800 rounded-2xl overflow-hidden">
        <div className="px-5 py-4 border-b border-zinc-800">
          <p className="text-sm font-semibold text-white">{t('wallet.tokens')}</p>
        </div>

        <div className="divide-y divide-zinc-800/40">
          {WALLET_TOKENS.map((token) => (
            <button
              key={token.id}
              onClick={() => open(token)}
              className="flex items-center gap-3 w-full px-5 py-3.5 hover:bg-zinc-800/40 active:bg-zinc-800/60 transition-colors"
            >
              <TokenIcon token={token} size={36} />

              <div className="flex-1 text-left min-w-0">
                <div className="flex items-center gap-1.5">
                  <p className="text-sm font-semibold text-white leading-tight">{token.symbol}</p>
                  {token.note && (
                    <span className="text-[9px] font-medium px-1.5 py-0.5 bg-zinc-700 text-zinc-400 rounded-full">{token.note}</span>
                  )}
                </div>
                <p className="text-[10px] text-zinc-600 mt-0.5 truncate">{token.network} · {token.name}</p>
              </div>

              <div className="text-right mr-1 shrink-0">
                <p className="text-sm font-mono text-white leading-tight">
                  {(balances[token.symbol]?.balance ?? 0).toFixed(token.decimals)}
                </p>
                {(balances[token.symbol]?.usdValue ?? 0) > 0 && (
                  <p className="text-[10px] font-mono text-zinc-500">
                    ${balances[token.symbol].usdValue.toFixed(2)}
                  </p>
                )}
              </div>
              <ChevronRight size={14} className="text-zinc-600 shrink-0" />
            </button>
          ))}
        </div>
      </div>

      {selected && (
        <TokenDetailSheet token={selected} txs={tokenTxs} onClose={close} />
      )}
    </>
  );
};
