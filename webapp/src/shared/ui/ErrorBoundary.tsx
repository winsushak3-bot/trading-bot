import { Component, ReactNode } from 'react';
import { useI18nStore } from '../../i18n/useTranslation';
import { translations } from '../../i18n/i18n';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: { componentStack: string }) {
    console.error('[ErrorBoundary]', error, info.componentStack);
  }

  render() {
    if (this.state.hasError) {
      const lang = useI18nStore.getState().language;
      const t = translations[lang];
      return (
        <div className="fixed inset-0 bg-black flex flex-col items-center justify-center p-8 text-center">
          <p className="text-4xl mb-4">⚠️</p>
          <h2 className="text-white text-xl font-bold mb-2">{t.common.somethingWrong}</h2>
          <p className="text-zinc-500 text-sm mb-6">{this.state.error?.message}</p>
          <button
            onClick={() => this.setState({ hasError: false, error: null })}
            className="px-6 py-3 bg-white text-black rounded-xl font-bold text-sm"
          >
            {t.common.tryAgain}
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
