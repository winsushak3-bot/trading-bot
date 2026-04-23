import { useState } from 'react';
import { X, ArrowUpDown, ChevronDown } from 'lucide-react';
import { useTranslation } from '../../../../../i18n';
import { haptic } from '../../../../../utils';
import { WALLET_TOKENS, type WalletToken } from '../../walletTokens';
import { TokenIcon } from '../../TokenIcon';
import { TokenPickerSheet } from '../../TokenPickerSheet';

interface Props { onClose: () => void }
type Picking = 'from' | 'to' | null;

const TokenBtn = ({ token, onClick }: { token: WalletToken; onClick: () => void }) => (
  <button
    onClick={onClick}
    className="flex items-center gap-2 px-3 py-2 bg-zinc-700 hover:bg-zinc-600 active:scale-95 rounded-xl transition-all shrink-0"
  >
    <TokenIcon token={token} size={22} />
    <span className="text-sm font-bold text-white">{token.symbol}</span>
    <ChevronDown size={13} className="text-zinc-400" />
  </button>
);

export const ExchangeModal = ({ onClose }: Props) => {
  const { t } = useTranslation();
  const [fromToken, setFromToken] = useState<WalletToken>(WALLET_TOKENS[0]);
  const [toToken,   setToToken]   = useState<WalletToken>(WALLET_TOKENS[1]);
  const [amount, setAmount]       = useState('');
  const [picking, setPicking]     = useState<Picking>(null);

  const openPicker = (side: Picking) => { haptic.light(); setPicking(side); };

  const pickToken = (token: WalletToken) => {
    if (picking === 'from') {
      if (token.id === toToken.id) setToToken(fromToken);
      setFromToken(token);
    } else {
      if (token.id === fromToken.id) setFromToken(toToken);
      setToToken(token);
    }
    setPicking(null);
  };

  const swapDir = () => {
    haptic.light();
    const tmp = fromToken;
    setFromToken(toToken);
    setToToken(tmp);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/70 backdrop-blur-sm" onClick={onClose}>
      <div className="w-full max-w-md bg-zinc-900 border-t border-zinc-800 rounded-t-2xl p-5 animate-slide-up" style={{ paddingBottom: 'calc(2rem + var(--safe-bottom, 0px))' }} onClick={(e) => e.stopPropagation()}>

        <div className="flex items-center justify-between mb-5">
          <h3 className="text-base font-bold text-white">{t('wallet.exchange')}</h3>
          <button onClick={onClose} className="p-1.5 rounded-full hover:bg-zinc-800 transition-colors">
            <X size={18} className="text-zinc-400" />
          </button>
        </div>

        {picking ? (
          <TokenPickerSheet
            active={picking === 'from' ? fromToken : toToken}
            onPick={pickToken}
            onClose={() => setPicking(null)}
          />
        ) : (
          <div>
            {/* Swap card */}
            <div className="bg-zinc-800 border border-zinc-700 rounded-2xl overflow-hidden mb-3">

              {/* From */}
              <div className="p-4">
                <p className="text-xs text-zinc-500 mb-3">{t('wallet.exchangeFrom')}</p>
                <div className="flex items-center gap-3">
                  <TokenBtn token={fromToken} onClick={() => openPicker('from')} />
                  <input
                    type="text"
                    inputMode="decimal"
                    value={amount}
                    onChange={(e) => {
                      const v = e.target.value;
                      if (v === '' || /^\d*\.?\d*$/.test(v)) setAmount(v);
                    }}
                    placeholder="0.00"
                    className="flex-1 min-w-0 bg-transparent text-right text-2xl font-bold text-white placeholder-zinc-700 focus:outline-none"
                  />
                </div>
                <p className="text-xs text-zinc-600 mt-2">{t('wallet.balance')}: 0.00 {fromToken.symbol}</p>
              </div>

              {/* Divider + swap button */}
              <div className="relative border-t border-zinc-700 flex justify-center">
                <button
                  onClick={swapDir}
                  className="absolute -top-4 p-2 bg-zinc-800 border border-zinc-700 rounded-xl hover:bg-zinc-700 active:scale-95 transition-all"
                >
                  <ArrowUpDown size={14} className="text-zinc-400" />
                </button>
                <div className="h-4" />
              </div>

              {/* To */}
              <div className="p-4">
                <p className="text-xs text-zinc-500 mb-3">{t('wallet.exchangeTo')}</p>
                <div className="flex items-center gap-3">
                  <TokenBtn token={toToken} onClick={() => openPicker('to')} />
                  <p className="flex-1 text-right text-2xl font-bold text-zinc-600">—</p>
                </div>
                <p className="text-xs text-zinc-600 mt-2">{t('wallet.balance')}: 0.00 {toToken.symbol}</p>
              </div>
            </div>

            <div className="flex items-center justify-between px-1 mb-3">
              <span className="text-xs text-zinc-500">{t('wallet.exchangePoweredBy')}</span>
              <span className="text-xs font-semibold text-zinc-400">STON.fi</span>
            </div>

            <button
              disabled={!amount || parseFloat(amount) <= 0}
              className="w-full py-3 bg-white text-black rounded-xl font-semibold text-sm hover:bg-zinc-100 active:scale-95 transition-all disabled:opacity-30 disabled:cursor-not-allowed"
            >
              {t('wallet.exchange')}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
