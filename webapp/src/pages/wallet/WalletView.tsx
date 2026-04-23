import { PageWrapper } from '../../shared/ui';
import { BalanceCard, TokenList } from './components';

export const WalletView = () => {
  return (
    <PageWrapper className="pb-4 -mx-2 space-y-3">
      <BalanceCard />
      <TokenList />
    </PageWrapper>
  );
};
