import type { Metadata } from 'next';
import './globals.css';
import AnalyticsConsent from '../components/AnalyticsConsent';

export const metadata: Metadata = {
  title: {
    default: 'Ahorra360 | Ayudas, descuentos y oportunidades para ahorrar',
    template: '%s | Ahorra360',
  },
  description: 'Encuentra ayudas públicas, beneficios fiscales, descuentos y oportunidades de ahorro para tu vivienda y tus gastos domésticos. Información contrastada con fuentes oficiales.',
  openGraph: {
    title: 'Ahorra360',
    description: 'Ayudas, descuentos y oportunidades para ahorrar.',
    type: 'website',
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body>
        {children}
        <AnalyticsConsent />
      </body>
    </html>
  );
}
