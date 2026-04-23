import { PageWrapper } from '../../shared/ui';
import { useAppStore } from '../../store';
import { haptic } from '../../utils';
import { CryptoTile, ForexTile, ScreenerTile } from './components';

export const TradeView = () => {
  const { setActiveMarket } = useAppStore();

  const handleTradeSelect = (market: 'crypto' | 'forex' | 'screener') => {
    haptic.light();
    setActiveMarket(market);
  };

  return (
    <PageWrapper className="-mx-4 -mt-2">
      <div className="grid grid-cols-2 gap-2 px-1 pt-0">
        <CryptoTile onClick={() => handleTradeSelect('crypto')} />
        <ForexTile onClick={() => handleTradeSelect('forex')} />
        <ScreenerTile onClick={() => handleTradeSelect('screener')} />
      </div>
    </PageWrapper>
  );
};
