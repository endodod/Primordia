import type { Config } from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'Primordia',
  tagline: 'A desktop evolution laboratory',
  url: 'https://endodod.github.io',
  baseUrl: '/Primordia/',
  organizationName: 'endodod',
  projectName: 'Primordia',
  onBrokenLinks: 'throw',
  i18n: { defaultLocale: 'en', locales: ['en'] },
  presets: [
    [
      'classic',
      {
        docs: {
          routeBasePath: '/',
          sidebarPath: './sidebars.ts',
          editUrl: 'https://github.com/endodod/Primordia/tree/dev/apps/docs/',
        },
        blog: {
          path: 'blog',
          routeBasePath: 'devlog',
          blogTitle: 'Devlog',
          showReadingTime: true,
        },
        theme: { customCss: './src/css/custom.css' },
      } satisfies Preset.Options,
    ],
  ],
  themeConfig: {
    navbar: {
      title: '🧬 Primordia',
      items: [
        { type: 'docSidebar', sidebarId: 'docs', position: 'left', label: 'Docs' },
        { to: '/devlog', label: 'Devlog', position: 'left' },
        { href: 'https://github.com/endodod/Primordia', label: 'GitHub', position: 'right' },
      ],
    },
    colorMode: { respectPrefersColorScheme: true },
  } satisfies Preset.ThemeConfig,
};

export default config;
