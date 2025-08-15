import React, { useEffect, useState } from 'react';
// ... existing code ...
// Importar tokens de cor e tipografia do tema
import { colors, typography } from '../../../ui/theme';

const Branding: React.FC = () => {
  const [logoSrc, setLogoSrc] = useState<string>('https://placehold.co/40x40?text=Logo');

  useEffect(() => {
    import('../../../static/image/logo.svg')
      .then((mod) => setLogoSrc(typeof mod === 'string' ? mod : (mod.default as string)))
      .catch(() => setLogoSrc('https://placehold.co/40x40?text=Logo'));
  }, []);

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
      {/* Logotipo (usar placeholder se não houver logo.svg/png) */}
      <img
        src={logoSrc}
        alt="Logo Omni Keywords Finder"
        style={{ width: 40, height: 40, borderRadius: 8, background: colors.background, boxShadow: colors.shadowMd }}
      />
      <span style={{ fontFamily: typography.fontFamily, fontWeight: 700, fontSize: typography.title, color: colors.primary }}>
        Omni Keywords Finder
      </span>
    </div>
  );
};

export default Branding; 