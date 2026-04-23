import { useState } from 'react';
import { X, ChevronDown } from 'lucide-react';
import { useTranslation } from '../../../../../i18n';
import { haptic } from '../../../../../utils';
import { type WalletToken } from '../../walletTokens';
import { TokenIcon } from '../../TokenIcon';
import { TokenPickerSheet } from '../../TokenPickerSheet';

interface Props { initial: WalletToken; onClose: () => void }

export const TransferModal = ({ initial, onClose }: Props) => {
  const { t } = useTranslation();
  const [token, setToken]         = useState(initial);
  const [picking, setPicking]     = useState(false);
  const [toAddress, setToAddress] = useState('');
  const [amount, setAmount]       = useState('');

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/70 backdrop-blur-sm" onClick={onClose}>
      <div className="w-full max-w-md bg-zinc-900 border-t border-zinc-800 rounded-t-2xl p-5 animate-slide-up" style={{ paddingBottom: 'calc(2rem + var(--safe-bottom, 0px))' }} onClick={(e) => e.stopPropagation()}>

        <div className="flex items-center justify-between mb-5">
          <h3 className="text-base font-bold text-white">{t('wallet.transfer')}</h3>
          <button onClick={onClose} className="p-1.5 rounded-full hover:bg-zinc-800 transition-colors">
            <X size={18} className="text-zinc-400" />
          </button>
        </div>

        {picking ? (
          <TokenPickerSheet
            active={token}
            onPick={(tok) => { setToken(tok); setPicking(false); }}
            onClose={() => setPicking(false)}
          />
        ) : (
          <div className="space-y-3">

            {/* Token selector */}
            <button
              onClick={() => { haptic.light(); setPicking(true); }}
              className="flex items-center gap-3 w-full px-4 py-3 bg-zinc-800 border border-zinc-700 rounded-xl hover:bg-zinc-700 transition-colors"
            >
              <TokenIcon token={token} size={32} />
              <div className="flex-1 text-left">
                <p className="text-sm font-bold text-white">{token.symbol}</p>
                <p className="text-[11px] text-zinc-500">{token.network}{token.note ? ` · ${token.note}` : ''}</p>
              </div>
              <ChevronDown size={16} className="text-zinc-400 shrink-0" />
            </button>

            <div>
              <label className="text-xs text-zinc-500 mb-1.5 block">{t('wallet.recipientAddress')}</label>
              <input
                type="text"
                value={toAddress}
                onChange={(e) => setToAddress(e.target.value)}
                placeholder="UQ..."
                className="w-full bg-zinc-800 border border-zinc-700 rounded-xl px-4 py-3 text-sm text-white placeholder-zinc-600 focus:outline-none focus:border-zinc-600 transition-colors"
              />
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-xs text-zinc-500">{t('wallet.amount')} ({token.symbol})</label>
                <span className="text-xs text-zinc-600">{t('wallet.balance')}: 0.00</span>
              </div>
              <input
                type="text"
                inputMode="decimal"
                value={amount}
                onChange={(e) => {
                  const v = e.target.value;
                  if (v === '' || /^\d*\.?\d*$/.test(v)) setAmount(v);
                }}
                placeholder="0.00"
                className="w-full bg-zinc-800 border border-zinc-700 rounded-xl px-4 py-3 text-sm text-white placeholder-zinc-600 focus:outline-none focus:border-zinc-600 transition-colors"
              />
            </div>

            <button
              disabled={!toAddress || !amount || parseFloat(amount) <= 0}
              className="w-full py-3 bg-white text-black rounded-xl font-semibold text-sm hover:bg-zinc-100 active:scale-95 transition-all disabled:opacity-30 disabled:cursor-not-allowed"
            >
              {t('wallet.send')}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
