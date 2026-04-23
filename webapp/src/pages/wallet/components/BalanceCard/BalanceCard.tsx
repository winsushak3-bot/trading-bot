import { useState } from 'react';
import { ArrowDownLeft, ArrowUpRight, ArrowLeftRight, Wallet } from 'lucide-react';
import { useTonWallet, useTonConnectUI, toUserFriendlyAddress } from '@tonconnect/ui-react';
import { useTranslation } from '../../../../i18n';
import { haptic } from '../../../../utils';
import { WALLET_TOKENS } from '../walletTokens';
import { useWalletBalances } from '../../hooks';
import { DepositModal }  from './modals/DepositModal';
import { TransferModal } from './modals/TransferModal';
import { ExchangeModal } from './modals/ExchangeModal';

type ModalType = 'deposit' | 'transfer' | 'exchange' | null;

export const BalanceCard = () => {
  const { t } = useTranslation();
  const [modal, setModal] = useState<ModalType>(null);

  const wallet = useTonWallet();
  const [tonConnectUI] = useTonConnectUI();
  const connected = !!wallet;
  const walletAddress = wallet ? toUserFriendlyAddress(wallet.account.address) : undefined;
  const { totalUsd, loading } = useWalletBalances();

  const open  = (type: ModalType) => { haptic.light(); setModal(type); };
  const close = () => setModal(null);

  return (
    <>
      <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-5">
        <div className="mb-6">
          <p className="text-xs text-zinc-500 uppercase tracking-widest mb-2">{t('wallet.totalBalance')}</p>
          {connected ? (
            <p className="text-5xl font-bold text-white tracking-tight">
              {loading ? '...' : `$${totalUsd.toFixed(2)}`}
            </p>
          ) : (
            <div className="flex items-end gap-3">
              <p className="text-5xl font-bold text-zinc-700 tracking-tight">$0.00</p>
            </div>
          )}
        </div>

        {!connected && (
          <button
            onClick={() => { haptic.light(); tonConnectUI.openModal(); }}
            className="flex items-center justify-center gap-2 w-full py-3 mb-4 bg-white text-black rounded-xl font-semibold text-sm hover:bg-zinc-100 active:scale-95 transition-all"
          >
            <Wallet size={16} strokeWidth={2.5} />
            {t('wallet.connectWallet')}
          </button>
        )}
        <div className="grid grid-cols-3 gap-2">
          {[
            { type: 'deposit'  as ModalType, icon: ArrowDownLeft,  label: t('wallet.deposit')  },
            { type: 'transfer' as ModalType, icon: ArrowUpRight,   label: t('wallet.transfer') },
            { type: 'exchange' as ModalType, icon: ArrowLeftRight, label: t('wallet.exchange') },
          ].map(({ type, icon: Icon, label }) => (
            <button
              key={type}
              onClick={() => connected ? open(type) : haptic.warning()}
              disabled={!connected}
              className="flex flex-col items-center gap-2 py-3.5 bg-zinc-800 hover:bg-zinc-700 active:scale-95 rounded-xl transition-all duration-150 disabled:opacity-40 disabled:cursor-not-allowed disabled:active:scale-100"
            >
              <div className="p-2 bg-zinc-700 rounded-full">
                <Icon size={16} className="text-white" strokeWidth={2.5} />
              </div>
              <span className="text-[11px] font-medium text-zinc-300">{label}</span>
            </button>
          ))}
        </div>
      </div>

      {modal === 'deposit'  && <DepositModal  initial={WALLET_TOKENS[0]} onClose={close} walletAddress={walletAddress} />}
      {modal === 'transfer' && <TransferModal initial={WALLET_TOKENS[0]} onClose={close} />}
      {modal === 'exchange' && <ExchangeModal onClose={close} />}
    </>
  );
};
