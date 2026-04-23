import { X, Info, ArrowDownLeft, ArrowUpRight } from 'lucide-react';
import { useTranslation } from '../../../../i18n';
import { type WalletToken } from '../walletTokens';
import { TokenIcon } from '../TokenIcon';

interface Tx {
  type: 'deposit' | 'transfer';
  label: string;
  amount: string;
  date: string;
}

interface Props {
  token: WalletToken;
  txs: Tx[];
  onClose: () => void;
}

export const TokenDetailSheet = ({ token, txs, onClose }: Props) => {
  const { t } = useTranslation();

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/70 backdrop-blur-sm" onClick={onClose}>
      <div className="w-full max-w-md bg-zinc-900 border-t border-zinc-800 rounded-t-2xl p-5 pb-8 animate-slide-up" onClick={(e) => e.stopPropagation()}>

        {/* Header */}
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-3">
            <TokenIcon token={token} size={40} />
            <div>
              <div className="flex items-center gap-2">
                <p className="text-base font-bold text-white leading-tight">{token.symbol}</p>
                {token.note && (
                  <span className="text-[9px] font-medium px-1.5 py-0.5 bg-zinc-700 text-zinc-400 rounded-full">{token.note}</span>
                )}
              </div>
              <p className="text-[10px] text-zinc-500 mt-0.5">{token.network} · {token.name}</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-full hover:bg-zinc-800 transition-colors">
            <X size={18} className="text-zinc-400" />
          </button>
        </div>

        {/* Wrapped info */}
        {token.note === 'Wrapped' && (
          <div className="flex items-start gap-2 bg-zinc-800 border border-zinc-700 rounded-xl p-3 mb-4">
            <Info size={13} className="text-zinc-400 mt-0.5 shrink-0" />
            <p className="text-xs text-zinc-400 leading-relaxed">{token.symbol} — {t('wallet.wrappedInfo')}</p>
          </div>
        )}

        {/* Balance */}
        <div className="bg-zinc-800 rounded-xl p-4 mb-5 text-center">
          <p className="text-xs text-zinc-500 mb-1">{t('wallet.balance')}</p>
          <p className="text-2xl font-bold text-white">{token.balance.toFixed(token.decimals)}</p>
          <p className="text-xs text-zinc-500 mt-0.5">{token.symbol}</p>
        </div>

        {/* History */}
        <p className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-3">{t('wallet.history')}</p>

        {txs.length === 0 ? (
          <div className="py-8 text-center">
            <p className="text-sm text-zinc-600">{t('wallet.noTransactions')}</p>
          </div>
        ) : (
          <div className="space-y-1 max-h-52 overflow-y-auto">
            {txs.map((tx) => (
              <div key={`${tx.date}-${tx.amount}-${tx.type}`} className="flex items-center gap-3 py-2.5">
                <div className="p-2 rounded-full shrink-0 bg-zinc-800">
                  {tx.type === 'deposit'
                    ? <ArrowDownLeft size={14} className="text-zinc-300" />
                    : <ArrowUpRight  size={14} className="text-zinc-400" />
                  }
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-white leading-tight">{tx.label}</p>
                  <p className="text-xs text-zinc-500">{tx.date}</p>
                </div>
                <p className="text-sm font-semibold shrink-0 text-zinc-300">
                  {tx.type === 'deposit' ? '+' : '-'}{tx.amount}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
