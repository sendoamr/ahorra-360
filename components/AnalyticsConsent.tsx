'use client';

import { useEffect, useState } from 'react';
import Script from 'next/script';
import Link from 'next/link';
import { GA_MEASUREMENT_ID } from '../config/analytics';

const CONSENT_KEY = 'ahorra360-analytics-consent';

export default function AnalyticsConsent() {
  const [consent, setConsent] = useState<'accepted' | 'rejected' | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    try {
      const saved = window.localStorage.getItem(CONSENT_KEY);
      if (saved === 'accepted' || saved === 'rejected') setConsent(saved);
    } finally {
      setReady(true);
    }
  }, []);

  const choose = (value: 'accepted' | 'rejected') => {
    try {
      window.localStorage.setItem(CONSENT_KEY, value);
    } finally {
      setConsent(value);
    }
  };

  if (!GA_MEASUREMENT_ID || !ready) return null;

  return (
    <>
      {consent === 'accepted' && (
        <>
          <Script
            src={`https://www.googletagmanager.com/gtag/js?id=${GA_MEASUREMENT_ID}`}
            strategy="afterInteractive"
          />
          <Script id="google-analytics-consent" strategy="afterInteractive">
            {`
              window.dataLayer = window.dataLayer || [];
              function gtag(){window.dataLayer.push(arguments);}
              window.gtag = gtag;
              gtag('js', new Date());
              gtag('config', '${GA_MEASUREMENT_ID}', { anonymize_ip: true });
            `}
          </Script>
        </>
      )}

      {consent === null && (
        <section
          aria-label="Preferencias de cookies"
          role="dialog"
          aria-live="polite"
          style={{
            position: 'fixed',
            zIndex: 1000,
            left: 16,
            right: 16,
            bottom: 16,
            maxWidth: 760,
            margin: '0 auto',
            padding: 20,
            border: '1px solid #dce5dd',
            borderRadius: 16,
            background: '#fff',
            color: '#183326',
            boxShadow: '0 8px 32px rgba(0,0,0,.16)',
          }}
        >
          <p style={{ margin: '0 0 8px', fontWeight: 700 }}>Tu privacidad importa</p>
          <p style={{ margin: '0 0 16px', lineHeight: 1.5, fontSize: 14 }}>
            Utilizamos Google Analytics para conocer de forma agregada cómo se utiliza Ahorra360
            y mejorar sus contenidos. Las cookies analíticas solo se activarán si las aceptas.
            Puedes consultar más información en nuestra <Link href="/privacidad" style={{ textDecoration: 'underline' }}>política de privacidad</Link>.
          </p>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10 }}>
            <button
              type="button"
              onClick={() => choose('accepted')}
              style={{ border: 0, borderRadius: 8, padding: '10px 16px', background: '#176b45', color: '#fff', fontWeight: 600, cursor: 'pointer' }}
            >
              Aceptar analítica
            </button>
            <button
              type="button"
              onClick={() => choose('rejected')}
              style={{ border: '1px solid #cbd5ce', borderRadius: 8, padding: '10px 16px', background: '#fff', color: '#183326', cursor: 'pointer' }}
            >
              Rechazar
            </button>
          </div>
        </section>
      )}
    </>
  );
}
