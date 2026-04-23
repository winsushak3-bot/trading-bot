import { Check } from 'lucide-react';
import { useTranslation } from '../../../i18n';
import { haptic } from '../../../utils';
import { WALLET_TOKENS, type WalletToken } from './walletTokens';
import { TokenIcon } from './TokenIcon';

interface Props {
  active: WalletToken;
  onPick: (token: WalletToken) => void;
  onClose: () => void;
}

export const TokenPickerSheet = ({ active, onPick, onClose }: Props) => {
  const { t } = useTranslation();

  const handlePick = (token: WalletToken) => {
    haptic.light();
    onPick(token);
  };

  return (
    <div className="space-y-1">
      <div className="max-h-60 overflow-y-auto space-y-0.5">
        {WALLET_TOKENS.map((token) => (
          <button
            key={token.id}
            onClick={() => handlePick(token)}
            className="flex items-center gap-3 w-full px-3 py-3 rounded-xl hover:bg-zinc-800 active:bg-zinc-700 transition-colors"
          >
            <TokenIcon token={token} size={36} />
            <div className="flex-1 text-left min-w-0">
              <p className="text-sm font-semibold text-white leading-tight">{token.symbol}</p>
              <p className="text-[11px] text-zinc-500">{token.name}</p>
            </div>
            {active.id === token.id && <Check size={16} className="text-zinc-300 shrink-0" />}
          </button>
        ))}
      </div>
      <button
        onClick={onClose}
        className="w-full py-2.5 bg-zinc-800 text-zinc-400 rounded-xl text-sm font-medium hover:bg-zinc-700 transition-colors"
      >
        {t('common.cancel')}
      </button>
    </div>
  );
};
