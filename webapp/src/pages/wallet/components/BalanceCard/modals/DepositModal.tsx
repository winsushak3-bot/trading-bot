import { useState } from 'react';
import { X, Copy, Info, ChevronDown } from 'lucide-react';
import { useTranslation } from '../../../../../i18n';
import { haptic } from '../../../../../utils';
import { type WalletToken } from '../../walletTokens';
import { TokenIcon } from '../../TokenIcon';
import { TokenPickerSheet } from '../../TokenPickerSheet';

interface Props { initial: WalletToken; onClose: () => void; walletAddress?: string }

export const DepositModal = ({ initial, onClose, walletAddress }: Props) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (!walletAddress) return;
    navigator.clipboard.writeText(walletAddress);
    haptic.success();
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  const { t } = useTranslation();
  const [token, setToken]     = useState(initial);
  const [picking, setPicking] = useState(false);
  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/70 backdrop-blur-sm" onClick={onClose}>
      <div className="w-full max-w-md bg-zinc-900 border-t border-zinc-800 rounded-t-2xl p-5 animate-slide-up" style={{ paddingBottom: 'calc(2rem + var(--safe-bottom, 0px))' }} onClick={(e) => e.stopPropagation()}>

        <div className="flex items-center justify-between mb-5">
          <h3 className="text-base font-bold text-white">{t('wallet.deposit')}</h3>
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

            {token.note === 'Wrapped' && (
              <div className="flex items-start gap-2 bg-zinc-800 border border-zinc-700 rounded-xl p-3">
                <Info size={13} className="text-zinc-400 mt-0.5 shrink-0" />
                <p className="text-xs text-zinc-400 leading-relaxed">{token.symbol} — {t('wallet.wrappedInfo')}</p>
              </div>
            )}

            <div className="bg-zinc-800 border border-zinc-700 rounded-xl p-4 text-center space-y-3">
              <p className="text-xs text-zinc-500">{t('wallet.sendTokensTo')}</p>
              {walletAddress ? (
                <p className="text-sm font-mono text-white break-all">{walletAddress}</p>
              ) : (
                <p className="text-sm font-mono text-zinc-500 italic">{t('wallet.connectToSeeAddress')}</p>
              )}
            </div>

            <button
              disabled={!walletAddress}
              onClick={handleCopy}
              className={`w-full flex items-center justify-center gap-2 py-2.5 rounded-xl font-semibold text-sm transition-all ${
                walletAddress
                  ? 'bg-zinc-800 text-white hover:bg-zinc-700 active:scale-95'
                  : 'bg-zinc-800 text-zinc-600 cursor-not-allowed'
              }`}
            >
              <Copy size={15} />{copied ? t('wallet.copied') : t('wallet.copyAddress')}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
