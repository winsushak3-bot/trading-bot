import { type WalletToken } from './walletTokens';

interface TokenIconProps {
  token: WalletToken;
  size?: number;
}

export const TokenIcon = ({ token, size = 36 }: TokenIconProps) => {
  const fontSize = token.abbr.length <= 3 ? Math.round(size * 0.28) : Math.round(size * 0.22);
  return (
    <div
      className="rounded-full flex items-center justify-center text-white font-bold shrink-0"
      style={{
        width: size,
        height: size,
        backgroundColor: token.color,
        fontSize,
      }}
    >
      {token.abbr}
    </div>
  );
};
