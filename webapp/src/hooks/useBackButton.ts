import { useEffect, useRef } from 'react';
import { useWebApp } from './useWebApp';

export const useBackButton = (onBack: (() => void) | null) => {
  const { webApp } = useWebApp();
  const onBackRef = useRef(onBack);
  onBackRef.current = onBack;

  useEffect(() => {
    if (!webApp?.BackButton) return;

    if (!onBackRef.current) {
      webApp.BackButton.hide();
      return;
    }

    const handler = () => onBackRef.current?.();
    webApp.BackButton.show();
    webApp.BackButton.onClick(handler);
    return () => {
      webApp.BackButton.offClick(handler);
      webApp.BackButton.hide();
    };
  }, [webApp, onBack === null]);  // only re-run when null↔function transition happens
};
